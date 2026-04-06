# Verify Discipline

BMADX does not close work without evidence.

This file is boundary/debug material. For obvious `X1/X2`, verify should stay
short and follow the response contract in `SKILL.md`.

## Rule

Implement first, verify second, report done last.

The dependency gate does not remove that rule:
- `X1/X2` may execute with a BMAD warning or with a cached healthy snapshot,
- `X3/X4` require healthy BMAD before process-grade verify makes sense,
- after classification, the preferred path is `sync_bmadx.py check --gear ... --compact`.

## Minimum contract

### X1
- 1-2 checks or the strongest available oracle,
- brief proof in the answer.

### X2
- short execution plan,
- local checks,
- `/review` if the diff is not trivial.

### X3
- verify aligned with BMAD criteria,
- alignment with `project-context.md`,
- evidence at both code and workflow level.

### X4
- verify matrix from the bundle,
- explicit ownership,
- proof that the scaffold does not create a second source of truth.

## If checks do not exist

- say so explicitly,
- use the strongest available oracle,
- do not pretend certainty you do not have.

## Anti-patterns

- "should work" without evidence,
- closing the task without check results,
- review without verify,
- verify without tying back to expected behavior.
