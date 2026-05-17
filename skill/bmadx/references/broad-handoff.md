# Broad Orchestrator Handoff

Use this reference when the task is too broad for BMADX's narrow Codex-first
lane but should not be executed directly by BMADX.

## Boundary

BMADX may recommend handoff. BMADX must not execute the broad orchestrator.

Handoff does not change the gear:
- `X3`, no handoff
- `X3`, handoff recommended
- `X4`, no handoff
- `X4`, handoff recommended

`X4/FUBAR` stays rare and rescue-shaped. Handoff is not `X5`.

## Stay in BMADX

Stay in BMADX when:
- `X1/X2` is obvious and compact,
- `X3` has clear BMAD artifacts, clear ownership, and clear proof path,
- `X4` needs only the Rescue Mode scaffold and Codex/BMAD execution discipline,
- the user asks for speed and the work is bounded.

## Recommend Broad Handoff

Recommend handoff when:
- architecture ownership is unclear,
- proof path is unclear,
- large context or many systems must be compared,
- multiple plausible architectures need independent critique,
- privacy or public-artifact risk needs a broader preflight,
- production, migration, rollout, rollback, or data-loss uncertainty remains,
- the user explicitly asks for broad orchestration, multi-model review, or
  second-model architecture judgment.

## Handoff Output Contract

For normal answers, use a short line:

```text
Handoff: yes — broad architecture review is useful because ownership and proof are unclear.
```

or:

```text
Handoff: no — BMADX/BMAD has enough scope and proof to proceed.
```

For explicit packet requests, emit JSON matching:

```text
skill/bmadx/assets/schemas/broad-handoff-packet.schema.json
```

## Forbidden in BMADX Handoff

Do not include:
- model names,
- worker lane choices,
- arbiter assignment,
- dispatch commands,
- MCP/hooks/plugins/subagent setup,
- persistent run IDs,
- runtime state.

BMADX exports risk and proof. The broad orchestrator owns orchestration.
