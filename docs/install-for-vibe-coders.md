# Install BMADX in Codex for Vibe Coders

This is the shortest realistic path if you want BMADX in your own Codex setup
without manually poking through the repo.

## What you need first

BMADX depends on `bmad-method-codex`.

So before installing BMADX, make sure you already have:

```bash
ls ~/.codex/skills/bmad-method-codex/SKILL.md
```

If that file is missing, install or sync `bmad-method-codex` first.

## Fast manual install

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_bmadx.py --force
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py sync --json
```

If the last command returns a healthy result, BMADX is installed.

## Vibe-coder path: let Codex do it

If you want to ask Codex to install it for you, give Codex this repo URL:

```text
https://github.com/pdurlej/BMADX
```

Then paste this prompt:

```text
Install BMADX from this repository into my Codex skills.
First verify that ~/.codex/skills/bmad-method-codex exists.
If BMAD is missing, stop and tell me to install it first.
If it exists, clone the repo, run `python3 scripts/install_bmadx.py --force`,
then verify with `python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py sync --json`
and `python3 ~/.codex/skills/bmadx/scripts/test_sync_bmadx.py`.
```

That is the cleanest low-friction path for users who want the tool but do not
want to manually inspect the skill internals first.

## Quick smoke checks

After install, these are the most useful first commands:

```bash
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X1 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X2 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X3 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X4 --compact
```

## What BMADX gives you after install

- automatic routing between `X1`, `X2`, `X3`, and `X4`
- a compact dependency gate after classification
- a lighter operator experience than a heavier orchestration runtime
- an `X4/FUBAR` bundle path for messy projects

## If install fails

The most likely reasons are:
- `bmad-method-codex` is missing
- your Codex skills directory is not under `~/.codex/skills`
- an older `bmadx` install already exists and you did not use `--force`

If in doubt, run:

```bash
python3 scripts/install_bmadx.py --dry-run
```
