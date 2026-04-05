---
name: bmadx
description: Orkiestruje BMAD w Codex przez automatyczną skrzynię biegów X1-X4, pilnuje zależności od bmad-method-codex, rekomenduje właściwy poziom planowania i verification oraz generuje FUBAR scaffold bundle dla trudnych projektów.
---

# BMADX

BMADX to BMAD-first overlay dla Codex. Nie zastępuje BMAD i nie tworzy drugiego
source-of-truth dla procesu. Dokłada operacyjno-taktyczną warstwę inspirowaną
OMX: routing, verify-before-done, capability-based politykę użycia subagentów i
`X4/FUBAR` scaffold bundle dla trudnych projektów.

## Używaj tego skilla, gdy

- użytkownik chce dobrać właściwy tryb pracy dla zadania zamiast od razu wejść
  w przypadkowy one-shot,
- użytkownik chce uruchomić BMAD z dodatkową dyscypliną routingu, review i
  verification,
- trzeba zdecydować, czy zadanie jest `X1`, `X2`, `X3` czy `X4`,
- trzeba wygenerować pakiet wdrożeniowy ponad BMAD: draft `AGENTS.md`,
  snippets `.customize.yaml`, trigger matrix, verify matrix, rollout checklist,
  politykę użycia subagentów,
- użytkownik mówi o chaosie, rozlanym zakresie, trudnym projekcie, planie,
  eskalacji lub potrzebie scaffold bundle.

## Nie używaj tego skilla, gdy

- użytkownik chce tylko uruchomić znany workflow BMAD i nie potrzebuje overlayu,
- zadanie jest czystym, lokalnym wykonaniem w ramach już ustalonego story BMAD,
- użytkownik pyta wyłącznie o aktualność BMAD; wtedy użyj
  `$bmad-method-codex`.

## Dependency Gate

BMADX ma zależność od `bmad-method-codex`, ale od `v0.2.2` używa kontraktu
`classify first, gate second`.

1. Najpierw sklasyfikuj zadanie na podstawie `gearbox.md` i `trigger-matrix.md`.
2. Dopiero po klasyfikacji uruchom gear-aware gate:

```bash
python3 /Users/pd/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X1 --compact
python3 /Users/pd/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X2 --compact
python3 /Users/pd/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X3 --compact
python3 /Users/pd/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X4 --compact
```

3. Czytaj compact raport w tej kolejności:
- jeśli `classification_allowed = false`, zatrzymaj się i wypisz lokalny problem `BMADX`,
- jeśli `classification_allowed = true`, utrzymaj poprawną klasyfikację biegu,
- dla `X1/X2` traktuj `warning` jako sygnał miękki; brak cache nie blokuje execution,
- dla `X3/X4` traktuj `execution_allowed = false` jako twardy stop execution,
- jeśli `cache_used = true`, `X1/X2` jadą po ostatnim zdrowym snapshotcie BMAD bez live checka.

4. Pełny verbose check zostaw na smoke-check i debug:

```bash
python3 /Users/pd/.codex/skills/bmadx/scripts/sync_bmadx.py check --json
```

5. Zasada gate:
- `X1/X2`: fast path z compact gate; czerwony BMAD bez cache daje warning, nie blokadę,
- `X3/X4`: pełny live gate; czerwony BMAD blokuje execution, ale nie klasyfikację,
- cache zdrowego stanu służy tylko `X1/X2`,
- compact remediation dla zablokowanego `X3/X4` ma wskazywać dokładnie:

```bash
python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py check --json
python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py sync
```

## Obvious `X1/X2` Fast Path

Przy oczywistym `X1` albo `X2` nie otwieraj reference docs. `SKILL.md` ma wtedy
wystarczyć do decyzji.

Traktuj zadanie jako obvious happy path, jeśli:
- `X1`: jedna lokalna zmiana, literówka/copy/fix małego tekstu, brak sygnałów o zmianie kontraktu albo ryzyku procesu,
- `X2`: 2–5 plików lub lokalny blast radius, potrzeba krótkiego planu i kilku checków, ale bez artefaktu BMAD,
- user prompt nie zawiera niejednoznaczności co do zakresu ani potrzeby eskalacji procesu,
- compact gate dla wybranego biegu jest zielony albo daje tylko soft warning.

Otwórz `gearbox.md`, `trigger-matrix.md` albo `verify-discipline.md` tylko wtedy, gdy:
- sygnały między `X1/X2/X3` konfliktują,
- prompt zawiera `plan`, ale nie wiadomo, czy chodzi o zwykły `X2` czy pełny BMAD,
- pojawia się story BMAD, nowy artefakt procesu, rollout/ownership, API/schema/auth/perf risk,
- compact gate dla wybranego biegu jest czerwony i trzeba uzasadnić eskalację.

Nie narracyjnie nie raportuj, że „używasz skilla”, „czytasz refs” albo „sprawdzasz gate”, jeśli nie jest to konieczne dla decyzji.

## Automatyczna Skrzynia Biegów

Najpierw sklasyfikuj zadanie, dopiero potem proponuj wykonanie.

- `X1` — One-shot
- `X2` — Regular
- `X3` — Complex (BMAD)
- `X4` — FUBAR (BMAD+)

Szczegóły i progi:
- [gearbox.md](references/gearbox.md)
- [trigger-matrix.md](references/trigger-matrix.md)

