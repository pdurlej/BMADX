# Architecture — BMADX v0.2.9

## Summary

`v0.2.9` changes the benchmark approval path, not BMADX routing. The release
adds a smaller skill activation surface and a deterministic performance
verifier for benchmark summaries.

## Skill Surface

`SKILL.md` now contains only:

- BMAD-first contract
- compact gate flow
- gearbox summary
- red-zone escalation
- Architecture Guardrail Card
- Thinking Budget map
- response contracts
- Rescue Mode entry
- short handoff/helper boundaries
- verification pointers

Longer strategy and adapter details live in references, especially
`references/execution-boundaries.md`.

## Verifier

`benchmark/scripts/verify_bmadx_performance.py` reads one or more benchmark
summary JSON files.

Baseline mode checks:

- required model
- required profiles and reasoning policies
- required group slug
- minimum repeat count
- token count presence
- duration presence
- format pass
- token pass and explicit `X1/X2` token caps
- reference-budget pass
- routing and overreach pass
- thinking-budget pass
- no global Codex config mutation language
- handoff runtime-drift checks
- empty `validation_failures`

Claim mode additionally compares advisor summaries against fixed summaries for:

- total tokens
- average tokens
- average duration
- p95 duration
- max duration

Advisor must improve or hold every metric before public savings language is
allowed.

## Full Baseline Flow

1. Run fixed canary on `core,boundary`.
2. Run advisor canary on `core,boundary`.
3. Verify both canaries in baseline mode.
4. Only if canary passes, run full healthy/degraded summaries.
5. Verify full summaries in baseline mode.
6. Run claim mode only before writing public savings claims.

## Invariants

- `BMAD > BMADX`
- no second plan store
- no runtime platform
- no relaxed token gates
- no `X4` normalization
- no red-zone under-escalation

