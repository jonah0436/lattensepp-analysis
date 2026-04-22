# Video script — "Wir haben IT-Mario wissenschaftlich auseinandergenommen"

Target runtime: ~9:30. Eight scenes, scene beats only (Jonah
improvises face-cam). German narration, English for code and chart
labels. Audience: German YouTube, Papaplatte-adjacent demographic.
Nerdy-but-accessible; explain TTR, keyword rates, and corpus
in-line the first time they appear.

---

## Scene 1 — Hook (0:00-0:30)

**Duration:** 30 sec.

**On-screen:**

- 0:00-0:08: IT-Mario clip (<=10 sec, the moment he says "Aped,
  Papa Platte und My Think — wer hat den größten Wortschatz?").
- 0:08-0:18: hard cut to face-cam, no B-roll. Jonah delivers hook.
- 0:18-0:30: title card motion graphic. Three columns slide in:
  "SEIN CODE / AI AGENTS / UNSER HYBRID". Title underneath:
  *"Wir haben IT-Mario wissenschaftlich auseinandergenommen"*.

**Message intent:** A data scientist published his entire YouTube
analysis pipeline. We rebuilt it three separate ways on the same
corpus. Viewer leaves with: "three methods, one comparison, we'll
show who was right."

**German key phrases:**

- Hook line: *"Ein Data Scientist hat seine komplette Pipeline
  offengelegt. Wir haben sie dreimal nachgebaut — einmal mit seinem
  Code, einmal mit AI, einmal mit einem besseren Ansatz. Hier ist
  was rausgekommen ist."*
- Transition out: *"Und ja, am Ende gibt's auch noch ein kleines
  Geständnis."* (teases the Scene 7 meta reveal).

**English notes:** title card reads English on the three columns
(HIS SCRIPT / AI AGENTS / OUR HYBRID) if Jonah prefers the DACH dev
convention; fallback is German. Pick one and stick with it for the
whole video.

---

## Scene 2 — What Mario did (0:30-2:00)

**Duration:** 90 sec.

**On-screen:**

- Animated 13-step pipeline flowchart. Steps come in one at a time
  with a soft pop. Each step: icon + one-line label. Play at roughly
  6-7 seconds per step, compress steps 2-4 into a combined "scraping
  was painful" beat.
- Ghosted face-cam lower-right for commentary layer.
- Highlight callouts: Step 6 (TTR), Step 12 (15k comments).

**Message intent:** Viewer understands Mario's pipeline as a story.
Scrape captions → clean text → count stuff per keyword list →
normalize by total words → declare a winner. Frame the keyword-list
bias honestly; Mario himself said *"steht und fällt mit der Liste"*.

**German key phrases:**

- Opener: *"Das ist Mario. Data Scientist, sagt er selbst. Und das
  hier ist seine Pipeline."*
- TTR explainer beat: *"TTR — Type Token Ratio. Klingt kompliziert,
  ist aber nur: wie viele verschiedene Wörter pro gesprochenem
  Wort. Quasi die Vokabular-Dichte."*
- Keyword-rate explainer: *"Pro 1000 Wörter zählen wir, wie oft
  bestimmte Begriffe fallen. Das ist eine Rate, keine absolute
  Zahl — sonst gewinnt immer der, der am meisten labert."*
- Closing beat: *"Sieben Metriken auf 150 Videos. Plus nochmal sechs
  Metriken auf 15.000 Kommentaren. Saubere Arbeit — wenn man ihm
  das glaubt."*

**English notes:** chart labels for the flowchart nodes in English
(`scrape → clean → tokenize → TTR → keyword rates → winner`) so
they stay readable if the video ever gets subtitled.

**Chart source:** none; pure animation.

---

## Scene 3 — Our 3 reimplementations (2:00-3:30)

**Duration:** 90 sec.

**On-screen:**

- Split screen into three columns. Each column gets ~25 sec on
  screen in sequence, then all three appear side-by-side for the
  last 15 sec.
- Column 1: "IT-Mario Replica" — terminal window, his exact 5-6
  word seed lists visible (`Geld, Cash, kaufen, Penthous, Premium`
  for wealth). Small IT-Mario face in the header.
- Column 2: "AI Agents" — three parallel Claude agent windows, each
  labeled with a creator (Papaplatte / Apored / MaiThinkX). Show
  live progress bars spinning.
- Column 3: "Our Hybrid" — VS Code, `src/script_version/analyze.py`
  visible. Highlight the 100-word denglisch anchor list and the
  deterministic TTR math.
- Final combo shot: three-column scoreboard at bottom of frame,
  still empty (seeds Scene 4).

**Message intent:** Viewer understands each method is a distinct
tool: replica for "did his exact thing work", AI for "does a
language model see the same things", hybrid for "deterministic
improvements without losing reproducibility". Corpus is the same
for all three — 50 videos per creator, 150 total, livestream VODs
filtered out.

**German key phrases:**

- Opener: *"Drei Methoden, ein Korpus. 150 Videos, 50 pro Creator.
  Livestreams raus, weil die Wortverteilung komplett anders ist."*
- Corpus explainer (first mention of word): *"Korpus — das ist
  einfach der Textberg, auf dem wir rechnen. Bei uns: alle
  gesprochenen Wörter aus den 150 Videos zusammen."*
- Method 1 line: *"Methode eins: sein exakter Code. Gleiche
  Keyword-Listen, gleiche Rechnung."*
- Method 2 line: *"Methode zwei: drei AI-Agenten parallel. Pro
  Creator einer. Sie kriegen die Metrik-Definitionen als Prompt und
  rechnen selber."*
- Method 3 line: *"Methode drei: unser Hybrid. Längere Listen, 234k-
  Wörter Englisch-Wörterbuch für Denglisch, deterministisches TTR."*
- Closer: *"Drei Methoden. Gleiche Videos. Mal gucken, wer was
  sagt."*

**English notes:** code snippets visible on-screen stay in English
(Python). Agent labels in English (`Agent: Papaplatte`, etc.).

**Chart source:** no JSON chart yet; screenshot of repo code
blocks. Reference: `src/script_version/analyze.py`,
`results/ai_metrics/`.

---

## Scene 4 — Accuracy comparison (3:30-5:00)

**Duration:** 90 sec.

**On-screen:**

- 0:00-0:15: 4x7 method-metric matrix slides in. Rows: IT-Mario
  Replica, Script (shown as baseline only, muted color), AI, Hybrid.
  Columns: the 7 creator metrics. Green checkmark for a match with
  IT-Mario's declared winner, red X for a miss. Use `hype_adjectives`
  as tie-match where applicable.
- 0:15-0:45: face-cam overlay on corner while Jonah narrates the
  headline number.
- 0:45-1:15: per-creator bar chart pops up next to the matrix.
  Animated bars for the six quant metrics at scaled comparable
  ranges.
- 1:15-1:30: "WINNER HITS" big-number card. IT-Mario replica:
  6/7 + 1 tie-match. AI: 4/7 + 1 tie-match. Hybrid: 6/7 + 1 tie-
  match. Under the strict scoring, all three methods earn the
  same tie-match credit on `hype_adjectives` (declared tie).
  What differs is the output text: AI literally outputs "tie";
  the deterministic methods output "papaplatte" (which sits
  inside the declared tie set).

**Message intent:** All three methods are in the same ballpark.
None of the methods is secretly broken. The interesting result
is not "one method wins" — it's that AI's output text mirrors
Mario's on-camera phrasing ("tie") where the deterministic
methods commit to a single winner from the tie set. Mechanically,
everyone scores the tie-match the same way.

**German key phrases:**

- Matrix reveal: *"Sieben Metriken, drei Methoden. Grüner Haken
  heißt Treffer — gleiche Sieger wie Mario."*
- Headline: *"IT-Mario-Replica: sechs von sieben. AI: vier von
  sieben. Unser Hybrid: auch sechs von sieben. Plus jeweils ein
  Tie-Match bei Hype-Adjektiven — das zählt aber nicht als voller
  Treffer."*
- Nuance beat: *"Kleine Pointe: die AI hat als einzige wortwörtlich
  'Unentschieden' ausgegeben. Mario hat im Video auch 'gleich
  häufig' gesagt. Die deterministischen Methoden haben Papaplatte
  gewählt — das ist mathematisch noch im Tie-Set von Mario,
  zählt also als Tie-Match, aber im Text steht halt 'Papaplatte'.
  Alle vier bekommen das gleiche Tie-Match-Kredit; unterschiedlich
  ist nur, was da wortwörtlich rauskommt."*
- Transition: *"Also — Methoden funktionieren alle. Die
  spannende Frage ist: wo liegt Mario trotzdem daneben?"*

**English notes:** matrix labels in English for readability
(`vocabulary_ttr`, `wealth_flex`, `drama_conflict`,
`hype_adjectives`, `egocentrism`, `denglisch`, `avg_word_len`).
Optional German tooltips on hover in the B-roll version.

**Chart sources:**

- `video_charts/01_three_method_accuracy_matrix.json`
- `video_charts/02_three_method_winners.json`

---

## Scene 5 — Where his method misses (5:00-7:00)

**Duration:** 120 sec. Four sub-beats plus a 10-sec sidebar.

**On-screen:**

- Sub-beat A (5:00-5:30): YouTube censorship density. 3-bar chart
  showing `[__]` censor markers per 1k tokens across all 150 videos.
  Papaplatte 1.63 / Apored 0.04 / MaiThinkX 0.00. Big number **"38×"**
  — subtitle *"so viel häufiger wurde Papaplatte zensiert als Apored"*.
  Side panel shows a real example: *"meine Mutter ist eine [__]"* with
  Claude's likely-word guess *"Hure"*, tagged as insult.
- Sub-beat B (5:30-6:00): tokenization failure. Animated word
  "Burgies sneaken" gets split into two tokens by Mario's regex,
  then re-combined by a slang-aware tokenizer. Small label: *"dies
  ist ein Wort, keine zwei"*.
- Sub-beat C (6:00-6:20): livestream filter context. Clip durations
  histogram; tag the 3+ hour VODs Mario probably included. Overlay:
  *"Raus damit — unterschiedliche Pacing, unterschiedliches
  Vokabular"*.
- Sub-beat D (6:20-6:50): denglisch reverse-engineer. Show our
  100-word English anchor list scrolling, then the output: our
  hybrid reproduces Papaplatte's denglisch win.
- Sidebar (6:50-7:00): Papaplatte sample-size correction. Short
  10-sec cut. Face-cam + chyron: *"Papaplatte sagt 1-2 Videos.
  Mario hat 50 pro Creator genommen. Quelle: sein eigenes
  Transkript."* No more weight on this — the hook is the
  methodology, not the correction.

**Message intent:** Mario's method has four fixable blind spots.
Three of them hurt Papaplatte specifically (censored profanity,
fused slang tokens, livestream mixing). The fourth (denglisch)
was recoverable with a bigger dictionary. The sample-size
critique from Papaplatte doesn't hold up — that's the sidebar.

**German key phrases:**

- Sub-beat A: *"Punkt eins: YouTube-Auto-Captions zensieren
  Schimpfwörter. Papaplatte hat's selbst gesagt — 'Beleidigungen
  fehlen, droppt meine Wörter um 50%'. Wir haben alle 150 Transkripte
  durchgezählt: 515 zensierte Stellen bei Papaplatte in 48 von 50
  Videos, 4 bei Apored, 0 bei MaiThinkX."*
- *"Das heißt: YouTube zensiert Papaplatte 38-mal häufiger als Apored.
  Auf derselben Plattform, gleiche Creator-Größe. Die Kritik trifft
  zu — nur Mario's Skript merkt das nicht."*
- Sub-beat B: *"Punkt zwei: Tokenisierung. 'Burgies sneaken' ist
  ein Wort in seiner Welt. Mario's Regex macht daraus zwei. Rechnet
  anders."*
- Sub-beat C: *"Punkt drei: Livestream-VODs. Drei Stunden am Stück
  reden ist ein anderer Job als ein editiertes Video. Raus damit."*
- Sub-beat D: *"Punkt vier: Denglisch. Mario sagt nicht wie er's
  gerechnet hat. Wir haben's von seinen Zahlen her rekonstruiert —
  100-Wörter-Ankerliste — und kriegen Papaplatte als Sieger raus.
  Wie er auch."*
- Sidebar line: *"Kurze Einordnung: Papaplatte sagt in der Reaktion
  'tiny sample, 1-2 Videos ist random'. Im Transkript steht aber
  ganz klar 50 Videos pro Creator. Diese Kritik hält also nicht."*

**English notes:** Censorship chart in English y-axis label
(`[__] censor markers per 1k tokens`). Tokenization example uses
German slang, no translation needed; the humor is in seeing the split.

**Methodology note (for on-screen code readers):** Original T07 spec
called for Whisper transcription on 3 Papaplatte samples. OpenRouter
(our LLM gateway for this project) does not host Whisper or any
audio-to-text models, so we pivoted to `[__]` density across the
full N=150 corpus. The pivoted method covers 50× more data and
directly answers the same question. See `results/profanity_delta.json`
methodology field for detail.

**Chart sources:**

- Sub-beat A: `video_charts/03_censorship_density.json`
- Sub-beat C: livestream duration histogram (generate from
  `data/meta/*.json` if needed; otherwise a simple stat chyron)
- Sub-beat D: denglisch per-creator bars from
  `results/methods_n50_clean.json`

---

## Scene 6 — Community bonus (7:00-8:00)

**Duration:** 60 sec.

**On-screen:**

- 0:00-0:10: title card *"Bonus: 15.000 Kommentare"*.
- 0:10-0:40: animated six-up bar chart. One bar group per metric:
  support, questions, comment length, caps, criticism, slang. Each
  group pops in with a mini label. Match-with-Mario checkmarks on
  four metrics, amber icons on two (support, slang).
- 0:40-1:00: big-text reveal: *"4 von 6 passen. Die zwei Misses
  sind kein Methoden-Bug — die sind Nenner-Wahl."*

**Message intent:** We also replicated his community analysis. Four
of six community winners match Mario cleanly. The two that don't
(support, slang) are artifacts of which denominator you divide by,
not of the method itself. A typical viewer leaves with: "same game,
same caveats, but his community winners mostly hold."

**German key phrases:**

- Opener: *"Er hat auch 15.000 Kommentare analysiert. Das haben wir
  auch gemacht — sechs Metriken, gleicher Logik: Keyword-Liste
  durch Gesamt-Tokens."*
- Results line: *"Vier von sechs matchen glatt: Fragen, Kommentar-
  Länge, Caps, Kritik. Bei Support und Slang weichen wir ab."*
- Punchline: *"Aber — und das ist der Witz — das ist kein
  Methoden-Bug. Je nachdem, ob du pro Kommentar zählst oder pro
  Token, kippt der Sieger. Die Methode entscheidet nicht über den
  Sieger. Der Nenner entscheidet."*
- Closer: *"Tiefer dazu in Short Nummer drei. Link unten."*

**English notes:** chart labels stay in English for the six metrics
(`support`, `questions`, `comment_length`, `caps_rate`,
`criticism`, `slang`). The punchline "denominator entscheidet" is
the central phrase and gets its own motion-graphic moment.

**Chart source:** `video_charts/04_community_metrics.json`.

---

## Scene 7 — Meta reveal / AI Playbook (8:00-9:00)

**Duration:** 60 sec.

**On-screen:**

- 0:00-0:15: hard cut to face-cam, full frame, no overlay. Eye
  contact. Jonah delivers the reveal directly.
- 0:15-0:45: split screen — face-cam left, agent dispatch UI
  right. Show actual Claude parallel-agent logs: three workers
  spawning, running, finishing. Terminal scroll of real commits.
  Timestamps visible.
- 0:45-1:00: receipts card: *"Total Compute Spend: $0.27"*, with
  line items (AI agents run $0.24, censorship-density analysis
  via Claude/OpenRouter $0.03, comment classification skipped).
  GitHub repo URL underneath.

**Message intent:** The whole analysis you just watched was built
with Claude plus parallel agents. This is the first episode of the
"AI Playbook" series. Show receipts — actual dispatch logs, actual
cost — so the reveal doesn't read as "I asked ChatGPT" slop.

**German key phrases:**

- Reveal line: *"Kleines Geständnis: Diese komplette Analyse wurde
  mit Claude und parallelen Agenten gebaut. Kein Praktikant, kein
  Team. Ein Laptop, ein paar gut geprompte Agenten, 27 Cent
  Rechenzeit."*
- Receipts: *"Siebenundzwanzig Cent. Ernsthaft. Code ist open
  source, Link unten."*
- Series tease: *"Das hier ist Episode eins von 'AI Playbook' —
  Serie, in der wir echte Data-Science-Projekte komplett mit AI
  bauen und die Belege zeigen. Kein Hype, tatsächliche Logs."*

**English notes:** terminal window and agent dispatch UI stay in
their native English. Receipts card uses English headers
(`Compute spend`, `Cost`).

**Chart source:** none (real UI + logs). Cost number comes from
`video_charts/05_bottom_line_summary.json` field
`total_compute_cost_usd`.

---

## Scene 8 — CTA (9:00-9:30)

**Duration:** 30 sec.

**On-screen:**

- 0:00-0:10: channel branding lower-third, minimalist. Subscribe
  nudge as motion graphic.
- 0:10-0:20: GitHub link card. Repo URL large and centered.
- 0:20-0:30: next-episode tease. Silhouette placeholder for the
  next video concept, with a one-line hook.

**Message intent:** Viewer knows three things when they close the
tab: (1) there's a GitHub repo with the full code, (2) this is a
series, (3) Short #1 drops in two hours with the method reveal in
60 seconds.

**German key phrases:**

- Closer line 1: *"Code ist komplett public — Link in der
  Beschreibung."*
- Closer line 2: *"Abonnier den Kanal, wenn du Episode zwei sehen
  willst. Wir gehen als nächstes an ein V3 des Ganzen: echte
  Speaker-Diarisierung mit Whisper auf allen drei Creatorn."*
- Short tease: *"Und in zwei Stunden droppt der erste Short — 60
  Sekunden, drei Methoden, ein Ergebnis."*

**English notes:** GitHub URL stays English. Subscribe button
language depends on Jonah's channel default (assume German).

---

## Production notes

**Face-cam scenes:** 1 (hook), 4 (partial overlay during matrix
reveal), 5 (sidebar beat), 7 (full-frame reveal), 8 (CTA).

**Chart-only / B-roll scenes:** 2, 3, 6 play as animation + voice-
over. Scene 4 is chart-dominant with a small face-cam overlay in
the corner. Scene 5 alternates: sub-beat A, B, D are chart/animation
with voice-over; sidebar is a 10-sec face-cam insert.

**Chart sources (master list):**

- Scene 4: `video_charts/01_three_method_accuracy_matrix.json` +
  `video_charts/02_three_method_winners.json`
- Scene 5: `video_charts/03_censorship_density.json` plus denglisch
  bars derived from `results/methods_n50_clean.json`
- Scene 6: `video_charts/04_community_metrics.json`
- Scene 7: cost number from `video_charts/05_bottom_line_summary.json`

**Placeholder audit:** none. T07 pivoted from a Whisper 3-sample
delta to a deterministic `[__]` censor-density count across all 150
videos, so Scene 5 sub-beat A lands on the 38× ratio directly rather
than a placeholder number. See `results/profanity_delta.json` and
`video_charts/03_censorship_density.json`.

**TL;DR length check:**

| Scene | Target | Running total |
|---|---|---|
| 1 Hook | 0:30 | 0:30 |
| 2 Pipeline | 1:30 | 2:00 |
| 3 Reimplementations | 1:30 | 3:30 |
| 4 Accuracy matrix | 1:30 | 5:00 |
| 5 Misses + sidebar | 2:00 | 7:00 |
| 6 Community bonus | 1:00 | 8:00 |
| 7 Meta reveal | 1:00 | 9:00 |
| 8 CTA | 0:30 | 9:30 |

Total: 9:30. If Scene 5 sub-beat A needs trimming for any reason,
scene 5 lands at 1:50, total 9:20 — still inside the 6-10 min spec.

**Tone check:** Scenes 1, 7, 8 lean casual. Scenes 2, 4, 5, 6 lean
serious-on-findings. Scene 3 is the transition from casual-setup to
serious-execution. Do not let the sidebar in Scene 5 turn into a
Papaplatte-correction hook — hold the line, 10 seconds, move on.
