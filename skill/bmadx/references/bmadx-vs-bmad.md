# BMADX vs BMAD

## Zasada nadrzędna

`BMAD > BMADX`

BMAD daje system działania, workflow map, artefakty i architekturę procesu.
BMADX daje taktyczny i operacyjny overlay dla Codex.

## BMAD pozostaje ownerem

- faz procesu,
- workflow map,
- agentów i workflowów BMAD,
- artefaktów takich jak PRD, architektura, stories,
- `project-context.md` jako trwałego kontekstu technicznego.

## BMADX pozostaje ownerem

- wyboru biegu `X1..X4`,
- krótkiej klasyfikacji zadania przed implementacją,
- verify-before-done,
- capability-based polityki użycia subagentów,
- scaffold bundle dla `X4/FUBAR`.

## Czego BMADX nie robi

- nie podmienia workflow map BMAD,
- nie tworzy drugiego trwałego plan store,
- nie kopiuje `.omx/`,
- nie wymaga `omx`, tmux, HUD ani team runtime,
- nie redefiniuje nazewnictwa faz BMAD.

## Decyzja operacyjna

Gdy jest konflikt między wygodą BMADX a artefaktem BMAD:
- wygrywa BMAD.

Gdy BMAD nie daje jeszcze wystarczającej warstwy operacyjnej:
- BMADX może wygenerować bundle i checklisty,
- ale nie przejmuje ownershipu nad procesem.
