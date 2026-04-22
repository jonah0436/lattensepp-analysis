# V2.5 Task Specification

Format per task: ID, owner, dependencies, acceptance criteria, and
effort estimate.

Status tags: [ ] open, [x] done, [~] in progress, [!] blocked.

Claude owns all T0x tasks (data and code). Jonah owns all T2x tasks
(video production).

---

## Week 1 — Data and code (Claude)

### T01. Fix FINDINGS.md sample-size error

- [x] Owner: Claude
- Dependencies: none
- Estimate: 10 min
- Acceptance:
  - FINDINGS.md line 21 no longer says IT-Mario used 1-2 videos
  - TL;DR reflects he used 50 per creator (150 total plus 15k
    comments)
  - "Why IT-Mario landed where he did" section revised to match
- Output: edited docs/FINDINGS.md

### T02. Livestream VOD detection and filter

- [x] Owner: Claude (no-op: heuristic did not fire on any of 150 videos)
- Dependencies: T01
- Estimate: 45 min
- Acceptance:
  - New module bench/livestream_filter.py identifies livestream VODs
    from the N=50 corpus
  - Heuristic: video duration greater than 60 minutes AND (title
    contains a live keyword such as "live" / "livestream" /
    "stream" OR video metadata tag includes isLiveContent)
  - data/transcripts_n50_clean/ contains the filtered corpus
  - Per-creator count of excluded videos logged to
    results/livestream_filter_log.json
- Output: data/transcripts_n50_clean/\*.json,
  bench/livestream_filter.py, results/livestream_filter_log.json

### T03. Comment scraper pilot (Papaplatte only)

- [x] Owner: Claude
- Dependencies: none
- Estimate: 60 min
- Acceptance:
  - Scrapes top N comments per video using yt-dlp --write-comments
    or youtube-comment-downloader (Claude picks whichever works
    first)
  - Pilot run on 5 Papaplatte videos completes without error
  - Comments stored in data/comments/{creator}/{video_id}.json
  - Per-video comment count logged
- Output: bench/fetch_comments.py, data/comments/papaplatte/ pilot

### T04. Comment scraper full run

- [x] Owner: Claude (18,146 comments across 76 videos, target was 15k)
- Dependencies: T03
- Estimate: 90 min
- Acceptance:
  - Target: 5,000 comments per creator, 15,000 total
  - All 3 creators complete
  - Rate-limit handling: retry with exponential backoff
  - Summary counts written to data/comments/\_summary.json
- Output: data/comments/{creator}/\*.json, count greater than or
  equal to 15,000

### T05. Community metrics implementation

- [x] Owner: Claude (4/6 match IT-Mario; 2 misses are denominator choice)
- Dependencies: T04
- Estimate: 90 min
- Acceptance:
  - Six metrics computed on the comment corpus:
    support (positive / praise keyword rate),
    questions (? symbol rate),
    comment_length (mean characters per comment),
    caps_rate (fraction of tokens in ALL CAPS),
    criticism (negative keyword rate),
    slang (internet slang rate)
  - Per-creator winners declared
  - Comparison with IT-Mario's declared community winners (all 6)
- Output: results/community_metrics.json,
  bench/community_compare.py

### T06. Denglisch reverse-engineer for IT-Mario replica

- [x] Owner: Claude
- Dependencies: none
- Estimate: 45 min
- Acceptance:
  - IT-Mario's declared denglisch rates are backed out to infer his
    likely wordlist size
  - Replica updated to use a 100-word English anchor list that
    reproduces his declared ranking (Papaplatte first)
  - results/it_mario_replica.json no longer has denglisch=None
  - Decision and wordlist documented in
    bench/method_compare.py comments
- Output: updated bench/method_compare.py,
  updated results/it_mario_replica.json

### T07. Whisper profanity test (3 Papaplatte videos)

