"""Community metrics: 6 deterministic keyword/regex metrics over comments.

Per T05 cut list: no AI sentiment. Keyword rates only.

Metrics (all rates per 1k tokens unless noted):
  1. support       — positive / praise keyword rate
  2. questions     — fraction of comments containing '?'
  3. comment_length— mean characters per comment
  4. caps_rate     — fraction of tokens that are ALL-CAPS (>=2 alpha chars)
  5. criticism     — negative keyword rate
  6. slang         — internet-slang keyword rate

Winner rule: MAX wins for support / questions / comment_length / criticism /
slang; MIN wins for caps_rate ("least caps wins"). Cross-check against
IT-Mario's declared winners from docs/IT-MARIO-VIDEO.md.

Outputs:
  results/community_metrics.json — per-creator values + winners + match count
  stdout                         — 6x3 comparison table + match score
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Unicode-safe word tokenizer: letters (incl. German umlauts + ß) only.
# Matches the regex used in src/script_version/analyze.py so counts stay
# directly comparable to the transcript-side metrics.
_TOKEN_RE = re.compile(r"[a-zA-ZäöüÄÖÜß]+")

# Separate regex for caps_rate: we want to know if a SURFACE token is all
# caps before lowercasing, so we grab raw alpha tokens (same char class) and
# check .isupper() with a 2-char minimum.
_RAW_TOKEN_RE = re.compile(r"[a-zA-ZäöüÄÖÜß]{2,}")


# =============================================================================
# Keyword lists (all lowercased, matched after lowercasing tokens)
# =============================================================================

SUPPORT_KWS: frozenset[str] = frozenset({
    "liebe", "super", "geil", "klasse", "top", "respekt", "danke",
    "mega", "beste", "stark", "hammer", "cool", "awesome", "krass",
    "weiter", "gemacht", "großartig", "grossartig",
    # "weiter so" and "gut gemacht" are bigrams — we seed the key words.
    # "weiter" tends to appear predominantly as "weiter so" in YT comments,
    # and "gemacht" together with "gut" covers "gut gemacht".
})

CRITICISM_KWS: frozenset[str] = frozenset({
    "scheiße", "scheisse", "schlecht", "hass", "cringe", "peinlich",
    "dumm", "blöd", "bloed", "idiot", "kacke", "nervt", "hört", "auf",
    "unnötig", "unnoetig", "schade", "enttäuscht", "enttaeuscht",
    "ekelhaft", "hater", "müll", "muell",
    # "hört auf" -> "hört" + "auf" both seeded.
})

SLANG_KWS: frozenset[str] = frozenset({
    "lol", "lmao", "xd", "omg", "wtf", "bro", "digga", "alter", "krass",
    "mega", "sus", "cap", "based", "ratio", "w", "l", "fr", "ong", "rn",
    "tbh", "imo", "ngl", "gg", "ez", "rip", "yeet", "cringe", "vibe",
    "slay",
})


# =============================================================================
# Stem-match helpers (support / criticism only — slang is strict-match)
# =============================================================================

def _stem_hit(token: str, kw_set: frozenset[str]) -> bool:
    """Return True if token matches or is a stem-variant of any keyword.

    Covers German suffix variants: liebe/lieben, super/superschön,
    scheiße/scheißen, etc. A token is a hit if:
      - it equals a keyword, OR
      - a keyword is a prefix of the token (for "super" -> "supergut"), OR
      - token minus a common German suffix equals a keyword
    """
    if token in kw_set:
        return True
    # Prefix match (handles "super" in "superschön", "mega" in "megageil")
    for kw in kw_set:
        if len(kw) >= 4 and token.startswith(kw):
            return True
    # Suffix strip: -en, -er, -es, -e, -st, -t
    for suf in ("en", "er", "es", "st", "e", "t"):
        if token.endswith(suf):
            stem = token[: -len(suf)]
            if stem in kw_set:
                return True
    return False


def _strict_hit(token: str, kw_set: frozenset[str]) -> bool:
    """Exact-match membership (used for slang — whole tokens only)."""
    return token in kw_set


# =============================================================================
# Per-creator comment loading
# =============================================================================

META_FILES = {"_run_summary.json", "_summary.json", "_pilot_summary.json"}


def load_creator_comments(creator_dir: Path) -> list[str]:
    """Return list of raw comment text strings for a creator."""
    out: list[str] = []
    for jf in sorted(creator_dir.glob("*.json")):
        if jf.name in META_FILES:
            continue
        try:
            data = json.loads(jf.read_text())
        except Exception as e:  # pragma: no cover
            print(f"WARN: failed to parse {jf.name}: {e}", file=sys.stderr)
            continue
        for c in data.get("comments", []):
            text = c.get("text")
            if isinstance(text, str) and text.strip():
                out.append(text)
    return out


# =============================================================================
# Metric computation
# =============================================================================

def compute_metrics(comments: list[str]) -> dict[str, float]:
    """Compute the 6 community metrics for a list of comment strings."""
    n_comments = len(comments)
    if n_comments == 0:
        return {
            "support": 0.0, "questions": 0.0, "comment_length": 0.0,
            "caps_rate": 0.0, "criticism": 0.0, "slang": 0.0,
            "n_comments": 0, "n_tokens": 0,
        }

    # Single pass over all comments
    total_chars = 0
    n_with_question = 0
    n_tokens = 0
    n_caps_tokens = 0
    n_support = 0
    n_criticism = 0
    n_slang = 0

    for text in comments:
        total_chars += len(text)
        if "?" in text:
            n_with_question += 1

        # Caps: look at raw (pre-lowercase) alpha tokens >= 2 chars.
        # ß never uppercases, so "SCHEIßE" would fail .isupper(); we accept
        # that edge — vanishingly rare in shouting comments and the rule is
        # conservative / consistent.
        for raw_tok in _RAW_TOKEN_RE.findall(text):
            if raw_tok.isupper():
                n_caps_tokens += 1
            n_tokens += 1

        # Keyword hits: work on lowercased tokens (re-tokenize to include
        # 1-char tokens for slang keywords like "w" and "l")
        lower_tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
        for tok in lower_tokens:
            if _stem_hit(tok, SUPPORT_KWS):
                n_support += 1
            if _stem_hit(tok, CRITICISM_KWS):
                n_criticism += 1
            if _strict_hit(tok, SLANG_KWS):
                n_slang += 1

    # n_tokens for caps denominator is raw tokens >=2 alpha chars.
    # For keyword rates we want a denom aligned with the full token stream
    # (including 1-char tokens like "w"). Use the sum of lowercased token
    # counts, which equals n_tokens (>=2) + count of 1-char tokens.
    # Recompute n_tokens_all for keyword-rate denominator:
    n_tokens_all = 0
    for text in comments:
        n_tokens_all += len(_TOKEN_RE.findall(text))

    denom_kw = n_tokens_all or 1
    denom_caps = n_tokens or 1

    return {
        "support": n_support / denom_kw * 1000,
        "questions": n_with_question / n_comments,
        "comment_length": total_chars / n_comments,
        "caps_rate": n_caps_tokens / denom_caps,
        "criticism": n_criticism / denom_kw * 1000,
        "slang": n_slang / denom_kw * 1000,
        "n_comments": n_comments,
        "n_tokens": n_tokens_all,
    }


# =============================================================================
# Winners + IT-Mario comparison
# =============================================================================

# "max" = higher value wins; "min" = lower value wins (least caps).
METRIC_DIRECTION = {
    "support": "max",
    "questions": "max",
    "comment_length": "max",
    "caps_rate": "min",
    "criticism": "max",
    "slang": "max",
}

IT_MARIO_DECLARED = {
    "support": "maithinkx",
    "questions": "maithinkx",
    "comment_length": "maithinkx",
    "caps_rate": "maithinkx",  # least caps
    "criticism": "apored",
    "slang": "apored",
}


def pick_winner(per_creator: dict[str, dict], metric: str) -> str:
    direction = METRIC_DIRECTION[metric]
    scored = [(c, per_creator[c][metric]) for c in per_creator]
    scored.sort(key=lambda r: r[1], reverse=(direction == "max"))
    return scored[0][0]


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    comments_root = ROOT / "data" / "comments"
    creators = ["papaplatte", "apored", "maithinkx"]

    per_creator: dict[str, dict] = {}
    for c in creators:
        comments = load_creator_comments(comments_root / c)
        metrics = compute_metrics(comments)
        per_creator[c] = metrics

    winners = {m: pick_winner(per_creator, m) for m in METRIC_DIRECTION}
    per_metric_match = {
        m: winners[m] == IT_MARIO_DECLARED[m] for m in METRIC_DIRECTION
    }
    match_count = sum(1 for v in per_metric_match.values() if v)

    out = {
        "creators": per_creator,
        "winners": winners,
        "it_mario_declared_winners": IT_MARIO_DECLARED,
        "match_count": match_count,
        "match_rate": f"{match_count}/6",
        "per_metric_match": per_metric_match,
        "notes": (
            "Deterministic keyword/regex analysis. No AI. "
            "Caps_rate: fraction of raw alpha tokens (>=2 chars) that are "
            "all-uppercase. Questions: fraction of comments containing '?'. "
            "Comment_length: mean characters per comment. Support / "
            "criticism / slang: keyword rate per 1k tokens. Winner = max "
            "value, except caps_rate where winner = min (least caps wins)."
        ),
    }

    out_path = ROOT / "results" / "community_metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    # Pretty stdout table
    metric_order = [
        "support", "questions", "comment_length",
        "caps_rate", "criticism", "slang",
    ]
    print(f"\nWrote {out_path}")
    print(f"\nCommunity metrics (N={sum(per_creator[c]['n_comments'] for c in creators)} comments)")
    print("-" * 78)
    header = f"{'metric':<18} " + " ".join(f"{c:>12}" for c in creators) + "  winner"
    print(header)
    print("-" * 78)
    for m in metric_order:
        row_vals = [per_creator[c][m] for c in creators]
        # Format: percentages / fractions differ by metric
        if m in ("support", "criticism", "slang"):
            fmt = lambda v: f"{v:>12.3f}"  # per 1k tokens
        elif m == "questions":
            fmt = lambda v: f"{v * 100:>11.2f}%"
        elif m == "caps_rate":
            fmt = lambda v: f"{v * 100:>11.2f}%"
        elif m == "comment_length":
            fmt = lambda v: f"{v:>12.2f}"
        else:
            fmt = lambda v: f"{v:>12.4f}"
        row = f"{m:<18} " + " ".join(fmt(v) for v in row_vals)
        w = winners[m]
        itm = IT_MARIO_DECLARED[m]
        mark = "MATCH" if w == itm else f"MISS (itm={itm})"
        row += f"  {w:<10} {mark}"
        print(row)
    print("-" * 78)
    print(f"Match vs IT-Mario: {match_count}/6")
    for m in metric_order:
        tag = "OK" if per_metric_match[m] else "DIFF"
        print(f"  [{tag}] {m:<18} ours={winners[m]:<10} itm={IT_MARIO_DECLARED[m]}")

    # n_comments / n_tokens line
    print()
    for c in creators:
        print(f"  {c:<12} n_comments={per_creator[c]['n_comments']:>6} "
              f"n_tokens={per_creator[c]['n_tokens']:>7}")


if __name__ == "__main__":
    main()
