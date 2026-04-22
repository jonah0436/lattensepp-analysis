"""Fetch YouTube comments via yt-dlp for community-signal analysis.

Uses yt-dlp --write-comments (no extra dependency). Picks the first
N videos from data/transcripts_n50/{creator}.json and stores one JSON
per video at data/comments/{creator}/{video_id}.json plus a summary at
data/comments/{creator}/_pilot_summary.json.

Usage:
    python bench/fetch_comments.py --creator papaplatte \
        --n-videos 5 --comments-per-video 200
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_creator_videos(creator: str) -> list[dict[str, Any]]:
    path = ROOT / "data" / "transcripts_n50" / f"{creator}.json"
    if not path.exists():
        raise FileNotFoundError(f"no transcripts file at {path}")
    data = json.loads(path.read_text())
    return data["videos"]


def pick_videos(
    videos: list[dict[str, Any]], n: int, mode: str = "first"
) -> list[dict[str, Any]]:
    if mode == "first":
        return videos[:n]
    if mode == "random":
        import random
        rng = random.Random(42)
        return rng.sample(videos, min(n, len(videos)))
    raise ValueError(f"unknown mode: {mode}")


RETRY_DELAYS_S = (2, 4, 8)


def _fetch_comments_ytdlp_once(
    video_id: str, max_comments: int, timeout_s: int = 300
) -> tuple[list[dict[str, Any]], str | None, str | None]:
    """Single attempt. Return (comments, title, error)."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    # max_comments syntax: max_comments,thread_sort,reply_sort,reply_max
    # Sort by "top" to get the highest-signal comments.
    extractor_args = (
        f"youtube:max_comments={max_comments},all,{max_comments},{max_comments}"
        ";comment_sort=top"
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out_tpl = str(tmp_path / "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-info-json",
            "--write-comments",
            "--extractor-args", extractor_args,
            "-o", out_tpl,
            url,
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.CalledProcessError as e:
            return [], None, f"yt-dlp failed: {e.stderr[-400:].strip()}"
        except subprocess.TimeoutExpired:
            return [], None, f"yt-dlp timeout after {timeout_s}s"

        info_path = tmp_path / f"{video_id}.info.json"
        if not info_path.exists():
            matches = list(tmp_path.glob("*.info.json"))
            if not matches:
                return [], None, "no info.json produced"
            info_path = matches[0]

        info = json.loads(info_path.read_text())
        title = info.get("title")
        raw = info.get("comments") or []
        comments = []
        for c in raw:
            ts = c.get("timestamp")
            published = (
                datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                if ts else (c.get("_time_text") or c.get("time_text"))
            )
            comments.append({
                "text": c.get("text") or "",
                "author": c.get("author") or "",
                "likes": c.get("like_count") or 0,
                "published": published,
                "parent": c.get("parent"),
                "is_pinned": bool(c.get("is_pinned")),
            })
        return comments, title, None


def fetch_comments_ytdlp(
    video_id: str,
    max_comments: int,
    timeout_s: int = 300,
    retry_delays_s: tuple[int, ...] = RETRY_DELAYS_S,
) -> tuple[list[dict[str, Any]], str | None, str | None]:
    """Return (comments, title, error) with exponential-backoff retry.

    Retries up to len(retry_delays_s) times on yt-dlp errors/timeouts.
    Logs each retry but does not raise; callers get the final error.
    """
    last_err: str | None = None
    attempts = 1 + len(retry_delays_s)
    for attempt in range(1, attempts + 1):
        comments, title, err = _fetch_comments_ytdlp_once(
            video_id, max_comments, timeout_s=timeout_s
        )
        if err is None:
            if attempt > 1:
                print(
                    f"    retry succeeded on attempt {attempt}/{attempts}",
                    flush=True,
                )
            return comments, title, None
        last_err = err
        if attempt < attempts:
            delay = retry_delays_s[attempt - 1]
            print(
                f"    attempt {attempt}/{attempts} failed "
                f"({err[:120]!s}); retrying in {delay}s",
                flush=True,
            )
            time.sleep(delay)
    return [], None, last_err


def run_pilot(
    creator: str,
    n_videos: int,
    comments_per_video: int,
    mode: str = "first",
    sleep_s: float = 1.0,
    skip_existing: bool = False,
    summary_name: str = "_pilot_summary.json",
) -> dict[str, Any]:
    """Fetch comments for the first N videos of a creator.

    When ``skip_existing=True``, videos that already have a JSON file on
    disk are loaded from there instead of being re-fetched. The returned
    summary still covers all N picked videos so downstream code can rely
    on it for full per-creator counts.
    """
    out_dir = ROOT / "data" / "comments" / creator
    out_dir.mkdir(parents=True, exist_ok=True)

    videos = load_creator_videos(creator)
    picked = pick_videos(videos, n_videos, mode=mode)
    print(f"[{creator}] picked {len(picked)} videos (mode={mode})")

    summary: dict[str, Any] = {
        "creator": creator,
        "mode": mode,
        "comments_per_video_target": comments_per_video,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "videos": [],
    }

    total_comments = 0
    for i, v in enumerate(picked, 1):
        vid = v["id"]
        title_hint = v.get("title", "")[:80]
        out_path = out_dir / f"{vid}.json"

        if skip_existing and out_path.exists():
            try:
                existing = json.loads(out_path.read_text())
                cached_count = int(existing.get("comment_count", 0))
            except (json.JSONDecodeError, ValueError):
                cached_count = 0
            print(
                f"  [{i}/{len(picked)}] {vid}  (cached, "
                f"{cached_count} comments)"
            )
            total_comments += cached_count
            summary["videos"].append({
                "video_id": vid,
                "title": existing.get("video_title", title_hint),
                "comment_count": cached_count,
                "seconds": 0.0,
                "error": None,
                "cached": True,
            })
            continue

        print(f"  [{i}/{len(picked)}] {vid}  {title_hint}", flush=True)
        t0 = time.time()
        comments, title, err = fetch_comments_ytdlp(vid, comments_per_video)
        elapsed = time.time() - t0
        if err:
            print(f"    ERROR: {err}  ({elapsed:.1f}s)")
            summary["videos"].append({
                "video_id": vid,
                "title": title or title_hint,
                "comment_count": 0,
                "seconds": round(elapsed, 1),
                "error": err,
            })
            time.sleep(sleep_s)
            continue

        record = {
            "video_id": vid,
            "video_title": title or title_hint,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "comment_count": len(comments),
            "comments": comments,
        }
        out_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2)
        )
        total_comments += len(comments)
        print(f"    got {len(comments)} comments ({elapsed:.1f}s)")
        summary["videos"].append({
            "video_id": vid,
            "title": record["video_title"],
            "comment_count": len(comments),
            "seconds": round(elapsed, 1),
            "error": None,
        })
        time.sleep(sleep_s)

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    summary["total_comments"] = total_comments
    (out_dir / summary_name).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    print(
        f"[{creator}] done: {total_comments} comments across "
        f"{len(picked)} videos"
    )
    return summary


def main() -> None:
    if not shutil.which("yt-dlp"):
        print("ERROR: yt-dlp not found on PATH", file=sys.stderr)
        sys.exit(2)

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--creator", required=True,
                    help="one of papaplatte / apored / maithinkx")
    ap.add_argument("--n-videos", type=int, default=5)
    ap.add_argument("--comments-per-video", type=int, default=200)
    ap.add_argument("--mode", choices=["first", "random"], default="first")
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="seconds between videos (rate-limit buffer)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="reuse existing data/comments/{creator}/{id}.json "
                         "files instead of re-fetching")
    ap.add_argument("--summary-name", default="_pilot_summary.json",
                    help="filename written under data/comments/{creator}/")
    args = ap.parse_args()

    run_pilot(
        creator=args.creator,
        n_videos=args.n_videos,
        comments_per_video=args.comments_per_video,
        mode=args.mode,
        sleep_s=args.sleep,
        skip_existing=args.skip_existing,
        summary_name=args.summary_name,
    )


if __name__ == "__main__":
    main()
