# data/ (regenerable corpus)

Everything in this directory except this README is gitignored.
The full corpus is about 5 MB of JSON and another chunk of raw
comment dumps, regenerable in about 10-20 minutes on a normal
connection. Regenerate locally before running the analysis scripts.

## What lives here after regeneration

```
data/
  transcripts/            # N=25 raw scrape (one JSON per creator)
    _raw/                 # per-video .vtt files cached by yt-dlp
    apored.json
    maithinkx.json
    papaplatte.json
  transcripts_filtered/   # N=25 after speaker filter
  transcripts_n50/        # N=50 raw scrape (150 videos total)
  transcripts_n50_clean/  # N=50 after livestream filter
  transcripts_holdout_n10/ # N=10 held-out validation set
  comments/
    apored/               # one JSON per video plus _summary.json
    maithinkx/
    papaplatte/
```

Source-video transcripts (IT-Mario and Papaplatte's reaction)
also live at the top of `data/` as `.txt` and `.vtt` pairs and
are gitignored by prefix.

## Regenerate: transcripts

The N=25 sample (fast, used for V2 baseline):

```bash
python3 -m src.common.fetch 25
# Writes data/transcripts/{creator}.json for papaplatte,
# apored, and maithinkx.
```

Top up to N=50 (appends new video ids, skipping duplicates):

```bash
python3 bench/fetch_n50_rest.py
# Writes data/transcripts_n50/{creator}.json.
```

The creator list and channel URLs live in
`src/common/fetch.py::CREATORS`. Edit that dict if you want a
different channel lineup.

## Regenerate: comments

```bash
python3 bench/fetch_comments.py --creator papaplatte \
    --n-videos 50 --comments-per-video 200
python3 bench/fetch_comments.py --creator apored \
    --n-videos 50 --comments-per-video 200
python3 bench/fetch_comments.py --creator maithinkx \
    --n-videos 50 --comments-per-video 200
```

Each call writes `data/comments/{creator}/{video_id}.json` plus a
rollup `_summary.json`. Picks the first N videos from the matching
`data/transcripts_n50/{creator}.json` file, so run the transcript
fetch first.

## Regenerate: livestream filter

```bash
.venv/bin/python bench/livestream_filter.py
# Reads data/transcripts_n50/{creator}.json, writes
# data/transcripts_n50_clean/{creator}.json and logs the dropped
# video ids to results/livestream_filter_log.json.
```

## Prerequisites

- `yt-dlp` installed and on PATH (`pip install yt-dlp` or brew).
- A working network connection; YouTube throttles aggressive
  scraping, so the fetch scripts sleep between requests.
- No API key is required for transcript or comment fetching.
  Only the AI-agents method in `bench/ai_rerun_n50.py` needs
  `ANTHROPIC_API_KEY`.

## Notes

- Re-fetching is idempotent by design: the top-up fetcher skips
  video ids already present.
- YouTube auto-caption output is lossy for profanity. T07
  originally spec'd a Whisper vs caption diff on 3 samples; the
  implemented version counts `[__]` censor markers across all 150
  videos instead. See `bench/censorship_analysis.py` and
  `results/profanity_delta.json`.
- The `transcripts_holdout_n10/` set is a fresh 10-video pull per
  creator used only for validation. Do not include it when
  training or tuning keyword lists.
