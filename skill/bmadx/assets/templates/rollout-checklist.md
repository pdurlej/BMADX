# BMADX Rollout Checklist for {{project_name}}

- [ ] The bundle is used only after entering BMAD through PRD and architecture.
- [ ] The bundle is not being used for `X1/X2` or as a shortcut for a normal `X3`.
- [ ] The repo has an `AGENTS.md` aligned with `BMAD > BMADX`.
- [ ] `_bmad-output/project-context.md` exists or there is an explicit plan to create it.
- [ ] The required bundle artifacts are ready for adoption: `AGENTS.md`, `core-bmad-master.customize.yaml`, `bmm-dev.customize.yaml`, `bmadx-trigger-matrix.md`, `bmadx-verify-matrix.md`, `bmadx-rollout-checklist.md`, `bmadx-subagent-policy.md`.
- [ ] Optional `bmm-architect.customize.yaml` is included only when the project genuinely needs an architect layer.
- [ ] The team understands `X1..X4`.
- [ ] Verify-before-done is enforced.
- [ ] `X4/FUBAR` remains an exceptional mode.
- [ ] Optional `.codex/agents` adoption has been assessed and is not required on day one.

## Architecture Guardrail Card

- [ ] The protected user/product outcome is written down.
- [ ] The owning system area is named.
- [ ] The existing pattern to follow is named.
- [ ] The likely breakage from a wrong implementation location is named.
- [ ] The proof a non-technical owner can understand is named.

## Failure Patterns / Guardians

Use this table for repeated failures or repo-specific hard constraints. This is
inspired by `GUARDRAILS.md`, but it is not a replacement for BMAD artifacts.

| Trigger | Risk | Guardian rule | Required proof | Escalation owner |
| --- | --- | --- | --- | --- |
| Auth, billing, permissions, migrations, data deletion, secrets, production config | High blast radius | `X3` minimum unless purely textual | BMAD artifact alignment plus deterministic checks | Technical reviewer |
| Repeated agent failure or circular debugging | Context pollution and bad retry loops | Stop, summarize failure pattern, update repo guardrail if appropriate | Repro or failing check plus new safe next step | Project owner |
| Unclear architecture owner | Logic lands in the wrong layer | Use Architecture Guardrail Card before implementation | Owner/system boundary identified | BMAD architect / technical reviewer |
| No credible verification path | False confidence for non-technical owner | Do not mark done; propose smallest proof or human review | Check command, manual proof, or explicit gap | Project owner |

- [ ] Oracle second-opinion review is used when the rescue plan has expert-level ambiguity.

Generated: {{generated_at}}
