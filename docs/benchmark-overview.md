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

Use these artifacts:
- [`../benchmark/summary-2026-04-04.json`](../benchmark/summary-2026-04-04.json)
- [`../benchmark/summary-2026-04-06-healthy-bmad.json`](../benchmark/summary-2026-04-06-healthy-bmad.json)
- [`../benchmark/summary-2026-04-06-degraded-bmad.json`](../benchmark/summary-2026-04-06-degraded-bmad.json)

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

## Best public reading today

- BMADX looks clearly better than OMX as a lighter tactical layer
- BMAD remains the upstream process owner and still wins on raw authority
- BMADX’s `healthy` average is now directionally close to the historical BMAD baseline while staying far below the historical OMX baseline
- BMADX is strongest as a low-friction layer for people who want guardrails without a heavy runtime
