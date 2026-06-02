# BMADX GPT-5.5 Performance Canary — 2026-06-01

This is a baseline, not a public savings claim.

`v0.2.8` added token and latency measurement for fixed-medium reasoning versus
advisor-selected reasoning. The first GPT-5.5 canary ran only the `core` and
`boundary` groups. Full healthy/degraded repeated baselines were not run because
the canary did not satisfy the existing token-budget gates.

## Run Scope

| Field | Value |
| --- | --- |
| Model | `gpt-5.5` |
| Profile | `healthy` |
| Groups | `core,boundary` |
| Repeat | `1` |
| Fixed policy | `--reasoning medium --reasoning-policy fixed` |
| Advisor policy | `--reasoning-policy advisor` |

Artifacts:

- [`../benchmark/summary-2026-06-01-gpt-5-5-healthy-fixed-core-boundary-bmadx.json`](../benchmark/summary-2026-06-01-gpt-5-5-healthy-fixed-core-boundary-bmadx.json)
- [`../benchmark/summary-2026-06-01-gpt-5-5-healthy-advisor-core-boundary-bmadx.json`](../benchmark/summary-2026-06-01-gpt-5-5-healthy-advisor-core-boundary-bmadx.json)

## Fixed Medium vs Advisor Canary

| Policy | Total tokens | Avg tokens | Min / max tokens | Avg latency | p50 latency | p95 latency | Max latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed | `49,762` | `9,952.4` | `5,017 / 12,739` | `6.724s` | `6.561s` | `8.228s` | `8.228s` |
| advisor | `53,105` | `10,621.0` | `6,532 / 19,125` | `11.272s` | `9.582s` | `24.238s` | `24.238s` |

## Validation Result

| Policy | Routing | Reference budget | Thinking budget | Token budget | Result |
| --- | --- | --- | --- | --- | --- |
| fixed | pass | pass | pass | fail: `X2` used `12,739` tokens | blocked |
| advisor | pass | pass | pass | fail: `X1` used `12,615` tokens | blocked |

The raw answers stayed compact and did not read reference docs in obvious
`X1/X2` cases. The failures are therefore hidden token-cost failures, not
response-shape failures.

## Healthy vs Degraded

No degraded full run was executed. The canary requirement is intentionally
strict: full healthy/degraded baselines should only run after both fixed and
advisor canaries pass token, routing, reference, and thinking-budget gates.

## What This Means

- The runner implementation is ready for repeated performance baselines.
- The first GPT-5.5 canary does not support a public savings claim.
- Advisor policy did not improve the canary aggregate on this run.
- The next improvement target is reducing hidden cost for obvious `X1/X2`
  without weakening red-zone routing or `X4` rarity.

