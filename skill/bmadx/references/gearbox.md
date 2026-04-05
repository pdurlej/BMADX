# Gearbox `X1..X4`

BMADX działa jak automatyczna skrzynia biegów. Najpierw klasyfikuje zadanie,
potem dobiera poziom procesu.

Od `v0.2` klasyfikacja biegu i zgoda na execution to osobne decyzje:
- `X1/X2` mogą przejść przy czerwonym BMAD jako soft gate,
- `X3/X4` wymagają zdrowego execution gate,
- czerwony gate nie zmienia poprawnej klasyfikacji zadania.

Od `v0.2.2` obowiązuje kolejność:
- najpierw klasyfikacja,
- potem `sync_bmadx.py check --gear ... --compact`,
- `check --json` bez `--gear` zostaje trybem diagnostycznym, nie domyślną ścieżką routingu.

Ten plik jest dla boundary cases i debugowania. Przy obvious `X1/X2` wystarcza
kontrakt osadzony w `SKILL.md`; nie otwieraj refs, jeśli klasyfikacja jest
jednoznaczna i compact gate jest zielony.

| Bieg | Kiedy użyć | Co robić | Co musi być na wyjściu |
| --- | --- | --- | --- |
| `X1` | mały, lokalny task; niski blast radius; 1–2 checki | krótki plan w głowie, implementacja, verify | zmiana + dowód |
| `X2` | kilka plików, trochę większe ryzyko, ale bez pełnego BMAD | krótki plan, implementacja, verify, opcjonalny review | plan, zmiana, dowód |
| `X3` | potrzeba artefaktów BMAD albo decyzji w ramach workflow map | wejście w właściwy flow BMAD i praca po artefaktach | artefakt BMAD + kod + dowód |
| `X4` | chaos, szeroki zakres, ryzyko, trudny rollout, potrzeba scaffold bundle | BMAD flow + FUBAR bundle + verify discipline | bundle + plan działania + dowód |

## Sygnały wejścia

### X1
- 1 plik albo bardzo lokalny zakres,
- brak zmian kontraktu API/CLI,
- brak auth/security/schema/migration risk,
- nie potrzeba nowego artefaktu BMAD.

### X2
- 2–5 plików lub więcej niż jeden katalog,
- potrzeba krótkiego planu,
- verification wymaga kilku checków,
- nie ma jeszcze potrzeby pełnego flow BMAD.

### X3
- nowe story albo istniejące story BMAD,
- potrzeba PRD, architektury, readiness albo story context,
- zmiana musi być osadzona w artefaktach procesu.

### X4
- użytkownik mówi o planie, chaosie, trudnym projekcie lub eskalacji,
- zakres jest wielowątkowy lub rozlany,
- rollout, ownership, verify matrix i snippets trzeba zbudować świadomie,
- zwykły quick flow przestaje być wystarczający.

## Reguły przejść

- `plan` lub wysoka niejednoznaczność -> pytania przed rekomendacją biegu.
- Nie eskaluj z `X1` do `X3`, jeśli wystarczy `X2`.
- `X4` nie jest karą ani domyślnym trybem. Używaj go tylko wtedy, gdy brak
  scaffold bundle zwiększa ryzyko błędnych decyzji.

## Exit gates

- `X1`: krótki wynik + verify.
- `X2`: plan wykonany + verify + ewentualny review.
- `X3`: zgodność z artefaktami BMAD + verify + zdrowy execution gate.
- `X4`: bundle wygenerowany, ownership jasny, verify matrix gotowa, zdrowy
  execution gate i dalej nadal obowiązuje BMAD jako source-of-truth.

## Compact gate po klasyfikacji

- `X1/X2`: preferuj fast path z cache zdrowego BMAD; brak cache daje warning, ale nie blokuje.
- `X3/X4`: zawsze wymagają live checka BMAD i mogą zwrócić remediation.
