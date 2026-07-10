#!/usr/bin/env python3
"""Report Codex CLI and model-catalog compatibility without exposing auth data."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "references" / "model-profiles.json"
TARGET_MODELS = ("gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna")
COMMAND_TIMEOUT_SECONDS = 30


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)", value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def load_profiles(path: Path = PROFILES_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("profiles"), dict):
        raise RuntimeError(f"{path}: expected a profiles object")
    return payload


def run_checked(
    command: list[str],
    runner: Callable[..., subprocess.CompletedProcess[str]],
) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Could not run {' '.join(command)}: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "no output").strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return result


def build_report(
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict:
    profiles = load_profiles()
    version_result = run_checked(["codex", "--version"], runner)
    catalog_result = run_checked(["codex", "debug", "models", "--bundled"], runner)

    observed_version = parse_version(version_result.stdout)
    if observed_version is None:
        raise RuntimeError(f"Could not parse Codex CLI version from {version_result.stdout!r}")

    catalog = json.loads(catalog_result.stdout)
    catalog_models = {
        str(item.get("slug")): item
        for item in catalog.get("models") or []
        if isinstance(item, dict) and item.get("slug")
    }

    model_reports: dict[str, dict] = {}
    warnings: list[str] = []
    for model in TARGET_MODELS:
        expected = profiles["profiles"].get(model)
        if not isinstance(expected, dict):
            warnings.append(f"{model} is missing from BMADX model-profiles.json")
            model_reports[model] = {
                "catalog_present": model in catalog_models,
                "cli_ready": False,
                "catalog_matches_profile": False,
                "default_reasoning": (catalog_models.get(model) or {}).get("default_reasoning_level"),
                "supported_reasoning": [],
                "bmadx_status": "missing-profile",
            }
            continue
        observed = catalog_models.get(model)
        observed_efforts = [
            str(item.get("effort"))
            for item in (observed or {}).get("supported_reasoning_levels") or []
            if isinstance(item, dict) and item.get("effort")
        ]
        expected_efforts = [str(value) for value in expected.get("supported_reasoning") or []]
        minimum = parse_version(str(expected.get("minimum_codex_cli") or ""))
        cli_ready = minimum is None or observed_version >= minimum
        catalog_match = observed is not None and set(observed_efforts) == set(expected_efforts)
        if not cli_ready:
            warnings.append(f"{model} requires Codex CLI >= {expected.get('minimum_codex_cli')}")
        if observed is None:
            warnings.append(f"{model} is missing from the bundled Codex model catalog")
        elif not catalog_match:
            warnings.append(f"{model} reasoning levels differ from BMADX model-profiles.json")
        model_reports[model] = {
            "catalog_present": observed is not None,
            "cli_ready": cli_ready,
            "catalog_matches_profile": catalog_match,
            "default_reasoning": (observed or {}).get("default_reasoning_level"),
            "supported_reasoning": observed_efforts,
            "bmadx_status": expected.get("status"),
        }

    return {
        "codex_cli_version": ".".join(map(str, observed_version)),
        "gpt56_ready": not warnings,
        "models": model_reports,
        "warnings": warnings,
        "note": "Catalog presence proves local CLI capability, not account entitlement or BMADX benchmark promotion.",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Codex compatibility for BMADX model profiles")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--require-gpt56",
        action="store_true",
        help="Exit non-zero unless all GPT-5.6 profiles match the local Codex catalog",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report()
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2) + "\n")
    else:
        print(f"codex_cli_version={report['codex_cli_version']}")
        print(f"gpt56_ready={str(report['gpt56_ready']).lower()}")
        for warning in report["warnings"]:
            print(f"warning: {warning}")
    return 0 if report["gpt56_ready"] or not args.require_gpt56 else 1


if __name__ == "__main__":
    raise SystemExit(main())
