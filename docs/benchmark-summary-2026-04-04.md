# Benchmark Summary — 2026-04-04 (`BMAD vs BMADX vs OMX`)

## Goal

Establish the first comparative baseline between:
- raw `BMAD`
- `BMADX`
- `OMX`

The benchmark focused on routing-style `X1..X4` scenarios.

## Main result

The first comparison showed:
- `BMAD` as the cheapest raw baseline
- `BMADX` as materially lighter than `OMX`
- `OMX` as the heaviest runtime in this sample

Historical averages:
- `BMAD`: `7237.5`
- `BMADX`: `10954.75`
- `OMX`: `25540.5`

## What this implied at the time

The repo's initial reading was:
- BMADX was not yet cheap enough in the simple cases
- the real problem was not the gear model itself, but the dependency gate
- `X4/FUBAR` was already a strong differentiator
- BMADX needed to get quieter and cheaper on `X1/X2`

## Why this benchmark still matters

This benchmark remains important because it captures the original public
positioning:
- BMADX should not try to out-BMAD BMAD
- BMADX should be lighter than OMX
- BMADX needs to justify itself on operator friction, not just process purity

## Follow-up

The current repo state supersedes this first result with `v0.2.1`, `v0.2.2`,
and `v0.2.3`
reruns, but this file remains the historical baseline for:
- the first `BMAD vs BMADX vs OMX` comparison
- the original justification for softening the dependency gate
- the first evidence that BMADX's strongest differentiator was `X4/FUBAR`
