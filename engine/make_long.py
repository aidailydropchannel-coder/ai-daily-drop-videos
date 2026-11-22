"""One-stop pipeline for the weekly LONG video (1920x1080, 4-6 min), e.g. "AI News This Week".

Folder: videos/<id>/script.json  (format: see videos/L001-ai-news-this-week/script.json)
  segments: cold_open -> sting -> 5-6 chapter -> recap -> cta. Each segment has "lines"; one line = one voice
  sentence or two, with a lower-third caption, 1-3 "footage" search phrases (one shot each, ~3-5 s per shot) and an
  optional "graphic" (headline | stat | feature | flow | bullets | cta).
  A footage entry may be {"url": "<official company press image/mp4>", "q": "what it shows"} (company media only).

    python3 engine/make_long.py stock  <id>   # request landscape Pixabay clips via the GitHub Action, download, sheet.jpg
    python3 engine/make_long.py stock  <id> --retry b --only g3_1_0,g4_2_1   # re-fetch some shots with new words
    python3 engine/make_long.py voice  <id>   # voice lines only (quick length check, prints the minutes)
    python3 engine/make_long.py render <id>   # voice + full render -> videos/<id>/final.mp4, chapters.txt, check frames
    python3 engine/make_long.py thumb  <id>   # 3 thumbnail options -> videos/<id>/thumb_A/B/C.jpg + phone-size previews
    python3 engine/make_long.py check  <id>   # loudness (LUFS) + contact sheet of frames from the finished file

Shot names: g<segment>_<line>_<n>. To swap a bad shot, edit the line's "clips" list ("file.mp4@start_seconds").
"""
import json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "aidailydropchannel-coder/ai-daily-drop-videos"
sys.path.insert(0, str(ROOT / "engine"))


