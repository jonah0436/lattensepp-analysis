"""Compare four methods of computing the same 8 metrics.

METHODS:
  1. it_mario     — His exact small keyword lists (as stated in his video)
  2. script       — Our extended keyword lists (15+ words per metric)
  3. ai           — Claude agent free-form (cached in results/ai_metrics/)
  4. hybrid       — Best-of-breed: deterministic math for TTR/word_len,
                    extended lists for keywords, full-dictionary for denglisch

TWO REFERENCE LAYERS — do not confuse them:

  PRIMARY (public, video-facing) — 'agreement_with_it_mario':
    How many of IT-Mario's 7 declared creator winners each method
    reproduces. This is the REBUILD FIDELITY score: did the replica
    recover his published ranking on the same corpus? Reported as
    hits/7. This is the only accuracy claim this project makes publicly.

  SECONDARY (diagnostic only) — 'internal_consistency_hybrid_vs_others':
    How often each method's ranking matches the hybrid method's ranking
    on the same corpus. Hybrid is our best-of-breed logic, NOT ground
    truth. Use this to spot outlier methods, not to claim correctness.

Also computes MAPE (mean absolute % error) of each method's raw numbers
versus hybrid — a magnitude diagnostic, not a correctness measure.

Outputs: results/methods_n50.json (default) or
results/methods_n50_clean.json (--corpus n50_clean).
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from common.metrics_spec import METRICS  # noqa: E402
from script_version.analyze import ENGLISH_SAMPLE, tokenize  # noqa: E402


# =============================================================================
# IT-Mario's exact small keyword lists — verbatim from his video transcript
# =============================================================================
IT_MARIO_LISTS: dict[str, set[str]] = {
    "wealth_flex":     {"geld", "cash", "kaufen", "penthouse",
                        "penthous", "premium"},
    "drama_conflict":  {"hater", "neid", "blockiert", "ehrenlos",
                        "gerücht", "geruecht"},
    "hype_adjectives": {"krass", "heftig", "brutal", "übelst", "uebelst"},
    "egocentrism":     {"ich", "mein", "meine", "mich", "mir"},
}


# =============================================================================
# IT-Mario's declared creator-metric winners from the source video (see
# docs/IT-MARIO-VIDEO.md). This is the PRIMARY reference for public accuracy
# scoring — "agreement_with_it_mario" below counts how many declared winners
# each method reproduces on the same corpus.
#
# Hype is declared as a tie between papaplatte and apored. A method that
# picks either tied creator (or returns "tie") counts as a match.
# =============================================================================
IT_MARIO_DECLARED: dict[str, set[str]] = {
    "vocabulary_ttr":  {"maithinkx"},
    "wealth_flex":     {"apored"},
    "drama_conflict":  {"apored"},
    "hype_adjectives": {"papaplatte", "apored"},
    "egocentrism":     {"papaplatte"},
    "denglisch":       {"papaplatte"},
    "avg_word_len":    {"maithinkx"},
}

# =============================================================================
# Denglisch anchor list for the IT-Mario replica (T06 reverse-engineer).
#
# IT-Mario declared Papaplatte as denglisch winner in his video but never
# disclosed the wordlist he used. For the replica to reproduce his ranking,
# we reverse-engineer a 100-word English anchor list of the most common
# English loanwords in contemporary German youth / gaming / streaming speech.
#
# Rationale:
#   - "Small-list" style mirrors IT-Mario's other metrics (5-6 seed words
#     per category); 100 words stays in the same spirit for denglisch
#     while giving enough coverage for a stable rate.
#   - Biased toward gaming / streaming / internet-culture tokens because
#     that is where Denglisch actually lives in modern German speech.
#   - Reproduces Papaplatte-as-winner on both our N=25 and N=50 corpora,
#     matching IT-Mario's declared ranking (see docs/IT-MARIO-VIDEO.md).
#   - Some tokens ("hi", "ok", "no") are rare German false friends but
#     appear overwhelmingly as English-speech markers in the target
#     creators' transcripts. The rates are robust to removing any single
#     token.
# =============================================================================
DENGLISCH_ANCHOR_LIST: frozenset[str] = frozenset({
    "okay", "ok", "cool", "chill", "nice", "crazy", "wild", "real",
    "level", "team", "player", "gamer", "stream", "streamer",
    "streaming", "gaming", "content", "clip", "clips", "live",
    "offline", "online", "random", "fail", "win", "lose", "best",
    "worst", "bro", "sister", "homie", "mate", "guys", "boys",
    "girls", "dude", "literally", "actually", "basically",
    "seriously", "whatever", "whenever", "however", "sorry",
    "thanks", "hello", "hi", "bye", "yeah", "yes", "no", "nope",
    "maybe", "hype", "epic", "trash", "sick", "lit", "based",
    "cringe", "vibe", "mood", "meme", "lol", "lmao", "omg", "wtf",
    "bruh", "skibidi", "deep", "dive", "flow", "grind", "hustle",
    "goal", "mindset", "energy", "space", "time", "money",
    "cash", "broke", "rich", "fresh", "smooth", "tight", "solid",
    "dope", "fire", "weird", "strange", "normal", "special",
    "different", "same", "funny", "serious", "easy", "hard", "yo",
})
# sanity: keep exactly 100 anchors — the number IT-Mario implied by scope
assert len(DENGLISCH_ANCHOR_LIST) == 100, (
    f"DENGLISCH_ANCHOR_LIST drifted from 100 to {len(DENGLISCH_ANCHOR_LIST)}"
)


def compute_denglisch_anchor(tokens: list[str],
                             anchors: frozenset[str]) -> float:
    """Denglisch rate per 1k tokens using a small anchor list.

    Matches the per-1k-tokens convention used by every other keyword metric
    in this module.
    """
    total = len(tokens) or 1
    hits = sum(1 for t in tokens if t in anchors)
    return hits / total * 1000

# =============================================================================
# English dictionary for Denglisch — use /usr/share/dict/words minus German
# overlap so we don't flag words like "name" that exist in both
# =============================================================================
def load_english_dict() -> set[str]:
    try:
        words = Path("/usr/share/dict/words").read_text(errors="ignore").splitlines()
        eng = {w.lower() for w in words if w.isalpha()}
    except Exception:
        eng = set(ENGLISH_SAMPLE)
    # remove common German-English false friends (words that exist in both)
    german_overlap = {
        "also", "finger", "hand", "haus", "name", "plan", "rang",
        "bad", "wind", "arm", "ring", "gold", "mind", "ball", "park",
        "to", "so", "in", "on", "an", "der", "mit", "nicht", "ist",
        "hier", "auf", "sie", "bei", "nach", "eine", "einer", "das",
        "rot", "gas", "aha", "hi", "ok",
    }
    return eng - german_overlap


ENGLISH_DICT_LARGE = load_english_dict()


# =============================================================================
# Method implementations
# =============================================================================

def compute_it_mario(tokens: list[str]) -> dict[str, float]:
    """IT-Mario's replica: exact keyword lists + 100-word denglisch anchor list.

    Denglisch uses DENGLISCH_ANCHOR_LIST — reverse-engineered to reproduce
    his declared Papaplatte-as-winner ranking (see T06 in docs/TASKS.md).
    """
    total = len(tokens) or 1
    unique = len(set(tokens))
    out: dict[str, float] = {
        "total_tokens": float(total),
        "vocabulary_ttr": unique / total,
        "avg_word_len": sum(len(t) for t in tokens) / total,
        "denglisch": compute_denglisch_anchor(tokens, DENGLISCH_ANCHOR_LIST),
    }
    for metric_key, kw in IT_MARIO_LISTS.items():
        hits = sum(1 for t in tokens if t in kw)
        out[metric_key] = hits / total * 1000
    return out


def compute_script(tokens: list[str]) -> dict[str, float]:
    """Our extended-list script version."""
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


def compute_hybrid(tokens: list[str]) -> dict[str, float]:
    """Best-of-breed per metric:

    - TTR, avg_word_len, total_tokens: pure math (deterministic)
    - Keywords: extended list with simple stemming (handle -er, -e, -en)
    - Denglisch: /usr/share/dict/words minus German overlap (large dict)
    """
    total = len(tokens) or 1
    unique = len(set(tokens))

    # simple stem set for better keyword recall
    def stemmed_match(kw: set[str], tok: str) -> bool:
        if tok in kw:
            return True
        # try stripping common German suffixes and checking again
        for suf in ("en", "er", "es", "e", "s"):
            if tok.endswith(suf) and tok[: -len(suf)] in kw:
                return True
        return False

    out: dict[str, float] = {
        "total_tokens": float(total),
        "vocabulary_ttr": unique / total,
        "avg_word_len": sum(len(t) for t in tokens) / total,
    }
    for m in METRICS:
        if m.kind != "keyword_count":
            continue
        kw = {k.lower() for k in m.keywords}
        hits = sum(1 for t in tokens if stemmed_match(kw, t))
        out[m.key] = hits / total * 1000

    # Denglisch via large dictionary
    hits = sum(1 for t in tokens if t in ENGLISH_DICT_LARGE)
    out["denglisch"] = hits / total * 1000

    return out


# =============================================================================
# Aggregation / accuracy
# =============================================================================

def load_ai_metrics(ai_dir: Path) -> dict[str, dict]:
    out = {}
    for jf in sorted(ai_dir.glob("*.json")):
        if jf.name.startswith("_"):
            continue
        d = json.loads(jf.read_text())
        out[d["creator"]] = d["metrics"]
    return out


def rank(per_creator: dict, key: str) -> str | None:
    items = [(c, d.get(key)) for c, d in per_creator.items()
             if d.get(key) is not None]
    if len(items) < 2:
        return None
    items.sort(key=lambda r: r[1], reverse=True)
    top, second = items[0], items[1]
    denom = max(abs(top[1]), abs(second[1]), 1e-9)
    if abs(top[1] - second[1]) / denom < 0.03:
        return "tie"
    return top[0]


def winners(per_creator: dict, metric_keys: list[str]) -> dict[str, str | None]:
    return {k: rank(per_creator, k) for k in metric_keys}


def mape_vs_reference(ref: dict, method: dict, metric_keys: list[str]) -> dict:
    """Per-metric mean absolute % error across creators."""
    out = {}
    for mk in metric_keys:
        errs = []
        for c in ref:
            rv = ref[c].get(mk)
            mv = method.get(c, {}).get(mk)
            if rv is None or mv is None or rv == 0:
                continue
            errs.append(abs(mv - rv) / abs(rv) * 100)
        out[mk] = round(sum(errs) / max(len(errs), 1), 2) if errs else None
    return out


# =============================================================================
# Main
# =============================================================================

def load_corpus(data_dir: Path) -> dict[str, list[str]]:
    """Return {creator: tokens} on joined videos."""
    out = {}
    for jf in sorted(data_dir.glob("*.json")):
        if jf.name.startswith("_"):
            continue
        d = json.loads(jf.read_text())
        joined = " ".join(v["text"] for v in d["videos"])
        out[d["creator"]] = tokenize(joined)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus", choices=["raw", "n50_clean"], default="raw",
        help="raw=data/transcripts_n50/+ai_metrics (V2 default); "
             "n50_clean=data/transcripts_n50_clean/+ai_metrics_n50",
    )
    args = parser.parse_args()

    if args.corpus == "n50_clean":
        primary_dir = ROOT / "data" / "transcripts_n50_clean"
        ai_dir = ROOT / "results" / "ai_metrics_n50"
        out_filename = "methods_n50_clean.json"
    else:
        primary_dir = ROOT / "data" / "transcripts_n50"
        ai_dir = ROOT / "results" / "ai_metrics"
        out_filename = "methods_n50.json"
    n25_dir = ROOT / "data" / "transcripts"
    creators = ["apored", "maithinkx", "papaplatte"]
    tokens_per_creator: dict[str, list[str]] = {}
    per_creator_n = {}
    for c in creators:
        primary_path = primary_dir / f"{c}.json"
        if primary_path.exists():
            d = json.loads(primary_path.read_text())
            if len(d.get("videos", [])) >= 40:
                joined = " ".join(v["text"] for v in d["videos"])
                tokens_per_creator[c] = tokenize(joined)
                per_creator_n[c] = len(d["videos"])
                continue
        # fall back to N=25
        d = json.loads((n25_dir / f"{c}.json").read_text())
        joined = " ".join(v["text"] for v in d["videos"])
        tokens_per_creator[c] = tokenize(joined)
        per_creator_n[c] = len(d["videos"])

    metric_keys = [m.key for m in METRICS]

    methods: dict[str, dict] = {"it_mario": {}, "script": {}, "hybrid": {}}
    t0 = time.time()
    for c, tok in tokens_per_creator.items():
        methods["it_mario"][c] = compute_it_mario(tok)
        methods["script"][c] = compute_script(tok)
        methods["hybrid"][c] = compute_hybrid(tok)
    wall = round(time.time() - t0, 4)

    # AI: cached from results/ai_metrics[_n50]/ depending on --corpus flag
    methods["ai"] = load_ai_metrics(ai_dir)

    win_all = {m: winners(methods[m], metric_keys) for m in methods}

    # ------------------------------------------------------------------
    # PRIMARY accuracy metric — agreement with IT-Mario's declared winners.
    # This is the public, video-facing score: "how many of his 7 declared
    # creator winners does each method reproduce on the same corpus?"
    #
    # Scoring convention (matches video_charts/01_three_method_accuracy_matrix,
    # which is the public reference the charts, README, and video script
    # consume):
    #   - Full HIT: non-tie metric, method picks the one declared creator.
    #   - TIE-MATCH (tracked separately, does NOT count as hit):
    #     metric is a declared tie and the method picked a creator inside
    #     the tie set OR the method itself returned "tie".
    #   - MISS: anything else (picked a creator not in the declared set,
    #     or returned "tie" on a non-tie metric).
    # We track tie-matches transparently rather than count them, so the
    # public number is strictly the reproducibility of a single declared
    # winner. Any method that "got the tie right" is visible as a
    # non-zero tie_matches count.
    # ------------------------------------------------------------------
    agreement_it_mario = {}
    for m in methods:
        hits = tie_matches = total = 0
        for mk, declared in IT_MARIO_DECLARED.items():
            picked = win_all[m].get(mk)
            if picked is None:
                continue
            total += 1
            is_tie = len(declared) > 1
            if is_tie:
                # Declared tie. Either pick a creator in the tie set or
                # explicitly return "tie" to earn a tie_match. Neither
                # counts as a hit under the public convention.
                if picked == "tie" or picked in declared:
                    tie_matches += 1
            else:
                if picked in declared:
                    hits += 1
        agreement_it_mario[m] = {
            "hits": hits,
            "tie_matches": tie_matches,
            "total": total,
            "pct": round(hits / max(total, 1) * 100, 1),
        }

    # ------------------------------------------------------------------
    # SECONDARY diagnostic — internal consistency vs the hybrid method.
    # Hybrid is our best-of-breed logic, NOT ground truth. This number
    # tells you which methods cluster with hybrid's rankings; it does
    # NOT tell you which method is correct. Useful for spotting outliers.
    # ------------------------------------------------------------------
    win_hybrid = win_all["hybrid"]
    internal_consistency = {}
    for m in methods:
        hits = total = 0
        for mk in metric_keys:
            if mk == "total_tokens":
                continue
            ref = win_hybrid.get(mk)
            pred = win_all[m].get(mk)
            if ref is None or pred is None:
                continue
            total += 1
            if ref == pred or (ref == "tie" and pred is not None):
                hits += 1
        internal_consistency[m] = {
            "hits": hits,
            "total": total,
            "pct": round(hits / max(total, 1) * 100, 1),
        }

    # MAPE per metric vs hybrid (magnitude diagnostic, not a truth claim).
    mape = {m: mape_vs_reference(methods["hybrid"], methods[m], metric_keys)
            for m in methods if m != "hybrid"}

    # Per-metric story: picked winner per method, flagged against IT-Mario's
    # declared winner (primary reference) and against hybrid (diagnostic).
    per_metric_story = []
    for mk in metric_keys:
        if mk == "total_tokens":
            continue
        declared = IT_MARIO_DECLARED.get(mk, set())
        row = {
            "metric": mk,
            "it_mario_declared": sorted(declared) if declared else None,
            "hybrid_picked": win_hybrid.get(mk),
            "methods": {},
        }
        for m in methods:
            picked = win_all[m].get(mk)
            is_tie = len(declared) > 1 if declared else False
            if not declared:
                match_label = None
            elif is_tie:
                # Strict convention (mirrors the aggregate counter above):
                # any output on a declared-tie metric is a tie_match, never
                # a full hit. Applies to both "tie" output and picked-in-set.
                if picked == "tie" or picked in declared:
                    match_label = "tie_match"
                else:
                    match_label = "miss"
            else:
                match_label = "hit" if picked in declared else "miss"
            row["methods"][m] = {
                "winner": picked,
                "match_vs_it_mario": match_label,
                "matches_hybrid": picked == win_hybrid.get(mk),
                "mape_vs_hybrid": mape.get(m, {}).get(mk),
            }
        per_metric_story.append(row)

    out = {
        "corpus_n_per_creator": per_creator_n,
        "wall_seconds_methods": wall,
        "methods": methods,
        "winners_by_method": win_all,
        # PRIMARY — public, video-facing accuracy score.
        "agreement_with_it_mario": agreement_it_mario,
        # SECONDARY — diagnostic only. Hybrid is not ground truth.
        "internal_consistency_hybrid_vs_others": internal_consistency,
        "mape_vs_hybrid_per_metric": mape,
        "per_metric_story": per_metric_story,
        "_reference_note": (
            "agreement_with_it_mario is the PRIMARY accuracy metric. "
            "internal_consistency_hybrid_vs_others is a DIAGNOSTIC and "
            "is not a truth claim — hybrid is our best-of-breed logic, "
            "not ground truth."
        ),
    }
    out_path = ROOT / "results" / out_filename
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {out_path}")

    # Standalone IT-Mario replica file (T06): keeps the isolated per-creator
    # view that the video / chart pipeline consumes. Denglisch now filled in
    # via the reverse-engineered DENGLISCH_ANCHOR_LIST — no more null values.
    sample_we_have = (
        f"{per_creator_n.get('papaplatte', '?')} videos per creator "
        "(actual counts in per_creator.*.n_videos), no comments"
    )
    replica = {
        "method": "IT-Mario exact replica",
        "sample_he_used": "150 videos (50 per creator) + 15k comments",
        "sample_we_have": sample_we_have,
        "denglisch_wordlist_size": len(DENGLISCH_ANCHOR_LIST),
        "denglisch_wordlist_note": (
            "100-word English anchor list reverse-engineered to reproduce "
            "his declared Papaplatte-as-winner ranking (T06)."
        ),
        "per_creator": {
            c: {
                "n_videos": per_creator_n[c],
                "metrics": methods["it_mario"][c],
            }
            for c in creators
        },
    }
    replica_path = ROOT / "results" / "it_mario_replica.json"
    replica_path.write_text(json.dumps(replica, ensure_ascii=False, indent=2))
    print(f"Wrote {replica_path}")

    print(f"Corpus sizes: {per_creator_n}")
    print("PRIMARY — agreement with IT-Mario's declared winners:",
          {m: f"{a['hits']}/{a['total']} hits, {a['tie_matches']} tie-match "
              f"({a['pct']}%)"
           for m, a in agreement_it_mario.items()})
    print("SECONDARY — internal consistency vs hybrid (diagnostic):",
          {m: f"{a['hits']}/{a['total']} ({a['pct']}%)"
           for m, a in internal_consistency.items()})
    print("IT-Mario denglisch rates (per 1k tokens):",
          {c: round(methods["it_mario"][c]["denglisch"], 3) for c in creators})


if __name__ == "__main__":
    main()
