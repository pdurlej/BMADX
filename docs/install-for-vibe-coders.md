# Install BMADX in Codex for Vibe Coders

This page is for people who want the shortest realistic install path.

## Use the wrapper

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

That wrapper:
- checks that `bmad-method-codex` exists,
- installs BMADX into your Codex skills,
- runs sync,
- runs BMADX skill tests,
- prints the next prompt to paste into Codex.

## Let Codex do it for you

Give Codex this repo URL:

```text
https://github.com/pdurlej/BMADX
```

Then paste:

```text
Install BMADX from this repository into my Codex skills.
Use the wrapper script if BMAD is already installed.
If BMAD is missing, stop and tell me to install `bmad-method-codex` first.
After install, give me the next prompt to paste into Codex.
```

## What to do next

Use one of the starter prompts from:
- [What to Paste into Codex](what-to-paste-into-codex.md)
- [5-Minute Quickstart](5-minute-quickstart.md)

## If install fails

Most failures come from one of these:
- `bmad-method-codex` is not installed yet
- your Codex skills directory is not where BMADX expects it
- an older `bmadx` install exists and you did not use `--force`

If you want to inspect the steps without changing anything:

```bash
python3 scripts/install_and_verify_bmadx.py --dry-run
```
