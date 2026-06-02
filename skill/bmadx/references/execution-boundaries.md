# Execution Boundaries

Use this reference only when the task asks about execution surfaces, model
experiments, adapters, or platform strategy.

## Codex-first

BMADX is built for Codex:
- Codex Skills
- `CODEX_HOME`
- compact local gate
- `codex exec` benchmarkability

Do not mutate global Codex config as part of BMADX routing.

## Claude Code

Claude Code is watch/prototype only. Do not present it as near-term parity.

Reasons:
- `CLAUDE.md` can override routing context,
- hooks can add hidden automation,
- subagents do not reliably inherit skills,
- MCP can change risk and permissions,
- plugins/settings can drift BMADX toward runtime-platform behavior,
- `claude -p` may not match interactive behavior.

BMADX must not install Claude hooks, MCP, plugins, settings, agents, or
persistent memory as a default path.

## Local and Cheap Model Experiments

Local or cheap models may be tested through Codex OSS providers. Treat them as
experiments until they pass the same gates as GPT-5.5:

- routing correctness,
- compact `X1/X2`,
- red-zone `X3` minimum,
- `X4` rarity,
- degraded BMAD hard-gate behavior,
- useful explanations for non-technical owners.

`PMAX X` is the named experiment lane for cheaper candidates. It is not a
product-default lane.

Cheap models may assist with:
- bounded discovery,
- draft alternatives,
- repo mapping,
- diff review,
- verification support.

The main BMADX/Codex lane keeps routing decisions, synthesis, and final
responsibility.

## Platform Drift Guardrails

BMADX must not become:
- `.omx`-style runtime state,
- a second plan store,
- an agent zoo,
- a CI platform,
- a tool-permission manager,
- a broad orchestration runtime.

BMADX exports risk and proof. BMAD owns process. Deterministic checks own hard
facts.

