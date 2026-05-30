# PRD — BMADX v0.2.7

## Summary

`v0.2.7` adds a Thinking Budget Advisor to BMADX. The advisor helps Codex
operators choose fit-for-purpose reasoning effort for a task without changing
BMADX routing semantics or mutating global Codex configuration.

The release preserves:

- `BMAD > BMADX`
- Codex-first support
- compact `X1/X2`
- hard-gated `X3/X4`
- rare `X4/FUBAR`
- no second plan store and no runtime-platform drift

## User Problem

Non-technical and low-friction builders often do not know when to spend more
model reasoning. They may overpay for trivial work or underthink red-zone work
such as auth, billing, data deletion, or migrations.

BMADX already chooses the lightest safe workflow. `v0.2.7` extends that
operator guidance by recommending how much thinking the current run deserves.

## Goals

- Recommend Codex reasoning effort after gear classification and compact gate.
- Use canonical effort values: `minimal`, `low`, `medium`, `high`, `xhigh`.
- Keep the recommendation advisory and per-run.
- Validate the recommendation in benchmark output.
- Prevent docs or model answers from suggesting persistent global config edits.

## Non-Goals

- Do not change `sync_bmadx.py` compact schema.
- Do not edit `~/.codex/config.toml`.
- Do not add profiles, hooks, MCP, plugins, subagents, or runtime state.
- Do not use thinking effort as a second router.
- Do not claim token savings until benchmark runs prove them.

## Contract

Default mapping:

- `X1`: `low`, fallback `medium`
- `X2`: `medium`
- `X2/X3` boundary: `high`
- `X3`: `high`
- `X4`: `xhigh` for rescue execution; `high` can be enough for classification-only prompts

Visible line when useful:

```text
Thinking: high — suggestion only for this Codex run.
```

For obvious `X1/X2`, BMADX should keep the recommendation silent unless the
user or benchmark asks for it.

## Acceptance Criteria

- Skill docs explain the advisor without weakening BMAD ownership.
- Public docs explain that BMADX does not change global Codex config.
- Benchmark scenarios include expected reasoning effort.
- Benchmark validation parses `Thinking:` lines and normalizes `extra_high` to
  `xhigh`.
- Benchmark validation rejects persistent config mutation language.
- Existing sync, installer, and benchmark tests still pass.
