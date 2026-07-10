# PRD — BMADX v0.3

## Summary

BMADX v0.3 makes the Codex-first routing layer capability-aware for GPT-5.6
Sol, Terra, and Luna without turning model selection into a second router.

The release exists because the previous GPT-5.5 assumptions were embedded in
installer copy, thinking validation, benchmark defaults, and performance claim
grouping. GPT-5.6 introduces asymmetric profiles and new reasoning levels, so a
single hardcoded model contract is no longer credible.

## User

Primary user: a solo operator who relies on BMADX to decide how much process,
verification, and BMAD ceremony an AI coding task needs.

Secondary user: a future Codex/Sol agent continuing BMADX development with
medium or high reasoning and limited historical context.

## Goals

- Support GPT-5.6 Sol, Terra, and Luna as explicit candidate profiles.
- Keep gear classification and BMAD execution permission model-independent.
- Recommend only reasoning levels supported by the active model.
- Prevent cross-model benchmark and performance-claim contamination.
- Make Codex CLI compatibility failures diagnosable before a task starts.
- Make goal/loop guidance terminate safely on success, bounded exhaustion,
  approval, hard stop, or human review.
- Leave a concise, current handoff for subsequent agents.

## Non-Goals

- No automatic model switching.
- No public claim that GPT-5.6 profiles are validated before repeated runs.
- No default use of `max` or `ultra`.
- No weakening of the `X3/X4` BMAD gate.
- No full OMX-style runtime, worker dispatch, or second plan store.
- No global Codex config mutation.

## Functional Requirements

### FR1 — Compatibility preflight

BMADX must report the installed Codex CLI version, presence of Sol/Terra/Luna in
the local model catalog, supported reasoning efforts, profile drift, and a clear
candidate/validated distinction without exposing credentials.

### FR2 — Model-aware advisor

After gear classification, BMADX may map the gear to a model-specific reasoning
effort. This mapping must not change the gear or BMAD gate.

### FR3 — Explicit benchmark identity

Every benchmark run must name a model explicitly. Raw and summary artifacts
must carry that identity, profile policy, reasoning policy, group scope, and
repeat index.

### FR4 — Per-model verification

Coverage and fixed/advisor comparisons must be evaluated independently for each
model. Different model families must never form a claim pair.

### FR5 — Safe goal and loop contract

Goal recommendations must state a measurable proof and blocked stop condition.
Repair loops must state a numeric maximum and termination criteria. Interactive
slash commands and headless natural-language goal creation must be documented
as different surfaces.

### FR6 — Portable Codex home

Benchmark auth metadata and BMAD dependency discovery must honor `CODEX_HOME`.

### FR7 — Agent continuation

The repo must contain a current audit, architecture, execution plan, and project
context that identify completed work, blocked work, exact verification, and
release gates.

## Acceptance Criteria

- Codex CLI `0.144.0+` compatibility check passes for all three GPT-5.6 model
  catalogs on a compatible installation.
- Sol accepts `ultra`; Terra accepts `ultra`; Luna rejects `ultra` before a live
  benchmark call.
- `max/ultra` parse as valid runtime efforts but are not advisor defaults.
- Sol maps `X4` to `high`; Terra/Luna map `X4` to `xhigh`.
- benchmark parser requires explicit `--model`.
- claim verifier never pairs different models.
- custom `CODEX_HOME` is used for source auth metadata and BMAD dependency.
- unbounded goal/loop examples fail deterministic validation.
- all local tests and CI pass.
- no GPT-5.6 support promotion appears before repeated benchmark evidence.

## Release Evidence

Required evidence is defined in `docs/bmadx-v0.3-plan.md`. Compatibility code
may merge before live model promotion, but public support status must remain
`candidate` until the evidence matrix passes.
