# BMADX Roadmap

This is the public roadmap surface for the repo.

It is intentionally lightweight.

## Current status

Current public version:
- `v0.3.1`

Current main development line:
- `v0.3.x`

What `v0.3.1` fixes:
- deterministic benchmark tests no longer depend on an operator-installed
  global BMAD skill when running on a clean CI host

What `v0.3.0` delivers:
- GPT-5.6 Sol, Terra, and Luna profile compatibility on Codex CLI `0.144.0+`
- model-aware thinking advice without changing `X1..X4` or BMAD gates
- explicit-model benchmark runs and per-model claim isolation
- goal stop conditions that terminate on proof, bounded attempts, approvals,
  hard stops, or human review
- audit and BMAD artifacts that let a medium/high-thinking Sol continue safely
- first healthy subscription-backed canaries for all three GPT-5.6 profiles,
  without promoting them to defaults or publishing performance claims

What `v0.2.10` focuses on:
- goal-aware BMADX contract for Codex `/goal` without adding a new gear
- bounded review/repair/validate loop discipline for `X3/X4`
- benchmark coverage for `Goal:` and `Loop:` lines with runtime-drift guards

What `v0.2.9` focuses on:
- reducing hidden activation cost by keeping `SKILL.md` focused on the core contract
- moving execution-surface and model-experiment details to references
- adding an autoverifier for full performance baselines
- keeping token-savings claims separate from baseline safety approval

What `v0.2.8` focuses on:
- GPT-5.5 token and latency performance baselines for fixed-medium vs
  advisor-selected reasoning policies
- repeatable benchmark output naming by reasoning policy and repeat index
- performance summary aggregates without making a public token-savings claim
- canary evidence that full baseline runs should wait until obvious `X1/X2`
  token-budget failures are reduced

What `v0.2.7` focused on:
- Thinking Budget Advisor: per-task Codex reasoning-effort recommendations
  that follow the selected gear without changing global Codex config
- benchmark validation for `Thinking:` lines and guardrails against persistent
  reasoning config mutation
- preserving `v0.2.6` broad-orchestrator handoff as a packet schema, not runtime integration

What `v0.2.6` focused on:
- broad-orchestrator handoff as a packet schema, not runtime integration
- cooperation with Gastown-style broad orchestration models without naming or depending on a private orchestrator
- preserving BMADX as the narrow Codex-first lane while allowing explicit handoff for broad, judgment-heavy, or long-context work

What `v0.2.5` focused on:
- tuning BMADX for Codex on GPT-5.5
- keeping GPT-5.5 from bypassing BMAD boundaries or Rescue Mode discipline
- model-aware benchmark artifacts that do not overwrite historical GPT-5.4 runs
- clearer positioning: BMADX is a boundary and verification layer, not a substitute for model intelligence
- clearer mission: architecture guardrails for non-technical builders, not a framework for framework people
- the full non-technical builder stack: Oracle, BMAD, BMADX, Guardrails.md, pyfallow, and CI/tests

## What is already stable

- BMAD dependency and `BMAD > BMADX`
- four-gear routing model: `X1..X4`
- hard/soft split between `X1/X2` and `X3/X4`
- `X4/FUBAR` scaffold bundle
- benchmark runner committed in-repo
- model-aware benchmark output naming
- local Codex model-catalog compatibility diagnostics

## Near-term improvements

- keep making the public surface friendlier for non-technical Codex users
- make architecture tradeoffs understandable without teaching users the whole process model
- ship the Architecture Guardrail Card as the default mental model for non-technical architecture risk
- keep red-zone routing strict for auth, billing, permissions, data, secrets, production config, and privacy
- integrate with companion guardrails such as pyfallow and Guardrails.md by recommendation, not by platform ownership
- validate whether advisor-selected reasoning levels reduce token spend without weakening red-zone routing or `X4` rarity
- run repeated healthy and degraded matrices for Sol, Terra, and Luna before
  any support promotion
- reduce hidden `codex exec` token cost for obvious `X1/X2` canary cases before
  publishing performance claims
- keep BMADX Codex-first; do not spend near-term roadmap on Claude Code parity
- add experimental Codex OSS-provider benchmark lanes for local models such as Mistral, without turning them into default claims
- improve proof surfaces with better transcripts and examples
- make Rescue Mode easier to adopt without turning it into a default mode
- keep tightening portability and low-friction install paths

## Long-term guardrails

These should not change:
- BMAD remains the upstream process owner
- BMADX stays lighter than OMX
- BMADX stays useful for vibe coders without becoming undisciplined
- BMADX should not drift into a full orchestration runtime
- BMADX should not promise adapter parity with Claude Code, Cursor, Windsurf, or other execution surfaces unless their gates and benchmarks prove the same behavior
