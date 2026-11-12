"""One-stop pipeline for an AI Daily Drop Short.

Folder: videos/<id>/script.json  (see videos/001v2/script.json for the format)
In the script, each scene may have "footage": ["search words", ...] (one entry per clip, 2-3 per scene).

    python3 engine/make_short.py stock  <id>   # writes requests/<id>.json, pushes, waits, downloads clips, makes sheet.jpg
    python3 engine/make_short.py render <id>   # voiceover + full render -> videos/<id>/final.mp4
    python3 engine/make_short.py sheet  <id>   # contact sheet of downloaded clips (build/<id>/sheet.jpg)

Clips land in build/<id>/stock/<scene>_<n>.mp4. To swap a bad clip, edit the scene's "clips" list in
script.json (file names, optional "@start" seconds), or change its "footage" words and run stock again
with a new request id suffix:  python3 engine/make_short.py stock <id> --retry b --only s2_0,s4_1
"""
import json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "aidailydropchannel-coder/ai-daily-drop-videos"
sys.path.insert(0, str(ROOT / "engine"))


def sh(*cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def load(vid):
    return json.load(open(ROOT / "videos" / vid / "script.json"))


def save(vid, spec):
    json.dump(spec, open(ROOT / "videos" / vid / "script.json", "w"), indent=1, ensure_ascii=False)


def build_dir(vid):
    d = ROOT / "build" / vid; (d / "stock").mkdir(parents=True, exist_ok=True); return d


def stock(vid, retry="", only=None):
    spec = load(vid); req_id = vid + (f"-{retry}" if retry else "")
    items = []
    for i, sc in enumerate(spec["scenes"]):
        for n, q in enumerate(sc.get("footage", [])):
            name = f"s{i}_{n}"
            if only and name not in only: continue
            items.append({"name": name, "q": q, "kind": "video"})
    (ROOT / "requests").mkdir(exist_ok=True)
    json.dump({"id": req_id, "items": items}, open(ROOT / "requests" / f"{req_id}.json", "w"), indent=1)
    sh("git", "-C", str(ROOT), "add", "requests", f"videos/{vid}")
    sh("git", "-C", str(ROOT), "commit", "-qm", f"Stock request {req_id}")
    sh("git", "-C", str(ROOT), "push", "-q", "origin", "HEAD:main")
    base = f"https://github.com/{REPO}/releases/download/stock-{req_id}/"
    print("waiting for GitHub Action...", flush=True)
    for _ in range(40):
        time.sleep(15)
        r = subprocess.run(["curl", "-sSL", "-o", "/tmp/manifest.json", "-w", "%{http_code}", base + "manifest.json"],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200": break
    else:
        raise SystemExit("stock release did not appear in 10 min - check the Actions tab on GitHub")
    man = json.load(open("/tmp/manifest.json")); bd = build_dir(vid)
    for m in man:
        if "file" in m:
            sh("curl", "-sSL", "-o", str(bd / "stock" / m["file"]), base + m["file"])
            print("ok ", m["name"], m["q"], "|", (m.get("tags") or "")[:80])
        else:
            print("ERR", m["name"], m["q"], m.get("error"))
    old = bd / "stock" / "manifest.json"
    merged = (json.load(open(old)) if old.exists() else [])
    merged = [x for x in merged if x["name"] not in {m["name"] for m in man}] + man
    json.dump(merged, open(old, "w"), indent=1)
    # default clip assignment
    have = {m["name"] for m in merged if "file" in m}
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("footage"):
            sc["clips"] = [f"s{i}_{n}.mp4@1" for n in range(len(sc["footage"])) if f"s{i}_{n}" in have]
    save(vid, spec)
    sheet(vid)


def sheet(vid):
    from PIL import Image, ImageDraw
    bd = build_dir(vid); ims = []
    for f in sorted((bd / "stock").glob("*.mp4")):
        sh("ffmpeg", "-loglevel", "error", "-y", "-ss", "1.5", "-i", str(f), "-frames:v", "1", "-vf",
           "scale=-2:280", "/tmp/_s.jpg")
        im = Image.open("/tmp/_s.jpg").copy(); ImageDraw.Draw(im).text((6, 6), f.stem, fill="yellow"); ims.append(im)
    if not ims: return
    rows, row, w = [], [], 0
    for im in ims:
        if w + im.width > 2000 and row: rows.append(row); row, w = [], 0
        row.append(im); w += im.width + 6
    rows.append(row)
    S = Image.new("RGB", (2000, 286 * len(rows)), (30, 30, 30))
    for r, rw in enumerate(rows):
        x = 0
        for im in rw: S.paste(im, (x, r * 286)); x += im.width + 6
    S.save(bd / "sheet.jpg", quality=85); print("sheet:", bd / "sheet.jpg")


def render(vid):
    import voice as V, numpy as np
    from render import render as do_render
    spec = load(vid); bd = build_dir(vid)
    v = V.Voice()
    for i, sc in enumerate(spec["scenes"]):
        a = v.speak(sc["say"], spec["voice"], spec.get("speed", 1.08))
        idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(idx[0] - 240, 0): idx[-1] + 2400]
        V.save_wav(bd / f"vo_{i}.wav", a)
    if V.MISSING: print("WARNING spelled-out words (add to CUSTOM in voice.py):", sorted(V.MISSING))
    out = ROOT / "videos" / vid / "final.mp4"
    do_render(str(ROOT / "videos" / vid / "script.json"), str(bd), str(ROOT / "music"), str(out),
              stock_dir=str(bd / "stock"))
    for t in (0.5, 6, 14, 22, 30):
        sh("ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", "-vf", "scale=360:-2",
           str(bd / f"check_{t}.jpg"))
    print("check frames:", bd)
    from thumbnail import make as make_thumb
    make_thumb(vid)


if __name__ == "__main__":
    cmd, vid = sys.argv[1], sys.argv[2]
    if cmd == "stock":
        retry = sys.argv[sys.argv.index("--retry") + 1] if "--retry" in sys.argv else ""
        only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
        stock(vid, retry, only)
    elif cmd == "render": render(vid)
    elif cmd == "sheet": sheet(vid)
