"""Runs on GitHub Actions: download Pixabay stock clips/photos for a request file.

Request file: requests/<id>.json
  {"id": "002-...", "items": [{"name": "s1", "q": "person typing laptop", "kind": "video"}, ...]}
Result: GitHub release "stock-<id>" with <name>.mp4 / <name>.jpg and manifest.json (sources).
Pixabay Content License: free for commercial use, no attribution required.
"""
import json, os, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

KEY = os.environ["PIXABAY_API_KEY"]
UA = {"User-Agent": "ai-daily-drop-stock/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def download(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


BLOCK = {"jesus", "christianity", "religion", "cross", "buddha", "buddhism", "meditation", "zen", "god", "church",
         "cartoon", "2d", "animated wallpaper", "nature animation video", "wallpaper engine", "sexy", "bikini",
         "lingerie", "green screen", "chroma key", "greenscreen", "chromakey", "transition", "glitch", "mockup", "weapon", "gun", "blood", "war", "flag", "politics"}


def relevance(q, tags):
    tags = [t.strip().lower() for t in (tags or "").split(",")]
    if any(t in BLOCK for t in tags): return -1
    words = [w for w in q.lower().split() if len(w) > 2]
    text = " ".join(tags)
    return sum(1 for w in words if w in text or w.rstrip("s") in text) / max(1, len(words))


def pick_video(q, used, min_dur=4, max_dur=60):
    data = get("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": KEY, "q": q, "per_page": 30, "safesearch": "true", "order": "popular"}))
    best = None
    for h in data.get("hits", []):
        if h["id"] in used or not min_dur <= h.get("duration", 0) <= max_dur: continue
        rel = relevance(q, h.get("tags"))
        if rel < 0.34: continue
        vids = {k: v for k, v in h["videos"].items() if v.get("url") and v.get("width")}
        if not vids: continue
        vertical = any(v["height"] > v["width"] for v in vids.values())
        # want a file that can fill 1080x1920 after a centre crop, without huge 4K downloads when possible
        def ok(v):
            return (v["width"] >= 1080 and v["height"] >= 1920) if v["height"] > v["width"] else v["height"] >= 2160
        cands = sorted(vids.values(), key=lambda v: (not ok(v), v.get("size", 0) or v["width"] * v["height"]))
        f = cands[0]
        if not ok(f):
            f = max(vids.values(), key=lambda v: v["width"] * v["height"])
        score = (round(rel, 1), ok(f), vertical, h.get("likes", 0) + h.get("downloads", 0) / 50)
        if best is None or score > best[0]:
            best = (score, h, f)
    return (best[1], best[2]) if best else (None, None)


def pick_photo(q, used):
    data = get("https://pixabay.com/api/?" + urllib.parse.urlencode(
        {"key": KEY, "q": q, "image_type": "photo", "orientation": "vertical", "per_page": 30,
         "safesearch": "true", "min_height": 1920}))
    hits = [h for h in data.get("hits", []) if h["id"] not in used and relevance(q, h.get("tags")) >= 0.34]
    hits.sort(key=lambda h: -relevance(q, h.get("tags")))
    return hits[0] if hits else None
    return None


def main():
    out_root = Path("stock_out"); out_root.mkdir(exist_ok=True)
    for req_path in sorted(Path("requests").glob("*.json")):
        req = json.load(open(req_path))
        tag = f"stock-{req['id']}"
        if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0:
            print("skip", tag); continue
        out = out_root / req["id"]; out.mkdir(exist_ok=True)
        manifest, used = [], set()
        for item in req["items"]:
            try:
                if item.get("kind", "video") == "video":
                    h, f = pick_video(item["q"], used)
                    if not h:
                        manifest.append({"name": item["name"], "q": item["q"], "error": "no result"}); continue
                    used.add(h["id"]); dest = out / f"{item['name']}.mp4"
                    download(f["url"], dest)
                    manifest.append({"name": item["name"], "q": item["q"], "file": dest.name, "kind": "video",
                                     "source": h["pageURL"], "author": h.get("user"), "duration": h["duration"],
                                     "width": f["width"], "height": f["height"], "tags": h.get("tags")})
                else:
                    h = pick_photo(item["q"], used)
                    if not h:
                        manifest.append({"name": item["name"], "q": item["q"], "error": "no result"}); continue
                    used.add(h["id"]); dest = out / f"{item['name']}.jpg"
                    download(h["largeImageURL"], dest)
                    manifest.append({"name": item["name"], "q": item["q"], "file": dest.name, "kind": "photo",
                                     "source": h["pageURL"], "author": h.get("user"), "tags": h.get("tags")})
                print("ok", item["name"], item["q"])
            except Exception as e:
                manifest.append({"name": item["name"], "q": item["q"], "error": str(e)})
                print("fail", item["name"], e, file=sys.stderr)
        (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
        subprocess.run(["gh", "release", "create", tag, *[str(p) for p in out.iterdir()], "--title", tag,
                        "--notes", "Pixabay stock media (Pixabay Content License). Sources in manifest.json."], check=True)
        print("released", tag)


if __name__ == "__main__":
    main()
