# IT-Mario's Original Video — Breakdown

Source: the analytical pipeline IT-Mario described in his own words,
extracted from his video transcript. Used as the specification that
our V2.5 replicates.

---

## Video metadata

- URL: https://youtu.be/6pLp8Uv6VA
- Creator: IT-Mario (self-identifies as Data Scientist)
- Subjects analyzed: Apored, Papaplatte, MaiThinkX
- Corpus claimed: 150 videos (50 per creator) plus 15,000 comments
- Transcript on disk: data/original__6pLp8Uv6VA.de.txt

## Reaction video metadata

- URL: https://youtu.be/w81qGuiQNEE
- Title: "Ich wurde wissenschaftlich auseinandergenommen…"
- Host: Papaplatte, reacting on the Lattensepp channel to IT-Mario's
  analysis of him
- Transcript on disk: data/Ich wurde wissenschaftlich
  auseinandergenommen… [w81qGuiQNEE].de.txt

---

## IT-Mario's research question

"Aped, Papa Platte und My Think. Wer hat den größten Wortschatz?"

Translation: Who has the biggest vocabulary: Apored, Papaplatte, or
MaiThinkX? Expanded during the video to 7 video metrics and 6
community metrics.

---

## Pipeline as described by IT-Mario

### Step 1. Scope decision

- 150 videos (50 per creator) plus 15,000 comments
- Time estimate if done manually: roughly 50 hours per creator
- Decision: automate everything

### Step 2. Transcription attempt 1 (abandoned)

- Approach: download MP3 via script, transcribe with a local AI model
- Problem A: YouTube detects scripts as bots
  - Workaround: VPN plus stored authenticated cookies in the script
- Problem B: local AI model too compute-heavy for a cheap laptop
- Outcome: abandoned this path

### Step 3. Transcription attempt 2 (used)

- Approach: download YouTube auto-generated captions via script
- Raw file contains timestamps and duplications
- Clean with a second script to recover raw spoken text
- Outcome: spoken-text corpus for all 150 videos

### Step 4. Reading the text (rejected as option)

- Considered manually reading 150 transcripts
- Decision: "keine Lust drauf", so automate analysis too

### Step 5. Vocabulary metric — first attempt

- Logic: count unique words across all of a creator's videos
- Worked example: "blablablabla" repeated 4 times in a 10-word
  sentence yields 7 unique words
- Result on raw counts: Papaplatte leads
- Insight: this result is biased by total spoken-word volume

### Step 6. Vocabulary metric — corrected (TTR)

- Logic: unique words divided by total words (type-token ratio)
- Result: MaiThinkX has the biggest relative vocabulary
- His comment: "hat mich nicht überrascht" (not surprising)

### Step 7. Wealth and drama metrics

- Build one keyword list for each concept
- Wealth examples he read out loud: Geld, Cash, kaufen, Penthous,
  Premium
- Drama examples he read out loud: Hater, Neid, blockiert,
  ehrenlos, Gerücht
- Count keyword hits per 1,000 tokens
- Disclaimer he stated: "keinen wissenschaftlichen Anspruch, steht
  und fällt mit der Liste"
- Results: Apored wins wealth, Apored wins drama
- His comment on Apored wealth: "wundert mich nicht, er ist ja
  wirklich ein Multimillionär"

### Step 8. Hype-adjectives metric

- Keywords: krass, heftig, brutal, übelst
- Result: Papaplatte and Apored tied ("gleich häufig")

### Step 9. Egocentrism metric

- Keywords: ich, mein, meine, mich, mir
- Result: Papaplatte wins, Apored close second

### Step 10. Denglisch metric

- Exact method not described in the transcript
- Result: Papaplatte wins
- His comment: not surprised due to gaming clips

### Step 11. Word length metric

- Result: MaiThinkX has the longest mean word length
- His caveat: "die Differenz ist nur sehr klein, deswegen ist das
  wenig aussagekräftig"

### Step 12. Community analysis on 15,000 comments

Same keyword-group logic, applied to the comment corpus.

Six community metrics and declared winners:

