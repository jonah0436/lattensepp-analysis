"""Censorship-density analysis across the full N=150 corpus.

PIVOT FROM ORIGINAL T07:
  Original T07 plan was "run OpenAI Whisper on 3 Papaplatte videos and
  diff the transcripts against YouTube auto-captions." That requires
  either an OpenAI account (user declined) or local `openai-whisper`
  with torch (user declined).

  OpenRouter — the user's available API path — does not host Whisper
  or any audio-transcription model. So we cannot replicate the
  Whisper-vs-captions A/B that the original task asked for.

WHAT THIS DOES INSTEAD:
  YouTube already marks censored words in its auto-captions with a
  `[ __ ]` token (encoded as `[&nbsp;__&nbsp;]` in the stored HTML).
  Every such marker is a word YouTube's own system redacted. Counting
  those markers across all 150 videos gives a much larger-N view of
  the "how much does YouTube censor each creator" question than the
  original 3-video Whisper sample could — 50x more data per creator.

  Step 1 (free, deterministic):
    Count [&nbsp;__&nbsp;] markers in every transcript, compute a
    density-per-1k-tokens rate, aggregate per creator.

  Step 2 (modest OpenRouter spend, <$0.10):
    Take the top-10-by-censor-count videos per creator (30 videos),
    extract up to 20 sentences each that contain a censor marker,
    and ask Claude to categorize the most likely censored word
    (profanity / insult / slur / unknown).

  Output: results/profanity_delta.json (filename kept for
  downstream-chart/script compatibility with the original T07 stub).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from script_version.analyze import tokenize  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = ROOT / "data" / "transcripts_n50_clean"
RESULTS_DIR = ROOT / "results"
OUT_PATH = RESULTS_DIR / "profanity_delta.json"

ENV_FILE = Path(
    "/Users/jonahhill/Desktop/Claude Projects/n8n creator/.env.local"
)
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# The YouTube auto-caption censor marker, as it appears in stored
# transcripts (non-breaking-space HTML entities inside square brackets).
# Also accept plain `[__]` and `[ __ ]` just in case the feed varies.
CENSOR_PATTERNS = [
    re.compile(r"\[&nbsp;__&nbsp;\]"),
    re.compile(r"\[\s*__+\s*\]"),
]

MODEL_CANDIDATES = [
    "anthropic/claude-haiku-4.5",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-sonnet-4.5",
]

# Per-call tuning — keep it small so cost stays under $0.10.
VIDEOS_PER_CREATOR_FOR_LLM = 10
SENTENCES_PER_VIDEO = 20
LLM_BATCH_SIZE = 20  # sentences per OpenRouter call
MAX_RETRIES = 3
COST_CAP_USD = 0.10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_openrouter_key(env_file: Path) -> str:
    """Read OPENROUTER_API_KEY from .env.local without logging the value."""
    for line in env_file.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENROUTER_API_KEY not found in .env.local")


def count_censors(text: str) -> int:
    return sum(len(p.findall(text)) for p in CENSOR_PATTERNS)


def normalize_for_display(text: str) -> str:
    """Replace `[&nbsp;__&nbsp;]` with `[__]` so the LLM sees a clean marker."""
    out = text
    out = re.sub(r"\[&nbsp;__&nbsp;\]", "[__]", out)
    out = re.sub(r"\[\s*__+\s*\]", "[__]", out)
    return out


def extract_censor_sentences(text: str, cap: int) -> list[str]:
    """Return up to `cap` sentences that contain a censor marker.

    We first normalize the censor marker to `[__]`, then split on sentence
    terminators. A "sentence" for our purposes is the window between two
    `.?!` or the ends of the string. We keep sentences that actually
    contain `[__]` after normalization.
    """
    norm = normalize_for_display(text)
    # crude sentence splitter: keep terminator attached
    parts = re.split(r"(?<=[\.!\?])\s+", norm)
    out = []
    for s in parts:
        s = s.strip()
        if not s:
            continue
        if "[__]" not in s:
            continue
        # hard-trim extremely long runs to keep LLM tokens down
        if len(s) > 400:
            idx = s.find("[__]")
            lo = max(0, idx - 150)
            hi = min(len(s), idx + 250)
            s = ("…" + s[lo:hi]).strip() if lo > 0 else s[:hi].strip()
        out.append(s)
        if len(out) >= cap:
            break
    return out


def build_prompt(batch: list[str]) -> list[dict]:
    """Construct a Chat Completions request payload for OpenRouter.

    We ask for a strict JSON array — one entry per input sentence. We
    keep the prompt terse to hold token costs down.
    """
    indexed = "\n".join(f"{i}. {s}" for i, s in enumerate(batch))
    system = (
        "You are a German-language linguistic annotator. For each input "
        "sentence, guess the German word that YouTube's auto-captioner "
        "censored (shown as [__]) and categorize it. Reply with ONLY a "
        "JSON array. No prose, no markdown fences. Each element: "
        "{\"sentence_index\": int, \"likely_word\": string, "
        "\"category\": one of \"profanity\"|\"insult\"|\"slur\"|\"unknown\"}. "
        "Be conservative — if you cannot confidently guess the word from "
        "context, set likely_word to \"?\" and category to \"unknown\"."
    )
    user = (
        f"{len(batch)} German sentences, each contains [__] where YouTube "
        f"censored a word. Return the JSON array, indexed from 0.\n\n"
        f"{indexed}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def call_openrouter(
    client: httpx.Client,
    api_key: str,
    model: str,
    messages: list[dict],
) -> tuple[str, dict]:
    """POST to OpenRouter, return (response_text, usage_dict). Retries 3x."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 1200,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/jonah0436/lattensepp-analysis",
        "X-Title": "lattensepp-analysis censorship T07",
    }
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            r = client.post(
                OPENROUTER_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=60.0,
            )
            if r.status_code == 429 or r.status_code >= 500:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage") or {}
            return text, usage
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"OpenRouter failed after {MAX_RETRIES} retries: {last_err}")


