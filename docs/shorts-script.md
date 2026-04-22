# Shorts scripts — Lattensepp / IT-Mario sprint

Three Shorts, 45-60 seconds each, staggered across launch week.
German audio. Vertical format. Each Short closes with a one-line
CTA back to the main video.

Launch cadence:

- Short #1: main-video day, +2 hours (method reveal)
- Short #2: day +2 (YouTube censorship density — 38× ratio)
- Short #3: day +4 (community reveal, denominator punchline)

---

## Short #1 — "Drei Wege, einen Data Scientist zu rekonstruieren"

**Duration:** 55 sec.

**Launch:** main-video day, +2 hours.

**Hook line (0:00-0:02):** *"Ein Data Scientist hat seine komplette
Pipeline offengelegt. Wir haben sie dreimal nachgebaut."*

**Beats:**

| Time | Beat | Visual |
|---|---|---|
| 0:02-0:10 | Mario clip (<=5 sec) + his pipeline in 3 icons: scrape → count → winner. | IT-Mario face + animated icons |
| 0:10-0:25 | Three methods flash in sequence, 5 sec each. "Sein Code" → terminal. "AI Agents" → three parallel agent windows. "Unser Hybrid" → VS Code with the 234k Englisch-Wörterbuch. | Split-screen 1/3, 2/3, 3/3 sweeps |
| 0:25-0:40 | 4x7 accuracy matrix zooms in. Big numbers drop: "Replica 6/7. AI 4/7. Hybrid 6/7." Plus shared tie-match on hype. Highlight that AI's output text literally says "tie" — same phrasing as Mario on camera. | Matrix from chart 01 + motion numbers |
| 0:40-0:50 | Punchline overlay: *"Methode entscheidet nicht über den Sieger."* | Full-screen text card |
| 0:50-0:55 | CTA card back to main video. | Channel logo + arrow |

**Visual reference:**
`video_charts/01_three_method_accuracy_matrix.json` for matrix,
`video_charts/02_three_method_winners.json` for winner rows.

**CTA (German):** *"Full Analyse — 10 Minuten, alle Details —
verlinkt oben."*

---

## Short #2 — "YouTube zensiert Papaplatte"

**Duration:** 50 sec.

**Launch:** day +2.

**Hook line (0:00-0:02):** *"'Beleidigungen fehlen, droppt meine
Wörter um 50%.' — Papaplatte, selbst gesagt."*

**Beats:**

| Time | Beat | Visual |
|---|---|---|
| 0:02-0:08 | Papaplatte clip (<=5 sec) with the self-quote. Subtitle burn-in. | Papaplatte face-cam + chyron |
| 0:08-0:22 | Three-bar count animation. "Papaplatte: 515" climbs, "Apored: 4" barely moves, "MaiThinkX: 0" stays flat. Label: *"Zensierte Stellen über 50 Videos pro Creator"*. | Animated bar race with [__] icons |
| 0:22-0:35 | Big number drop: **"38×"** — sub-line: *"so viel häufiger hat YouTube Papaplatte zensiert als Apored."* | Full-screen number card |
| 0:35-0:45 | Example sentence pops in: *"'meine Mutter ist eine [__]'"* with arrow to guess *"Hure"*. Framing line: *"IT-Mario hat Auto-Captions benutzt. Papaplatte's eigenes Wortfeld verschwindet rechnerisch."* | Sentence card + motion type |
| 0:45-0:50 | CTA card. | Channel logo |

**Visual reference:**
`video_charts/03_censorship_density.json`. Primary number is the
38× ratio; secondary is the 48-out-of-50 Papaplatte videos with at
least one `[__]` marker. MaiThinkX's zero is the anti-control — same
platform, different content, zero censorship.

**Methodology note (for pinned-comment readers):** The original plan
was Whisper transcription on 3 Papaplatte videos. Our LLM gateway
(OpenRouter) does not host Whisper, so we pivoted to a direct
`[__]`-density comparison across the full 150-video corpus. The
pivoted method hits 50× more data than the original spec.

**CTA (German):** *"Warum das Mario's Zahlen verzerrt — im Main
Video. Link oben."*

---

## Short #3 — "Sechs Community-Metriken. Vier matchen. Zwei nicht."

**Duration:** 55 sec.

**Launch:** day +4.

**Hook line (0:00-0:02):** *"Sechs Community-Metriken, 15.000
Kommentare. Vier matchen Mario. Zwei nicht."*

**Beats:**

| Time | Beat | Visual |
|---|---|---|
| 0:02-0:12 | Six bar-chart groups flash in order: Support → Fragen → Länge → Caps → Kritik → Slang. Checkmarks auf vier. Amber-Icons auf Support und Slang. | Animated six-up bar chart |
| 0:12-0:25 | Zoom in on Support. Show his result (MaiThinkX) next to ours (Papaplatte). Same keyword list. Different winner. | Split-screen two bar charts |
| 0:25-0:38 | Reveal: *"Er zählt Keyword-Treffer pro Kommentar. Wir zählen pro 1000 Tokens. Bei kurzen Kommentaren kippt's — und Papaplatte hat die kürzesten."* | Two denominators, side-by-side math |
| 0:38-0:48 | Punchline card: *"4 von 6 passen. Die zwei Misses sind Nenner-Wahl, kein Methoden-Bug."* | Full-screen type overlay |
| 0:48-0:55 | CTA card. | Channel logo |

**Visual reference:** `video_charts/04_community_metrics.json`.
Key numbers to show: 4/6 match rate; Papaplatte comment length 62
chars vs MaiThinkX 201 chars (explains why per-comment vs
per-token denominators diverge).

**CTA (German):** *"Der ganze Nerd-Talk zur Nenner-Wahl — Main
Video, Link oben."*

---

## Production notes

**Format:** 9:16 vertical. Face-cam reserved for hook (first 2-3
sec) and close-out in Short #1 and #3. Short #2 stays chart/B-roll
dominant; open with the Papaplatte clip, close with a type card.

**Captions:** burn in German subtitles for the hook and for every
quote. Shorts run with sound off half the time — subtitles are
not optional.

**Length discipline:** if any Short runs over 60, cut the transition
beat (not the punchline). Punchline card stays on screen for at
least 2 seconds in all three.

**Placeholders in use:** none. All three Shorts reference resolved
chart data. T07 pivot resolved the original `{{WHISPER_DELTA}}`
placeholder into the "38×" headline number.

**CTA consistency:** all three Shorts close with a one-line link-
upward phrase. Do not over-engineer the CTA — the point is "Haupt-
video, Link oben", not a pitch.
