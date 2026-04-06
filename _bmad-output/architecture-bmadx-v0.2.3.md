# Architecture — BMADX v0.2.3

## Decision

Treat non-technical adoption as a productization layer, not as a routing rewrite.

## Main architectural choices

- keep the existing routing semantics; improve public usability around them
- make all machine-facing commands portable via `CODEX_HOME` with `~/.codex` fallback
- keep `install_bmadx.py` as the lower-level installer and add a wrapper for public onboarding
- add `--public-sample` rendering for the sample bundle instead of maintaining a second template tree
- keep benchmark governance, but add more human-readable proof surfaces

## Constraints

- `BMAD > BMADX`
- no `.omx` runtime drift
- `X4/FUBAR` stays rare
- no second durable plan store
