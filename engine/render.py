"""AI Daily Drop Shorts renderer.

Turns a script.json (scenes + per-scene voiceover wavs) into a finished 1080x1920 Short:
animated brand visuals, word-synced captions, voiceover and ducked background music.

    python3 render.py <script.json> <build_dir> <music_dir> <out.mp4> [--frames 0.5,1.2]
"""
import json, math, re, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (5, 11, 26)
NAVY = (14, 42, 82)
ACC = (34, 211, 238)
ACC_LIGHT = (125, 236, 255)
WHITE = (255, 255, 255)
MUTED = (194, 206, 223)
FONT_DIR = "/usr/share/fonts/opentype/inter/"
PAD_AFTER = 0.32          # silence after each scene's voice line


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_BLACK = lambda s: font("InterDisplay-Black.otf", s)
F_XBOLD = lambda s: font("InterDisplay-ExtraBold.otf", s)
F_BOLD = lambda s: font("InterDisplay-Bold.otf", s)
F_SEMI = lambda s: font("Inter-SemiBold.otf", s)
F_MED = lambda s: font("Inter-Medium.otf", s)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, start, dur): return clamp((t - start) / dur)


# ---------- sprite helpers ----------
def glow(sprite, color=ACC, radius=18, strength=1.6):
    """Return sprite with a soft coloured glow behind it (canvas grows by 3*radius)."""
    pad = radius * 3
    w, h = sprite.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = sprite.split()[3]
    g = Image.new("RGBA", out.size, color + (0,))
    mask = Image.new("L", out.size, 0); mask.paste(a, (pad, pad))
    mask = mask.filter(ImageFilter.GaussianBlur(radius))
    mask = mask.point(lambda v: min(255, int(v * strength)))
    g.putalpha(mask)
    out = Image.alpha_composite(out, g)
    out.alpha_composite(sprite, (pad, pad))
    return out


def text_sprite(text, fnt, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0)):
    box = fnt.getbbox(text, stroke_width=stroke)
    w, h = box[2] - box[0], box[3] - box[1]
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - box[0], 2 - box[1]), text, font=fnt, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if fnt.getlength(test) <= max_w or not cur: cur = test
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines


def place(canvas, sprite, cx, cy, alpha=1.0, scale=1.0):
    """Paste sprite centred at (cx, cy) with alpha and scale."""
    if alpha <= 0.003: return
    s = sprite
    if abs(scale - 1) > 0.004:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if alpha < 0.997:
        s = s.copy(); s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


# ---------- brand pieces ----------
def drop_poly(cx, cy, r):
    apex = (cx, cy - r * math.sqrt(2))
    pts = [apex]
    for k in range(0, 271, 6):          # arc from 45deg right of top round the bottom to 45deg left
        ang = math.radians(-45 + k)
        pts.append((cx + r * math.sin(ang), cy - r * math.cos(ang)))
    return pts