def estimate_cost(model: str, usage: dict) -> float:
    """Rough USD estimate. Prices as of early 2026 (per MTok).

    haiku-4.5   : ~$1 in / $5 out per MTok
    3.5-haiku   : ~$0.80 in / $4 out per MTok
    sonnet-4.5  : ~$3 in / $15 out per MTok
    If unknown, assume haiku-4.5 pricing.
    """
    rates = {
        "anthropic/claude-haiku-4.5": (1.0, 5.0),
        "anthropic/claude-3.5-haiku": (0.80, 4.0),
        "anthropic/claude-sonnet-4.5": (3.0, 15.0),
    }
    in_rate, out_rate = rates.get(model, (1.0, 5.0))
    pin = usage.get("prompt_tokens", 0)
    pout = usage.get("completion_tokens", 0)
    return (pin * in_rate + pout * out_rate) / 1_000_000


def parse_llm_json(raw: str) -> list[dict]:
    """Extract a JSON array even if the model wraps it in a code fence."""
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    # find first `[` and last `]` just in case
    lo = s.find("[")
    hi = s.rfind("]")
    if lo == -1 or hi == -1 or hi < lo:
        return []
    try:
        return json.loads(s[lo : hi + 1])
    except Exception:
        return []


def pick_model(client: httpx.Client, api_key: str) -> str:
    """Try MODEL_CANDIDATES[0] first with a ping request; on 404 fall back."""
    for model in MODEL_CANDIDATES:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 4,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            r = client.post(
                OPENROUTER_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            if r.status_code == 200:
                return model
            # 404 or other non-200 — try next
        except Exception:
            continue
    raise RuntimeError("None of the candidate OpenRouter models responded.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    api_key = load_openrouter_key(ENV_FILE)
    os.environ["OPENROUTER_API_KEY"] = api_key  # in-process only

    # --- Step 1: deterministic counts ------------------------------------
    creators = ["papaplatte", "apored", "maithinkx"]
    per_video: list[dict] = []
    per_creator: dict = {}
    for c in creators:
        d = json.loads((DATA_DIR / f"{c}.json").read_text())
        total_censors = 0
        total_tokens = 0
        videos_with = 0
        max_single = 0
        for v in d["videos"]:
            text = v.get("text", "")
            cc = count_censors(text)
            toks = tokenize(text)
            tc = len(toks)
            total_censors += cc
            total_tokens += tc
            if cc > 0:
                videos_with += 1
                if cc > max_single:
                    max_single = cc
            density = (1000 * cc / tc) if tc else 0.0
            per_video.append({
                "creator": c,
                "video_id": v.get("id", ""),
                "title": v.get("title", ""),
                "censor_count": cc,
                "token_count": tc,
                "density_per_1k_tokens": round(density, 4),
            })
        corpus_density = (
            round(1000 * total_censors / total_tokens, 4) if total_tokens else 0.0
        )
        per_creator[c] = {
            "total_censors": total_censors,
            "total_tokens": total_tokens,
            "density_per_1k_tokens": corpus_density,
            "videos_with_any_censor": videos_with,
            "max_single_video_count": max_single,
        }

    # papaplatte vs others ratio
    pp = per_creator["papaplatte"]["density_per_1k_tokens"] or 0.0
    ap = per_creator["apored"]["density_per_1k_tokens"] or 0.0
    mx = per_creator["maithinkx"]["density_per_1k_tokens"] or 0.0
    ratio_vs_apored = (pp / ap) if ap > 0 else float("inf")
    ratio_vs_maithinkx = (pp / mx) if mx > 0 else float("inf")

    def _fmt_ratio(r: float) -> str:
        if r == float("inf"):
            return "infinite"
        return f"{r:.2f}x"

    papaplatte_vs_others_ratio = (
        f"{_fmt_ratio(ratio_vs_apored)} higher than apored, "
        f"{_fmt_ratio(ratio_vs_maithinkx)} higher than maithinkx"
    )

    print(
        f"[deterministic] papaplatte={per_creator['papaplatte']['total_censors']} "
        f"apored={per_creator['apored']['total_censors']} "
        f"maithinkx={per_creator['maithinkx']['total_censors']}"
    )
    print(f"[deterministic] ratio: {papaplatte_vs_others_ratio}")

    # --- Step 2: LLM categorization -------------------------------------
    # pick top-10 videos per creator with highest censor_count
    top_videos_by_creator: dict[str, list[dict]] = {}
    for c in creators:
        rows = [r for r in per_video if r["creator"] == c and r["censor_count"] > 0]
        rows.sort(key=lambda r: r["censor_count"], reverse=True)
        top_videos_by_creator[c] = rows[:VIDEOS_PER_CREATOR_FOR_LLM]

    # build (creator, video_id, sentences) from original texts
    # we need text back from disk, keyed by id
    text_by_id: dict[str, str] = {}
    for c in creators:
        d = json.loads((DATA_DIR / f"{c}.json").read_text())
        for v in d["videos"]:
            text_by_id[v["id"]] = v.get("text", "")

    # gather sentences per creator
    creator_sentences: dict[str, list[dict]] = {c: [] for c in creators}
    for c in creators:
        for row in top_videos_by_creator[c]:
            vid = row["video_id"]
            sents = extract_censor_sentences(
                text_by_id.get(vid, ""), cap=SENTENCES_PER_VIDEO
            )
            for s in sents:
                creator_sentences[c].append({"video_id": vid, "sentence": s})

    # If a creator has zero censors (maithinkx), skip LLM for them
    total_sent = sum(len(v) for v in creator_sentences.values())
    print(f"[llm] total sentences to categorize: {total_sent}")

    # pick model
    client = httpx.Client()
    try:
        model = pick_model(client, api_key)
    except Exception as e:
        print(f"[llm] model probe failed: {e}")
        client.close()
        raise
    print(f"[llm] using model: {model}")

    # send batches
    spent_usd = 0.0
    per_creator_categories: dict[str, dict] = {
        c: {"profanity": 0, "insult": 0, "slur": 0, "unknown": 0}
        for c in creators
    }
    example_censors: dict[str, list[dict]] = {c: [] for c in creators}

    for c in creators:
        sents = creator_sentences[c]
        if not sents:
            continue
        # batch
        for i in range(0, len(sents), LLM_BATCH_SIZE):
            if spent_usd >= COST_CAP_USD:
                print(f"[llm] cost cap hit (${spent_usd:.4f}); stopping.")
                break
            batch_records = sents[i : i + LLM_BATCH_SIZE]
            batch_text = [r["sentence"] for r in batch_records]
            messages = build_prompt(batch_text)
            try:
                raw, usage = call_openrouter(client, api_key, model, messages)
            except Exception as e:  # noqa: BLE001
                print(f"[llm] call failed for {c} batch {i}: {e}")
                continue
            cost = estimate_cost(model, usage)
            spent_usd += cost
            parsed = parse_llm_json(raw)
            for item in parsed:
                try:
                    idx = int(item.get("sentence_index"))
                    cat = str(item.get("category", "unknown")).lower()
                    word = str(item.get("likely_word", "?"))
                except Exception:
                    continue
                if cat not in per_creator_categories[c]:
                    cat = "unknown"
                per_creator_categories[c][cat] += 1
                if idx < 0 or idx >= len(batch_records):
                    continue
                if len(example_censors[c]) < 10:
                    example_censors[c].append({
                        "sentence": batch_records[idx]["sentence"],
                        "likely_word": word,
                        "category": cat,
                    })
            print(
                f"[llm] {c} batch {i//LLM_BATCH_SIZE}: parsed={len(parsed)} "
                f"cost_so_far=${spent_usd:.4f}"
            )
        if spent_usd >= COST_CAP_USD:
            break

    client.close()

    # --- verdict on 50% claim -------------------------------------------
    # Papaplatte said auto-captions drop ~50% of his profanity words.
    # We can't measure "50% of true profanity" without a gold transcript,
    # but we CAN measure directional support: if papaplatte's censor
    # density is much higher than his peers, his claim that he gets
    # disproportionately censored is supported.
    if ratio_vs_apored == float("inf") or ratio_vs_apored >= 10:
        verdict = "supported"
    elif ratio_vs_apored >= 3:
        verdict = "directionally supported"
    elif ratio_vs_apored >= 1.5:
        verdict = "weak"
    else:
        verdict = "not supported"

    out = {
        "methodology": (
            "YouTube auto-caption [__] censor-marker density across 150 "
            "videos (50 per creator). Categorized via Claude/OpenRouter "
            "on the top-10-by-censor-count videos per creator (30 videos, "
            "up to 20 censor sentences each)."
        ),
        "note_vs_original_spec": (
            "Original T07 used Whisper vs auto-captions on 3 Papaplatte "
            "videos. Pivoted to full-corpus [__] density because "
            "OpenRouter does not host Whisper and the user declined both "
            "OpenAI and local torch install. This covers ~50x more data."
        ),
        "per_video": sorted(
            per_video,
            key=lambda r: (r["creator"], -r["censor_count"]),
        ),
        "per_creator": per_creator,
        "per_creator_category_counts": per_creator_categories,
        "example_censors": example_censors,
        "papaplatte_vs_others_ratio": papaplatte_vs_others_ratio,
        "papaplatte_50pct_claim": {
            "papaplatte_quote": (
                "Beleidigungen fehlen, droppt meine Wörter um 50%"
            ),
            "interpretation": (
                "Papaplatte claimed ~50% of his profanity words are "
                "dropped by auto-captions. We can't measure the absolute "
                "drop rate without a gold transcript, but we can measure "
                "whether his censor-marker density is disproportionately "
                "high vs peers — which would directionally support his "
                "claim that YouTube censors him more aggressively."
            ),
            "verdict": verdict,
        },
        "openrouter_model": model,
        "cost_estimate_usd": round(spent_usd, 4),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_PATH}")
    print(f"Total OpenRouter spend: ${spent_usd:.4f}")


if __name__ == "__main__":
    main()
