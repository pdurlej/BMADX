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
