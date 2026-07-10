# GPT-5.6 Sol, Terra, and Luna Compatibility

Status: released compatibility candidates; first healthy canaries passed,
benchmark promotion pending.

BMADX main now profiles all three GPT-5.6 Codex models without changing its
core rule: model capability may change the recommended reasoning effort, but it
does not change `X1..X4`, BMAD ownership, or the compact execution gate.

## Prerequisite

OpenAI requires Codex CLI `0.144.0` or newer, or ChatGPT desktop/Codex mode
`26.707.30751` or newer, for GPT-5.6. Update and verify the CLI path:

```bash
codex update
codex --version
python3 skill/bmadx/scripts/check_codex_compat.py --json --require-gpt56
```

The compatibility checker reads the local Codex model catalog and emits only
model capability metadata. It does not read or print credentials and does not
change Codex configuration.

Official references:

- [GPT-5.6 availability in ChatGPT and Codex](https://help.openai.com/en/articles/20001354)
- [GPT-5.6 Preview System Card](https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf)

## BMADX Profile Matrix

| Model | Product shape | BMADX status | Suggested `X1/X2` | Suggested `X3` | Suggested `X4` |
| --- | --- | --- | --- | --- | --- |
| Sol | most capable | candidate | `medium` | `high` | `high` |
| Terra | balanced capability, speed, and cost | candidate | `medium` | `high` | `xhigh` |
| Luna | fastest and lowest cost | candidate | `medium` | `high` | `xhigh` |

The Sol `X4=high` choice is intentional. The current Codex catalog recommends
starting Sol at lower effort, so BMADX should test whether `high` closes Rescue
Mode work before paying the latency and quota cost of `xhigh`. This is a test
policy, not a savings claim.

Terra and Luna keep `xhigh` for `X4` because they are smaller profiles. Luna is
the strongest candidate for cheap `X1/X2`, but its `X3/X4` behavior must not be
promoted before red-zone and overwrite-safety benchmarks pass.

## Supported Reasoning Levels

- Sol: `low`, `medium`, `high`, `xhigh`, `max`, `ultra`
- Terra: `low`, `medium`, `high`, `xhigh`, `max`, `ultra`
- Luna: `low`, `medium`, `high`, `xhigh`, `max`

BMADX accepts `max` and `ultra` as real Codex values but does not recommend
them automatically. In the current catalog, `ultra` includes automatic task
delegation. Making it a default would quietly turn thinking advice into an
orchestration decision, which is outside BMADX scope.

## What "Compatible" Means

Compatible means:

- the CLI can expose the model and its reasoning levels,
- the installer and benchmark runner no longer hardcode GPT-5.5,
- model-specific reasoning advice can be validated,
- benchmark summaries and claims remain isolated per model.

It does not yet mean that Sol, Terra, or Luna is a validated BMADX default.
That requires repeated healthy and degraded runs with zero red-zone
under-escalation and no ordinary-work `X4` false positives.

## 2026-07-10 Canary Evidence

| Model | Canary scope | Baseline | Notes |
| --- | --- | --- | --- |
| Sol | `core,boundary,goal_loop` | pass | `X1/X2` total-token cap warnings remain |
| Terra | `core,boundary` | pass | no validation or token-cap warnings |
| Luna | `core,boundary,non_technical` | pass | total-token cap warnings remain for four light cases |

Artifacts:

- [Sol summary](../benchmark/summary-2026-07-10-gpt-5-6-sol-healthy-advisor-precomputed-core-boundary-goal-loop-bmadx.json)
- [Terra summary](../benchmark/summary-2026-07-10-gpt-5-6-terra-healthy-advisor-precomputed-core-boundary-bmadx.json)
- [Luna summary](../benchmark/summary-2026-07-10-gpt-5-6-luna-healthy-advisor-precomputed-core-boundary-non-technical-bmadx.json)

These are one-repeat healthy canaries. They prove account entitlement and the
claimed compatibility surface on this environment, but they are not the
repeated healthy/degraded matrix required for promotion or performance claims.

## Benchmark Entry Commands

Start with canaries, not full matrix runs:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-sol --profile healthy --reasoning-policy advisor --groups core,boundary,goal_loop --repeat 1
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-terra --profile healthy --reasoning-policy advisor --groups core,boundary --repeat 1
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-luna --profile healthy --reasoning-policy advisor --groups core,boundary,non_technical --repeat 1
```

These commands consume Codex model quota. The first canaries passed; run the
full matrix only with operator approval for the additional spend.
