# Lattensepp / IT-Mario Replication — Project Outline

Version: 2.5 (public content sprint)
Last updated: 2026-04-22
Status: Active

---

## Mission

IT-Mario laid out his entire YouTube analysis pipeline on camera.
We rebuild it three ways on the same 150-video corpus — his exact
script, three parallel AI agents, and an improved hybrid — then
compare accuracy across methods. Ship a 6-10 minute German YouTube
video that walks through his method, our three reimplementations,
and where ours wins, with motion graphics making the results
readable for a normal viewer. Full code public on GitHub.

## Why this exists

Three stacked motivations:

1. Showcase a full data-science rebuild in public. IT-Mario outlined
   his whole pipeline on camera — an unusually clean spec to
   reproduce. Three independent reimplementations (his script, AI
   agents, our hybrid) make the comparison legible to a non-technical
   viewer.
2. Launch a new German YouTube channel positioned as a hybrid data/AI
   creator. First episode of the "AI Playbook" series.
3. Portfolio piece. End-to-end agent-powered data-science work in
   public, with a linked code repo.

Primary success: a clean, nerdy-but-accessible methodology showcase
that holds up for any normal viewer. Rebuild, compare, visualize.
Secondary: creators (Papaplatte, IT-Mario, adjacent German creators)
notice the video. Tertiary: raw views. The Papaplatte sample-size
correction that nerd-sniped this project becomes a sidebar in the
improvements scene, not the hook.

## Audience

German YouTube viewers, Papaplatte-adjacent demographic. German audio
narrative. English for code, chart labels, and technical terms (the
standard dev-YouTube pattern in the DACH region). Tone half casual,
half serious: casual hooks, serious on the findings.

## Channel identity

Positioning: hybrid data / AI creator. First episode of the "AI
Playbook" series format, where the video ends with a meta reveal
showing that the analysis was built with Claude plus agents.

Visual convention: clean minimalist data-viz thumbnails, single
headline number. Voice + screen default, face-cam for hook,
reactions, and the meta reveal.

## Deliverables

| Artifact | Status | Owner |
|---|---|---|
| 6-10 min main video | Planned | Jonah |
| 3 YouTube Shorts (45-60s each) | Planned | Jonah |
| Public GitHub repo | V2 ready, V2.5 pending | Claude |
| report.html dashboard with V2.5 sections | Pending | Claude |
| Scene-by-scene video beats doc | Pending | Claude |

Explicitly NOT in scope for this sprint:

- Companion blog post
- Public dashboard URL (report.html stays local)
- Full V3 pipeline (spaCy lemmatization, stratified multi-channel
  sampling, bootstrap confidence intervals)
- Multi-creator expansion beyond the original three

## Story arc

