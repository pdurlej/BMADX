# PRD — BMADX v0.2.6

## Summary

`v0.2.6` makes BMADX easier to use alongside broad orchestration workflows
without turning BMADX into a runtime platform.

BMADX remains the narrow Codex-first lane:
- classify the task,
- check the BMAD-backed gate,
- keep `X1/X2` compact,
- escalate risky work into BMAD,
- keep `X4/FUBAR` as rare Rescue Mode.

The new release adds a public handoff contract for tasks that should move into a
broad orchestrator after BMADX has identified risk, proof requirements, and open
questions.

## Goals

- Define a portable broad-orchestrator handoff packet.
- Explain cooperation with generic broad orchestration patterns such as
  Gastown-style workflows without depending on a private orchestrator.
- Keep `BMAD > BMADX` explicit.
- Keep `X4/FUBAR` rare and prevent a hidden `X5`.
- Improve subagent guidance so operators can reduce time-to-value on `X1/X2`
  without spawning unnecessary workers.
- Add benchmark checks that catch handoff runtime drift.

## Non-Goals

- No second plan store.
- No `.omx`-style runtime.
- No worker dispatch.
- No model-lane selection.
- No arbiter assignment.
- No hooks, MCP, plugins, or installed subagents.
- No Claude Code parity claim.
- No replacement of BMAD as process source of truth.

## User-Facing Changes

- Public docs explain when BMADX should stay narrow and when to recommend a
  broad-orchestrator handoff.
- The skill can emit one compact `Handoff: yes/no` line when the task shape
  needs external broad review.
- A JSON schema documents the handoff packet fields and explicitly forbids
  runtime orchestration fields.
- Samples show `X3` auth architecture review and `X4` migration recovery
  handoff packets.
- Subagent guidance now favors one bounded helper for `X2` discovery or
  verification when it saves time and does not block the main lane.

## Acceptance Criteria

- Skill version is `0.2.6`.
- `sync_bmadx.py check --gear X3 --compact` remains green when BMAD is healthy.
- Public repo contains no private-orchestrator names.
- Handoff docs position broad orchestration as a receiving system, not BMADX
  runtime behavior.
- Benchmark tests cover handoff routing and reject runtime details such as
  worker lanes, model names, dispatch commands, hooks, MCP, plugins, subagents,
  and runtime state.
- Local installed Codex skill reports `skill_version=0.2.6`.
