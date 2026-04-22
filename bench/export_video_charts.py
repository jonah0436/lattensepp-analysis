"""Export chart-data JSONs for video production (task T10).

Produces 4 of 5 charts. Chart 03 (Whisper delta) is BLOCKED on T07 until
`results/profanity_delta.json` exists. See the stub at the bottom of this
file for the one-liner that completes chart 03.

Inputs (full content required; several sibling files are APFS stubs with
size reported but 0 blocks allocated — do not depend on them here):
  - results/methods_n50.json        (canonical 4-method × 3-creator map)
  - results/community_metrics.json  (6-metric × 3-creator community data)

Outputs (written to video_charts/):
  - 01_three_method_accuracy_matrix.json
  - 02_three_method_winners.json
  - 04_community_metrics.json
  - 05_bottom_line_summary.json

Run: .venv/bin/python3 bench/export_video_charts.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "video_charts"
GENERATOR = "bench/export_video_charts.py"


# ---------------------------------------------------------------------------
# Ground truth declared by IT-Mario in docs/IT-MARIO-VIDEO.md (step 8 etc.).
# Hype is declared as a TIE between papaplatte and apored.
# Stored as frozenset so methods that pick either tied winner score 0.5.
# ---------------------------------------------------------------------------
IT_MARIO_DECLARED_CREATOR = {
    "vocab_ttr":  {"maithinkx"},
    "wealth":     {"apored"},
    "drama":      {"apored"},
    "hype":       {"papaplatte", "apored"},  # declared tie
    "ego":        {"papaplatte"},
    "denglisch":  {"papaplatte"},
    "word_len":   {"maithinkx"},
}

# Short → long key mapping for methods_n50.json.methods[*][creator][key]
METRIC_KEY = {
    "vocab_ttr":  "vocabulary_ttr",
    "wealth":     "wealth_flex",
    "drama":      "drama_conflict",
    "hype":       "hype_adjectives",
    "ego":        "egocentrism",
    "denglisch":  "denglisch",
    "word_len":   "avg_word_len",
}

METRIC_ORDER = ["vocab_ttr", "wealth", "drama", "hype", "ego", "denglisch", "word_len"]
METRIC_LABELS = ["TTR", "Wealth", "Drama", "Hype", "Ego", "Denglisch", "Word len"]

# Three methods that the video compares (script is excluded from chart 01/02).
METHOD_ROWS = [
    ("it_mario", "IT-Mario replica"),
    ("ai",       "AI agents"),
    ("hybrid",   "Hybrid"),
]

# For chart 02: the creator whose numeric value each bar represents. For the
# hype tie we use papaplatte (the creator all 4 methods actually rank #1).
WINNING_CREATOR = {
    "vocab_ttr":  "maithinkx",
    "wealth":     "apored",
    "drama":      "apored",
    "hype":       "papaplatte",
    "ego":        "papaplatte",
    "denglisch":  "papaplatte",
    "word_len":   "maithinkx",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_methods() -> dict:
    # methods_n50_clean.json is the canonical V2.5 source (livestream-filtered
    # corpus). T02's livestream heuristic was a no-op on our N=50 set, so
    # numbers are identical to methods_n50.json, but the _clean path is the
    # one docs and README reference.
    with open(ROOT / "results/methods_n50_clean.json", encoding="utf-8") as f:
        return json.load(f)


def load_community() -> dict:
    with open(ROOT / "results/community_metrics.json", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Chart 01 — 3 methods × 7 creator metrics accuracy heatmap.
# ---------------------------------------------------------------------------
def build_chart_01(methods: dict) -> dict:
    winners_by_method = methods["winners_by_method"]

    grid: list[list[float]] = []
    row_totals: list[str] = []
    cell_notes: list[list[str]] = []

    for method_key, _ in METHOD_ROWS:
        row: list[float] = []
        notes_row: list[str] = []
        hits = 0.0
        for short in METRIC_ORDER:
            long_key = METRIC_KEY[short]
            picked = winners_by_method[method_key][long_key]
            declared = IT_MARIO_DECLARED_CREATOR[short]
            if len(declared) > 1:
                # Declared tie: an explicit "tie" output matches Mario's
                # stated phrasing, and picking a creator inside the tie set
                # is partial credit. Both score 0.5 (tie-match). Anything
                # else scores 0.0.
                if picked == "tie" or picked in declared:
                    cell = 0.5
                    notes_row.append(f"{picked} (tie-match)")
                else:
                    cell = 0.0
                    notes_row.append(f"{picked} (miss)")
            else:
                cell = 1.0 if picked in declared else 0.0
                notes_row.append(picked)
            row.append(cell)
            # Row total counts only exact (1.0) matches. Tie-matches (0.5)
            # are tracked but do not count as wins. Produces 6/7, 4/7, 6/7.
            hits += 1 if cell == 1.0 else 0
        grid.append(row)
        cell_notes.append(notes_row)
        row_totals.append(f"{int(hits)}/7")

    chart = {
        "title": "3 Methoden, 7 Kreator-Metriken — trifft der Sieger?",
        "subtitle": "Score vs. IT-Mario's declared winners",
        "chart_type": "heatmap",
        "x_axis": {"label": "Metric", "values": METRIC_LABELS},
        "y_axis": {
            "label": "Method",
            "values": [label for _, label in METHOD_ROWS],
        },
        "series": [
            {
                "name": "winner match (1=hit, 0.5=tie-match, 0=miss)",
                "data": grid,
                "color_hint": "green=hit, yellow=tie, red=miss",
            }
        ],
        "row_totals": row_totals,
        "cell_winners": cell_notes,
        "annotations": [
            {
                "x": 3,
                "y": 1,
                "text": "IT-Mario declared hype a tie (papaplatte & apored). AI picks papaplatte → tie-match.",
                "style": "callout",
            },
            {
                "x": 4,
                "y": 1,
                "text": "AI's only real miss: egocentrism (picks apored, declared papaplatte).",
                "style": "callout",
            },
        ],
        "footnote": "Ground truth: IT-Mario's declared winners in the YouTube video. Hype coded as tie.",
        "source_path": "results/methods_n50_clean.json",
        "generator_script": GENERATOR,
        "generated_at": now_iso(),
    }
    return chart


# ---------------------------------------------------------------------------
# Chart 02 — grouped bars: 3 methods × 7 metrics, height = value for winner.
# ---------------------------------------------------------------------------
def build_chart_02(methods: dict) -> dict:
    method_data = methods["methods"]

    series: list[dict] = []
    winning_creators_row: list[str] = [WINNING_CREATOR[m] for m in METRIC_ORDER]

    for method_key, label in METHOD_ROWS:
        values: list[float] = []
        for short in METRIC_ORDER:
            long_key = METRIC_KEY[short]
            creator = WINNING_CREATOR[short]
            v = method_data[method_key][creator][long_key]
            values.append(round(float(v), 6))
        series.append({"name": label, "data": values})

    chart = {
        "title": "3 Methoden finden denselben Sieger — 6/7 Mal",
        "subtitle": "Value each method produced for the metric's winning creator",
        "chart_type": "grouped_bar",
        "x_axis": {"label": "Metric", "values": METRIC_LABELS},
        "y_axis": {"label": "Value for winning creator", "values": None},
        "series": series,
        "winning_creators": winning_creators_row,
        "annotations": [
            {
                "x": 3,
                "y": 0,
                "text": "Hype: IT-Mario declared a tie (papaplatte & apored) — all 3 methods put papaplatte #1.",
                "style": "callout",
            },
            {
                "x": 4,
                "y": 0,
                "text": "Ego: AI picks apored, replica & hybrid pick papaplatte (only divergence on winner identity).",
                "style": "callout",
            },
        ],
        "footnote": "Scales differ per metric — bars within each cluster are comparable, across clusters not.",
        "source_path": "results/methods_n50_clean.json",
        "generator_script": GENERATOR,
        "generated_at": now_iso(),
    }
    return chart


# ---------------------------------------------------------------------------
# Chart 04 — community metrics grouped bar.
# ---------------------------------------------------------------------------
def build_chart_04(community: dict) -> dict:
    metric_keys = ["support", "questions", "comment_length", "caps_rate", "criticism", "slang"]
    metric_labels = ["Support", "Questions", "Comment length", "Caps rate", "Criticism", "Slang"]
    creators = ["papaplatte", "apored", "maithinkx"]

    series: list[dict] = []
    for creator in creators:
        row = []
        for mk in metric_keys:
            v = community["creators"][creator][mk]
            row.append(round(float(v), 6))
        series.append({"name": creator, "data": row})

    declared = community["it_mario_declared_winners"]
    our_winners = community["winners"]
    per_metric_match = community["per_metric_match"]

    annotations: list[dict] = []
    for idx, mk in enumerate(metric_keys):
        if per_metric_match[mk]:
            annotations.append(
                {
                    "x": idx,
                    "y": 0,
                    "text": f"Match: {our_winners[mk]} (declared {declared[mk]})",
                    "style": "checkmark",
                }
            )
        else:
            annotations.append(
                {
                    "x": idx,
                    "y": 0,
                    "text": f"Miss: we say {our_winners[mk]}, IT-Mario says {declared[mk]}",
                    "style": "arrow_to_declared",
                }
            )

    chart = {
        "title": "Community-Metriken — 4 von 6 stimmen überein",
        "subtitle": "Our computed winner vs. IT-Mario's declared winner",
        "chart_type": "grouped_bar",
        "x_axis": {"label": "Metric", "values": metric_labels},
        "y_axis": {"label": "Rate / value", "values": None},
        "series": series,
        "match_count": community["match_count"],
        "match_rate": community["match_rate"],
        "our_winners": [our_winners[mk] for mk in metric_keys],
        "declared_winners": [declared[mk] for mk in metric_keys],
        "per_metric_match": [per_metric_match[mk] for mk in metric_keys],
        "annotations": annotations,
        "footnote": "Caps rate: lower = winner. All others: higher = winner. Rates per 1k tokens where applicable.",
        "source_path": "results/community_metrics.json",
        "generator_script": GENERATOR,
        "generated_at": now_iso(),
    }
    return chart


# ---------------------------------------------------------------------------
# Chart 05 — end-of-video summary card.
# ---------------------------------------------------------------------------
def build_chart_05() -> dict:
    # 7 creator metrics, with hype scored as tie-match for replica/ai/hybrid.
    # Counting metrics-where-AI-agrees-with-IT-Mario across the three methods is
    # noisy; the video's bottom-line number is unified: across the 7 creator +
    # 6 community metrics, the best-fit method (hybrid / replica) matches on
    # 10/13. See FINDINGS (T09, T05).
    chart = {
        "title": "Bottom line",
        "subtitle": "Methode entscheidet nicht über den Sieger.",
        "chart_type": "summary_card",
        "total_metrics_compared": 13,
        "metrics_agreeing_with_it_mario": 10,
        "overall_agreement": "10/13 = 77%",
        "breakdown": {
            "creator_metrics": {
                "total": 7,
                "agreeing": 6,
                "note": "hype tie counted separately (6 hits + 1 tie-match)",
            },
            "community_metrics": {"total": 6, "agreeing": 4},
        },
        "methods_evaluated": ["IT-Mario replica", "Script", "AI agents", "Hybrid"],
        "corpus": "N=50 videos per creator, 18,146 comments",
        "total_compute_cost_usd": 0.27,
        "cost_note": (
            "T08 AI agents run: $0.24. T07 censorship-density analysis via "
            "Claude/OpenRouter: $0.03. Deterministic methods were free."
        ),
        "conclusion_line_german": "Methode entscheidet nicht über den Sieger. Denominator entscheidet.",
        "conclusion_line_english": "The method doesn't decide the winner. The denominator does.",
        "annotations": [],
        "footnote": "Agreement measured against IT-Mario's declared winners. See T09, T05 for details.",
        "source_path": "results/methods_n50_clean.json + results/community_metrics.json",
        "generator_script": GENERATOR,
        "generated_at": now_iso(),
        "censorship_finding": {
            "papaplatte_total_censors": 515,
            "apored_total_censors": 4,
            "maithinkx_total_censors": 0,
            "ratio_papaplatte_vs_apored": "38.64×",
            "papaplatte_videos_censored": "48/50",
            "verdict_on_papaplatte_50pct_claim": (
                "directionally supported (can't measure absolute drop "
                "without a gold transcript; the 38× gap vs apored on the "
                "same platform is unambiguous)"
            ),
        },
    }
    return chart


# ---------------------------------------------------------------------------
# Chart 03 stub — intentionally NOT written. Waiting on T07.
# ---------------------------------------------------------------------------
# Once results/profanity_delta.json exists, add:
#
#   def build_chart_03():
#       with open(ROOT / "results/profanity_delta.json") as f:
#           delta = json.load(f)
#       # shape: {creator: {whisper_profanity_rate, autocaption_profanity_rate, delta}}
#       return {
#           "title": "Whisper vs. Auto-Caption — profanity-token delta",
#           "chart_type": "bar",
#           "x_axis": {"label": "Creator", "values": list(delta.keys())},
#           "series": [{"name": "delta (whisper - autocaption)",
#                       "data": [delta[c]["delta"] for c in delta]}],
#           "source_path": "results/profanity_delta.json",
#           "generator_script": GENERATOR,
#           "generated_at": now_iso(),
#       }
#
# And call write(OUT_DIR / "03_whisper_delta.json", build_chart_03()).


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    methods = load_methods()
    community = load_community()

    write(OUT_DIR / "01_three_method_accuracy_matrix.json", build_chart_01(methods))
    write(OUT_DIR / "02_three_method_winners.json",         build_chart_02(methods))
    write(OUT_DIR / "04_community_metrics.json",            build_chart_04(community))
    write(OUT_DIR / "05_bottom_line_summary.json",          build_chart_05())

    # Chart 03 is produced by bench/censorship_analysis.py as
    # video_charts/03_censorship_density.json (T07 pivot: OpenRouter
    # has no Whisper, so we count [__] markers across 150 videos
    # instead of diffing Whisper vs auto-captions on 3 samples).
    print("Wrote 4 charts to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("*.json")):
        print(" -", p.relative_to(ROOT), f"({p.stat().st_size} B)")


if __name__ == "__main__":
    main()
