# BMADX Benchmark Overview

## What this proves

The benchmark is useful for showing:
- BMADX is much lighter than OMX in this repo’s runs
- BMADX can stay compact for normal work while keeping BMAD-first boundaries
- BMADX can validate more than tokens alone through format, routing, and reference-budget checks

## What this does not prove

The benchmark does not prove:
- that BMADX is categorically better than BMAD
- that token counts equal user value
- that BMADX should replace plain Codex for trivial work

## Main benchmark surfaces

- historical `BMAD vs BMADX vs OMX` comparison from `2026-04-04`
- BMADX `healthy` rerun from `2026-04-06`
- BMADX `degraded` rerun from `2026-04-06`
- BMADX GPT-5.5 optimization rerun from `2026-04-24`

Use these artifacts:
- [`../benchmark/summary-2026-04-04.json`](../benchmark/summary-2026-04-04.json)
- [`../benchmark/summary-2026-04-06-healthy-bmad.json`](../benchmark/summary-2026-04-06-healthy-bmad.json)
- [`../benchmark/summary-2026-04-06-degraded-bmad.json`](../benchmark/summary-2026-04-06-degraded-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json)

## Historical baseline

From `2026-04-04`:
- `BMAD`: average `7237.5` tokens
- `BMADX`: average `10954.75` tokens
- `OMX`: average `25540.5` tokens

Directional reading:
- BMAD was the cheapest raw process baseline
- BMADX was much lighter than OMX
- OMX was the heaviest runtime in the comparison

## BMADX reruns after the public adoption sprint

From `2026-04-06`:

### Healthy profile

- `X1`: `7762`
- `X2`: `5286`
- `X3`: `8023`
- `X4`: `8634`
- core average: `7426.25`

Validation:
- `format_pass=true`
- `token_pass=true`
- `reference_budget_pass=true`
- `routing_pass=true`

### Degraded profile

- `X1`: `5068`
- `X2`: `8283`
- `X3`: `4534`
- `X4`: `5469`
- core average: `5838.5`

Validation:
- core cases still passed formatting, token budget, reference budget, and routing checks
- `X3/X4` kept the correct BMAD-first execution semantics under degraded dependency conditions

## BMADX GPT-5.5 optimization reruns

From `2026-04-24`:

### GPT-5.5 healthy profile

- `X1`: `5682`
- `X2`: `5607`
- `X3`: `8240`
- `X4`: `5679`
- core average: `6302.0`

Validation:
- core cases passed `format`, `token`, `reference_budget`, `routing`, and `overreach`
- boundary `X2/X3` escalated correctly to `X3`
- `X3/X4` returned `execution_allowed=true` with healthy BMAD

### GPT-5.5 degraded profile

- `X1`: `13833`
- `X2`: `10212`
- `X3`: `5786`
- `X4`: `5843`
- core average: `8918.5`

Validation:
- `X3/X4` preserved hard-gate semantics with `execution_allowed=false`
- `X1/X2` remained classified correctly and did not read reference docs
- token budgets are not treated as the primary ergonomics gate for degraded BMAD

### GPT-5.4 healthy comparison

- core average: `12370.75`
- GPT-5.5 healthy was `49.1%` lower than the same runner profile on GPT-5.4
- GPT-5.5 healthy was `15.1%` lower than the `v0.2.3` healthy baseline of `7426.25`

## Best public reading today

- BMADX looks clearly better than OMX as a lighter tactical layer
- BMAD remains the upstream process owner and still wins on raw authority
- BMADX’s GPT-5.5 `healthy` average is now below the `v0.2.3` healthy baseline and far below the historical OMX baseline
- BMADX is strongest as a low-friction layer for people who want guardrails without a heavy runtime