- Support / praise (Supportfaktor und Lob): MaiThinkX
- Questions asked: MaiThinkX
- Comment length (longest comments): MaiThinkX
- Caps usage (least caps): MaiThinkX
- Criticism: Apored's community
- Slang words: Apored's community

### Step 13. Closing synthesis

- Quote: "Die Ergebnisse sind ehrlicherweise nicht besonders
  spektakulär"
- Real purpose he stated: demo of data collection, cleaning, and
  analysis methodology
- Application he cited: in industry, the same pipeline runs across
  300 YouTubers to find product-placement partners
- Example application he gave: MaiThinkX's community has high
  question rate plus high support plus supportive tone, which
  suggests book-placement potential

---

## Metrics summary (winners he declared)

| Metric | IT-Mario winner |
|---|---|
| Vocabulary (TTR) | MaiThinkX |
| Wealth keywords | Apored |
| Drama keywords | Apored |
| Hype adjectives | Tie (Papaplatte and Apored) |
| Egocentrism | Papaplatte |
| Denglisch | Papaplatte |
| Word length | MaiThinkX (small difference) |
| Community support | MaiThinkX |
| Community questions | MaiThinkX |
| Comment length | MaiThinkX |
| Community caps (least) | MaiThinkX |
| Community criticism | Apored |
| Community slang | Apored |

Totals: 6 of 7 creator-video metrics with a clear winner (one tie),
and 6 of 6 community metrics.

---

## Limitations IT-Mario himself acknowledged

- Keyword lists are subjective: "steht und fällt mit der Liste"
- Total sample is 150 videos plus 15,000 comments, not a random
  population
- Results are not particularly spectacular; the point is the
  methodology

## Limitations IT-Mario did NOT acknowledge

These are the gaps our V2.5 replication targets.

- YouTube auto-captions censor profanity. Papaplatte pointed this
  out directly: "Beleidigungen fehlen, droppt meine Wörter um 50%".
  This affects Papaplatte's word counts specifically.
- Tokenization treats "Burgies sneaken" as two separate tokens even
  when the spoken content is a single slang phrase (a Papaplatte
  critique in his reaction).
- Channel selection bias for Papaplatte: only his Gaming channel was
  sampled. He has Podcast, Uncut, Main, Reaction, and Clips
  channels, each with different vocabulary distributions.
  Papaplatte's quote: "hätte den Podcast genommen, wäre ein insaner
  Buff".
- Livestream VODs may be mixed with regular uploads; pacing and
  vocabulary distribution differ.
- No confidence intervals or statistical significance testing; every
  metric is reported as a point estimate.
- "Wins" are not operationally defined; no margin or tie threshold
  stated in advance.

---

## Papaplatte's reaction — critique points and validity

| Papaplatte critique | Valid? | Source evidence |
|---|---|---|
| "Tiny sample, 1-2 videos is random" | Misreading. IT-Mario used 50 | Transcript: "150 Videos analysieren" |
| "Confirmation bias — wollte Mailab gewinnen lassen" | Plausible but unprovable | Reaction tone |
| "Nur Gaming, nicht Podcast Channel" | Valid (channel selection) | Multiple channels confirmed |
| "Rohdaten nicht so geil" | Valid (auto-captions censor and misspell) | T07 (pivoted) measured 38× Papaplatte vs Apored `[__]` censor density |
| "Tokenization broken (Burgies sneaken)" | Valid | Auto-caption artifacts visible in corpus |

---

## Mapping limitations to V2.5 tasks

| Limitation or critique | Addressed by |
|---|---|
| Livestream mixing | T02 (livestream VOD filter) |
| Missing community analysis | T03, T04, T05 (comments + 6 metrics) |
| Denglisch method unknown | T06 (reverse-engineer from his numbers) |
| Profanity censorship | T07 pivoted to `[__]` density across 150 videos; see results/profanity_delta.json |
| Sample-size misread | T01 (FINDINGS.md fix) plus Scene 1 hook |
| No confidence intervals | Explicitly out of scope; future V3 |
| Channel selection bias | Kept Gaming only to match him; V3 teaser |
