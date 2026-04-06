# Architecture — BMADX v0.2.1

## Decision

Separate infrastructure improvements from answer-shaping improvements.

## Main architectural choices

- `X1/X2` get a fast path that can use the last healthy BMAD cache
- `X3/X4` keep a hard live BMAD gate
- `sync_bmadx.py --compact` becomes the routing-facing output contract
- benchmark runs should create separate `healthy` and `degraded` datasets
