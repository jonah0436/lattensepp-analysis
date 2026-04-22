# Current state

> One file, authoritative. If anything elsewhere in the repo contradicts
> this document, this document wins and the other file is stale. Updated
> 2026-04-22.

## What the project is, in one sentence

A rebuild of IT-Mario's YouTube-analysis pipeline on the same 150-video
corpus, run four ways (his exact replica, an extended-list script, an
AI version, and a best-of-breed hybrid), packaged as a German YouTube
video about methodology rather than about any one creator.

## Current version

**V2.5.** All of T01 through T13 complete. V2 artefacts exist in the
repo but are superseded. See "Legacy paths" below.

## Dataset

- 50 videos per creator, 3 creators, 150 videos total.
- 18,146 YouTube comments across the 25 most-recent videos per creator.
- Transcripts: `data/transcripts_n50/` (raw), `data/transcripts_n50_clean/`
  (livestream-filtered; the T02 filter was a no-op, so these files are
  identical by coincidence).
- Comments: `data/comments/{creator}/{video_id}.json`.

## Methods

Four are implemented. The video narrative talks about three of them
(replica / AI / hybrid); the script version is included in the code for
completeness and for the deterministic-trio consistency check.

| Method             | Purpose                                           | Reported in video? |
|--------------------|---------------------------------------------------|--------------------|
| IT-Mario replica   | His exact pipeline on the same corpus             | yes                |
| Script             | Extended keyword lists, no stemming               | no (internal only) |
| AI agents          | Three parallel Claude agents, one per creator     | yes                |
| Hybrid             | Deterministic math + stemming + full dictionary   | yes                |

## Reference layers (this is the anti-circularity section)

**Primary, public, video-facing** (`agreement_with_it_mario`):
how many of IT-Mario's 7 declared creator winners each method
reproduces on the same corpus. This is the only accuracy claim the
project makes publicly. Output key lives in
`results/methods_n50_clean.json`.

**Secondary, diagnostic only** (`internal_consistency_hybrid_vs_others`):
how often each method's ranking matches the hybrid method's ranking
on the same corpus. Hybrid is our best-of-breed logic, NOT ground
truth. Use this to spot outlier methods; do not use it to claim any
method is correct. Output key also lives in
`results/methods_n50_clean.json`.

Any public artefact (chart, README, video script, slide) that cites an
accuracy number MUST be referring to the primary metric.

## Headline numbers

| Metric                                 | Value       |
|----------------------------------------|-------------|
| Agreement with IT-Mario (overall)      | **10 / 13 = 77 %** |
| Creator-metric hits (best-fit method)  | 6 / 7 hits + 1 tie-match |
| Community-metric matches               | 4 / 6       |
| Papaplatte : Apored censor ratio       | **38.64 ×** |
| Held-out stability (N=10)              | 5 / 7 winners held |
| Total compute cost                     | **$0.27**   |

Cost breakdown: $0.24 for the three parallel Claude agents (T08) and
$0.03 for the censorship-density analysis via Claude on OpenRouter
(T07 pivot from the original Whisper plan). Deterministic methods
were free.

## Canonical file paths

Each artefact has exactly one source-of-truth path. Anything else is
either intermediate or legacy.

### Code

| Role                               | Path                                |
|------------------------------------|-------------------------------------|
| Four-method comparison             | `bench/method_compare.py`           |
| Chart data exporter                | `bench/export_video_charts.py`      |
| Community metrics                  | `bench/community_compare.py`        |
| Censorship-density analysis        | `bench/censorship_analysis.py`      |
| Comment scraper                    | `bench/fetch_comments.py`           |
| Livestream-VOD filter              | `bench/livestream_filter.py`        |

### Results

| Role                               | Path                                      |
|------------------------------------|-------------------------------------------|
| Four-method comparison (canonical) | `results/methods_n50_clean.json`          |
| IT-Mario replica standalone        | `results/it_mario_replica.json`           |
| Community metrics                  | `results/community_metrics.json`          |
| Censorship-density output          | `results/profanity_delta.json`            |
| Held-out validation                | `results/holdout_n10.json`                |
| Chart data for video               | `video_charts/0[1-5]_*.json`              |

