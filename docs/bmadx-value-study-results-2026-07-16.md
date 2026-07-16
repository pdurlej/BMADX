# BMADX Decision-Value Study: July 16, 2026

## Verdict

**Inconclusive before unblinding. No BMADX value-added claim is allowed from
this run.**

The generation stage completed all 162 GPT-5.6 Sol calls across three blinded
arms. The synthetic review stage then completed all 325 scientific judgments
with five Ollama Cloud model families through Pi. However, two reviewers did
not pass the preregistered candidate-order stability threshold, so the protocol
blocked unblinding and final arm comparison.

This is a valid negative result for the evaluation system, not evidence that
BMADX has no value. The study did not reach the stage that estimates value.

## Final panel gate

| Reviewer | Preference-order Jaccard | Minimum | Score delta | Maximum | Health |
| --- | ---: | ---: | ---: | ---: | --- |
| Gemma 4 31B | 0.712 | 0.700 | 0.134 | 1.000 | pass |
| Mistral Large 3 | 0.727 | 0.700 | 0.216 | 1.000 | pass |
| Qwen 3.5 | 0.727 | 0.700 | 0.424 | 1.000 | pass |
| GLM 5.2 | 0.591 | 0.700 | 0.468 | 1.000 | fail |
| Nemotron 3 Ultra | 0.652 | 0.700 | 0.710 | 1.000 | fail |

Operational totals:

- 325/325 scientific judgments completed;
- 329 provider attempts;
- 3 scientific calls required at least one retry;
- 3/5 reviewers passed every frozen health gate;
- 0 arms revealed;
- 0 positive performance claims allowed.

Machine-readable evidence:

- [`panel-summary-v1.13.json`](../benchmark/value-study/results/panel-summary-v1.13.json)
- [`panel-gate-v1.13.json`](../benchmark/value-study/results/panel-gate-v1.13.json)
- [`synthetic-panel-v1.13.json`](../benchmark/value-study/synthetic-panel-v1.13.json)
- [`review-runner-amendment-v1.13.json`](../benchmark/value-study/review-runner-amendment-v1.13.json)

## What the run established

The harness now demonstrates behavior that earlier BMADX comparisons did not:

- arm identities remain unavailable to model reviewers;
- absolute scores are collected before preferences;
- candidate order is independently varied and tested;
- incomplete or malformed judgments cannot silently enter the analysis;
- schema failures, transport failures, and valid judgments have separate retry
  accounting;
- every failed provider attempt remains hash-bound and auditable;
- reviewer instability blocks a favorable claim instead of being removed after
  results are visible.

The run also showed that a large synthetic panel is operationally expensive and
fragile. Schema-only and transport retries added little volume, but two models
still changed preferences too often when candidate order changed.

## What the run did not establish

It did not establish that BMADX is better or worse than plain Sol at `medium`,
`high`, or `xhigh`. It also did not establish that non-technical builders ship
better applications, learn faster, or make fewer mistakes with BMADX.

Those questions require a healthy panel followed by the frozen arm analysis,
and eventually an implementation benchmark or novice-user study. Earlier exact
scorer and causal-canary results remain directional engineering evidence only.

## Who should use BMADX now

BMADX remains appropriate as an opt-in workflow guardrail for builders who want
Codex to distinguish tiny changes, bounded product work, high-risk work, and
rare rescue situations. Its public value proposition is currently based on the
inspectable routing contract, read-only BMAD dependency gate, explicit goals,
bounded loops, and verification discipline.

It should not yet be selected because of a claimed measured productivity or
quality advantage. Users who already route work safely and prefer direct Codex
control may reasonably stay with plain Codex.

## Next benchmark

The next preregistered run should improve judge reliability before spending on
another 325-call panel. It should use a separate reviewer qualification set,
require repeated order-stability canaries across more than one block family,
and freeze the qualified panel before any study candidates are scored. The
current arm mapping must remain sealed and must not be reused to tune that
qualification set.

The original one-run blinding key was not retained. An exact post-review
redacted-payload hash map can reconstruct the mapping, but it was not used here
because the panel failed before unblinding. Future runs should retain the key in
an approved external store to remove this protocol deviation.
