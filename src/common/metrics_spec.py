"""The 8 metrics IT-Mario computed in the original video.

Each metric maps to (a) what it measures and (b) the keyword list (seed words)
used in the script version. The AI version gets the same spec in prompt form.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Metric:
    key: str
    label: str
    kind: str  # "ratio" | "keyword_count" | "english_count" | "avg_word_len"
    keywords: list[str] = field(default_factory=list)
    description: str = ""


METRICS: list[Metric] = [
    Metric(
        key="vocabulary_ttr",
        label="Wortschatz (Type-Token Ratio)",
        kind="ratio",
        description="Unique words / total words. Higher = bigger relative vocabulary.",
    ),
    Metric(
        key="wealth_flex",
        label="Reichtum / Flex",
        kind="keyword_count",
        keywords=[
            "geld", "cash", "kaufen", "penthouse", "premium", "luxus",
            "reich", "millionen", "million", "teuer", "rolex", "gucci",
            "bankkonto", "millionaer", "euro",
        ],
        description="How often wealth/luxury vocabulary appears.",
    ),
    Metric(
        key="drama_conflict",
        label="Konflikt / Drama",
        kind="keyword_count",
        keywords=[
            "hater", "neid", "blockiert", "ehrenlos", "geruecht", "gerücht",
            "drama", "streit", "beef", "beleidigt", "skandal", "lüge", "luege",
            "verraten", "betrug",
        ],
        description="How often drama/conflict vocabulary appears.",
    ),
    Metric(
        key="hype_adjectives",
        label="Hype-Adjektive",
        kind="keyword_count",
        keywords=[
            "krass", "heftig", "brutal", "übelst", "uebelst", "insane",
            "crazy", "wild", "absolut", "extrem", "hardcore",
        ],
        description="Artificially intensifying adjectives.",
    ),
    Metric(
        key="egocentrism",
        label="Ich-Bezug",
        kind="keyword_count",
        keywords=["ich", "mein", "meine", "mich", "mir", "meins", "meiner"],
        description="First-person references. High = talks about self a lot.",
    ),
    Metric(
        key="denglisch",
        label="Englisch-Anteil (Denglisch)",
        kind="english_count",
        description="Fraction of tokens that are English words.",
    ),
    Metric(
        key="avg_word_len",
        label="Durchschnittliche Wortlänge",
        kind="avg_word_len",
        description="Mean character length of tokens. Proxy for complexity.",
    ),
    Metric(
        key="total_tokens",
        label="Gesamtwörter",
        kind="ratio",
        description="Context metric: total words spoken across sample.",
    ),
]


def metrics_as_prompt_spec() -> str:
    """Render the metric spec as a prompt block for the AI version."""
    lines = ["Compute the following 8 metrics for each creator:"]
    for i, m in enumerate(METRICS, 1):
        line = f"{i}. {m.key} ({m.label}) — {m.description}"
        if m.keywords:
            line += f" Seed words: {', '.join(m.keywords[:8])}..."
        lines.append(line)
    return "\n".join(lines)
