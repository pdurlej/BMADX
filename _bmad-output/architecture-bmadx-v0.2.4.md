# Architecture — BMADX v0.2.4

## Decision

Treat GPT-5.5 as a stronger Codex execution substrate, not as a reason to
change BMADX routing semantics.

## Main architectural choices

- keep `sync_bmadx.py` gate behavior unchanged
- move model choice into benchmark configuration, not global user config
- make benchmark artifacts model-aware through a stable filename slug
- add overreach validation so stronger models do not over-escalate simple cases
- keep public docs clear that BMADX is a boundary and verification layer

## Constraints

- `BMAD > BMADX`
- no `.omx` runtime drift
- `X4/FUBAR` stays rare
- no second durable plan store
- GPT-5.5 is a Codex/ChatGPT target for BMADX, not an API availability claim
