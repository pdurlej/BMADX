# BMADX v0.3 GPT-5.6 Plan

Status: `v0.3.1` compatibility release complete; repeated promotion evidence
pending.

## Objective

Make BMADX capability-aware for GPT-5.6 Sol, Terra, and Luna while preserving
the invariants that make the project useful:

- `BMAD > BMADX`,
- model profile never changes the selected gear,
- `X1/X2` remain light,
- `X3/X4` keep the BMAD hard execution gate,
- `X4` stays rare,
- no runtime-orchestrator drift.

## Phase 0 — Audit and Environment

Status: complete.

- upgrade Codex CLI from `0.143.0` to `0.144.1`,
- verify Sol/Terra/Luna in the local model catalog,
- diagnose and remediate BMAD dependency drift that blocked `X3/X4`,
- record findings in `audit-2026-07-10-gpt56.md`.

## Phase 1 — Deterministic Compatibility

Status: complete.

- add `model-profiles.json` as BMADX policy data,
- add local compatibility checker,
- require explicit benchmark `--model`,
- honor custom `CODEX_HOME`,
- make advisor reasoning model-aware,
- recognize `max/ultra` without recommending them by default,
- isolate performance coverage and claims per model,
- require bounded goal loops and blocked stop conditions,
- update installer, skill, and public docs,
- add CI.

Acceptance:

- all local tests pass,
- compatibility checker passes on CLI `0.144.1`,
- unknown/OSS models remain benchmarkable without false first-party claims,
- historical GPT-5.5 summaries remain readable.

## Phase 2 — Canary Gate

Status: complete on 2026-07-10 under live operator approval.

Run one repeat only:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-sol --profile healthy --reasoning-policy advisor --groups core,boundary,goal_loop --repeat 1
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-terra --profile healthy --reasoning-policy advisor --groups core,boundary --repeat 1
python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.6-luna --profile healthy --reasoning-policy advisor --groups core,boundary,non_technical --repeat 1
```

Canary pass requires:

- 100% selected-gear routing,
- auth/billing/data/migration tasks at `X3` minimum,
- no ordinary-work `X4` false positives,
- compact `X1/X2`,
- no reference reads on obvious `X1/X2`,
- expected model-aware `Thinking:` values,
- bounded goal/loop output with blocked stop conditions,
- no runtime/handoff drift.

Stop the phase after the first safety-critical under-escalation. Diagnose before
spending more quota.

Result:

- Sol: baseline pass on `core,boundary,goal_loop` after one policy clarification
  made goal and loop selection explicitly independent; final run retains
  `X1/X2` total-token cap warnings,
- Terra: baseline pass on `core,boundary`,
- Luna: baseline pass on `core,boundary,non_technical`, with total-token cap
  warnings in four light cases,
- no safety-critical under-escalation and no ordinary-work `X4` false positive.

## Phase 3 — Full Evidence Matrix

Status: ready, pending explicit quota approval for the larger matrix.

For each model that passes its canary:

- healthy: fixed + advisor, repeat `3`, all groups,
- degraded: fixed + advisor, repeat `2`, all groups,
- verify baseline mode with explicit `--require-model`,
- run claim mode only within the same model,
- write a dated summary; do not overwrite GPT-5.5 history.

Promotion targets:

- Sol: full `X1..X4`, red-zone, Rescue, goal/loop, final synthesis candidate,
- Terra: `X1/X2` plus bounded `X3` candidate,
- Luna: `X1/X2` candidate first; `X3/X4` remain unpromoted unless all red-zone
  gates pass.

## Phase 4 — Release Decision

Status: compatibility release complete; model promotion remains blocked on
Phase 3.

Release only when:

- deterministic suite and CI pass,
- all claimed model scopes have repeated evidence,
- BMAD dependency is healthy for hard-gate runs,
- docs distinguish compatibility, candidate, validated, and default,
- no token/cost claim is made unless same-model claim verification passes,
- public version, manifest, changelog, and project context agree.

Release decision: `v0.3.0` delivered the compatibility surface and `v0.3.1`
isolated its deterministic CI fixture from operator-global state. Sol, Terra,
and Luna remain `candidate`; neither release makes a token, latency, cost, or
default-model claim.

## Handoff for the next evidence run

Start on `high`, not `max/ultra`.

1. Read `_bmad-output/project-context.md`, the v0.3 PRD, architecture, and audit.
2. Re-run all deterministic tests and `check_codex_compat.py --require-gpt56`.
3. Inspect the diff for model-policy leakage into gear or BMAD gate logic.
4. Confirm global BMAD health before any `X3/X4` canary; do not weaken the gate.
5. Request operator approval before the repeated live model matrix because it
   consumes materially more quota than the completed canaries.
6. Run same-model fixed/advisor pairs for healthy and degraded profiles.
7. Stop on the first safety-critical failure and preserve dated evidence.

Do not create new planning files unless the decision no longer fits this plan.

## Post-release v0.3.2 Evidence

Status: implementation complete; value-study result inconclusive before
unblinding.

- Dependency gate repaired: compact `X3/X4` now performs a local read-only
  capability check. Release/reference drift and cache-write failures warn but
  do not block; stateful BMAD sync is operator-requested maintenance only.
- Sol `medium/high/xhigh` fixed-effort comparison completed across all groups,
  repeat `2`.
- Decision quality: `29/30`, `30/30`, `30/30` respectively.
- `high` is the default recommendation for consequential Sol planning;
  `xhigh` requires explicit complexity signals.
- Planning `max/ultra` uses a visible eight-signal rubric and operator
  confirmation; it remains provisional until planning-specific evidence.
- The first neutral plain-Sol control produced directional assigned-arm gains,
  but external review found fixture, activation, isolation, resume, and scorer
  limits. Its v1 summary is historical evidence, not causal proof.
- A/B runner v2 hardening is complete locally. The next live run must use an
  opaque activation check, independently adjudicated held-out scenarios, and a
  placebo/BMADX-only/BMADX+real-BMAD decomposition at `high` before effort work.
- The three-arm causal canary v1.2 executed 16/18 calls with 16/16 activation,
  zero protected-path mutations, and complete per-case evidence. It stopped on
  the frozen `critical` risk label after a recovery/high answer with complete
  safeguards. Independent label adjudication now blocks the larger live run.
- The replacement decision-value study v1 is pre-registered at 18 scenario
  clusters, three arms, three repeats, and 162 Sol/high calls. It uses blinded
  preference plus frozen quality/cost/safety gates instead of the project exact
  scorer. The revised 18-scenario manifest passed independent pre-run audit;
  generation v1 stopped at call 130 on malformed JSON. Protocol v1.1 restarts
  from zero with a frozen native output schema under operator-approved quota.
- Its review stage completed all 270 primary judgments and 55 order-stability
  judgments through a five-family Ollama Cloud panel in Pi. GLM 5.2 and
  Nemotron 3 Ultra missed the frozen `0.70` candidate-order stability gate, so
  the run remained blinded and supports no BMADX value-added claim. Synthetic
  evidence also remains insufficient for real novice learning or productivity
  claims.
