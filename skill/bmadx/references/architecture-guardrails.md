# Architecture Guardrails for Non-Technical Builders

BMADX is not an architect. It is a small boundary layer that helps Codex avoid
architecture-shaped mistakes and escalate to BMAD when the work is no longer
safe as a compact task.

Use this reference for boundary cases, red-zone tasks, and Rescue Mode. For
obvious `X1/X2`, the embedded `SKILL.md` contract is enough.

## Architecture Guardrail Card

Use five questions:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

The card is meant to reduce architecture guessing. It should not become a new
artifact store. If the answer needs durable process memory, write or update the
BMAD-owned artifact instead.

## Defaults by Gear

| Gear | Default behavior | User-facing behavior |
| --- | --- | --- |
| `X1` | Answer the card silently from local context. | No questions unless a red zone appears. |
| `X2` | Answer the card silently and keep a short plan. | Surface only the key tradeoff and proof. |
| `X3` | Answer the card explicitly and enter BMAD. | Ground decisions in PRD, architecture, story, or `project-context.md`. |
| `X4` | Put the card into Rescue Mode. | Connect outcomes, owners, failure patterns, guardians, and verification. |

## Red-Zone Escalation

These signals are never normal `X1` work unless the change is purely textual or
documentation-only:

- auth, login, sessions, OAuth, SSO
- billing, payments, subscriptions, refunds
- permissions, roles, admin panels, multi-tenant access
- database migrations, destructive data changes, data deletion
- secrets, tokens, production configuration
- user data privacy, legal/compliance, GDPR-style work
- encryption, webhooks, external API side effects

Default rule:
- red-zone task -> `X3` minimum
- red-zone task plus messy ownership, rollback risk, incident recovery, or unclear verification -> `X4`

## When This Becomes BMAD

Choose `X3` when:
- a BMAD artifact should drive the work,
- architecture ownership is unclear,
- the change alters contracts, data, auth, billing, permissions, or production behavior,
- the proof cannot be reduced to a few local checks.

Choose `X4` only when:
- the project is already messy or high-entropy,
- failure patterns are repeating,
- owners and rollout need to be made explicit,
- BMAD needs a tactical scaffold bundle for Codex adoption.

## Structured Question UI Pattern

When ambiguity blocks safe classification, ask at most three questions. In
Codex planning mode, prefer the structured multiple-choice UI:

- use two or three mutually exclusive options,
- put the safest/recommended option first,
- rely on the free-form `Other` option for unusual cases,
- avoid long explanation inside the question.

Good question examples:

- Scope: `Small local change (recommended)` / `Touches architecture` / `Not sure`
- Risk area: `No red zone (recommended)` / `Auth/billing/data` / `Production/deploy`
- Proof: `Local tests/build (recommended)` / `Needs BMAD artifact` / `Needs human review`

Do not ask questions just to make the process feel formal. Ask only when the
answer changes the gear, the proof, or whether BMAD must own the next step.

## Guardrails.md Relationship

`GUARDRAILS.md`-style files are useful as repo-local safety memory for repeated
failure patterns and forbidden moves. BMADX should read them when present and
use them as constraints, but they must not replace BMAD artifacts or
`_bmad-output/project-context.md`.

Best fit:
- `GUARDRAILS.md` captures failure lessons and hard constraints.
- BMAD captures requirements, architecture, workflow, and durable plan context.
- BMADX routes the work and decides when to escalate.

## Oracle Relationship

Oracle is a second-opinion layer. Use it when the card exposes uncertainty that
the current Codex session should not resolve alone:

- architecture ownership is unclear,
- several implementation paths look plausible,
- red-zone verification is weak,
- the user cannot judge the technical tradeoff,
- a stronger model with selected files can challenge the plan.

Oracle output is advisory. BMADX still owns routing discipline, BMAD still owns
process artifacts, and checks still own proof.
