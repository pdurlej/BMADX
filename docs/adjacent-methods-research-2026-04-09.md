# Adjacent Methods Research — updated 2026-04-12

## Purpose

This is a qualitative research benchmark of adjacent methods worth studying for
`BMADX`, beyond `BMAD` and `OMX`.

It answers one practical question:

> Which public methods are worth borrowing from to improve BMADX without
> turning it into a heavier runtime, a second plan store, or a replacement for
> BMAD?

## What this proves

This research is useful for:
- identifying strong product and workflow ideas worth adapting for `BMADX`
- ranking adjacent methods by fit with `BMAD > BMADX`
- separating ideas to borrow now from ideas to only watch or explicitly avoid

## What this does not prove

This research does not prove:
- that any of these methods are categorically better than BMADX
- that BMADX should become a full workflow engine
- that a product with stronger packaging also has a better runtime model
- any token-cost comparison between these methods and BMADX

## BMADX anchor

BMADX should remain:
- `BMAD`-first
- lighter than `OMX`
- focused on low-friction day-to-day Codex work
- strongest as a routing and verification layer, not a second process source of truth

Current repo benchmark context:
- historical `BMAD` average: `7237.5`
- historical `BMADX` average: `10954.75`
- historical `OMX` average: `25540.5`
- current `BMADX healthy` average (`2026-04-06`): `7426.25`

That means adjacent-method research should primarily improve:
- `X1/X2` ergonomics
- onboarding and reusable first-success flows
- later governance surfaces that do not violate `BMAD > BMADX`
- `X4/FUBAR` clarity without making Rescue Mode normal

## Research benchmark method

The matrix below scores each method on a `1..5` scale:

- `X1/X2 ergonomics`: fit for lightweight, bounded day-to-day work
- `Onboarding / reuse`: fit for install, activation, and reusable launch surfaces
- `Governance`: fit for later guardrails, auditable automation, and safety surfaces
- `Rescue-mode relevance`: fit for `X4/FUBAR`-adjacent adoption or recovery scenarios
- `BMADX fit`: how compatible the method is with `BMAD > BMADX`

Higher is better. This is a research benchmark, not a runtime benchmark.

## Research benchmark matrix

| Method | What it is | `X1/X2` ergonomics | Onboarding / reuse | Governance | Rescue-mode relevance | BMADX fit | Priority |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `Aider` | terminal coding workflow with explicit chat modes and repo-map context thrift | `5` | `3` | `2` | `1` | `5` | `Borrow now` |
| `Goose` | local agent with reusable recipes, subrecipes, and launch surfaces | `3` | `5` | `3` | `2` | `4` | `Borrow now` |
| `Task Master` | task-management layer with `parse-prd`, `next-task`, and lean tool modes | `3` | `4` | `3` | `2` | `2` | `Prototype later` |
| `GitHub Agentic Workflows` | markdown-defined agent automation with strong guardrails and auditable outputs | `1` | `2` | `5` | `3` | `4` | `Prototype later` |
| `OneRedOak` | narrow review workflows packaged for Claude Code and GitHub | `2` | `3` | `4` | `3` | `4` | `Watch only` |
| `superpowers` | agentic skills framework and software-development methodology with mandatory workflows | `3` | `5` | `4` | `4` | `2` | `Borrow packaging only` |

## Method-by-method read

### Aider

**What it is**

Aider is a coding workflow built around explicit chat modes and a repository map
that gives the model broad context without always sending full files.

**Best BMADX fit**

`Aider` is the strongest inspiration for `X1/X2`: compact mode splitting,
context thrift, and a bias toward keeping small work small.

**Borrow now**

- a clearer public split between lightweight discussion, normal execution, and heavier escalation
- repo-map style thinking for context economy in `X1/X2`
- stronger public language around "stay small unless the task proves otherwise"

**Watch later**

- whether BMADX needs a thin repo-overview helper for compact path routing

**Avoid copying**

- turning BMADX into a generic pair-programming product
- introducing opaque memory-like behavior behind the scenes

**Risk to `BMAD > BMADX`**

Low. The strongest ideas are ergonomic and packaging-oriented, not process-owning.

**Priority**

`Borrow now`

### Goose

**What it is**