def logo_mark(size=120):
    """Neon ring + Ai monogram (matches the channel logo)."""
    S = 800
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((150, 150, 650, 650), outline=ACC + (255,), width=16)
    d.ellipse((178, 178, 622, 622), outline=ACC + (110,), width=4)
    ox, oy = -34, 10
    a = Image.new("L", (S, S), 0); da = ImageDraw.Draw(a)
    da.polygon([(300 + ox, 500 + oy), (380 + ox, 290 + oy), (420 + ox, 290 + oy), (500 + ox, 500 + oy),
                (452 + ox, 500 + oy), (436 + ox, 456 + oy), (364 + ox, 456 + oy), (348 + ox, 500 + oy)], fill=255)
    da.polygon([(378 + ox, 418 + oy), (422 + ox, 418 + oy), (400 + ox, 356 + oy)], fill=0)
    da.rounded_rectangle((524 + ox, 360 + oy, 568 + ox, 500 + oy), 4, fill=255)
    white = Image.new("RGBA", (S, S), WHITE + (0,)); white.putalpha(a)
    im = Image.alpha_composite(im, white)
    ImageDraw.Draw(im).polygon(drop_poly(546 + ox, 330 + oy, 20), fill=ACC + (255,))
    im = im.crop((120, 120, 680, 680)).resize((size, size), Image.LANCZOS)
    return glow(im, radius=max(4, size // 14), strength=1.3)


def icon(name, size=300, stroke=None):
    """Simple line icons drawn at 4x then downsampled."""
    k = 4; S = size * k; sw = (stroke or max(8, size // 22)) * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = ACC + (255,)
    m = S * 0.12
    if name == "chat":
        d.rounded_rectangle((m, m * 1.4, S - m, S * 0.72), radius=S * 0.12, outline=c, width=sw)
        d.polygon([(S * 0.28, S * 0.70), (S * 0.24, S * 0.90), (S * 0.46, S * 0.71)], fill=c)
        for i in range(3):
            x = S * (0.34 + 0.16 * i); y = S * 0.45; r = S * 0.045
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    elif name == "film":
        d.rounded_rectangle((m, S * 0.2, S - m, S * 0.8), radius=S * 0.05, outline=c, width=sw)
        for row in (0.26, 0.74):
            for i in range(6):
                x = m + S * 0.06 + i * (S - 2 * m - S * 0.12) / 5
                d.rounded_rectangle((x - S * 0.025, S * row - S * 0.025, x + S * 0.025, S * row + S * 0.025), radius=S * 0.01, fill=c)
        for i in range(3):
            x0 = m + S * 0.05 + i * (S - 2 * m - S * 0.1) / 3
            d.rectangle((x0 + S * 0.02, S * 0.36, x0 + (S - 2 * m - S * 0.1) / 3 - S * 0.02, S * 0.64), outline=c, width=sw // 2)
    elif name == "bookmark":
        d.polygon([(S * 0.27, m), (S * 0.73, m), (S * 0.73, S - m), (S * 0.5, S * 0.7), (S * 0.27, S - m)], outline=c, width=sw)
        d.line([(S * 0.27, m), (S * 0.73, m), (S * 0.73, S - m), (S * 0.5, S * 0.7), (S * 0.27, S - m), (S * 0.27, m)], fill=c, width=sw, joint="curve")
        cx, cy, r = S * 0.5, S * 0.38, S * 0.11
        d.polygon([(cx, cy - r), (cx + r * 0.25, cy - r * 0.25), (cx + r, cy), (cx + r * 0.25, cy + r * 0.25),
                   (cx, cy + r), (cx - r * 0.25, cy + r * 0.25), (cx - r, cy), (cx - r * 0.25, cy - r * 0.25)], fill=c)
    elif name == "spark":
        cx = cy = S / 2; r = S * 0.4
        d.polygon([(cx, cy - r), (cx + r * 0.18, cy - r * 0.18), (cx + r, cy), (cx + r * 0.18, cy + r * 0.18),
                   (cx, cy + r), (cx - r * 0.18, cy + r * 0.18), (cx - r, cy), (cx - r * 0.18, cy - r * 0.18)], fill=c)
    elif name == "gauge":
        d.arc((m, m, S - m, S - m), 150, 390, fill=c, width=sw)
        d.line([(S / 2, S / 2), (S * 0.74, S * 0.3)], fill=c, width=sw)
        r = S * 0.06; d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), fill=c)
    im = im.resize((size, size), Image.LANCZOS)
    return glow(im, radius=size // 16, strength=1.4)


def pill(text, fnt, fg=ACC, bg=(10, 30, 56), pad=(34, 16), border=ACC):
    tw = fnt.getlength(text); box = fnt.getbbox(text)
    w, h = int(tw + pad[0] * 2), int(box[3] - box[1] + pad[1] * 2)
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=h // 2, fill=bg + (235,), outline=border + (255,), width=3)
    d.text((4 + pad[0], 4 + pad[1] - box[1]), text, font=fnt, fill=fg)
    return glow(im, radius=10, strength=0.9)


def card(w, h, radius=36):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=(12, 28, 56, 235), outline=ACC + (150,), width=3)
    return im


# ---------- background ----------
def make_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2 * 1.4)
    t = np.clip(dist / 0.62, 0, 1)[..., None]
    img = (np.array(NAVY) * (1 - t) + np.array(BG) * t)
    # dot grid
    dots = ((xx % 48 > 21) & (xx % 48 < 26) & (yy % 48 > 21) & (yy % 48 < 26))[..., None]
    img = img + dots * 10
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


CIRCUITS = [  # (points) decorative traces near the edges
    [(0, 300), (120, 300), (170, 250), (260, 250)], [(1080, 360), (950, 360), (900, 410), (820, 410)],
    [(0, 1600), (110, 1600), (160, 1650), (250, 1650)], [(1080, 1540), (980, 1540), (930, 1490), (860, 1490)],
    [(0, 980), (70, 980), (110, 940)], [(1080, 1120), (1010, 1120), (970, 1160)],
]


def circuit_layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for pts in CIRCUITS:
        d.line(pts, fill=ACC + (120,), width=4, joint="curve")
        x, y = pts[-1]; d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=BG + (255,), outline=ACC + (200,), width=4)
    return glow(im, radius=6, strength=0.8).crop((18, 18, 18 + W, 18 + H))


def pulse_dots(canvas, t):
    d = ImageDraw.Draw(canvas)
    for i, pts in enumerate(CIRCUITS):
        segs = list(zip(pts[:-1], pts[1:]))
        lens = [math.dist(a, b) for a, b in segs]; total = sum(lens)
        pos = ((t * 260 + i * 137) % (total + 300)) - 150
        if not 0 <= pos <= total: continue
        for (a, b), L in zip(segs, lens):
            if pos <= L:
                f = pos / L; x = a[0] + (b[0] - a[0]) * f; y = a[1] + (b[1] - a[1]) * f
                for r, al in ((16, 50), (10, 110), (5, 255)):
                    d.ellipse((x - r, y - r, x + r, y + r), fill=ACC + (al,))
                break
            pos -= L


# ---------- stock footage ----------
ZW, ZH = 1296, 2304            # decode 20% larger than frame, then slow push-in crop


class Footage:
    """Streams frames of one clip (centre-cropped to 9:16) with a slow push-in. Frames must be read in order."""
    def __init__(self, path, dur, start=1.0, zoom=(1.0, 1.09), drift=(0, 0)):
        self.dur, self.zoom, self.drift = dur, zoom, drift
        self.cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{start:.2f}", "-i", str(path), "-t", f"{dur + 0.3:.2f}",
                    "-vf", f"fps={FPS},scale={ZW}:{ZH}:force_original_aspect_ratio=increase:flags=lanczos,crop={ZW}:{ZH}",
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc, self.k, self.last = None, -1, None

    def _frame(self, k):
        if self.proc is None or k < self.k:
            if self.proc: self.proc.kill()
            self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); self.k = -1
        fs = ZW * ZH * 3
        while self.k < k:
            buf = self.proc.stdout.read(fs)
            if len(buf) < fs: break           # clip ended: hold last frame
            self.last = buf; self.k += 1
        if self.last is None: raise SystemExit("no frames from " + self.cmd[5])
        return Image.frombytes("RGB", (ZW, ZH), self.last)

    def get(self, t):
        im = self._frame(int(t * FPS))
        p = clamp(t / self.dur)
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * p
        cw, ch = ZW / z, ZH / z
        cx = ZW / 2 + self.drift[0] * p; cy = ZH / 2 + self.drift[1] * p
        return im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))


