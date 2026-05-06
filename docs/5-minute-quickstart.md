# 5-Minute Quickstart

This is the shortest realistic path from zero to a first useful BMADX task.

## Prerequisite

BMAD must already be installed in your Codex skills.

BMADX depends on `bmad-method-codex`. It does not replace it.

BMADX `v0.2.5` is tuned for Codex on GPT-5.5. The installer does not edit your
Codex model configuration; choose GPT-5.5 in Codex if it is available to you.

Check the BMAD dependency:

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills/bmad-method-codex/SKILL.md"
```

If that file is missing, install BMAD for Codex first.

## Install and verify

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

If that succeeds, BMADX is installed and verified.

## What the installer changes

- copies `skill/bmadx` into `${CODEX_HOME:-$HOME/.codex}/skills/bmadx`
- checks that `bmad-method-codex` is available
- runs BMADX sync/check verification
- runs the local installer verification path
- prints the next prompt to paste into Codex

It does not edit your global Codex model config, install hooks, create a runtime
state platform, or replace BMAD.

## Expected success output

The exact wording can change, but a successful run should end with a clear next
prompt and no dependency error. You should be able to run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bmadx/scripts/sync_bmadx.py" check --gear X1 --compact
```

Expected shape:

```json
{
  "classification_allowed": true,
  "execution_allowed": true,
  "bmad_status": "ok"
}
```

Extra fields are normal.

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

Tiny expected result:

```text
Choice: X1 / tiny local change
Why: This is copy-only and has no auth, billing, data, production, or migration risk.
Next step: Make the smallest patch and verify the changed page renders.
```

Normal bounded expected result:

```text
Choice: X2 / normal bounded change
Why: This is local product work with clear scope and no red-zone risk.
Plan:
1. Update the relevant component using existing patterns.
2. Keep the diff small and avoid unrelated refactors.
Verify:
1. Run the focused test or build command.
2. Check the changed page or flow manually.
```

## Re-run or uninstall

Re-run safely:

```bash
python3 scripts/install_and_verify_bmadx.py --force
```

Uninstall:

```bash
rm -rf "${CODEX_HOME:-$HOME/.codex}/skills/bmadx"
```

This removes BMADX from Codex skills. It does not remove BMAD.

## If you want examples

- [What to Paste into Codex](what-to-paste-into-codex.md)
- [Architecture Guardrail Card](architecture-guardrail-card.md)
- [Install for Vibe Coders](install-for-vibe-coders.md)
- [FAQ](faq.md)
