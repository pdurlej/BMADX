# Sol BMADX Causal Canary v1.1

Status: protocol frozen after v1 harness feedback and before execution.

The canonical machine-readable protocol is
`benchmark/protocols/sol-bmadx-causal-canary-v1.1.json`.

## Purpose

This 18-call canary validates treatment activation, dependency decomposition,
experiment-surface isolation, provenance, checkpointing, and stop conditions.
It is not powered for a quality or statistical claim.

## Delta From v1

The v1 canary stopped after one healthy model response because a fresh Codex
runtime initializes system skills, model cache, local SQLite files, and config.
The workspace and assigned workflow/dependency skills were unchanged.

Version 1.1 therefore treats only these paths as experiment mutation surfaces:

- the fresh task workspace;
- the assigned opaque workflow skill;
- the BMAD dependency skill, when present.

Codex runtime-home bookkeeping is still hashed and reported, but it is not a
stop condition. New aliases and nonces prevent reuse of the v1 manipulation
proofs. The schedule is scenario-stratified, with arm order shuffled by seed
`560714`, so all three arms first prove activation on non-critical scenarios.

## Frozen Design

- model: `gpt-5.6-sol`
- effort: fixed `high`
- scenarios: six frozen task shapes
- repeats: one
- arms: opaque placebo workflow, BMADX with deterministic healthy no-op BMAD,
  and BMADX with real BMAD pinned by tree hash and release tag `v6.10.0`
- prompt: identical except for a unique opaque workflow alias and task text
- manipulation check: unique 128-bit nonce visible only in the assigned skill
- isolation: fresh prepared snapshot, runtime home, and workspace per call
- freeze anchors: scenario, source, dependency, runner, and helper hashes plus
  the clean checkout commit recorded in the result

## Stop Conditions

Stop immediately on activation failure, a nonce belonging to another arm,
runtime/provenance mismatch, mutation of an experiment surface, transport
failure, or a concrete safeguard failure in a safety-critical scenario.

## Interpretation

Canary success means the harness is eligible for a larger held-out experiment.
It does not prove BMADX or BMAD quality. A later quality benchmark requires
independent scenario adjudication and scenario-cluster analysis.
