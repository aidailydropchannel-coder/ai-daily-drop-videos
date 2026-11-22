"""Thumbnails for long videos (1280x720), built to channel/thumbnail_playbook.md.

    python3 engine/make_long.py thumb <id>
      -> videos/<id>/thumb_A.jpg, thumb_B.jpg, thumb_C.jpg   (3 options, full size)
      -> build/<id>/thumb_compare.jpg                        (all 3 at full size, 320x180 and 168x94 for the phone test)
    Pick the best, then set "thumb_choice": "B" in script.json and run again: it copies it to videos/<id>/thumb.jpg.

script.json "thumbs": list of 3 options, e.g.
  {"name": "A", "lines": ["GEMINI AGENT", "NOW FREE"], "accent": 1, "accent_color": "yellow", "badge": "FREE",
   "hero": {"type": "image", "src": "g2_0_0.mp4@2"}}          # a stock/official file in build/<id>/stock (@seconds for video)
  hero types: image (src) | number (text, icons: [...]) - one dominant subject only.
Layout: text left (2-3 lines, 2-4 words), hero right, small logo top-left, bottom-right corner left clear (timestamp).
"""
import json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from render import BG, ACC, ACC_LIGHT, WHITE, F_BLACK, F_XBOLD, glow, text_sprite, place, logo_mark, pill, icon  # noqa

TW, TH = 1280, 720
HOT = (255, 196, 61)
OUTLINE = (2, 6, 16)


def load_src(vid, src, size):
    """Frame of a stock clip (name.mp4@seconds) or an image, cover-cropped to size."""
    name, _, t = src.partition("@"); p = ROOT / "build" / vid / "stock" / name
    tmp = "/tmp/_thumb_src.png"
    args = ["-ss", t or "1.5"] if name.endswith(".mp4") else []
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-i", str(p), "-frames:v", "1", "-vf",
                    f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=increase:flags=lanczos,crop={size[0]}:{size[1]}", tmp], check=True)
    return Image.open(tmp).convert("RGB")


def background(vid, opt):
    """Blurred, darkened hero (or brand navy) + cyan glow where the hero sits: bright, not black."""
    hero = opt["hero"]
    if hero["type"] == "image":
        bg = load_src(vid, hero["src"], (TW, TH)).filter(ImageFilter.GaussianBlur(26))
        bg = ImageEnhance.Brightness(bg).enhance(0.55).convert("RGBA")
        bg.alpha_composite(Image.new("RGBA", (TW, TH), (8, 30, 70, 120)))
    else:
        bg = Image.new("RGBA", (TW, TH), (10, 42, 92, 255))
    glow_l = Image.new("L", (TW, TH), 0); d = ImageDraw.Draw(glow_l)
    d.ellipse((560, 40, 1320, 760), fill=180); glow_l = glow_l.filter(ImageFilter.GaussianBlur(120))
    tint = Image.new("RGBA", (TW, TH), ACC + (0,)); tint.putalpha(glow_l.point(lambda v: int(v * 0.75)))
    bg.alpha_composite(tint)
    # left side a little darker so the words pop
    shade = Image.new("L", (TW, TH), 0); ds = ImageDraw.Draw(shade)
    for x in range(TW): ds.line([(x, 0), (x, TH)], fill=int(120 * max(0, 1 - x / 700)))
    dark = Image.new("RGBA", (TW, TH), BG + (0,)); dark.putalpha(shade); bg.alpha_composite(dark)
    return bg


def hero_layer(vid, c, opt):
    hero = opt["hero"]
    if hero["type"] == "image":
        w, h = hero.get("size", (560, 420))
        im = load_src(vid, hero["src"], (w, h))
        im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.25)).enhance(1.12)
        mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=255)
        fr = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
        ImageDraw.Draw(fr).rounded_rectangle((0, 0, w + 15, h + 15), radius=36, fill=ACC + (255,))
        fr.paste(im, (8, 8), mask)
        fr = glow(fr, radius=26, strength=1.1)
        place(c, fr, hero.get("cx", 925), hero.get("cy", 350))
    elif hero["type"] == "number":
        num = text_sprite(hero["text"], F_BLACK(hero.get("font", 500)), fill=ACC_LIGHT, stroke=10, stroke_fill=OUTLINE)
        num = glow(num, radius=40, strength=1.0)
        place(c, num, hero.get("cx", 960), hero.get("cy", 300))
        icons = hero.get("icons", [])
        for k, name in enumerate(icons):
            ic = icon(name, 88); x = hero.get("cx", 960) + (k - (len(icons) - 1) / 2) * 104
            place(c, ic, x, 575)


def text_block(c, opt):
    lines = opt["lines"]; acc = opt.get("accent", len(lines) - 1)
    acc_col = HOT if opt.get("accent_color") == "yellow" else ACC_LIGHT
    max_w = opt.get("text_w", 640); sprites = []
    for i, l in enumerate(lines):
        size = opt.get("size", 128)
        while True:
            spr = text_sprite(l, F_BLACK(size), fill=acc_col if i == acc else WHITE, stroke=9, stroke_fill=OUTLINE)
            if spr.width <= max_w or size <= 60: break
            size -= 4
        sprites.append(glow(spr, color=(0, 0, 0), radius=14, strength=1.6))
    total = sum(s.height - 84 for s in sprites) + 6 * (len(sprites) - 1)
    y = opt.get("text_cy", 380) - total / 2
    if opt.get("badge"):
        b = pill(opt["badge"], F_XBOLD(44), fg=BG, bg=HOT, border=HOT, pad=(26, 12))
        place(c, b, 64 + b.width / 2 - 8, y - 50)
    for s in sprites:
        h = s.height - 84
        place(c, s, 64 + s.width / 2 - 42, y + h / 2); y += h + 6


def make_one(vid, opt):
    c = background(vid, opt)
    hero_layer(vid, c, opt)
    text_block(c, opt)
    place(c, logo_mark(58), 34 + 29, 34 + 26)
    place(c, text_sprite("AI DAILY DROP", F_XBOLD(26), stroke=3, stroke_fill=OUTLINE), 34 + 58 + 12 + 88, 34 + 26)
    out = ROOT / "videos" / vid / f"thumb_{opt['name']}.jpg"
    c.convert("RGB").save(out, quality=92)
    return out


def make_all(vid):
    spec = json.load(open(ROOT / "videos" / vid / "script.json"))
    outs = [make_one(vid, o) for o in spec["thumbs"]]
    # comparison sheet: full size + phone (320x180) + suggested-video size (168x94)
    S = Image.new("RGB", (TW + 40 + 340, len(outs) * (TH + 20)), (24, 24, 24)); d = ImageDraw.Draw(S)
    for k, p in enumerate(outs):
        im = Image.open(p); y = k * (TH + 20)
        S.paste(im, (0, y)); S.paste(im.resize((320, 180), Image.LANCZOS), (TW + 30, y))
        S.paste(im.resize((168, 94), Image.LANCZOS), (TW + 30, y + 200))
        d.text((TW + 30, y + 310), p.stem, fill="yellow")
    S.save(ROOT / "build" / vid / "thumb_compare.jpg", quality=88)
    print("thumbnails:", *outs, "\ncompare:", ROOT / "build" / vid / "thumb_compare.jpg")
    if spec.get("thumb_choice"):
        shutil.copy(ROOT / "videos" / vid / f"thumb_{spec['thumb_choice']}.jpg", ROOT / "videos" / vid / "thumb.jpg")
        print("chosen:", spec["thumb_choice"], "-> thumb.jpg")


if __name__ == "__main__":
    make_all(sys.argv[1])
