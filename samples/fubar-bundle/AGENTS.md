# AGENTS.md for BMADX

To repo używa `BMAD > BMADX`.

- BMAD pozostaje systemem działania i architekturą procesu.
- BMADX pozostaje warstwą operacyjno-taktyczną dla Codex.
- Gdy routing jest niejasny, użyj `bmad-help` zamiast wymyślać nowy workflow.

## Routing

- `X1` — One-shot: mały, lokalny task.
- `X2` — Regular: krótki plan i standardowy verify.
- `X3` — Complex (BMAD): wejście w właściwy flow BMAD.
- `X4` — FUBAR (BMAD+): scaffold bundle, rollout, verify matrix.

## Trwały kontekst

- Proces i artefakty: BMAD.
- Technical memory: `_bmad-output/project-context.md`.
- Lokalna pamięć sesji nie jest source-of-truth.

## Verify before done

- Nie zamykaj pracy bez dowodu.
- Dla nietrywialnych zmian uruchamiaj review.
- Przy konfliktach między wygodą a artefaktem procesu wygrywa BMAD.

## Escalation

- Gdy `X1` nie wystarcza, przejdź do `X2`.
- Gdy potrzebne są artefakty procesu, przejdź do `X3`.
- Gdy potrzebny jest scaffold bundle i porządkowanie ownershipu, użyj `X4`.
- Nie renderuj `X4/FUBAR`, jeśli wystarcza `X2` albo zwykły `X3`.

Generated: 2026-04-04T23:03:29.385049+00:00
Project path: /Users/pd/Developer/BMADX
