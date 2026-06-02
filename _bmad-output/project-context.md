# Project Context — BMADX v0.2.8

## Scope

This repo develops `BMADX` as the operational and tactical layer on top of `BMAD`.

Non-negotiable rule:
- `BMAD > BMADX`

## Active program

Current release focus:
- publish `v0.2.8` as the GPT-5.5 token and latency performance baseline for the Thinking Budget Advisor,
- tune BMADX for Codex on GPT-5.5 without changing core routing semantics,
- make BMADX genuinely usable for non-technical, low-friction Codex users,
- position BMADX as an architecture guardrail for people who understand the
  product problem better than the software architecture,
- add the Architecture Guardrail Card as the default non-technical interface for architecture risk,
- add red-zone escalation defaults so auth, billing, data, permissions, secrets, and production work enter BMAD,
- add an explicit packet-based handoff surface for work that should move from
  the narrow Codex-first lane into a broad orchestration workflow,
- document cooperation with broad orchestration models such as Gastown-style
  workflows without naming, depending on, or copying private orchestrators,
- improve subagent guidance for operator time-to-value while keeping final
  responsibility in the main BMADX/Codex lane,
- recommend fit-for-purpose Codex reasoning effort per task without mutating
  global Codex config,
- measure fixed-medium reasoning against advisor-selected reasoning before
  making any public token-savings claim,
- keep BMAD as the process owner,
- make public install, activation, and proof surfaces portable and easier to trust,
- keep `X4/FUBAR` valuable without making it normal.

Out of scope:
- porting OMX,
- adding a second durable plan store,
- turning BMADX into a runtime platform,
- shipping Claude Code parity or a generic multi-agent adapter layer.
- dispatching workers, choosing model lanes, assigning arbiters, installing
  hooks/MCP/plugins/subagents, or creating runtime state for broad orchestration.
- publishing a savings claim from a single performance run.

## Active BMAD artifacts

- PRD: `_bmad-output/prd-bmadx-v0.2.8.md`
- Architecture: `_bmad-output/architecture-bmadx-v0.2.8.md`

## Model target

- target Codex model: `gpt-5.5`
- default benchmark reasoning: `medium`
- BMADX does not mutate global Codex config; users choose their model outside BMADX
- Thinking Budget Advisor may recommend `low`, `medium`, `high`, or `xhigh`
  per run, but this is advisory and follows gear/risk/phase after
  classification and gate checks
- canonical highest-effort label is `xhigh`; normalize `extra_high` wording to
  `xhigh` in public and benchmark surfaces
- stronger models reduce prompt scaffolding, but do not bypass `BMAD > BMADX`
- Codex remains the only supported execution surface for BMADX core
- Claude Code is watch/prototype only because its `CLAUDE.md`, hooks, subagents,
  MCP, plugins, permissions, and `claude -p` behavior are different enough that
  a simple adapter would be unreliable or would create runtime-platform drift
- local models such as Mistral may be tested only through Codex OSS-provider
  benchmark runs and must pass the same routing and safety gates before any
  public claim
- `PMAX X` is the named cheap-model experiment lane, not a product-default lane
- no PMAX X candidate can be promoted without repeated healthy/degraded passes,
  zero red-zone under-escalations, no `X4` false positives, and useful
  explanations for non-technical owners
- current cheap-model watchlist should treat Ollama Cloud `minimax-m2.7:cloud`
  as the best experiment so far, but not as a safe BMADX router: the full Codex
  OSS runner still under-escalated Google login and subscription billing to `X2`
- `minimax-m2.5:cloud` is useful for cheap drafting/exploration, but the full
  Codex OSS runner under-escalated auth, billing, data deletion, and BMAD-story
  boundary cases despite passing a simple `ollama run` red-zone smoke
- `kimi-k2.6:cloud`, `glm-5.1:cloud`, and `gemma4:31b-cloud` passed the simple
  red-zone smoke and remain watch candidates; `glm` and `gemma` showed strict
  JSON/markdown-fence issues
- `qwen3-coder-next:cloud`, `devstral-small-2:24b-cloud`, and
  `devstral-2:123b-cloud` under-escalated Google login to `X2`; treat them as
  code helper candidates only, not routing/guardrail candidates
- Codex OSS with Ollama Cloud works on Codex CLI `0.125.0`, but emits warning
  noise around model IDs containing `:` and uses fallback model metadata, so
  this lane remains experimental

## Routing contract

### Architecture Guardrail Card

Default questions:

