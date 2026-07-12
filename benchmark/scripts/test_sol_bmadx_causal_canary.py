#!/usr/bin/env python3
"""Tests for the frozen three-arm Sol/BMADX causal canary."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_sol_bmadx_ab import all_scenarios
from run_sol_bmadx_causal_canary import (
    DEFAULT_PROTOCOL,
    install_aliased_bmadx_skill,
    install_placebo_skill,
    install_stub_bmad,
    load_protocol,
    protected_hashes,
    raw_artifact_paths,
    validate_protocol,
)
from sol_bmadx_ab_contract import build_causal_prompt, score_causal_response


class SolBmadxCausalCanaryTests(unittest.TestCase):
    def test_frozen_protocol_is_complete_and_valid(self) -> None:
        protocol = load_protocol(DEFAULT_PROTOCOL)
        validate_protocol(protocol, all_scenarios())
        assignments = protocol["assignments"]
        self.assertEqual(len(assignments), 18)
        self.assertEqual(len({item["alias"] for item in assignments}), 18)
        self.assertEqual(len({item["nonce"] for item in assignments}), 18)
        self.assertEqual(
            {(item["arm"], item["scenario"]) for item in assignments},
            {
                (arm, scenario)
                for arm in ("placebo", "bmadx_stub", "bmadx_real")
                for scenario in protocol["scenarios"]
            },
        )

    def test_protocol_rejects_source_hash_drift(self) -> None:
        protocol = load_protocol(DEFAULT_PROTOCOL)
        protocol["source_hashes"]["bmadx_tree_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "BMADX source tree hash"):
            validate_protocol(protocol, all_scenarios())

    def test_prompt_exposes_only_opaque_alias(self) -> None:
        prompt = build_causal_prompt("Fix the callback.", "wf-1234567890")
        self.assertIn("$wf-1234567890", prompt)
        self.assertNotIn("bmadx", prompt.lower())
        self.assertNotIn("activation-secret", prompt)
        self.assertNotIn("X1", prompt)

    def test_placebo_skill_contains_nonce_without_treatment_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            install_placebo_skill(home, "wf-placebo", "a" * 32)
            content = (home / "skills" / "wf-placebo" / "SKILL.md").read_text(
                encoding="utf-8"
            )
        self.assertIn("a" * 32, content)
        self.assertNotIn("BMADX", content.upper())
        self.assertNotIn("X1", content)

    def test_aliased_skill_rewrites_name_and_nonce(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            install_aliased_bmadx_skill(home, "wf-treatment", "b" * 32)
            content = (home / "skills" / "wf-treatment" / "SKILL.md").read_text(
                encoding="utf-8"
            )
        self.assertIn("name: wf-treatment", content)
        self.assertNotIn("name: bmadx\n", content)
        self.assertIn("b" * 32, content)

    def test_stub_dependency_reports_healthy_without_workflow_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = install_stub_bmad(Path(tmpdir))
            result = subprocess.run(
                ["python3", str(target / "scripts" / "sync_bmad_method.py"), "check", "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            skill = (target / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(payload["action"], "ok")
        self.assertEqual(payload["latest_release"]["tag"], "stub-healthy-v1")
        self.assertIn("No workflow guidance", skill)

    def test_protected_hashes_ignore_runtime_bookkeeping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            workdir = root / "workspace"
            install_placebo_skill(home, "wf-placebo", "a" * 32)
            workdir.mkdir()
            before = protected_hashes(home, workdir, "wf-placebo")
            (home / "models_cache.json").write_text("{}\n", encoding="utf-8")
            (home / "state_5.sqlite").write_bytes(b"runtime bookkeeping")
            after = protected_hashes(home, workdir, "wf-placebo")
        self.assertEqual(before, after)

    def test_protected_hashes_detect_assigned_skill_and_workspace_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            workdir = root / "workspace"
            install_placebo_skill(home, "wf-placebo", "a" * 32)
            workdir.mkdir()
            before = protected_hashes(home, workdir, "wf-placebo")
            (home / "skills" / "wf-placebo" / "extra.txt").write_text("changed\n")
            (workdir / "output.txt").write_text("changed\n")
            after = protected_hashes(home, workdir, "wf-placebo")
        self.assertNotEqual(before["assigned_skill"], after["assigned_skill"])
        self.assertNotEqual(before["workspace"], after["workspace"])

    def test_raw_artifact_paths_preserve_dotted_protocol_version(self) -> None:
        raw_txt, raw_log = raw_artifact_paths(
            "canary-sol-bmadx-causal-canary-v1.2-gpt-5-6-sol-o01-placebo-x1"
        )
        self.assertTrue(raw_txt.name.endswith("-o01-placebo-x1.txt"))
        self.assertTrue(raw_log.name.endswith("-o01-placebo-x1.log"))
        self.assertNotEqual(raw_txt, raw_log)

    def test_causal_scorer_requires_exact_nonce(self) -> None:
        nonce = "c" * 32
        stdout = json.dumps(
            {
                "activation_nonce": nonce,
                "process": "direct",
                "risk": "low",
                "handoff": False,
                "goal": False,
                "goal_stop": None,
                "loop": False,
                "loop_max_passes": None,
                "loop_stop": None,
                "safeguards": [],
                "reasons": ["tiny local change"],
            }
        )
        result = score_causal_response(
            stdout,
            all_scenarios()["x1"],
            expected_nonce=nonce,
            known_nonces={nonce, "d" * 32},
            required_safeguards=[],
            safety_critical=False,
        )
        self.assertTrue(result["activation_pass"])
        self.assertTrue(result["primary_pass"])
        self.assertFalse(result["cross_arm_nonce"])

    def test_causal_scorer_detects_cross_arm_nonce_and_safety_failure(self) -> None:
        expected = "e" * 32
        other = "f" * 32
        stdout = json.dumps(
            {
                "activation_nonce": other,
                "process": "bounded",
                "risk": "moderate",
                "handoff": False,
                "goal": False,
                "goal_stop": None,
                "loop": False,
                "loop_max_passes": None,
                "loop_stop": None,
                "safeguards": [],
                "reasons": ["limited change"],
            }
        )
        result = score_causal_response(
            stdout,
            all_scenarios()["google-login"],
            expected_nonce=expected,
            known_nonces={expected, other},
            required_safeguards=[["callback"], ["session"]],
            safety_critical=True,
        )
        self.assertFalse(result["activation_pass"])
        self.assertTrue(result["cross_arm_nonce"])
        self.assertTrue(result["concrete_safety_failure"])


if __name__ == "__main__":
    unittest.main()
