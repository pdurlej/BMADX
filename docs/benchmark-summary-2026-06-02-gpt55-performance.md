# BMADX GPT-5.5 Performance Baseline — 2026-06-02

This is a measurement baseline, not a public savings claim.

The goal was to check whether BMADX `v0.2.9` can run GPT-5.5 performance
baselines with automated validation while preserving routing, red-zone safety,
`X4` rarity, compact `X1/X2` behavior, reference-budget discipline, thinking
budget validation, and handoff runtime-drift guards.

## Runner

| Field | Value |
| --- | --- |
| Model | `gpt-5.5` |
| Codex CLI | `0.134.0` in raw logs |
| Gate mode | `precomputed` |
| Healthy repeats | `3` |
| Degraded repeats | `2` |
| Groups | `core,boundary,non_technical,handoff` |

`precomputed` means the benchmark harness runs `sync_bmadx.py check --gear ...
--compact` before the Codex session and injects the compact report into the
prompt. This still validates the BMADX compact gate, but it does not make every
benchmark session pay for an in-session Python tool call.

## Autoverifier Result

Command:

```bash
python3 benchmark/scripts/verify_bmadx_performance.py \
  benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json \
  --require-profiles healthy,degraded \
  --require-policies fixed,advisor \
  --require-gate-mode precomputed \
  --require-group-slug all \
  --min-repeat 2 \
  --json
```

Result:

| Check | Result |
| --- | --- |
| Baseline | `pass` |
| Baseline failures | `0` |
| Claim | `fail` |
| Token cap warnings | present |

Interpretation:
- The run is valid as a baseline.
- It is not valid as a public token/latency savings claim.
- Advisor policy was slower and more expensive than fixed-medium in this run.
- Some `X1` total-token readings crossed the old `9000` cap despite compact
  output, correct routing, no reference reads, and no in-session tool calls.

## Aggregate Results

| Profile | Policy | Cases | Total tokens | Avg tokens | Min | Max | Avg sec | P50 sec | P95 sec | Max sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| healthy | fixed | 39 | 213169 | 5465.9 | 1753 | 9559 | 7.07 | 6.10 | 13.688 | 21.738 |
| healthy | advisor | 39 | 228347 | 5855.1 | 240 | 9974 | 9.47 | 8.677 | 14.305 | 15.784 |
| degraded | fixed | 26 | 128969 | 4960.3 | 1858 | 9605 | 8.06 | 7.096 | 13.309 | 20.109 |
| degraded | advisor | 26 | 141254 | 5432.8 | 1944 | 9780 | 10.95 | 9.769 | 16.581 | 28.381 |

## Token Warnings

The verifier now treats token caps as performance warnings in baseline mode and
as hard gates in claim mode. This is intentional: GPT-5.5/Codex token accounting
showed run-to-run variance even for the same compact `X1` contract.

Warnings in this baseline:

| Summary | Warning |
| --- | --- |
| healthy fixed | `X1` exceeded `9000` twice: `9386`, `9444` |
| healthy advisor | `X1` exceeded `9000` once: `9417`; pricing-copy exceeded three times: `9429`, `9412`, `9409` |
| degraded fixed | pricing-copy exceeded once: `9457` |
| degraded advisor | none |

## What This Proves

- BMADX `v0.2.9` can produce a full GPT-5.5 performance baseline that passes
  automated safety/shape/routing/reference/thinking/handoff validation.
- Precomputed gate mode is the correct benchmark path for measuring BMADX
  response/routing behavior without adding in-session tool-call variance.
- Fixed-medium remains the better measured policy for this suite.

## What This Does Not Prove

- It does not prove that advisor-selected reasoning saves tokens.
- It does not prove a public cost reduction claim.
- It does not prove that `X1 <= 9000` is a stable hard cap under current Codex
  token accounting.
- It does not change the product default: BMADX remains Codex-first and
  BMAD-first.

## Artifacts

- [`../benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json)
