# BMADX

[![Release](https://img.shields.io/github/v/release/pdurlej/BMADX?display_name=tag)](https://github.com/pdurlej/BMADX/releases/latest)
[![License](https://img.shields.io/github/license/pdurlej/BMADX)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](docs/5-minute-quickstart.md)
[![BMAD-first](https://img.shields.io/badge/BMAD-first-12263A)](docs/why-bmad-is-required.md)
[![Docs](https://img.shields.io/badge/docs-English-0A7EA4)](START_HERE.md)

BMADX is a lightweight BMAD-first guardrail for Codex.

It helps agentic builders choose the smallest safe workflow:
- copy tweaks stay tiny,
- normal product changes stay bounded,
- auth, billing, data, and production work escalates,
- messy repos get a rare Rescue Mode (`X4/FUBAR`).

Use it when plain Codex feels too ad-hoc, but full BMAD ceremony feels too heavy
for everyday work. Copy tweak != architecture ceremony. Auth change !=
vibe-coded one-shot.

Star this repo if you use Codex/BMAD and want pragmatic guardrails for real
product-building tasks.

![BMADX architecture overview](docs/assets/bmadx-architecture-overview.svg)

Current public version: `v0.2.5`

## Start here

If this is your first time:

1. Read [START_HERE.md](START_HERE.md)
2. Run the install wrapper from [5-Minute Quickstart](docs/5-minute-quickstart.md)
3. Paste one of the prompts from [What to Paste into Codex](docs/what-to-paste-into-codex.md)

## Tiny demo

Task:

```text
Add a pricing section to the landing page and keep the change small.
```

BMADX should keep this tiny or bounded, preserve existing page patterns, and
avoid full BMAD ceremony unless pricing logic, billing, permissions, or
production behavior changes.

Red-zone task:

```text
Add Google login.
```

BMADX should not treat this as a normal copy/code task. Auth affects identity,
data access, security, and failure recovery, so it should escalate to BMAD-heavy
handling.

## Known limits today

- BMADX requires BMAD for Codex. If BMAD is not installed, start there first.
- BMADX is Codex-first, not Claude Code-native.
- BMADX adds routing and guardrails; it does not prove code quality by itself.
- Model experiments such as `PMAX X` are benchmark probes, not support claims.
- Tests, CI, static analysis, and human review still matter for red-zone work.

## Who this is for

BMADX is for:
- founders, makers, designers, and PM-ish users who already use Codex
- non-technical builders who understand the problem better than the technology
- engineers who want more discipline than ad-hoc prompting
- people who want BMAD behind the scenes without running full BMAD ceremony on every bounded task
- teams that occasionally need a rescue/scaffold layer for messy repos

BMADX is probably not for you if:
- you already know you want to work directly in BMAD all the time
- you want a durable orchestration runtime with `.omx`-style state and runtime tooling
- you only need plain Codex for trivial one-off prompts
- you want Claude Code-native hooks, MCP, plugins, subagents, or settings automation

## Codex-first stance

BMADX is intentionally Codex-first. The current product is optimized around
Codex Skills, `CODEX_HOME`, `codex exec` benchmarkability, and a compact gate
that separates classification from execution permission.

Claude Code is not a near-term target. Its Skills, `CLAUDE.md`, hooks,
subagents, MCP, plugins, permissions, and interactive/non-interactive behavior
make a simple BMADX port misleading. BMADX may watch Claude Code as an
execution surface, but the repo does not currently ship or promise a Claude
adapter.

Model experiments are welcome inside Codex. The benchmark runner supports the
primary OpenAI/Codex path and can also run experimental local-model checks via
Codex OSS providers when a local model is installed.

### Model lanes

- Primary lane: Codex on GPT-5.5.
- Experiment lane: `PMAX X`, currently focused on cheaper Ollama/OpenRouter/local candidates.
- Current best PMAX X experiment: `minimax-m2.7:cloud`, but it is not safe as the BMADX router yet.
- Not defaults: Claude adapters, local/Ollama/OpenRouter models, and any model that fails red-zone routing.

Rule: no public model claim without the same BMADX benchmark gates for routing,
compactness, red-zone escalation, degraded BMAD behavior, and `X4` rarity.

## Help test BMADX

The most useful feedback is not "nice project." It is where BMADX
over-escalated, under-escalated, or explained itself badly.

Try one real Codex task and report:
- what BMADX chose,
- what you expected,
- whether the result was too light or too heavy,
- what proof would convince a non-technical owner it is safe.

Feedback templates: [Community Feedback](docs/community-feedback.md)

## 5 minute quickstart

Prerequisite: BMAD must already be installed in your Codex skills. BMADX depends
on `bmad-method-codex`.

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

Then open Codex in your project and paste:

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.
Use the Architecture Guardrail Card silently unless a risk changes the safe mode.

My task:
<describe the change in plain English>

What I care about:
<speed / clarity / safety / cleanup / shipping>
```

More onboarding:
- [5-Minute Quickstart](docs/5-minute-quickstart.md)
- [Install for Vibe Coders](docs/install-for-vibe-coders.md)
- [What to Paste into Codex](docs/what-to-paste-into-codex.md)

## What happens after install

Most users should not choose `X1/X2/X3/X4` manually.

The intended model is:
1. describe the task in plain language
2. let BMADX classify it
3. let BMADX stay compact for normal work
4. escalate to BMAD-heavy work only when the task genuinely needs it

The internal gear model is:
- `X1` for tiny local fixes
- `X2` for normal bounded changes
- `X3` for BMAD-heavy work
- `X4` for Rescue Mode (`X4/FUBAR`) when the repo or rollout needs extra structure

`X4` is intentionally rare. It is the ace in the sleeve, not the default.

## BMAD vs BMADX vs OMX vs plain Codex

| Use this when... | Best fit | Why |
| --- | --- | --- |
| you just need a trivial one-off answer | plain Codex | lowest setup and lowest ceremony |
| you want full process ownership and BMAD artifacts should drive the work | BMAD | BMAD remains the upstream source of truth |
| you want lighter day-to-day Codex usage with BMAD-compatible guardrails | BMADX | compact routing, verify discipline, rare rescue mode |
| you want a heavier runtime layer and broader orchestration | OMX | closer to that product category than BMADX |

More detail:
- [Architecture Guardrail Card](docs/architecture-guardrail-card.md)
- [Why BMAD is required](docs/why-bmad-is-required.md)
- [Choose BMAD vs BMADX vs OMX](docs/choose-bmad-bmadx-omx.md)
- [Ecosystem and strategic stance](docs/ecosystem-and-stance.md)
- [Model experiments](docs/model-experiments.md)
- [FAQ](docs/faq.md)

## Recommended companion stack

BMADX works best as part of a small, explicit stack:

- BMAD for process and architecture source of truth
- BMADX for lightest-safe-mode routing in Codex
- [Oracle](https://github.com/steipete/oracle) for second-opinion reviews with the right files and stronger models when the builder does not know what to ask
- [pyfallow](https://github.com/pdurlej/pyfallow) for Python codebase intelligence when available
- [Guardrails.md](https://guardrails.md/) for repo-local safety constraints and repeated failure lessons
- CI, tests, static analysis, and secret scans for hard technical facts

More detail: [Ecosystem and strategic stance](docs/ecosystem-and-stance.md)

In plain language: Oracle helps ask the expert second opinion, BMADX decides the
safe work mode, BMAD owns the process, Guardrails.md remembers hard mistakes,
pyfallow checks Python code structure, and CI/tests prove the result.

## What BMADX proves well today

BMADX has a real public wedge:
- it is much lighter than OMX in the repo’s benchmarked runs
- it keeps BMAD as the source of truth instead of competing with it
- it reduces day-to-day process selection friction inside Codex
- it keeps a rare but useful Rescue Mode for messy repos

What it does not prove:
- that BMADX is categorically better than BMAD
- that token counts alone capture user value
- that every task should use BMADX instead of plain Codex

Benchmark reading:
- [Benchmark Overview](docs/benchmark-overview.md)
- [Historical benchmark summary](docs/benchmark-summary-2026-04-04.md)
- [Current mixed-metric summary](docs/benchmark-summary-2026-04-06.md)
- [GPT-5.5 benchmark summary](docs/benchmark-summary-2026-04-24-gpt55.md)

Human-readable proof:
- [Plain Codex vs BMADX transcript](samples/transcripts/plain-codex-vs-bmadx.md)
- [BMAD vs BMADX vs OMX transcript](samples/transcripts/bmad-vs-bmadx-vs-omx.md)

Latest benchmark snapshot:
- `BMADX GPT-5.5 healthy` (`2026-04-24`): `6302.0` average tokens
- `BMADX GPT-5.5 degraded` (`2026-04-24`): `8918.5` average tokens, with X3/X4 hard-gate semantics preserved
- `BMADX GPT-5.4 healthy` (`2026-04-24` comparison): `12370.75` average tokens
- GPT-5.5 healthy passed core `format`, `token`, `reference_budget`, `routing`, and `overreach` validation
- historical `OMX` baseline remains `25540.5` average tokens

## Rescue Mode (`X4/FUBAR`)

Rescue Mode exists for cases where BMAD alone is not enough as a tactical
operating surface inside Codex.

Typical triggers:
- the repo is messy or high-entropy
- scope is diffuse or multi-threaded
- rollout and ownership need to be made explicit
- the team needs a scaffold bundle, not just a short answer

What it generates:
- `AGENTS.md`
- `.customize.yaml` snippets
- trigger and verify matrices
- rollout checklist
- subagent policy

More detail:
- [Rescue Mode guide](docs/x4-rescue-mode.md)
- [Sample bundle](samples/fubar-bundle)

## Repository map

- [START_HERE.md](START_HERE.md)
- [docs/index.md](docs/index.md)
- [skill/bmadx](skill/bmadx)
- [scripts/install_and_verify_bmadx.py](scripts/install_and_verify_bmadx.py)
- [scripts/install_bmadx.py](scripts/install_bmadx.py)
- [benchmark/scripts/run_bmadx_benchmark.py](benchmark/scripts/run_bmadx_benchmark.py)
- [samples/fubar-bundle](samples/fubar-bundle)

## Contributing

Public onboarding comes first. Contributor and internal guidance lives here:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/architecture.md](docs/architecture.md)
- [_bmad-output/project-context.md](_bmad-output/project-context.md)
