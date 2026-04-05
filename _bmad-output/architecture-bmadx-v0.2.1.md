# Architecture — BMADX v0.2.1

## Wejście BMAD

Ten zakres jest osadzony w sekwencji:

1. `/bmad-bmm-create-prd`
2. `/bmad-bmm-create-architecture`

PRD i architektura są source-of-truth. `BMADX` jedynie dopina routing, kontrakt gate i benchmark harness.

## Główne decyzje

### Klasyfikacja przed gate

- skill najpierw klasyfikuje `X1..X4` na podstawie `gearbox.md` i `trigger-matrix.md`,
- dopiero potem odpala `sync_bmadx.py check --gear ... --compact`.

### Dwa tryby oceny zależności

- `diagnostic`: pełny live check BMAD, pełne hashe i drift check,
- `fast-path`: dla `X1/X2`; bez live checka, z użyciem cache zdrowego BMAD albo lokalnego warningu.

### Stabilny compact schema

Minimalny schema:

- `skill_version`
- `requested_gear`
- `classification_allowed`
- `execution_allowed`
- `warning`
- `bmad_status`
- `cache_used`
- `remediation`

### Benchmark harness

- runner buduje tymczasowy `CODEX_HOME`,
- kopiuje tylko `bmadx` i `bmad-method-codex`,
- profile `healthy` i `degraded` są sterowane środowiskiem benchmarku,
- `healthy` robi warmup `sync_bmadx.py sync --json`, żeby napełnić cache dla fast path,
- dataset `healthy` zapisuje osobne `txt`, `log` i `summary`.

## Granice

- `render_fubar_bundle.py` nie zmienia kontraktu rendera,
- bundle ma opisywać ownership i verify, ale nie zastępuje PRD ani architektury,
- `_bmad-output/project-context.md` pozostaje jedyną trwałą pamięcią techniczną dla tego zakresu.
