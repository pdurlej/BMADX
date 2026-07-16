# Oracle Review Response - 2026-07-12

GPT-5.6 Sol Pro independently reviewed the 180-call plain-Sol versus assigned
BMADX experiment. Its arithmetic recomputation matched the stored summary. Its
methodology criticism is accepted.

## Accepted Findings

| Finding | Disposition |
| --- | --- |
| Healthy fixture used for warmup but not every model-call environment | Fixed in A/B runner v2; inherited BMAD variables are cleared and the pinned fixture is passed to every treatment call. |
| Review ZIP omitted scenarios and raw evidence | Accepted; future review bundle includes all scenarios and a preselected discordant/concordant raw sample. |
| Two resume segments were described too loosely | Corrected in the historical report; v2 resume requires an exact experiment-manifest and runtime-provenance match. |
| Skill activation was not directly observed | Accepted; v1 remains intention-to-treat directional evidence. A nonce-based opaque-skill manipulation check is required for the next causal run. |
| Exact scorer is BMADX-authored and scorer-sensitive | Accepted; v2 scores explicit positive and negative handoff/goal/loop truth, uses a fixed denominator, and labels ordinal disagreements honestly. Held-out independent adjudication remains required. |
| Shared homes/workspace allowed carryover | Fixed in v2 with fresh per-call home/workspace clones and before/after hashes. |
| Precomputed gate remained route-conditioned | Fixed in the general runner: classification is committed first, then the gate runs on the model-selected route. |
| Provenance, timeout, atomic checkpoint and naming were weak | Fixed in v2 with manifest/source hashes, CLI/fixture/skill provenance, explicit timeout, atomic replace and model/date/seed artifact names. |

## Claim Policy

The v1 result may be described only as higher agreement with the project-authored
exact scorer in the assigned BMADX arm on the fixed 15-scenario suite. It is not
proof that BMADX activated, that BMAD contributed, or that implementation quality
improved.

`high` remains a provisional operational default. `xhigh` produced a net one-case
gain over high, with two paired wins, one loss, higher aggregate cost and no
credible dominance.

## Next Decisive Run

The next causal benchmark should use opaque randomized skill aliases and three
arms at `high`: placebo workflow, BMADX policy with a healthy-shaped no-op BMAD
stub, and BMADX with pinned real BMAD. Every call must return an unscored hidden
activation nonce. Use fresh immutable homes, held-out independently adjudicated
scenarios, explicit negative expectations and blinded review of discordant cases.

Only after treatment activation and the high-effort decomposition are healthy
should medium versus xhigh be repeated. Implementation-quality claims require a
separate hidden-test repository benchmark.
