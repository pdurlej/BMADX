#!/usr/bin/env python3
"""Tests for the BMADX install-and-verify wrapper."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from install_and_verify_bmadx import CANONICAL_NEXT_PROMPT, MODEL_NOTE, install_and_verify


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_source(root: Path) -> Path:
    source = root / "repo" / "skill" / "bmadx"
    write(source / "SKILL.md", "---\nname: bmadx\n---\n")
    write(source / "scripts" / "sync_bmadx.py", "print('sync ok')\n")
    write(source / "scripts" / "test_sync_bmadx.py", "print('tests ok')\n")
    return source


def build_dependency(root: Path) -> Path:
    dependency = root / "skills" / "bmad-method-codex"
    write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")
    return dependency


class RunnerStub:
    def __init__(self, return_codes: list[int] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.return_codes = return_codes or [0, 0]

    def __call__(self, command, capture_output, text, check):
        self.calls.append(list(command))
        return_code = self.return_codes[len(self.calls) - 1]
        return subprocess.CompletedProcess(command, return_code, stdout="ok\n", stderr="")


class InstallAndVerifyTests(unittest.TestCase):
    def test_dry_run_reports_verification_and_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"

            message = install_and_verify(source, dependency, target, force=False, dry_run=True)

            self.assertIn("would verify with", message)
            self.assertIn(MODEL_NOTE, message)
            self.assertIn(CANONICAL_NEXT_PROMPT, message)

    def test_happy_path_runs_verification_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"
            runner = RunnerStub()

            message = install_and_verify(source, dependency, target, force=False, dry_run=False, runner=runner)

            self.assertEqual(len(runner.calls), 2)
            self.assertTrue(target.joinpath("SKILL.md").exists())
            self.assertIn("verification completed", message)
            self.assertIn(MODEL_NOTE, message)
            self.assertIn(CANONICAL_NEXT_PROMPT, message)

    def test_missing_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            with self.assertRaises(FileNotFoundError):
                install_and_verify(source, dependency, target, force=False, dry_run=False)

    def test_verification_failure_raises_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"
            runner = RunnerStub(return_codes=[0, 1])

            with self.assertRaises(RuntimeError):
                install_and_verify(source, dependency, target, force=False, dry_run=False, runner=runner)


if __name__ == "__main__":
    unittest.main()
