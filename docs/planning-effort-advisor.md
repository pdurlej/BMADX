# Planning Effort Advisor

BMADX can tell the operator when a planning phase deserves more reasoning than
the later execution phase. The recommendation is evidence shown as `Y/8`, not
a hidden model switch.

## Signals

Count: red-zone/irreversible impact, cross-system scope, ambiguous ownership or
requirements, long horizon/compaction, repeated failure/incident, complex
rollback/recovery, weak or expensive verification, and broad decomposition
pressure.

| Score | Recommendation |
| --- | --- |
| `0..1 / 8` | `high` |
| `2..3 / 8` | `xhigh` |
| `4..5 / 8` | `max`, with operator confirmation |
| `6..8 / 8` | `ultra` only if broad decomposition is useful; otherwise `max` |

The active model caps the result. Luna therefore caps `ultra` to `max`.

Example:

```text
Planning effort: max - 5/8 signals: cross-system scope, ambiguous ownership, long horizon, rollback complexity, expensive verification; suggestion only.
```

This is not a fifth gear. It does not change `X1..X4`, BMAD gates, global Codex
config, or the execution effort. A task can plan on `max` and execute on `high`.
`ultra` needs explicit operator confirmation because it may introduce automatic
delegation behavior on models that support it.
