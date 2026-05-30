# FAQ

## Do I need BMAD first?

Yes. BMADX depends on `bmad-method-codex` and does not replace it.

## Do I have to choose `X1/X2/X3/X4` myself?

Usually no. The normal use pattern is to describe the task in plain language and let BMADX choose the lightest safe mode.

## Does BMADX require GPT-5.5?

No. BMADX `v0.2.7` is tuned for Codex on GPT-5.5, but the installer does not change your Codex model config. Benchmarks should record the model explicitly so GPT-5.4 and GPT-5.5 runs stay comparable.

## Does BMADX change my Codex thinking level?

No. BMADX can recommend a per-task thinking budget, such as `low`, `medium`,
`high`, or `xhigh`, but it does not edit global Codex config. Treat the
recommendation as fit-for-purpose guidance for the current run.

## Does BMADX work with broad orchestrators?

Yes, through a packet contract. BMADX can export gear, BMAD gate state, risk
flags, privacy guess, proof needs, forbidden changes, and open questions to a
separate broad orchestrator. This works with Gastown-style orchestration models
or private review stacks, but BMADX does not ship worker dispatch, model lanes,
arbiters, MCP, hooks, plugins, subagents, or runtime state.

## When does `X4/FUBAR` happen?

Only when the repo or rollout needs extra structure: messy scope, unclear ownership, or a need for scaffold bundle artifacts. It is intentionally rare.

## Is BMADX cheaper than BMAD?

Not in every case. The honest public claim is that BMADX looks strongest against OMX, while BMAD still wins as the upstream process owner and often on raw token cost.

## Why not just use OMX?

Because BMADX is intentionally lighter. If you want a heavier runtime, OMX is closer to that product.

## Does BMADX support Claude Code?

Not currently. BMADX is Codex-first because its compact gate, skill install
path, and benchmark runner are built around Codex. Claude Code has different
native surfaces such as `CLAUDE.md`, hooks, subagents, MCP, plugins,
permissions, and `claude -p`; a simple port would be misleading. The current
stance is watch/prototype, not ship.

## Can BMADX run on Mistral or other local models?

Only experimentally through Codex OSS providers. If Codex can run a local model
through Ollama or LM Studio, the benchmark runner can test BMADX routing against
that model. Passing a local-model experiment does not make it the default
product target; it must still pass format, routing, red-zone, and Rescue Mode
rarity checks.

## Can I use BMADX if I am not a developer?

Yes. BMADX is explicitly meant for people who understand the product problem but
do not want to manually design the software process or architecture workflow.
You still need Codex and BMAD installed, but you should be able to describe the
task in plain English and let BMADX pick the lightest safe mode.

## Does BMADX make architecture decisions for me?

It gives Codex architecture guardrails, not unchecked authority. Small changes
stay compact, larger architecture-shaped work escalates to BMAD, and Rescue Mode
exists only when a messy repo needs extra structure.

## What is the Architecture Guardrail Card?

It is a five-question check BMADX uses to keep Codex from guessing architecture:
what outcome is protected, which system area owns the change, which pattern to
follow, what could break, and what proof a non-technical owner can understand.
For obvious `X1/X2`, BMADX should answer it silently.

## When should BMADX force BMAD?

Use `X3` minimum for auth, billing, payments, permissions, migrations, data
deletion, secrets, production config, user data privacy, multi-tenant access,
webhooks, encryption, admin roles, or compliance unless the change is purely
textual.

## Should I use pyfallow or Guardrails.md with BMADX?

Yes, when they fit. `pyfallow` is a good companion for Python codebase
intelligence. Guardrails.md-style files are useful for repo-local failure
lessons and hard constraints. Neither replaces BMAD as the process source of
truth.

## Where does Oracle fit?

Oracle is the second-opinion layer. Use it when a decision is architecture-heavy,
ambiguous, or outside the non-technical builder's expertise. It can bundle the
right files and ask a stronger model for review, but BMADX still has to route
the work and verify accepted advice against BMAD artifacts and tests.

## What should I do right after install?

Paste one of the prompts from [What to Paste into Codex](what-to-paste-into-codex.md).
