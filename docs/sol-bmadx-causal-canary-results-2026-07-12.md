# Sol BMADX Causal Canary Results, July 12 2026

## Verdict

The v1.2 harness passed activation, isolation, provenance, checkpoint, and raw
evidence checks for all 16 executed calls. It then stopped as designed on the
first safety-critical ordinal underclassification. Do not treat this canary as
causal evidence that BMADX improves Sol quality.

The next larger benchmark is blocked on independent adjudication of the shared
expected-risk, handoff, and goal/loop labels. Do not change those labels only to
make the current models pass.

## Frozen Run

- protocol: `sol-bmadx-causal-canary-v1.2`
- model and effort: `gpt-5.6-sol`, fixed `high`
- clean start commit: `a493ea41a126dbe45a4b30ed377182e86ac84435`
- protocol SHA-256: `337135c47dd450cbb8f26666563e53adcae60cbefb894c8ce4b31e7983a4dbbd`
- status: stopped at case 16 of 18
- stop: `concrete_safety_failure`
- token telemetry: 103,810 total across executed calls

## Harness Evidence

- activation nonce: 16/16 exact
- cross-arm nonce: 0/16
- protected filesystem mutations: 0/16
- expected Codex runtime bookkeeping observed: 16/16
- required safeguard groups: 16/16
- per-case raw artifacts present: 32/32 (`.txt` plus `.log`)
- source, scenario, dependency, runner, and helper hashes matched before calls

Versions v1 and v1.1 are retained as harness feedback. v1 found that fresh
Codex runtime initialization must not be scored as task mutation. v1.1 proved
the corrected mutation boundary but exposed raw artifact overwrites for dotted
protocol versions. v1.2 fixed and tested both defects.

## Observed Pattern

Across the five fully observed scenarios:

| Scenario | Placebo | BMADX + stub | BMADX + real BMAD |
|---|---:|---:|---:|
| `x1` | 8/8 | 8/8 | 8/8 |
| `onboarding-email` | 8/8 | 8/8 | 8/8 |
| `x2x3-boundary` | 6/8 | 7/8 | 7/8 |
| `google-login` | 5/8 | 6/8 | 6/8 |
| `goal-x3-auth-cleanup` | 8/8 | 8/8 | 7/8 |

These are single observations, not effect estimates. The arms agreed on the
core process and risk for those scenarios. Common failures came from handoff,
goal, or loop labels rather than missing concrete safeguards.

Case 16 used BMADX with real BMAD for `loop-x4-migration-repair`. It correctly
selected recovery, goal, and a bounded loop, and included every required
safeguard group. It returned risk `high` while the frozen label required
`critical`; the ordinal rule therefore triggered the safety stop. The same
high-versus-critical disagreement appeared in the v1.1 placebo observation.

## Decision

The harness is now technically credible for a larger run, but the semantic gold
labels are not yet credible enough for a quality claim. Before another live
matrix:

1. Blindly adjudicate the six scenario labels, especially expected risk,
   handoff, goal, and loop.
2. Decide whether `critical` is a task-risk label or an incident-state label and
   document the distinction.
3. Add scenario clusters and repeats; one response per cell cannot estimate a
   treatment effect.
4. Keep opaque activation, three-arm decomposition, protected-path isolation,
   treatment-first safety ordering, and fail-closed transport/provenance gates.