- [x] Owner: Claude (**PIVOTED**: OpenRouter has no Whisper, local declined. Shipped `[__]`-density analysis across full 150-video corpus instead. See HANDOFF §3 and `results/profanity_delta.json`. Output: 38× Papaplatte-vs-Apored censorship ratio, $0.0276 spend.)
- Dependencies: none
- Estimate: 60 min
- Acceptance:
  - Pick 3 Papaplatte videos with highest [\_\_] censor density in
    their auto-captions
  - Download audio via yt-dlp -x
  - Run Whisper-large-v3 locally (if the .venv has it) or via API
  - Tokenize both caption and Whisper transcripts with the same
    regex
  - Report: total token count delta, profanity-specific delta,
    per-video and mean
  - Total cost stays under $0.40
- Output: results/profanity_delta.json,
  data/whisper_samples/{video_id}.json

### T08. AI re-run on N=50 cleaned corpus

- [x] Owner: Claude (ran via local Claude CLI claude-haiku-4-5; $0.24)
- Dependencies: T02
- Estimate: 15 min setup, 10 min runtime
- Acceptance:
  - 3 parallel Claude agents run on data/transcripts_n50_clean/
  - Output written to results/ai_metrics_n50/{creator}.json
  - Cost stays under $0.60
- Output: results/ai_metrics_n50/\*.json

### T09. 3-method re-run on cleaned corpus

- [x] Owner: Claude
- Dependencies: T02, T06, T08
- Estimate: 5 min
- Acceptance:
  - bench/method_compare.py runs on data/transcripts_n50_clean/
    with AI pulled from results/ai_metrics_n50/
  - results/methods_n50_clean.json written with all 4 methods; the
    3 for the video (IT-Mario replica / AI / Hybrid) extractable
    cleanly for T10 chart exports
  - IT-Mario vs AI vs Hybrid story is clean for the video
- Output: results/methods_n50_clean.json

### T10. Chart data JSON exports for video production

- [x] Owner: Claude (chart 03 is `03_censorship_density.json`, not `03_whisper_delta.json`)
- Dependencies: T05, T07, T09
- Estimate: 45 min
- Acceptance: one JSON per chart, each file containing title,
  x/y axis labels, series data, and a footnote source path.
  Files:
  - video_charts/01_three_method_accuracy_matrix.json
  - video_charts/02_three_method_winners.json
  - video_charts/03_censorship_density.json (T07 pivot; was 03_whisper_delta.json)
  - video_charts/04_community_metrics.json
  - video_charts/05_bottom_line_summary.json
- Output: video_charts/\*.json

### T11. N=10 held-out validation set

- [x] Owner: Claude
- Dependencies: T02
- Estimate: 30 min
- Acceptance:
  - Fetch 10 more videos per creator (not in the N=50 corpus)
  - Run both IT-Mario and Hybrid methods on the held-out set
  - Stability check: do winners match the N=50 result?
  - Result logged in results/holdout_n10.json
- Output: results/holdout_n10.json

### T12. GitHub repo cleanup and README

- [x] Owner: Claude (shipped — public repo live at `github.com/jonah0436/lattensepp-analysis`)
- Dependencies: all data tasks complete
- Estimate: 60 min
- Acceptance:
  - README.md with project overview, how to reproduce, license
  - .gitignore covers .venv, data/whisper_samples/, HANDOFF.md
  - License: MIT, added as LICENSE file
  - All Python modules have a top-level docstring
  - Repo pushed public at github.com/jonah0436/lattensepp-analysis
- Output: public GitHub repo URL

### T13. Video script beats and Shorts beats

- [x] Owner: Claude
- Dependencies: T10
- Estimate: 90 min
- Acceptance:
  - docs/video-script.md with 8 scenes following the methodology-
    showcase arc (Hook / Mario's pipeline / Our 3 reimplementations
    / Accuracy comparison / Where his method misses / Community
    bonus / Meta reveal / CTA). Each scene documents duration
    target, on-screen elements, message intent, and German key
    phrases for hooks and punchlines. Tone: nerdy-but-accessible.
    A normal viewer should follow without already knowing what TTR
    means.
  - docs/shorts-script.md with 3 Short briefs:
    Short #1: "three ways to rebuild his pipeline" (method reveal)
    Short #2: YouTube censors Papaplatte (Whisper delta)
    Short #3: community reveal
