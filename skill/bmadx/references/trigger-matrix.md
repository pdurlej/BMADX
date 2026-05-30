# Trigger Matrix

Operational matrix for classifying tasks without guessing.

This file is mainly for boundary cases. In the obvious `X1/X2` happy path, use
the heuristics embedded in `SKILL.md` and do not open reference docs.

| Signal | X1 | X2 | X3 | X4 |
| --- | --- | --- | --- | --- |
| 1 local file | yes | no | no | no |
| a few files / local blast radius | no | yes | no | no |
| needs a new BMAD artifact | no | no | yes | yes |
| user says `plan` | no | questions | questions | questions |
| ambiguous scope | no | questions | questions | questions |
| API/schema/auth/perf/concurrency risk | no | sometimes | yes | yes |
| auth, billing, payments, permissions, secrets, production config | no | no | yes | yes |
| data deletion or destructive migration | no | no | yes | yes |
| rollout and ownership need design | no | no | sometimes | yes |
| repeated failure pattern or unclear architecture owner | no | no | sometimes | yes |
| scaffold bundle beyond BMAD | no | no | no | yes |

## Recommended thresholds

- `X1`: simple fix or simple upgrade.
- `X2`: bounded multi-file local change.
- `X3`: normal BMAD flow.
- `X4`: BMAD plus bundle when BMAD alone does not yet provide enough operational structure.

## Red-zone escalation

These signals should become `X3` minimum unless the change is purely textual or
documentation-only:

- auth, login, sessions, OAuth, SSO,
- billing, payments, subscriptions, refunds,
- permissions, admin roles, multi-tenant access,
- database migrations, destructive data changes, data deletion,
- secrets, tokens, production config,
- privacy, compliance, encryption, webhooks, external side effects.

Escalate to `X4` when the red-zone task also has unclear ownership, repeated
failures, rollback risk, incident recovery, or no credible verification path.

## Thinking budget

BMADX may recommend Codex reasoning effort after classification:

- `X1`: `low`
- `X2`: `medium`
- `X2/X3` boundary: `high`
- `X3`: `high`
- `X4`: `xhigh` for rescue execution

This recommendation is a cost-control hint for the current run, not a new gate
and not a global Codex config change. Details: [thinking-budget.md](thinking-budget.md)

## Architecture Guardrail Card

For boundary cases, answer five questions before final classification:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

## Gate after classification

- the correct classification should remain correct even when BMAD is red,
- `X1/X2` use `check --gear X1|X2 --compact` and the cached fast path,
- `X1/X2` without cache should get a warning instead of a block,
- `X3/X4` use `check --gear X3|X4 --compact` with the full live gate,
- without healthy BMAD, execution for `X3/X4` must stop,
- the last healthy BMAD cache softens communication for `X1/X2`, but must not unlock `X3/X4`.

## Example classifications

- "Fix a typo in one component" -> `X1`
- "Add support for a new field in a few places and run tests" -> `X2`
- "Add Google login" -> `X3`
- "Change subscription billing" -> `X3`
- "Delete inactive users" -> `X3`, or `X4` if rollback/ownership is unclear
- "Add admin role" -> `X3`
- "Implement a story from the current BMAD sprint" -> `X3`
- "Set up a working approach for a difficult repo and generate scaffolding" -> `X4`
