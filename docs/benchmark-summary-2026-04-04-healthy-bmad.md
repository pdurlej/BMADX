# Benchmark Summary — 2026-04-04 (`BMADX healthy`)

## Cel

Sprawdzić, jak `BMADX v0.2.1` zachowuje się po:
- fast path `X1/X2`,
- compact gate z `sync_bmadx.py`,
- warmup cache zdrowego BMAD przed właściwym benchmarkiem.

## Metodyka

- runner: [`benchmark/scripts/run_bmadx_benchmark.py`](../benchmark/scripts/run_bmadx_benchmark.py)
- profil: `healthy`
- model: `gpt-5.4`
- reasoning: `medium`
- MCP startup: `no servers`
- przed scenariuszami wykonany został warmup `sync_bmadx.py sync --json`, żeby napełnić cache zdrowego BMAD dla fast path

Summary JSON:
- [`benchmark/summary-2026-04-04-healthy-bmad.json`](../benchmark/summary-2026-04-04-healthy-bmad.json)

## Wyniki

| Scenariusz | `BMADX degraded` | `BMADX healthy` | Delta |
| --- | --- | --- | --- |
| `X1` | `10492` | `10306` | `-1.8%` |
| `X2` | `10334` | `12472` | `+20.7%` |
| `X3` | `12366` | `6504` | `-47.4%` |
| `X4` | `10627` | `10354` | `-2.6%` |
| średnia | `10954.75` | `9909.0` | `-9.5%` |

## Co zadziałało

- runner odtwarza benchmark w czystym `CODEX_HOME` i zapisuje osobny dataset `healthy`,
- `X1/X2` rzeczywiście używają `check --gear ... --compact`,
- `X3/X4` zachowują klasyfikację i full BMAD-first workflow,
- `X3` mocno tanieje przy zdrowym BMAD, bo znika degradacyjny narzut gate.

## Co nie spełniło celu

Kryterium planu mówiło o spadku tokenów `X1` i `X2` o co najmniej `20%` względem rerunu `v0.2`.

To się nie wydarzyło:
- `X1` spadł tylko o `1.8%`,
- `X2` wzrósł o `20.7%`.

Przyczyna z logów:
- skill używa już compact gate,
- ale model nadal czyta reference docs przed odpowiedzią,
- a `X2` generuje zbyt rozbudowany plan i verify jak na benchmark routingowy.

## Wniosek

`v0.2.1` dowozi infrastrukturę:
- BMAD-first source-of-truth,
- compact gate,
- repo-tracked runner,
- osobny dataset `healthy`.

Nie dowozi jeszcze docelowej zwięzłości `X1/X2`. Następny krok powinien uderzyć już nie w gate, tylko w kontrakt odpowiedzi skilla:
- krótszy output budget dla `X1/X2`,
- mniejsza potrzeba otwierania reference docs przy oczywistej klasyfikacji,
- twardszy limit planowania dla benchmarkowego `X2`.
