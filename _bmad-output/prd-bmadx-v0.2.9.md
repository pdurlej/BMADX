# PRD — BMADX v0.2.9

## Summary

`v0.2.9` prepares BMADX for full GPT-5.5 performance baselines that can be
approved mechanically. It follows the `v0.2.8` canary, which proved the runner
works but blocked full baseline publication because token caps failed.

This release keeps routing semantics unchanged.

## Goals

- Reduce hidden activation cost by shrinking `SKILL.md` to the core BMADX
  contract.
- Move execution-surface, model-experiment, and platform-drift details into
  references.
- Add a performance verifier that can approve or reject canary/full benchmark
  summaries without manual interpretation.
- Keep baseline approval separate from public token-savings claims.

## Non-Goals

- No gate relaxation.
- No public savings claim unless claim verification passes.
- No PMAX X or local-model baseline.
- No Claude Code adapter.
- No change to `sync_bmadx.py` execution semantics.

## Acceptance Criteria

- `SKILL.md` stays focused on activation-path routing, compact gate, response
  contract, thinking budget, and Rescue Mode.
- `verify_bmadx_performance.py` exits non-zero for the failed `v0.2.8` canary
  summaries.
- Baseline verification requires token and duration presence, routing pass,
  token pass, reference-budget pass, thinking-budget pass, handoff-drift pass,
  expected profile/policy coverage, group scope, and repeat count.
- Claim verification additionally requires advisor metrics to improve or hold
  fixed-medium metrics.
- Full baseline runs only after canary passes.

