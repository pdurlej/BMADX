# PRD — BMADX v0.2.8

## Summary

`v0.2.8` adds a GPT-5.5 performance benchmark baseline for BMADX. The release
measures fixed-medium reasoning against advisor-selected reasoning without
changing routing semantics and without making a public token-savings claim.

Primary question:

Does the Thinking Budget Advisor produce measurable token or latency differences
while preserving routing, red-zone escalation, `X4` rarity, compact `X1/X2`
behavior, and BMAD-first hard gates?

## Goals

- Keep GPT-5.5 as the only model in scope for this baseline.
- Compare `fixed` reasoning policy with `advisor` reasoning policy.
- Record token counts and latency per case.
- Support canary subsets and repeated full runs without artifact overwrites.
- Preserve existing validation for routing, format, token budget, reference
  budget, thinking budget, handoff drift, and degraded BMAD hard gates.
- Disable cost estimation unless an operator supplies explicit pricing.
- Publish results as a baseline, not as a savings claim.

## Non-Goals

- No PMAX X, Ollama, MiniMax, Mistral, Qwen, or other model comparison.
- No change to `sync_bmadx.py` gate semantics.
- No global Codex config mutation.
- No public savings claim from single-run data.
- No broader execution-surface adapter work.

## User Value

Non-technical builders need the agent to buy enough reasoning for risky work
without spending high-effort tokens on tiny tasks. `v0.2.8` tests whether BMADX
can measure that tradeoff honestly before turning it into product copy.

## Public Interface

Benchmark runner additions:

- `--reasoning-policy fixed|advisor`, default `fixed`
- `--groups core,boundary,non_technical,handoff`, default all groups
- `--repeat N`, default `1`
- `--cost-per-million-tokens`, optional explicit all-token cost estimate

Per-case output additions:

- `duration_seconds`
- `reasoning_policy`
- `repeat_index`

Summary additions:

- token aggregates: total, average, min, max
- latency aggregates: average, p50, p95, max
- performance summaries for all cases and each group
- optional cost estimate when explicitly configured

## Acceptance Criteria

- Canary runs pass before full runs.
- Every benchmark case records token count and duration.
- Core, boundary, non-technical, and handoff routing remain correct.
- Red-zone scenarios remain `X3` minimum unless purely textual.
- `X4` appears only for rescue-shaped scenarios.
- Obvious `X1/X2` cases keep reference-budget pass.
- Thinking-budget validation passes every case.
- No answer instructs editing global Codex configuration.
- Handoff cases do not leak model names, worker lanes, dispatch commands, MCP,
  hooks, plugins, subagents, or runtime state.
- Degraded profile preserves `X3/X4` hard-gate semantics.

## Reporting Rule

The generated benchmark doc must explicitly state:

> This is a baseline, not a public savings claim.