1. What user or product outcome are we protecting?
2. Which system area should own this change?
3. Which existing pattern should the agent follow?
4. What could break if this is implemented in the wrong place?
5. What proof would convince a non-technical owner it is safe?

Gear defaults:
- `X1`: card is silent; no questions unless a red-zone signal appears.
- `X2`: card is silent; surface only the key tradeoff and proof.
- `X3`: card is explicit and tied to BMAD artifacts.
- `X4`: card goes into Rescue Mode with failure patterns, guardians, owners, and verification.

Red-zone tasks are `X3` minimum unless purely textual:
- auth, billing, payments, permissions, migrations, data deletion, secrets,
  production config, user data privacy, multi-tenant access, webhooks,
  encryption, admin roles, legal/compliance.

Escalate to `X4` when red-zone work also has unclear ownership, repeated
failures, rollback risk, incident recovery, or no credible verification path.

### Broad-orchestrator handoff

- Handoff is a packet contract, not a new gear and not `X5`.
- `X4/FUBAR` remains Rescue Mode, not automatic broad orchestration.
- BMADX may recommend handoff for domain-heavy, judgment-heavy, long-context,
  privacy-sensitive, multi-system, public-artifact, or explicitly requested
  broad-review work.
- BMADX may export only gear, BMAD gate state, red-zone flags, privacy and
  reversibility guesses, proof requirements, forbidden changes, open questions,
  and BMAD artifact references.
- BMADX must not export model choices, worker lanes, arbiters, dispatch
  commands, MCP/hooks/plugins/subagent setup, persistent run IDs, or runtime
  state.
- Public docs may name only generic broad orchestration examples such as
  Gastown-style workflows, team-specific review systems, or private arbitration
  stacks.

### Thinking Budget Advisor

- Thinking budget is not a new gear and not a router.
- Default mapping: `X1=low`, `X2=medium`, `X2/X3 boundary=high`,
  `X3=high`, `X4=xhigh` for rescue execution.
- `X4` classification-only prompts may stay at `high` while naming `xhigh` for
  real execution.
- The advisor must not write or instruct edits to `~/.codex/config.toml`.
- Benchmark validation should reject non-canonical effort values and persistent
  config mutation language.

### X1/X2

- classify first,
- then run `sync_bmadx.py check --gear X1|X2 --compact`,
- use the cached healthy BMAD state when available,
- warn instead of blocking when there is no fresh healthy BMAD snapshot,
- keep the response compact in the obvious happy path.
- default subagent stance: do not spawn for most `X1`; for `X2`, one bounded
  read-only helper can improve time-to-value when it checks independent repo
  patterns, duplicate text, or verification while the main lane keeps moving.

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
- plain-language architecture guidance for non-technical builders, without
  hiding the BMAD dependency or weakening verification gates

## Benchmark context

- runner: `benchmark/scripts/run_bmadx_benchmark.py`
- profiles: `healthy`, `degraded`
- mixed metrics: token budget, response format, routing, reference-read budget
- model-aware artifacts use the model slug in raw and summary file names
- broad-handoff benchmark extension: scenarios now cover an `X3` auth
  architecture review handoff and an `X4` migration recovery handoff
- broad-handoff benchmark extension: summaries include `handoff_cases`,
  handoff routing, and runtime-drift checks that reject worker lanes, model
  names, dispatch commands, and platform-surface leakage
- thinking-budget benchmark extension: scenarios include
  `expected_reasoning_effort`, summaries count `thinking_budget_*` checks, and
  validation rejects global Codex config mutation language
- `v0.2.8` performance benchmark extension: runner supports
  `--reasoning-policy fixed|advisor`, `--groups`, and `--repeat`
- `v0.2.8` performance benchmark extension: per-case records include
  `duration_seconds`, `reasoning_policy`, and `repeat_index`
- `v0.2.8` performance benchmark extension: raw artifacts include model,
  profile, reasoning policy, group slug, repeat index, and scenario key to avoid
  canary/full overwrites
- `v0.2.8` performance benchmark extension: summaries include total/average/min/max
  token aggregates plus average/p50/p95/max latency aggregates
- `v0.2.8` performance benchmark extension: optional cost estimate is disabled
  by default and requires an explicit operator-provided all-token price
- `v0.2.8` reporting rule: this is a baseline until repeated healthy/degraded
  runs preserve routing, red-zone safety, `X4` rarity, compact `X1/X2`, and
  thinking-budget validation
