# Trigger Matrix

Operacyjna macierz do klasyfikacji zadań bez zgadywania.

Ten plik służy głównie boundary cases. Przy obvious `X1/X2` happy path użyj
heurystyk osadzonych w `SKILL.md` i nie otwieraj reference docs.

| Sygnał | X1 | X2 | X3 | X4 |
| --- | --- | --- | --- | --- |
| 1 lokalny plik | tak | nie | nie | nie |
| kilka plików / lokalny blast radius | nie | tak | nie | nie |
| potrzeba nowego artefaktu BMAD | nie | nie | tak | tak |
| `plan` w prośbie użytkownika | nie | pytania | pytania | pytania |
| niejasny zakres | nie | pytania | pytania | pytania |
| API/schema/auth/perf/concurrency risk | nie | czasem | tak | tak |
| rollout i ownership do zaprojektowania | nie | nie | czasem | tak |
| scaffold bundle ponad BMAD | nie | nie | nie | tak |

## Rekomendowane progi

- `X1`: prosty fix lub prosty upgrade.
- `X2`: lokalna zmiana wieloplikowa.
- `X3`: regularny flow BMAD.
- `X4`: BMAD+ bundle, gdy sam BMAD nie daje jeszcze wystarczająco
  uporządkowanej warstwy operacyjnej.

## Gate po klasyfikacji

- poprawna klasyfikacja ma pozostać poprawna nawet przy czerwonym BMAD,
- `X1/X2` używają `check --gear X1|X2 --compact` i fast path z cache,
- `X1/X2` bez cache dostają warning zamiast blokady,
- `X3/X4` używają `check --gear X3|X4 --compact` z pełnym live gate,
- bez zdrowego BMAD execution dla `X3/X4` ma być zatrzymany,
- cache ostatniego zdrowego BMAD pomaga zmiękczyć komunikację dla `X1/X2`,
  ale nie odblokowuje `X3/X4`.

## Przykładowe klasyfikacje

- „Napraw literówkę w jednym komponencie” -> `X1`
- „Dodaj obsługę nowego pola w kilku miejscach i sprawdź testy” -> `X2`
- „Zaimplementuj story z istniejącego sprintu BMAD” -> `X3`
- „Ułóż nam kompletny sposób pracy dla trudnego projektu i wygeneruj scaffolding”
  -> `X4`
