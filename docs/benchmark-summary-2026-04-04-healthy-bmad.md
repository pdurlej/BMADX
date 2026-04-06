# Benchmark Summary — 2026-04-04 (`BMADX healthy`)

## Goal

Check how `BMADX v0.2.1` behaved after:
- the true `X1/X2` fast path,
- compact gate output from `sync_bmadx.py`,
- a warm-up sync that populated the last healthy BMAD cache.

## Method

- runner: [`benchmark/scripts/run_bmadx_benchmark.py`](../benchmark/scripts/run_bmadx_benchmark.py)
- profile: `healthy`
- model: `gpt-5.4`
- reasoning effort: `medium`
- MCP startup: `no servers`
- before the scenarios, the runner executed `sync_bmadx.py sync --json` to warm the healthy BMAD cache

Summary JSON:
- [`benchmark/summary-2026-04-04-healthy-bmad.json`](../benchmark/summary-2026-04-04-healthy-bmad.json)

## Results

| Scenario | `BMADX degraded` | `BMADX healthy` | Delta |
| --- | --- | --- | --- |
| `X1` | `10492` | `10306` | `-1.8%` |
| `X2` | `10334` | `12472` | `+20.7%` |
| `X3` | `12366` | `6504` | `-47.4%` |
| `X4` | `10627` | `10354` | `-2.6%` |
| average | `10954.75` | `9909.0` | `-9.5%` |

## What worked

- the runner recreated a clean `CODEX_HOME` and stored a separate `healthy` dataset
- `X1/X2` really did use `check --gear ... --compact`
- `X3/X4` kept correct classification and full BMAD-first workflow behavior
- `X3` became much cheaper under healthy BMAD because the degraded-gate overhead disappeared

## What did not hit the target

The plan wanted `X1` and `X2` token counts to drop by at least `20%` compared
to the earlier rerun.

That did not happen:
- `X1` only dropped `1.8%`
- `X2` increased `20.7%`

## Reading

`v0.2.1` delivered the infrastructure:
- BMAD-first source of truth
- compact gate
- repo-tracked runner
- separate `healthy` dataset

It did not yet deliver compact enough `X1/X2` answers. The next step clearly
had to target the skill response contract rather than the gate itself.
