# Gearbox `X1..X4`

BMADX acts like an automatic gearbox. It classifies the task first, then chooses
the right process weight.

Since `v0.2`, gear classification and execution approval are separate decisions:
- `X1/X2` can proceed through a soft gate when BMAD is degraded,
- `X3/X4` require a healthy execution gate,
- a red gate must not change the correct task classification.

Since `v0.2.2`, the preferred order is:
- classify first,
- then run `sync_bmadx.py check --gear ... --compact`,
- keep `check --json` without `--gear` as a diagnostic mode, not the default routing path.

This file is for boundary cases and debugging. For obvious `X1/X2`, the contract
embedded in `SKILL.md` is enough; do not open refs if classification is clear
and the compact gate is green.

| Gear | When to use it | What to do | What should exist on exit |
| --- | --- | --- | --- |
| `X1` | tiny local task; low blast radius; 1-2 checks | keep the plan in your head, implement, verify | change plus evidence |
| `X2` | a few files, some risk, still no full BMAD | short plan, implement, verify, optional review | short plan, change, evidence |
| `X3` | needs BMAD artifacts or workflow-map guidance | enter the real BMAD flow and work from artifacts | BMAD artifact plus code plus evidence |
| `X4` | chaos, wide scope, risky rollout, needs scaffold bundle | BMAD flow plus bundle plus verify discipline | bundle plus operating plan plus evidence |

## Architecture defaults

Use the Architecture Guardrail Card as the default decision model, but expose it
only when it helps the user:

- `X1`: silent card, no user questions unless a red zone appears.
- `X2`: silent card, short plan, key tradeoff only.
- `X3`: explicit card, BMAD artifact alignment, hard execution gate.
- `X4`: explicit card inside the Rescue Mode bundle, tied to owners, failure patterns, guardians, and verification.

The card asks:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

## Thinking budget defaults

Thinking budget is advisory and follows the chosen gear; it must not change the
gear or mutate global Codex config.

- `X1`: `low`, fallback `medium`.
- `X2`: `medium`.
- `X2/X3` boundary: `high`.
- `X3`: `high`.
- `X4`: `xhigh` for rescue execution; `high` can be enough for classification-only prompts.

Details: [thinking-budget.md](thinking-budget.md)

## Goal and loop defaults

Goal and loop discipline is an execution aid, not a fifth gear.

- `X1/X2`: no `/goal` and no loop unless the user explicitly asks for a longer
  thread-level objective.
- `X3`: recommend `/goal` when the task needs a persistent definition of done
  across multiple Codex turns, with proof and stop conditions.
- `X4`: recommend `/goal` plus a bounded review/repair/validate loop only for
  real Rescue Mode execution.

Details: [goal-loop.md](goal-loop.md)

## Input signals

### X1
- 1 file or very local scope,
- no API/CLI contract changes,
- no auth/security/schema/migration/data/billing risk,
- no new BMAD artifact needed.

### X2
- 2-5 files or more than one directory,
- needs a short plan,
- verification needs a few checks,
- still does not need the full BMAD flow.

### X3
- new story or an existing BMAD story,
- needs PRD, architecture, readiness, or story context,
- the change must stay grounded in process artifacts,
- touches a red-zone area unless purely textual or documentation-only.

### X4
- the user talks about a plan, chaos, a hard project, or escalation,
- the scope is multi-threaded or diffuse,
- rollout, ownership, verify matrix, and snippets need deliberate design,
- a normal quick flow is no longer enough.

## Transition rules

- `plan` or high ambiguity means ask questions before recommending a gear.
- Do not escalate from `X1` to `X3` if `X2` is enough.
- Red-zone areas are `X3` minimum unless the change is purely textual or documentation-only.
- Red-zone areas plus messy ownership, incident recovery, destructive data risk, or unclear proof can become `X4`.
- `X4` is not a punishment or the default. Use it only when the absence of a scaffold bundle increases decision risk.

## Exit gates

- `X1`: short result plus verify.
- `X2`: short plan executed plus verify plus optional review.
- `X3`: BMAD artifact alignment plus verify plus a healthy execution gate.
- `X4`: bundle rendered, ownership clear, verify matrix ready, healthy execution gate, and BMAD still remains the source of truth.

## Compact gate after classification

- `X1/X2`: prefer the fast path with a cached healthy BMAD snapshot; no cache should warn, not block.
- `X3/X4`: always require a live BMAD check and can return remediation.
