"""Scrape a small sample of YouTube transcripts via yt-dlp.

Writes one JSON per creator: {creator, videos: [{id, title, text}], meta: {...}}
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CREATORS = {
    "papaplatte": "https://www.youtube.com/@papaplatte/videos",
    "apored": "https://www.youtube.com/@ApoRed/videos",
    "maithinkx": "https://www.youtube.com/@maithinkx/videos",
}


def list_recent_videos(channel_url: str, n: int = 5) -> list[dict]:
    """Return up to n recent videos via yt-dlp flat playlist."""
    cmd = [
        "yt-dlp", "--flat-playlist", "--playlist-end", str(n),
        "--print", "%(id)s\t%(title)s", channel_url,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    vids = []
    for line in out.stdout.strip().splitlines():
        if "\t" in line:
            vid, title = line.split("\t", 1)
            vids.append({"id": vid.strip(), "title": title.strip()})
    return vids


def download_transcript(video_id: str, out_dir: Path) -> str | None:
    """Download auto-generated German subtitles, return cleaned plain text."""
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"t_{video_id}"
    cmd = [
        "yt-dlp", "--write-auto-subs", "--write-subs",
        "--sub-langs", "de,de-orig", "--skip-download",
        "--sub-format", "vtt", "-o", str(out_dir / f"{prefix}"),
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    # find the VTT file
    for p in out_dir.glob(f"{prefix}.*.vtt"):
        return _vtt_to_plain(p.read_text(encoding="utf-8", errors="ignore"))
    return None


def _vtt_to_plain(vtt: str) -> str:
    lines = []
    for raw in vtt.split("\n"):
        l = raw.strip()
        if not l or "-->" in l:
            continue
        if l.startswith(("WEBVTT", "Kind:", "Language:", "NOTE", "STYLE", "align:", "position:")):
            continue
        l = re.sub(r"<[^>]+>", "", l)
        if not lines or lines[-1] != l:
            lines.append(l)
    return " ".join(lines)


def main(per_creator: int = 3) -> None:
    root = Path(__file__).resolve().parents[2] / "data" / "transcripts"
    root.mkdir(parents=True, exist_ok=True)
    for creator, url in CREATORS.items():
        print(f"\n[{creator}] listing videos...", flush=True)
        vids = list_recent_videos(url, per_creator)
        print(f"  got {len(vids)} video ids", flush=True)
        out = {"creator": creator, "videos": []}
        for v in vids:
            print(f"  fetching {v['id']}: {v['title'][:60]}", flush=True)
            text = download_transcript(v["id"], root / "_raw")
            if text:
                out["videos"].append({"id": v["id"], "title": v["title"], "text": text})
            time.sleep(1)
        (root / f"{creator}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"  saved {len(out['videos'])} transcripts to {creator}.json", flush=True)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(n)
