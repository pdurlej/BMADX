# Architecture — BMADX v0.2.2

## Główne decyzje

### Ograniczenie kontraktu, nie gate

- `sync_bmadx.py` pozostaje bez nowych flag,
- zmiana dzieje się w kontrakcie skilla i benchmark harness,
- obvious `X1/X2` mają korzystać wyłącznie z wiedzy osadzonej w `SKILL.md` plus compact gate.

### Mixed metric benchmark

- runner ocenia tokeny, format, routing i czytanie refs,
- `X1/X2` nie mogą domyślnie otwierać `references/*.md`,
- boundary scenario `X2/X3` chroni przed zbyt agresywnym skracaniem `X2`.

### Productized X4

- bundle ma jawne obowiązkowe i opcjonalne artefakty,
- rollout checklist ma mówić kiedy renderować i kiedy nie renderować,
- `project-context.md` pozostaje jedyną trwałą pamięcią techniczną.

## Granice

- `BMAD > BMADX` pozostaje nadrzędne,
- brak wejścia w pełny `OMX`,
- brak redefinicji faz BMAD przez bundle albo benchmark harness.
