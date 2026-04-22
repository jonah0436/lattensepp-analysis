# Lattensepp / IT-Mario Replication — V2.5

Rebuilds the YouTube-analysis pipeline from IT-Mario's video
"Ich wurde wissenschaftlich auseinandergenommen" three different
ways on the same 150-video corpus, then scores each method against
his declared winners. The goal is a legible, side-by-side comparison
of a hand-written keyword script, three parallel AI agents, and a
hybrid that mixes deterministic math with extended keyword lists.

## Headline numbers

- 10 of 13 metrics (77%) agree with IT-Mario's declared winners
  across all three methods.
- Corpus: 150 videos (50 per creator: apored, maithinkx, papaplatte)
  plus 18,146 YouTube comments.
- Total compute cost: $0.27 ($0.24 for the three parallel AI agents
  plus $0.03 for the Claude-via-OpenRouter censorship-density
  analysis). The deterministic methods are free on a laptop.

Source: `video_charts/05_bottom_line_summary.json`.

## The three methods

1. **IT-Mario replica.** His exact 5-6 word keyword lists as stated
   on camera. Deterministic. Reproduces what he would have computed
   with his own declared inputs.
2. **AI agents.** Three parallel Claude agents, one per creator,
   each given the metric spec and asked to count and normalize. No
   shared state between agents.
3. **Hybrid.** Extended keyword lists plus simple stemming, a
   234k-word English dictionary for the denglisch metric, and pure
   math for TTR / word length / token count. This is our best-of-
   breed internal diagnostic, NOT a truth claim; the public accuracy
   number is each method's agreement with IT-Mario's declared
   winners. See `docs/CURRENT_STATE.md` for the full primary/
   secondary reference split.

A fourth deterministic "script" method (wider keyword lists, no
stemming) lives in the repo as an internal baseline but does not
appear in the video narrative.

## Dataset

- 150 German YouTube videos: 50 each from apored, maithinkx, and
  papaplatte.
- 18,146 comments scraped from a subset of those videos.
- All data is regenerable via the fetch scripts and is gitignored.
  See `data/README.md` for the exact commands.

## How to reproduce

```bash
# 1. Clone and enter the repo
git clone https://github.com/jonah0436/lattensepp-analysis.git
cd lattensepp-analysis

# 2. Create a virtualenv and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Set the API keys you need
export ANTHROPIC_API_KEY="sk-ant-..."    # for the AI-agents method (T08)
export OPENROUTER_API_KEY="sk-or-..."    # for the censorship-density analysis (T07)

# 4. Rebuild the corpus (takes about 10 minutes, downloads transcripts)
python3 bench/fetch_n50_rest.py
python3 bench/fetch_comments.py --creator papaplatte --n-videos 50 \
    --comments-per-video 200

# 5. Re-run the three-method comparison on the N=50 clean corpus
.venv/bin/python bench/method_compare.py

# 6. Rerun the AI agents (costs about $0.24)
.venv/bin/python bench/ai_rerun_n50.py

# 7. Compute the 6 community metrics
.venv/bin/python bench/community_compare.py

# 8. Render the video-chart JSONs
.venv/bin/python bench/export_video_charts.py

# 9. Render the PNG charts
.venv/bin/python bench/visualize_methods.py

# 10. Open the dashboard
open report.html
```

Use `.venv/bin/python` for any script that imports matplotlib. Plain
`python3` works for fetch scripts and pure-stdlib analysis.

## Results

- `results/methods_n50_clean.json`: four-method accuracy on the
  livestream-filtered N=50 corpus.
- `results/community_metrics.json`: 6 community metrics across
  18,146 comments.
- `results/accuracy_summary.json`, `results/accuracy_detail.json`:
  MAPE plus winner-hit rates per method per metric.
- `video_charts/*.json`: chart-data exports for video production.
- `results/charts/*.png`: 8 rendered charts for the dashboard.
- `report.html`: the full interactive dashboard.

## Project layout

```
src/
  common/
    metrics_spec.py      # 8-metric definitions, single source of truth
    fetch.py             # yt-dlp scraper with CREATORS dict
    speaker_filter.py    # LLM-based text speaker filter
  script_version/
    analyze.py           # deterministic pipeline (internal baseline)
  ai_version/
    analyze.py           # AI-agent pipeline (single-creator entry)

bench/
  compare.py                # 4-condition benchmark (N=25)
  method_compare.py         # 4-method N=50 comparison
  ai_rerun_n50.py           # parallel 3-agent AI run on N=50
  community_compare.py      # 6 community metrics on comments
  livestream_filter.py      # livestream VOD detection
  fetch_comments.py         # YouTube-comment scraper
  fetch_n50_rest.py         # top-up fetcher (25 to 50)
  export_video_charts.py    # chart-data JSONs for video production
  visualize.py              # charts 1-5
  visualize_methods.py      # charts 6-8

data/     # gitignored; regenerate via fetch scripts
docs/     # project brief, findings, task plan
results/  # JSON outputs (committed)
video_charts/  # video-production chart JSONs (committed)
```

## Companion video

This repo is the codebase for the video "Wir haben IT-Mario
wissenschaftlich auseinandergenommen" on a new German data / AI
YouTube channel. Channel link: TBD (will be added once public).

## Attribution

- IT-Mario's original video:
  https://www.youtube.com/watch?v=6pLp8Uv6VA
- Papaplatte's reaction:
  https://www.youtube.com/watch?v=w81qGuiQNEE
- All code in this repo is original. The keyword lists for the
  `it_mario` replica method are verbatim from IT-Mario's
  on-camera explanation.

## License

MIT. See `LICENSE`.

## Known limitations

1. The speaker filter is text-only. It can't separate short
   interjections from a guest or a movie clip without true audio
   diarization. That work is deferred to V3 with pyannote.
2. The papaplatte N=50 corpus still contains co-host dialogue
   inside his own videos. Reaction-clip audio couldn't be
   reliably separated without speaker labels.
3. The denglisch dictionary is English-dominant. Words like "Bro"
   that are equally German and English slang get counted as
   English. V2.5 task T06 reverse-engineered IT-Mario's declared
   denglisch numbers to a 100-word English anchor list; a full
   lemmatization pass is deferred to V3.
4. "Ground truth" is IT-Mario's on-screen winners, not his raw
   data. He did not publish the 150-video list he used.
5. The hybrid's simple suffix stripping is not real lemmatization.
   It occasionally over-matches. Logged for V3.3.

These caveats are intentional in the V2.5 scope and are called
out in the video's methodology scene.
