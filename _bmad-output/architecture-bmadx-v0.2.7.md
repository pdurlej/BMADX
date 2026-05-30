# Architecture — BMADX v0.2.7

## Summary

`v0.2.7` keeps the existing Codex skill architecture and adds one pure advisory
layer: the Thinking Budget Advisor.

The advisor is deliberately downstream of the existing flow:

```text
classify gear -> compact gate -> thinking budget recommendation -> response
```

It does not change execution permission, BMAD dependency checks, compact JSON
schema, or install behavior.

## Components

### Skill contract

`skill/bmadx/SKILL.md` embeds the default effort mapping so obvious `X1/X2`
does not need reference reads.

`skill/bmadx/references/thinking-budget.md` contains boundary rules, display
policy, and anti-drift constraints.

### Benchmark validation

`benchmark/scripts/bmadx_benchmark_scenarios.py` adds
`expected_reasoning_effort` to scenario specs.

`benchmark/scripts/bmadx_benchmark_validation.py` parses a `Thinking:` line,
normalizes aliases, checks the expected value, and rejects persistent config
mutation language.

`benchmark/scripts/run_bmadx_benchmark.py` asks benchmark responses to include
one `Thinking:` line and records observed/expected effort in summary cases.

### Public docs

`docs/thinking-budget-advisor.md` explains the feature to users as cost-control
guidance, not a new workflow mode.

## Invariants

- Gear remains the router.
- BMAD remains the process owner.
- `X3/X4` hard gates remain hard.
- `xhigh` does not make `X4` normal.
- BMADX never writes or instructs edits to global Codex config.
- Thinking-budget benchmark checks extend existing mixed metrics; they do not
replace routing, token, reference-budget, or handoff validation.

## Verification

Required checks:

- `python3 benchmark/scripts/test_run_bmadx_benchmark.py`
- `python3 skill/bmadx/scripts/test_sync_bmadx.py`
- `python3 scripts/test_install_bmadx.py`
- `python3 scripts/test_install_and_verify_bmadx.py`
- `python3 skill/bmadx/scripts/sync_bmadx.py check --gear X3 --compact`

If benchmark results are published, run healthy and degraded profiles before
making token-savings claims.
