# BMADX v0.2 Plan

## Cel

Podnieść użyteczność `BMADX` bez utraty jego głównej przewagi:
- prosty routing `X1..X4`,
- `BMAD-first`,
- mocne `X4/FUBAR`,
- niski narzut dla prostych zadań.

## Zakres v0.2

### 1. Soft gate dla `X1/X2`

Obecny problem:
- `v0.1` odpala dependency gate zawsze,
- nawet dla prostych zadań użytkownik dostaje zbędny komunikat o `needs_attention`.

Cel:
- `X1` i `X2` mają klasyfikować się i działać bez blokowania przez czerwony stan BMAD,
- dependency gate ma być dla nich co najwyżej ostrzeżeniem, nie blokadą.

### 2. Rozdzielenie classify vs execute

Obecny problem:
- `v0.1` miesza wybór biegu z prawem wejścia w cięższy flow.

Cel:
- klasyfikacja ma odpowiadać na pytanie: `jaki to bieg?`
- execution gate ma odpowiadać osobno na pytanie: `czy wolno teraz wejść w X3/X4?`

Efekt:
- nawet przy niezdrowym BMAD użytkownik dostaje poprawną klasyfikację `X3` lub `X4`,
- ale też jasny komunikat, że execution jest zablokowany.

### 3. Cache ostatniego zdrowego stanu BMAD

Obecny problem:
- dependency gate zbyt łatwo przechodzi w `needs_attention`,
- benchmark pokazał, że to zanieczyszcza proste przypadki.

Cel:
- zapisywać ostatni zdrowy stan BMAD z timestampem,
- używać go jako miękkiego sygnału dla `X1/X2`,
- dla `X3/X4` nadal wymagać świeższego i bardziej rygorystycznego checku.

## Poza zakresem v0.2

- pełny port `OMX`,
- `.omx/` jako drugi system pamięci,
- tmux/team runtime,
- większa liczba helper skills,
- rozbijanie `BMADX` na skomplikowaną siatkę zależności.

## Kryteria akceptacji

- `X1` i `X2` nie spamują użytkownika gate'em, jeśli routing jest oczywisty,
- `X3` i `X4` nadal respektują zdrowie BMAD,
- `X4/FUBAR` nadal generuje kompletny scaffold bundle,
- re-benchmark pokazuje poprawę doświadczenia dla `X1/X2`,
- koszt tokenowy nie rośnie wyraźnie względem `v0.1`.

## Minimalny plan pracy

1. Zmienić logikę w [`sync_bmadx.py`](../skill/bmadx/scripts/sync_bmadx.py), tak żeby wynik rozróżniał:
   - `classification_allowed`
   - `execution_allowed`
   - `warning`
2. Zmienić opis dependency gate w [`SKILL.md`](../skill/bmadx/SKILL.md) i reference docs.
3. Dodać testy dla:
   - czerwonego BMAD + `X1`
   - czerwonego BMAD + `X2`
   - czerwonego BMAD + `X3`
   - czerwonego BMAD + `X4`
4. Uruchomić smoke-check.
5. Powtórzyć benchmark `X1..X4`.

## Co sprawdzić po wdrożeniu

- czy `X1/X2` stały się lżejsze komunikacyjnie,
- czy `X3/X4` nadal są bezpieczne,
- czy output nie zrobił się bardziej rozwlekły,
- czy benchmark nadal pokazuje przewagę `BMADX` w `X4`.
