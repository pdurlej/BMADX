# BMADX Benchmark Overview

## What this proves

The benchmark is useful for showing:
- BMADX is much lighter than OMX in this repo’s runs
- BMADX can stay compact for normal work while keeping BMAD-first boundaries
- BMADX can validate more than tokens alone through format, routing, and reference-budget checks
- BMADX can test non-technical red-zone routing, such as auth, billing, data deletion, and messy recovery tasks
- BMADX can detect whether broad-orchestrator handoff stays a small risk/proof packet instead of drifting into runtime orchestration
- BMADX can validate fit-for-purpose thinking-budget recommendations without treating them as routing decisions
- BMADX can validate goal-aware and bounded repair-loop contracts without turning them into runtime orchestration
- BMADX can measure token and latency baselines for fixed-medium reasoning vs advisor-selected reasoning

## What this does not prove

The benchmark does not prove:
- that BMADX is categorically better than BMAD
- that token counts equal user value
- that BMADX should replace plain Codex for trivial work
- that a single advisor-policy run proves public token savings
- that the July 16, 2026 synthetic value panel established BMADX value; two of
  five reviewers failed the frozen order-stability gate before unblinding

## Main benchmark surfaces

- historical `BMAD vs BMADX vs OMX` comparison from `2026-04-04`
- BMADX `healthy` rerun from `2026-04-06`
- BMADX `degraded` rerun from `2026-04-06`
- BMADX GPT-5.5 optimization rerun from `2026-04-24`
- BMADX GPT-5.5 performance canary from `2026-06-01`; full baseline was blocked by token-budget canary failures
- BMADX GPT-5.5 performance baseline from `2026-06-02`; automated baseline verification passed, but claim verification failed
- experimental Codex OSS-provider reruns for local models, if a local provider such as Ollama or LM Studio is installed
- the blinded GPT-5.6 Sol decision-value study from 2026-07-16; generation and
  all 325 panel judgments completed, but the result is inconclusive because the
  reviewer panel was unhealthy

