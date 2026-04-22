"""T08 AI re-run on cleaned N=50 corpus.

Matches V2 prompt + CLI invocation style (``src/ai_version/analyze.py``)
but parallelises the 3 creators and captures CLI-reported cost + usage
via ``--output-format json``.

Output schema per creator matches ``results/ai_metrics/<creator>.json``:
    {creator, n_videos, source, metrics: {8 keys}}
plus top-level ``cost_usd`` and ``runtime_s`` fields as required by T08.

A combined ``_run_summary.json`` captures per-creator token usage, wall
time, and total cost.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common.metrics_spec import METRICS, metrics_as_prompt_spec  # noqa: E402

# ---- Config -----------------------------------------------------------

# V2 used claude-haiku-4-5 via the `claude` CLI. Keep the same model +
# invocation path for behaviour consistency with the V2 AI baseline.
MODEL = "claude-haiku-4-5-20251001"

MAX_CHARS = 50_000  # same truncation as V2
COST_CAP_USD = 0.60

PROMPT_TEMPLATE = """You are a data analyst replicating IT-Mario's German YouTube vocabulary analysis.

I will give you one creator's combined transcript (auto-generated German subtitles,
possibly with English slang / Denglisch). Compute these metrics and return **only**
a JSON object — no prose, no markdown fences.

{spec}

Rules:
- `vocabulary_ttr`: unique tokens / total tokens (use lowercased alphabetic tokens).
- Keyword metrics: count occurrences of seed words (case-insensitive),
  normalize per 1000 tokens.
- `denglisch`: count English tokens per 1000 German tokens.
- `avg_word_len`: mean character length of tokens.
- `total_tokens`: raw token count.

Output shape:
{{"vocabulary_ttr": 0.0, "wealth_flex": 0.0, "drama_conflict": 0.0,
  "hype_adjectives": 0.0, "egocentrism": 0.0, "denglisch": 0.0,
  "avg_word_len": 0.0, "total_tokens": 0}}

Creator: {creator}
Transcript (truncated to 50k chars if longer):
---
{transcript}
---
Return only the JSON object."""


# ---- Helpers ----------------------------------------------------------

def parse_metric_json(raw: str) -> dict:
    """Extract first JSON object from raw text. Tolerant to code fences."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        raise ValueError(f"no JSON found in: {raw[:200]}")
    return json.loads(m.group(0))


def build_prompt(creator: str, transcript: str) -> str:
    if len(transcript) > MAX_CHARS:
        transcript = transcript[:MAX_CHARS]
    return PROMPT_TEMPLATE.format(
        spec=metrics_as_prompt_spec(),
        creator=creator,
        transcript=transcript,
    )


# ---- Core -------------------------------------------------------------

