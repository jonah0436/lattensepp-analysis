# Lattensepp / IT-Mario Replication — System Specification

Version: 2.5 (public release)
Repository: `github.com/jonah0436/lattensepp-analysis`
Last updated: 2026-04-22

This document is a self-contained specification of the entire
project. A reader with no access to the repo should be able to
reason about what we did, how the numbers were computed, what the
scoring conventions are, and where each claim comes from. It is
written so it can be pasted into a language model for analysis.

---

## 1. TL;DR

A German YouTuber named IT-Mario published a video in which he
described, on camera, his full pipeline for analyzing the
vocabulary and community of three other German creators
(Papaplatte, Apored, MaiThinkX). He declared 13 winners (7 across
video metrics, 6 across community metrics).

This project rebuilds that pipeline on the same 150-video corpus
three separate ways and grades each method on how well it
reproduces IT-Mario's declared winners. The headline result:

- 10 of 13 declared winners (77%) are reproduced by our best-fit
  deterministic method on the same corpus.
- The three deterministic methods (his exact replica, our extended
  script, our hybrid) all hit 6 of 7 creator metrics plus a
  tie-match on the declared-tie metric.
- The AI-agent method hits 4 of 7 creator metrics plus the same
  tie-match.
- A discovery outside the 13 metrics: YouTube auto-captions
  censored Papaplatte 38 times more often than Apored across 50
  videos each (515 vs 4 `[__]` markers), with MaiThinkX at zero as
  the anti-control.
- Total compute spend: $0.27 against a $5.00 cap.

The project's claim is fidelity to IT-Mario's stated results on
the same corpus. It does not claim any method is objectively
correct, and it does not treat its own hybrid method as ground
truth.

---

## 2. The source work being replicated

IT-Mario is a self-described Data Scientist who published a video
titled roughly "Aped, Papa Platte und My Think: who has the
biggest vocabulary?" (YouTube ID `6pLp8Uv6VA`). In that video he
walked through his 13-step pipeline:

1. Scope: 150 videos (50 per creator) plus about 15,000 comments.
2. Abandoned local-AI transcription (too compute-heavy, YouTube
   blocked scraping).
3. Used YouTube auto-generated captions instead, cleaned them with
   a second script.
4. Rejected manually reading the 150 transcripts.
5. Computed vocabulary uniqueness (raw count, biased by total
   volume).
6. Corrected to type-token ratio (TTR = unique / total).
7. Built keyword lists for "wealth" and "drama" and counted hits
   per 1,000 tokens.
8. Built a "hype-adjectives" list.
9. Built an "egocentrism" list (first-person pronouns).
10. Computed a "denglisch" (English-in-German) rate (method not
    disclosed on camera).
11. Computed mean word length.
12. Ran six community metrics on about 15,000 comments.
13. Wrapped up with a caveat that the results are "not
    particularly spectacular; the point is the methodology."

The winners he declared on camera are the ground truth our project
grades against. See section 5 for the full table.

---

## 3. What we built

Four separate implementations of the same spec run on the same
corpus. Three appear in the public video; the fourth is an
internal deterministic baseline.

| Method          | What it is                                                            | In video? |
|-----------------|-----------------------------------------------------------------------|-----------|
| IT-Mario replica | His exact 5-6 word keyword lists, stated on camera. Deterministic.    | yes       |
| Script          | Extended keyword lists, no stemming, wider dictionary. Deterministic. | no        |
| AI agents       | Three parallel Claude Haiku 4.5 agents, one per creator, free-form.   | yes       |
| Hybrid          | Extended lists plus simple stemming, a 234k-word English dictionary for denglisch, and pure math for TTR, word length, and token count. | yes       |

The hybrid is our best-of-breed internal diagnostic. It is NOT
claimed as truth. Any public accuracy number is fidelity to
IT-Mario's declared winners, not fidelity to the hybrid.

---

## 4. Dataset

- **150 video transcripts.** 50 videos per creator across three
  creators (Papaplatte, Apored, MaiThinkX). Sourced via yt-dlp as
  YouTube auto-generated captions (same source IT-Mario used).
