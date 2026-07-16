#!/usr/bin/env python3
"""Tests for the BMADX install-and-verify wrapper."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from install_and_verify_bmadx import (
    CANONICAL_NEXT_PROMPT,
    MODEL_NOTE,
    VERIFY_TIMEOUT_SECONDS,
    install_and_verify,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_source(root: Path) -> Path:
    source = root / "repo" / "skill" / "bmadx"
    write(source / "SKILL.md", "---\nname: bmadx\n---\n")
    write(source / "scripts" / "sync_bmadx.py", "print('sync ok')\n")
    write(source / "scripts" / "test_sync_bmadx.py", "print('tests ok')\n")
    write(source / "scripts" / "check_codex_compat.py", "print('{}')\n")
    return source


def build_dependency(root: Path) -> Path:
    dependency = root / "skills" / "bmad-method-codex"
    write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")
    return dependency


class RunnerStub:
    OK_SYNC_JSON = (
        '{"action":"ok","classification_allowed":true,"execution_allowed":true,'
        '"bmad_dependency":{"healthy":true}}'
    )

    def __init__(self, return_codes: list[int] | None = None, stdout_values: list[str] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.return_codes = return_codes or [0, 0, 0]
        self.stdout_values = stdout_values or [self.OK_SYNC_JSON, "tests ok\n", "{}\n"]

    def __call__(self, command, capture_output, text, check, timeout=None):
        self.calls.append(list(command))
        self.last_timeout = timeout
        return_code = self.return_codes[len(self.calls) - 1]
        stdout = self.stdout_values[len(self.calls) - 1]
        return subprocess.CompletedProcess(command, return_code, stdout=stdout, stderr="")


class TimeoutRunnerStub:
    def __call__(self, command, capture_output, text, check, timeout=None):
        raise subprocess.TimeoutExpired(command, timeout)


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

            self.assertEqual(len(runner.calls), 3)
            self.assertEqual(runner.calls[0][0], sys.executable)
            self.assertEqual(runner.calls[0][-4:], ["check", "--gear", "X3", "--json"])
            self.assertEqual(runner.calls[1][0], sys.executable)
            self.assertEqual(runner.last_timeout, VERIFY_TIMEOUT_SECONDS)
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

    def test_verification_rejects_needs_attention_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"
            runner = RunnerStub(
                stdout_values=[
                    (
                        '{"action":"needs_attention","classification_allowed":true,'
                        '"execution_allowed":false,"warning":"blocked",'
                        '"bmad_dependency":{"healthy":false}}'
                    ),
                    "tests ok\n",
                    "{}\n",
                ]
            )

            with self.assertRaisesRegex(RuntimeError, "semantic verification failed"):
                install_and_verify(source, dependency, target, force=False, dry_run=False, runner=runner)

    def test_verification_accepts_nonblocking_warning_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"
            runner = RunnerStub(
                stdout_values=[
                    (
                        '{"action":"warning","classification_allowed":true,'
                        '"execution_allowed":true,"warning":"soft",'
                        '"bmad_dependency":{"healthy":true}}'
                    ),
                    "tests ok\n",
                    "{}\n",
                ]
            )

            message = install_and_verify(
                source,
                dependency,
                target,
                force=False,
                dry_run=False,
                runner=runner,
            )
            self.assertIn("verification completed", message)

    def test_verification_timeout_raises_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = build_source(root)
            dependency = build_dependency(root)
            target = root / "skills" / "bmadx"

            with self.assertRaisesRegex(RuntimeError, "Verification timed out"):
                install_and_verify(
                    source,
                    dependency,
                    target,
                    force=False,
                    dry_run=False,
                    runner=TimeoutRunnerStub(),
                )


if __name__ == "__main__":
    unittest.main()