Use these artifacts:
- [`../benchmark/summary-2026-04-04.json`](../benchmark/summary-2026-04-04.json)
- [`../benchmark/summary-2026-04-06-healthy-bmad.json`](../benchmark/summary-2026-04-06-healthy-bmad.json)
- [`../benchmark/summary-2026-04-06-degraded-bmad.json`](../benchmark/summary-2026-04-06-degraded-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json)
- [`../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json`](../benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json)
- [`../benchmark/summary-2026-06-01-gpt-5-5-healthy-fixed-core-boundary-bmadx.json`](../benchmark/summary-2026-06-01-gpt-5-5-healthy-fixed-core-boundary-bmadx.json)
- [`../benchmark/summary-2026-06-01-gpt-5-5-healthy-advisor-core-boundary-bmadx.json`](../benchmark/summary-2026-06-01-gpt-5-5-healthy-advisor-core-boundary-bmadx.json)
- [`benchmark-summary-2026-06-02-gpt55-performance.md`](benchmark-summary-2026-06-02-gpt55-performance.md)
- [`../benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json)
- [`../benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json`](../benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json)
- [`bmadx-value-study-results-2026-07-16.md`](bmadx-value-study-results-2026-07-16.md)
- [`../benchmark/value-study/results/panel-gate-v1.13.json`](../benchmark/value-study/results/panel-gate-v1.13.json)

Runner hardening after `v0.2.4`:
- benchmark runs now fail if `codex exec` does not report a `tokens used` footer
- validation summaries track `token_count_present_count` alongside `token_pass_count`
- summaries include explicit `validation_failures` lists so failed cases are visible without recomputing counters
- routing validation now checks the selected gear in the response contract instead of passing on incidental gear mentions
- future BMADX benchmark summaries use a `-bmadx.json` suffix; historical files keep their original names
- raw logs keep benchmark-relevant stderr while omitting analytics HTML noise
- future runner summaries include `non_technical_cases` plus a plain-language `what_failed_why_it_matters` readout
- runner summaries record whether the run used the primary Codex/OpenAI path or an experimental OSS local provider
- `v0.2.6` runner summaries include `handoff_cases` and runtime-drift checks that reject worker lanes, model names, dispatch commands, MCP, hooks, plugins, subagents, and runtime state
- `v0.2.7` runner validation can parse `Thinking:` lines, compare them with expected reasoning effort, and reject global Codex config mutation language
- `v0.2.8` runner summaries include per-case `duration_seconds`, reasoning policy, repeat index, token/latency performance aggregates, and optional explicit operator-provided cost estimates
- `v0.2.8` raw and summary artifact names include reasoning policy and group scope so canary runs do not overwrite full baselines
- `v0.2.9` adds `benchmark/scripts/verify_bmadx_performance.py` so full baselines are approved by the same gates instead of manual inspection
- `v0.2.9` adds `--gate-mode precomputed|in-session`; the performance baseline uses `precomputed` so the harness validates compact gates without adding in-session tool-call variance
- `v0.2.9` verifier baseline mode reports token cap overages as warnings; `claim` mode remains strict before any public savings claim
- `v0.3.0` strengthens `goal_loop_cases` with independent goal/loop selection,
  blocked stop conditions, and numeric bounds for review/repair/validate loops

## Thinking budget validation

The benchmark can now ask BMADX to include a compact line such as:

```text
Thinking: high — suggestion only.
```

Expected defaults:

| Scenario shape | Expected thinking |
| --- | --- |
| `X1` tiny local work | `medium` |
| `X2` bounded normal work | `medium` |
| `X2/X3` boundary | `high` |
| `X3` red-zone or BMAD-heavy work | `high` |
| `X4` Rescue Mode execution | `xhigh` |

This is advisory. The benchmark must not treat higher thinking as permission to
skip BMAD, and it must not accept answers that tell users to mutate global Codex
config as part of normal BMADX routing.

## Goal and loop validation

The benchmark can ask BMADX to include compact goal and loop lines:

```text
Goal: yes — use `/goal` because the work needs a persistent definition of done.
Loop: yes — max 3 review/repair/validate passes; stop on pass, stale delta, hard stop, or human review.
```

Expected defaults:

| Scenario shape | Expected goal | Expected loop |
| --- | --- | --- |
| obvious `X1/X2` | no | no |
| multi-turn `X3` with proof criteria | yes | usually no |
| `X4` rescue execution with repeated validation deltas | yes | yes |

Goal and loop validation must not accept answers that create hooks, MCP,
plugins, subagents, worker lanes, dispatch commands, persistent run IDs,
runtime state, or a second plan store.

## GPT-5.5 performance baseline

`v0.2.9` measures two policies:

| Policy | Meaning |
| --- | --- |
| `fixed` | use one CLI `--reasoning` value for every case, normally `medium` |
| `advisor` | use the scenario's expected thinking budget: `X1=medium`, `X2=medium`, `X3=high`, `X4=xhigh` |

The recommended performance path uses `--gate-mode precomputed`. The benchmark
harness now records the model's classification first and only then runs the
compact gate against the model-selected route. No route-conditioned gate report
is injected before classification. Historical precomputed artifacts generated
before 2026-07-12 are contract-conformance evidence, not independently blinded
routing evidence.

Canary runs:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py \
  --model gpt-5.5 \
  --profile healthy \
  --reasoning medium \
  --reasoning-policy fixed \
  --gate-mode precomputed \
  --groups core,boundary \
  --repeat 1 \
  --date-stamp 2026-06-02

python3 benchmark/scripts/run_bmadx_benchmark.py \
  --model gpt-5.5 \
  --profile healthy \
  --reasoning-policy advisor \
  --gate-mode precomputed \
  --groups core,boundary \
  --repeat 1 \
  --date-stamp 2026-06-02
```

Full baseline runs:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile healthy --reasoning medium --reasoning-policy fixed --gate-mode precomputed --repeat 3 --date-stamp 2026-06-02
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile healthy --reasoning-policy advisor --gate-mode precomputed --repeat 3 --date-stamp 2026-06-02
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile degraded --reasoning medium --reasoning-policy fixed --gate-mode precomputed --repeat 2 --date-stamp 2026-06-02
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile degraded --reasoning-policy advisor --gate-mode precomputed --repeat 2 --date-stamp 2026-06-02
```

Reporting rule:

This is a baseline, not a public savings claim. Do not update README with token
savings language unless repeated healthy and degraded runs preserve routing,
red-zone safety, `X4` rarity, compact `X1/X2`, reference budget, and
thinking-budget validation.

## Performance verifier

Use the verifier after canary or full runs:

```bash
python3 benchmark/scripts/verify_bmadx_performance.py \
  benchmark/summary-2026-06-02-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-healthy-advisor-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-degraded-fixed-precomputed-all-bmadx.json \
  benchmark/summary-2026-06-02-gpt-5-5-degraded-advisor-precomputed-all-bmadx.json \
  --require-model gpt-5.5 \
  --require-profiles healthy,degraded \
  --require-policies fixed,advisor \
  --require-gate-mode precomputed \
  --require-group-slug all \
  --min-repeat 2
```

`baseline` mode exits `0` only when the safety and validation gates pass.
Token cap overages are reported as warnings in baseline mode, because current
Codex/GPT-5.5 token accounting showed run-to-run variance even for compact
`X1` responses. Use `--token-cap-mode strict` or `--mode claim` when token caps
must be hard gates.

`claim` mode additionally requires advisor metrics to improve or hold fixed
metrics for total tokens, average tokens, average latency, p95 latency, and max
latency. Use `claim` mode before writing any public savings claim:

```bash
python3 benchmark/scripts/verify_bmadx_performance.py \
  <same summaries> \
  --mode claim \
  --require-model gpt-5.5 \
  --require-profiles healthy,degraded \
  --require-policies fixed,advisor \
  --require-group-slug all \
  --min-repeat 2
```

## Model and provider experiments

The benchmark runner has no implicit model default. Every run must pass
`--model` so artifacts and claims cannot drift silently. GPT-5.5 remains the
validated historical baseline; GPT-5.6 Sol, Terra, and Luna are candidate
profiles described in [GPT-5.6 Model Compatibility](gpt56-model-compatibility.md).

Local-model experiments use Codex OSS providers and are explicitly exploratory.
For example, after installing a Mistral-family model in Ollama, run:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py \
  --oss \
  --local-provider ollama \
  --model mistral \
  --profile healthy \
  --date-stamp 2026-05-05
```

Read these results as model-behavior experiments, not release claims. A local
model has to pass the same format, routing, red-zone escalation, reference
budget, and `X4` rarity checks before it is useful for BMADX’s non-technical
builder promise.

## Non-technical routing scenarios

The runner now includes a dedicated non-technical scenario group:

| Scenario | Expected routing | Why it matters |
| --- | --- | --- |
| pricing-page copy | `X1` | copy-only work should stay tiny |
| onboarding email variant | `X2` | bounded product work should stay compact |
| Google login | `X3` | auth is red-zone work |
| subscription billing change | `X3` | billing and permissions need BMAD grounding |
| delete inactive users | `X3` | destructive data work needs architecture and proof |
| failed migration recovery | `X4` | messy ownership plus rollback risk needs Rescue Mode |

These are not a new claim that BMADX beats every adjacent tool. They test the
core non-technical promise: small work stays small, red-zone work escalates, and
Rescue Mode appears only when the situation is actually rescue-shaped.

## Broad handoff scenarios

The runner now includes a small handoff scenario group:

| Scenario | Expected routing | Expected handoff | Why it matters |
| --- | --- | --- | --- |
| auth architecture review | `X3` | yes | unclear auth ownership may deserve broad review, but it is not Rescue Mode by default |
| migration recovery review | `X4` | yes | rollback uncertainty and long-context recovery can justify external broad orchestration |

These cases do not benchmark an external orchestrator. They only verify that
BMADX can say “handoff useful” without naming models, workers, arbiters, hooks,
MCP, plugins, subagents, dispatch commands, or runtime state.

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