- **18,146 YouTube comments.** Across 76 videos, about 5,000 per
  creator. Sourced via a comment-scraper script with exponential
  backoff. The target from IT-Mario's stated scope was 15,000
  total; we overshot.
- **Text only, no audio.** We did not transcribe the raw audio.
  The pipeline operates on YouTube's auto-generated captions,
  which is the same data source IT-Mario used. Section 9 explains
  why this matters.
- **Papaplatte channel scope: Gaming only.** Matches IT-Mario's
  choice. Papaplatte also runs Podcast, Uncut, Main, Reaction, and
  Clips channels; multi-channel sampling is deferred to V3.

All data is regenerable via `bench/fetch_n50_rest.py` and
`bench/fetch_comments.py`. Raw data is gitignored so the repo
stays under a megabyte.

---

## 5. The 13 metrics

### 5a. Seven creator metrics (on video transcripts)

Each creator has 50 transcripts concatenated into a single spoken
text corpus. The metrics are:

| Key                | What it measures                                                                             | IT-Mario's seed words                         | IT-Mario's declared winner |
|--------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------|----------------------------|
| `vocabulary_ttr`   | Type-Token Ratio: unique_words / total_words. Higher = bigger relative vocabulary.           | (no keyword list; pure math)                  | MaiThinkX                  |
| `wealth_flex`      | Rate of wealth-related keyword hits per 1,000 tokens.                                        | Geld, Cash, kaufen, Penthouse, Premium        | Apored                     |
| `drama_conflict`   | Rate of drama/conflict keyword hits per 1,000 tokens.                                        | Hater, Neid, blockiert, ehrenlos, Gerücht     | Apored                     |
| `hype_adjectives`  | Rate of intensifier adjectives per 1,000 tokens.                                             | krass, heftig, brutal, übelst                 | Tie (Papaplatte + Apored)  |
| `egocentrism`      | Rate of first-person pronouns per 1,000 tokens.                                              | ich, mein, meine, mich, mir                   | Papaplatte                 |
| `denglisch`        | Fraction of tokens that are English words. Method underspecified in the source video.        | (no list stated on camera)                    | Papaplatte                 |
| `avg_word_len`     | Mean character length of tokens. Proxy for vocabulary complexity.                            | (pure math)                                   | MaiThinkX                  |

The full seed-word lists for the script and hybrid methods are in
`src/common/metrics_spec.py`. The IT-Mario-replica seed lists are
verbatim from his on-camera explanation and live in
`bench/method_compare.py`.

Note on `denglisch`: IT-Mario did not describe how he computed
this metric on camera. Our replica reverse-engineers his declared
ranking (Papaplatte first) using a 100-word English anchor list.
Our hybrid uses a 234k-word English dictionary for the same
metric.

Note on tokenization: auto-captions lose word boundaries in slang
compounds ("Burgies sneaken" gets split into two tokens). This is
a limitation of the source data, not of the method.

### 5b. Six community metrics (on comments)

Each creator has about 5,000 to 7,000 comments. The metrics are
computed per 1,000 comment tokens:

| Key              | What it measures                                         | IT-Mario's declared winner |
|------------------|----------------------------------------------------------|----------------------------|
| `support`        | Positive / praise keyword rate.                          | MaiThinkX                  |
| `questions`      | Rate of `?` tokens per 1,000 comment tokens.             | MaiThinkX                  |
| `comment_length` | Mean characters per comment.                             | MaiThinkX                  |
| `caps_rate`      | Fraction of tokens that are ALL CAPS. **Lower wins.**    | MaiThinkX                  |
| `criticism`      | Negative keyword rate.                                   | Apored                     |
| `slang`          | Internet-slang rate.                                     | Apored                     |

`caps_rate` is inverted: a lower value wins. All others: higher
value wins.

IT-Mario measured support and slang per-comment. We measure per
1,000 tokens. This denominator choice is what flips two of the six
community winners; see section 8b.

---

## 6. The four methods in detail

