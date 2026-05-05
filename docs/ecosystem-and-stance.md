# BMADX Ecosystem and Strategic Stance

BMADX should not become a platform. Its job is to make Codex safer and lighter
for BMAD-backed work, especially for non-technical builders.

## Recommended package

For serious non-technical building, BMADX should sit in a small stack:

| Layer | Recommended tool | Role |
| --- | --- | --- |
| Expert second opinion | Oracle | Bundle prompt plus files and ask stronger models when architectural judgment is uncertain |
| Process and architecture source of truth | BMAD | PRD, architecture, stories, workflow ownership |
| Codex work-mode router | BMADX | Lightest safe mode, compact gates, Rescue Mode |
| Python codebase intelligence | pyfallow | Deterministic Python graph, boundary, dependency, cycle, and dead-code checks |
| Repo-local failure memory | Guardrails.md-style file | Persistent constraints and repeated failure lessons |
| Hard technical facts | CI, tests, static analysis, secret scans | Evidence that work is safe enough to ship |

This package keeps responsibilities separate: Oracle brings a second opinion
when the builder does not know what to ask, BMAD owns process, BMADX routes
work, pyfallow and scanners provide facts, and repo guardrails capture hard
lessons.

## Full-stack flow for non-technical builders

The target flow is:

1. State the product outcome in plain English.
2. Ask Oracle for a high-quality second opinion when the decision is outside the builder's expertise.
3. Let BMADX choose the lightest safe mode and apply the Architecture Guardrail Card.
4. Use BMAD when the work needs process, architecture, PRD, or story ownership.
5. Use Guardrails.md-style constraints when the repo has repeated failure lessons or forbidden moves.
6. Use pyfallow, tests, CI, scanners, and reviews to prove the code is not just plausible, but safer.

BMADX is the connective layer in this stack. It should know when to stay small,
when to call BMAD, when to recommend a second opinion, and when deterministic
checks matter more than model confidence.

## Who BMADX should compete with

BMADX should compete with:

- ad-hoc Codex prompting for tasks that are not actually safe as one-shots,
- architecture-blind vibe-coding flows that let non-technical users accidentally change auth, billing, data, or production behavior,
- heavy runtime defaults when the real task only needs `X1/X2`,
- agent workflows that hide verification behind confident prose.

## Who BMADX should not compete with

BMADX should not compete with:

- BMAD, because BMAD is the source of truth,
- Oracle, because second-opinion review strengthens hard decisions,
- pyfallow, because deterministic codebase intelligence strengthens BMADX verification,
- Guardrails.md, because repo-local failure constraints strengthen Rescue Mode,
- Semgrep, CodeQL, Gitleaks, dependency-cruiser, ruff, pyright, tests, and CI,
- Codex, Claude Code, Cursor, Windsurf, or other execution surfaces,
- spec/workflow tools that intentionally own more process than BMADX should own.

## Execution-surface stance

BMADX is Codex-first by design. Its current working contract depends on Codex
Skills, `CODEX_HOME`, a portable Python compact gate, and `codex exec`
benchmark runs. That is a strength, not a temporary limitation.

BMADX should not chase parity with every coding agent. Claude Code is useful to
watch, but it should not be a near-term implementation target because its
native surfaces introduce different failure modes: `CLAUDE.md`, hooks,
subagents, MCP, plugins, permissions, and differences between interactive and
`claude -p` behavior. A naive adapter would either be unreliable or would push
BMADX toward runtime-platform drift.

Near-term rule:
- optimize BMADX for Codex,
- benchmark model behavior through Codex,
- treat Claude Code as watch/prototype only,
- do not ship hooks, MCP, plugins, subagents, or global settings automation.

Local-model experiments, including Mistral-family models, are acceptable only
as Codex OSS-provider benchmarks. They are not the default product target until
they pass routing, red-zone escalation, compact-output, and Rescue Mode rarity
checks.

## Collaboration stance

### BMAD

BMAD is upstream. BMADX should make BMAD easier to use from Codex, not dilute it
or create a second planning tree.

### Oracle

Oracle is a strong companion for architecture-heavy or ambiguous decisions. It
bundles prompts plus selected files so another model can review with real repo
context, including GPT-5.5 Pro through browser mode when available. BMADX should
recommend Oracle when the user is likely to miss an expert-level question, but
BMADX must still verify accepted advice against BMAD artifacts and tests.

Public reference: [github.com/steipete/oracle](https://github.com/steipete/oracle)

### pyfallow

`pyfallow` is a natural companion for Python repositories. BMADX should
recommend it for `X2/X3/X4` verification when the repo is Python-heavy, because
it gives agents deterministic signals about imports, dependencies, complexity,
cycles, boundaries, and likely dead code.

Public target: [github.com/pdurlej/pyfallow](https://github.com/pdurlej/pyfallow)

### Guardrails.md

Guardrails.md-style files are useful for persistent safety constraints and
failure lessons. BMADX should learn from the pattern and recommend it when
projects enter repeated-failure or red-zone territory.

Public reference: [guardrails.md](https://guardrails.md/)

Important boundary: Guardrails.md is safety memory. BMAD is process memory.
BMADX should not merge those roles.

## What to avoid

Do not add:

- `.omx`-style runtime state,
- agent zoo,
- BMADX-owned project task store,
- automatic X4 as the default,
- hidden production access,
- “AI confidence” as a substitute for tests or static checks.

## Near-term integration candidates

| Candidate | Near-term BMADX fit | Boundary |
| --- | --- | --- |
| Oracle | Recommended second-opinion companion for `X3/X4`, boundary decisions, and architecture review | Do not treat model advice as proof |
| pyfallow | Recommended verification companion for Python repos | Do not make BMADX a static analyzer |
| Guardrails.md | X4 Failure Patterns / Guardians and repo safety constraints; evaluate a thin Codex skill or MCP bridge later | Do not replace BMAD artifacts |
| Codex OSS providers | Experimental benchmark lane for local models such as Mistral through Ollama or LM Studio | Do not make local-model behavior a release claim until it passes the same gates |
| Semgrep / CodeQL / Gitleaks | Safety Kit or docs-level recommended checks | Do not bundle heavyweight security runtime into core |
| GitHub Actions | Optional CI templates later | Do not turn BMADX into CI platform |

## Product sentence

BMADX helps non-technical builders use Codex without accidentally skipping the
architecture and verification boundaries that technical builders normally hold
in their heads.

## Missing product layer

The stack is now strong on architecture, second opinions, repo guardrails, and
code checks. The next obvious gap is a product/analytics guardrail layer:

- product goal clarity,
- user journey and success metric checks,
- analytics/event naming discipline,
- release checklist from product promise to measured outcome,
- "should we build this at all?" prompts before implementation.

That should remain a companion layer, not BMADX core, unless it directly affects
gear classification or verification.
