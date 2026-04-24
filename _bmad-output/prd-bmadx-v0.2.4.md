# PRD — BMADX v0.2.4

## Goal

Tune BMADX for Codex on GPT-5.5 while preserving the existing BMAD-first routing
contract.

## Product goals

- make GPT-5.5 the BMADX target/default for repo tooling and benchmark runs
- keep the installer from mutating global Codex configuration
- reduce prompt scaffolding for simple work while keeping explicit boundaries
- prove the change with model-aware benchmark artifacts

## Scope

- update skill, manifest, docs, and BMAD source-of-truth surfaces to `v0.2.4`
- make the benchmark runner accept `--model` and `--reasoning`
- prevent GPT-5.4 and GPT-5.5 benchmark artifacts from overwriting each other
- rerun BMADX healthy/degraded benchmarks on GPT-5.5 and a healthy comparison on GPT-5.4

## Success criteria

- GPT-5.5 healthy average improves on the `v0.2.3` healthy baseline of `7426.25`
- `X1/X2` keep format, token, routing, and reference-budget discipline
- `X3/X4` preserve BMAD-first execution semantics
- no new runtime state, no second plan store, and no normalizing of `X4/FUBAR`