def grade_layer(strength=1.0):
    """Navy tint + darker top/bottom so brand bar and captions always read."""
    y = np.linspace(0, 1, H)[:, None]
    a = 0.16 + 0.45 * np.clip((0.16 - y) / 0.16, 0, 1) + 0.50 * np.clip((y - 0.58) / 0.30, 0, 1)
    a = np.clip(a * strength, 0, 0.92)
    xx = np.linspace(-1, 1, W)[None, :]
    a = np.clip(a + 0.18 * (xx ** 2), 0, 0.95)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = BG; rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def whoosh(sr=48000, dur=0.42):
    n = int(sr * dur); t = np.arange(n) / sr
    noise = np.random.default_rng(7).standard_normal(n)
    # band-pass sweep via moving average differences
    out = np.zeros(n); lp = 0.0; lp2 = 0.0
    for i in range(n):
        f = 0.02 + 0.25 * (i / n)
        lp += f * (noise[i] - lp); lp2 += f * 0.5 * (lp - lp2); out[i] = lp - lp2
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    out = out * env; out /= np.abs(out).max() + 1e-9
    return (out * 0.5).astype(np.float32)


# ---------- captions ----------
def word_timings(text, dur):
    words = re.findall(r"[^\s]+", text)
    weights = []
    for w_ in words:
        base = len(re.sub(r"[^\w]", "", w_)) + 2.2
        pause = 5 if w_[-1] in ".?!" else 2.6 if w_[-1] in ",;:" else 0
        weights.append((base, pause))
    total = sum(b + p for b, p in weights)
    t, out = 0.0, []
    for w_, (b, p) in zip(words, weights):
        s = t; t += b / total * dur; out.append((w_, s, t)); t += p / total * dur
    return out


