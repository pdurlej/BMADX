# Benchmark Summary — 2026-04-04

## Cel

Porównać `BMAD`, `BMADX` i `OMX` na tych samych czterech scenariuszach routingowo-planistycznych:
- `X1` — mały one-shot,
- `X2` — średni task wieloplikowy,
- `X3` — istniejące story BMAD,
- `X4` — rozlany projekt z potrzebą scaffold bundle.

## Metodyka

- Wszystkie odpowiedzi były generowane przez `codex exec`.
- `BMAD` i `OMX` pozostają wynikami z wcześniejszego przebiegu bazowego.
- `BMADX` został uruchomiony ponownie po wdrożeniu zmian `v0.2` w dependency gate.
- `BMADX healthy` został uruchomiony osobnym runnerem po wdrożeniu `v0.2.1`.
- `BMAD` i `BMADX` działały na `gpt-5.4` z `reasoning effort = medium`.
- `OMX` działał na `gpt-5.4` z `reasoning effort = high` i aktywnymi MCP:
  - `omx_state`
  - `omx_memory`
  - `omx_trace`
  - `omx_team_run`
  - `omx_code_intel`
- To nie jest benchmark czysto „promptowy”. To benchmark realnych domyślnych setupów.

Osobny dataset `healthy`:
- [`benchmark/summary-2026-04-04-healthy-bmad.json`](../benchmark/summary-2026-04-04-healthy-bmad.json)
- [`docs/benchmark-summary-2026-04-04-healthy-bmad.md`](benchmark-summary-2026-04-04-healthy-bmad.md)

## Wyniki skrócone

| Scenariusz | BMAD | BMADX | OMX | Werdykt |
| --- | --- | --- | --- | --- |
| `X1` | `quick-dev` | `X1` + soft warning | `solo execute` | `BMAD` lub `OMX` |
| `X2` | `quick-spec` | `X2` + soft warning | `ralplan` | `BMADX` |
| `X3` | `dev-story` | `X3`, klasyfikacja poprawna; execution zablokowany | `ralplan -> ralph` | `BMAD` |
| `X4` | `create-prd` | `X4/FUBAR`, klasyfikacja poprawna; execution zablokowany | `ralplan` | `BMADX` |

## Koszt

Średni koszt tokenowy:
- `BMAD`: `7237.5`
- `BMADX`: `10954.75`
- `OMX`: `25540.5`

Wniosek kosztowy:
- `BMADX` po rerunie `v0.2` jest wyraźnie droższy od `BMAD`, ale nadal dużo tańszy od `OMX`.
- `OMX` płaci za cięższy setup i większą orkiestrację.

## Co wygrało gdzie

### BMAD

Najmocniejszy tam, gdzie zadanie jest po prostu natywnym flow BMAD.

Najlepszy przykład:
- `X3`: istniejące story BMAD do wdrożenia.

### BMADX

Najmocniejszy tam, gdzie chcesz nadal żyć w `BMAD`, ale potrzebujesz:
- lepszego routingu,
- prostszej skrzyni biegów,
- verify discipline,
- gotowego scaffoldu ponad BMAD.

Najlepsze przykłady:
- `X2`
- `X4`

### OMX

Najmocniejszy jako cięższa, ogólna warstwa orkiestracji Codex.

Przewagi:
- silne reguły wykonawcze,
- konsekwentne routingowanie do `solo execute`, `ralplan`, `ralph`,
- gotowość do szerszej orkiestracji i subagentów.

Koszt:
- wyraźnie większy narzut operacyjny,
- własny świat `.omx` i runtime'u.

## Najważniejsza obserwacja po rerunie `BMADX v0.2`

Rerun potwierdził, że główna zmiana w `v0.2` zadziałała semantycznie:
- `X1/X2` nie są już blokowane przez czerwony stan BMAD; odpowiedź komunikuje soft warning zamiast twardego `stop`,
- `X3/X4` zachowują poprawną klasyfikację nawet wtedy, gdy execution gate jest czerwony,
- cache ostatniego zdrowego stanu BMAD działa jako miękki sygnał dla `X1/X2`,
- `X4` nadal pozostaje najmocniejszym wyróżnikiem `BMADX`.

Jednocześnie rerun nie poprawił kosztu:
- odpowiedzi `BMADX` są teraz bardziej poprawne procesowo,
- ale średni koszt tokenowy wzrósł względem wcześniejszego benchmarku `v0.1`,
- więc kolejny etap optymalizacji powinien dotyczyć zwięzłości komunikacji, a nie samego modelu gate.

## Co wniósł osobny dataset `healthy`

Osobny rerun `BMADX healthy` potwierdził, że:
- infrastruktura `v0.2.1` działa: compact gate, warmup cache i osobny runner są poprawnie spięte,
- średnia `BMADX` spadła do `9909.0` tokenów,
- największy zysk pojawia się w `X3`,
- cel `-20%` dla `X1/X2` nadal nie został dowieziony.

To oznacza, że kolejna optymalizacja musi uderzyć w kontrakt odpowiedzi skilla, nie tylko w dependency gate.

## Artefakt przewagi `BMADX`

`BMADX` ma realną przewagę funkcjonalną w `X4`, bo poza rekomendacją potrafi wygenerować scaffold bundle.

Dowód:
- [`samples/fubar-bundle/AGENTS.md`](../samples/fubar-bundle/AGENTS.md)
- [`samples/fubar-bundle/bmadx-trigger-matrix.md`](../samples/fubar-bundle/bmadx-trigger-matrix.md)
- [`samples/fubar-bundle/bmadx-verify-matrix.md`](../samples/fubar-bundle/bmadx-verify-matrix.md)

`BMAD` i `OMX` w tym benchmarku kończyły `X4` na rekomendacji workflowu i kolejnego kroku. `BMADX` dowiózł pakiet wyjściowy.
