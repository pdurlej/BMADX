# Contributing to BMADX

Thanks for considering a contribution.

## Before you change anything

Understand the project boundary first:
- `BMAD` is the upstream process system
- `BMADX` is the tactical overlay for Codex
- `OMX` is a source of selected inspiration, not a runtime target

Non-negotiable rule:
- `BMAD > BMADX`

## Good contributions

The repo benefits most from contributions that improve:
- practical routing behavior
- verification discipline
- installability and public usability
- benchmark quality
- `X4/FUBAR` bundle usefulness without making `X4` the default mode

## Contributions to avoid

Please avoid contributions that:
- turn BMADX into a competing process system
- port `.omx` runtime concepts wholesale
- add ceremony for the sake of elegance
- make `X4` the common path for ordinary tasks

## Development notes

Key locations:
- [`skill/bmadx`](skill/bmadx) - the actual skill
- [`benchmark/scripts`](benchmark/scripts) - benchmark runner and tests
- [`docs`](docs) - public documentation
- [`samples/fubar-bundle`](samples/fubar-bundle) - generated bundle example

## Verify

If you change the BMADX skill:

```bash
python3 skill/bmadx/scripts/test_sync_bmadx.py
python3 skill/bmadx/scripts/sync_bmadx.py check --json
```

If you change install surfaces:

```bash
python3 scripts/test_install_bmadx.py
python3 scripts/test_install_and_verify_bmadx.py
python3 scripts/install_and_verify_bmadx.py --dry-run
```

If you change benchmark behavior:

```bash
python3 benchmark/scripts/test_run_bmadx_benchmark.py
python3 benchmark/scripts/run_bmadx_benchmark.py --profile healthy --date-stamp 2026-04-06
```

If you change `X4` artifacts:

```bash
python3 skill/bmadx/scripts/render_fubar_bundle.py \
  --project-name BMADX \
  --project-path "$PWD" \
  --output-dir samples/fubar-bundle \
  --include-architect \
  --public-sample \
  --json
```

## Documentation

Public-facing documentation should be English and portable.
