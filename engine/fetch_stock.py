"""Runs on GitHub Actions: download Pexels stock clips/photos for a request file.

Request file: requests/<id>.json
  {"id": "002-...", "items": [{"name": "s1", "q": "person typing laptop night", "kind": "video"}, ...]}
Result: GitHub release "stock-<id>" with <name>.mp4 / <name>.jpg and manifest.json (credits).
"""
import json, os, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

KEY = os.environ["PEXELS_API_KEY"]
UA = {"Authorization": KEY, "User-Agent": "ai-daily-drop-stock/1.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def pick_video(q, used):
    for orientation in ("portrait", None):
        params = {"query": q, "per_page": 15, "size": "medium"}
        if orientation: params["orientation"] = orientation
        data = get("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(params))
        for v in data.get("videos", []):
            if v["id"] in used or not 4 <= v.get("duration", 0) <= 40: continue
            files = [f for f in v["video_files"] if f.get("file_type") == "video/mp4" and f.get("height")]
            portrait = orientation == "portrait"
            # prefer ~1080-wide portrait or >=1080 tall landscape, avoid giant 4K files
            files.sort(key=lambda f: (abs((f["width"] if portrait else f["height"]) - 1080), f["width"] * f["height"]))
            if files:
                return v, files[0]
    return None, None


def pick_photo(q, used):
    data = get("https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "per_page": 15, "orientation": "portrait"}))
    for p in data.get("photos", []):
        if p["id"] not in used:
            return p
    return None


def main():
    out_root = Path("stock_out"); out_root.mkdir(exist_ok=True)
    for req_path in sorted(Path("requests").glob("*.json")):
        req = json.load(open(req_path))
        tag = f"stock-{req['id']}"
        exists = subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0
        if exists:
            print("skip", tag); continue
        out = out_root / req["id"]; out.mkdir(exist_ok=True)
        manifest, used = [], set()
        for item in req["items"]:
            try:
                if item.get("kind", "video") == "video":
                    v, f = pick_video(item["q"], used)
                    if not v:
                        manifest.append({"name": item["name"], "q": item["q"], "error": "no result"}); continue
                    used.add(v["id"]); dest = out / f"{item['name']}.mp4"
                    download(f["link"], dest)
                    manifest.append({"name": item["name"], "q": item["q"], "file": dest.name, "kind": "video",
                                     "pexels_url": v["url"], "author": v["user"]["name"], "duration": v["duration"],
                                     "width": f["width"], "height": f["height"]})
                else:
                    p = pick_photo(item["q"], used)
                    if not p:
                        manifest.append({"name": item["name"], "q": item["q"], "error": "no result"}); continue
                    used.add(p["id"]); dest = out / f"{item['name']}.jpg"
                    download(p["src"]["large2x"], dest)
                    manifest.append({"name": item["name"], "q": item["q"], "file": dest.name, "kind": "photo",
                                     "pexels_url": p["url"], "author": p["photographer"]})
                print("ok", item["name"], item["q"])
            except Exception as e:
                manifest.append({"name": item["name"], "q": item["q"], "error": str(e)})
                print("fail", item["name"], e, file=sys.stderr)
        (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
        files = [str(p) for p in out.iterdir()]
        subprocess.run(["gh", "release", "create", tag, *files, "--title", tag,
                        "--notes", "Pexels stock media (free to use, see manifest.json for credits)"], check=True)
        print("released", tag)


if __name__ == "__main__":
    main()