Goose is a local agent product with reusable recipes, parameters, subrecipes,
and launch surfaces that make repeatable flows easy to start.

**Best BMADX fit**

`Goose` is the best inspiration for onboarding, reusable launch paths, and
prompt-pack productization.

**Borrow now**

- recipe-like prompt packs for common BMADX entry points
- better first-run launch surfaces for founders, designers, and PM-ish users
- parameterized "start here" flows that reduce setup thinking

**Watch later**

- limited subrecipe-style packaging for a few reusable Rescue Mode entry cases

**Avoid copying**

- deep recipe trees
- runtime sprawl or a product surface that feels like a platform

**Risk to `BMAD > BMADX`**

Medium-low. Reuse ideas fit well, but nested workflow packaging can drift toward framework creep.

**Priority**

`Borrow now`

### Task Master

**What it is**

Task Master is a task-oriented workflow layer with strong "what next?" behavior,
PRD parsing, and leaner tool-budget modes.

**Best BMADX fit**

It is most useful as a constrained inspiration for "next best step" behavior
and for clearly separating advanced vs everyday surfaces.

**Borrow now**

- lean tool-budget thinking
- better "what now?" guidance after classification

**Watch later**

- a thin BMADX helper that suggests the next operational step while still using BMAD artifacts as the source of truth

**Avoid copying**

- a BMADX-owned task store
- project management state that competes with BMAD artifacts

**Risk to `BMAD > BMADX`**

High. This is the easiest adjacent tool to over-copy in a way that creates a second plan system.

**Priority**

`Prototype later`

### GitHub Agentic Workflows

**What it is**

GitHub Agentic Workflows defines repository automation from markdown and compiles
it into auditable machine surfaces with explicit triggers, permissions, and
safe outputs.

**Best BMADX fit**

This is the strongest source for later governance and auditable automation, not
for day-to-day `X1/X2` UX.

**Borrow now**

- the idea of explicit safe outputs
- guardrails that make automation readable and reviewable

**Watch later**

- CI-adjacent BMADX automation policies
- auditable automation contracts for later benchmark and proof surfaces

**Avoid copying**

- shifting BMADX toward repository automation as its center of gravity
- optimizing for CI workflows before local Codex ergonomics

**Risk to `BMAD > BMADX`**

Low-medium. Governance ideas fit well, but too much automation would pull BMADX away from interactive Codex work.

**Priority**

`Prototype later`

### OneRedOak

**What it is**

OneRedOak packages narrow specialized workflows, especially review-oriented
flows such as code review, design review, and security review.

**Best BMADX fit**

It is useful as a model for narrow, legible specialized flows, especially around
review-adjacent or rescue-adjacent work.

**Borrow now**

- sharper packaging for specialized review or rescue adjuncts
- clearer examples that explain when a specialized surface is worth invoking

**Watch later**

- whether BMADX should expose a few tighter review-oriented adjuncts around `X2/X4`

**Avoid copying**

- becoming review-centric
- multiplying workflow families until the product becomes fragmented

**Risk to `BMAD > BMADX`**

Low. The main risk is sprawl, not source-of-truth conflict.

**Priority**

`Watch only`

### superpowers

**What it is**

superpowers is an agentic skills framework and software-development methodology
with mandatory workflows, worktrees, plan-writing, subagent-driven development,
TDD, and review gates.

**Best BMADX fit**

superpowers is most useful for activation UX, auto-trigger packaging, and
first-run workflow framing, not for the BMADX core runtime model.

**Borrow now**

- stronger activation and packaging story
- clearer first-run flow after install
- better explanation of what the system will do automatically vs what the user has to choose manually

**Watch later**

- whether a small amount of auto-trigger framing can make BMADX feel more automatic without making it mandatory everywhere

**Avoid copying**

- mandatory workflow on all tasks
- worktree-first and subagent-heavy default behavior
- turning BMADX into a complete software methodology

**Risk to `BMAD > BMADX`**

High. superpowers is strong exactly where BMADX must be disciplined not to become a second top-level workflow owner.

**Priority**

`Borrow packaging only`

## Watchlist context

These are not part of the main six-method matrix, but they remain useful context:

