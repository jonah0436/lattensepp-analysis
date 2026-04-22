"""Livestream VOD filter for the N=50 corpus (T02).

Classifies each video as a livestream VOD using the heuristic:
    duration > 60 minutes
    AND (title contains a live keyword OR metadata flags live content)

Duration is derived from the last timestamp in the associated VTT
caption file under data/transcripts/_raw or data/transcripts_n50/_raw,
since the corpus JSON only stores {id, title, text}. Live-status
yt-dlp fields (is_live, was_live, live_status, release_timestamp)
are not captured in this corpus, so only the duration + title-keyword
branch of the heuristic fires in practice; the metadata hook is kept
for forward compatibility if the corpus is re-fetched with richer
yt-dlp --print fields.

Writes cleaned corpus to data/transcripts_n50_clean/{creator}.json
and per-creator counts to results/livestream_filter_log.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data" / "transcripts_n50"
CLEAN_DIR = ROOT / "data" / "transcripts_n50_clean"
LOG_PATH = ROOT / "results" / "livestream_filter_log.json"
RAW_DIRS = (
    ROOT / "data" / "transcripts_n50" / "_raw",
    ROOT / "data" / "transcripts" / "_raw",
)

CREATORS = ("apored", "maithinkx", "papaplatte")

# Keywords checked against lowercased title. "stream" intentionally
# loose per TASKS.md spec; may over-flag but duration gate keeps
# non-livestreams in.
LIVE_TITLE_KEYWORDS = ("live", "livestream", "stream")

DURATION_THRESHOLD_SECONDS = 60 * 60  # 60 minutes

# VTT timestamp regex: HH:MM:SS.mmm
TS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})")


def _ts_to_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def vtt_duration_seconds(video_id: str) -> float | None:
    """Return duration in seconds from the last timestamp in the VTT.

    Tries both raw dirs; prefers the non -orig caption track.
    Returns None if no VTT is found or parseable.
    """
    candidates: list[Path] = []
    for raw in RAW_DIRS:
        if not raw.exists():
            continue
        # Prefer de.vtt over de-orig.vtt (cleaner timing lines).
        de = raw / f"t_{video_id}.de.vtt"
        orig = raw / f"t_{video_id}.de-orig.vtt"
        if de.exists():
            candidates.append(de)
        if orig.exists():
            candidates.append(orig)
    for p in candidates:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        last = None
        for m in TS_RE.finditer(text):
            last = m
        if last is None:
            continue
        # The final timestamp we see is the end of the last cue
        # (YouTube auto-captions list "--> END"). Take the max
        # timestamp as an upper bound on duration.
        all_secs = [
            _ts_to_seconds(*mm.groups())
            for mm in TS_RE.finditer(text)
        ]
        if all_secs:
            return max(all_secs)
    return None


def title_has_live_keyword(title: str) -> tuple[bool, str | None]:
    t = title.lower()
    for kw in LIVE_TITLE_KEYWORDS:
        # Word-ish boundary: avoid matching inside longer unrelated
        # words. Accept hyphen, slash, digit boundaries common in
        # YouTube titles.
        if re.search(rf"(?:^|[^a-z]){re.escape(kw)}(?:$|[^a-z])", t):
            return True, kw
    return False, None


def metadata_flags_live(video: dict) -> tuple[bool, str | None]:
    """Forward-compatible check against yt-dlp live fields.

    The current corpus does not carry these fields; this is a no-op
    in practice but keeps the heuristic faithful to the task spec.
    """
    for key in ("is_live", "was_live", "live_status"):
        val = video.get(key)
        if val in (True, "is_live", "was_live", "post_live"):
            return True, key
    return False, None


def classify(video: dict, duration_s: float | None) -> tuple[bool, str | None]:
    """Return (is_livestream_vod, reason).

    Heuristic per TASKS.md T02:
        duration > 60 minutes
        AND (title live keyword OR metadata live flag)
    """
    if duration_s is None or duration_s <= DURATION_THRESHOLD_SECONDS:
        return False, None
    kw_hit, kw = title_has_live_keyword(video.get("title", ""))
    meta_hit, meta_key = metadata_flags_live(video)
    if kw_hit or meta_hit:
        reasons = []
        reasons.append(f"duration={duration_s / 60:.1f}min>60")
        if kw_hit:
            reasons.append(f"title_kw='{kw}'")
        if meta_hit:
            reasons.append(f"metadata_flag='{meta_key}'")
        return True, "; ".join(reasons)
    return False, None


def process_creator(creator: str) -> dict:
    src = SRC_DIR / f"{creator}.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    videos: Iterable[dict] = data.get("videos", [])

    kept: list[dict] = []
    excluded: list[dict] = []

    for v in videos:
        duration = vtt_duration_seconds(v["id"])
        is_livestream, reason = classify(v, duration)
        if is_livestream:
            excluded.append({
                "id": v["id"],
                "title": v["title"],
                "duration": round(duration, 1) if duration else None,
                "reason": reason,
            })
        else:
            kept.append(v)

    # Preserve original schema: {creator, videos: [...]}.
    clean_out = {"creator": data.get("creator", creator), "videos": kept}
    (CLEAN_DIR / f"{creator}.json").write_text(
        json.dumps(clean_out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "excluded_count": len(excluded),
        "kept_count": len(kept),
        "excluded": excluded,
    }


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    log: dict[str, dict] = {}
    for creator in CREATORS:
        log[creator] = process_creator(creator)
        print(
            f"[{creator}] kept={log[creator]['kept_count']} "
            f"excluded={log[creator]['excluded_count']}"
        )
        for ex in log[creator]["excluded"]:
            print(f"  - {ex['id']} ({ex['duration']}s) :: {ex['title'][:60]}")

    LOG_PATH.write_text(
        json.dumps(log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nwrote {LOG_PATH}")
    print(f"wrote cleaned corpus to {CLEAN_DIR}")


if __name__ == "__main__":
    main()
