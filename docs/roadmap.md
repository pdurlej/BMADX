# BMADX Roadmap

This is the public roadmap surface for the repo.

It is intentionally lightweight.

## Current status

Current public version:
- `v0.2.4`

What `v0.2.4` focuses on:
- tuning BMADX for Codex on GPT-5.5
- keeping GPT-5.5 from bypassing BMAD boundaries or Rescue Mode discipline
- model-aware benchmark artifacts that do not overwrite historical GPT-5.4 runs
- clearer positioning: BMADX is a boundary and verification layer, not a substitute for model intelligence

## What is already stable

- BMAD dependency and `BMAD > BMADX`
- four-gear routing model: `X1..X4`
- hard/soft split between `X1/X2` and `X3/X4`
- `X4/FUBAR` scaffold bundle
- benchmark runner committed in-repo
- model-aware benchmark output naming

## Near-term improvements

- keep making the public surface friendlier for non-technical Codex users
- improve proof surfaces with better transcripts and examples
- make Rescue Mode easier to adopt without turning it into a default mode
- keep tightening portability and low-friction install paths

## Long-term guardrails

These should not change:
- BMAD remains the upstream process owner
- BMADX stays lighter than OMX
- BMADX stays useful for vibe coders without becoming undisciplined
- BMADX should not drift into a full orchestration runtime
