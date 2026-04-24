# Benchmark Summary — 2026-04-24 (`BMADX v0.2.4`, GPT-5.5)

## Goal

Verify that `BMADX v0.2.4` is tuned for Codex on GPT-5.5 without changing the
core routing contract: BMAD remains the source of truth, BMADX stays lighter
than OMX, and Rescue Mode (`X4/FUBAR`) remains rare.

This is a Codex benchmark, not an API availability claim for GPT-5.5.

## Runner

- runner: [`benchmark/scripts/run_bmadx_benchmark.py`](../benchmark/scripts/run_bmadx_benchmark.py)
- reasoning effort: `medium`
- MCP startup: `no servers`
- Codex CLI: `0.124.0`
- benchmark runs isolate local user config, disable plugin/app startup surfaces, and use model-aware artifact names

## Artifacts

- [`../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json)
- raw logs in [`../benchmark/raw`](../benchmark/raw)

## GPT-5.5 Healthy

Core `X1..X4`:
- `X1`: `5682` tokens, `3` lines, `213` chars
- `X2`: `5607` tokens, `8` lines, `514` chars
- `X3`: `8240` tokens, correct BMAD-heavy routing
- `X4`: `5679` tokens, correct Rescue Mode routing
- core average: `6302.0`

Validation:
- `format_pass=true` for all core cases
- `token_pass=true` for all core cases
- `reference_budget_pass=true` for all core cases
- `routing_pass=true` for all core and boundary cases
- `overreach_pass=true` for all core and boundary cases
- boundary `X2/X3` escalated to `X3`

## GPT-5.5 Degraded

Core `X1..X4`:
- `X1`: `13833` tokens, correct fast-path classification
- `X2`: `10212` tokens, correct bounded-work classification
- `X3`: `5786` tokens, `execution_allowed=false` under unhealthy BMAD
- `X4`: `5843` tokens, `execution_allowed=false` under unhealthy BMAD
- core average: `8918.5`

Reading:
- degraded is the safety/regression profile, not the primary ergonomics gate
- the important degraded result is that `X3/X4` preserve hard-gate semantics
- `X1/X2` still avoid reference reads and preserve routing, but token budgets are not the release claim here

## GPT-5.4 Healthy Comparison

Same runner, same date, same reasoning effort:
- `GPT-5.4 healthy`: `12370.75` average tokens
- `GPT-5.5 healthy`: `6302.0` average tokens
- delta: `-49.1%` versus the same fresh GPT-5.4 runner profile

Compared with the `v0.2.3` healthy baseline:
- `v0.2.3 healthy`: `7426.25` average tokens
- `v0.2.4 GPT-5.5 healthy`: `6302.0` average tokens
- delta: `-15.1%`

## What This Proves

- GPT-5.5 is a better Codex target for the current BMADX contract.
- The optimized benchmark prompt and isolated runner reduce waste without weakening routing.
- `X1/X2` stay compact in the healthy path.
- `X3/X4` keep BMAD-first semantics and do not become default modes.

## What This Does Not Prove

- It does not prove BMADX replaces BMAD.
- It does not prove GPT-5.5 is a stable public API default.
- It does not claim degraded BMAD is cheaper than healthy BMAD; degraded exists to test safety behavior.
- It does not make Rescue Mode (`X4/FUBAR`) the default path.
