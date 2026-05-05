# Rescue Mode (`X4/FUBAR`)

Rescue Mode is the rare, stronger path for difficult repos or difficult changes.

It exists for situations where BMAD alone is not enough as an operational layer inside Codex.

## Use Rescue Mode when

- the repo is messy or high-entropy,
- ownership is unclear,
- rollout or verification structure needs to be made explicit,
- a scaffold bundle will reduce risk,
- a normal bounded answer is no longer enough.

## Do not use Rescue Mode when

- the task is a small fix,
- a normal bounded change is enough,
- a standard BMAD flow already covers the work,
- you are treating `X4` like a default mode.

## What it generates

- `AGENTS.md`
- `.customize.yaml` snippets
- trigger matrix
- verify matrix
- rollout checklist
- subagent policy
- Architecture Guardrail Card
- Failure Patterns / Guardians section inspired by Guardrails.md-style safety memory

## Failure Patterns / Guardians

Rescue Mode should make repeated mistakes explicit:

| Trigger | Risk | Guardian |
| --- | --- | --- |
| auth, billing, permissions, migrations, data deletion, secrets, production config | high blast radius | `X3` minimum unless purely textual |
| repeated failed attempts | context pollution and retry loops | stop, summarize, add a repo guardrail if appropriate |
| unclear architecture owner | logic lands in the wrong layer | answer the Architecture Guardrail Card before implementation |
| no proof path | false confidence for a non-technical owner | do not mark done; propose the smallest credible proof |

This section is compatible with `GUARDRAILS.md`, but it does not replace BMAD.
BMAD remains the owner of PRD, architecture, stories, and durable process
context.

## Entry rule

Enter BMAD first:
1. `/bmad-bmm-create-prd`
2. `/bmad-bmm-create-architecture`

Only then render the bundle if the repo really needs it.

## Exit rule

Rescue Mode is not a permanent state.

Once the repo has enough structure:
- return to normal BMAD-driven work for process-heavy tasks,
- return to compact BMADX usage for bounded tasks,
- keep `_bmad-output/project-context.md` as the durable technical memory.
