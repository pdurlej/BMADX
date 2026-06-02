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

## Canonical values

Use only these values:

- `minimal`
- `low`
- `medium`
- `high`
- `xhigh`

If the user says `extra_high`, `extra-high`, or `extra high`, normalize it to
`xhigh`. Do not emit `extra_high` in public docs, benchmark summaries, or skill
answers.

## Defaults

| Work shape | Recommended effort | Notes |
| --- | --- | --- |
| `X1` obvious tiny/local | `medium` | `low` is experimental until repeatable GPT-5.5 canaries prove it is cheaper |
| `X2` bounded normal work | `medium` | default for most useful BMADX work |
| `X2/X3` boundary | `high` | ambiguity, contract risk, API/schema/auth/perf signals |
| `X3` BMAD-heavy | `high` | BMAD artifacts and hard gate matter more than model effort |
| `X4` Rescue execution | `xhigh` | only for real rescue/bundle/incident-shaped work |
| `X4` classification-only prompt | `high` | `xhigh` may be suggested for real execution |

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
work and the blast radius is local. For Codex/GPT-5.5 code tasks, prefer
`medium` until `low` proves cheaper in repeatable canaries.

Prefer `medium` for normal bounded `X2` work with a clear owner, existing
pattern, and known verification path.

For classification-only answers, cap effort at `medium` or `high` unless the
task is a real Rescue Mode execution.

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
Thinking: low|medium|high|xhigh — suggestion only.
```

## What not to do

- Do not use thinking effort to choose the gear.
- Do not let `xhigh` make `X4` normal.
- Do not use `minimal` or default `low` for code-editing `X1` until benchmark evidence supports it.
- Do not edit `~/.codex/config.toml`.
- Do not create profiles, hooks, MCP, plugins, runtime state, or a second plan store.
- Do not claim token savings until healthy and degraded benchmark runs prove them.
