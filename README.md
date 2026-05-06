# BMADX

[![Release](https://img.shields.io/github/v/release/pdurlej/BMADX?display_name=tag)](https://github.com/pdurlej/BMADX/releases/latest)
[![License](https://img.shields.io/github/license/pdurlej/BMADX)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](docs/5-minute-quickstart.md)
[![BMAD-first](https://img.shields.io/badge/BMAD-first-12263A)](docs/why-bmad-is-required.md)
[![Docs](https://img.shields.io/badge/docs-English-0A7EA4)](START_HERE.md)

BMADX is a BMAD-first guardrail layer for Codex: small changes stay small,
risky work escalates, and messy repos can drop into a rare Rescue Mode
(`X4/FUBAR`) instead of improvising architecture in the dark.

The longer-term mission is practical: help non-technical builders get better
software architecture from AI agents without needing to become software
architects first. BMAD provides the process backbone; BMADX keeps day-to-day
Codex work guided, bounded, and understandable.

BMADX now includes an Architecture Guardrail Card: five plain-English questions
that help Codex protect product outcomes, system ownership, existing patterns,
failure risk, and proof a non-technical owner can understand.

BMADX `v0.2.5` is tuned for Codex on GPT-5.5. Stronger models reduce the need
for prompt scaffolding, but they make explicit boundaries and verification more
important: BMAD still owns process, BMADX keeps the work mode light and safe.

![BMADX architecture overview](docs/assets/bmadx-architecture-overview.svg)

BMADX is:
- BMAD-first
- lighter than OMX
- focused on low-friction day-to-day Codex work
- opinionated about verification and escalation
- designed for product people and builders who want safer agent output, not more ceremony

BMADX is not:
- a replacement for BMAD
- a second process system
- a clone of the `.omx` runtime
- a general adapter layer for every AI coding tool

Current public version: `v0.2.5`

## Start here

If this is your first time:

1. Read [START_HERE.md](START_HERE.md)
2. Run the install wrapper from [5-Minute Quickstart](docs/5-minute-quickstart.md)
3. Paste one of the prompts from [What to Paste into Codex](docs/what-to-paste-into-codex.md)

## Try it on a real task

BMADX is easiest to judge on tasks where a coding agent can either stay useful
or quietly become too clever.

| Task you give Codex | BMADX should do |
| --- | --- |
| "Fix this typo in the pricing copy" | keep it tiny (`X1`) |
| "Add Google login without breaking existing auth" | slow down, identify the owner and proof (`X3`) |
| "This repo is messy and I need a migration plan" | use Rescue Mode only if the entropy is real (`X4/FUBAR`) |

If that routing feels useful in your repo, a star helps me find early testers.
If it misroutes, open a [Discussion](https://github.com/pdurlej/BMADX/discussions)
or issue with the task prompt and what you expected instead.

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

## Feedback wanted

The most useful feedback right now is concrete:
- a real Codex task where BMADX picked the wrong mode,
- a non-technical builder question that the README still does not answer,
- a messy-repo case that might deserve Rescue Mode,
- a cheaper/local model run that passes the same routing expectations.

Humans and agents are both welcome to test it. Please include the prompt,
expected mode, observed mode, and any safety concern you noticed.