def caption_chunks(timed, max_words=3):
    chunks, cur = [], []
    for item in timed:
        cur.append(item)
        if len(cur) >= max_words or item[0][-1] in ".,?!;:":
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return chunks


CAP_FONT = F_BLACK(84)


def draw_caption(canvas, chunks, t):
    for ch in chunks:
        if ch[0][1] - 0.05 <= t < ch[-1][2] + 0.12 or (ch is chunks[-1] and t >= ch[0][1]):
            words = [re.sub(r"[^\w'%$+.-]", "", w_).rstrip(".").upper() for w_, _, _ in ch]
            spr = []
            for (w_, s, e), txt in zip(ch, words):
                active = s - 0.03 <= t < e + 0.05
                spr.append((text_sprite(txt, CAP_FONT, fill=ACC if active else WHITE, stroke=7, stroke_fill=(2, 6, 16)), active, s))
            gap = 24
            total = sum(s_.width for s_, _, _ in spr) + gap * (len(spr) - 1)
            scale = min(1.0, 900 / total)
            x = W / 2 - total * scale / 2; y = 1300
            appear = ease_back(prog(t, ch[0][1] - 0.05, 0.16))
            for s_, active, st in spr:
                sc = scale * (0.9 + 0.1 * appear) * (1.08 if active else 1.0)
                place(canvas, s_, x + s_.width * scale / 2, y, alpha=clamp(appear * 1.4), scale=sc)
                x += (s_.width + gap) * scale
            return


