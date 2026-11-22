"""AI Daily Drop LONG video renderer (1920x1080, 30 fps).

Reuses the brand pieces of render.py (fonts, colours, glow, icons, whoosh, caption timing) and adds a 16:9 timeline:
  cold open (voice + footage, headline from frame 0) -> 3 s brand sting -> per chapter: 2.4 s title card + voiced lines
  -> recap -> call to action.
Every voiced line: footage shots split evenly over the line (one shot every ~3-5 s, slow push-in + drift, quick flash
on cuts), optional graphic (headline / stat / feature / flow / bullets / cta), sentence-level lower-third caption.
Audio: voice lines placed on the timeline, music looped + ducked under the voice (sidechain), whooshes on cuts and
chapter cards, two-pass loudnorm to -14 LUFS / -1.5 dBTP.

Called by make_long.py render <id>; expects build/<id>/vo/<seg>_<line>.wav and build/<id>/stock/*.
Returns {"chapters": [(start_seconds, name), ...], "length": seconds}.
"""
import json, math, re, subprocess, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from render import (BG, NAVY, ACC, ACC_LIGHT, WHITE, MUTED, F_BLACK, F_XBOLD, F_BOLD, F_SEMI, F_MED,
                    clamp, ease_out, ease_back, prog, glow, text_sprite, wrap, place, logo_mark, icon, pill,
                    whoosh, word_timings)

W, H, FPS = 1920, 1080, 30
ZW, ZH = 2112, 1188            # decode 10% larger than the frame, then push-in crop
PAD = 0.38                     # silence after each voiced line
CARD_DUR, STING_DUR = 2.4, 3.0
HOT = (255, 196, 61)           # warm accent (strike-through, highlights)


# ---------- backgrounds ----------
def brand_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - W * 0.5) / W) ** 2 * 1.2 + ((yy - H * 0.45) / H) ** 2)
    t = np.clip(dist / 0.7, 0, 1)[..., None]
    img = np.array(NAVY) * (1 - t) + np.array(BG) * t
    dots = ((xx % 48 > 21) & (xx % 48 < 26) & (yy % 48 > 21) & (yy % 48 < 26))[..., None]
    return Image.fromarray(np.clip(img + dots * 10, 0, 255).astype(np.uint8)).convert("RGBA")


def grade(extra_dim=0.0):
    """Navy tint, darker top band (logo) and bottom (caption); extra_dim darkens all for graphics."""
    y = np.linspace(0, 1, H)[:, None]
    a = 0.10 + 0.35 * np.clip((0.16 - y) / 0.16, 0, 1) + 0.55 * np.clip((y - 0.62) / 0.38, 0, 1)
    xx = np.linspace(-1, 1, W)[None, :]
    a = np.clip(a + 0.14 * xx ** 2 + extra_dim, 0, 0.93)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = BG; rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


class Footage:
    """Streams one clip (centre-cropped to 16:9) with a slow push-in; frames must be read in order."""
    def __init__(self, path, dur, start=1.0, drift=(0, 0)):
        self.dur, self.drift = dur, drift
        still = str(path).lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        self.zoom = (1.0, 1.12) if still else (1.0, 1.07)
        src = ["-loop", "1", "-framerate", str(FPS), "-i", str(path)] if still else ["-ss", f"{start:.2f}", "-i", str(path)]
        self.cmd = ["ffmpeg", "-loglevel", "error", *src, "-t", f"{dur + 0.3:.2f}", "-vf",
                    f"fps={FPS},scale={ZW}:{ZH}:force_original_aspect_ratio=increase:flags=lanczos,crop={ZW}:{ZH}",
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc, self.k, self.last = None, -1, None

    def get(self, t):
        k = int(t * FPS)
        if self.proc is None:
            self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        fs = ZW * ZH * 3
        while self.k < k:
            buf = self.proc.stdout.read(fs)
            if len(buf) < fs: break                   # clip ended: hold last frame
            self.last = buf; self.k += 1
        if self.last is None: raise SystemExit("no frames from " + " ".join(self.cmd))
        im = Image.frombytes("RGB", (ZW, ZH), self.last)
        p = clamp(t / self.dur); z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * p
        cw, ch = W * 1.1 / z, H * 1.1 / z
        cx = ZW / 2 + self.drift[0] * p; cy = ZH / 2 + self.drift[1] * p
        return im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

    def close(self):
        if self.proc: self.proc.kill(); self.proc = None


# ---------- lower-third caption ----------
CAP_F = F_BOLD(50)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]


