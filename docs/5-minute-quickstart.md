# 5-Minute Quickstart

This is the shortest realistic path from zero to a first useful BMADX task.

## Prerequisite

BMAD must already be installed in your Codex skills.

BMADX depends on `bmad-method-codex`. It does not replace it.

BMADX `v0.2.4` is tuned for Codex on GPT-5.5. The installer does not edit your
Codex model configuration; choose GPT-5.5 in Codex if it is available to you.

## Install and verify

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

If that succeeds, BMADX is installed and verified.

## Paste this into Codex next

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.
Use the Architecture Guardrail Card silently unless a risk changes the safe mode.

My task:
<describe the change in plain English>

What I care about:
<speed / clarity / safety / cleanup / shipping>
```

## What a good first result looks like

For a normal bounded task, BMADX should:
- keep the answer compact,
- avoid making you think about process gears,
- give you a short execution shape,
- explain architecture tradeoffs in plain language when they matter,
- escalate only if the task really needs BMAD-heavy handling.

## If you want examples

- [What to Paste into Codex](what-to-paste-into-codex.md)
- [Architecture Guardrail Card](architecture-guardrail-card.md)
- [Install for Vibe Coders](install-for-vibe-coders.md)
- [FAQ](faq.md)
