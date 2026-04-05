# Verify Discipline

BMADX nie zamyka pracy bez dowodu.

Ten plik jest materiałem boundary/debug. Dla obvious `X1/X2` verify ma być
krótkie i wynikać z kontraktu odpowiedzi w `SKILL.md`.

## Zasada

Najpierw implementacja, potem verify, potem dopiero status `done`.

Dependency gate nie znosi tej zasady:
- `X1/X2` mogą wejść w execution przy warningu z BMAD lub po cache healthy snapshot,
- `X3/X4` wymagają zdrowego BMAD zanim verify będzie miało sens procesowy,
- po klasyfikacji preferowaną ścieżką jest `sync_bmadx.py check --gear ... --compact`.

## Minimalny kontrakt

### X1
- 1–2 checki lub najmocniejszy dostępny oracle,
- krótki dowód w odpowiedzi.

### X2
- plan wykonania,
- checki lokalne,
- `/review`, jeśli diff nie jest trywialny.

### X3
- verify zgodne z kryteriami BMAD,
- zgodność z `project-context.md`,
- dowód na poziomie kodu i workflowu.

### X4
- verify matrix z bundle,
- wyraźne ownership,
- dowód, że scaffold nie tworzy drugiego source-of-truth.

## Jeśli checki nie istnieją

- powiedz to wprost,
- użyj najmocniejszego dostępnego oracle,
- nie udawaj pełnej pewności.

## Anti-patterny

- „powinno działać” bez dowodu,
- zakończenie taska bez wyniku checków,
- review bez verify,
- verify bez odniesienia do oczekiwanego zachowania.
