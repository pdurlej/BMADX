# BMADX Decision-Value Study v1

## Decision

Use a pre-registered, arm-blinded, three-arm study to measure whether BMADX adds
decision and planning value over ordinary reasoning, and what that value costs.
Do not use the earlier exact scorer as the primary outcome.

This study is ready for independent scenario audit. Live execution is blocked
until that audit is approved and committed before any model response exists.

## Estimands

Primary:

- BMADX plus real BMAD versus ordinary-reasoning placebo.

Mechanism checks:

- BMADX plus no-op healthy BMAD versus placebo estimates policy value;
- BMADX plus real BMAD versus BMADX plus no-op BMAD estimates dependency value.

The v1 scope is decision and planning quality. It does not prove implementation
quality. The hidden-repository requirements for that separate stage are frozen
in `benchmark/value-study/implementation-protocol-template-v1.json`.

## Design

- GPT-5.6 Sol at fixed `high`;
- 18 scenario clusters across frontend, backend, platform, auth, billing,
  privacy, data, database, delivery, and security;
- three arms and three repeats: 162 calls;
- unique opaque skill alias and hidden activation nonce per call;
- fresh prepared skill snapshot, runtime home, and workspace per call;
- model-call order randomized in complete scenario/repeat blocks;
- no gold labels or BMADX-authored exact score in the primary outcome;
- quality and safety failures are retained as outcomes;
- only integrity failures stop execution.

The runner refuses execution unless the operator passes
`--confirm-call-count 162`. It checkpoints every call and permits resume only
from the same commit and protocol, with no changes outside the run directory.

## Blinded Review

After a complete run, the packet builder removes arm names, case IDs, aliases,
nonces, token counts, latency, and setup metadata. Prohibited framework labels
are neutrally redacted and retained as a `blindability_failure` outcome rather
than causing post-run exclusion. A worse leakage rate blocks a positive claim.

Candidate IDs and candidate order use HMAC with a random 32-byte blinding key.
Keep that key outside the packet and unavailable to reviewers. Reveal and
archive it only after all reviews are signed, so the final analysis remains
reproducible without making the review mapping reversible in advance.

Five preregistered model families score every response independently: MiniMax,
DeepSeek, Qwen, GLM, and Kimi. Each family has exactly one primary vote and
must attest that the arm mapping was unavailable. Reviewers score absolute
dimensions before choosing a preferred candidate. The rubric is frozen in
`benchmark/value-study/rubric-v1.json`; panel identities, runtimes, health
gates, and call counts are frozen in
`benchmark/value-study/synthetic-panel-v1.json`.

Every reviewer receives its own deterministic candidate order. Eleven of 54
blocks per reviewer are repeated with a rotated order to measure position
stability. All five Ollama Cloud model families run through the same minimal Pi
runtime with tools, extensions, skills, project context, and session persistence
disabled. Stability calls never vote in the primary outcome. A failed health
threshold blocks a positive claim instead of silently excluding or replacing
the reviewer.

Primary outcome: within-block blinded preference, analyzed with a scenario-
cluster bootstrap. Secondary outcomes include all rubric dimensions, safety
omissions, fatal flaws, schema compliance, tokens, latency, and ceremony burden.

## Frozen Positive Claim Gate

`positive_value_added` requires all of the following:

- BMADX-real net blinded preference at least `+0.10` versus placebo;
- lower bound of the scenario-cluster bootstrap 95% interval above zero;
- mean pairwise reviewer preference agreement at least `0.60` by Jaccard score;
- no worse safety-omission or fatal-flaw rate;
- median token ratio no greater than `1.25`;
- median latency ratio no greater than `1.30`;
- ceremony-burden increase no greater than `0.5` on the 1-7 scale.

A clear negative preference interval or worse safety/fatal-flaw rate produces
`negative_or_harmful`. Everything else is `inconclusive`. The thresholds are
pre-registered; do not tune them after seeing results.

## Procedure

1. Give an independent reviewer the scenario files,
   `scenario-audit-prompt.md`, and `scenario-audit-v1.json`.
2. Apply any required scenario edits before live execution, regenerate hashes,
   and request a new audit. Do not preserve an approval across edits.
3. Commit the approved audit and verify the repo is clean.
4. Validate without calls:

   ```bash
   python3 benchmark/scripts/run_bmadx_value_study.py --validate-only
   ```

5. Run only after explicit quota approval:

   ```bash
   python3 benchmark/scripts/run_bmadx_value_study.py --confirm-call-count 162
   ```

6. If transport fails, fix only the transport condition and resume from the
   same commit:

   ```bash
   python3 benchmark/scripts/run_bmadx_value_study.py --confirm-call-count 162 --resume
   ```

7. Generate a one-run blinding key outside the repo and build the packet:

   ```bash
   openssl rand -hex 32 > /tmp/bmadx-value-blinding-key
   python3 benchmark/scripts/build_bmadx_value_review_packet.py \
     --protocol benchmark/value-study/protocol-v1.json \
     --summary benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/summary.json \
     --output-dir benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review \
     --blinding-key-file /tmp/bmadx-value-blinding-key
   ```

   Do not share the key, run summary, raw logs, repository branch, or arm map
   with reviewers.
8. Validate the synthetic panel without model calls:

   ```bash
   python3 benchmark/scripts/run_bmadx_synthetic_review_panel.py --validate-only
   ```

9. Run the frozen five-family panel only after explicit approval of its 325
   calls:

   ```bash
   python3 benchmark/scripts/run_bmadx_synthetic_review_panel.py \
     --packet benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/review-packet.json \
     --output-dir benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel \
     --confirm-call-count 325
   ```

10. Run `analyze_bmadx_value_study.py` with all five review files, the panel
summary, and the same key. Report the frozen
   verdict plus every failed gate, not only the headline preference. Archive
   the key only after reviews are final.

   ```bash
   python3 benchmark/scripts/analyze_bmadx_value_study.py \
     --protocol benchmark/value-study/protocol-v1.json \
     --summary benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/summary.json \
     --packet benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/review-packet.json \
     --panel-summary benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/panel-summary.json \
     --review benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/reviews/minimax-m3.json \
     --review benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/reviews/deepseek-v4-pro.json \
     --review benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/reviews/qwen-35.json \
     --review benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/reviews/glm-52.json \
     --review benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/review/synthetic-panel/reviews/kimi-k27-code.json \
     --blinding-key-file /tmp/bmadx-value-blinding-key \
     --output benchmark/value-study/runs/sol-bmadx-decision-value-v1-gpt-5-6-sol/analysis.json
   ```

## Why This Is More Objective

The prior canary was useful for harness integrity but used project-authored
exact labels and stopped on semantic safety disagreement. That design measured
agreement with BMADX assumptions and introduced informative missingness.

This design instead separates:

- manipulation and provenance, which remain deterministic;
- quality, which is judged blind and retained even when poor;
- mechanism value, through the no-op versus real BMAD decomposition;
- trade-offs, which can veto a positive quality result;
- implementation quality, which remains a separate hidden-test claim.

Residual limitations remain: model judges may share training-data and
evaluation biases, the task distribution is synthetic, model calls are not
guaranteed deterministic, all judges share the Ollama/Pi transport, and 18
clusters do not represent every repository. The study can support a cross-model
blinded-preference claim within that runtime. It cannot claim transport
independence, or that human beginners learn faster, feel less confused, or
complete more work; those remain later external-validation questions.
