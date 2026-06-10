---
name: bmadx
description: "Use when Codex should pick the lightest safe BMAD-backed workflow for a coding task: tiny change, bounded change, BMAD-heavy work, or rare Rescue Mode."
---

# BMADX

BMADX is a BMAD-first guardrail for Codex. It chooses the lightest safe mode,
checks the compact gate, and keeps copy tweaks, normal work, risky work, and
rescue work separate.

Hard rules:
- `BMAD > BMADX`
- Codex-first; no second plan store; no runtime platform.
- Stronger models do not bypass BMAD ownership, gates, or verification.
- Answer starts with one `Choice:` line. Never start with `Phase`, `Gate`,
  `Contract`, `Plan`, `FAZA`, or `WYKONANE`.

## Fast Flow

1. Classify.
2. Use compact gate for the chosen gear.
3. Answer in the shortest safe contract.
4. Open references only for ambiguity, red zones, boundary cases, or `X4`.

Compact gate command:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X1 --compact
```

Replace `X1` with the chosen gear.

Gate semantics:
- `classification_allowed=false`: stop and report the BMADX blocker.
- `X1/X2`: warnings are soft unless BMADX itself is blocked.
- `X3/X4`: `execution_allowed=false` is a hard execution stop.
- If `X3/X4` are blocked, keep the classification and report execution block separately.

Blocked `X3/X4` remediation must be exactly:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/scripts/sync_bmad_method.py" check --json
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/scripts/sync_bmad_method.py" sync
```

## Gearbox

- `X1`: tiny local change, no process or architecture risk.
- `X2`: bounded normal change, short plan and verify.
- `X3`: BMAD-heavy, red-zone, architecture, contract, data, or rollout work.
- `X4`: rare Rescue Mode for messy ownership, recovery, incidents, or scaffold-shaped work.

Rules:
- A plan request does not force `X3`; bounded work can stay `X2`.
- Obvious `X1/X2` must not open references.
- Red-zone work is `X3` minimum unless purely textual.
- `X4` only for rescue-shaped cases.

Red zones: auth, billing, payments, permissions, migrations, data deletion,
privacy, secrets, production config, webhooks, encryption, admin roles,
multi-tenant access, legal/compliance.

## Guardrail Card

Use silently for `X1/X2`; surface only when risk changes the mode.

1. What outcome are we protecting?
2. Which system area owns this?
3. Which existing pattern should be followed?
4. What breaks if this lands in the wrong place?
5. What proof would convince a non-technical owner?

## Thinking Budget

Advisory only; never changes routing, gate, or global Codex config.

- `X1=medium` for Codex/GPT-5.5 code tasks; `low` is experimental.
- `X2=medium`
- `X2/X3 boundary=high`
- `X3=high`
- `X4=xhigh` for real rescue execution

Canonical values: `minimal`, `low`, `medium`, `high`, `xhigh`. Normalize
`extra high` / `extra_high` to `xhigh`.

Line when needed:

```text
Thinking: high — suggestion only.
```

## Goal and Loop Discipline

Use only for multi-step work where it improves closure. It does not add a gear.

- `/goal` is a Codex thread objective; BMADX still chooses `X1..X4`.
- Goal text should name the outcome, proof, and stop condition.
- Use `/plan` first when the goal is unclear.
- Loops are bounded review -> repair -> validate passes, not runtime state.
- Stop a loop when validation passes, attempts are exhausted, delta stalls, or
  human review is needed.
- Do not create hooks, MCP, plugins, subagents, workers, dispatch commands,
  persistent run IDs, or a second plan store.

Lines when relevant:

```text
Goal: yes — use `/goal` because the work needs a persistent definition of done.
Loop: yes — max 3 review/repair/validate passes; stop on pass, stale delta, hard stop, or human review.
```

## Response Contract

`X1`: max 5 lines / 650 chars.

```text
Choice: X1 — One-shot
Why: one sentence.
Next step: one sentence.
```

`X2`: max 12 lines / 1000 chars.

```text
Choice: X2 — Regular
Why: one sentence.
Plan:
1. ...
2. ...
Verify:
1. ...
2. ...
```

`X3/X4`: preserve BMAD-first ownership, execution gate state, and verification.
Do not inline long artifacts in planning-only or benchmark prompts.

## X4 Rescue Mode

Use `X4/FUBAR` only for unclear ownership, repeated failure, rollback risk,
incident recovery, no credible verification path, or high-entropy repo/scope.
Start from BMAD PRD and architecture, update `_bmad-output/project-context.md`,
then render the bundle only when execution is allowed.

## References On Demand

- [gearbox.md](references/gearbox.md)
- [trigger-matrix.md](references/trigger-matrix.md)
- [architecture-guardrails.md](references/architecture-guardrails.md)
- [thinking-budget.md](references/thinking-budget.md)
- [goal-loop.md](references/goal-loop.md)
- [execution-boundaries.md](references/execution-boundaries.md)
- [verify-discipline.md](references/verify-discipline.md)
- [fubar-bundle-spec.md](references/fubar-bundle-spec.md)