All four methods compute the same 8 keys
(`vocabulary_ttr`, `wealth_flex`, `drama_conflict`,
`hype_adjectives`, `egocentrism`, `denglisch`, `avg_word_len`,
`total_tokens`) for each of the three creators. `total_tokens` is
a context metric, not a winner metric, so 7 of the 8 contribute to
the agreement count.

### 6a. IT-Mario replica

- Deterministic.
- Uses his exact verbatim 5-6 word keyword lists, no extensions,
  no stemming, no wildcard matching.
- Denglisch: reverse-engineered 100-word English anchor list
  chosen to reproduce his declared Papaplatte-first ranking.
- TTR, word length, token count: pure math.
- Runs offline on a laptop. Zero API cost.

### 6b. Script (internal only)

- Deterministic.
- Extended keyword lists (roughly 15 keywords per category).
- No stemming; "Millionen" and "Million" are counted separately.
- Same math for TTR, word length, token count.
- Runs offline on a laptop. Zero API cost.

### 6c. AI agents

- Three parallel Claude Haiku 4.5 agents (one per creator).
- Each agent receives the metric spec as a prompt and the full
  transcript corpus for its assigned creator, then computes and
  returns the 8 metrics as JSON.
- No shared state between agents; they cannot collude.
- Runtime: about 6 minutes total.
- API cost: $0.24 via the local Claude CLI.

The AI is deliberately given the same spec as the deterministic
methods, not a looser prompt. The goal is to measure how closely a
reasoning model reproduces IT-Mario's declared winners on
identical inputs.

### 6d. Hybrid

- Deterministic.
- Extended keyword lists, plus simple suffix-stripping stemming
  ("Millionen" -> "million" matches "million", "Millionen", etc.).
- Denglisch uses a 234k-word English dictionary (full lexicon,
  not an anchor list).
- Same math for TTR, word length, token count.
- Our best-of-breed internal reference. Secondary diagnostic,
  not a truth claim.
- Runs offline. Zero API cost.

---

## 7. Strict scoring convention

Grading each method against IT-Mario's declared winners uses three
cell values:

| Cell value | Meaning                                                              |
|-----------:|----------------------------------------------------------------------|
| `1.0`      | Hit. The method's winner equals IT-Mario's single declared winner.   |
| `0.5`      | Tie-match. Applies only on declared-tie metrics (hype_adjectives).   |
| `0.0`      | Miss.                                                                |

The only declared-tie metric is `hype_adjectives`
(`{papaplatte, apored}`). A method scores tie-match (0.5) on it
under either of these conditions:

- Method outputs a creator inside the tie set (e.g. `"papaplatte"`
  or `"apored"`).
- Method outputs the literal string `"tie"`.

Anything else on hype_adjectives (e.g. `"maithinkx"`) is a miss.

On a single-winner metric, outputting `"tie"` is a miss, not a
partial credit. The AI agents did this on `drama_conflict`
(declared winner Apored, AI output "tie"); that cost AI one of its
misses.

Row totals count only full hits, not partial credit. So a
6/7 row total with a tie-match on hype adds up to 6 hits + 1
tie-match + 0 misses = 7 metrics accounted for.

This convention is applied consistently across
`bench/method_compare.py`, `bench/export_video_charts.py`, and
every chart JSON in `video_charts/`.

---

## 8. Results

### 8a. Primary reference layer — agreement with IT-Mario

Each row: how many of IT-Mario's 7 declared creator winners the
method reproduces on the same corpus.

| Method           | Hits | Tie-matches | Misses | % hits |
|------------------|-----:|------------:|-------:|-------:|
| IT-Mario replica | 6    | 1           | 0      | 85.7%  |
| Script           | 6    | 1           | 0      | 85.7%  |
| AI agents        | 4    | 1           | 2      | 57.1%  |
| Hybrid           | 6    | 1           | 0      | 85.7%  |

Cell-level breakdown of AI's two misses:

- `drama_conflict`: declared Apored; AI output `"tie"` (miss; tie
  is not valid on a single-winner metric).
