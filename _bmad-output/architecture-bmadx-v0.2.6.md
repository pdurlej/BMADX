# Architecture — BMADX v0.2.6

## Summary

`v0.2.6` keeps the existing Codex skill architecture and adds one boundary:
BMADX may produce a broad-orchestrator handoff packet, but it does not run,
configure, or own the receiving orchestrator.

## Stable Runtime Architecture

The BMADX runtime remains:
- `skill/bmadx/SKILL.md` for the Codex skill contract,
- `skill/bmadx/scripts/sync_bmadx.py` for BMAD dependency and gate checks,
- `skill/bmadx/references/*` for progressive-disclosure rules,
- `skill/bmadx/assets/templates/*` for `X4/FUBAR` bundle generation,
- `benchmark/scripts/run_bmadx_benchmark.py` for routing and response-shape
  validation.

No new runtime daemon, task store, hook, MCP server, plugin, or subagent
installer is introduced.

## Handoff Boundary

The handoff boundary is file/schema-based:
- schema: `skill/bmadx/assets/schemas/broad-handoff-packet.schema.json`
- skill reference: `skill/bmadx/references/broad-handoff.md`
- public docs: `docs/broad-orchestrator-handoff.md`
- samples: `samples/handoff/*.json`

BMADX may export:
- gear classification,
- BMAD gate status,
- red-zone flags,
- privacy and reversibility guesses,
- proof requirements,
- forbidden changes,
- open questions,
- BMAD artifact references.

BMADX must not export:
- worker lanes,
- model names,
- arbiters,
- dispatch commands,
- MCP/hooks/plugins/subagent setup,
- persistent run IDs,
- runtime state paths.

## Gear Semantics

- `X1`: stay tiny; no handoff unless the user explicitly asks for broad review.
- `X2`: stay bounded; one read-only helper may improve time-to-value when it
  answers an independent side question.
- `X3`: BMAD-heavy work; handoff may be recommended when architecture ownership,
  proof path, privacy, or multi-system context is unclear.
- `X4`: Rescue Mode; handoff may be recommended for long-context or
  judgment-heavy review, but `X4/FUBAR` remains BMADX's scaffold and is not
  replaced by broad orchestration.

## Benchmark Architecture

The benchmark runner now has a separate `handoff_cases` group. Those cases test:
- selected gear,
- expected `Handoff: yes/no`,
- absence of worker-lane language,
- absence of model-name language,
- absence of dispatch/runtime commands,
- absence of MCP/hooks/plugins/subagent leakage.

This keeps the benchmark focused on BMADX behavior rather than measuring any
external orchestrator.
