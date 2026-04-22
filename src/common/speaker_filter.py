"""Speaker filter: extract only the creator's own speech from a transcript.

YouTube auto-captions don't tag speakers. A reaction streamer's transcript
includes clips, guests, movie audio, etc. — raw counting over-counts.

We ask Claude to classify spans by speaker and keep only the creator's.
For solo-presentation creators (e.g., MaiThinkX, ApoRed music videos)
this is a near-noop but still safe.

Runs one LLM call per video. Results are cached to data/filtered/.
"""
from __future__ import annotations
import json
import re
import subprocess
import time
from pathlib import Path


FILTER_PROMPT = """You are cleaning a YouTube auto-caption transcript.

Creator: {creator_desc}

The transcript below may contain:
- The creator's own speech (KEEP)
- Clips from other videos the creator is reacting to (REMOVE)
- Quotes from movies / games / external audio (REMOVE)
- Guest speakers (REMOVE unless clearly the host narrating)
- Sung lyrics in music videos (KEEP — it's still the creator)

Return the creator's own speech only. Preserve wording and order;
just remove the parts that aren't them. Do not summarize. Do not
add markdown. Output plain text only, nothing else.

If nearly all of the transcript is the creator (solo vlog, science
presentation, music video), return it unchanged.

Transcript:
---
{text}
---
Creator's own speech only:"""


CREATOR_DESC = {
    "papaplatte": "German streamer / reactor who watches and comments on clips",
    "apored": "German rapper — mostly music videos (lyrics are his)",
    "maithinkx": "German science journalist (Mai Thi Nguyen-Kim), solo presenter",
}


def filter_one(creator: str, text: str, timeout: int = 240,
               model: str = "claude-haiku-4-5-20251001") -> tuple[str, float]:
    prompt = FILTER_PROMPT.format(
        creator_desc=CREATOR_DESC.get(creator, f"German YouTuber {creator}"),
        text=text[:80_000],  # hard cap to stay in context
    )
    t0 = time.time()
    r = subprocess.run(
        ["claude", "-p", "--model", model, prompt],
        capture_output=True, text=True, timeout=timeout,
    )
    wall = time.time() - t0
    if r.returncode != 0:
        raise RuntimeError(f"filter failed: {r.stderr[:300]}")
    out = r.stdout.strip()
    # strip any accidental fences
    out = re.sub(r"^```[a-zA-Z]*\n?", "", out)
    out = re.sub(r"\n?```\s*$", "", out)
    return out, wall


def filter_creator(raw_path: Path, filtered_path: Path) -> dict:
    data = json.loads(raw_path.read_text())
    creator = data["creator"]
    out_videos = []
    total_wall = 0.0
    kept_chars = 0
    orig_chars = 0
    for i, v in enumerate(data["videos"]):
        orig = v["text"]
        orig_chars += len(orig)
        if len(orig) < 200:
            # too short to bother filtering
            filtered = orig
            wall = 0.0
        else:
            filtered, wall = filter_one(creator, orig)
            total_wall += wall
        kept_chars += len(filtered)
        out_videos.append({
            "id": v["id"], "title": v["title"],
            "text": filtered, "orig_chars": len(orig),
            "filtered_chars": len(filtered),
        })
        print(f"  [{creator}] {i+1}/{len(data['videos'])} "
              f"{len(orig)}→{len(filtered)} chars "
              f"({len(filtered)*100//max(len(orig),1)}%) in {wall:.1f}s",
              flush=True)
    out = {
        "creator": creator,
        "videos": out_videos,
        "kept_pct": round(kept_chars / max(orig_chars, 1) * 100, 1),
        "filter_wall_seconds": round(total_wall, 2),
    }
    filtered_path.parent.mkdir(parents=True, exist_ok=True)
    filtered_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    raw_dir = root / "data" / "transcripts"
    filt_dir = root / "data" / "transcripts_filtered"
    filt_dir.mkdir(parents=True, exist_ok=True)
    for jf in sorted(raw_dir.glob("*.json")):
        if jf.name.startswith("_"):
            continue
        print(f"\n=== filtering {jf.name} ===", flush=True)
        filter_creator(jf, filt_dir / jf.name)


if __name__ == "__main__":
    main()
