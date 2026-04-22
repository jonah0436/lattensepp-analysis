"""Generate charts for the final report.

Outputs (PNG) in results/charts/:
  01_metrics_by_creator.png   - grouped bars per metric (filtered, N=all)
  02_ai_vs_script.png         - side-by-side AI vs Script per creator per metric
  03_filter_impact.png        - % change raw→filtered per metric
  04_sample_impact.png        - % change N=1 → N=all per metric
  05_perf_comparison.png      - wall time + cost (AI vs script)
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

# shared style
plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
})
CREATOR_COLORS = {
    "papaplatte": "#e63946",
    "apored": "#f4a261",
    "maithinkx": "#2a9d8f",
}
METHOD_COLORS = {"ai": "#457b9d", "script": "#8338ec"}


def _load(p: Path) -> dict:
    return json.loads(p.read_text())


def chart_metrics_by_creator(script_nall: dict, ai_agg: dict) -> None:
    """Grouped bars: each metric shows each creator, comparing methods side-by-side."""
    metric_keys = [m.key for m in METRICS if m.key != "total_tokens"]
    creators = sorted(script_nall["per_creator"].keys())
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    for i, mk in enumerate(metric_keys):
        ax = axes[i]
        label = next(m.label for m in METRICS if m.key == mk)
        x = np.arange(len(creators))
        w = 0.38
        s_vals = [script_nall["per_creator"][c]["metrics"].get(mk, 0) for c in creators]
        a_vals = [ai_agg["per_creator"].get(c, {}).get("metrics", {}).get(mk, 0) for c in creators]
        ax.bar(x - w/2, s_vals, w, label="Script", color=METHOD_COLORS["script"])
        ax.bar(x + w/2, a_vals, w, label="AI", color=METHOD_COLORS["ai"])
        ax.set_title(label, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(creators, rotation=20, fontsize=8)
        if i == 0:
            ax.legend(fontsize=8)
    plt.suptitle("Metric values per creator — AI vs Script (filtered, N=all)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUT / "01_metrics_by_creator.png", dpi=130)
    plt.close()


def chart_ai_vs_script_scatter(script_nall: dict, ai_agg: dict) -> None:
    """Scatter: script (x) vs AI (y) per metric. Perfect agreement = on y=x."""
    points_x, points_y, labels = [], [], []
    for c in script_nall["per_creator"]:
        for m in METRICS:
            if m.key == "total_tokens":
                continue
            sv = script_nall["per_creator"][c]["metrics"].get(m.key)
            av = ai_agg["per_creator"].get(c, {}).get("metrics", {}).get(m.key)
            if sv is None or av is None:
                continue
            # normalize each metric by script value so scales are comparable
            denom = max(abs(sv), 1e-6)
            points_x.append(sv / denom)
            points_y.append(av / denom)
            labels.append(f"{c}:{m.key}")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(points_x, points_y, s=50, alpha=0.7,
               color=METHOD_COLORS["ai"])
    lim = max(max(points_x, default=2), max(points_y, default=2)) * 1.1
    ax.plot([0, lim], [0, lim], "--", color="gray", label="perfect agreement")
    ax.set_xlabel("Script (normalized to 1.0)")
    ax.set_ylabel("AI (relative to script)")
    ax.set_title("AI vs Script values — distance from y=x shows disagreement")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "02_ai_vs_script_scatter.png", dpi=130)
    plt.close()


def chart_filter_impact(report: dict) -> None:
    rows = report["filter_impact_raw_to_filtered"]["rows"]
    keys = [r["metric"] for r in rows if r["metric"] != "total_tokens"]
    vals = [r["mean_rel_change_pct"] for r in rows if r["metric"] != "total_tokens"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(keys, vals, color="#e76f51")
    ax.set_xlabel("Mean symmetric relative change (SMAPE, 0-100)")
    ax.set_title("Impact of speaker filter (raw → filtered) — higher = filter changed result more")
    for i, v in enumerate(vals):
        ax.text(v, i, f"  {v:.1f}", va="center", fontsize=9)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUT / "03_filter_impact.png", dpi=130)
    plt.close()


def chart_sample_impact(report: dict) -> None:
    rows = report["sample_impact_n1_to_nall"]["rows"]
    keys = [r["metric"] for r in rows if r["metric"] != "total_tokens"]
    vals = [r["mean_rel_change_pct"] for r in rows if r["metric"] != "total_tokens"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(keys, vals, color="#264653")
    ax.set_xlabel("Mean symmetric relative change (SMAPE, 0-100)")
    ax.set_title("Impact of sample size (N=1 → N=all, filtered)")
    mv = max(vals) if vals else 1
    for i, v in enumerate(vals):
        ax.text(v, i, f"  {v:.1f}", va="center", fontsize=9,
                color="white" if v > mv * 0.3 else "black")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUT / "04_sample_impact.png", dpi=130)
    plt.close()


def chart_performance(perf: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    # wall times
    names = ["Script\n(4 conditions total)", "AI\n(filter + analyze, 3 parallel agents)"]
    wall_s = [perf["script_wall_s_total"], perf["ai_total_wall_s"]]
    axes[0].bar(names, wall_s, color=[METHOD_COLORS["script"], METHOD_COLORS["ai"]])
    axes[0].set_ylabel("Wall seconds")
    axes[0].set_title("Runtime")
    for i, v in enumerate(wall_s):
        axes[0].text(i, v, f" {v:.1f}s", ha="center", va="bottom", fontsize=10)

    # cost
    costs = [0.0, perf["ai_cost_usd_est"]]
    axes[1].bar(names, costs, color=[METHOD_COLORS["script"], METHOD_COLORS["ai"]])
    axes[1].set_ylabel("USD")
    axes[1].set_title("Estimated cost")
    for i, v in enumerate(costs):
        axes[1].text(i, v, f" ${v:.4f}", ha="center", va="bottom", fontsize=10)
    plt.suptitle("Performance — AI vs Script", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(OUT / "05_perf_comparison.png", dpi=130)
    plt.close()


def main() -> None:
    res_dir = ROOT / "results"
    report = _load(res_dir / "report.json")
    script_nall = _load(res_dir / "script_filtered_nall.json")
    ai_agg = _load(res_dir / "ai_aggregated.json")

    # perf: script_wall already in report; AI wall = placeholder here — filled
    # by the bench runner after agents finish (see perf.json)
    perf_path = res_dir / "perf.json"
    perf = _load(perf_path) if perf_path.exists() else {
        "script_wall_s_total": report["script_wall_s_total"],
        "ai_total_wall_s": 0.0,
        "ai_cost_usd_est": 0.0,
    }

    chart_metrics_by_creator(script_nall, ai_agg)
    chart_ai_vs_script_scatter(script_nall, ai_agg)
    chart_filter_impact(report)
    chart_sample_impact(report)
    chart_performance(perf)
    print(f"charts written to {OUT}")


if __name__ == "__main__":
    main()
