# BMADX v0.2 Plan

## Goal

Increase BMADX usefulness without losing its main advantages:
- simple `X1..X4` routing
- BMAD-first discipline
- strong `X4/FUBAR`
- low overhead for simple tasks

## Scope

### 1. Soft gate for `X1/X2`

Problem:
- `v0.1` always ran the dependency gate,
- even simple tasks produced noisy `needs_attention` output.

Goal:
- `X1` and `X2` should classify and continue without being blocked by a red BMAD state,
- the dependency gate should be a warning for them, not a hard block.

### 2. Separate classify vs execute

Problem:
- `v0.1` mixed gear selection with permission to enter heavier flows.

Goal:
- classification answers: what gear is this?
- execution gate answers: can `X3/X4` execute right now?

### 3. Cache the last healthy BMAD state

Problem:
- the dependency gate moved to `needs_attention` too easily,
- benchmark runs showed that this polluted simple cases.

Goal:
- store the last healthy BMAD state with a timestamp,
- use it as a soft signal for `X1/X2`,
- still require stricter checks for `X3/X4`.

## Out of scope

- full OMX port
- `.omx/` as a second memory system
- tmux or team runtime
- turning BMADX into a dense dependency graph

## Acceptance criteria

- `X1` and `X2` stop spamming the user with dependency-gate noise when routing is obvious
- `X3` and `X4` still respect BMAD health
- `X4/FUBAR` still renders the full scaffold bundle
- reruns show a better simple-task experience
- token cost does not clearly worsen versus `v0.1`
