# Benchmark Summary — 2026-04-05 (`BMADX v0.2.2`)

## Cel

Sprawdzić, czy `v0.2.2` dowozi:
- krótszy kontrakt odpowiedzi dla obvious `X1/X2`,
- mixed-metric benchmark guardrails,
- brak regresji semantyki `X3/X4`,
- boundary case `X2/X3`, który nadal poprawnie eskaluje do `X3`.

## Artefakty

- [`benchmark/summary-2026-04-05-healthy-bmad.json`](../benchmark/summary-2026-04-05-healthy-bmad.json)
- [`benchmark/summary-2026-04-05-degraded-bmad.json`](../benchmark/summary-2026-04-05-degraded-bmad.json)
- raw logs w [`benchmark/raw`](../benchmark/raw)

## Healthy

Core `X1..X4`:
- `X1`: `8630` tokenów, `3` linie, `353` znaki, `format_pass=true`, `token_pass=true`, `reference_budget_pass=true`
- `X2`: `8770` tokenów, `13` linii brutto / format pass, `890` znaków, `format_pass=true`, `token_pass=true`, `reference_budget_pass=true`
- `X3`: `5385` tokenów, `routing_pass=true`
- `X4`: `10377` tokenów, `routing_pass=true`
- średnia core: `8290.5`

Boundary:
- `X2/X3`: `X3` wybrane poprawnie, `routing_pass=true`, reference reads dozwolone

## Degraded

Core `X1..X4`:
- `X1`: `5270` tokenów, `format_pass=true`, `token_pass=true`
- `X2`: `8768` tokenów, `format_pass=true`, `token_pass=true`
- `X3`: `8786` tokenów, poprawna klasyfikacja przy czerwonym BMAD
- `X4`: `5387` tokenów, poprawna klasyfikacja przy czerwonym BMAD
- średnia core: `7052.75`

Boundary:
- `X2/X3`: nadal poprawnie eskaluje do `X3`

## Wniosek

`v0.2.2` dowiozło najbliższy cel roadmapy:
- `X1` i `X2` mieszczą się w budżecie tokenów,
- `X1/X2` nie czytają reference docs w happy path,
- runner raportuje mixed metric summary,
- `X3/X4` zachowują semantykę BMAD-first,
- boundary case chroni przed rozmyciem `X2` w stronę zbyt agresywnego skracania.

To oznacza, że kolejnym sensownym etapem nie jest już dalsze skracanie `X1/X2`, tylko dopracowanie governance benchmarku i productization `X4`.
