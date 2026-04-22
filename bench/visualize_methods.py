"""Visualize method accuracy per metric on N=50 corpus.

Outputs:
  06_method_accuracy_matrix.png — heatmap of MAPE per method per metric,
    annotated with ✓/✗ for winner match
  07_method_values_per_metric.png — grouped bars comparing method values
    for each creator per metric (small multiples)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from common.metrics_spec import METRICS  # noqa: E402

OUT = ROOT / "results" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "figure.facecolor": "white",
})

METHOD_COLORS = {
    "it_mario": "#e76f51",
    "script":   "#2a9d8f",
    "hybrid":   "#264653",
    "ai":       "#457b9d",
}

# What logic each metric is: deterministic math vs fuzzy categorization
METRIC_KIND = {
    "vocabulary_ttr":  "Deterministic math",
    "avg_word_len":    "Deterministic math",
    "total_tokens":    "Deterministic math",
    "wealth_flex":     "Keyword list",
    "drama_conflict":  "Keyword list",
    "hype_adjectives": "Keyword list",
    "egocentrism":     "Pronoun list",
    "denglisch":       "Dictionary lookup",
}


def chart_accuracy_matrix(data: dict) -> None:
    """Heatmap: rows=methods, cols=metrics. Cell = MAPE, with ✓/✗ overlay."""
    methods = ["it_mario", "script", "ai", "hybrid"]
    metric_keys = [m.key for m in METRICS if m.key != "total_tokens"]
    labels = {m.key: m.label for m in METRICS}

    mape_mat = np.zeros((len(methods), len(metric_keys)))
    hit_mat = np.zeros((len(methods), len(metric_keys)), dtype=bool)
    win_gold = data["winners_by_method"]["hybrid"]
    for i, meth in enumerate(methods):
        for j, mk in enumerate(metric_keys):
            if meth == "hybrid":
                mape_mat[i, j] = 0.0
                hit_mat[i, j] = True
                continue
            mv = data["mape_vs_hybrid_per_metric"].get(meth, {}).get(mk)
            mape_mat[i, j] = mv if mv is not None else np.nan
            pred = data["winners_by_method"][meth].get(mk)
            hit_mat[i, j] = (pred == win_gold.get(mk)) if pred else False

    fig, ax = plt.subplots(figsize=(12, 4.5))
    # clip for color scale readability
    display = np.clip(np.nan_to_num(mape_mat, nan=0.0), 0, 100)
    im = ax.imshow(display, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=80)
    ax.set_xticks(range(len(metric_keys)))
    ax.set_xticklabels([labels[k] for k in metric_keys], rotation=25, ha="right")
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels(["IT-Mario\n(small lists)", "Script\n(extended lists)",
                        "AI\n(Claude agent)", "Hybrid\n(best-per-metric)"])
    for i in range(len(methods)):
        for j in range(len(metric_keys)):
            v = mape_mat[i, j]
            txt = "—" if np.isnan(v) else f"{v:.1f}%"
            mark = "✓" if hit_mat[i, j] else ("✗" if methods[i] != "hybrid"
                                              or methods[i] == "hybrid" else "")
            if methods[i] == "hybrid":
                mark = "●"
            color = "white" if display[i, j] > 40 else "black"
            ax.text(j, i - 0.12, txt, ha="center", va="center",
                    fontsize=9, color=color)
            ax.text(j, i + 0.22, mark, ha="center", va="center",
                    fontsize=11, color=color, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("MAPE vs hybrid (%)", fontsize=9)
    ax.set_title("Method accuracy per metric (N=50) — "
                 "✓ = correct ranking, ✗ = wrong ranking, ● = reference",
                 pad=12)
    # annotate metric type along bottom
    for j, mk in enumerate(metric_keys):
        ax.text(j, len(methods) - 0.35, METRIC_KIND[mk],
                ha="center", va="top", fontsize=7, style="italic", color="#555",
                transform=ax.get_xaxis_transform())
    plt.tight_layout()
    plt.savefig(OUT / "06_method_accuracy_matrix.png", dpi=140,
                bbox_inches="tight")
    plt.close()


def chart_values_per_metric(data: dict) -> None:
    """Small multiples: one subplot per metric, bars per method per creator."""
    methods = ["it_mario", "script", "ai", "hybrid"]
    creators = ["apored", "maithinkx", "papaplatte"]
    metric_keys = [m.key for m in METRICS if m.key != "total_tokens"]
    labels = {m.key: m.label for m in METRICS}

    fig, axes = plt.subplots(2, 4, figsize=(17, 8))
    axes = axes.flatten()
    for idx, mk in enumerate(metric_keys):
        ax = axes[idx]
        x = np.arange(len(creators))
        w = 0.2
        for k, meth in enumerate(methods):
            vals = []
            for c in creators:
                v = data["methods"].get(meth, {}).get(c, {}).get(mk)
                vals.append(v if v is not None else 0)
            ax.bar(x + (k - 1.5) * w, vals, w,
                   label=meth.replace("_", "-"),
                   color=METHOD_COLORS[meth])
        ax.set_title(f"{labels[mk]}\n[{METRIC_KIND[mk]}]", fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(creators, fontsize=8)
        if idx == 0:
            ax.legend(fontsize=8, loc="upper right")
    plt.suptitle("Per-metric value comparison — 4 methods × 3 creators (N=50)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUT / "07_method_values_per_metric.png", dpi=130)
    plt.close()


def chart_method_summary(data: dict) -> None:
    """Top-level 2-panel summary:

    Left: PRIMARY accuracy — agreement with IT-Mario's declared winners.
    Right: mean MAPE per method across non-deterministic metrics
      (magnitude diagnostic vs hybrid, not a truth claim).
    """
    methods = ["it_mario", "script", "ai", "hybrid"]
    # PRIMARY accuracy metric: agreement with IT-Mario's declared winners.
    # Falls back to the legacy key for older methods_n50.json files.
    acc = data.get(
        "agreement_with_it_mario",
        data.get("winner_accuracy_vs_hybrid", {}),
    )
    mape = data["mape_vs_hybrid_per_metric"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    # Winner accuracy
    ax = axes[0]
    pcts = [acc[m]["pct"] for m in methods]
    bars = ax.bar(methods, pcts, color=[METHOD_COLORS[m] for m in methods])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Agreement with IT-Mario (%)")
    ax.set_title("Rebuild fidelity — declared winners reproduced")
    for b, v in zip(bars, pcts):
        ax.text(b.get_x() + b.get_width() / 2, v + 2,
                f"{v}%", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticklabels([m.replace("_", "-") for m in methods], rotation=0)

    # Mean MAPE (fuzzy metrics only)
    ax = axes[1]
    fuzzy_keys = ["wealth_flex", "drama_conflict", "hype_adjectives",
                  "egocentrism", "denglisch"]
    mean_mape = []
    for m in methods:
        if m == "hybrid":
            mean_mape.append(0.0)
            continue
        vals = [mape.get(m, {}).get(k) for k in fuzzy_keys]
        vals = [v for v in vals if v is not None]
        mean_mape.append(sum(vals) / len(vals) if vals else 0)
    bars = ax.bar(methods, mean_mape,
                  color=[METHOD_COLORS[m] for m in methods])
    ax.set_ylabel("Mean MAPE across fuzzy metrics (%)")
    ax.set_title("Numerical error on categorization metrics")
    for b, v in zip(bars, mean_mape):
        ax.text(b.get_x() + b.get_width() / 2, v + 1,
                f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticklabels([m.replace("_", "-") for m in methods], rotation=0)
    plt.suptitle("Method comparison summary — N=50 corpus",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(OUT / "08_method_summary.png", dpi=140)
    plt.close()


def main() -> None:
    data = json.loads((ROOT / "results" / "methods_n50.json").read_text())
    chart_accuracy_matrix(data)
    chart_values_per_metric(data)
    chart_method_summary(data)
    print(f"charts written to {OUT}")


if __name__ == "__main__":
    main()
