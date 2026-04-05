# BMADX

BMADX to `BMAD-first` overlay dla Codex.

To projekt dla osób, które chcą robić rzeczy w stylu vibe coding, ale bez
wchodzenia od razu w cięższy runtime albo ręczne wybieranie procesu przy każdym
tasku. W praktyce: bardziej leniwy niż czysty `BMAD`, dużo lżejszy niż `OMX`,
ale nadal z procesową dyscypliną tam, gdzie to potrzebne.

Założenie projektu:
- `BMAD` zostaje systemem działania i architekturą procesu,
- `BMADX` dokłada warstwę operacyjno-taktyczną,
- inspiracje z `OMX` są selektywne, bez portowania całego runtime'u `.omx`.

Ten repo powstał jako osobny punkt startowy pod dedykowany wątek Codexa dla `BMADX v0.2`, a bieżący zakres roboczy dopina `v0.2.2`.

## Dlaczego to istnieje

`BMADX` jest celowo „leniwym” rozwiązaniem dla wyzwań vibe coderskich:
- nie chcesz za każdym razem ręcznie rozstrzygać, czy to `X1`, `X2`, `X3` czy `X4`,
- nie chcesz budować pełnego runtime'u orkiestracyjnego,
- chcesz zachować `verify-before-done`,
- chcesz móc wejść w mocniejsze `X4/FUBAR`, ale nie płacić tej ceny na co dzień.

Krótko:
- `BMAD` jest najlepszy, gdy już żyjesz natywnym flow BMAD,
- `OMX` jest mocny jako cięższa orkiestracja,
- `BMADX` jest środkiem: mniej ceremonii, prostszy routing, scaffold bundle tylko wtedy, gdy naprawdę trzeba.

## Zależności i inspiracje

### Twarda zależność od BMAD

`BMADX` nie jest samodzielnym systemem procesu. Zależy od [`bmad-method-codex`](skill/bmadx/references/skill-manifest.json), który dostarcza synchronizację z BMAD i jest wymagany przez dependency gate.

Zasada projektu jest nienegocjowalna:
- `BMAD > BMADX`

To znaczy:
- artefakty procesu i workflow map pozostają po stronie BMAD,
- `BMADX` odpowiada za routing, poziom dyscypliny i `X4/FUBAR` scaffold bundle,
- `BMADX` nie próbuje zastąpić BMAD drugim source-of-truth.

### Podziękowanie dla OMX

Dziękuję `OMX` za inspirację. To właśnie z `OMX` pochodzą wybrane intuicje, które okazały się warte zachowania:
- prosty routing do kilku trybów pracy,
- verify discipline,
- myślenie capability-based o użyciu subagentów,
- nacisk na praktyczną orkiestrację zamiast „ładnej teorii”.

Jednocześnie `BMADX` świadomie nie portuje `.omx`, team runtime ani pełnego świata `OMX`.

## Co tu jest

- [`AGENTS.md`](AGENTS.md) — kontrakt roboczy dla repo.
- [`skill/bmadx`](skill/bmadx) — aktualny snapshot skilla `BMADX v0.2.2`.
- [`benchmark/raw`](benchmark/raw) — surowe wyniki benchmarku `BMAD vs BMADX vs OMX`.
- [`benchmark/scenarios`](benchmark/scenarios) — scenariusze testowe `X1..X4` i boundary cases.
- [`benchmark/summary-2026-04-04.json`](benchmark/summary-2026-04-04.json) — starsze porównanie `BMAD vs BMADX vs OMX`.
- [`benchmark/summary-2026-04-05-healthy-bmad.json`](benchmark/summary-2026-04-05-healthy-bmad.json) — mixed-metric rerun `healthy` po `v0.2.2`.
- [`benchmark/summary-2026-04-05-degraded-bmad.json`](benchmark/summary-2026-04-05-degraded-bmad.json) — mixed-metric rerun `degraded` po `v0.2.2`.
- [`benchmark/scripts/run_bmadx_benchmark.py`](benchmark/scripts/run_bmadx_benchmark.py) — runner dla profili `healthy` i `degraded`.
- [`samples/fubar-bundle`](samples/fubar-bundle) — przykładowy bundle wygenerowany przez `X4/FUBAR`.
- [`_bmad-output/project-context.md`](_bmad-output/project-context.md) — aktywny technical memory dla programu `v0.2.2`.
- [`docs/benchmark-summary-2026-04-04.md`](docs/benchmark-summary-2026-04-04.md) — interpretacja benchmarku `BMAD vs BMADX vs OMX`.
- [`docs/benchmark-summary-2026-04-05.md`](docs/benchmark-summary-2026-04-05.md) — mixed-metric summary dla `v0.2.2`.
- [`docs/bmadx-v0.2-plan.md`](docs/bmadx-v0.2-plan.md) — plan prac dla `v0.2`.

## Aktualny stan

- `v0.2.2` dopina krótszy response contract dla `X1/X2`, mixed-metric benchmark guardrails i boundary scenario `X2/X3`.
- Benchmark routingowy `X1..X4` został wykonany dla `BMAD`, `BMADX` i `OMX`.
- Najmocniejsza przewaga `BMADX` jest w `X4/FUBAR`, gdzie poza routingiem potrafi wygenerować scaffold bundle.
- `v0.2` rozdziela klasyfikację biegu od execution gate, `v0.2.1` przenosi routing na compact gate po klasyfikacji, a `v0.2.2` skraca happy path `X1/X2` bez regresji `X3/X4`.

## Najkrótszy onboarding dla nowego wątku

