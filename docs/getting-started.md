# Getting Started with BMADX

BMADX is a Codex skill, not a standalone app.

It assumes:
- you already use Codex,
- you want a `BMAD-first` routing layer on top of it,
- you already have the dependency skill `bmad-method-codex` available in your
  Codex skills directory.

## Prerequisites

- Python 3.10+
- a Codex install with access to `~/.codex/skills`
- `bmad-method-codex` installed at `~/.codex/skills/bmad-method-codex`

BMADX depends on BMAD.

If that dependency is missing, BMADX should not be treated as fully installed.

## Install from this repository

Clone the repo:

```bash
git clone https://github.com/pdurlej/BMADX.git
cd BMADX
```

Install the skill into your Codex skills directory:

```bash
python3 scripts/install_bmadx.py --force
```

What the installer does:
- checks that `bmad-method-codex` is present,
- copies `skill/bmadx` into `~/.codex/skills/bmadx`,
- stops with a clear error if BMAD is missing.

## Verify the install

Run:

```bash
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py sync --json
python3 ~/.codex/skills/bmadx/scripts/test_sync_bmadx.py
python3 scripts/test_install_bmadx.py
```

Expected result:
- BMADX sync succeeds,
- the BMADX skill tests pass,
- the installer tests pass.

## First practical checks

For the compact gear gate:

```bash
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X1 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X2 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X3 --compact
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --gear X4 --compact
```

For the verbose diagnostic report:

```bash
python3 ~/.codex/skills/bmadx/scripts/sync_bmadx.py check --json
```

## Rendering the `X4/FUBAR` bundle

If you want the scaffold bundle for a messy or high-entropy project:

```bash
python3 ~/.codex/skills/bmadx/scripts/render_fubar_bundle.py \
  --project-name "Your project" \
  --project-path "$PWD" \
  --output-dir /tmp/bmadx-fubar
```

This generates bundle artifacts such as:
- `AGENTS.md`
- `.customize.yaml` snippets
- trigger and verify matrices
- rollout checklist

## Running the benchmark

The benchmark runner is tracked in the repo:

```bash
python3 benchmark/scripts/run_bmadx_benchmark.py --profile healthy --date-stamp 2026-04-05
python3 benchmark/scripts/run_bmadx_benchmark.py --profile degraded --date-stamp 2026-04-05
```

Profiles:
- `healthy` measures the low-friction happy path,
- `degraded` checks routing and safety under dependency trouble.

## Recommended reading after install

- [Architecture](architecture.md)
- [Benchmark Overview](benchmark-overview.md)
- [BMADX skill contract](../skill/bmadx/SKILL.md)