- `OpenHands`: useful as a watchlist for public proof surfaces and productization, but too platform-shaped for BMADX
- `Archon`: useful as a watchlist for workflow-engine and governance thinking, but too close to orchestration/runtime territory

Neither should be treated as a near-term design target.

## BMADX translation layer

### `X1/X2`

Primary inspirations:
- `Aider` for context thrift and lightweight mode discipline
- `Task Master` for a thinner "what next?" instinct, but only without BMADX-owned state

Translation for BMADX:
- keep `X2` as the public default mental model
- improve compact-path context thrift before adding any new framework surface
- add better post-classification guidance without creating a task system

### Onboarding / public UX

Primary inspirations:
- `Goose` for recipe-like launch surfaces
- `superpowers` for stronger activation framing and first-run workflow explanation

Translation for BMADX:
- expand prompt packs into more reusable launch surfaces
- make installation and first successful task feel more like a guided start and less like a technical setup

### Governance / automation

Primary inspirations:
- `GitHub Agentic Workflows` for safe outputs and auditable automation
- `OneRedOak` for narrower specialized workflow packaging

Translation for BMADX:
- if BMADX later adds repo automation, it should be explicit, reviewable, and narrow
- keep governance as a later layer, not the core product story

### Rescue Mode (`X4/FUBAR`)

Primary inspirations:
- `superpowers` for packaging and activation clarity
- `OneRedOak` for narrow specialized adjuncts

Translation for BMADX:
- make Rescue Mode easier to understand and adopt
- do not make Rescue Mode the normal entry path
- keep BMAD artifacts primary and BMADX scaffolding secondary

## Final ranking

### Borrow now

- `Aider`
- `Goose`

Why:
- they improve `X1/X2` and onboarding without pressuring BMADX to become a full workflow engine

### Prototype later

- `Task Master`
- `GitHub Agentic Workflows`

Why:
- both contain strong ideas, but they belong to later BMADX workstreams:
  - `Task Master` for limited next-step guidance
  - `GitHub Agentic Workflows` for later automation guardrails

### Watch only

- `OneRedOak`

Why:
- useful for sharpening specialized surfaces, but not a near-term driver of BMADX identity

### Avoid

- `superpowers` as a runtime/process model

Why:
- BMADX should borrow its packaging and activation strengths only
- copying the full method would collapse the boundary between `BMAD` and `BMADX`

## Suggested BMADX follow-ups

Short-term:
- adapt `Aider`-style context thrift into the public BMADX mental model for `X1/X2`
- create a few `Goose`-style reusable launch surfaces for common BMADX entry cases
- strengthen activation framing using lessons from `superpowers`, without adopting mandatory workflows

Medium-term:
- prototype a thin "what next?" helper inspired by `Task Master`, but backed by BMAD artifacts
- define a future "safe outputs" policy inspired by `GitHub Agentic Workflows`
- explore whether `OneRedOak`-style narrow review surfaces make sense for `X2` or `X4`

Do not do:
- do not add a BMADX-owned plan store
- do not add `.omx`-style runtime state
- do not make `X4` the normal path
- do not let BMADX replace BMAD as workflow owner

## Sources

Primary sources used for this research benchmark:

- [`Aider` chat modes](https://aider.chat/docs/usage/modes.html)
- [`Aider` repository map](https://aider.chat/docs/repomap.html)
- [`Goose` recipes docs](https://goose-docs.ai/docs/guides/recipes/)
- [`Goose` upstream repository](https://github.com/aaif-goose/goose)
- [`Task Master` upstream repository](https://github.com/eyaltoledano/claude-task-master)
- [`GitHub Agentic Workflows` docs](https://github.github.com/gh-aw/)
- [`GitHub Agentic Workflows`: how they work](https://github.github.com/gh-aw/introduction/how-they-work/)
- [`OneRedOak / Claude Code Workflows` upstream repository](https://github.com/OneRedOak/claude-code-workflows)
- [`superpowers` upstream repository](https://github.com/obra/superpowers)
- [`superpowers` Codex install notes](https://raw.githubusercontent.com/obra/superpowers/main/.codex/INSTALL.md)

Secondary watchlist context:

- [`OpenHands` product site](https://openhands.dev/)
- [`Archon` upstream repository](https://github.com/coleam00/Archon)
