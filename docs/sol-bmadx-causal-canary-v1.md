# Sol BMADX Causal Canary v1

Status: protocol frozen before execution.

The canonical machine-readable protocol is
`benchmark/protocols/sol-bmadx-causal-canary-v1.json`.

## Purpose

This 18-call canary validates treatment activation, dependency decomposition,
filesystem isolation, provenance, checkpointing, and stop conditions before a
larger causal benchmark. It is not powered for a quality or statistical claim.

## Design

- model: `gpt-5.6-sol`
- effort: fixed `high`
- scenarios: six frozen task shapes
- repeats: one
- arms: opaque placebo workflow, BMADX with deterministic healthy no-op BMAD,
  and BMADX with real BMAD pinned by tree hash and release tag `v6.10.0`
- order: pre-generated from seed `560713`
- prompt: identical except for a unique opaque workflow alias and task text
- manipulation check: a unique 128-bit nonce exists only inside the assigned
  alias skill and must be returned as an unscored field
- isolation: fresh snapshot, runtime home, and workspace per call
- dependency check: a deterministic minimal state prevents BMAD `check` from
  treating the fixture as a first-run refresh and mutating pinned references
- freeze anchors: scenario, BMADX, real BMAD, runner, and scoring-contract
  hashes plus the clean checkout commit recorded in the result

## Stop Conditions

Stop immediately on activation failure, a nonce belonging to another arm,
runtime/provenance mismatch, filesystem mutation, transport failure, or a
concrete safeguard failure in a safety-critical scenario.

## Interpretation

Canary success means the harness is eligible for a larger held-out experiment.
It does not prove BMADX or BMAD quality. A later quality benchmark requires
independent scenario adjudication and scenario-cluster analysis.