# ---------- scenes ----------
class Scene:
    def __init__(self, spec, dur, idx, total_scenes, stock_dir=None):
        self.s, self.d, self.idx, self.n = spec, dur, idx, total_scenes
        self.feeds, self.cuts = [], []
        clips = spec.get("clips") or []
        if clips and stock_dir:
            seg = dur / len(clips); t0 = 0.0
            for k, c in enumerate(clips):
                drift = ((-1) ** (idx + k) * 40, (-1) ** k * 30)
                name, _, st = c.partition("@")
                self.feeds.append(Footage(Path(stock_dir) / name, seg + 0.05, start=float(st or 1.0), drift=drift))
                self.cuts.append(t0); t0 += seg
        self.kicker = pill(spec.get("kicker", ""), F_BOLD(40)) if spec.get("kicker") else None
        getattr(self, "prep_" + spec["type"])()

    # --- hook / cta: big stacked headline ---
    def prep_hook(self):
        self.lines, self.line_h = [], []
        for i, line in enumerate(self.s["headline"]):
            acc = i == self.s.get("accent_line", -1)
            self.line_h.append(int((168 if acc else 138) * 1.08))
            spr = text_sprite(line, F_BLACK(168 if acc else 138), fill=ACC_LIGHT if acc else WHITE)
            if acc: spr = glow(spr, radius=26, strength=0.75)
            else: spr = glow(spr, color=(0, 0, 0), radius=16, strength=1.3)
            self.lines.append(spr)

    def draw_hook(self, c, t):
        y = 560 if self.s["type"] == "hook" else 600
        for i, spr in enumerate(self.lines):
            p = ease_out(prog(t, 0.08 + i * 0.14, 0.45))
            h = self.line_h[i]
            place(c, spr, W / 2, y + h / 2 + (1 - p) * 80, alpha=p, scale=0.92 + 0.08 * ease_back(prog(t, 0.08 + i * 0.14, 0.5)))
            y += h + 6

    prep_cta = prep_hook

    def draw_cta(self, c, t):
        self.draw_hook(c, t)
        if not hasattr(self, "btn"):
            self.btn = pill("FOLLOW  AI DAILY DROP", F_XBOLD(46), fg=BG, bg=ACC, pad=(46, 24))
            self.mark = logo_mark(170)
        p = ease_back(prog(t, 0.9, 0.5))
        pulse = 1 + 0.035 * math.sin(t * 6) * clamp(t - 1.4)
        place(c, self.mark, W / 2, 1000, alpha=clamp(p), scale=p * pulse)
        place(c, self.btn, W / 2, 1150, alpha=clamp(p), scale=(0.85 + 0.15 * p) * pulse)

    # --- flow: input card -> arrow -> output card with animated GIF grid ---
    def prep_flow(self):
        self.c1, self.c2 = card(820, 200), card(820, 330)
        self.i1, self.i2 = icon(self.s["icon_left"], 110), icon(self.s["icon_right"], 110)
        self.t1 = text_sprite(self.s["left"], F_BOLD(56)); self.t2 = text_sprite(self.s["right"], F_BOLD(56))
        self.arrow = Image.new("RGBA", (120, 150), (0, 0, 0, 0))
        ad = ImageDraw.Draw(self.arrow)
        ad.line([(60, 0), (60, 110)], fill=ACC, width=12); ad.polygon([(18, 92), (102, 92), (60, 148)], fill=ACC)
        self.arrow = glow(self.arrow, radius=10)

    def draw_flow(self, c, t):
        p1 = ease_out(prog(t, 0.1, 0.45)); p2 = ease_out(prog(t, 1.6, 0.45)); pa = ease_out(prog(t, 1.0, 0.4))
        place(c, self.c1, W / 2, 560 + (1 - p1) * 60, alpha=p1)
        place(c, self.i1, 230, 560 + (1 - p1) * 60, alpha=p1)
        place(c, self.t1, 300 + self.t1.width / 2, 560 + (1 - p1) * 60, alpha=p1)
        bob = 10 * math.sin(t * 5)
        place(c, self.arrow, W / 2, 745 + bob, alpha=pa)
        y2 = 990 + (1 - p2) * 60
        place(c, self.c2, W / 2, y2, alpha=p2)
        place(c, self.i2, 230, y2 - 95, alpha=p2)
        place(c, self.t2, 300 + self.t2.width / 2, y2 - 95, alpha=p2)
        if p2 > 0.01:  # 3x2 frame grid, one frame lit at a time like a looping GIF
            d = ImageDraw.Draw(c)
            lit = int(t * 8) % 6
            for k in range(6):
                col, row = k % 3, k // 3
                x0 = 170 + col * 250; y0 = y2 - 15 + row * 92
                a = int(255 * p2)
                fill = ACC + (int(a * 0.9),) if k == lit else (30, 60, 100, int(a * 0.8))
                d.rounded_rectangle((x0, y0, x0 + 230, y0 + 76), radius=14, fill=fill)

    # --- feature: big icon + title + subtitle ---
    def prep_feature(self):
        self.ic = icon(self.s["icon"], 300)
        self.ring = Image.new("RGBA", (460, 460), (0, 0, 0, 0))
        ImageDraw.Draw(self.ring).ellipse((10, 10, 450, 450), fill=(12, 30, 60, 230), outline=ACC + (170,), width=5)
        self.ring = glow(self.ring, radius=16, strength=0.9)
        self.title = glow(text_sprite(self.s["title"], F_BLACK(104)), color=(0, 0, 0), radius=14, strength=1.2)
        self.sub = [glow(text_sprite(l, F_SEMI(50), fill=(225, 233, 243)), color=(0, 0, 0), radius=10, strength=1.3) for l in wrap(self.s["subtitle"], F_SEMI(50), 860)]

    def draw_feature(self, c, t):
        p = ease_back(prog(t, 0.05, 0.55)); pt = ease_out(prog(t, 0.35, 0.45)); ps = ease_out(prog(t, 0.6, 0.45))
        float_y = 8 * math.sin(t * 2.4)
        if self.feeds:
            place(c, self.ic, W / 2, 760 + float_y, alpha=clamp(p), scale=(0.42 + 0.18 * p))
            place(c, self.title, W / 2, 940 + (1 - pt) * 50, alpha=pt)
            for i, s_ in enumerate(self.sub):
                place(c, s_, W / 2, 1035 + i * 62 + (1 - ps) * 40, alpha=ps)
            return
        place(c, self.ring, W / 2, 640 + float_y, alpha=clamp(p), scale=0.6 + 0.4 * p)
        place(c, self.ic, W / 2, 640 + float_y, alpha=clamp(p), scale=(0.6 + 0.4 * p) * (1 + 0.03 * math.sin(t * 4)))
        place(c, self.title, W / 2, 975 + (1 - pt) * 50, alpha=pt)
        for i, s_ in enumerate(self.sub):
            place(c, s_, W / 2, 1075 + i * 64 + (1 - ps) * 40, alpha=ps)

    # --- stat: count-up number ---
    def prep_stat(self):
        self.label = glow(text_sprite(self.s["label"], F_BOLD(64)), color=(0, 0, 0), radius=12, strength=1.2)
        self.note = text_sprite(self.s.get("note", ""), F_MED(40), fill=MUTED) if self.s.get("note") else None
        self.cache = {}

    def draw_stat(self, c, t):
        p = ease_out(prog(t, 0.1, 1.1))
        val = int(round(self.s["value"] * p))
        key = val
        if key not in self.cache:
            self.cache[key] = glow(text_sprite(f"{val}{self.s['suffix']}", F_BLACK(300), fill=ACC_LIGHT), radius=30, strength=0.75)
        pin = ease_back(prog(t, 0.05, 0.5))
        place(c, self.cache[key], W / 2, 690, alpha=clamp(pin), scale=0.8 + 0.2 * pin)
        # progress bar
        d = ImageDraw.Draw(c)
        bw = 700; x0 = (W - bw) / 2; y0 = 900
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + 22), radius=11, fill=(30, 60, 100, 255))
        d.rounded_rectangle((x0, y0, x0 + max(22, bw * p), y0 + 22), radius=11, fill=ACC + (255,))
        pl = ease_out(prog(t, 0.5, 0.45))
        place(c, self.label, W / 2, 1010 + (1 - pl) * 40, alpha=pl)
        if self.note: place(c, self.note, W / 2, 1090 + (1 - pl) * 40, alpha=pl)

    def background(self, t):
        k = max(i for i, c0 in enumerate(self.cuts) if t >= c0 - 1e-6)
        return self.feeds[k].get(t - self.cuts[k]), t - self.cuts[k], k

    # --- frame ---
    def draw(self, c, t):
        if self.kicker:
            pk = ease_back(prog(t, 0.0, 0.4))
            place(c, self.kicker, W / 2, 380, alpha=clamp(pk), scale=0.8 + 0.2 * pk)
        getattr(self, "draw_" + self.s["type"])(c, t)


