# Sol BMADX Causal Canary v1.2

Status: protocol frozen after v1.1 artifact-path feedback and before execution.

The canonical protocol is
`benchmark/protocols/sol-bmadx-causal-canary-v1.2.json`.

## Purpose

This 18-call canary validates activation, dependency decomposition, isolation,
per-case evidence retention, provenance, checkpointing, and stop conditions. It
is not powered for a quality or statistical claim.

## Delta From v1.1

Version 1.1 validated activation and experiment-surface isolation for 16 calls,
then stopped on a concrete safety underclassification in the placebo recovery
case. Its checkpoint is valid, but dotted protocol version text interacted with
`Path.with_suffix()`, causing per-case raw files to overwrite one another.

Version 1.2:

- constructs `.txt` and `.log` paths by explicit concatenation and tests dotted
  protocol IDs;
- uses new opaque aliases and nonces;
- keeps the scenario-stratified schedule;
- runs both BMADX treatment arms before placebo on safety-critical scenarios,
  so a placebo safety stop cannot hide treatment observations for that cell.

## Frozen Design

- model: `gpt-5.6-sol`
- effort: fixed `high`
- six scenarios, three arms, one repeat
- fresh prepared snapshot, runtime home, and workspace per call
- mutation stops protect workspace, assigned skill, and BMAD dependency
- Codex runtime bookkeeping is reported but not scored
- scenario, source, dependency, runner, helper, and clean-checkout hashes are
  recorded

## Stop Conditions

Stop immediately on activation failure, cross-arm nonce, provenance mismatch,
mutation of an experiment surface, transport failure, or concrete safeguard
failure in a safety-critical scenario.

## Interpretation

Canary success means the harness is eligible for a larger held-out experiment.
It does not prove BMADX or BMAD quality.
