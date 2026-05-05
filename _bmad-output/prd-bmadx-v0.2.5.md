# PRD — BMADX v0.2.5

## Summary

`v0.2.5` is a public release surface for the non-technical architecture
guardrail stack. It does not change BMADX routing semantics. It packages the
post-`v0.2.4` hardening and the new Architecture Guardrail Card, red-zone
defaults, non-technical benchmark scenarios, and ecosystem stance into a proper
GitHub release.

## Goals

- Make GitHub Releases match the current `main` and local installed skill.
- Replace outdated `lazy overlay` public wording with low-friction architecture
  guardrails for non-technical builders.
- Publish the companion stack clearly: Oracle, BMAD, BMADX, Guardrails.md,
  pyfallow, CI/tests.
- Keep `BMAD > BMADX`, keep BMADX lighter than OMX, and keep `X4/FUBAR` rare.

## Non-Goals

- No new runtime platform.
- No second plan store.
- No new gate semantics.
- No fresh public claim that token benchmarks changed after `v0.2.4`; the
  runner gained scenarios, but historical model runs remain historical.

## Acceptance Criteria

- `skill_version` is `0.2.5` in the manifest and compact gate.
- README, roadmap, FAQ, quickstart, project context, changelog, tag, and GitHub
  Release all point to `v0.2.5`.
- GitHub About description no longer says `lazy overlay`.
- Local Codex skill is reinstalled and reports `0.2.5`.
- Unit/smoke tests pass.
