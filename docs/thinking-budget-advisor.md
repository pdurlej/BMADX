# Thinking Budget Advisor

BMADX can recommend how much Codex reasoning effort is worth spending on a
task. This is a cost-control hint for the current run, not a new workflow mode.

The order stays the same:

1. BMADX classifies the gear.
2. BMADX checks the compact gate.
3. BMADX recommends a thinking budget for the current task.

BMADX does not edit `~/.codex/config.toml`, create profiles, or change your
global Codex defaults.

## Defaults

| Task shape | BMADX gear | Suggested effort |
| --- | --- | --- |
| tiny copy, typo, local fix | `X1` | `low` |
| bounded normal product change | `X2` | `medium` |
| unclear `X2/X3` boundary | `X3` if risky | `high` |
| BMAD-heavy architecture or red-zone work | `X3` | `high` |
| real Rescue Mode execution | `X4/FUBAR` | `xhigh` |

Use `xhigh`, not `extra_high`, for the highest Codex reasoning effort.

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

Use `xhigh` only for real rescue-shaped work: repeated failures, incident
recovery, unclear rollback ownership, destructive data risk, or a scaffold
bundle that must coordinate owners and proof.

## What this does not do

- It does not choose the gear.
- It does not bypass BMAD.
- It does not make `X4/FUBAR` normal.
- It does not mutate global Codex config.
- It does not prove code quality without tests, CI, static checks, and review.

## Benchmarking

`v0.2.7` adds parser and validation support for a `Thinking:` line in benchmark
responses. This validates whether the recommendation matches the task shape and
whether the answer avoids global config mutation.

Do not claim token savings from the advisor until healthy and degraded benchmark
runs show the savings without red-zone under-escalation, `X4` false positives,
or reference-budget regressions.
