#!/usr/bin/env python3
"""Install BMADX, verify it, and print the next prompt to paste into Codex."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

from install_bmadx import (
    build_parser as build_install_parser,
    install_skill,
    repo_root,
    source_skill_path,
)

CANONICAL_NEXT_PROMPT = """Use BMADX for this repo. Pick the lightest safe mode.
Keep it lightweight unless BMAD is truly needed.
Use the Architecture Guardrail Card silently unless a risk changes the safe mode.
Suggest the thinking budget only if it matters for this task.

My task:
<describe the change in plain English>

What I care about:
<speed / clarity / safety / cleanup / shipping>
"""
MODEL_NOTE = (
    "BMADX supports profiled Codex runs on GPT-5.5 and GPT-5.6 Sol/Terra/Luna. "
    "GPT-5.6 requires Codex CLI 0.144.0 or newer; profiles remain candidates until their BMADX benchmarks pass. "
    "This installer does not change your Codex model or thinking config."
)
VERIFY_TIMEOUT_SECONDS = 60


def build_parser() -> argparse.ArgumentParser:
    parser = build_install_parser()
    parser.description = "Install BMADX, verify the install, and print the next prompt to paste into Codex."
    return parser


def verification_commands(target: Path) -> list[list[str]]:
    sync_script = target / "scripts" / "sync_bmadx.py"
    test_script = target / "scripts" / "test_sync_bmadx.py"
    planning_test_script = target / "scripts" / "test_advise_planning_effort.py"
    compat_script = target / "scripts" / "check_codex_compat.py"
    return [
        [sys.executable, str(sync_script), "sync", "--json"],
        [sys.executable, str(test_script)],
        [sys.executable, str(planning_test_script)],
        [sys.executable, str(compat_script), "--json"],
    ]


def validate_sync_report(stdout: str) -> None:
    try:
        payload = json.loads(stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Verification returned invalid BMADX sync JSON: {exc}") from exc

    healthy_dependency = bool((payload.get("bmad_dependency") or {}).get("healthy"))
    if (
        payload.get("action") != "ok"
        or payload.get("classification_allowed") is not True
        or payload.get("execution_allowed") is not True
        or healthy_dependency is not True
    ):
        detail = json.dumps(
            {
                "action": payload.get("action"),
                "classification_allowed": payload.get("classification_allowed"),
                "execution_allowed": payload.get("execution_allowed"),
                "bmad_dependency_healthy": healthy_dependency,
                "warning": payload.get("warning"),
            },
            sort_keys=True,
        )
        raise RuntimeError(f"BMADX semantic verification failed: {detail}")


def run_verification(
    commands: list[list[str]],
    runner: Callable[..., subprocess.CompletedProcess[str]],
) -> list[str]:
    completed: list[str] = []
    for index, command in enumerate(commands):
        try:
            result = runner(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=VERIFY_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Verification timed out after {VERIFY_TIMEOUT_SECONDS} seconds for `{' '.join(command)}`"
            ) from exc
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or "no output"
            raise RuntimeError(f"Verification failed for `{' '.join(command)}`: {detail}")
        if index == 0:
            validate_sync_report(result.stdout)
        completed.append(" ".join(command))
    return completed


def install_and_verify(
    source: Path,
    dependency_path: Path,
    target: Path,
    force: bool,
    dry_run: bool,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> str:
    install_message = install_skill(source, dependency_path, target, force=force, dry_run=dry_run)
    commands = verification_commands(target)

    if dry_run:
        lines = [install_message, f"- {MODEL_NOTE}", "- would verify with:"]
        lines.extend(f"  - {' '.join(command)}" for command in commands)
        lines.append("- next prompt to paste into Codex:")
        lines.append(CANONICAL_NEXT_PROMPT)
        return "\n".join(lines)

    completed = run_verification(commands, runner)
    lines = [install_message, f"- {MODEL_NOTE}", "- verification completed:"]
    lines.extend(f"  - {command}" for command in completed)
    lines.append("- next prompt to paste into Codex:")
    lines.append(CANONICAL_NEXT_PROMPT)
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source = source_skill_path(repo_root())

    try:
        message = install_and_verify(
            source=source,
            dependency_path=args.dependency_path.expanduser(),
            target=args.target.expanduser(),
            force=args.force,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
