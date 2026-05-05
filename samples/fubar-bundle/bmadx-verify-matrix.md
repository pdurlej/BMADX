# BMADX Verify Matrix for BMADX

| Gear | Minimum verify |
| --- | --- |
| X1 | 1-2 checks or the strongest available oracle |
| X2 | local checks plus optional review |
| X3 | verify aligned with BMAD and `project-context.md` |
| X4 | verify matrix plus ownership clarity plus bundle sanity |

## Non-technical proof

Every non-trivial result should say:

- what was checked,
- what failed, if anything,
- why it matters to the user/product,
- what the next safe step is.

## Recommended companion checks

- Use Oracle when a second-opinion architecture review would reduce risk.
- If `GUARDRAILS.md` exists, read it before red-zone edits and treat it as safety constraints.
- For Python repos, run `pyfallow` when available to catch boundary, dependency, cycle, and dead-code risks.
- For security-sensitive changes, prefer deterministic scanners such as secret scans and static analysis over model confidence.

Project path: $PROJECT_ROOT
