"""Fetch 50 videos for apored and maithinkx (papaplatte already done).

Skips video IDs already present in the existing N=25 corpus to avoid
duplicates; tops up to 50 per creator.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from common.fetch import CREATORS, list_recent_videos, download_transcript  # noqa: E402

TARGET = 50
N50_DIR = ROOT / "data" / "transcripts_n50"
N50_DIR.mkdir(parents=True, exist_ok=True)
RAW_OUT = N50_DIR / "_raw"


def fetch_creator(creator: str) -> None:
    existing_path = ROOT / "data" / "transcripts" / f"{creator}.json"
    existing = json.loads(existing_path.read_text())["videos"]
    existing_ids = {v["id"] for v in existing}
    print(f"[{creator}] have {len(existing_ids)} existing; target {TARGET}")
    # list more than we need to cover skips
    candidates = list_recent_videos(CREATORS[creator], n=TARGET + 30)
    print(f"[{creator}] listed {len(candidates)} candidates from channel")
    kept = list(existing)
    seen = set(existing_ids)
    for v in candidates:
        if len(kept) >= TARGET:
            break
        if v["id"] in seen:
            continue
        print(f"  fetch {v['id']}: {v['title'][:60]}", flush=True)
        text = download_transcript(v["id"], RAW_OUT)
        if text and len(text) > 500:
            kept.append({"id": v["id"], "title": v["title"], "text": text})
            seen.add(v["id"])
        time.sleep(0.5)
    (N50_DIR / f"{creator}.json").write_text(
        json.dumps({"creator": creator, "videos": kept},
                   ensure_ascii=False, indent=2)
    )
    print(f"[{creator}] saved {len(kept)} videos")


def main() -> None:
    # papaplatte already done
    for c in ["apored", "maithinkx"]:
        if (N50_DIR / f"{c}.json").exists():
            d = json.loads((N50_DIR / f"{c}.json").read_text())
            if len(d.get("videos", [])) >= TARGET:
                print(f"[{c}] already has {len(d['videos'])} — skipping")
                continue
        fetch_creator(c)


if __name__ == "__main__":
    main()
