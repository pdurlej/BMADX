# Planning Effort Advisor

Planning effort is separate from execution effort. Use it when the next Codex
phase is primarily architecture, decomposition, recovery planning, or another
decision-heavy activity. Do not surface it for obvious `X1/X2` execution.

## Eight Signals

Count only signals that are actually present:

1. `red_zone_or_irreversible` - auth, billing, privacy, deletion, destructive
   migration, public side effect, or another hard-to-reverse consequence.
2. `cross_system_scope` - several systems, repositories, or ownership
   boundaries must agree.
3. `ambiguous_ownership_or_requirements` - the owner, requirements, or evidence
   are unclear or contradictory.
4. `long_horizon_or_compaction` - the work spans phases, long context, or likely
   compaction.
5. `repeated_failure_or_incident` - previous attempts failed or the system is
   already in incident/recovery state.
6. `rollback_or_recovery_complexity` - rollback, migration, or recovery cannot
   be proved cheaply.
7. `weak_or_expensive_verification` - verification is indirect, slow, costly,
   or incomplete.
8. `broad_decomposition_pressure` - planning benefits from broad decomposition
   or delegated research before one owner synthesizes the decision.

## Mapping

| Matched signals | Planning effort | Meaning |
| --- | --- | --- |
| `0..1 / 8` | `high` | normal consequential planning |
| `2..3 / 8` | `xhigh` | several interacting constraints |
| `4..5 / 8` | `max` | high-complexity planning; operator confirms |
| `6..8 / 8` | `ultra` only with signal 8; otherwise `max` | broad decomposition; operator confirms |

Cap the recommendation to levels exposed by the active model. For example,
Luna caps an `ultra` recommendation to `max`; GPT-5.5 caps `max/ultra` to
`xhigh`.

`ultra` is exceptional because the observed Sol/Terra catalog may add automatic
delegation behavior. Suggest it only when broad decomposition is itself useful,
not merely because the task is risky.

## Display Contract

```text
Planning effort: max - 5/8 signals: cross_system_scope, long_horizon_or_compaction, ...; suggestion only.
```

Name the matched signals. Never imply that a score changes `X1..X4`, BMAD
ownership, execution permission, goal/loop state, or global Codex config. After
the plan is accepted, execution can return to the normal model/gear mapping,
often `high` for Sol.

Deterministic helper:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/advise_planning_effort.py" \
  --model gpt-5.6-sol \
  --signals cross_system_scope,long_horizon_or_compaction,weak_or_expensive_verification \
  --json
```
