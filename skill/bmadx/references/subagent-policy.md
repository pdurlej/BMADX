# Capability-Based Subagent Policy

BMADX promuje użycie subagentów według zdolności, nie według jednej sztywnej
nazwy modelu.

## Zasada

- szybsze i mniejsze subagenty: bounded, read-heavy, równoległe wsparcie,
- główny model: decyzje, integracja, końcowa odpowiedzialność.

## Dobre zastosowania

- repo mapping i discovery,
- diff review support,
- verification support,
- porównanie dwóch wariantów implementacji,
- odczyt długich artefaktów bez zanieczyszczania głównego kontekstu.

## Złe zastosowania

- delegowanie całego problemu bez własnej syntezy,
- odpalanie subagentów do prostych `X1`,
- równoleglenie rzeczy, które i tak są zależne sekwencyjnie,
- używanie subagentów jako maskowania braku decyzji.

## Reguła dla BMADX

- `X1`: domyślnie bez subagentów.
- `X2`: opcjonalnie jeden bounded helper.
- `X3`: subagenty tylko wtedy, gdy przyspieszają discovery, review lub verify.
- `X4`: można użyć kilku bounded lanes, ale ownership i synteza zostają w
  głównym modelu.

## Future-proofing

Nie hardcode’uj:
- jednego modelu,
- jednego vendora,
- jednego typu subagenta.

Hardcode’uj tylko zadanie pomocnicze:
- co ma zbadać,
- jaki ma mieć write scope,
- jaki wynik ma zwrócić.
