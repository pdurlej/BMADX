# Changelog

All notable changes to this repository will be documented here.

## [0.2.4] - 2026-04-24

### Added

- GPT-5.5 as the BMADX target/default for Codex-oriented tooling and benchmark runs
- model-aware benchmark output names so GPT-5.4 and GPT-5.5 runs do not overwrite each other
- benchmark overreach validation for stronger-model escalation discipline
- BMAD source-of-truth artifacts for the GPT-5.5 optimization release
- deterministic healthy BMAD release fixture for benchmark runs

### Changed

- updated public positioning around BMADX as a boundary and verification layer for stronger Codex models
- benchmark runner now accepts `--model` and `--reasoning`
- benchmark runner isolates local Codex config and disables plugin/app startup surfaces for stable model comparisons
- install-and-verify output now states that BMADX is tuned for GPT-5.5 without changing the user's Codex config

### Benchmarks

- GPT-5.5 healthy: `6302.0` average tokens, all core validation gates passed
- GPT-5.5 degraded: `8918.5` average tokens, X3/X4 hard-gate semantics preserved
- GPT-5.4 healthy comparison: `12370.75` average tokens

## [0.2.3] - 2026-04-06

### Added

- `START_HERE.md` and a new first-success onboarding path
- `scripts/install_and_verify_bmadx.py` as the primary public install wrapper
- prompt pack for Codex starter prompts
- plain-language chooser docs for BMAD vs BMADX vs OMX
- FAQ and Rescue Mode docs
- transcript-based proof surfaces for non-technical users

### Changed

- translated the public skill surface and public repo surfaces to English
- removed maintainer-local path leakage from portable runtime and public docs
- made remediation commands portable through `${CODEX_HOME:-$HOME/.codex}`
- added public-sample rendering mode for the sample `X4/FUBAR` bundle
- repositioned the public onboarding path around low-friction usage rather than smoke checks

## [0.2.2] - 2026-04-05

### Added

- shorter response contract for obvious `X1/X2`
- mixed-metric benchmark runner with `format_pass`, `token_pass`,
  `reference_budget_pass`, and `routing_pass`
- `healthy` and `degraded` benchmark profiles
- boundary scenario for `X2/X3`
- MIT license, English public docs, architecture diagram, and lightweight public repo surfaces
- installer for BMADX and a vibe-coder-oriented install path

### Changed

- public positioning of BMADX as a `BMAD-first` tactical overlay
- benchmark methodology from token-only to mixed-metric validation

## [0.2.1] - 2026-04-04

### Added

- fast path for `X1/X2`
- compact output mode for `sync_bmadx.py`
- benchmark runner for explicit `healthy` and `degraded` profiles
- BMAD-side project context and architecture artifacts under `_bmad-output`

### Changed

- split between classification and execution permission
- gear-aware gate behavior for `X1/X2` vs `X3/X4`

## [0.2.0] - 2026-04-04

### Added

- soft dependency gate for `X1/X2`
- cached last healthy BMAD state
- explicit `X4/FUBAR` tactical positioning

### Changed

- dependency gate no longer blocks all gears equally
- execution semantics for `X3/X4` align more clearly with BMAD-first behavior
