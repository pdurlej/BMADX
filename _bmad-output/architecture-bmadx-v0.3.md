# Architecture — BMADX v0.3

## Decision

Introduce a model-profile policy layer after gear classification and BMAD gate
evaluation. Do not introduce a model router.

```text
user task
  -> BMADX gear X1..X4
  -> compact BMAD gate
  -> active-model capability/profile lookup
  -> model-aware thinking advice
  -> optional surface-aware goal/loop contract
  -> execution and deterministic verification
```

## Source-of-Truth Order

1. BMAD owns process, architecture workflow, and hard-gate readiness.
2. The active Codex model catalog owns runtime-supported reasoning levels.
3. BMADX `model-profiles.json` owns candidate status and gear-to-effort policy.
4. Repeated benchmark summaries own promotion evidence.
5. Public docs describe only what the preceding layers prove.

If layers disagree, the earlier layer wins. In particular, a strong model or
high thinking level cannot bypass a red BMAD gate.

## Components

### Model profile manifest

`skill/bmadx/references/model-profiles.json` is structured policy data. It
records candidate status, minimum CLI, observed supported reasoning, and
advisor mapping by gear.

It is not the runtime capability source. The compatibility checker compares it
with `codex debug models --bundled` and reports drift.

### Compatibility checker

`skill/bmadx/scripts/check_codex_compat.py`:

- parses `codex --version`,
- reads the bundled model catalog,
- reports only version and capability metadata,
- never reads or prints auth values,
- can fail closed with `--require-gpt56`.

### Benchmark model policy

`benchmark/scripts/bmadx_model_profiles.py` loads the same manifest and exposes
pure helpers for profile lookup, advisor effort, prompt contract, and option
validation.

The benchmark runner:

- requires `--model`,
- validates known model/effort/CLI combinations before remote execution,
- records a profile snapshot in summary JSON,
- computes expected `Thinking:` from model plus gear,
- honors source `CODEX_HOME` before creating an isolated temporary home.

### Performance verifier

Coverage is evaluated per observed model. Claim grouping key is:

```text
(model, BMAD profile, scenario group, reasoning policy)
```

Fixed/advisor pairs from different models cannot compare.

### Goal and loop validator

Goal validation now separates:

- recommendation (`Goal: yes/no`),
- termination quality (success or blocked stop condition),
- runtime drift.

Loop validation requires both a positive recommendation and a bounded contract
with a numeric maximum or explicit bounded marker plus stop criteria.

## Model Policy

| Model | Status | Advisor map |
| --- | --- | --- |
| GPT-5.5 | validated historical baseline | `medium, medium, high, xhigh` |
| GPT-5.6 Sol | candidate | `medium, medium, high, high` |
| GPT-5.6 Terra | candidate | `medium, medium, high, xhigh` |
| GPT-5.6 Luna | candidate | `medium, medium, high, xhigh` |

The four values correspond to `X1..X4`. `max/ultra` remain explicit experiments
and are never selected by the advisor in v0.3.

## Failure Behavior

- old CLI: fail before benchmark execution with minimum-version guidance,
- unsupported effort: fail before model invocation,
- catalog/profile drift: compatibility checker warns or fails in required mode,
- unavailable account entitlement: model invocation may still fail; catalog
  presence is not presented as entitlement proof,
- BMAD drift: classify but block `X3/X4` execution,
- repeated approval/hard-stop goal blocker: stop and report blocked state,
- mixed-model claim inputs: report missing same-model pairs.

## Portability

No user-specific absolute path belongs in committed outputs. Use
`${CODEX_HOME:-$HOME/.codex}` in documentation and `CODEX_HOME` discovery in
Python. Temporary benchmark homes continue to isolate user config, plugins,
apps, rules, and runtime state.

## Verification

- unit tests for profile parsing, minimum CLI, capability drift, advisor map,
  goal stop conditions, bounded loops, and claim isolation,
- existing installer, sync, handoff schema, runner, and performance tests,
- local compatibility check on the installed Codex CLI,
- live model canaries only after deterministic checks and operator approval.

## Rollback

All repo changes are additive or policy-local. Revert the v0.3 commit to return
to GPT-5.5-only behavior. Historical benchmark JSON remains untouched. The
global CLI update has a separate binary backup and is not controlled by this
repository.
