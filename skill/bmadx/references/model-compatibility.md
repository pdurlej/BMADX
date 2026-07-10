# Codex Model Compatibility

Use this reference when a task asks which Codex model or reasoning effort fits
the selected BMADX gear. Model choice never changes the gear or BMAD gate.

## Runtime Preflight

GPT-5.6 requires Codex CLI `0.144.0` or newer. Check the installed skill and
local bundled model catalog without changing Codex configuration:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/check_codex_compat.py" --json
```

The runtime Codex catalog wins if it disagrees with
`references/model-profiles.json`. Catalog presence proves local CLI capability,
not account entitlement or BMADX benchmark promotion.

## Profile Policy

| Model | BMADX status | `X1` | `X2` | `X3` | `X4` |
| --- | --- | --- | --- | --- | --- |
| `gpt-5.5` | validated historical baseline | `medium` | `medium` | `high` | `xhigh` |
| `gpt-5.6-sol` | candidate | `medium` | `medium` | `high` | `high` |
| `gpt-5.6-terra` | candidate | `medium` | `medium` | `high` | `xhigh` |
| `gpt-5.6-luna` | candidate | `medium` | `medium` | `high` | `xhigh` |

Interpretation:

- Sol is the primary GPT-5.6 candidate for red-zone work, Rescue Mode, and
  final synthesis. Its lower-effort capability justifies testing `high` rather
  than automatically forcing `xhigh` for `X4`.
- Terra is the balanced everyday candidate. Do not promote its red-zone or
  Rescue behavior before healthy and degraded benchmark passes.
- Luna is the fast candidate for `X1/X2`. Keep `X3/X4` support claims pending
  red-zone, overwrite-safety, and Rescue Mode evidence.

These are reasoning recommendations, not execution permissions. A Luna run can
still classify a task as `X3`; the BMAD gate remains the authority on whether
the workflow may execute.

## Reasoning Levels

The current Codex catalog exposes:

- GPT-5.5: `low`, `medium`, `high`, `xhigh`
- GPT-5.6 Sol and Terra: `low`, `medium`, `high`, `xhigh`, `max`, `ultra`
- GPT-5.6 Luna: `low`, `medium`, `high`, `xhigh`, `max`

BMADX does not recommend `max` or `ultra` by default. They are explicit
experiments until repeated benchmarks prove a narrow use case. `ultra` also
implies automatic task delegation in the current Sol/Terra catalog, so it must
not silently turn BMADX into a model-orchestration policy.

## Promotion Rule

Keep all GPT-5.6 profiles at candidate status until each claimed scope passes:

- healthy and degraded BMAD profiles,
- fixed and advisor reasoning policies,
- core, boundary, non-technical, handoff, and goal/loop groups,
- zero red-zone under-escalation,
- zero ordinary-work `X4` false positives,
- compact `X1/X2` output,
- bounded goal/loop behavior,
- repeated runs rather than one canary.