1. Otwórz [`AGENTS.md`](AGENTS.md).
2. Przeczytaj [`docs/benchmark-summary-2026-04-04.md`](docs/benchmark-summary-2026-04-04.md).
3. Wejdź w [`docs/bmadx-v0.2-plan.md`](docs/bmadx-v0.2-plan.md).
4. Edytuj skill w [`skill/bmadx`](skill/bmadx).

## Gdzie działa lepiej niż OMX, a gdzie niż BMAD

### Lepsze od OMX

- dużo niższy koszt i mniejsza ceremonia operacyjna,
- brak potrzeby pełnego runtime'u `.omx`,
- prostszy próg wejścia dla vibe coders, którzy chcą „po prostu zacząć”, ale nadal mieć routing i verify discipline.

Z benchmarku `2026-04-04`:
- średni koszt `OMX`: `25540.5` tokenów
- średni koszt `BMADX`: `10954.75` tokenów
- po `v0.2.2` core `healthy`: `8290.5` tokenów

### Lepsze od czystego BMAD

- w `X2`, gdy chcesz mniej ręcznego wyboru workflow i bardziej automatyczną skrzynię biegów,
- w `X4`, gdy poza rekomendacją chcesz od razu scaffold bundle: `AGENTS.md`, snippets `.customize.yaml`, trigger matrix, verify matrix, rollout checklist.

W praktyce:
- `BMAD` wygrywa tam, gdzie zadanie jest po prostu natywnym flow BMAD, szczególnie `X3`,
- `BMADX` wygrywa tam, gdzie chcesz nadal być w świecie BMAD, ale z lżejszą warstwą operacyjną i gotowym `X4/FUBAR`.

## Uczciwe porównanie benchmarkowe

Poniżej są dwa różne pytania i dwa różne typy odpowiedzi:
- kto wygrywa surowym kosztem tokenów,
- kto wygrywa praktycznie dla danego typu pracy.

### `BMADX` vs `OMX`

| Obszar | `BMADX` | `OMX` | Wniosek |
| --- | --- | --- | --- |
| średni koszt historyczny `X1..X4` | `10954.75` | `25540.5` | `BMADX` jest tańszy o `14585.75` tokena, czyli około `57.1%` |
| `v0.2.2` core `healthy` | `8290.5` | historyczny baseline `25540.5` | `BMADX` jest tańszy o `17250.0` tokenów, czyli około `67.5%` |
| próg wejścia | lekki overlay nad BMAD | cięższy runtime `.omx` | `BMADX` jest praktyczniejszy dla vibe coders |

Wniosek:
- jeśli celem jest lekki routing, verify discipline i brak pełnego runtime'u orkiestracyjnego, `BMADX` wypada lepiej niż `OMX`,
- `OMX` pozostaje ważną inspiracją, ale nie jest target runtime tego projektu.

### `BMADX` vs `BMAD`

| Obszar | `BMAD` | `BMADX` | Uczciwy wniosek |
| --- | --- | --- | --- |
| średni koszt historyczny `X1..X4` | `7237.5` | `10954.75` | surowo tokenowo wygrywa `BMAD` |
| `X1` tiny task | `4179` | `8630` (`v0.2.2 healthy`) | surowo wygrywa `BMAD`, ale `BMADX` daje automatyczny wybór biegu |
| `X2` regular multi-file | `5686` | `8770` (`v0.2.2 healthy`) | surowo wygrywa `BMAD`, praktycznie `BMADX` wygrywa mniejszą liczbą decyzji ręcznych |
| `X3` story/process-first | `11044` | `5385` (`v0.2.2 healthy`) | w tej próbce taniej wyszedł `BMADX`, ale semantycznie to nadal obszar natywny dla `BMAD` |
| `X4` chaos + scaffold | `8041` | `10377` (`v0.2.2 healthy`) | tokenowo wygrywa `BMAD`, funkcjonalnie `BMADX` dokłada bundle i warstwę operacyjną |

Najważniejszy wniosek:
- `BMADX` nie jest projektem pod tezę „BMADX jest lepszy od BMAD we wszystkim”,
- `BMADX` jest projektem pod tezę „BMAD jest source-of-truth, a BMADX jest leniwą warstwą operacyjną dla Codexa”.

## Snapshot benchmarku

- `BMAD`: średnio `7237.5` tokenów
- `BMADX`: średnio `10954.75` tokenów
- `BMADX healthy`: średnio `9909.0` tokenów
- `BMADX healthy v0.2.2`: średnio `8290.5` tokenów
- `BMADX degraded v0.2.2`: średnio `7052.75` tokenów
- `OMX`: średnio `25540.5` tokenów

### Szybki werdykt

| Obszar | Najmocniejszy wybór | Dlaczego |
| --- | --- | --- |
| `X1` tiny task | `BMAD` lub `BMADX v0.2.2` | oba są lekkie; `BMADX` daje gotowy routing bez ręcznego zastanawiania się |
| `X2` lokalna zmiana wieloplikowa | `BMADX` | mniej ręcznego wyboru procesu niż w czystym BMAD, dużo lżej niż OMX |
| `X3` story/process-first | `BMAD` | to natywne środowisko BMAD |
| `X4` chaos + scaffold | `BMADX` | daje bundle ponad BMAD, bez wejścia w pełny świat OMX |

Wniosek: `BMADX` nie zastępuje ani `BMAD`, ani `OMX`. To celowo leniwe, praktyczne rozwiązanie dla vibe coders, którzy chcą mniej tarcia niż w `OMX`, ale więcej dyscypliny niż w czystym one-shot workflow.
