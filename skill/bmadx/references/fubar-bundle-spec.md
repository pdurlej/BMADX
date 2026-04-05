# FUBAR Bundle Spec

`X4/FUBAR` generuje scaffold bundle dla trudnego projektu lub trudnej zmiany.

## Cel

Nie zastąpić BMAD, tylko szybko dołożyć brakującą warstwę operacyjno-taktyczną
pod Codex.

## Bundle zawiera

- obowiązkowy `AGENTS.md` draft dla repo,
- obowiązkowy snippet `core-bmad-master.customize.yaml`,
- obowiązkowy snippet `bmm-dev.customize.yaml`,
- opcjonalny snippet `bmm-architect.customize.yaml`,
- obowiązkowy `bmadx-trigger-matrix.md`,
- obowiązkowy `bmadx-verify-matrix.md`,
- obowiązkowy `bmadx-rollout-checklist.md`,
- obowiązkowy `bmadx-subagent-policy.md`.

## Kiedy renderować

Renderuj bundle tylko wtedy, gdy:
- klasyfikacja wskazuje `X4`,
- najpierw zamknąłeś wejście BMAD przez `/bmad-bmm-create-prd` i `/bmad-bmm-create-architecture`,
- trzeba uporządkować ownership, rollout, verify matrix albo adopcję snippetów ponad samym BMAD.

## Kiedy nie renderować

Nie renderuj bundle, gdy:
- zadanie jest obvious `X1` albo `X2`,
- wystarczy zwykły flow `X3` w oparciu o istniejące artefakty BMAD,
- bundle miałby stać się drugim plan store albo substytutem `project-context.md`.

## Zasady bundle

- prosty język,
- zero OMX vocabulary drift,
- jawne `BMAD > BMADX`,
- `project-context.md` wskazany jako trwały technical memory,
- bundle ma być ręcznie wdrażalny bez dodatkowego runtime.

## Parametry rendera

- `project_name`
- `project_path`
- `generated_at`
- `bmadx_skill_path`
- `bmad_skill_path`
- `include_architect`

## Exit criteria

- wszystkie pliki bundle zostały wygenerowane,
- obowiązkowe artefakty są gotowe do adopcji bez dodatkowych decyzji,
- opcjonalny snippet architect jest dołączany tylko wtedy, gdy projekt realnie potrzebuje tej roli,
- każdy plik jest czytelny bez znajomości OMX,
- nie ma drugiego trwałego plan store,
- nie ma redefinicji faz BMAD.
