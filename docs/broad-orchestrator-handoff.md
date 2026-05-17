# Broad Orchestrator Handoff

BMADX is the narrow Codex-first lane. Sometimes a task is broad enough that an
external or private orchestration system should take over.

This document defines the public handoff contract. It works with broad
orchestration models such as Gastown-style multi-model workflows, team-specific
review systems, or private arbitration stacks. BMADX does not ship or depend on
those systems.

## Core Rule

BMADX classifies and gates. A broad orchestrator may take over only after an
explicit handoff.

Handoff is not `X5`. `X4/FUBAR` remains Rescue Mode, not automatic broad
orchestration.

## When BMADX Should Stay Narrow

| Case | BMADX mode | Handoff |
| --- | --- | --- |
| Typo, copy, tiny local fix | `X1` | no |
| Bounded product/code change | `X2` | no |
| Red-zone work with clear BMAD artifacts and proof path | `X3` | no by default |
| Messy repo needing Codex/BMAD scaffold only | `X4` | no by default |

## When BMADX Should Recommend Handoff

Recommend broad handoff when the task is not just risky, but broad,
judgment-heavy, privacy-sensitive, long-context, or multi-system.

Common triggers:
- architecture ownership is unclear,
- proof path is unclear after BMADX/Codex checks,
- large logs, long documents, or many repo areas must be compared,
- multiple plausible architectures need independent critique,
- the user explicitly asks for multi-model review or broad orchestration,
- the task may publish a public artifact under the operator or organization name,
- production, migration, rollout, data-loss, or rollback uncertainty remains.

Red zone does not automatically mean broad handoff. For example, an auth change
with a clear BMAD story, clear owner, and clear verification path can stay
`X3` in BMADX.

## What BMADX May Export

BMADX may export:
- gear classification,
- BMAD gate state,
- red-zone flags,
- privacy guess,
- reversibility guess,
- hard-stop candidates,
- proof required,
- forbidden changes,
- open questions,
- BMAD artifact references.

BMADX must not export:
- worker lane choices,
- model names,
- Opus or other arbiter assignment,
- dispatch commands,
- MCP/hooks/plugins/subagent setup,
- persistent run IDs,
- runtime state.

## Minimal Packet

```json
{
  "schema_version": "bmadx_handoff.v1",
  "origin": "bmadx",
  "task_summary": "Add Google login without breaking existing auth.",
  "gear": "X3",
  "bmad_gate_status": "allowed",
  "handoff_recommended": true,
  "handoff_reason_codes": [
    "architecture_ownership_unclear",
    "red_zone_auth",
    "proof_path_unclear"
  ],
  "red_zone_flags": [
    "auth",
    "external_api_integration",
    "user_data_privacy"
  ],
  "privacy_guess": "internal",
  "reversibility_guess": "unknown",
  "proof_required": [
    "auth flow tests",
    "session/callback verification",
    "rollback plan"
  ],
  "forbidden_changes": [
    "no production deploy",
    "no secret creation or rotation",
    "no OAuth app creation without operator approval"
  ],
  "open_questions": [
    "Which auth system owns login/session state?",
    "What proof would convince a non-technical owner this is safe?"
  ]
}
```

The packet is advisory. The receiving orchestrator must re-check privacy,
hard-stop risks, and execution permissions under its own policy.

## Public Positioning

BMADX works well with broad orchestration systems because it exports a small
risk-and-proof packet instead of trying to become the orchestrator.

In plain language:
- BMADX decides whether the task is small, bounded, BMAD-heavy, or rescue-shaped.
- A broad orchestrator decides whether to use multiple models, critics,
  arbitration, or long-context review.
- BMAD remains the process source of truth.