def run_one(creator: str, videos: list) -> dict:
    joined = " ".join(v["text"] for v in videos)
    prompt = build_prompt(creator, joined)

    t0 = time.time()
    # V2-style invocation: `claude -p --model ... <prompt>`
    # Add --output-format json for cost + usage capture.
    proc = subprocess.run(
        [
            "claude",
            "-p",
            "--output-format", "json",
            "--model", MODEL,
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    wall = time.time() - t0

    if proc.returncode != 0:
        raise RuntimeError(
            f"claude CLI exit {proc.returncode}: {proc.stderr[:500]}"
        )

    cli_out = json.loads(proc.stdout)
    if cli_out.get("is_error"):
        raise RuntimeError(f"CLI error: {cli_out.get('result', '')[:300]}")

    result_text = cli_out.get("result", "")
    metrics = parse_metric_json(result_text)
    usage = cli_out.get("usage", {})
    cost_usd = float(cli_out.get("total_cost_usd", 0.0))

    return {
        "creator": creator,
        "n_videos": len(videos),
        "source": "n50_clean",
        "metrics": metrics,
        # Required top-level fields from T08 spec:
        "cost_usd": round(cost_usd, 6),
        "runtime_s": round(wall, 3),
        # Extra metadata (kept — V2 schema allows it; compare.py only
        # reads creator / n_videos / metrics):
        "_meta": {
            "model": MODEL,
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
            "duration_api_ms": cli_out.get("duration_api_ms"),
            "prompt_chars": len(prompt),
        },
    }


def main() -> int:
    # The CLI uses OAuth from keychain when ANTHROPIC_API_KEY is absent —
    # we only hard-fail if there's no auth path at all.
    oauth = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not oauth and not api_key:
        # OAuth may still live in keychain — probe with a tiny call
        # rather than failing hard.
        print("note: neither ANTHROPIC_API_KEY nor CLAUDE_CODE_OAUTH_TOKEN set; "
              "relying on claude CLI keychain auth.", flush=True)

    data_dir = ROOT / "data" / "transcripts_n50_clean"
    if not data_dir.exists():
        print(f"ERROR: {data_dir} does not exist", file=sys.stderr)
        return 2
    out_dir = ROOT / "results" / "ai_metrics_n50"
    out_dir.mkdir(parents=True, exist_ok=True)

    creators = ["papaplatte", "apored", "maithinkx"]
    jobs = {}
    for creator in creators:
        jf = data_dir / f"{creator}.json"
        data = json.loads(jf.read_text())
        jobs[creator] = data["videos"]
        print(f"  [{creator}] {len(data['videos'])} videos loaded", flush=True)

    client_t0 = time.time()
    results = {}
    errors = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(run_one, c, v): c for c, v in jobs.items()}
        for fut in as_completed(futures):
            creator = futures[fut]
            try:
                results[creator] = fut.result()
                r = results[creator]
                meta = r["_meta"]
                print(
                    f"  [{creator}] done "
                    f"in={meta['input_tokens']} "
                    f"out={meta['output_tokens']} "
                    f"cache_read={meta['cache_read_input_tokens']} "
                    f"cache_create={meta['cache_creation_input_tokens']} "
                    f"wall={r['runtime_s']}s "
                    f"cost=${r['cost_usd']:.4f}",
                    flush=True,
                )
            except Exception as e:
                errors[creator] = repr(e)
                print(f"  [{creator}] ERROR {e!r}", file=sys.stderr, flush=True)
    total_wall = time.time() - client_t0

    if errors:
        print(f"ERRORS: {errors}", file=sys.stderr)

    # Write per-creator JSON (keep _meta inside the file — it's additive,
    # V2 callers that only read metrics / creator / n_videos are unaffected).
    summary = {
        "model": MODEL,
        "source": "n50_clean",
        "total_wall_seconds": round(total_wall, 3),
        "total_cost_usd": 0.0,
        "cost_cap_usd": COST_CAP_USD,
        "per_creator": {},
        "errors": errors,
    }
    for creator, r in results.items():
        out_path = out_dir / f"{creator}.json"
        out_path.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        meta = r["_meta"]
        summary["per_creator"][creator] = {
            "input_tokens": meta["input_tokens"],
            "output_tokens": meta["output_tokens"],
            "cache_read_input_tokens": meta["cache_read_input_tokens"],
            "cache_creation_input_tokens": meta["cache_creation_input_tokens"],
            "wall_seconds": r["runtime_s"],
            "cost_usd": r["cost_usd"],
            "prompt_chars": meta["prompt_chars"],
            "n_videos": r["n_videos"],
        }
        summary["total_cost_usd"] += r["cost_usd"]

    summary["total_cost_usd"] = round(summary["total_cost_usd"], 6)
    (out_dir / "_run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )

    print(
        f"\nTotal: ${summary['total_cost_usd']:.4f} across {len(results)} creators "
        f"in {total_wall:.2f}s wall"
    )
    if summary["total_cost_usd"] > COST_CAP_USD:
        print("WARN: exceeded cost cap", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