def sh(*cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def load(vid): return json.load(open(ROOT / "videos" / vid / "script.json"))
def save(vid, spec): json.dump(spec, open(ROOT / "videos" / vid / "script.json", "w"), indent=1, ensure_ascii=False)


def build_dir(vid):
    d = ROOT / "build" / vid; (d / "stock").mkdir(parents=True, exist_ok=True); return d


def all_lines(spec):
    """Yield (segment_index, line_index, line) for every voiced line."""
    for si, seg in enumerate(spec["segments"]):
        for li, line in enumerate(seg.get("lines", [])):
            yield si, li, line


def stock(vid, retry="", only=None):
    spec = load(vid); req_id = vid + (f"-{retry}" if retry else "")
    items = []
    for si, li, line in all_lines(spec):
        for n, q in enumerate(line.get("footage", [])):
            name = f"g{si}_{li}_{n}"
            if only and name not in only: continue
            if isinstance(q, dict) and q.get("url"):
                items.append({"name": name, "url": q["url"], "q": q.get("q", ""), "kind": "url"})
            else:
                items.append({"name": name, "q": q, "kind": "video"})
    (ROOT / "requests").mkdir(exist_ok=True)
    json.dump({"id": req_id, "orientation": "landscape", "items": items}, open(ROOT / "requests" / f"{req_id}.json", "w"), indent=1)
    sh("git", "-C", str(ROOT), "add", "requests", f"videos/{vid}", "engine")
    sh("git", "-C", str(ROOT), "commit", "-qm", f"Stock request {req_id} (landscape, {len(items)} shots)")
    sh("git", "-C", str(ROOT), "push", "-q", "origin", "HEAD:main")
    base = f"https://github.com/{REPO}/releases/download/stock-{req_id}/"
    print(f"waiting for GitHub Action ({len(items)} shots)...", flush=True)
    for _ in range(80):                      # long videos need more clips: wait up to 20 min
        time.sleep(15)
        r = subprocess.run(["curl", "-sSL", "-o", "/tmp/manifest_long.json", "-w", "%{http_code}", base + "manifest.json"],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200": break
    else:
        raise SystemExit("stock release did not appear in 20 min - check the Actions tab on GitHub")
    man = json.load(open("/tmp/manifest_long.json")); bd = build_dir(vid)
    for m in man:
        if "file" in m:
            sh("curl", "-sSL", "-o", str(bd / "stock" / m["file"]), base + m["file"])
            print("ok ", m["name"], m["q"], "|", (m.get("tags") or "")[:80])
        else:
            print("ERR", m["name"], m["q"], m.get("error"))
    old = bd / "stock" / "manifest.json"
    merged = json.load(open(old)) if old.exists() else []
    merged = [x for x in merged if x["name"] not in {m["name"] for m in man}] + man
    json.dump(merged, open(old, "w"), indent=1)
    assign_clips(vid)
    sheet(vid)


def assign_clips(vid):
    """Default clip list per line = every downloaded shot of that line (videos start at 1 s)."""
    spec = load(vid); bd = build_dir(vid)
    files = {x["name"]: x["file"] for x in json.load(open(bd / "stock" / "manifest.json")) if "file" in x}
    for si, li, line in all_lines(spec):
        if line.get("footage") and not line.get("clips_locked"):
            line["clips"] = [files[k] + ("" if files[k].endswith((".jpg", ".jpeg", ".png", ".webp")) else "@1")
                             for k in (f"g{si}_{li}_{n}" for n in range(len(line["footage"]))) if k in files]
    save(vid, spec)


def sheet(vid):
    from PIL import Image, ImageDraw
    bd = build_dir(vid); ims = []
    for f in sorted((bd / "stock").iterdir()):
        if f.suffix.lower() not in (".mp4", ".jpg", ".jpeg", ".png", ".webp"): continue
        args = ["-ss", "1.5"] if f.suffix == ".mp4" else []
        sh("ffmpeg", "-loglevel", "error", "-y", *args, "-i", str(f), "-frames:v", "1", "-vf", "scale=320:180:force_original_aspect_ratio=increase,crop=320:180", "/tmp/_sl.jpg")
        im = Image.open("/tmp/_sl.jpg").convert("RGB").copy()
        d = ImageDraw.Draw(im); d.rectangle((0, 0, 120, 16), fill=(0, 0, 0)); d.text((4, 2), f.stem, fill="yellow")
        ims.append(im)
    cols = 6; rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (cols * 326, rows * 186), (30, 30, 30))
    for k, im in enumerate(ims): S.paste(im, ((k % cols) * 326, (k // cols) * 186))
    S.save(bd / "sheet.jpg", quality=85); print("sheet:", bd / "sheet.jpg")


def voice(vid):
    """Speak every line -> build/<id>/vo/<si>_<li>.wav. Returns total voice seconds."""
    import voice as V, numpy as np
    spec = load(vid); bd = build_dir(vid); (bd / "vo").mkdir(exist_ok=True)
    v = V.Voice(); total = 0.0
    for si, li, line in all_lines(spec):
        a = v.speak(line["say"], spec["voice"], spec.get("speed", 1.04))
        idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(idx[0] - 240, 0): idx[-1] + 2400]
        V.save_wav(bd / "vo" / f"{si}_{li}.wav", a); total += len(a) / V.SR
    if V.MISSING: print("WARNING spelled-out words (add to CUSTOM in voice.py):", sorted(V.MISSING))
    words = sum(len(l["say"].split()) for _, _, l in all_lines(spec))
    print(f"voice: {words} words, {total:.1f} s ({total / 60:.2f} min) of speech")
    return total


def render(vid):
    from render_long import render as do_render
    voice(vid)
    bd = build_dir(vid); out = ROOT / "videos" / vid / "final.mp4"
    info = do_render(ROOT / "videos" / vid / "script.json", bd, ROOT / "music", out)
    write_description(vid, info["chapters"])
    check(vid)


def fmt(t):
    t = int(t); return f"{t // 60:02d}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}"


def write_description(vid, chapters):
    """YouTube chapters from the REAL start times (first must be 00:00, each >= 10 s, at least 3)."""
    spec = load(vid)
    lines = [f"{fmt(t)} {name}" for t, name in chapters]
    (ROOT / "videos" / vid / "chapters.txt").write_text("\n".join(lines) + "\n")
    spec["chapters"] = lines
    spec["description"] = "\n\n".join([spec["description_intro"], "Chapters:\n" + "\n".join(lines),
                                       spec.get("sources_text", ""), spec.get("hashtags", "")]).strip()
    save(vid, spec)
    print("chapters:\n" + "\n".join(lines))


def check(vid):
    """Loudness of the finished file + a contact sheet of 12 frames (build/<id>/frames.jpg)."""
    from PIL import Image
    out = ROOT / "videos" / vid / "final.mp4"; bd = build_dir(vid)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                               capture_output=True, text=True).stdout)
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    summ = r[r.rfind("Summary:"):]
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", summ); peak = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    print(f"length {dur:.1f} s ({fmt(dur)}), loudness {lufs.group(1) if lufs else '?'} LUFS, true peak {peak.group(1) if peak else '?'} dBFS")
    ims = []
    for k in range(12):
        t = 1 + k * (dur - 2) / 11
        sh("ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=640:360", "/tmp/_fr.jpg")
        ims.append(Image.open("/tmp/_fr.jpg").copy())
    S = Image.new("RGB", (3 * 646, 4 * 366), (30, 30, 30))
    for k, im in enumerate(ims): S.paste(im, ((k % 3) * 646, (k // 3) * 366))
    S.save(bd / "frames.jpg", quality=85); print("frames:", bd / "frames.jpg")


if __name__ == "__main__":
    cmd, vid = sys.argv[1], sys.argv[2]
    if cmd == "stock":
        retry = sys.argv[sys.argv.index("--retry") + 1] if "--retry" in sys.argv else ""
        only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
        stock(vid, retry, only)
    elif cmd == "voice": voice(vid)
    elif cmd == "render": render(vid)
    elif cmd == "thumb":
        from thumbnail_long import make_all
        make_all(vid)
    elif cmd == "check": check(vid)
    elif cmd == "sheet": sheet(vid)
    elif cmd == "assign": assign_clips(vid)
