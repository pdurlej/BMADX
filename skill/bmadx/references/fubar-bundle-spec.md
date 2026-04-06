# FUBAR Bundle Spec

`X4/FUBAR` generates a scaffold bundle for a hard repo or a hard change.

## Goal

Do not replace BMAD. Add the missing operational layer under Codex quickly and
portably.

## What the bundle includes

- required `AGENTS.md` draft for the repo,
- required `core-bmad-master.customize.yaml` snippet,
- required `bmm-dev.customize.yaml` snippet,
- optional `bmm-architect.customize.yaml` snippet,
- required `bmadx-trigger-matrix.md`,
- required `bmadx-verify-matrix.md`,
- required `bmadx-rollout-checklist.md`,
- required `bmadx-subagent-policy.md`.

## When to render it

Render the bundle only when:
- classification says `X4`,
- you already entered BMAD through `/bmad-bmm-create-prd` and `/bmad-bmm-create-architecture`,
- you need to clean up ownership, rollout, verify matrix, or snippet adoption beyond plain BMAD.

## When not to render it

Do not render the bundle when:
- the task is obviously `X1` or `X2`,
- a normal `X3` flow based on existing BMAD artifacts is enough,
- the bundle would become a second plan store or a substitute for `project-context.md`.

## Bundle rules

- keep the language simple,
- avoid OMX vocabulary drift,
- state `BMAD > BMADX` explicitly,
- point to `project-context.md` as durable technical memory,
- keep the bundle manually adoptable without an extra runtime.

## Render parameters

- `project_name`
- `project_path`
- `generated_at`
- `bmadx_skill_path`
- `bmad_skill_path`
- `include_architect`

## Exit criteria

- every bundle file is generated,
- required artifacts are ready for adoption without extra decisions,
- the optional architect snippet is included only when the project genuinely needs that role,
- every file is understandable without OMX context,
- there is no second durable plan store,
- BMAD phases are not redefined.
