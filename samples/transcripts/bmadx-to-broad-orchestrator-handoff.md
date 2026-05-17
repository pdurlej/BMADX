# BMADX to Broad Orchestrator Handoff

This transcript shows the intended boundary. BMADX does not run a broad
orchestrator; it emits a small packet that another system can consume.

## User

```text
Use BMADX. Add Google login. The repo has two auth systems and I am not sure
which one owns sessions. I want a broad architecture review before code changes.
```

## BMADX

```text
Choice: X3 / BMAD-heavy
Why: Google login touches auth, sessions, external provider setup, and user data privacy.
Handoff: yes — broad architecture review is useful because ownership and proof are unclear.
Execution gate: allowed
Proof: identify auth owner, callback/session strategy, tests, rollback plan, and human review for provider setup.
```

If the user asks for a machine-readable packet, BMADX emits
`bmadx_handoff.v1`. The receiving orchestrator re-checks privacy, hard stops,
and route selection under its own policy.

## Boundary

BMADX did not:
- choose model names,
- dispatch workers,
- assign an arbiter,
- create runtime state,
- bypass BMAD.

BMADX only exported risk, proof, and open questions.