# ---------- main ----------
def wav_dur(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def render(script_path, build, music_dir, out, preview_frames=None, stock_dir=None):
    spec = json.load(open(script_path)); build = Path(build)
    scenes = spec["scenes"]
    durs = [wav_dur(build / f"vo_{i}.wav") + PAD_AFTER for i in range(len(scenes))]
    total = sum(durs)
    bg = make_background(); circ = circuit_layer()
    base = Image.alpha_composite(bg, circ)
    mark = logo_mark(92); brand = text_sprite("AI DAILY DROP", F_XBOLD(40))
    starts = np.cumsum([0] + durs[:-1])

    grade = grade_layer()

    def frame(i, sc, t_local, chunks):
        tg = starts[i] + t_local
        flash = 0.0
        if sc.feeds:
            bgim, tc, k = sc.background(t_local)
            c = bgim.convert("RGBA"); c.alpha_composite(grade)
            since = tc if (k > 0 or i > 0) else 99
            flash = max(0.0, 1 - since / 0.12) * 0.35
        else:
            c = base.copy()
            pulse_dots(c, tg)
        place(c, mark, 110 + 46, 150)
        place(c, brand, 110 + 92 + 24 + brand.width / 2, 150)
        # global progress line
        ImageDraw.Draw(c).rounded_rectangle((60, 66, 60 + (W - 120) * tg / total, 74), radius=4, fill=ACC + (255,))
        sc.draw(c, t_local)
        draw_caption(c, chunks, t_local)
        img = c.convert("RGB")
        if sc.feeds:
            if flash > 0: img = Image.blend(img, Image.new("RGB", (W, H), (235, 250, 255)), flash)
        else:
            fade = clamp(t_local / 0.12)
            if fade < 1: img = Image.blend(Image.new("RGB", (W, H), BG), img, fade)
        return img

    objs, chunk_list = [], []
    for i, s in enumerate(scenes):
        objs.append(Scene(s, durs[i], i, len(scenes), stock_dir))
        chunk_list.append(caption_chunks(word_timings(s["say"], durs[i] - PAD_AFTER)))

    if preview_frames:
        for tg in preview_frames:
            i = int(np.searchsorted(starts, tg, side="right") - 1)
            frame(i, objs[i], tg - starts[i], chunk_list[i]).save(build / f"preview_{tg:.1f}.jpg", quality=90)
        return

    parts = []
    for i, sc in enumerate(objs):
        n = int(round(durs[i] * FPS)); tmp = build / f"scene_{i}.tmp.mp4"; dst = build / f"scene_{i}.mp4"
        p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                              "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
        for f in range(n):
            p.stdin.write(frame(i, sc, f / FPS, chunk_list[i]).tobytes())
        p.stdin.close()
        if p.wait() != 0: raise SystemExit(f"scene {i} failed")
        tmp.rename(dst); parts.append(dst)
        print(f"scene {i} done ({n} frames)", flush=True)

    # voice track with padding, exact scene lengths
    vo_parts = []
    for i in range(len(scenes)):
        vo_parts += ["-i", str(build / f"vo_{i}.wav")]
    fc = "".join(f"[{i}:a]aresample=48000,apad=whole_dur={round(durs[i]*FPS)/FPS:.4f}[a{i}];" for i in range(len(scenes)))
    fc += "".join(f"[a{i}]" for i in range(len(scenes))) + f"concat=n={len(scenes)}:v=0:a=1[vo]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *vo_parts, "-filter_complex", fc, "-map", "[vo]", str(build / "voice.wav")], check=True)

    (build / "list.txt").write_text("".join(f"file '{p_.name}'\n" for p_ in parts))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(build / "list.txt"),
                    "-c", "copy", str(build / "video.mp4")], check=True)

    cut_times = []
    for i, sc in enumerate(objs):
        for k, c0 in enumerate(sc.cuts):
            if i > 0 or k > 0: cut_times.append(starts[i] + c0)
    sfx_len = int(48000 * (sum(round(d * FPS) for d in durs) / FPS + 1))
    sfx = np.zeros(sfx_len, np.float32); w_ = whoosh()
    for ct in cut_times:
        a = int((ct - 0.18) * 48000)
        if a < 0: continue
        sfx[a:a + len(w_)] += w_[: max(0, min(len(w_), sfx_len - a))] * 0.55
    with wave.open(str(build / "sfx.wav"), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
        wf.writeframes((np.clip(sfx, -1, 1) * 32767).astype(np.int16).tobytes())

    music = Path(music_dir) / f"{spec['music']}.mp3"
    vid_len = sum(round(d * FPS) for d in durs) / FPS
    mix = (f"[3:a]volume=0.5[sfx];"
           f"[1:a]aresample=48000,asplit=2[v1][v2];"
           f"[2:a]aresample=48000,atrim=0:{vid_len:.3f},volume=0.13,afade=t=in:d=0.6,afade=t=out:st={vid_len-1.5:.3f}:d=1.5[m];"
           f"[m][v1]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=350[md];"
           f"[v2][md][sfx]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    tmp_out = Path(out).with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(build / "video.mp4"), "-i", str(build / "voice.wav"),
                    "-i", str(music), "-i", str(build / "sfx.wav"), "-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(tmp_out)], check=True)
    tmp_out.rename(out)
    print("done", out, f"{vid_len:.1f}s")


if __name__ == "__main__":
    args = sys.argv[1:]
    pf = None
    if "--frames" in args:
        k = args.index("--frames"); pf = [float(x) for x in args[k + 1].split(",")]; args = args[:k] + args[k + 2:]
    sd = None
    if "--stock" in args:
        k = args.index("--stock"); sd = args[k + 1]; args = args[:k] + args[k + 2:]
    render(*args, preview_frames=pf, stock_dir=sd)
