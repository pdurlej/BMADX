# Goal and Loop Discipline

BMADX can now describe when a Codex task should use `/goal` or a bounded repair
loop. This is not a new BMADX gear.

The order stays:

1. classify `X1..X4`,
2. check the compact gate,
3. recommend thinking budget when useful,
4. recommend `/goal` or a bounded loop only when the task shape needs it.

## Goal Mode

Use `/goal` when the work may span multiple turns and Codex needs a persistent
definition of done. Good goal text names the outcome, proof, stop condition, and
hard constraints.

Do not use `/goal` for obvious `X1/X2` work. A tiny copy fix or bounded local
change should stay in the normal BMADX contract.

Example:

```text
Goal: yes — use `/goal` because the work needs a persistent definition of done.
```

## Repair Loops

A loop is useful when each pass should learn from validation evidence:

1. review,
2. repair,
3. validate,
4. carry forward only the remaining delta.

Stop when validation passes, the attempt limit is reached, the remaining delta
stops shrinking, a hard stop appears, or human review is needed.

Defaults:

| Gear | Loop default |
| --- | --- |
| `X1/X2` | no loop |
| `X3` | max 2 passes when evidence must drive the next pass |
| `X4` | max 3 passes for real Rescue Mode execution |

Example:

```text
Loop: yes — max 3 review/repair/validate passes; stop on pass, stale delta, hard stop, or human review.
```

## Boundaries

Goal and loop discipline must not create hooks, MCP setup, plugins, subagents,
worker lanes, dispatch commands, persistent run IDs, runtime state, a second
plan store, auto-merge, or auto-deploy behavior.

BMAD remains the process source of truth. BMADX exports the smallest useful
contract for Codex to keep working safely.
