# Project Context — BMADX v0.2.3

## Scope

This repo develops `BMADX` as the operational and tactical layer on top of `BMAD`.

Non-negotiable rule:
- `BMAD > BMADX`

## Active program

Current release focus:
- make BMADX genuinely usable for non-technical, low-friction Codex users,
- keep BMAD as the process owner,
- make public install, activation, and proof surfaces portable and easier to trust,
- keep `X4/FUBAR` valuable without making it normal.

Out of scope:
- porting OMX,
- adding a second durable plan store,
- turning BMADX into a runtime platform.

## Active BMAD artifacts

- PRD: `_bmad-output/prd-bmadx-v0.2.3.md`
- Architecture: `_bmad-output/architecture-bmadx-v0.2.3.md`

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
- historical baselines:
  - `benchmark/summary-2026-04-04.json`
  - `benchmark/summary-2026-04-05-healthy-bmad.json`
  - `benchmark/summary-2026-04-05-degraded-bmad.json`
  - `benchmark/summary-2026-04-06-healthy-bmad.json`
  - `benchmark/summary-2026-04-06-degraded-bmad.json`

## Verify

- `python3 skill/bmadx/scripts/test_sync_bmadx.py`
- `python3 scripts/test_install_bmadx.py`
- `python3 scripts/test_install_and_verify_bmadx.py`
- `python3 benchmark/scripts/test_run_bmadx_benchmark.py`
- `python3 skill/bmadx/scripts/sync_bmadx.py check --json`
- `python3 skill/bmadx/scripts/render_fubar_bundle.py --project-name BMADX --project-path "$PWD" --output-dir samples/fubar-bundle --include-architect --public-sample`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile healthy --date-stamp 2026-04-06`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile degraded --date-stamp 2026-04-06`