### Docs

| Role                               | Path                                |
|------------------------------------|-------------------------------------|
| This file (current state)          | `docs/CURRENT_STATE.md`             |
| Findings report                    | `docs/FINDINGS.md`                  |
| Project plan + scene arc           | `docs/PROJECT.md`                   |
| Task spec                          | `docs/TASKS.md`                     |
| IT-Mario's original pipeline       | `docs/IT-MARIO-VIDEO.md`            |
| Main video script                  | `docs/video-script.md`              |
| Shorts briefs                      | `docs/shorts-script.md`             |

## Legacy paths (V2, superseded; do not treat as current)

These files still exist in the repo because they produced reproducible
V2 outputs and are useful as a record. They are NOT the current pipeline.

| Legacy path                              | Superseded by                                  |
|------------------------------------------|------------------------------------------------|
| `bench/compare.py`                       | `bench/method_compare.py`                      |
| `data/transcripts/` (N=25 per creator)   | `data/transcripts_n50/` (N=50)                 |
| `results/ai_metrics/` (V2 AI outputs)    | `results/ai_metrics_n50/`                      |
| `results/methods_n50.json` (raw)         | `results/methods_n50_clean.json` (canonical)   |
| `results/report.json` (V2 summary)       | `docs/FINDINGS.md` (V2.5)                      |

If `bench/compare.py` or `results/ai_metrics/` is cited anywhere outside
this legacy table, that citation is stale and should be updated to the
corresponding canonical path.

## What each method claims, and what it does not

| Claim                                                        | Do we make it? |
|--------------------------------------------------------------|----------------|
| Our rebuild reproduces IT-Mario's 7 declared winners 6 of 7 times | **yes** (replica, script, hybrid each do) |
| The three deterministic methods agree on every creator ranking | **yes**        |
| AI matches the rebuild on 4 of 7 creator metrics (plus a shared tie-match on hype) | **yes** |
| YouTube auto-captions censor Papaplatte 38 × more than Apored | **yes** (same platform, same pipeline) |
| Papaplatte's "50 % of words dropped" is directionally true   | **yes** (magnitude not measured)  |
| Any method is objectively correct                            | no              |
| Hybrid is ground truth                                       | no (it is the secondary diagnostic reference) |
| IT-Mario's declared winners are factually correct            | no (we measure fidelity to his stated results, not their underlying truth) |
| Papaplatte's absolute profanity-drop rate                    | no (no gold transcript available) |
| Keyword metrics measure personality, intelligence, or intent | no (they are proxies for specific token rates) |

## Known open items

- `git init` and public push to GitHub (awaiting Jonah's call on repo
  layout: standalone vs monorepo).
- Video-script framing audit before recording: verify that every
  accuracy claim in `docs/video-script.md` refers to the primary metric
  (agreement with IT-Mario), not to the hybrid diagnostic.

## How to rebuild this report from scratch

```bash
# Deterministic pipeline (seconds, free)
.venv/bin/python3 bench/method_compare.py --corpus n50_clean

# Chart JSONs for video production (seconds, free)
.venv/bin/python3 bench/export_video_charts.py

# Community metrics (seconds, free)
.venv/bin/python3 bench/community_compare.py

# Censorship-density analysis (~2 minutes, ~$0.03 on OpenRouter)
.venv/bin/python3 bench/censorship_analysis.py

# AI metrics (~6 minutes, ~$0.24)
# See results/ai_metrics_n50/ for cached outputs; re-running requires
# ANTHROPIC_API_KEY set and the three parallel-agent script.
```

Keys required: `ANTHROPIC_API_KEY` for the AI metrics pass and
`OPENROUTER_API_KEY` for the censorship-density analysis. All other
steps are free and run locally.
