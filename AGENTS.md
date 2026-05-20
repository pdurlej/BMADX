# BMADX Project AGENTS

## 0. Fresh session? Read agent-souls onboarding first

If you are a fresh cousin session (claude / codex / glm / iskra / hermes / dziadek / pan-herbatka / pyfallow) entering this repo, read [`pdurlej/agent-souls/skills/cousin-onboarding/SKILL.md`](https://git.pdurlej.com/pdurlej/agent-souls/src/branch/main/skills/cousin-onboarding/SKILL.md) **first**, then return to the repo-specific sections below.

The skill covers: identity verification, Infisical machine identity bootstrap (NOT operator paste), cardinal `agent-souls` reads, per-repo entry table, hard rules (no secrets in chat, per-cousin commits, ADR-0017 + ADR-0018).

BMADX-specific: `BMAD > BMADX` discipline applies here. BMAD = source of truth for phases/workflow. BMADX = operational/tactical layer for Codex routing.

Discipline source: [`pdurlej/agent-souls/practices/repo-onboarding-pointer.md`](https://git.pdurlej.com/pdurlej/agent-souls/src/branch/main/practices/repo-onboarding-pointer.md).

---

To repo jest dedykowane rozwojowi `BMADX`.

## Tożsamość projektu

- `BMAD` jest systemem działania i architekturą procesu.
- `BMADX` jest warstwą operacyjno-taktyczną dla Codex.
- `OMX` jest źródłem wybranych insightów, nie docelowym runtime'em tego projektu.
- Zasada nadrzędna: `BMAD > BMADX`.

## Cel bieżący

Pierwszy cel repo to przygotowanie `BMADX v0.2`.

Priorytety `v0.2`:
- zmiękczyć dependency gate dla `X1/X2`,
- rozdzielić klasyfikację biegu od zgody na execution dla `X3/X4`,
- cachować ostatni zdrowy stan BMAD zamiast stale zwracać `needs_attention`,
- utrzymać przewagę `X4/FUBAR` bez zwiększania ceremonii dla prostych tasków.

## Mapa repo

- `skill/bmadx/` — aktualny skill i skrypty.
- `benchmark/raw/` — surowe logi i odpowiedzi z benchmarku.
- `benchmark/scenarios/` — wejściowe scenariusze `X1..X4`.
- `benchmark/summary-2026-04-04.json` — zebrane metryki.
- `samples/fubar-bundle/` — przykładowy output `X4`.
- `docs/` — podsumowania i plan `v0.2`.

## Source of truth

- aktualny kod skilla: `skill/bmadx/`
- aktualna interpretacja benchmarku: `docs/benchmark-summary-2026-04-04.md`
- aktualny plan zmian: `docs/bmadx-v0.2-plan.md`

Nie twórz równoległych planów w innych plikach, jeśli nie ma konkretnego powodu.

## Zasady pracy

- najpierw przeczytaj benchmark i plan `v0.2`,
- zmieniaj jak najmniej, ale tak, żeby poprawić realne zachowanie,
- nie komplikuj architektury skilla tylko po to, żeby była „ładniejsza”,
- benchmarkuj znowu po istotnych zmianach w routingu i dependency gate,
- `X4` ma pozostać asem w rękawie, nie trybem domyślnym,
- nie rozbudowuj projektu w stronę pełnego `OMX`.

## Verify

Po zmianach w skillu:
- uruchom testy z [`skill/bmadx/scripts/test_sync_bmadx.py`](/Users/pd/Developer/BMADX/skill/bmadx/scripts/test_sync_bmadx.py),
- uruchom smoke-check z [`skill/bmadx/scripts/sync_bmadx.py`](/Users/pd/Developer/BMADX/skill/bmadx/scripts/sync_bmadx.py),
- jeśli zmieniasz `X4`, wygeneruj ponownie bundle przez [`skill/bmadx/scripts/render_fubar_bundle.py`](/Users/pd/Developer/BMADX/skill/bmadx/scripts/render_fubar_bundle.py),
- jeśli zmieniasz routing, porównaj zachowanie przynajmniej na scenariuszach `X1..X4`.
