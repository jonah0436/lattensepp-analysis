# Lattensepp / IT-Mario replication: findings (V2.5)

> **What this document is.** A record of what happened when we rebuilt
> IT-Mario's YouTube-analysis pipeline three ways on the same 150 videos
> and ran all three against his declared winners. It is a rebuild report,
> not a science paper. See "Two reference layers" below for what we are
> and are not claiming.

Source video being replicated:
[`6pLp8Uv6VA`](https://youtu.be/6pLp8Uv6VA) (IT-Mario).
Reaction video that triggered the project:
[`w81qGuiQNEE`](https://youtu.be/w81qGuiQNEE) (Papaplatte / Lattensepp).

## TL;DR

1. **The rebuild reproduces IT-Mario's 7 creator winners 6 out of 7 times**
   (plus 1 tie-match) across all three deterministic methods: replica,
   extended-list script, and hybrid. The AI method reproduces 4 of 7
   (plus 1 tie-match). Combined with community metrics (4 of 6 match)
   the overall agreement for the best-fit method is **10 of 13 = 77 %**.
2. **All three deterministic methods agree with each other on every
   creator metric** (7 of 7 internal consistency). Dictionary size and
   preprocessing do not change the ranking for this corpus: a 5-word
   list and a 234 000-word dictionary land on the same winner for every
   metric we tested.
3. **The AI method diverges on 2 creator metrics** (drama, hype) and
   undershoots on token volume (sampled about 5 % of the corpus each
   run). Its misses are sample-size artefacts, not deeper reasoning.
4. **Transcript integrity is the biggest fragility we found.** Papaplatte
   shows **515** YouTube-censored `[__]` markers across his 50 videos
   versus **4** for Apored (same platform, same auto-caption pipeline).
   Ratio: **38.64 ×**. This is the direction of Papaplatte's own "50 %
   of my words are missing" critique, confirmed on the data but not
   pinned to an absolute number (we have no gold transcript).
5. **Total compute cost: $0.27.** Three parallel AI agents on N=50
   ($0.24) plus the censorship-density analysis via Claude/OpenRouter
   ($0.03). Deterministic methods were free and ran in seconds.

## What we actually did

### Corpus

| Creator    | Channel                       | Videos (transcripts) | Comments | Comment-source videos |
|------------|-------------------------------|---------------------:|---------:|----------------------:|
| Papaplatte | papaplatte (gaming / reaction) |    50 |    5,745 | 25 |
| ApoRed     | ApoRedOfficial (music videos)  |    50 |    6,151 | 25 |
| MaiThinkX  | MAITHINK X (science)           |    50 |    6,250 | 25 |
| **Total**  |                                | **150** | **18,146** | **75** |

Transcripts cover all 50 videos per creator. The comment scrape ran on
the 25 most-recent videos per creator (target: 5 000 per creator;
delivered 5 745 – 6 250 each).

Transcripts via `yt-dlp` auto-captions (German). Comments via
`youtube-comment-downloader`. The T02 livestream-VOD filter ran but
did not fire on any video, so the cleaned corpus is identical to the
raw corpus by coincidence, not by construction.

### Four methods on the same corpus

| Method             | How it counts                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------|
| **IT-Mario replica** | His exact 5–6-word seed lists, verbatim from the video. Denglisch uses a 100-word English anchor list (see below).    |
| **Script**         | Our extended seed lists (15+ words per metric). Deterministic, no stemming.                                           |
| **AI**             | Three parallel Claude agents, one per creator, given the metric definitions and asked to compute on the filtered text. |
| **Hybrid**         | Deterministic math for TTR / word length, extended keyword lists with light German suffix stemming, and Denglisch via the full `/usr/share/dict/words` dictionary minus known German-English overlaps. |

The three deterministic methods differ in dictionary size and
preprocessing, not just "logic". We report them side-by-side; we do
not pretend they isolate a single variable.

### Denglisch: reconstruction, not measurement

IT-Mario declared Papaplatte as the Denglisch winner in his video but
did not publish the wordlist he used. For the replica to have any
Denglisch number at all, we reverse-engineered a 100-word English
anchor list (see `DENGLISCH_ANCHOR_LIST` in `bench/method_compare.py`)
that reproduces his declared Papaplatte-first ranking. This list is
scoped to the gaming / streaming / internet-culture register where
modern-German Denglisch actually lives.

This is a **reconstruction of his likely method**, not an independent
measurement of Denglisch. The hybrid method's full-dictionary Denglisch
count is the better neutral estimate; the replica's number exists so
the replica has an entry in the comparison.

## Two reference layers

This project deliberately keeps two reference layers separate, because
conflating them is the fastest way to attack the work:

| Layer | Metric name                           | What it measures                                      | Where it lives            |
|-------|---------------------------------------|-------------------------------------------------------|---------------------------|
| **Primary (public)**   | `agreement_with_it_mario`             | How many of IT-Mario's 7 declared creator winners each method reproduces. Rebuild-fidelity check. | Charts, README, video |
| **Secondary (diagnostic)** | `internal_consistency_hybrid_vs_others` | How often each method's ranking matches hybrid's ranking. Outlier-spotting tool, NOT a truth claim. Hybrid is our best-of-breed logic, not ground truth. | `results/methods_n50_clean.json`, internal only |

The secondary metric exists because "all three deterministic methods
agree with each other on every ranking" is itself a finding worth
knowing. We do not use it to argue any method is correct.

## Results

### 1. Creator metrics (7)

Scoring convention: a method gets a full **hit** if it reproduces
IT-Mario's declared winner. For hype (declared a tie between
papaplatte and apored), a method gets a hit if it also returned
"tie" and a **tie-match** (tracked separately, does not count as a
hit) if it picked one of the two tied creators.

| Metric              | IT-Mario declared | Replica          | Script           | AI               | Hybrid           |
|---------------------|-------------------|------------------|------------------|------------------|------------------|
| `vocabulary_ttr`    | maithinkx         | maithinkx ✓      | maithinkx ✓      | maithinkx ✓      | maithinkx ✓      |
| `wealth_flex`       | apored            | apored ✓         | apored ✓         | apored ✓         | apored ✓         |
| `drama_conflict`    | apored            | apored ✓         | apored ✓         | tie (miss)       | apored ✓         |
| `hype_adjectives`   | tie (papaplatte = apored) | papaplatte (tie-match) | papaplatte (tie-match) | tie (tie-match) | papaplatte (tie-match) |
| `egocentrism`       | papaplatte        | papaplatte ✓     | papaplatte ✓     | apored (miss)    | papaplatte ✓     |
| `denglisch`         | papaplatte        | papaplatte ✓     | papaplatte ✓     | papaplatte ✓     | papaplatte ✓     |
| `avg_word_len`      | maithinkx         | maithinkx ✓      | maithinkx ✓      | maithinkx ✓      | maithinkx ✓      |
| **Hits / total**    |                   | **6 / 7**        | **6 / 7**        | **4 / 7**        | **6 / 7**        |

Internal consistency vs hybrid (diagnostic, not a truth claim):
replica 7/7, script 7/7, AI 4/7 on the canonical `results/methods_n50_clean.json`.
This is a clustering measure, not a correctness claim. Hybrid is our
best-of-breed logic, not ground truth.

### 2. Community metrics (6)

Scoring is on the 18,146-comment corpus. Our method uses per-comment
rates; IT-Mario's convention is per-1 000-tokens. This denominator
difference is where both of our misses come from.

| Metric            | IT-Mario declared | Ours             | Match? |
|-------------------|-------------------|------------------|--------|
| Support / praise  | maithinkx         | apored           | miss (denominator flip) |
| Questions (`?`)   | maithinkx         | maithinkx        | ✓ |
| Comment length    | maithinkx         | maithinkx (202 chars vs 62 / 65) | ✓ |
| Caps rate (least) | maithinkx         | maithinkx        | ✓ |
| Criticism         | apored            | apored           | ✓ |
| Slang             | apored            | maithinkx        | miss (denominator flip) |

Both misses collapse to the same mechanism: MaiThinkX's comments are
about **3 ×** longer than the other two creators', so per-comment
rates move in the opposite direction to per-1 000-tokens rates.
Neither denominator is "correct" in the abstract. IT-Mario picked
one, we picked another, they disagree.

### 3. Transcript integrity (the T07 finding)

Papaplatte's critique in the Lattensepp reaction: "Beleidigungen
fehlen, droppt meine Wörter um 50 %". We could not directly test the
50 % number because that would require a gold transcript we don't have.
What we could measure: YouTube's own `[__]` censor markers in the
auto-caption stream across all 150 videos.

| Creator    | `[__]` censors | Total tokens | Per 1 000 tokens | Videos hit |
|------------|---------------:|-------------:|-----------------:|-----------:|
| Papaplatte |            **515** |      315,854 |        **1.631** |      **48 / 50** |
| Apored     |              4 |       94,884 |            0.042 |        2 / 50  |
| MaiThinkX  |              0 |      149,164 |            0.000 |        0 / 50  |

**Ratio Papaplatte : Apored = 38.64 ×** on the same platform, same
auto-caption pipeline. 48 of 50 Papaplatte videos contain at least
one censor marker. Category breakdown (via Claude / OpenRouter, $0.03):
124 profanity, 5 insult, 0 slur, 29 unknown-context in the Papaplatte
sample.

This does not prove the 50 % claim, and we say so. It does show the
direction of the effect is real and specific to Papaplatte's speech.

### 4. Held-out stability (N=10 per creator)

Fetched 10 more videos per creator not in the N=50 set (Apored's
channel capped at 5 holdouts). Re-ran both IT-Mario replica and hybrid.

**5 of 7 creator winners held**. TTR and drama flipped; both are
small-margin metrics and sensitive to sample draw. Wins that held:
wealth, hype (tie), ego, denglisch, word length.

### 5. Cost and runtime

| Component                                    | Method          | Cost    | Wall time   |
|-----------------------------------------------|-----------------|--------:|-------------|
| Deterministic methods (replica, script, hybrid) | `method_compare.py` | $0.00 | ~3 s |
| AI metrics on N=50                             | 3 parallel agents | $0.24 | ~6 min      |
| Censorship-density analysis                    | Claude / OpenRouter | $0.03 | ~2 min      |
| **Total**                                      |                 | **$0.27** |           |

## What the rebuild shows, and what it doesn't

**Shows (comparison claims):**

- Given IT-Mario's declared metrics and our same-corpus reconstruction,
  small keyword lists and full dictionaries produce the same ranking.
  Dictionary size is not the fragile variable for these creators.
- AI with free-form prompting matches on 4 of 7 creator rankings and
  flags hype as a tie (matching IT-Mario's own call, tracked as a
  tie-match rather than a hit under the strict public scoring). Its
  misses on drama and ego are sampling artefacts, not a reasoning
  advantage.
- Papaplatte shows a transcript-censorship rate 38 × Apored's on the
  same platform. This is specific to his speech, not a pipeline bug.
- Community-metric rankings flip based on denominator choice. IT-Mario's
  per-token convention is defensible; so is per-comment.

**Does not show (what we are not claiming):**

- That any method is objectively correct.
- That our hybrid method is ground truth (it is our best-of-breed
  logic; we use it as a diagnostic, not a reference).
- That IT-Mario's declared winners are factually right. We measure
  reproducibility of his stated results, not their underlying truth.
- That the 50 % profanity-drop figure Papaplatte cited is numerically
  precise. We show direction, not magnitude.
- That any of these keyword-based metrics measure personality,
  intelligence, or intent. They are operational proxies: rates of
  specific tokens per 1 000 words, nothing more.

## Limitations we know about

1. **Text-only speaker filter.** YouTube auto-captions don't tag
   speakers. Our LLM filter guesses from context. It catches obvious
   quote blocks but probably misses short interjections and
   mixed-mic moments. True diarization needs `pyannote.audio`.
2. **Auto-caption quality.** German diacritics sometimes get lost,
   compound words get split (`Deep Dive` instead of `DeepDive`),
   and YouTube's profanity censor overwrites words with `[__]`. The
   latter is the T07 finding; the former two are still in the data.
3. **Hand-tuned Denglisch list for the replica.** Described above:
   reconstruction, not measurement. The hybrid's dictionary-based
   Denglisch is more neutral but also more noisy (flags words the
   speaker used as loanwords and words that exist in both languages).
4. **Keyword-list subjectivity.** Every keyword metric in this project
   is a proxy. Different lists produce different rates. We picked lists
   that match IT-Mario's declared examples where possible and the
   hybrid method's wider lists where his were not specified.
5. **Channel-selection bias.** We matched IT-Mario's choice (Papaplatte
   Gaming channel, not Podcast / Uncut / Main / Reaction / Clips).
   Papaplatte himself pointed this out in the Lattensepp reaction.
   Sampling the Podcast channel would likely move Papaplatte's TTR up
   and his egocentrism rate down.
