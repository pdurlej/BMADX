# Benchmark Summary — 2026-04-05 (`BMADX v0.2.2`)

## Goal

Verify that `v0.2.2` actually delivered:
- a shorter response contract for obvious `X1/X2`,
- mixed-metric benchmark guardrails,
- no semantic regression in `X3/X4`,
- a boundary case where `X2/X3` still escalates correctly to `X3`.

## Artifacts

- [`../benchmark/summary-2026-04-05-healthy-bmad.json`](../benchmark/summary-2026-04-05-healthy-bmad.json)
- [`../benchmark/summary-2026-04-05-degraded-bmad.json`](../benchmark/summary-2026-04-05-degraded-bmad.json)
- raw logs in [`../benchmark/raw`](../benchmark/raw)

## Healthy

Core `X1..X4`:
- `X1`: `8630` tokens, `3` lines, `353` chars, `format_pass=true`, `token_pass=true`, `reference_budget_pass=true`
- `X2`: `8770` tokens, `13` raw lines / format pass, `890` chars, `format_pass=true`, `token_pass=true`, `reference_budget_pass=true`
- `X3`: `5385` tokens, `routing_pass=true`
- `X4`: `10377` tokens, `routing_pass=true`
- core average: `8290.5`

Boundary:
- `X2/X3`: `X3` selected correctly, `routing_pass=true`, reference reads allowed

## Degraded

Core `X1..X4`:
- `X1`: `5270` tokens, `format_pass=true`, `token_pass=true`
- `X2`: `8768` tokens, `format_pass=true`, `token_pass=true`
- `X3`: `8786` tokens, correct classification under degraded BMAD
- `X4`: `5387` tokens, correct classification under degraded BMAD
- core average: `7052.75`

Boundary:
- `X2/X3`: still escalates correctly to `X3`

## Conclusion

`v0.2.2` delivered the immediate roadmap goal:
- `X1` and `X2` fit their token budgets,
- `X1/X2` do not read reference docs in the happy path,
- the runner now reports a mixed-metric summary,
- `X3/X4` keep BMAD-first semantics,
- the boundary case protects against over-compressing `X2`.

The next sensible stage is no longer further shrinking `X1/X2`, but improving
benchmark governance and making `X4` easier to productize in external repos.
