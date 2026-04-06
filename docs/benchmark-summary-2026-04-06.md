# Benchmark Summary — 2026-04-06 (`BMADX v0.2.3`)

## Goal

Verify that `v0.2.3` improved the public adoption surface without losing BMADX’s
core routing discipline.

This rerun checked:
- English/public-facing skill wording
- tighter `X2` output shape
- portable benchmark artifacts
- no regression in BMAD-first routing semantics

## Artifacts

- [`../benchmark/summary-2026-04-06-healthy-bmad.json`](../benchmark/summary-2026-04-06-healthy-bmad.json)
- [`../benchmark/summary-2026-04-06-degraded-bmad.json`](../benchmark/summary-2026-04-06-degraded-bmad.json)
- raw logs in [`../benchmark/raw`](../benchmark/raw)

## Healthy

Core `X1..X4`:
- `X1`: `7762` tokens, `3` lines, `287` chars, `format_pass=true`
- `X2`: `5286` tokens, `9` lines, `811` chars, `format_pass=true`
- `X3`: `8023` tokens, `routing_pass=true`
- `X4`: `8634` tokens, `routing_pass=true`
- core average: `7426.25`

Boundary:
- `X2/X3`: still escalates correctly to `X3`

## Degraded

Core `X1..X4`:
- `X1`: `5068` tokens, `format_pass=true`
- `X2`: `8283` tokens, `format_pass=true`
- `X3`: `4534` tokens, correct classification under degraded BMAD
- `X4`: `5469` tokens, correct classification under degraded BMAD
- core average: `5838.5`

Boundary:
- `X2/X3`: still escalates correctly to `X3`

## Reading

What `v0.2.3` clearly improved:
- public-facing BMADX is now portable and English-first
- `X2` finally fits the mixed-metric format gate in both profiles
- both profiles pass core `format`, `token`, `reference_budget`, and `routing` validation
- BMADX remains dramatically lighter than the historical OMX baseline

What this does not mean:
- BMADX has not replaced BMAD
- the comparison is still directional, not perfectly symmetric
- the strongest public claim remains “lighter than OMX, BMAD-first, easier day-to-day than raw BMAD,” not “BMADX beats BMAD”