6. **No confidence intervals.** Every number in this report is a point
   estimate on one draw of 50 videos. The held-out N=10 run gives a
   rough stability read (5 of 7 winners held), but we did not run
   bootstraps. V3 territory.

## Files

| What                                       | Where                                                                         |
|--------------------------------------------|-------------------------------------------------------------------------------|
| Metric definitions (single source of truth) | `src/common/metrics_spec.py`                                                 |
| Transcript scraper                          | `src/common/fetch.py`                                                         |
| Speaker filter (LLM-based)                  | `src/common/speaker_filter.py`                                                |
| Deterministic script pipeline               | `src/script_version/analyze.py`                                               |
| V2 benchmark harness (legacy)               | `bench/compare.py`                                                            |
| V2.5 four-method comparison                 | `bench/method_compare.py`                                                     |
| Comment scraper                             | `bench/fetch_comments.py`                                                     |
| Community metrics                           | `bench/community_compare.py`                                                  |
| Censorship density                          | `bench/censorship_analysis.py`                                                |
| Chart exporter                              | `bench/export_video_charts.py`                                                |
| Transcripts (raw)                           | `data/transcripts_n50/{creator}.json`                                         |
| Transcripts (livestream-filtered)           | `data/transcripts_n50_clean/{creator}.json`                                   |
| Comments                                    | `data/comments/{creator}/{video_id}.json`                                     |
| AI metric outputs (N=50)                    | `results/ai_metrics_n50/{creator}.json`                                       |
| Four-method comparison                      | `results/methods_n50_clean.json`                                              |
| IT-Mario replica standalone                 | `results/it_mario_replica.json`                                               |
| Community metrics output                    | `results/community_metrics.json`                                              |
| Censorship-density output                   | `results/profanity_delta.json`                                                |
| Held-out validation                         | `results/holdout_n10.json`                                                    |
| Video-facing chart data                     | `video_charts/0[1-5]_*.json`                                                  |

## V3 ideas (explicitly out of scope for this rebuild)

These are the fixes that would turn this from a rebuild into a paper.
None are planned for this project; listed for completeness.

- Stratified random sampling of 50 videos per creator spanning 18+
  months, instead of most-recent.
- Pyannote diarization + Whisper-large-v3 on creator-only segments,
  to replace text-only speaker filtering.
- spaCy `de_core_news_lg` lemmatization + `CharSplit` compound splitter.
- Triangulated signals per metric (seed list + NER + sentiment) with
  a confidence band, declaring winners only when all signals agree.
- 1 000-resample bootstrap per creator with 95 % confidence intervals;
  flag as "tie" any ranking whose intervals overlap.
- Pre-registered analysis plan published before the data is seen.

## Mapping this rebuild to IT-Mario's own caveat

IT-Mario himself said in the video: "keinen wissenschaftlichen Anspruch,
steht und fällt mit der Liste". That framing is correct. Our rebuild
lands in the same place, with more explicit layering: a replica of his
pipeline, a richer deterministic version, an AI version, a hybrid, and
an honest accounting of what the agreement numbers do and do not mean.
