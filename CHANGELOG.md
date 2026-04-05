# Changelog

All notable changes to this repository will be documented here.

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
