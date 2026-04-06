#!/usr/bin/env python3
"""Install the BMADX skill into a Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def default_target() -> Path:
    return default_codex_home() / "skills" / "bmadx"


def default_dependency() -> Path:
    return default_codex_home() / "skills" / "bmad-method-codex"


def codex_home_shell() -> str:
    return "${CODEX_HOME:-$HOME/.codex}"


def build_parser() -> argparse.ArgumentParser:
    target_default = default_target()
    dependency_default = default_dependency()
    parser = argparse.ArgumentParser(
        description="Install the BMADX skill from this repository into Codex."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=target_default,
        help=f"Target install path (default: {target_default})",
    )
    parser.add_argument(
        "--dependency-path",
        type=Path,
        default=dependency_default,
        help=(
            "Path to the required bmad-method-codex skill "
            f"(default: {dependency_default})"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing BMADX install at the target path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the intended actions without copying files.",
    )
    return parser


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def source_skill_path(root: Path) -> Path:
    return root / "skill" / "bmadx"


def validate_paths(
    source: Path,
    dependency_path: Path,
    target: Path,
    force: bool,
    dry_run: bool,
) -> None:
    if not source.joinpath("SKILL.md").exists():
        raise FileNotFoundError(f"BMADX source skill not found at {source}")

    if not dependency_path.joinpath("SKILL.md").exists():
        raise FileNotFoundError(
            "Required dependency skill `bmad-method-codex` was not found at "
            f"{dependency_path}. Install or sync BMAD first, then install BMADX."
        )

    if target.exists() and not force and not dry_run:
        raise FileExistsError(
            f"Target path {target} already exists. Re-run with --force to replace it."
        )


def install_skill(source: Path, dependency_path: Path, target: Path, force: bool, dry_run: bool) -> str:
    validate_paths(source, dependency_path, target, force, dry_run)

    if dry_run:
        target_state = (
            "would replace existing target" if target.exists() else "target does not exist yet"
        )
        return (
            "Dry run only.\n"
            f"- dependency confirmed at {dependency_path}\n"
            f"- target status: {target_state}\n"
            f"- would copy {source} -> {target}"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)

    return (
        "BMADX installed successfully.\n"
        f"- source: {source}\n"
        f"- target: {target}\n"
        f"- dependency: {dependency_path}\n"
        f'- next: run `python3 "{codex_home_shell()}/skills/bmadx/scripts/sync_bmadx.py" sync --json`'
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source = source_skill_path(repo_root())

    try:
        message = install_skill(
            source=source,
            dependency_path=args.dependency_path.expanduser(),
            target=args.target.expanduser(),
            force=args.force,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
