#!/usr/bin/env python3
"""Smoke and unit tests for sync_bmadx.py."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().with_name("sync_bmadx.py")

LOCAL_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/gearbox.md",
    "references/trigger-matrix.md",
    "references/bmadx-vs-bmad.md",
    "references/subagent-policy.md",
    "references/verify-discipline.md",
    "references/fubar-bundle-spec.md",
    "references/skill-manifest.json",
    "scripts/sync_bmadx.py",
    "scripts/test_sync_bmadx.py",
    "scripts/render_fubar_bundle.py",
    "assets/templates/AGENTS.repo.md",
    "assets/templates/core-bmad-master.customize.yaml",
    "assets/templates/bmm-dev.customize.yaml",
    "assets/templates/bmm-architect.customize.yaml",
    "assets/templates/trigger-matrix.md",
    "assets/templates/verify-matrix.md",
    "assets/templates/rollout-checklist.md",
    "assets/templates/subagent-policy.md",
]

BMAD_REFS = [
    "docs_reference_workflow_map.md",
    "docs_reference_commands.md",
    "docs_reference_agents.md",
    "docs_reference_modules.md",
    "latest-release-summary.md",
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_manifest() -> dict:
    return {
        "name": "bmadx",
        "skill_version": "0.2.2",
        "target_codex_profile": "codex-5.4",
        "required_bmad_references": BMAD_REFS,
        "tracked_local_files": LOCAL_FILES,
        "template_checks": {
            "assets/templates/AGENTS.repo.md": [
                "BMAD > BMADX",
                "_bmad-output/project-context.md",
                "X1",
                "X4",
                "bmad-help",
            ],
            "assets/templates/core-bmad-master.customize.yaml": [
                "_bmad-output/project-context.md",
                "verify-before-done",
                "X1",
                "X4",
            ],
            "assets/templates/bmm-dev.customize.yaml": [
                "_bmad-output/project-context.md",
                "verify-before-done",
                "X2",
                "X3",
            ],
            "assets/templates/bmm-architect.customize.yaml": [
                "_bmad-output/project-context.md",
                "X3",
                "X4",
            ],
        },
    }


def make_root(tmp: Path) -> Path:
    root = tmp / "bmadx"
    write(root / "SKILL.md", "---\nname: bmadx\ndescription: test\n---\n")
    write(root / "agents" / "openai.yaml", "interface:\n  display_name: \"BMADX\"\n")
    write(root / "references" / "gearbox.md", "x1 x2 x3 x4\n")
    write(root / "references" / "trigger-matrix.md", "matrix\n")
    write(root / "references" / "bmadx-vs-bmad.md", "BMAD > BMADX\n")
    write(root / "references" / "subagent-policy.md", "policy\n")
    write(root / "references" / "verify-discipline.md", "verify\n")
    write(root / "references" / "fubar-bundle-spec.md", "spec\n")
    write(root / "references" / "skill-manifest.json", json.dumps(build_manifest(), indent=2) + "\n")
    write(root / "scripts" / "sync_bmadx.py", "placeholder\n")
    write(root / "scripts" / "test_sync_bmadx.py", "placeholder\n")
    write(root / "scripts" / "render_fubar_bundle.py", "placeholder\n")
    write(
        root / "assets" / "templates" / "AGENTS.repo.md",
        "BMAD > BMADX\n_bmad-output/project-context.md\nX1\nX4\nbmad-help\n",
    )
    write(
        root / "assets" / "templates" / "core-bmad-master.customize.yaml",
        "_bmad-output/project-context.md\nverify-before-done\nX1\nX4\n",
    )
    write(
        root / "assets" / "templates" / "bmm-dev.customize.yaml",
        "_bmad-output/project-context.md\nverify-before-done\nX2\nX3\n",
    )
    write(
        root / "assets" / "templates" / "bmm-architect.customize.yaml",
        "_bmad-output/project-context.md\nX3\nX4\n",
    )
    write(root / "assets" / "templates" / "trigger-matrix.md", "matrix\n")
    write(root / "assets" / "templates" / "verify-matrix.md", "verify\n")
    write(root / "assets" / "templates" / "rollout-checklist.md", "rollout\n")
    write(root / "assets" / "templates" / "subagent-policy.md", "policy\n")
    return root


def make_bmad_skill(
    tmp: Path,
    release_tag: str = "v1.0.0",
    *,
    action: str = "ok",
    warnings: list[str] | None = None,
    return_code: int = 0,
) -> Path:
    bmad = tmp / "bmad-method-codex"
    write(bmad / "SKILL.md", "---\nname: bmad-method-codex\ndescription: test\n---\n")
    for name in BMAD_REFS:
        write(bmad / "references" / "upstream" / name, f"{name}:{release_tag}\n")
    payload = {
        "mode": "check",
        "latest_release": {"tag": release_tag},
        "warnings": warnings or [],
        "is_optimal": action == "ok",
        "action": action,
        "health": {"versions_match": action == "ok"},
    }
    script = textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        import json
        import sys
        payload = {repr(payload)}
        print(json.dumps(payload))
        raise SystemExit({return_code})
        """
    )
    write(bmad / "scripts" / "sync_bmad_method.py", script)
    os.chmod(bmad / "scripts" / "sync_bmad_method.py", 0o755)
    return bmad


