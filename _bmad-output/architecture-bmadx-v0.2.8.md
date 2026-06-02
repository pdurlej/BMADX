# Architecture — BMADX v0.2.8

## Summary

`v0.2.8` extends the committed benchmark runner with performance measurement
controls. It does not change BMADX routing, compact gate semantics, BMAD
dependency checks, or the skill response contract.

## Data Flow

1. The runner parses model, profile, reasoning policy, group scope, and repeat
   count.
2. It creates a temporary `CODEX_HOME`.
3. It copies only BMADX and BMAD Method skill trees into that temporary home.
4. It warms BMADX against the selected BMAD dependency profile.
5. For each selected scenario and repeat index, it builds a classification-only
   prompt, runs `codex exec`, records latency, parses the token footer, validates
   the response, and writes raw text/log artifacts.
6. It writes one JSON summary for the run scope.

## Reasoning Policy

`fixed` policy:

- uses the CLI `--reasoning` value for every case.
- defaults to `medium`.

`advisor` policy:

- uses each scenario's `expected_reasoning_effort`.
- maps the current BMADX gear expectations as:
  - `X1=low`
  - `X2=medium`
  - `X2/X3 boundary=high`
  - `X3=high`
  - `X4=xhigh`

The advisor policy is scenario-driven. It does not let the model pick its own
reasoning effort during the benchmark.

## Artifact Naming

Raw artifacts include:

- model slug
- BMAD profile
- reasoning policy
- group slug
- repeat index
- scenario key

This prevents `core,boundary` canary runs from overwriting full-run raw files.

Summary artifacts include:

- date stamp
- model slug
- BMAD profile
- reasoning policy
- group slug

## Summary Aggregates

Each summary records performance aggregates for:

- all selected cases
- core cases
- boundary cases
- non-technical cases
- handoff cases

Aggregates include:

- case count
- total tokens
- average tokens
- min/max tokens
- average duration
- p50 duration
- p95 duration
- max duration

## Cost Estimate

Cost estimation is disabled by default. If the operator provides
`--cost-per-million-tokens` or `BMADX_BENCHMARK_COST_PER_MILLION_TOKENS`, the
runner emits an explicit all-token estimate with a note that Codex token footers
do not split input and output tokens.

No public docs should hardcode pricing as truth.

## Invariants

- `BMAD > BMADX`
- GPT-5.5 is the only model in scope for this baseline.
- `sync_bmadx.py` gate semantics stay unchanged.
- `X1/X2` remain compact and reference-light.
- `X3/X4` keep hard-gate behavior under degraded BMAD.
- `X4` remains rare and rescue-shaped.
- Handoff remains a packet/schema signal, not runtime orchestration.
- Benchmark output is a baseline until repeated runs prove safety and stability.