Video title: "Wir haben IT-Mario wissenschaftlich auseinandergenommen"
(meta-callback to Papaplatte's reaction video title).

Hook: "Ein Data Scientist hat seine komplette Pipeline offengelegt.
Wir haben sie dreimal nachgebaut — einmal mit seinem Code, einmal mit
AI, einmal mit einem besseren Ansatz. Hier ist was rausgekommen ist."

Eight scenes:

| # | Beat | Duration | On-screen |
|---|---|---|---|
| 1 | Hook | 0:00-0:30 | Mario clip ≤10s, 3-method teaser title card |
| 2 | What Mario did | 0:30-2:00 | Animated 13-step pipeline flowchart |
| 3 | Our 3 reimplementations | 2:00-3:30 | Side-by-side: his script / AI agents / our hybrid, with code snippets |
| 4 | Accuracy comparison | 3:30-5:00 | Method × metric matrix, per-creator bars, winner hits |
| 5 | Where his method misses | 5:00-7:00 | Censorship density (38× Papaplatte vs Apored, T07 pivot), tokenization (Burgies sneaken), livestream filter, denglisch reverse-engineer. Papaplatte sample-size correction as 10-sec sidebar. |
| 6 | Community bonus | 7:00-8:00 | 6 community metrics animated |
| 7 | Meta reveal (AI Playbook) | 8:00-9:00 | Face-cam + agent UI + terminal |
| 8 | CTA | 9:00-9:30 | Channel branding, GitHub link, next-episode tease |

## Method decisions (V2.5)

- 3 methods in the video narrative: (a) IT-Mario exact replica using
  his verbatim 5-6 word keyword lists, (b) AI — three parallel Claude
  agents computing metrics independently, (c) Hybrid — our improved
  version with extended lists, a 234k-word English denglisch
  dictionary, simple stemming, and deterministic math for TTR and
  word length. The deterministic "script version" from V2 stays as an
  internal baseline for the repo but does not appear in the video.
- Gaming channel only for Papaplatte (matches IT-Mario's choice).
  Multi-channel sample becomes a V3 teaser at video end.
- Filter out livestream VODs from the N=50 corpus, re-run numbers.
- Reverse-engineer IT-Mario's denglisch method from his declared
  numbers instead of marking it unknown.
- Add comment analysis: 6 community metrics on roughly 15,000
  comments (matches IT-Mario's full scope).
- Measure YouTube auto-caption profanity censorship by counting
  `[__]` marker density across all 150 videos. (Pivoted from a
  Whisper 3-sample diff because OpenRouter, the LLM gateway used
  here, does not host audio-to-text.)
- Add N=10 held-out validation set.

## Success criteria (ship gates)

- [x] All 4 V2.5 data components complete: comments, livestream
      filter, denglisch replica, censorship-density pivot (was
      Whisper profanity test)
- [ ] report.html updated with V2.5 sections, all charts synced
- [ ] Chart data exported as JSON for the video production pipeline
- [ ] Public GitHub repo with working code, README, and MIT license
- [ ] Video scene-by-scene beats doc complete
- [ ] Main video shipped on new channel
- [ ] 3 Shorts staggered over week 1 post-launch
- [ ] Reddit launch posts up within 24h of upload

## Timeline

2 weeks from kickoff.

| Week | Focus |
|---|---|
| 1 | Data and code work (Claude): comments, filters, Whisper, reruns, exports, repo cleanup, script beats |
| 2 | Video production (Jonah): animations, record, edit, thumbnail, Shorts cut, launch |

See docs/TASKS.md for the day-by-day task breakdown with acceptance
criteria.

## Budget

Cap: $5 total for compute and API spend.

Projected spend:

- AI re-run on N=50: about $0.56
- Censorship-density analysis (T07 pivot, was Whisper): about $0.03 actual
- Comment AI classification (if needed for sentiment/support):
  about $1.00
- Headroom: about $3.14

## Constraints

- Budget: $5 compute ceiling
- Timeline: 2 weeks to public upload
- Jonah's production time: only in week 2
- Fair use: clips of IT-Mario and Papaplatte capped at 10 seconds
  each, German §51 UrhG covers the commentary purpose
- Language: German on-screen narrative; English for code and chart
  labels

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Scope creep past V2.5 | Cut-list ordered: N=10 held-out, then denglisch reverse-engineer, then comment AI classification. Ship without them if Day 5 is behind. |
| Fair use challenge on clips | Hard 10-second cap per clip, commentary frame, visible code repo establishes work product. |
| Creators respond negatively | Balanced second-opinion tone, no roasting, Papaplatte correction framed diplomatically. |
| Algorithm deadzone on new channel | 3-Short launch drumbeat and Reddit seeding substitute for organic algorithmic lift. |
| Meta reveal reads as LLM slop | Show actual agent dispatch logs and raw chart data in the reveal, not "I asked ChatGPT" energy. |

## Launch plan

- Day of upload: main video goes live morning DE, Short #1 two hours
  later the same day.
- Day +1: Reddit seeding on r/papaplatte, r/de, and German
  data-science subs. Top-comment with code-repo link.
- Day +2: Short #2 (YouTube censors Papaplatte).
- Day +4: Short #3 (community reveal).
- Day +7: pin a retro comment on the main video.

No proactive DMs to creators. They notice organically via Reddit
seeding or not at all. Soft signal over thirsty outreach.

## Decision log

From the 40-question intake interview plus Day-1 scope refinement:

- 3 methods in final video (his script / AI / our hybrid). Originally
  planned as a 2-method cut; expanded to 3 once the rebuild-and-
  compare framing took over from the Papaplatte-correction framing.
- Primary goal is the methodology showcase. Creator reaction is
  bonus, not the success metric.
- Gaming only for Papaplatte (match IT-Mario, save multi-channel for
  V3)
- 6-10 min video length (new channel, retention matters)
- Comments included despite scope expansion (matches Mario's full
  scope)
- Whisper on 3 samples, not 1 (bracket profanity delta with a mean)
- Scene beats, not full script (face-cam improv reads natural)
- Reddit seeding, not creator DMs (soft signal, not thirsty)
- Meta reveal at video end (sets up AI Playbook series)
- Tone: nerdy-but-accessible. A normal viewer should follow the
  comparison without already knowing what TTR means going in.

## Related docs

- HANDOFF.md — session-to-session handoff summary
- docs/TASKS.md — task specification with acceptance criteria
- docs/IT-MARIO-VIDEO.md — source video breakdown
- docs/FINDINGS.md — V2 technical findings (needs sample-size fix in
  task T01)
- docs/video-script.md — scene-by-scene beats (created in task T13)
- docs/shorts-script.md — Shorts beats (created in task T13)
- report.html — live dashboard
