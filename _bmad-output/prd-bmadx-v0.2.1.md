# PRD — BMADX v0.2.1

## Cel

Obniżyć koszt operacyjny `BMADX` dla `X1/X2` bez rozmycia bezpieczeństwa `X3/X4`.

## Problem

- `v0.2` naprawiło semantykę dependency gate, ale benchmark nadal pokazał zbyt wysoki koszt odpowiedzi.
- `X1/X2` są poprawne procesowo, ale nadal za ciężkie komunikacyjnie.
- `X3/X4` mają działać z pełnym BMAD-first execution gate i nie mogą zostać „odblokowane” przez skróty pod lekkie taski.

## Workstreamy

### 1. Fast Path `X1/X2`

- klasyfikacja biegu ma dziać się przed dependency gate,
- `check --gear X1|X2` ma używać lekkiej ścieżki bez live checka BMAD, jeśli wystarcza cache zdrowego stanu,
- brak cache nie blokuje `X1/X2`; daje tylko miękkie ostrzeżenie.

### 2. Compact Output

- `sync_bmadx.py` ma wystawiać stabilny `--compact`,
- compact output ma być jedynym kontraktem routingowym używanym przez skill i benchmark,
- verbose JSON zostaje wyłącznie do smoke-checków i debugowania.

### 3. Healthy Benchmark

- benchmark ma mieć repo-tracked runner zamiast ręcznych jednorazowych komend,
- runner ma tworzyć oddzielny dataset dla profilu `healthy`,
- wynik ma być porównywalny z wcześniejszym `BMADX degraded` i bazami `BMAD/OMX`.

## Kryteria sukcesu

- `X1` i `X2` spadają o co najmniej `20%` tokenów względem rerunu `v0.2`,
- `X3/X4` zachowują hard gate i poprawną klasyfikację,
- `X4/FUBAR` nadal wskazuje wejście przez BMAD i nie tworzy drugiego plan store,
- benchmark zapisuje osobne artefakty `healthy` bez nadpisywania starego summary.
