# Thinking Budget Advisor

BMADX can recommend how much Codex reasoning effort is worth spending on a
task. This is a cost-control hint for the current run, not a new workflow mode.

The order stays the same:

1. BMADX classifies the gear.
2. BMADX checks the compact gate.
3. BMADX recommends a thinking budget for the current task.

BMADX does not edit `~/.codex/config.toml`, create profiles, or change your
global Codex defaults.

## Model-aware defaults

| Model | `X1` | `X2` | `X3` | `X4/FUBAR` |
| --- | --- | --- | --- | --- |
| GPT-5.5 | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Sol | `medium` | `medium` | `high` | `high` |
| GPT-5.6 Terra | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Luna | `medium` | `medium` | `high` | `xhigh` |

Use `xhigh`, not `extra_high`. Current Sol and Terra also expose `max` and
`ultra`; Luna exposes `max`. BMADX accepts those values but does not recommend
them automatically until model-specific benchmark evidence exists.

## When BMADX should show it

For obvious `X1/X2`, BMADX should usually keep the recommendation silent. The
point is to keep simple work simple.

For boundary cases, `X3`, `X4`, and benchmark output, BMADX can show one compact
line:

```text
Thinking: high — suggestion only for this Codex run.
```

## Escalation rules

Use `high` when the work touches API contracts, schema changes, auth, billing,
permissions, secrets, production config, user data, privacy, performance,
concurrency, or unclear architecture ownership.

Use `xhigh` only when the active profile maps real rescue-shaped work there:
repeated failures, incident recovery, unclear rollback ownership, destructive
data risk, or a scaffold bundle that must coordinate owners and proof. Sol
starts at `high` for the same shape and escalates only with evidence.

## What this does not do

- It does not choose the gear.
- It does not bypass BMAD.
- It does not make `X4/FUBAR` normal.
- It does not mutate global Codex config.
- It does not prove code quality without tests, CI, static checks, and review.

## Benchmarking

The benchmark parser validates `Thinking:` against the task shape and active
model profile while rejecting global config mutation. `max` and `ultra` are
recognized Codex values, but the advisor does not select them by default.

Do not claim token savings from the advisor until healthy and degraded benchmark
runs show the savings without red-zone under-escalation, `X4` false positives,
or reference-budget regressions.
