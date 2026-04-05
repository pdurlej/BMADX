# BMADX Roadmap

This is the public roadmap surface for the repo.

It is intentionally lightweight. Historical planning artifacts still exist in
the repo, but this file is the easier public entry point.

## Current status

Current public version:
- `v0.2.2`

What `v0.2.2` established:
- short response contract for obvious `X1/X2`
- `classify first, gate second`
- compact gate usage for routing
- mixed-metric benchmark guardrails
- `healthy` and `degraded` benchmark profiles

## What is already stable

- BMAD dependency and `BMAD > BMADX`
- four-gear routing model: `X1..X4`
- hard/soft split between `X1/X2` and `X3/X4`
- `X4/FUBAR` scaffold bundle
- benchmark runner committed in-repo

## Near-term improvements

- make installation more one-command friendly
- translate or replace the remaining important Polish public docs
- tighten the public benchmark story so the caveats are obvious at a glance
- make `X4` easier to adopt in external repositories without turning it into a default mode

## Long-term guardrails

These should not change:
- BMAD remains the upstream process owner
- BMADX stays lighter than OMX
- BMADX stays useful for vibe coders without becoming undisciplined
- BMADX should not drift into a full orchestration runtime