Reguła wyboru:
- jeśli użytkownik sygnalizuje `plan` albo niejednoznaczność jest wysoka,
  przejdź w tryb pytający przed rekomendacją biegu,
- jeśli intencja jest jasna, zarekomenduj bieg i uzasadnij go jednym akapitem,
- po klasyfikacji zawsze dopytaj tylko właściwy compact gate dla wybranego biegu,
- dla obvious `X1/X2` nie otwieraj refs i odpowiedz od razu w krótkim formacie,
- jeśli zadanie dotyczy istniejących artefaktów BMAD, `X3/X4` muszą opierać się
  na BMAD jako source-of-truth,
- jeśli klasyfikacja wskazuje `X3/X4`, ale execution gate jest czerwony,
  podaj poprawną klasyfikację i osobno powiedz, że execution jest zablokowany.

## Response Contract

### `X1` obvious happy path

Format:
- `Wybór: ...`
- `Uzasadnienie: ...`
- `Następny krok: ...`

Zasady:
- maksimum `5` linii,
- maksimum `650` znaków,
- jedno zdanie uzasadnienia i jedno zdanie następnego kroku,
- nie wspominaj o gate, jeśli jest zielony,
- wspomnij gate tylko przy warningu albo blokadzie.

### `X2` obvious happy path

Format:
- `Wybór: ...`
- `Uzasadnienie: ...`
- `Plan:` z maksymalnie `3` krokami,
- `Verify:` z maksymalnie `3` krokami.

Zasady:
- maksimum `12` linii,
- maksimum `1000` znaków,
- plan ma być konkretny, ale krótki,
- verify ma obejmować tylko najmocniejsze checki,
- bez końcówki typu „jeśli chcesz, mogę...” jeśli user nie prosi o kolejny krok.

### `X3/X4`

Nie skracaj ich według tych samych limitów. Dla `X3/X4` ważniejsze są:
- poprawna klasyfikacja,
- jawny stan execution gate,
- zgodność z BMAD jako source-of-truth.

## Biegi

### X1 — One-shot

Użyj dla małych, lokalnych zmian o niskim blast radius.

- brak nowych artefaktów BMAD,
- 1–2 checki końcowe,
- szybkie wykonanie + dowód verification.

### X2 — Regular

Użyj dla małych i średnich zadań, które wymagają krótkiego planu, ale nie
potrzebują pełnego flow BMAD.

- zwięzły plan,
- wykonanie,
- verify-before-done,
- opcjonalny `/review` przy nietrywialnym diffie.

### X3 — Complex (BMAD)

Użyj, gdy trzeba wejść w pełny flow BMAD.

- BMAD definiuje fazy, workflow map i artefakty,
- `project-context.md` i artefakty BMAD są source-of-truth,
- BMADX jedynie pilnuje routingu, review i verification discipline.

### X4 — FUBAR (BMAD+)

Użyj, gdy projekt jest rozlany, wielowątkowy, ryzykowny albo wymaga scaffold
bundle ponad BMAD.

`X4` nie jest domyślnym trybem. To as w rękawie.

W `X4`:
- wybierasz właściwy flow BMAD,
- zaczynasz od `/bmad-bmm-create-prd`, potem `/bmad-bmm-create-architecture`,
- traktujesz `_bmad-output/project-context.md` jako trwały technical memory,
- generujesz scaffold bundle z szablonów,
- porządkujesz ownership, verify matrix i rollout,
- zachowujesz prosty język i jedną hierarchię decyzji: BMAD > BMADX.

Specyfikacja bundle:
- [fubar-bundle-spec.md](references/fubar-bundle-spec.md)

Render bundle:

```bash
python3 /Users/pd/.codex/skills/bmadx/scripts/render_fubar_bundle.py \
  --project-name "Nazwa projektu" \
  --project-path "$PWD" \
  --output-dir /tmp/bmadx-fubar
```

## Verify Before Done

BMADX wymusza verify-before-done niezależnie od biegu.

- `X1`: minimum 1–2 checki lub jednoznaczny oracle,
- `X2`: plan + checki + ewentualny `/review`,
- `X3/X4`: checki muszą być zgodne z kryteriami BMAD i bieżącym
  `project-context.md`.

Szczegóły:
- [verify-discipline.md](references/verify-discipline.md)

## Subagenci

BMADX promuje capability-based użycie subagentów.

- szybsze/mniejsze modele: bounded discovery, read-heavy repo mapping, diff
  review support, verification support,
- główny model: decyzje, synteza, integracja i odpowiedzialność końcowa,
- bez hardcode pod jeden model lub jeden vendor.

Szczegóły:
- [subagent-policy.md](references/subagent-policy.md)

## Granice BMADX vs BMAD

BMAD pozostaje ownerem:
- faz,
- workflow map,
- artefaktów,
- języka procesu.

BMADX pozostaje ownerem:
- wyboru biegu,
- operacyjnego poziomu dyscypliny,
- verify gate,
- scaffold bundle dla `X4`.

Granice i ownership:
- [bmadx-vs-bmad.md](references/bmadx-vs-bmad.md)

## Zasoby

- `scripts/sync_bmadx.py` — health check, drift check, cache zdrowego BMAD i soft/hard dependency gate
- `scripts/test_sync_bmadx.py` — smoke/unit testy dla sync
- `scripts/render_fubar_bundle.py` — generator FUBAR scaffold bundle
- `assets/templates/` — szablony bundle i snippets
- `references/` — gearbox, trigger matrix, boundaries, verify, subagents
