# Thinking Budget Advisor

BMADX can recommend how much Codex reasoning effort is worth spending for a
task. The recommendation is not a new router. It is a consequence of the chosen
gear, the risk shape, and the phase of work.

Non-negotiable rules:
- gear classification still comes first,
- the compact gate still decides execution permission,
- BMAD remains the process source of truth,
- the recommendation is per task or per benchmark run,
- BMADX must not edit or tell the user to edit global Codex config.

## Runtime-supported values

Use only values supported by the active model. The current Codex catalog union
is:

- `low`
- `medium`
- `high`
- `xhigh`
- `max`
- `ultra`

If the user says `extra_high`, `extra-high`, or `extra high`, normalize it to
`xhigh`. Do not emit `extra_high` in public docs, benchmark summaries, or skill
answers.

BMADX does not recommend `max` or `ultra` as execution defaults. The separate
planning-effort advisor may suggest them from a visible `Y/8` score with
operator confirmation. Luna does not currently expose `ultra`.

## Defaults

| Model | `X1` | `X2` | `X3` | `X4` |
| --- | --- | --- | --- | --- |
| GPT-5.5 | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Sol | `medium` | `medium` | `high` | `high` |
| GPT-5.6 Terra | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Luna | `medium` | `medium` | `high` | `xhigh` |

For `X2/X3` boundaries, use at least `high`. For classification-only `X4`,
`high` is enough even when real execution would use the profile's `X4` value.

## Escalate effort

Escalate to `high` when the task touches:

- API or schema contracts,
- auth, billing, payments, permissions, or secrets,
- production config,
- privacy or user data safety,
- performance, concurrency, or external side effects,
- unclear architecture ownership.

Escalate to `xhigh` only when the work is genuinely rescue-shaped:

- repeated failure loop,
- destructive migration or data deletion with unclear rollback,
- incident recovery,
- no credible verification path,
- broad scaffold bundle or Rescue Mode execution.

## Downgrade effort

Try `low` only as an explicit experiment when the task is pure typo/copy/doc-only
work and the blast radius is local. Prefer `medium` until `low` proves cheaper
in repeatable model-specific canaries.

Prefer `medium` for normal bounded `X2` work with a clear owner, existing
pattern, and known verification path.

For classification-only answers, cap effort at `medium` or `high` unless the
task is a real Rescue Mode execution.

For planning-only work, use [planning-effort.md](planning-effort.md). A plan may
use `xhigh`, `max`, or `ultra` and then hand execution back to the normal gear
mapping. Do not carry an expensive planning level into execution automatically.

If the current session is already running above the recommendation, do not ask
the user to restart mid-task. Say that the next run can use lower effort if the
savings matter.

## Display policy

For obvious `X1/X2`, hide the recommendation unless the user asks or the
benchmark prompt requests it.

For boundary cases and `X3/X4`, show one compact line:

```text
Thinking: high — suggestion only for this Codex run.
```

For benchmark output, the line is required so the runner can validate it:

```text
Thinking: low|medium|high|xhigh|max|ultra — suggestion only.
```

## What not to do

- Do not use thinking effort to choose the gear.
- Do not let `xhigh` make `X4` normal.
- Do not default to `low`, `max`, or `ultra` without model-specific benchmark evidence.
- Do not edit `~/.codex/config.toml`.
- Do not create profiles, hooks, MCP, plugins, runtime state, or a second plan store.
- Do not claim token savings until healthy and degraded benchmark runs prove them.