class SyncBmadxTests(unittest.TestCase):
    def run_sync(
        self,
        root: Path,
        bmad_path: Path | None,
        *,
        gear: str | None = None,
        mode: str = "check",
        state_path: Path | None = None,
        compact: bool = False,
    ) -> dict:
        env = os.environ.copy()
        env["BMADX_ROOT"] = str(root)
        env["BMADX_MANIFEST_FILE"] = str(root / "references" / "skill-manifest.json")
        env["BMADX_STATE_FILE"] = str(state_path or (root / "state" / "bmadx-state.json"))
        if bmad_path is not None:
            env["BMADX_BMAD_SKILL_PATH"] = str(bmad_path)
        else:
            env["BMADX_BMAD_SKILL_PATH"] = str(root / "missing-bmad-method-codex")
        command = ["python3", str(SCRIPT_PATH), mode]
        if gear is not None:
            command.extend(["--gear", gear])
        if compact:
            command.append("--compact")
        command.append("--json")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return json.loads(result.stdout)

    def test_healthy_path_returns_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(tmp)
            payload = self.run_sync(root, bmad)
            self.assertEqual(payload["action"], "ok")
            self.assertTrue(payload["classification_allowed"])
            self.assertTrue(payload["execution_allowed"])
            self.assertTrue(payload["bmad_dependency"]["healthy"])
            self.assertTrue(payload["bmad_dependency"]["cache"]["available"])
            self.assertTrue(payload["bmad_dependency"]["checked_live"])

    def test_missing_bmad_only_warns_without_requested_gear(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            payload = self.run_sync(root, None)
            self.assertEqual(payload["action"], "warning")
            self.assertTrue(payload["classification_allowed"])
            self.assertFalse(payload["execution_allowed"])
            self.assertFalse(payload["bmad_dependency"]["available"])
            self.assertTrue(payload["bmad_dependency"]["checked_live"])

    def test_x2_without_cache_uses_local_fast_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            payload = self.run_sync(root, None, gear="X2")
            self.assertEqual(payload["action"], "warning")
            self.assertTrue(payload["classification_allowed"])
            self.assertTrue(payload["execution_allowed"])
            self.assertFalse(payload["bmad_dependency"]["checked_live"])
            self.assertFalse(payload["bmad_dependency"]["cache_used"])
            self.assertIn("lokalnym stanie BMADX", payload["warning"])
            self.assertIn(
                "Brak świeżego checka BMAD dla `X3/X4`.",
                payload["execution_gate"]["by_gear"]["X3"]["blockers"],
            )

    def test_x1_with_healthy_cache_skips_live_red_bmad(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            healthy = make_bmad_skill(tmp, "v1.0.0")
            warmup = self.run_sync(root, healthy, mode="sync")
            self.assertEqual(warmup["action"], "ok")

            unhealthy = make_bmad_skill(
                tmp,
                "v1.0.0",
                action="needs_attention",
                warnings=["BMAD dependency is red."],
            )
            payload = self.run_sync(root, unhealthy, gear="X1")
            self.assertEqual(payload["action"], "ok")
            self.assertTrue(payload["execution_allowed"])
            self.assertFalse(payload["bmad_dependency"]["checked_live"])
            self.assertTrue(payload["bmad_dependency"]["cache_used"])
            self.assertIsNone(payload["warning"])

    def test_red_bmad_blocks_x3_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(
                tmp,
                action="needs_attention",
                warnings=["BMAD dependency is red."],
            )
            payload = self.run_sync(root, bmad, gear="X3")
            self.assertEqual(payload["action"], "needs_attention")
            self.assertFalse(payload["execution_allowed"])
            self.assertIn(
                "Bieżący check BMAD nie jest zdrowy.",
                payload["execution_gate"]["by_gear"]["X3"]["blockers"],
            )
            self.assertEqual(
                payload["remediation"],
                [
                    "python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py check --json",
                    "python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py sync",
                ],
            )

    def test_x4_with_healthy_bmad_execution_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(tmp, "v1.0.0")
            payload = self.run_sync(root, bmad, gear="X4")
            self.assertEqual(payload["action"], "ok")
            self.assertTrue(payload["execution_allowed"])
            self.assertEqual(payload["remediation"], [])
            self.assertTrue(payload["bmad_dependency"]["checked_live"])

    def test_bmad_release_drift_blocks_x3_until_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(tmp, "v1.0.0")
            first = self.run_sync(root, bmad, gear="X3")
            self.assertEqual(first["action"], "ok")

            make_bmad_skill(tmp, "v1.1.0")
            second = self.run_sync(root, bmad, gear="X3")
            self.assertEqual(second["action"], "needs_attention")
            self.assertFalse(second["execution_allowed"])
            self.assertIn("v1.0.0", "\n".join(second["warnings"]))
            self.assertIn(
                "Wykryto zmianę releasu BMAD od ostatniego zapisu.",
                second["execution_gate"]["by_gear"]["X3"]["blockers"],
            )

    def test_state_write_failure_does_not_crash_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(tmp)
            bad_parent = root / "state-parent-file"
            bad_parent.write_text("not a directory\n", encoding="utf-8")
            state_path = bad_parent / "bmadx-state.json"

            payload = self.run_sync(root, bmad, state_path=state_path)
            self.assertEqual(payload["action"], "ok")
            self.assertFalse(payload["state_persisted"])
            self.assertIn("Nie udało się zapisać stanu BMADX", payload["state_write_warning"])

    def test_compact_x1_schema_is_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            payload = self.run_sync(root, None, gear="X1", compact=True)
            self.assertEqual(
                set(payload),
                {
                    "skill_version",
                    "requested_gear",
                    "classification_allowed",
                    "execution_allowed",
                    "warning",
                    "bmad_status",
                    "cache_used",
                    "remediation",
                },
            )
            self.assertEqual(payload["skill_version"], "0.2.2")
            self.assertEqual(payload["requested_gear"], "X1")
            self.assertTrue(payload["execution_allowed"])
            self.assertEqual(payload["bmad_status"], "warning")
            self.assertFalse(payload["cache_used"])
            self.assertEqual(payload["remediation"], [])

    def test_compact_x3_blocked_returns_needs_attention_and_exact_remediation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            root = make_root(tmp)
            bmad = make_bmad_skill(
                tmp,
                action="needs_attention",
                warnings=["BMAD dependency is red."],
            )
            payload = self.run_sync(root, bmad, gear="X3", compact=True)
            self.assertFalse(payload["execution_allowed"])
            self.assertEqual(payload["bmad_status"], "needs_attention")
            self.assertEqual(
                payload["remediation"],
                [
                    "python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py check --json",
                    "python3 /Users/pd/.codex/skills/bmad-method-codex/scripts/sync_bmad_method.py sync",
                ],
            )


if __name__ == "__main__":
    unittest.main()
