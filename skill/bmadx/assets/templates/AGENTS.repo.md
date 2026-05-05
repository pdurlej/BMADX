# AGENTS.md for {{project_name}}

This repository uses `BMAD > BMADX`.

- BMAD remains the process system and workflow architecture.
- BMADX remains the operational routing layer for Codex.
- If routing is unclear, use `bmad-help` instead of inventing a parallel workflow.

## Routing

- `X1` — One-shot: tiny, local task.
- `X2` — Regular: short plan and standard verify.
- `X3` — Complex (BMAD): enter the real BMAD flow.
- `X4` — Rescue Mode (`X4/FUBAR`, BMAD+): scaffold bundle, rollout, verify matrix.

## Architecture Guardrail Card

Use these questions when a task might affect architecture, ownership, data, auth,
billing, or production behavior:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

For `X1/X2`, answer the card silently unless a red-zone signal appears. For
`X3/X4`, make the answers explicit and tie them back to BMAD artifacts.

## Red zones

Use `X3` minimum for auth, billing, payments, permissions, database migrations,
data deletion, secrets, production config, user data privacy, multi-tenant
access, encryption, webhooks, admin roles, or legal/compliance unless the change
is purely textual.

## Durable context

- Process and artifacts: BMAD.
- Technical memory: `_bmad-output/project-context.md`.
- Session-local notes are not source-of-truth.

## Verify before done

- Do not close work without evidence.
- For non-trivial changes, run review.
- If convenience conflicts with the process artifact, BMAD wins.
- If `GUARDRAILS.md` exists, treat it as repo-local safety constraints and do not rewrite it into a BMAD substitute.
- Use Oracle for second-opinion review when architecture ownership or red-zone risk is unclear.
- For Python repos, use `pyfallow` when available as a static architecture/codebase-intelligence check.

## Escalation

- If `X1` is not enough, move to `X2`.
- If the task needs BMAD artifacts, move to `X3`.
- If the repo needs scaffolding, ownership cleanup, or a rollout/verify layer, use `X4`.
- Do not render `X4/FUBAR` when `X2` or a normal `X3` is enough.

Generated: {{generated_at}}
Project path: {{project_path}}
