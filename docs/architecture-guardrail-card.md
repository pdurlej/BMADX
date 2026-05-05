# Architecture Guardrail Card

BMADX is for people who understand the product problem better than the software
architecture. The Architecture Guardrail Card gives Codex five simple questions
that reduce the chance of putting code in the wrong place, skipping risky
dependencies, or pretending a change is safer than it is.

## The five questions

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

You usually do not answer these manually. BMADX should answer them silently for
normal work and only ask when the answer changes the safe mode.

## Defaults by mode

| Mode | Default |
| --- | --- |
| `X1` tiny fix | No questions. BMADX silently checks that this is low-risk. |
| `X2` normal bounded change | Short plan and verification. BMADX surfaces only the key tradeoff. |
| `X3` BMAD-heavy work | The card becomes explicit and must tie back to BMAD artifacts. |
| `X4/FUBAR` Rescue Mode | The card goes into the bundle with owners, failure patterns, guardians, and proof. |

## When this becomes BMAD

Use `X3` minimum when the task touches:

- auth, login, sessions, OAuth, SSO
- billing, payments, subscriptions, refunds
- permissions, admin roles, multi-tenant access
- database migrations, destructive data changes, data deletion
- secrets, tokens, production config
- user data privacy, compliance, encryption, webhooks, external side effects

Use `X4/FUBAR` only when the work is also messy: unclear ownership, repeated
failures, incident recovery, risky rollout, or no credible verification path.

## Clarifying-question UX

If BMADX needs more information, it should ask at most three concise questions.
When Codex exposes the structured question UI, use it with the safest option
first and a free-form `Other` option.

Good question shapes:

- Scope: `Small local change` / `Touches architecture` / `Not sure`
- Risk: `No red zone` / `Auth, billing, or data` / `Production or deployment`
- Proof: `Local tests/build` / `Needs BMAD artifact` / `Needs human review`

The goal is less manual process thinking, not more ceremony.

## When to ask Oracle

Use Oracle as a second-opinion companion when the card exposes an expert gap:

- ownership is unclear and the repo is large,
- several architecture options look plausible,
- a red-zone change has no obvious proof path,
- the builder cannot tell whether the implementation plan is safe,
- a review from a stronger model with selected files would reduce risk.

Oracle advice is still advisory. BMADX should route the work, BMAD should own
the process artifact, and verification should prove the accepted path.

## Example

Prompt:

```text
Add Google login to the app.
```

BMADX should not treat this as a quick UI task. Even if the prompt sounds small,
it touches auth, sessions, callbacks, user identity, and security boundaries.
The safe default is `X3`: enter BMAD, ground the change in architecture/story
artifacts, and require verification beyond “the button appears”.
