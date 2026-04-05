#!/usr/bin/env python3
"""Tests for the BMADX installer."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from install_bmadx import install_skill


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class InstallBmadxTests(unittest.TestCase):
    def test_install_copies_skill_when_dependency_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "repo" / "skill" / "bmadx"
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            write(source / "SKILL.md", "---\nname: bmadx\n---\n")
            write(source / "scripts" / "sync_bmadx.py", "print('ok')\n")
            write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")

            message = install_skill(source, dependency, target, force=False, dry_run=False)

            self.assertIn("installed successfully", message)
            self.assertTrue(target.joinpath("SKILL.md").exists())
            self.assertTrue(target.joinpath("scripts", "sync_bmadx.py").exists())

    def test_install_requires_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "repo" / "skill" / "bmadx"
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            write(source / "SKILL.md", "---\nname: bmadx\n---\n")

            with self.assertRaises(FileNotFoundError):
                install_skill(source, dependency, target, force=False, dry_run=False)

    def test_install_requires_force_for_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "repo" / "skill" / "bmadx"
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            write(source / "SKILL.md", "---\nname: bmadx\n---\n")
            write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")
            write(target / "SKILL.md", "old\n")

            with self.assertRaises(FileExistsError):
                install_skill(source, dependency, target, force=False, dry_run=False)

    def test_dry_run_does_not_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "repo" / "skill" / "bmadx"
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            write(source / "SKILL.md", "---\nname: bmadx\n---\n")
            write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")

            message = install_skill(source, dependency, target, force=False, dry_run=True)

            self.assertIn("Dry run only", message)
            self.assertFalse(target.exists())

    def test_dry_run_allows_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "repo" / "skill" / "bmadx"
            dependency = root / "skills" / "bmad-method-codex"
            target = root / "skills" / "bmadx"

            write(source / "SKILL.md", "---\nname: bmadx\n---\n")
            write(dependency / "SKILL.md", "---\nname: bmad-method-codex\n---\n")
            write(target / "SKILL.md", "already-here\n")

            message = install_skill(source, dependency, target, force=False, dry_run=True)

            self.assertIn("would replace existing target", message)
            self.assertEqual(target.joinpath("SKILL.md").read_text(encoding="utf-8"), "already-here\n")


if __name__ == "__main__":
    unittest.main()
