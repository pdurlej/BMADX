# Changelog

All notable changes to this repository will be documented here.

## [Unreleased]

### Fixed

- Replaced the stateful BMAD dependency invocation in the compact gate with a
  local read-only capability check, so sandboxed `X3/X4` tasks no longer fail
  because BMAD tried to write under `~/.codex`.
- BMAD release/reference drift and unwritable cache state are now nonblocking,
  convergent warnings; only a missing or structurally unusable dependency
  blocks execution.
- Removed automatic BMAD `check`/`sync` remediation from task startup and made
  installer verification exercise the read-only `X3` gate.

## [0.3.1] - 2026-07-10

### Fixed

- Isolated the benchmark skill-copy test from the operator's installed
  `CODEX_HOME`, so deterministic CI passes on clean GitHub runners.

## [0.3.0] - 2026-07-10

### Added

- GPT-5.6 Sol, Terra, and Luna model profiles with local Codex catalog
  compatibility diagnostics.
- Model-aware benchmark reasoning policy and model-profile metadata in summary
  artifacts.
- Explicit goal stop-condition and bounded-loop validation.

### Changed

- Benchmark runs now require an explicit `--model` and performance claims are
  isolated per model.
- GPT-5.6 requires Codex CLI `0.144.0` or newer; `max` and `ultra` are accepted
  runtime values but remain explicit experiments.
- Benchmark source paths now honor `CODEX_HOME` instead of assuming
  `~/.codex`.

### Benchmarks

- Subscription-backed healthy canaries passed baseline verification for GPT-5.6
  Sol (`core,boundary,goal_loop`), Terra (`core,boundary`), and Luna
  (`core,boundary,non_technical`).
- Sol retained token-cap warnings for the `X1` and `X2` core cases. Luna
  retained them for `X1/X2` in core plus pricing-copy and onboarding-email
  cases, so no token, latency, cost, or default-model claim is made.
- All GPT-5.6 profiles remain candidates until repeated healthy and degraded
  evidence passes within each model.

## [0.2.10] - 2026-06-10

### Added

- Goal and loop discipline for longer `X3/X4` Codex work, including a compact
  `Goal:`/`Loop:` response contract without adding a new BMADX gear.
- Benchmark parser and scenario coverage for goal-aware and bounded
  review/repair/validate loop answers.

### Changed

- Current public version is `v0.2.10`.

## [0.2.9] - 2026-06-02

### Added

- Performance verifier for BMADX benchmark summaries with separate baseline and claim modes.
- Verifier coverage checks for required profiles, policies, group scope, repeat count, token caps, latency fields, routing gates, thinking-budget gates, and handoff drift gates.
- `execution-boundaries.md` reference for Codex-first, Claude Code, PMAX X, local-model, and platform-drift details.
- Benchmark `--gate-mode precomputed|in-session`; performance baselines now validate compact gates in the harness instead of forcing in-session tool calls.
- GPT-5.5 performance baseline summary for `2026-06-02`.

### Changed

- `SKILL.md` is now much smaller and keeps only the core routing, compact gate, response, thinking-budget, and Rescue Mode contract in the activation path.
- Execution-surface and model-experiment details moved out of the happy path to references.
- Performance verifier baseline mode reports `X1/X2` token cap overages as warnings; `claim` mode and `--token-cap-mode strict` keep token caps as hard failures.
- Current public version is `v0.2.9`.

### Benchmarks

- Full GPT-5.5 `precomputed` baseline passed automated baseline verification across healthy/degraded and fixed/advisor policies.
- Claim verification failed because advisor policy was slower and more expensive than fixed-medium in this run.
- Token cap warnings remain visible for several `X1` cases; no public savings claim is made from this baseline.

## [0.2.8] - 2026-06-02

### Added

- GPT-5.5 performance benchmark controls for fixed-medium vs advisor-selected reasoning policy.
- Benchmark `--groups`, `--repeat`, `--reasoning-policy`, and optional explicit all-token cost estimate.
- Per-case `duration_seconds`, `reasoning_policy`, and repeat index fields.
- Summary-level token and latency aggregates for all scenario groups.

### Changed

- Raw benchmark artifacts and summary files now include reasoning policy, group scope, and repeat index to avoid overwrites.
- Performance docs frame `v0.2.8` as a baseline, not a public token-savings claim.

