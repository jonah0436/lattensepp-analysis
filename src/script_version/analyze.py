"""Version B: grep/script replica of IT-Mario's analysis.

Deterministic. Pure word counting with seed lists from metrics_spec.
Can run on raw OR filtered transcripts, and on a subset of the first N
videos per creator (to study sample-size effects).
"""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.metrics_spec import METRICS  # noqa: E402


ENGLISH_SAMPLE = {
    "the", "is", "are", "and", "but", "for", "you", "your", "my", "our", "their",
    "real", "talk", "content", "good", "bad", "nice", "bro", "mate",
    "insane", "crazy", "wild", "easy", "hard", "fucking", "shit", "damn",
    "yeah", "nope", "yes", "stuff", "thing", "things",
    "flex", "flexing", "like", "love", "hate", "vibe", "vibes",
    "random", "chat", "stream", "streamer", "clip", "clips", "video",
    "youtube", "twitch", "gaming", "gameplay", "match", "win", "lose",
    "cool", "dope", "lit", "fire", "banger", "savage", "based", "cringe",
    "mindset", "hustle", "grind", "flow", "feature", "boost",
    "hello", "hi", "hey", "what", "why", "how", "when", "where",
    "one", "two", "three", "go", "let", "lets", "come", "get",
    "fuck", "fucked", "ass", "bitch", "man", "dude", "yo",
    "check", "checked", "fine", "okay", "ok", "baby", "honey",
    "money", "cash", "rich", "poor", "boy", "girl", "woman", "people",
    "life", "live", "time", "love", "see", "make", "take", "done",
    "back", "front", "up", "down", "left", "right", "in", "out",
    "off", "on", "by", "to", "of", "it", "at", "this", "that",
}

_TOKEN_RE = re.compile(r"[a-zA-ZäöüÄÖÜß]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def compute_metrics(tokens: list[str]) -> dict[str, float]:
    total = len(tokens) or 1
    unique = len(set(tokens))
    out: dict[str, float] = {}
    for m in METRICS:
        if m.key == "vocabulary_ttr":
            out[m.key] = unique / total
        elif m.key == "total_tokens":
            out[m.key] = float(total)
        elif m.kind == "keyword_count":
            kw = {k.lower() for k in m.keywords}
            hits = sum(1 for t in tokens if t in kw)
            out[m.key] = hits / total * 1000
        elif m.kind == "english_count":
            hits = sum(1 for t in tokens if t in ENGLISH_SAMPLE)
            out[m.key] = hits / total * 1000
        elif m.kind == "avg_word_len":
            out[m.key] = sum(len(t) for t in tokens) / total
    return out


def run(data_dir: Path, out_path: Path, n: int | None = None,
        source_label: str = "raw") -> dict:
    """Run script analysis. n = take first N videos per creator (None = all)."""
    t0 = time.time()
    results = {"version": "script", "source": source_label, "n": n,
               "per_creator": {}}
    for jf in sorted(data_dir.glob("*.json")):
        if jf.name.startswith("_"):
            continue
        data = json.loads(jf.read_text())
        vids = data["videos"] if n is None else data["videos"][:n]
        joined = " ".join(v["text"] for v in vids)
        tokens = tokenize(joined)
        results["per_creator"][data["creator"]] = {
            "n_videos": len(vids),
            "metrics": compute_metrics(tokens),
        }
    results["wall_seconds"] = round(time.time() - t0, 4)
    results["cost_usd"] = 0.0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    return results


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    source = sys.argv[2] if len(sys.argv) > 2 else "raw"
    data_dir = root / "data" / (
        "transcripts_filtered" if source == "filtered" else "transcripts"
    )
    out = root / "results" / f"script_{source}_n{n or 'all'}.json"
    r = run(data_dir, out, n=n, source_label=source)
    print(json.dumps(r, ensure_ascii=False, indent=2))
