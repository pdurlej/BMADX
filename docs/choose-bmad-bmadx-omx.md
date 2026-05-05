# Choose BMAD vs BMADX vs OMX

Use this page when you want the shortest honest chooser.

| Situation | Best fit | Why |
| --- | --- | --- |
| You just need a trivial answer or a tiny one-off prompt | plain Codex | lowest setup, lowest ceremony |
| Process artifacts should drive the work from the start | BMAD | BMAD is the source of truth |
| You want lighter day-to-day Codex usage with BMAD-compatible guardrails | BMADX | compact routing plus verify discipline |
| You want a heavier runtime layer and broader orchestration | OMX | closer to that product category |
| You need an expert second opinion with repo files attached | Oracle with BMADX | Oracle reviews hard decisions; BMADX keeps routing and verification disciplined |
| You need deterministic Python architecture/codebase checks | pyfallow with BMADX | pyfallow adds static facts; BMADX routes the work |
| You need persistent repo-local failure lessons | Guardrails.md with BMADX | Guardrails.md records safety constraints; BMAD still owns process |

## Pick BMADX when

- you already have BMAD installed,
- you want less manual process selection in Codex,
- most of your work is normal bounded change, not full-process planning,
- you still want guardrails and a rare rescue path.

BMADX should ask the Architecture Guardrail Card only when it changes the safe
mode. Normal bounded work stays compact.

## Pick BMAD when

- you already know the task is BMAD-heavy,
- PRD/architecture/story artifacts should drive execution,
- process authority matters more than low-friction routing.

## Pick OMX when

- you actually want runtime-heavy workflow tooling,
- you want that product shape on purpose,
- BMADX feels intentionally too small for your use case.

## Pick plain Codex when

- the task is tiny,
- you do not need BMAD discipline,
- setup would cost more than the task.

## Use companion tools when

- use Oracle when an architecture, product, or debugging decision needs a stronger second opinion with real repo context,
- use pyfallow when a Python repo needs import, dependency, boundary, cycle, or likely-dead-code signals,
- use Guardrails.md-style files when a repo has repeated failure lessons or hard constraints that agents must remember,
- use CI, tests, static analysis, and secret scans for hard facts BMADX cannot infer from prompting alone.