def sentence_times(text, dur):
    """Start/end of each sentence, from the per-word timing estimate of render.py."""
    timed = word_timings(text, dur); out = []; k = 0
    for s in sentences(text):
        n = len(s.split()); seg = timed[k:k + n]; k += n
        out.append((s, seg[0][1], seg[-1][2]))
    return out


def caption_sprite(text):
    lines = wrap(text, CAP_F, 1500)
    if len(lines) > 2:                                # very long sentence: smaller font
        f = F_BOLD(42); lines = wrap(text, f, 1560)
    else:
        f = CAP_F
    lh = int(f.size * 1.28); h = lh * len(lines) + 34
    w = int(max(f.getlength(l) for l in lines)) + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=(5, 14, 32, 215))
    d.rounded_rectangle((0, 0, 10, h - 1), radius=5, fill=ACC + (255,))
    for i, l in enumerate(lines):
        d.text((44, 17 + i * lh), l, font=f, fill=WHITE)
    return im


# ---------- graphics (16:9 versions of the Shorts scenes) ----------
class Graphic:
    def __init__(self, g, dur, sent_times):
        self.g, self.dur, self.st = g, dur, sent_times
        getattr(self, "prep_" + g["type"])()

    def draw(self, c, t):
        getattr(self, "draw_" + self.g["type"])(c, t)

    # big stacked headline (cold open)
    def prep_headline(self):
        self.kick = pill(self.g["kicker"], F_XBOLD(44), fg=BG, bg=ACC, pad=(34, 16)) if self.g.get("kicker") else None
        self.lines = []
        for i, l in enumerate(self.g["lines"]):
            acc = i == self.g.get("accent", -1)
            spr = text_sprite(l, F_BLACK(150), fill=ACC_LIGHT if acc else WHITE, stroke=6, stroke_fill=(2, 6, 16))
            if spr.width > W - 200:
                spr = text_sprite(l, F_BLACK(int(150 * (W - 200) / spr.width)), fill=ACC_LIGHT if acc else WHITE, stroke=6, stroke_fill=(2, 6, 16))
            self.lines.append(glow(spr, color=ACC if acc else (0, 0, 0), radius=22, strength=0.8 if acc else 1.3))

    def draw_headline(self, c, t):
        if self.kick: place(c, self.kick, W / 2, 230)
        y = 400
        for spr in self.lines:
            place(c, spr, W / 2, y); y += 165

    # count-up number
    def prep_stat(self):
        self.label = glow(text_sprite(self.g["label"], F_BOLD(66)), color=(0, 0, 0), radius=12, strength=1.3)
        self.note = glow(text_sprite(self.g["note"], F_MED(40), fill=MUTED), color=(0, 0, 0), radius=10, strength=1.3) if self.g.get("note") else None
        self.cache = {}

    def draw_stat(self, c, t):
        v = self.g["value"]; p = ease_out(prog(t, 0.1, 1.0))
        val = f"{v * p:.1f}" if isinstance(v, float) and not v.is_integer() else str(int(round(v * p)))
        txt = f"{self.g.get('prefix', '')}{val}{self.g.get('suffix', '')}"
        if txt not in self.cache:
            self.cache[txt] = glow(text_sprite(txt, F_BLACK(250), fill=ACC_LIGHT, stroke=5, stroke_fill=(2, 6, 16)), radius=30, strength=0.75)
        pin = ease_back(prog(t, 0.05, 0.5)); spr = self.cache[txt]
        place(c, spr, W / 2, 380, alpha=clamp(pin), scale=0.8 + 0.2 * pin)
        if self.g.get("strike"):
            ps = ease_out(prog(t, 1.4, 0.35))
            if ps > 0:
                d = ImageDraw.Draw(c); x0 = W / 2 - spr.width * 0.36; x1 = x0 + spr.width * 0.72 * ps
                d.line([(x0, 420), (x1, 340)], fill=HOT + (255,), width=22)
        pl = ease_out(prog(t, 0.45, 0.45))
        place(c, self.label, W / 2, 575 + (1 - pl) * 30, alpha=pl)
        if self.note: place(c, self.note, W / 2, 655 + (1 - pl) * 30, alpha=pl)

    # icon + title + subtitle on a card
    def prep_feature(self):
        self.ic = icon(self.g["icon"], 230)
        self.title = text_sprite(self.g["title"], F_BLACK(96))
        f = F_SEMI(46); self.sub = [text_sprite(l, f, fill=(225, 233, 243)) for l in wrap(self.g["subtitle"], f, 900)]
        w = 360 + max([self.title.width] + [s.width for s in self.sub]) + 80
        h = max(330, 130 + self.title.height + 60 * len(self.sub))
        self.card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(self.card).rounded_rectangle((0, 0, w - 1, h - 1), radius=36, fill=(8, 22, 46, 228), outline=ACC + (170,), width=3)
        self.card = glow(self.card, radius=14, strength=0.6)

    def draw_feature(self, c, t):
        p = ease_back(prog(t, 0.05, 0.55)); pt = ease_out(prog(t, 0.3, 0.45)); ps = ease_out(prog(t, 0.55, 0.45))
        cx, cy = W / 2, 430; x0 = cx - (self.card.width - 84) / 2
        place(c, self.card, cx, cy + (1 - p) * 40, alpha=clamp(p))
        place(c, self.ic, x0 + 190, cy + 4 * math.sin(t * 2.4), alpha=clamp(p), scale=0.7 + 0.3 * p)
        tx = x0 + 340; th = self.title.height + 60 * len(self.sub); ty = cy - th / 2
        place(c, self.title, tx + self.title.width / 2 + (1 - pt) * 30, ty + self.title.height / 2, alpha=pt)
        for i, s in enumerate(self.sub):
            place(c, s, tx + s.width / 2 + (1 - ps) * 30, ty + self.title.height + 28 + i * 60 + s.height / 2, alpha=ps)

    # A -> B (two cards and an arrow)
    def prep_flow(self):
        self.cards = []
        for side in ("left", "right"):
            ic = icon(self.g["icon_" + side], 120); tx = text_sprite(self.g[side], F_BLACK(84))
            w = 120 + tx.width + 120; im = Image.new("RGBA", (w, 210), (0, 0, 0, 0))
            ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, 209), radius=40, fill=(8, 22, 46, 230), outline=ACC + (170,), width=4)
            im.alpha_composite(ic, (10, (210 - ic.height) // 2)); im.alpha_composite(tx, (150, (210 - tx.height) // 2))
            self.cards.append(glow(im, radius=12, strength=0.6))
        a = Image.new("RGBA", (220, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(a)
        d.line([(10, 60), (160, 60)], fill=ACC, width=16); d.polygon([(150, 18), (212, 60), (150, 102)], fill=ACC)
        self.arrow = glow(a, radius=10)

    def draw_flow(self, c, t):
        p1 = ease_out(prog(t, 0.1, 0.45)); pa = ease_out(prog(t, 0.6, 0.4)); p2 = ease_back(prog(t, 1.0, 0.5))
        l, r = self.cards; gap = 260; total = l.width + r.width + gap; x = W / 2 - total / 2
        place(c, l, x + l.width / 2 + (1 - p1) * -40, 430, alpha=p1)
        place(c, self.arrow, x + l.width + gap / 2 + 10 * math.sin(t * 5), 430, alpha=pa)
        place(c, r, x + l.width + gap + r.width / 2, 430, alpha=clamp(p2), scale=0.85 + 0.15 * p2)

    # recap list: items appear with the matching sentence
    def prep_bullets(self):
        self.head = pill(self.g["title"], F_XBOLD(44), fg=BG, bg=ACC, pad=(34, 16))
        self.items = [text_sprite(s, F_BOLD(52)) for s in self.g["items"]]
        n = len(self.items)
        starts = [s for _, s, _ in self.st]
        self.at = starts[-n:] if len(starts) >= n else [0.4 + k * (self.dur - 1) / n for k in range(n)]

    def draw_bullets(self, c, t):
        place(c, self.head, W / 2, 170)
        d = ImageDraw.Draw(c)
        x0 = W / 2 - max(s.width for s in self.items) / 2 - 40
        for k, (s, a) in enumerate(zip(self.items, self.at)):
            p = ease_out(prog(t, a - 0.1, 0.35))
            if p <= 0: continue
            y = 290 + k * 98
            d.rounded_rectangle((x0 - 30, y - 38, x0 + s.width + 70, y + 40), radius=20, fill=(8, 22, 46, int(220 * p)))
            d.ellipse((x0 - 12, y - 12, x0 + 12, y + 12), fill=ACC + (int(255 * p),))
            place(c, s, x0 + 40 + s.width / 2 + (1 - p) * 40, y, alpha=p)

    # end call to action
    def prep_cta(self):
        self.lines = [glow(text_sprite(l, F_BLACK(120), fill=ACC_LIGHT if i == len(self.g["lines"]) - 1 else WHITE),
                           color=ACC if i == len(self.g["lines"]) - 1 else (0, 0, 0), radius=20, strength=0.8) for i, l in enumerate(self.g["lines"])]
        self.mark = logo_mark(150)
        self.btn = pill("SUBSCRIBE", F_XBOLD(54), fg=BG, bg=ACC, pad=(54, 26))
        self.sub = text_sprite("New episode every Sunday", F_SEMI(42), fill=MUTED)

    def draw_cta(self, c, t):
        y = 230
        for i, s in enumerate(self.lines):
            p = ease_out(prog(t, 0.05 + i * 0.15, 0.45)); place(c, s, W / 2, y + (1 - p) * 40, alpha=p); y += 135
        # subscribe appears with the sentence that asks for it
        a = self.st[1][1] if len(self.st) > 1 else 3.0
        p = ease_back(prog(t, a - 0.2, 0.5)); pulse = 1 + 0.03 * math.sin(t * 6) * clamp(t - a - 0.6)
        place(c, self.mark, W / 2 - 210, 640, alpha=clamp(p), scale=p * pulse)
        place(c, self.btn, W / 2 + 90, 640, alpha=clamp(p), scale=(0.85 + 0.15 * p) * pulse)
        place(c, self.sub, W / 2, 750, alpha=clamp(p))


# ---------- timeline ----------
def wav_dur(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def build_timeline(spec, build):
    units, chapters, t, ch_no = [], [(0.0, "Intro")], 0.0, 0
    for si, seg in enumerate(spec["segments"]):
        kind = seg["kind"]
        if kind == "sting":
            units.append({"kind": "sting", "start": t, "dur": STING_DUR}); t += STING_DUR; continue
        if kind == "chapter":
            ch_no += 1; chapters.append((t, seg["title"]))
            units.append({"kind": "card", "start": t, "dur": CARD_DUR, "no": ch_no, "title": seg["title"]}); t += CARD_DUR
        if kind == "recap": chapters.append((t, "Recap"))
        for li, line in enumerate(seg["lines"]):
            wav = build / "vo" / f"{si}_{li}.wav"; vd = wav_dur(wav)
            d = round((vd + PAD) * FPS) / FPS
            if kind == "cta": d += 1.5                                      # hold the end screen a moment
            units.append({"kind": "line", "start": t, "dur": d, "voice": vd, "wav": wav, "line": line, "seg": seg,
                          "chapter": ch_no if kind == "chapter" else 0, "first": si == 0 and li == 0})
            t += d
    return units, chapters, t


def render(script_path, build, music_dir, out):
    spec = json.load(open(script_path)); build = Path(build); stock = build / "stock"
    units, chapters, total = build_timeline(spec, build)
    n_frames = int(round(total * FPS))
    base = brand_background(); g_plain, g_dim = grade(), grade(0.30)
    mark_small = logo_mark(70); brand = text_sprite("AI DAILY DROP", F_XBOLD(34))
    ch_pills = {}
    for u in units:
        if u["kind"] == "line" and u["chapter"]:
            ch_pills[u["chapter"]] = pill(f"{u['chapter']:02d}  {u['seg'].get('short', u['seg']['title'].upper())}", F_BOLD(32))

    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                            "-pix_fmt", "yuv420p", str(build / "video_long.mp4")], stdin=subprocess.PIPE)
    cut_times, frame_no = [], 0
    for ui, u in enumerate(units):
        n = int(round(u["dur"] * FPS))
        draw = {"sting": sting_frames, "card": card_frames, "line": line_frames}[u["kind"]]
        cuts = draw(u, n, base, g_plain, g_dim, mark_small, brand, ch_pills, stock, enc, frame_no, total)
        cut_times += [(u["start"] + c, kind) for c, kind in cuts]
        frame_no += n
        print(f"unit {ui + 1}/{len(units)} {u['kind']} {u['dur']:.1f}s done", flush=True)
    enc.stdin.close()
    if enc.wait() != 0: raise SystemExit("video encode failed")
    vid_len = frame_no / FPS
    mix_audio(spec, units, cut_times, vid_len, build, Path(music_dir), Path(out))
    print(f"done {out} {vid_len:.1f}s")
    return {"chapters": chapters, "length": vid_len}


def chrome(c, mark_small, brand, pill_spr=None):
    """Persistent brand bug top-left + chapter label top-right."""
    place(c, mark_small, 60 + 35, 62)
    place(c, brand, 60 + 70 + 18 + brand.width / 2, 62)
    if pill_spr is not None: place(c, pill_spr, W - 60 - pill_spr.width / 2, 62)


def line_frames(u, n, base, g_plain, g_dim, mark_small, brand, ch_pills, stock, enc, frame_no, total):
    line = u["line"]; clips = line.get("clips") or []
    st = sentence_times(line["say"], u["voice"])
    gfx = Graphic(line["graphic"], u["dur"], st) if line.get("graphic") else None
    gr = g_dim if gfx else g_plain
    feeds, cuts = [], []
    if clips:
        seg = u["dur"] / len(clips)
        for k, cl in enumerate(clips):
            name, _, s0 = cl.partition("@")
            drift = ((-1) ** (frame_no // 7 + k) * 60, (-1) ** k * 30)
            feeds.append(Footage(stock / name, seg + 0.1, start=float(s0 or 1.0), drift=drift)); cuts.append(k * seg)
    caps = [(caption_sprite(s), a, b) for s, a, b in st]
    pill_spr = ch_pills.get(u["chapter"])
    cut_events = [(c0, "cut") for k, c0 in enumerate(cuts) if not (u["first"] and k == 0)]
    for f in range(n):
        t = f / FPS
        if feeds:
            k = max(i for i, c0 in enumerate(cuts) if t >= c0 - 1e-6)
            c = feeds[k].get(t - cuts[k]).convert("RGBA"); c.alpha_composite(gr)
            since = t - cuts[k] if not (u["first"] and k == 0) else 99
        else:
            c = base.copy(); since = 99
        chrome(c, mark_small, brand, pill_spr)
        if gfx: gfx.draw(c, t + (3.0 if u["first"] else 0.0))   # cold open: headline fully visible at frame 0
        # caption: current sentence (stays until the next one starts)
        cur = None
        for spr, a, b in caps:
            if t >= a - 0.1: cur = (spr, a)
        if cur is None and caps: cur = (caps[0][0], 0.0)
        if cur:
            spr, a = cur; p = 1.0 if u["first"] else ease_out(prog(t, a - 0.1, 0.22))
            place(c, spr, W / 2, H - 70 - spr.height / 2 + (1 - p) * 14, alpha=p)
        img = c.convert("RGB")
        flash = max(0.0, 1 - since / 0.1) * 0.22
        if flash > 0: img = Image.blend(img, Image.new("RGB", (W, H), (235, 250, 255)), flash)
        if frame_no + f >= total * FPS - 15:                      # fade out the last half second
            img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, clamp((total * FPS - frame_no - f) / 15))
        enc.stdin.write(img.tobytes())
    for fd in feeds: fd.close()
    return cut_events


def card_frames(u, n, base, g_plain, g_dim, mark_small, brand, ch_pills, stock, enc, frame_no, total):
    """Chapter title card: big outlined number + title, wipe in, slight push."""
    num = glow(text_sprite(f"{u['no']:02d}", F_BLACK(300), fill=(0, 0, 0, 0), stroke=6, stroke_fill=ACC), radius=24, strength=1.0)
    kick = text_sprite(f"STORY {u['no']}" if u["title"] != "Quick hits" else "QUICK HITS", F_XBOLD(40), fill=ACC)
    title = glow(text_sprite(u["title"], F_BLACK(104)), color=(0, 0, 0), radius=16, strength=1.2)
    if title.width > W - 160: title = title.resize((W - 160, int(title.height * (W - 160) / title.width)), Image.LANCZOS)
    for f in range(n):
        t = f / FPS; c = base.copy()
        chrome(c, mark_small, brand)
        pw = ease_out(prog(t, 0.0, 0.35))
        ImageDraw.Draw(c).rectangle((0, 520, int(W * pw), 528), fill=ACC + (255,))
        pn = ease_back(prog(t, 0.05, 0.5)); place(c, num, W / 2, 330, alpha=clamp(pn), scale=0.85 + 0.15 * pn + 0.02 * t)
        pk = ease_out(prog(t, 0.2, 0.4)); place(c, kick, W / 2, 600 + (1 - pk) * 20, alpha=pk)
        pt = ease_out(prog(t, 0.3, 0.45)); place(c, title, W / 2 + (1 - pt) * 60, 720, alpha=pt)
        out = ease_out(prog(t, u["dur"] - 0.2, 0.2))
        img = c.convert("RGB")
        if out > 0: img = Image.blend(img, Image.new("RGB", (W, H), BG), out * 0.8)
        enc.stdin.write(img.tobytes())
    return [(0.0, "card")]


def sting_frames(u, n, base, g_plain, g_dim, mark_small, brand, ch_pills, stock, enc, frame_no, total):
    """3 s brand intro: logo pops with a ring pulse, name + show title slide up."""
    mark = logo_mark(260); name = glow(text_sprite("AI DAILY DROP", F_BLACK(120)), color=ACC, radius=18, strength=0.5)
    show = pill(spec_show(u), F_XBOLD(40), fg=BG, bg=ACC, pad=(34, 14))
    for f in range(n):
        t = f / FPS; c = base.copy(); d = ImageDraw.Draw(c)
        for k in range(3):                                    # expanding rings
            r = 120 + (t * 520 - k * 160)
            if 120 < r < 1100:
                a = int(160 * (1 - (r - 120) / 980)); d.ellipse((W / 2 - r, 380 - r, W / 2 + r, 380 + r), outline=ACC + (a,), width=6)
        pm = ease_back(prog(t, 0.05, 0.55)); place(c, mark, W / 2, 380, alpha=clamp(pm), scale=0.6 + 0.4 * pm)
        pn = ease_out(prog(t, 0.45, 0.5)); place(c, name, W / 2, 640 + (1 - pn) * 40, alpha=pn)
        ps = ease_out(prog(t, 0.8, 0.45)); place(c, show, W / 2, 770 + (1 - ps) * 30, alpha=ps)
        img = c.convert("RGB")
        fade = ease_out(prog(t, u["dur"] - 0.25, 0.25))
        if t < 0.12: img = Image.blend(Image.new("RGB", (W, H), (235, 250, 255)), img, t / 0.12)
        if fade > 0: img = Image.blend(img, Image.new("RGB", (W, H), BG), fade * 0.7)
        enc.stdin.write(img.tobytes())
    return [(0.0, "sting")]


SHOW_NAME = ["AI NEWS THIS WEEK"]
def spec_show(u): return SHOW_NAME[0]


# ---------- audio ----------
def thump(sr=48000, dur=0.5):
    t = np.arange(int(sr * dur)) / sr
    f = 90 * np.exp(-t * 6) + 45
    return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 7) * 0.9).astype(np.float32)


def mix_audio(spec, units, cut_times, vid_len, build, music_dir, out):
    sr = 48000; L = int(sr * (vid_len + 0.5))
    vo = np.zeros(L, np.float32); sfx = np.zeros(L, np.float32)
    for u in units:
        if u["kind"] != "line": continue
        r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(u["wav"]), "-ar", str(sr), "-ac", "1", "-f", "f32le", "-"],
                           capture_output=True, check=True)
        a = np.frombuffer(r.stdout, np.float32); s = int(u["start"] * sr)
        vo[s:s + len(a)] += a[: max(0, min(len(a), L - s))]
    w_ = whoosh(); th = thump()
    for t, kind in cut_times:
        gain = {"cut": 0.22, "card": 0.75, "sting": 0.8}[kind]
        s = int((t - 0.18) * sr)
        if s < 0: continue
        sfx[s:s + len(w_)] += w_[: max(0, min(len(w_), L - s))] * gain
        if kind in ("card", "sting"):
            s2 = int(t * sr) + int(0.05 * sr); sfx[s2:s2 + len(th)] += th[: max(0, min(len(th), L - s2))] * (0.5 if kind == "card" else 0.7)
    for name, arr in (("voice_long.wav", vo), ("sfx_long.wav", sfx)):
        with wave.open(str(build / name), "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            wf.writeframes((np.clip(arr, -1, 1) * 32767).astype(np.int16).tobytes())
    music = music_dir / f"{spec['music']}.mp3"
    pre = (f"[2:a]aresample=48000,atrim=0:{vid_len:.3f},volume=0.16,afade=t=in:d=1,afade=t=out:st={vid_len - 3:.3f}:d=3[m];"
           f"[1:a]aresample=48000,asplit=2[v1][v2];[3:a]volume=0.6[sfx];"
           f"[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=30:release=500[md];"
           f"[v2][md][sfx]amix=inputs=3:normalize=0")
    inputs = ["-i", str(build / "video_long.mp4"), "-i", str(build / "voice_long.wav"),
              "-stream_loop", "-1", "-i", str(music), "-i", str(build / "sfx_long.wav")]
    # pass 1: measure
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *inputs, "-filter_complex", pre + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[a]",
                        "-map", "[a]", "-t", f"{vid_len:.3f}", "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    tmp = out.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", pre + "," + ln + "[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-t", f"{vid_len:.3f}", "-movflags", "+faststart", str(tmp)], check=True)
    tmp.rename(out)
