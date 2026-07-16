# Project Context — BMADX v0.3.2-dev

## Product Boundary

BMAD is the process and architecture source of truth. BMADX is the lightweight
Codex routing, gate, thinking-advice, verification, and rare Rescue Mode layer.

Non-negotiable:

- `BMAD > BMADX`,
- `X1..X4` stays model-independent,
- model capability never bypasses a BMAD gate,
- `X4/FUBAR` stays rare,
- no second plan store or broad runtime platform.

## Active Artifacts

- PRD: `_bmad-output/prd-bmadx-v0.3.md`
- Architecture: `_bmad-output/architecture-bmadx-v0.3.md`
- Audit: `docs/audit-2026-07-10-gpt56.md`
- Execution plan: `docs/bmadx-v0.3-plan.md`
- Model guide: `docs/gpt56-model-compatibility.md`
- Sol reasoning evidence: `docs/sol-reasoning-comparison-2026-07-11.md`

Historical v0.2 artifacts remain evidence, not current instructions.

## Current State

Done:

- Codex CLI upgraded to `0.144.1`; GPT-5.6 minimum is `0.144.0`.
- Local catalog exposes Sol, Terra, and Luna with expected reasoning levels.
- Public release remains `v0.3.1`; main development is `v0.3.2-dev`.
- Shared model profile policy and compatibility checker added.
- Benchmark model is explicit and advisor output is model-aware.
- Performance claims and required coverage are isolated per model.
- Benchmark source discovery honors `CODEX_HOME`.
- Goal recommendations require blocked stop conditions; loops require bounds.
- Installer/docs/skill surfaces describe GPT-5.6 candidates.
- Deterministic CI added.
- Global BMAD synchronized to upstream `v6.10.0`; the live X3 hard gate passes.
- Subscription-backed healthy canaries pass baseline verification for Sol,
  Terra, and Luna.
- Sol fixed-effort evidence: `medium=29/30`, `high=30/30`, `xhigh=30/30` on
  decision quality across all groups with two repeats.
- Criteria-based planning-effort advisor added with visible `Y/8` evidence and
  model caps.

Blocked/pending:

- no GPT-5.6 profile is promoted until repeated healthy/degraded evidence.
- Sol and Luna retain total-token cap warnings in light canary cases; Terra's
  canary has none.

## Model Policy

| Model | Status | `X1` | `X2` | `X3` | `X4` |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | validated historical baseline | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Sol | candidate | `medium` | `medium` | `high` | `high` |
| GPT-5.6 Terra | candidate | `medium` | `medium` | `high` | `xhigh` |
| GPT-5.6 Luna | candidate | `medium` | `medium` | `high` | `xhigh` |

`max/ultra` are recognized runtime values but not BMADX defaults. Luna does not
expose `ultra` in the observed Codex `0.144.1` catalog.

## Goal and Loop Policy

- interactive clients interpret `/goal`,
- `codex exec` requires an explicit natural-language request to create a goal,
- BMADX recommendation alone does not create a goal,
- goal completion includes success, bounded exhaustion, approval/hard-stop
  blocking, and human review,
- goal and loop decisions are independent; multi-turn goal work does not imply
  repeated repair,
- repair loops carry only remaining delta and stop after bounded attempts.

## Immediate Next Work

1. Keep the published `v0.3.x` compatibility scope distinct from model
   promotion.
2. Add a plain-Sol control before claiming causal BMAD/BMADX quality uplift.
3. Add executable implementation tasks before claiming code-quality uplift.
4. Validate planning `max/ultra` only on planning-heavy scenarios.
5. Investigate Sol/Luna total-token stability before recommending efficiency
   gains for light work.
6. Use same-model claim verification before writing any performance claim.

## Verify

```bash
python3 scripts/test_install_bmadx.py
python3 scripts/test_install_and_verify_bmadx.py
python3 skill/bmadx/scripts/test_advise_planning_effort.py
python3 skill/bmadx/scripts/test_check_codex_compat.py
python3 skill/bmadx/scripts/test_sync_bmadx.py
python3 benchmark/scripts/test_handoff_packet_schema.py
python3 benchmark/scripts/test_run_bmadx_benchmark.py
python3 benchmark/scripts/test_verify_bmadx_performance.py
python3 skill/bmadx/scripts/check_codex_compat.py --json --require-gpt56
python3 skill/bmadx/scripts/sync_bmadx.py check --gear X2 --compact
python3 skill/bmadx/scripts/sync_bmadx.py check --gear X3 --compact
```

## Handoff Capsule

- Current state: `v0.3.2-dev` planning advisor and Sol reasoning evidence implemented locally.
- Done: audit, model policy, checker, runner/verifier hardening, docs, CI, BMAD sync, canaries, Sol medium/high/xhigh comparison.
- Next: plain-Sol control, implementation-quality tasks, and planning-specific max/ultra evidence.
- Active approvals: none persisted; live-thread approval is not reusable.
- Hard stops: do not weaken `X3/X4`, mutate global model config, or publish performance/default-model claims.
- Rollback: revert the release commit and restore global skill backups from `/private/tmp`.
- Secrets/access cleanup: checker emits no auth data; benchmark temp homes self-delete.
