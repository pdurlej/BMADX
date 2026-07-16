# Plain Sol vs BMADX A/B - 2026-07-12

Status: historical directional evidence. The original v1 summary is frozen and
must not be silently rescored. An external GPT-5.6 Sol Pro review found material
treatment-fidelity, scorer-sensitivity, and provenance limits; see
[Oracle review response](oracle-review-response-2026-07-12.md).

## Question

Does BMADX with a healthy BMAD dependency improve GPT-5.6 Sol workflow
decisions versus plain Sol at fixed `medium`, `high`, and `xhigh` effort?

## Protocol

- model: `gpt-5.6-sol`
- assigned arms: clean plain Sol and Sol prompted to use local BMADX after a
  healthy-fixture warmup
- efforts: fixed `medium`, `high`, and `xhigh`
- scenarios: the same 15 task shapes in each cell
- repeats: `2`, producing 30 cases per cell and 180 total model calls
- order: repeat 1 and repeat 2 were separate resume segments; each segment
  shuffled arm and effort with seed `560712`
- output: one shared framework-neutral JSON contract
- blinding: neither task prompt exposed the expected route; the BMADX treatment
  intentionally exposed its internal X1-X4 ontology through the assigned skill
- scoring: project-authored exact process/risk agreement, strict schema and
  response shape; handoff/goal/loop were scored only for positive reference cases
- raw evidence: 360 `.txt`/`.log` files, plus a checkpointed summary

Artifacts:

- [A/B summary](../benchmark/ab-summary-2026-07-12-gpt-5-6-sol-causal-neutral-v1.json)
- runner: `benchmark/scripts/run_sol_bmadx_ab.py`
- neutral contract: `benchmark/scripts/sol_bmadx_ab_contract.py`

## Results

| Effort | Plain perfect | Assigned BMADX perfect | Delta | Plain score | BMADX score | Ordinal underclassification: plain / BMADX | Token cost | Latency cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `medium` | 22/30 | 27/30 | +16.67 pp | 91.43% | 97.86% | 4 / 2 | +29.46% | +19.85% |
| `high` | 23/30 | 27/30 | +13.33 pp | 92.86% | 97.86% | 4 / 1 | +50.99% | +20.61% |
| `xhigh` | 23/30 | 28/30 | +16.67 pp | 92.86% | 98.57% | 4 / 2 | +28.72% | +14.42% |

Matched primary-score outcomes (`BMADX win / tie / loss`):

- `medium`: `8 / 21 / 1`
- `high`: `4 / 26 / 0`
- `xhigh`: `6 / 24 / 0`

The repeat-level direction was consistent. The assigned BMADX arm had a higher full-pass count in
both repeats at every effort except one medium matched case where plain scored
higher. Per-effort samples are still small: these directional results are not
treated as a population-level statistical claim.

## Where The Scorer Differed

The assigned BMADX arm's clearest exact-oracle gains were concentrated in four
workflow-boundary scenarios:

- goal-aware auth cleanup: plain passed 2/6; BMADX passed 6/6,
- onboarding variant: plain passed 0/6; BMADX passed 4/6,
- generic X4-shaped scaffold task: plain passed 0/6; BMADX passed 3/6,
- bounded migration repair loop: plain passed 1/6; BMADX passed 4/6.

The other 11 scenarios had no aggregate arm difference. Across efforts, most
score-point gain came from exact risk labels; handoff and goal had no arm
difference. This is scorer-sensitive directional evidence, not proof of broad
goal discipline or universal workflow quality.

## Decision

The supplied summary supports one narrow statement: the assigned BMADX arm had
higher agreement with the project-authored exact scorer on this fixed suite.
Do not publish this run as causal proof of activated BMADX or healthy BMAD.

Keep `high` as the provisional Sol planning baseline. Within the assigned BMADX arm, `high` and
`medium` both passed 27/30, while `xhigh` passed 28/30. The one-case xhigh gain
is too small to justify making it default; xhigh also used 6.60% more tokens
and 1.56% more latency than high.

## Limits

- The healthy fixture was used for warmup but was not pinned in every v1 model
  call environment. The treatment name therefore overstates demonstrated fidelity.
- Per-call hidden skill activation was not measured.
- The intervention combines explicit `$bmadx` wording, skill availability,
  ontology exposure, local state and BMAD setup; component causality is unsupported.
- The second repeat was appended in a fresh resume segment rather than produced
  by one immutable 180-call manifest.
- Homes and workspace were reused within each segment without mutation hashes.
- Negative handoff/goal/loop false positives were not scored, reasons were only
  shape-checked, and the variable score denominator overweighted goal/loop cases.
- It measures workflow decisions, not implementation quality.
- The scenarios and reference answers are authored by this project and may
  favor its process philosophy even though the response schema is neutral.
- Two repeats expose direction and obvious instability, not broad statistical
  generalization.
- Codex's human-readable token footer is an all-token operational measure, not
  a clean input/output billing decomposition.
- Codex logs the isolated BMADX `CODEX_HOME` and explicit `$bmadx` treatment but
  does not expose hidden skill injection as a shell read event. The treatment
  setup verifies `SKILL.md` exists only in the BMADX home; this is strong setup
  evidence, not direct per-call skill-read telemetry.

## Implementation Benchmark

The next benchmark should use 6-10 small, isolated repositories with hidden,
executable tests. Each task should run through the same six cells and be scored
without framework labels on:

1. hidden test pass rate and regression count,
2. required behavior coverage,
3. unsafe or out-of-scope mutations,
4. diff size and maintainability review,
5. rollback and verification quality,
6. tokens, latency, and retries to green.

Use fresh worktrees, identical starting commits, fixed tool permissions, and a
hard time/token budget. Randomize cell order per task, keep graders blind to the
arm, stop a cell on destructive behavior or budget exhaustion, and report both
intention-to-treat and completed-run outcomes.

## Oracle Consultation

Initial Oracle browser automation attempts failed before prompt commit. The
operator later supplied a completed GPT-5.6 Sol Pro review. It verified all
headline arithmetic, rated the arm effect directional, rejected component-level
causality, and identified the fidelity and scorer limits documented above.
