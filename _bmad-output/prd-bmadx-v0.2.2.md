# PRD — BMADX v0.2.2

## Cel

Obniżyć koszt komunikacyjny obvious `X1/X2` bez zmiany semantyki compact gate i bez utraty bezpieczeństwa `X3/X4`.

## Problem

- `v0.2.1` naprawiło infrastrukturę, ale benchmark pokazał, że model nadal czyta reference docs i rozwleka odpowiedzi `X1/X2`.
- Sam gate nie jest już bottleneckiem.
- Brakuje stałych guardrails benchmarku oraz bardziej wdrażalnej dokumentacji `X4`.

## Zakres releasu

- nowy response contract dla obvious `X1/X2`,
- benchmark runner z mixed metric summary i boundary case `X2/X3`,
- doprecyzowanie adoption rules dla `X4/FUBAR`.

## Kryteria sukcesu

- `X1`: do `5` linii i `650` znaków,
- `X2`: do `12` linii i `1000` znaków,
- benchmark raportuje `format_pass`, `token_pass`, `reference_budget_pass`,
- `X4` pozostaje trybem wyjątkowym i nie zastępuje BMAD.
