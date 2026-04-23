# Project Context — BMADX v0.2.4

## Scope

This repo develops `BMADX` as the operational and tactical layer on top of `BMAD`.

Non-negotiable rule:
- `BMAD > BMADX`

## Active program

Current release focus:
- tune BMADX for Codex on GPT-5.5 without changing core routing semantics,
- make BMADX genuinely usable for non-technical, low-friction Codex users,
- keep BMAD as the process owner,
- make public install, activation, and proof surfaces portable and easier to trust,
- keep `X4/FUBAR` valuable without making it normal.

Out of scope:
- porting OMX,
- adding a second durable plan store,
- turning BMADX into a runtime platform.

## Active BMAD artifacts

- PRD: `_bmad-output/prd-bmadx-v0.2.4.md`
- Architecture: `_bmad-output/architecture-bmadx-v0.2.4.md`

## Model target

- target Codex model: `gpt-5.5`
- default benchmark reasoning: `medium`
- BMADX does not mutate global Codex config; users choose their model outside BMADX
- stronger models reduce prompt scaffolding, but do not bypass `BMAD > BMADX`

## Routing contract

### X1/X2

- classify first,
- then run `sync_bmadx.py check --gear X1|X2 --compact`,
- use the cached healthy BMAD state when available,
- warn instead of blocking when there is no fresh healthy BMAD snapshot,
- keep the response compact in the obvious happy path.

### X3/X4

- classify first,
- then run `sync_bmadx.py check --gear X3|X4 --compact`,
- keep the BMAD-first hard execution gate,
- if blocked, communicate correct classification plus lack of execution permission,
- remediation points to `sync_bmad_method.py check --json` and `sync`.

## Public productization goals

- English public docs and skill surfaces
- no maintainer-local path leakage
- install that ends in a first real task, not in smoke checks
- transcript-based proof for non-technical users
- portable public sample bundle for `X4/FUBAR`

## Benchmark context

- runner: `benchmark/scripts/run_bmadx_benchmark.py`
- profiles: `healthy`, `degraded`
- mixed metrics: token budget, response format, routing, reference-read budget
- model-aware artifacts use the model slug in raw and summary file names
- historical baselines:
  - `benchmark/summary-2026-04-04.json`
  - `benchmark/summary-2026-04-05-healthy-bmad.json`
  - `benchmark/summary-2026-04-05-degraded-bmad.json`
  - `benchmark/summary-2026-04-06-healthy-bmad.json`
  - `benchmark/summary-2026-04-06-degraded-bmad.json`

## Adjacent methods decision memo — 2026-04-12

Top 3 ideas to borrow now:
- `Aider`: context thrift and clearer lightweight/heavier mode discipline for `X1/X2`
- `Goose`: reusable launch surfaces, recipe-like prompt packs, and stronger onboarding reuse
- `superpowers`: activation UX and clearer first-run framing, but only as packaging

Top 3 ideas to explicitly not copy:
- `Task Master`: any BMADX-owned task store or project-management state
- `superpowers`: mandatory workflow, worktree-first behavior, and methodology takeover
- `GitHub Agentic Workflows`: repository-automation-first product posture

Best-fit mapping:
- `X1/X2`: `Aider`, then limited `Task Master` inspiration for thin "what next?" guidance
- onboarding / public UX: `Goose`, then `superpowers`
- governance / automation: `GitHub Agentic Workflows`, then `OneRedOak`
- `X4` / Rescue Mode: `superpowers` for packaging clarity, `OneRedOak` for narrow specialized adjuncts

Near-term BMADX implication:
- likely release candidate: onboarding and `X1/X2` ergonomics only
- later exploration: governance helpers, safe-output automation, and any review-adjacent adjuncts
- not a release candidate: new runtime state, new plan ownership, or making `X4` normal

## Verify

- `python3 skill/bmadx/scripts/test_sync_bmadx.py`
- `python3 scripts/test_install_bmadx.py`
- `python3 scripts/test_install_and_verify_bmadx.py`
- `python3 benchmark/scripts/test_run_bmadx_benchmark.py`
- `python3 skill/bmadx/scripts/sync_bmadx.py check --json`
- `python3 skill/bmadx/scripts/render_fubar_bundle.py --project-name BMADX --project-path "$PWD" --output-dir samples/fubar-bundle --include-architect --public-sample`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile healthy --date-stamp 2026-04-06`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile degraded --date-stamp 2026-04-06`
