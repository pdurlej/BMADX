# Getting Started with BMADX

If you want the shortest path, use [5-Minute Quickstart](5-minute-quickstart.md).

This page is the slightly fuller version.

## What BMADX assumes

BMADX is a Codex skill, not a standalone app.

It assumes:
- you already use Codex,
- you want a BMAD-first layer on top of it,
- `bmad-method-codex` is already available in your Codex skills.

## Install

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
python3 scripts/install_and_verify_bmadx.py --force
```

What this does:
- verifies that `bmad-method-codex` exists,
- installs `skill/bmadx` into your Codex skills directory,
- runs `sync_bmadx.py sync --json`,
- runs BMADX skill tests,
- prints the next prompt to paste into Codex.

## First use

Open Codex in your project and paste:

```text
Use BMADX for this repo. Pick the lightest safe mode. Keep it lightweight unless BMAD is truly needed.

My task:
<describe the change in plain English>

What I care about:
<speed / clarity / safety / cleanup / shipping>
```

Most users should not choose `X1/X2/X3/X4` manually.

## What to read next

- [What to Paste into Codex](what-to-paste-into-codex.md)
- [Why BMAD is required](why-bmad-is-required.md)
- [Choose BMAD vs BMADX vs OMX](choose-bmad-bmadx-omx.md)
- [Rescue Mode (`X4/FUBAR`)](x4-rescue-mode.md)