- `2026-06-01` GPT-5.5 canary result: fixed-medium and advisor policies both
  passed routing, reference-budget, and thinking-budget checks on `core,boundary`
  but each had one token-budget failure (`fixed`: `X2`; `advisor`: `X1`)
- `2026-06-01` full baseline decision: do not run or publish full
  healthy/degraded performance baselines until obvious `X1/X2` hidden token
  cost is reduced
- current `v0.2.4` GPT-5.5 healthy result: `6302.0` average tokens, all core validation gates passed
- current `v0.2.4` GPT-5.5 degraded result: `8918.5` average tokens, X3/X4 hard-gate semantics preserved
- current GPT-5.4 healthy comparison: `12370.75` average tokens
- post-release hardening: missing `tokens used` is a benchmark failure, not a silent `0` token result
- post-release hardening: summary JSON includes `validation_failures` for direct failed-check inspection
- post-release hardening: BMAD dependency checks and install verification use explicit timeouts
- post-release hardening: `sync` only accepts a BMAD dependency baseline when live BMAD is healthy and required references are present
- post-release hardening: benchmark routing uses the selected `Choice:` gear, not incidental gear mentions
- post-release hardening: future BMADX benchmark summaries use `-bmadx.json`
- post-release hardening: installer excludes runtime `state/*.json` from copied skill trees
- post-release hardening: benchmark runner can label primary Codex/OpenAI runs
  separately from experimental Codex OSS-provider local-model runs
- non-technical benchmark extension: scenarios now cover pricing copy (`X1`), onboarding email (`X2`), Google login (`X3`), subscription billing (`X3`), deleting inactive users (`X3`), and failed migration recovery (`X4`)
- non-technical benchmark extension: summaries include `non_technical_cases` and `what_failed_why_it_matters`
- historical baselines:
  - `benchmark/summary-2026-04-04.json`
  - `benchmark/summary-2026-04-05-healthy-bmad.json`
  - `benchmark/summary-2026-04-05-degraded-bmad.json`
  - `benchmark/summary-2026-04-06-healthy-bmad.json`
  - `benchmark/summary-2026-04-06-degraded-bmad.json`
  - `benchmark/summary-2026-04-24-gpt-5-5-healthy-bmad.json`
  - `benchmark/summary-2026-04-24-gpt-5-5-degraded-bmad.json`
  - `benchmark/summary-2026-04-24-gpt-5-4-healthy-bmad.json`

## Verify

- `python3 skill/bmadx/scripts/test_sync_bmadx.py`
- `python3 scripts/test_install_bmadx.py`
- `python3 scripts/test_install_and_verify_bmadx.py`
- `python3 benchmark/scripts/test_run_bmadx_benchmark.py`
- `python3 skill/bmadx/scripts/sync_bmadx.py check --json`
- `python3 skill/bmadx/scripts/render_fubar_bundle.py --project-name BMADX --project-path "$PWD" --output-dir samples/fubar-bundle --include-architect --public-sample`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --reasoning medium --profile healthy --date-stamp 2026-04-24`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --reasoning medium --profile degraded --date-stamp 2026-04-24`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.4 --reasoning medium --profile healthy --date-stamp 2026-04-24`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile healthy --reasoning medium --reasoning-policy fixed --groups core,boundary --repeat 1 --date-stamp 2026-06-01`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --model gpt-5.5 --profile healthy --reasoning-policy advisor --groups core,boundary --repeat 1 --date-stamp 2026-06-01`

## Ecosystem stance

- Oracle: recommended second-opinion layer for architecture-heavy, ambiguous, or expert-gap decisions with selected repo files.
- BMAD: upstream process and architecture source of truth.
- BMADX: lightest-safe-mode routing, compact gates, Rescue Mode.
- pyfallow: recommended companion for Python static codebase intelligence.
- Guardrails.md: recommended pattern for repo-local safety constraints and repeated failure lessons.
- deterministic checks: tests, CI, static analysis, secret scans, and architecture checks provide hard facts.

BMADX is the connective layer: it decides when to stay compact, when to use
BMAD, when to ask Oracle for a second opinion, when to respect repo guardrails,
and when deterministic checks matter more than model confidence.

Compete with ad-hoc prompting, architecture-blind vibe coding, and overbuilt
runtime defaults. Do not compete with Oracle, BMAD, pyfallow, Guardrails.md,
scanners, CI, or execution surfaces.

Future product gap:
- a product/analytics guardrail companion that checks product goals, user
  journeys, analytics/event naming, release proof, and whether the feature
  should be built before implementation.
