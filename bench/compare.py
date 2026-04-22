"""Benchmark harness. Runs the script version across 4 conditions:
  - N=1 raw, N=1 filtered
  - N=all raw, N=all filtered

Loads AI results from results/ai_metrics/{creator}.json (produced by the
3 parallel agents).

Computes:
- Per-metric winners per condition
- Agreement AI vs Script (filtered at N=all — fair condition)
- Delta from raw→filtered (how much speaker filtering changed each metric)
- Delta from N=1→N=all (stability)
- Agreement vs IT-Mario's declared winners (ground truth)
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from common.metrics_spec import METRICS  # noqa: E402
from script_version.analyze import run as run_script  # noqa: E402


IT_MARIO_WINNERS = {
    "vocabulary_ttr": "maithinkx",
    "wealth_flex": "apored",
    "drama_conflict": "apored",
    "hype_adjectives": "tie",
    "egocentrism": "papaplatte",
    "denglisch": "papaplatte",
    "avg_word_len": "maithinkx",
    "total_tokens": None,
}


def load_ai_results(ai_dir: Path) -> dict:
    """Aggregate the 3 per-creator AI metric files into a run result."""
    per_creator = {}
    for jf in sorted(ai_dir.glob("*.json")):
        d = json.loads(jf.read_text())
        per_creator[d["creator"]] = {
            "n_videos": d.get("n_videos"),
            "metrics": d["metrics"],
        }
    return {"version": "ai", "source": "filtered", "per_creator": per_creator}


def rank(per_creator: dict, key: str) -> list[tuple[str, float]]:
    rows = []
    for c, d in per_creator.items():
        v = d["metrics"].get(key)
        if v is not None:
            rows.append((c, float(v)))
    rows.sort(key=lambda r: r[1], reverse=True)
    return rows


def winner(per_creator: dict, key: str, tie_eps: float = 0.03) -> str | None:
    ranked = rank(per_creator, key)
    if len(ranked) < 2:
        return None
    top, second = ranked[0], ranked[1]
    denom = max(abs(top[1]), abs(second[1]), 1e-9)
    if abs(top[1] - second[1]) / denom < tie_eps:
        return "tie"
    return top[0]


def agreement_table(res_a: dict, res_b: dict,
                    label_a: str = "ai", label_b: str = "script") -> dict:
    rows = []
    hits = gt_a = gt_b = 0
    counted = 0
    for m in METRICS:
        if m.key == "total_tokens":
            continue
        a_win = winner(res_a["per_creator"], m.key)
        b_win = winner(res_b["per_creator"], m.key)
        gt = IT_MARIO_WINNERS.get(m.key)
        rows.append({
            "metric": m.key,
            "label": m.label,
            f"{label_a}_winner": a_win,
            f"{label_b}_winner": b_win,
            "ground_truth": gt,
            "ab_agree": a_win == b_win,
            f"{label_a}_matches_gt": gt is not None and a_win == gt,
            f"{label_b}_matches_gt": gt is not None and b_win == gt,
        })
        counted += 1
        if a_win == b_win:
            hits += 1
        if gt and a_win == gt:
            gt_a += 1
        if gt and b_win == gt:
            gt_b += 1
    return {
        "rows": rows,
        "ab_agreement_pct": round(hits / max(counted, 1) * 100, 1),
        f"{label_a}_vs_gt_pct": round(gt_a / max(counted, 1) * 100, 1),
        f"{label_b}_vs_gt_pct": round(gt_b / max(counted, 1) * 100, 1),
    }


def delta_report(res_a: dict, res_b: dict) -> dict:
    """Mean absolute % change per metric from res_a to res_b.

    To avoid division-by-zero blowups when a metric is 0 at low N, we use a
    symmetric-relative-change (SMAPE-style): |a-b| / max(|a|+|b|, eps) * 100.
    That caps each point at 100% and keeps the average interpretable.
    """
    rows = []
    for m in METRICS:
        deltas = []
        for c in res_a["per_creator"]:
            if c not in res_b["per_creator"]:
                continue
            va = res_a["per_creator"][c]["metrics"].get(m.key)
            vb = res_b["per_creator"][c]["metrics"].get(m.key)
            if va is None or vb is None:
                continue
            denom = max(abs(va) + abs(vb), 1e-6)
            deltas.append(abs(vb - va) / denom * 100)
        rows.append({
            "metric": m.key,
            "mean_rel_change_pct": round(sum(deltas) / max(len(deltas), 1), 2),
        })
    return {"rows": rows}


def main() -> None:
    raw_dir = ROOT / "data" / "transcripts"
    filt_dir = ROOT / "data" / "transcripts_filtered"
    ai_dir = ROOT / "results" / "ai_metrics"
    out_dir = ROOT / "results"

    conditions = {}
    print("Running script version across 4 conditions...")
    t0 = time.time()
    conditions["script_raw_n1"] = run_script(raw_dir, out_dir / "script_raw_n1.json",
                                              n=1, source_label="raw")
    conditions["script_raw_nall"] = run_script(raw_dir, out_dir / "script_raw_nall.json",
                                                n=None, source_label="raw")
    conditions["script_filtered_n1"] = run_script(filt_dir, out_dir / "script_filtered_n1.json",
                                                   n=1, source_label="filtered")
    conditions["script_filtered_nall"] = run_script(filt_dir, out_dir / "script_filtered_nall.json",
                                                     n=None, source_label="filtered")
    script_wall = time.time() - t0
    print(f"  script total wall: {script_wall:.3f}s (all 4 conditions)")

    ai_res = load_ai_results(ai_dir)
    (out_dir / "ai_aggregated.json").write_text(
        json.dumps(ai_res, ensure_ascii=False, indent=2)
    )

    # Agreement at the FAIR condition: ai (filtered) vs script_filtered_nall
    agr_fair = agreement_table(ai_res, conditions["script_filtered_nall"],
                               "ai", "script")

    # Delta: raw→filtered (impact of speaker filter)
    filter_impact = delta_report(conditions["script_raw_nall"],
                                  conditions["script_filtered_nall"])

    # Delta: n1→nall (impact of sample size)
    sample_impact = delta_report(conditions["script_filtered_n1"],
                                  conditions["script_filtered_nall"])

    report = {
        "conditions": list(conditions.keys()),
        "script_wall_s_total": round(script_wall, 4),
        "agreement_fair_ai_vs_script": agr_fair,
        "filter_impact_raw_to_filtered": filter_impact,
        "sample_impact_n1_to_nall": sample_impact,
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n== Summary ==")
    print(f"AI vs Script agreement (filtered): "
          f"{agr_fair['ab_agreement_pct']}%")
    print(f"AI vs ground truth:      {agr_fair['ai_vs_gt_pct']}%")
    print(f"Script vs ground truth:  {agr_fair['script_vs_gt_pct']}%")


if __name__ == "__main__":
    main()
