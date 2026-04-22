"""Version A: AI-driven replica of IT-Mario's analysis.

Sends transcripts + metric spec to Claude, asks for a JSON object of metrics.
Uses the `claude` CLI (with -p / --print). Matches the script version's
output shape for apples-to-apples comparison.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.metrics_spec import METRICS, metrics_as_prompt_spec  # noqa: E402


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


def call_claude(prompt: str, timeout: int = 180) -> tuple[str, float]:
    """Call claude CLI in print mode, return (stdout, wall_seconds)."""
    t0 = time.time()
    r = subprocess.run(
        ["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt],
        capture_output=True, text=True, timeout=timeout,
    )
    wall = time.time() - t0
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {r.stderr[:500]}")
    return r.stdout, wall


def parse_json(raw: str) -> dict:
    """Extract first JSON object from raw text. Tolerant to code fences/prose."""
    raw = raw.strip()
    # strip fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)
    # find first {...}
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        raise ValueError(f"no JSON found in: {raw[:200]}")
    return json.loads(m.group(0))


def run(data_dir: Path, out_path: Path, max_chars: int = 50_000) -> dict:
    results = {"version": "ai", "per_creator": {}}
    t0 = time.time()
    calls_wall = 0.0
    for jf in sorted(data_dir.glob("*.json")):
        if jf.name.startswith("_"):
            continue
        data = json.loads(jf.read_text())
        joined = " ".join(v["text"] for v in data["videos"])
        if len(joined) > max_chars:
            joined = joined[:max_chars]
        prompt = PROMPT_TEMPLATE.format(
            spec=metrics_as_prompt_spec(),
            creator=data["creator"],
            transcript=joined,
        )
        print(f"  [ai] calling claude for {data['creator']} ({len(joined)} chars)",
              flush=True)
        raw, wall = call_claude(prompt)
        calls_wall += wall
        try:
            metrics = parse_json(raw)
        except Exception as e:
            print(f"  parse error for {data['creator']}: {e}", flush=True)
            metrics = {m.key: None for m in METRICS}
        results["per_creator"][data["creator"]] = {
            "n_videos": len(data["videos"]),
            "metrics": metrics,
            "call_wall_seconds": round(wall, 3),
        }
    results["wall_seconds"] = round(time.time() - t0, 4)
    results["api_wall_seconds"] = round(calls_wall, 3)
    # Rough cost estimate: Haiku 4.5 at input ~$1/M, output ~$5/M
    # Assume ~15k input tokens per call + ~200 output tokens.
    n_calls = len(results["per_creator"])
    results["cost_usd_estimate"] = round(n_calls * (15_000 / 1_000_000 * 1.0
                                                    + 200 / 1_000_000 * 5.0), 4)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    return results


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    r = run(root / "data" / "transcripts", root / "results" / "ai.json")
    print(json.dumps(r, ensure_ascii=False, indent=2))