- Output: docs/video-script.md, docs/shorts-script.md

---

## Week 2 — Video production (Jonah)

### T20. Channel setup

- [ ] Owner: Jonah
- Estimate: 60 min
- Acceptance: channel handle, banner, about section, channel
  category. Minimalist data-viz visual convention established.

### T21. Remotion / Manim animations

- [ ] Owner: Jonah
- Dependencies: T10 (chart JSON), T13 (script)
- Estimate: 2 days
- Acceptance: animated scenes matching script timing. One animation
  per chart in video_charts/ plus the flowchart in Scene 3.

### T22. Voiceover and face-cam recording

- [ ] Owner: Jonah
- Dependencies: T21
- Estimate: 1 day
- Acceptance: clean German audio for all scenes. Face-cam recorded
  for Scene 1 hook, Scene 4 reactions, Scene 7 meta reveal.

### T23. Editing and final cut

- [ ] Owner: Jonah
- Dependencies: T22
- Estimate: 2 days
- Acceptance: 6-10 minute final export. Clips of IT-Mario and
  Papaplatte capped at 10 seconds each.

### T24. Thumbnail design

- [ ] Owner: Jonah
- Dependencies: none (runs parallel to T21-T23)
- Estimate: 90 min
- Acceptance: clean minimalist data-viz style, single headline
  number or short phrase.

### T25. Shorts cutdown

- [ ] Owner: Jonah
- Dependencies: T23
- Estimate: 1 day
- Acceptance: 3 Shorts of 45-60 seconds each, each standalone,
  each linking back to the main video.

### T26. Upload and launch sequence

- [ ] Owner: Jonah
- Dependencies: T23, T24, T25
- Estimate: 2 hours on launch day, intermittent over 7 days
- Acceptance:
  - Main video live morning DE time
  - Short #1 two hours later same day
  - Reddit posts day +1 on r/papaplatte, r/de, relevant data subs
  - Shorts #2 and #3 on day +2 and day +4
  - Retro pinned comment on main video day +7

---

## Cut list (if behind schedule at Day 5)

Ordered from first to cut to last:

1. T11 (N=10 held-out validation): internal only, no video impact
2. Part of T05: skip AI sentiment classification, use keyword rates
   for support and criticism instead
3. T06 (denglisch reverse-engineer): fall back to "method unknown,
   used our hybrid" disclosed in the video
4. Part of T07: drop Whisper from 3 Papaplatte samples to 1 if
   runtime blows up

Do not cut: T01 findings fix, T02 livestream filter, T04 comments,
T07 Whisper, T08 AI re-run (now in-video, not optional),
T09 clean re-run, T13 script. The 3-method comparison (his script
/ AI / ours) is the spine of the video narrative and cannot collapse.

---

## Dependency graph

```
T01 -> T02 -> T08 -> T09 -> T10 -> T13
T02 -> T11
T03 -> T04 -> T05 -> T10
T06 -> T09
T07 -> T10
all data tasks -> T12
T13 -> T21 -> T22 -> T23 -> T25 -> T26
T24 runs parallel to T21-T25
```

---

## Budget tracking

Actual spend: $0.27 against $5.00 cap.

| Task | Projected | Actual |
|---|---:|---:|
| T07 censorship-density (pivoted from Whisper) | $0.30 | $0.03 |
| T08 AI re-run on N=50 | $0.56 | $0.24 |
| T05 AI sentiment (cut to keyword rates) | $1.00 | $0.00 |
| Headroom remaining | $3.14 | $4.73 |
| **Total cap** | **$5.00** | **$0.27** |