- `egocentrism`: declared Papaplatte; AI output `"apored"` (miss).

AI's tie-match on `hype_adjectives`: declared tie
(`{papaplatte, apored}`); AI output the literal string `"tie"`
(tie-match, 0.5).

The three deterministic methods (replica, script, hybrid) all
match the same 6 metrics and all score tie-match on hype. Method
choice does not flip winners on 6 of the 7 creator metrics; AI
makes the only divergence.

Source: `results/methods_n50_clean.json`,
key `agreement_with_it_mario`.

### 8b. Community metrics

Four of six community winners reproduce cleanly. The two that
don't (`support`, `slang`) flip on denominator choice:

| Metric           | IT-Mario winner | Our winner (per 1k tokens) | Match? |
|------------------|-----------------|----------------------------|:------:|
| `support`        | Papaplatte      | MaiThinkX                  | no     |
| `questions`      | MaiThinkX       | MaiThinkX                  | yes    |
| `comment_length` | MaiThinkX       | MaiThinkX                  | yes    |
| `caps_rate`      | MaiThinkX       | MaiThinkX                  | yes    |
| `criticism`      | Apored          | Apored                     | yes    |
| `slang`          | Papaplatte      | Papaplatte per 1k only     | no     |

Papaplatte's average comment length is 62 characters vs
MaiThinkX's 201. When the denominator switches from per-comment
(IT-Mario's method) to per-1000-tokens (ours), two winners flip.
This is a denominator artifact, not a method bug.

Source: `results/community_metrics.json`.

### 8c. Overall headline

Adding up both layers:

- Creator metrics: 6 of 7 hit by best-fit deterministic method.
- Community metrics: 4 of 6 match.
- Total: **10 of 13 = 77 % agreement**.

Source: `video_charts/05_bottom_line_summary.json`.

### 8d. Secondary diagnostic — internal consistency vs hybrid

How often each method's ranking matches the hybrid's ranking on
the same corpus. Hybrid is NOT ground truth; this layer is for
spotting outlier methods, not for claiming correctness.

| Method           | Matches hybrid ranking (of 7) |
|------------------|-------------------------------|
| IT-Mario replica | 7 / 7                         |
| Script           | 7 / 7                         |
| AI agents        | 4 / 7                         |

The three deterministic methods are unanimous with each other on
every creator ranking. AI diverges on drama, hype, and ego.

Source: `results/methods_n50_clean.json`,
key `internal_consistency_hybrid_vs_others`.

---

## 9. Censorship-density finding

Originally planned as a Whisper-vs-auto-captions profanity-delta
test on 3 Papaplatte videos. OpenRouter (the LLM gateway used in
this project) does not host audio-to-text models, so T07 pivoted
to a deterministic `[__]` censor-density count across the full
150-video corpus. The pivot covers 50 times more data than the
original plan.

Counts of `[__]` markers in YouTube auto-captions across 50 videos
per creator:

| Creator     | `[__]` markers | Videos with >=1 censor |
|-------------|---------------:|-----------------------:|
| Papaplatte  | 515            | 48 / 50                |
| Apored      | 4              | 2 / 50                 |
| MaiThinkX   | 0              | 0 / 50                 |

Ratio: **Papaplatte is censored 38.64 times more often than Apored
on the same platform** (and infinitely more often than MaiThinkX,
who serves as the anti-control).

Follow-up Claude categorization on the top 30 most-censored videos
(10 per creator, up to 20 sentences each):

- 124 sentences classified as profanity.
- 5 as insult.
- 0 as slur.
- 29 as unknown.

Example sentence with a censored token:
`"meine Mutter ist eine [__]"` (Claude's guessed word: "Hure",
tagged as insult). Other guessed words: "Fick", "verarschen",
"fuck".

Top single video: a Papaplatte gameshow video with 30 censors.

**Verdict on Papaplatte's self-quote that YouTube "drops my words
by 50%": directionally supported.** The 38-fold gap vs Apored on
the same platform with the same pipeline is unambiguous. The
absolute drop-rate would require a gold audio transcript we do not
have.

Cost of the analysis: $0.0276 via Claude on OpenRouter.
Sources: `results/profanity_delta.json`,
`video_charts/03_censorship_density.json`,
`bench/censorship_analysis.py`.

---

## 10. Code architecture

### Source modules

```
src/
  common/
    metrics_spec.py      # 8-metric definitions (single source of truth)
    fetch.py             # yt-dlp scraper with CREATORS dict
    speaker_filter.py    # text-only speaker filter (V2.5 no-op for N=50)
  script_version/
    analyze.py           # deterministic pipeline (script version)
  ai_version/
    analyze.py           # AI-agent pipeline (single-creator entry)
```

### Benchmark / pipeline scripts

```
bench/
  method_compare.py          # 4-method N=50 comparison (canonical)
  ai_rerun_n50.py            # parallel 3-agent run on N=50
  community_compare.py       # 6 community metrics on comment corpus
  livestream_filter.py       # duration + title heuristic for VODs
  censorship_analysis.py     # [__] density + Claude categorization
  fetch_comments.py          # YouTube comment scraper
  fetch_n50_rest.py          # top-up from N=25 to N=50
  export_video_charts.py     # chart-JSON exports for video production
  visualize.py               # charts 1-5
  visualize_methods.py       # charts 6-8
  compare.py                 # legacy V2 4-condition benchmark (N=25)
```

### Canonical results

```
results/
  methods_n50_clean.json     # 4-method comparison (canonical)
  it_mario_replica.json      # standalone replica output
  community_metrics.json     # 6 community metrics
  profanity_delta.json       # censorship-density output
  holdout_n10.json           # N=10 stability check
  ai_metrics_n50/            # 3 JSONs from the AI-agent run
  livestream_filter_log.json # 0 excluded (heuristic no-op on N=50)
```

### Chart JSONs for video production

```
video_charts/
  01_three_method_accuracy_matrix.json   # 3x7 heatmap
  02_three_method_winners.json           # grouped bars, value for winning creator
  03_censorship_density.json             # 3-bar density race
  04_community_metrics.json              # 6x3 grouped bars
  05_bottom_line_summary.json            # 10/13 headline card
```

### Docs

```
docs/
  SPECIFICATION.md     # this file
  CURRENT_STATE.md     # one-page authoritative snapshot
  PROJECT.md           # mission, audience, deliverables, risks
  TASKS.md             # T01-T26 task spec with acceptance criteria
  IT-MARIO-VIDEO.md    # source-video breakdown, declared winners
  FINDINGS.md          # V2.5 findings report
  video-script.md      # 8-scene video beats
  shorts-script.md     # 3 Shorts briefs
```

---

## 11. How the agreement number is computed (end-to-end)

```
1. Fetch transcripts via yt-dlp.
2. Clean captions (strip timestamps, deduplicate).
3. Split into token streams per creator.
4. For each method, for each creator, compute the 8 metrics.
5. Rank creators per metric.
6. Declare the method's winner per metric.
7. Compare to IT-Mario's declared winner per metric.
8. Count hits, tie-matches, misses under the strict convention.
9. Write methods_n50_clean.json with both reference layers.
10. Export video-facing chart JSONs from step 9.
```

The only step that involves an external model is step 4 for the AI
method. Steps 1 through 3 and 5 through 10 are pure Python.

---

## 12. Known limitations

From IT-Mario's pipeline (inherited, not claimed as fixed by us):

1. Keyword lists are subjective. IT-Mario said so on camera:
   "steht und fällt mit der Liste".
2. 150 videos plus 18,146 comments is a convenience sample, not a
   random population.
3. YouTube auto-captions censor profanity with `[__]` tokens.
   This hurts Papaplatte's word counts specifically. Section 9
   quantifies the effect.
4. Auto-caption tokenization breaks slang compounds
   ("Burgies sneaken" becomes two tokens).
5. Channel-selection bias: only Papaplatte's Gaming channel was
   sampled. His other five channels have different vocabulary
   distributions.

From our V2.5 implementation (known blind spots):

6. The speaker filter is text-only. It cannot separate short
   interjections from a guest or a movie clip without true audio
   diarization. Deferred to V3 (pyannote).
7. Papaplatte's N=50 corpus still contains co-host dialogue inside
   his own videos. Reaction-clip audio could not be reliably
   separated without speaker labels.
8. The denglisch dictionary is English-dominant. Words like "Bro"
   that are equally German and English slang get counted as
   English.
9. Ground truth is IT-Mario's on-screen winners, not his raw
   data. He did not publish the 150-video list he used.
10. Hybrid's simple suffix stripping is not real lemmatization.
    Over-matches occasionally. Deferred to V3.
11. Censorship verdict is directional, not exact. The 38-fold
    ratio is unambiguous; Papaplatte's "50% of words missing"
    self-quote would need a gold audio transcript to confirm
    numerically.
12. About 19% of `[__]` markers are not clearly profanity (29 of
    the 158 classified sentences were "unknown"). Could be
    truncated proper nouns, product names, or caption artifacts.

---

## 13. Compute budget

Cap: $5.00. Actual spend: $0.27.

| Task                                                   | Projected | Actual  |
|--------------------------------------------------------|----------:|--------:|
| T08 AI re-run on N=50 (3 parallel agents)              | $0.56     | $0.24   |
| T07 Censorship-density pivot (Claude via OpenRouter)   | $0.30     | $0.03   |
| T05 AI sentiment (cut; used keyword rates instead)     | $1.00     | $0.00   |
| Deterministic methods (replica, script, hybrid)        | $0.00     | $0.00   |
| Headroom remaining                                     | $3.14     | $4.73   |

Keys required to reproduce:

- `ANTHROPIC_API_KEY` for the AI-agent pass.
- `OPENROUTER_API_KEY` for the censorship-density analysis.

All other steps run locally and for free.

---

## 14. What this project claims, and what it does not

| Claim                                                                     | Do we make it? |
|---------------------------------------------------------------------------|:--------------:|
| Our rebuild reproduces 6 of 7 of IT-Mario's declared creator winners      | yes            |
| The three deterministic methods agree on every creator ranking            | yes            |
| AI reproduces 4 of 7 creator winners plus a tie-match on hype             | yes            |
| YouTube auto-captions censor Papaplatte 38x more than Apored              | yes            |
| Papaplatte's "50% of words dropped" self-quote is directionally true      | yes            |
| Any single method is objectively correct                                  | no             |
| Our hybrid method is ground truth                                         | no             |
| IT-Mario's declared winners are factually correct                         | no             |
| We can quantify Papaplatte's absolute profanity-drop rate                 | no             |
| Keyword metrics measure personality, intelligence, or intent              | no             |

---

## 15. Questions a reviewer should ask

If you are analyzing this project, useful interrogation prompts:

1. Are any of the accuracy numbers circular? Specifically, does
   the hybrid method ever get scored against itself as ground
   truth?
2. On the one metric where AI diverges (egocentrism), which
   seed-word set is right? Is `ich, mein, meine, mich, mir` a
   fair measure of "egocentrism" at all?
3. How robust is the 38-fold censorship ratio to the definition
   of a `[__]` marker? (The source captions encode it as
   `[&nbsp;__&nbsp;]` with HTML entities; the parser handles both
   forms.)
4. Could denominator choice flip other community metrics too, not
   just support and slang?
5. Does the N=10 held-out set (5/7 winner stability) suggest any
   of the N=50 winners are noise?
6. What happens to the 4/7 AI number if you swap Haiku 4.5 for a
   larger model? (Not tested in this sprint.)
7. Which of the 12 known limitations is most likely to change the
   headline number if fixed?

---

## 16. One-line summary

A replication project that grades three rebuilds of a published
YouTube-analysis pipeline against the creator's own stated
results on the same 150-video corpus, and finds that 10 of 13
declared winners survive the reproduction, with one striking
side-finding about platform-level censorship of one creator
relative to the others.
