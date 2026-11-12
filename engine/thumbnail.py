"""Thumbnail maker for AI Daily Drop Shorts (1080x1920 JPG, also used as cover frame).

    python3 engine/thumbnail.py <id>        -> videos/<id>/thumb.jpg

Text comes from script.json "thumb": {"lines": ["CHATGPT", "MAKES GIFS"], "accent": 1, "badge": "NEW"}
(2-3 lines, max ~12 characters each, ALL CAPS, the curiosity hook). Falls back to the hook headline.
Background: the best footage frame (scene 0 clip if available, else a frame of final.mp4).
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from render import W, H, BG, ACC, ACC_LIGHT, WHITE, F_BLACK, F_XBOLD, glow, text_sprite, place, logo_mark, pill  # noqa


def frame_from(path, t):
    out = "/tmp/_thumb_bg.jpg"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-q:v", "2", out], check=True)
    return Image.open(out).convert("RGB")


def make(vid):
    spec = json.load(open(ROOT / "videos" / vid / "script.json"))
    th = spec.get("thumb") or {}
    lines = th.get("lines") or [l.upper() for l in spec["scenes"][0].get("headline", [spec["title"]])][:3]
    accent = th.get("accent", len(lines) - 1)
    clips = spec["scenes"][0].get("clips") or []
    stock = ROOT / "build" / vid / "stock"
    if clips and (stock / clips[0].split("@")[0]).exists():
        name, _, st = clips[0].partition("@")
        bg = frame_from(stock / name, float(st or 1) + 0.8)
    else:
        bg = frame_from(ROOT / "videos" / vid / "final.mp4", 0.05)

    # punchy grade: more contrast/saturation, darker top and bottom for text
    bg = ImageEnhance.Contrast(bg).enhance(1.15)
    bg = ImageEnhance.Color(bg).enhance(1.25).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(shade)
    for y in range(H):
        a = 0
        if y < 760: a = int(200 * (1 - y / 760) ** 1.2)
        if y > 1150: a = max(a, int(150 * ((y - 1150) / 770)))
        d.line([(0, y), (W, y)], fill=BG + (a,))
    bg.alpha_composite(shade)

    # headline: huge, tight, accent line in brand cyan with glow; thick dark outline for small-size readability
    y = 250
    for i, line in enumerate(lines):
        size = 190 if len(line) <= 8 else 160 if len(line) <= 11 else 130
        fill = ACC_LIGHT if i == accent else WHITE
        spr = text_sprite(line, F_BLACK(size), fill=fill, stroke=10, stroke_fill=(2, 6, 16))
        spr = glow(spr, color=ACC if i == accent else (0, 0, 0), radius=22, strength=1.0 if i == accent else 1.3)
        place(bg, spr, W / 2, y + size * 0.55)
        y += int(size * 1.02)

    if th.get("badge"):
        place(bg, pill(th["badge"], F_XBOLD(56), fg=BG, bg=ACC, pad=(40, 18)), W / 2, 150)
    place(bg, logo_mark(120), W / 2 - 170, H - 260)
    place(bg, text_sprite("AI DAILY DROP", F_XBOLD(52), stroke=4, stroke_fill=(2, 6, 16)), W / 2 + 60, H - 260)
    out = ROOT / "videos" / vid / "thumb.jpg"
    bg.convert("RGB").save(out, quality=92)
    print("thumbnail:", out)
    return out


if __name__ == "__main__":
    make(sys.argv[1])
