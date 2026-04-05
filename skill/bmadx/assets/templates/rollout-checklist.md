# BMADX Rollout Checklist for {{project_name}}

- [ ] Bundle został uruchomiony tylko po wejściu BMAD przez PRD i architekturę.
- [ ] Bundle nie jest używany dla `X1/X2` ani jako skrót dla zwykłego `X3`.
- [ ] W repo jest `AGENTS.md` zgodny z zasadą `BMAD > BMADX`.
- [ ] `_bmad-output/project-context.md` istnieje lub ma jawny plan utworzenia.
- [ ] Obowiązkowe artefakty bundle są gotowe do adopcji: `AGENTS.md`, `core-bmad-master.customize.yaml`, `bmm-dev.customize.yaml`, `bmadx-trigger-matrix.md`, `bmadx-verify-matrix.md`, `bmadx-rollout-checklist.md`, `bmadx-subagent-policy.md`.
- [ ] Opcjonalny `bmm-architect.customize.yaml` jest dołączony tylko wtedy, gdy projekt realnie potrzebuje warstwy architect.
- [ ] Zespół zna biegi `X1..X4`.
- [ ] Verify-before-done jest egzekwowane.
- [ ] `X4/FUBAR` pozostaje trybem wyjątkowym.
- [ ] Opcjonalna adopcja `.codex/agents` została oceniona i nie jest wymagana na start.

Generated: {{generated_at}}
