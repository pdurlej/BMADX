#!/usr/bin/env python3
"""Install BMADX, verify it, and print the next prompt to paste into Codex."""

from __future__ import annotations

import argparse
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

My task:
<describe the change in plain English>

What I care about:
<speed / clarity / safety / cleanup / shipping>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = build_install_parser()
    parser.description = "Install BMADX, verify the install, and print the next prompt to paste into Codex."
    return parser


def verification_commands(target: Path) -> list[list[str]]:
    sync_script = target / "scripts" / "sync_bmadx.py"
    test_script = target / "scripts" / "test_sync_bmadx.py"
    return [
        ["python3", str(sync_script), "sync", "--json"],
        ["python3", str(test_script)],
    ]


def run_verification(
    commands: list[list[str]],
    runner: Callable[..., subprocess.CompletedProcess[str]],
) -> list[str]:
    completed: list[str] = []
    for command in commands:
        result = runner(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or "no output"
            raise RuntimeError(f"Verification failed for `{' '.join(command)}`: {detail}")
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
        lines = [install_message, "- would verify with:"]
        lines.extend(f"  - {' '.join(command)}" for command in commands)
        lines.append("- next prompt to paste into Codex:")
        lines.append(CANONICAL_NEXT_PROMPT)
        return "\n".join(lines)

    completed = run_verification(commands, runner)
    lines = [install_message, "- verification completed:"]
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
