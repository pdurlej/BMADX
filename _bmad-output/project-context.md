# Project Context — BMADX v0.2.2

## Zakres

Repo rozwija `BMADX` jako warstwę operacyjno-taktyczną nad `BMAD`.

Zasada nadrzędna:

- `BMAD > BMADX`

## Aktywny program prac

- cel najbliższego releasu: skrócić kontrakt odpowiedzi dla obvious `X1/X2` bez utraty safety dla `X3/X4`,
- cele kolejnych etapów: mixed-metric benchmark guardrails i lepsza adopcja `X4/FUBAR`,
- poza zakresem: port `OMX`, drugi runtime pamięci, bundle jako plan store.

## Aktywne artefakty BMAD

- PRD: `_bmad-output/prd-bmadx-v0.2.2.md`
- Architektura: `_bmad-output/architecture-bmadx-v0.2.2.md`

## Kontrakt routingowy

### X1/X2

- najpierw klasyfikacja,
- potem `python3 .../sync_bmadx.py check --gear X1|X2 --compact`,
- cache zdrowego BMAD daje `cache_used=true` i nie wymaga live checka,
- brak cache daje soft warning, ale nie blokuje execution.
- przy obvious happy path odpowiedź ma używać krótkiego formatu z `SKILL.md`,
- reference docs nie są domyślnym inputem dla obvious `X1/X2`.

### X3/X4

- najpierw klasyfikacja,
- potem pełny gate `python3 .../sync_bmadx.py check --gear X3|X4 --compact`,
- przy blokadzie odpowiedź ma rozdzielać: poprawna klasyfikacja i brak zgody na execution,
- remediation zawsze wskazuje `sync_bmad_method.py check --json` i `sync`.

## Benchmark

- runner: `benchmark/scripts/run_bmadx_benchmark.py`
- profile: `healthy`, `degraded`
- benchmark waliduje teraz nie tylko tokeny, ale też format, routing i budżet czytania refs,
- boundary suite zawiera co najmniej jeden przypadek `X2/X3`,
- baseline history:
  - `benchmark/summary-2026-04-04.json` — stare baseline `BMAD/OMX` + rerun `BMADX degraded`
  - `benchmark/summary-2026-04-04-healthy-bmad.json` — nowy dataset `BMADX healthy`
  - `benchmark/summary-2026-04-05-healthy-bmad.json` — mixed-metric rerun `healthy` po `v0.2.2`
  - `benchmark/summary-2026-04-05-degraded-bmad.json` — mixed-metric rerun `degraded` po `v0.2.2`

## Verify

- `python3 skill/bmadx/scripts/test_sync_bmadx.py`
- `python3 benchmark/scripts/test_run_bmadx_benchmark.py`
- `python3 skill/bmadx/scripts/sync_bmadx.py check --json`
- `python3 skill/bmadx/scripts/render_fubar_bundle.py --project-name BMADX --project-path "$PWD" --output-dir samples/fubar-bundle --include-architect`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile healthy`
- `python3 benchmark/scripts/run_bmadx_benchmark.py --profile degraded`