### Benchmarks

- GPT-5.5 `core,boundary` canary artifacts were generated for fixed-medium and advisor policies.
- Full healthy/degraded performance baselines were intentionally not run because both canaries had one token-budget failure despite passing routing, reference-budget, and thinking-budget gates.

## [0.2.7] - 2026-05-30

### Added

- Thinking Budget Advisor for per-task Codex reasoning-effort recommendations.
- Public and skill docs for canonical reasoning values: `minimal`, `low`, `medium`, `high`, and `xhigh`.
- Benchmark parsing and validation for `Thinking:` lines, including checks that reject persistent Codex config mutation guidance.

### Changed

- BMADX now treats thinking budget as advisory output after gear classification and compact gate checks.
- Benchmark scenarios now carry expected thinking-budget values alongside expected gears.
- Public docs clarify that BMADX can suggest fit-for-purpose reasoning effort without editing global Codex config.

## [0.2.6] - 2026-05-17

### Added

- Broad Orchestrator Handoff contract for exporting BMADX gear, BMAD gate state, risk flags, proof needs, and open questions to external orchestration systems.
- `bmadx_handoff.v1` JSON schema and sample handoff packets for `X3` auth architecture review and `X4` migration recovery review.
- Skill reference for broad handoff boundaries, including `X3/X4` with and without handoff.
- Public docs explaining that the handoff schema can cooperate with broad orchestration models such as Gastown-style workflows without making BMADX a runtime platform.
- Benchmark validation hooks for handoff cases and runtime-drift checks.

### Changed

- BMADX public positioning now separates the narrow Codex-first lane from broad orchestration handoff.
- `PMAX X` is clarified as a model-experiment lane, not broad orchestration support.
- Subagent guidance now optimizes for operator time-to-value: no default helpers for simple `X1`, and one bounded read-only helper when `X2` discovery or verification can run in parallel.

## [0.2.5] - 2026-05-05

### Added

- Architecture Guardrail Card for non-technical builders, with five plain-language questions and gear-specific defaults.
- red-zone escalation guidance for auth, billing, payments, permissions, migrations, data deletion, secrets, production config, privacy, multi-tenant access, webhooks, encryption, admin roles, and compliance.
- `X4/FUBAR` Failure Patterns / Guardians section in the rollout checklist and sample bundle.
- non-technical benchmark scenarios for pricing copy, onboarding email, Google login, subscription billing, data deletion, and messy migration recovery.
- benchmark summary readout for `what_failed_why_it_matters` so failures are understandable beyond token counts.
- public ecosystem/strategic stance doc covering Oracle, BMAD, BMADX, pyfallow, Guardrails.md, OMX, and adjacent tools.
- explicit full-stack framing for non-technical builders: Oracle for second opinion, BMAD for process, BMADX for routing, Guardrails.md for safety memory, pyfallow for Python code intelligence, and CI/tests for proof.

### Fixed

- `sync_bmadx.py check` and `report` no longer accept BMAD release/reference drift as the new baseline; only explicit `sync` or first run can do that.
- `sync_bmadx.py sync` no longer records a BMAD dependency baseline unless the live dependency check is healthy and required references are present.
- compact `X3/X4` output now reports `bmad_status=needs_attention` when hard-gate execution is blocked by dependency drift.
- benchmark summaries now include explicit `validation_failures` lists so failed checks are inspectable without recomputing pass counters.
- BMAD dependency checks and install verification now fail with explicit timeout errors instead of hanging indefinitely.
- benchmark routing validation now uses the selected gear from the response contract, not incidental gear mentions.
- install verification now parses BMADX sync JSON and rejects semantic warning/error states.
- installer copy now excludes runtime `state/*.json` files so local health cache does not leak into installs.

### Changed

- public and skill copy now frame BMADX more clearly as architecture guardrails for non-technical builders, while preserving `BMAD > BMADX`.
- clear bounded plan requests remain `X2` by default instead of forcing clarification or escalation.
- future benchmark summary filenames use a `-bmadx.json` suffix to avoid confusing BMADX results with BMAD baselines.
- GitHub repository description now uses the public low-friction architecture guardrails positioning instead of the older `lazy overlay` wording.

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
