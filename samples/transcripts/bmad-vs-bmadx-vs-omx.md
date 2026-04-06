# BMAD vs BMADX vs OMX

This comparison is directional, not lab-perfect. It exists to explain product
shape to humans.

## BMAD

Best when:
- process artifacts should drive the work from the start
- PRD/architecture/story alignment is the main concern

Tradeoff:
- heavier than many bounded day-to-day tasks need

## BMADX

Best when:
- you want Codex to pick the lightest safe mode
- most work is normal bounded change
- you still want BMAD-compatible guardrails

Tradeoff:
- it does not replace BMAD
- it is not a runtime platform

## OMX

Best when:
- you actually want a heavier orchestration/runtime shape

Tradeoff:
- more runtime weight than BMADX is aiming for

## Honest reading

- BMADX looks strongest publicly when compared with OMX
- BMAD still wins as the process owner
- BMADX is the middle layer for lower-friction Codex work
