# GPT-5.6 Sol Reasoning Comparison - 2026-07-11

## Question

Does Sol make better BMADX decisions at `high` or `xhigh` than at `medium`,
and is `xhigh` measurably better than `high`?

This experiment measures decision quality under BMADX with a healthy BMAD
dependency. It does not measure implementation quality and does not isolate a
causal `plain Sol` versus `Sol + BMAD/BMADX` effect.

Retrospective validity note: the legacy `precomputed` gate included the expected
gear in the model prompt. These results therefore measure conformance after a
supplied route, not independently blinded routing quality. The neutral A/B on
[July 12](sol-bmadx-ab-2026-07-12.md) supersedes routing-quality conclusions.

## Protocol

- model: `gpt-5.6-sol`
- BMAD profile: `healthy`
- gate mode: `precomputed`
- policy: fixed `medium`, fixed `high`, fixed `xhigh`
- scope: all 15 scenarios in `core`, `boundary`, `non_technical`, `handoff`,
  and `goal_loop`
- repeats: `2`, producing 30 cases per effort
- quality excludes token caps and requires every routing, format, reference,
  thinking, handoff, goal/loop, and runtime-drift gate to pass

Artifacts:

- [medium summary](../benchmark/summary-2026-07-11-gpt-5-6-sol-healthy-fixed-precomputed-all-sol-medium-2026-07-11-bmadx.json)
- [high summary](../benchmark/summary-2026-07-11-gpt-5-6-sol-healthy-fixed-precomputed-all-sol-high-2026-07-11-bmadx.json)
- [xhigh summary](../benchmark/summary-2026-07-11-gpt-5-6-sol-healthy-fixed-precomputed-all-sol-xhigh-2026-07-11-bmadx.json)

## Results

| Effort | Perfect quality | Routing | Token-cap pass | Total tokens | Avg latency | P95 latency | Avg response chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `medium` | 29/30 | 29/30 | 30/30 | 144,720 | 6.821 s | 11.956 s | 385.0 |
| `high` | 30/30 | 30/30 | 27/30 | 231,194 | 6.245 s | 9.215 s | 366.5 |
| `xhigh` | 30/30 | 30/30 | 30/30 | 143,670 | 7.384 s | 11.949 s | 345.8 |

The `medium` failure was an over-escalation, not a safety under-escalation: in
repeat 2, the X3 auth-review handoff was classified as X4 Rescue Mode.

Pairwise deltas:

- `high` versus `medium`: one additional perfect case, `+59.75%` total tokens,
  `-8.45%` average latency, and `-22.93%` P95 latency.
- `xhigh` versus `high`: no quality gain, `-37.86%` total tokens, `+18.23%`
  average latency, and `+29.67%` P95 latency.
- `xhigh` versus `medium`: one additional perfect case, `-0.73%` total tokens,
  and `+8.25%` average latency.

## Decision

Use `high` as the Sol baseline for consequential BMADX planning. It removed the
observed medium-level precision error and was faster than `xhigh` in this run.

Do not default Sol planning to `xhigh`: it produced no additional validated
quality on this classification suite. Use it only when explicit task signals
justify more planning depth.

Do not infer that `xhigh` is cheaper from the token totals. The human-readable
Codex footer is a noisy all-token measure, the ordering is non-monotonic, and
two repeats are insufficient for a cost claim.

`max` and `ultra` were not part of this A/B. Their criteria in the Planning
Effort Advisor are conservative policy thresholds for future validation, not a
benchmark-proven quality advantage. `ultra` remains exceptional and requires
broad-decomposition pressure plus operator confirmation.

## Next Evidence

1. Repeat the three-effort matrix at least three more times to estimate
   variance.
2. Add an implementation benchmark with executable tests to measure code
   quality, not only decision quality.
3. Completed: run the neutral plain-Sol control in the
   [July 12 A/B](sol-bmadx-ab-2026-07-12.md).
4. Test `max/ultra` only on planning-heavy scenarios, not ordinary execution.
