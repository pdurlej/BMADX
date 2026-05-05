# Architecture — BMADX v0.2.5

## Decision

`v0.2.5` keeps the `v0.2.4` runtime architecture and releases the public
non-technical guardrail stack as the current version.

## Stable Runtime Architecture

- `sync_bmadx.py check --gear ... --compact` remains the post-classification
  gate.
- `X1/X2` keep the compact fast path.
- `X3/X4` keep the BMAD hard gate.
- `X4/FUBAR` remains rare and bundle-oriented.

## Public Architecture Additions

- Architecture Guardrail Card is the default mental model for non-technical
  architecture risk.
- Red-zone escalation defaults route auth, billing, permissions, migrations,
  data deletion, secrets, production config, privacy, multi-tenant access,
  webhooks, encryption, admin roles, and compliance to `X3` minimum unless
  purely textual.
- Rescue Mode bundle includes Failure Patterns / Guardians.
- Benchmark runner includes non-technical scenarios and a plain-language
  `what_failed_why_it_matters` readout.

## Ecosystem Boundary

BMADX is the connective layer:

- Oracle: expert second opinion with selected files.
- BMAD: process and architecture source of truth.
- BMADX: lightest-safe-mode routing and verification discipline.
- Guardrails.md: repo-local safety constraints and repeated failure lessons.
- pyfallow: Python codebase intelligence.
- CI/tests/scanners: hard technical proof.

None of these companions replace BMAD process artifacts, and BMADX does not
become a runtime or plan store.
