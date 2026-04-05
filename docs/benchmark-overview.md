# BMADX Benchmark Overview

This is the public-friendly benchmark summary for the repo.

If you want the raw historical artifacts, use:
- [`../benchmark/summary-2026-04-04.json`](../benchmark/summary-2026-04-04.json)
- [`../benchmark/summary-2026-04-05-healthy-bmad.json`](../benchmark/summary-2026-04-05-healthy-bmad.json)
- [`../benchmark/summary-2026-04-05-degraded-bmad.json`](../benchmark/summary-2026-04-05-degraded-bmad.json)

## What was benchmarked

The repo currently keeps three relevant benchmark surfaces:
- historical `BMAD vs BMADX vs OMX` comparison from `2026-04-04`
- `BMADX healthy` rerun after `v0.2.2`
- `BMADX degraded` rerun after `v0.2.2`

The benchmark is not perfectly symmetric, so it should be read carefully.

## Historical baseline

From `2026-04-04`:

- `BMAD`: average `7237.5` tokens
- `BMADX`: average `10954.75` tokens
- `OMX`: average `25540.5` tokens

Immediate reading:
- BMAD was the cheapest raw process baseline
- BMADX was much lighter than OMX
- OMX was the heaviest runtime in the comparison

## Current BMADX reruns

From `2026-04-05`:

### Healthy profile

- `X1`: `8630`
- `X2`: `8770`
- `X3`: `5385`
- `X4`: `10377`
- core average: `8290.5`

Validation:
- `format_pass=true` on all core cases
- `token_pass=true` on all core cases
- `reference_budget_pass=true` on all core cases
- `routing_pass=true` on all core cases

### Degraded profile

- `X1`: `5270`
- `X2`: `8768`
- `X3`: `8786`
- `X4`: `5387`
- core average: `7052.75`

Validation:
- all core cases still passed formatting, token budget, reference budget, and routing checks
- `X3/X4` kept the correct BMAD-first execution semantics under degraded dependency conditions

## What BMADX seems better at than OMX

In this repo's own benchmark framing, BMADX looks better than OMX in:
- raw operational cost
- lower ceremony
- lower runtime weight
- easier justification for pragmatic Codex usage

This is the strongest public positioning claim the repo can currently make.

## What BMAD still does better

BMAD still looks stronger as:
- the upstream process owner
- the native home for process-heavy work
- the cheaper raw option in several task categories

BMADX is valuable not because it replaces BMAD, but because it makes BMAD
easier to operate tactically inside Codex.

## Honest caveats

Do not oversell the numbers.

Important caveats:
- the `BMAD` and `OMX` numbers come from the historical `2026-04-04` run
- the `BMADX v0.2.2` numbers come from `2026-04-05` reruns
- the comparison is directionally useful, not a perfect lab-grade benchmark
- BMADX wins most clearly against OMX, not against BMAD

## Best current reading

The cleanest public reading is:
- BMADX beats OMX on lightweight tactical usability in these runs
- BMAD still beats BMADX on raw process authority and often on token cost
- BMADX is strongest as a lazy operational layer for vibe coders who still want
  guardrails
