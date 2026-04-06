# Architecture — BMADX v0.2.2

## Decision

Keep BMADX small and tactical.

## Main architectural choices

- response shaping for obvious `X1/X2` belongs in the skill contract, not in new gate flags
- benchmark governance should validate response shape and reference-read budget, not just tokens
- BMADX remains an overlay on BMAD rather than a parallel process system

## Constraints

- `BMAD > BMADX`
- BMADX stays lighter than OMX
- `X4/FUBAR` stays rare and valuable
- no second durable plan store
