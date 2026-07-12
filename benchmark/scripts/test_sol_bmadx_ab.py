#!/usr/bin/env python3
"""Tests for the framework-neutral Sol/BMADX A/B benchmark."""

from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from os import environ
from pathlib import Path
from unittest.mock import patch

from run_sol_bmadx_ab import (
    ab_env,
    all_scenarios,
    artifact_stem,
    build_schedule,
    experiment_manifest,
    setup_home,
    write_checkpoint,
)
from sol_bmadx_ab_contract import build_neutral_prompt, score_neutral_response


class SolBmadxAbTests(unittest.TestCase):
    def test_prompts_share_contract_without_leaking_gears_to_plain(self) -> None:
        plain = build_neutral_prompt("Fix a typo.", "plain")
        bmadx = build_neutral_prompt("Fix a typo.", "bmadx")
        self.assertNotIn("$bmadx", plain.lower())
        self.assertNotIn("X1", plain)
        self.assertIn("without loading or invoking a workflow skill", plain)
        self.assertIn("Use $bmadx internally", bmadx)
        self.assertIn('"process":"direct|bounded|governed|recovery"', plain)
        self.assertIn('"process":"direct|bounded|governed|recovery"', bmadx)

    def test_neutral_scorer_accepts_matching_goal_without_loop(self) -> None:
        stdout = (
            '{"process":"governed","risk":"high","handoff":false,"goal":true,'
            '"goal_stop":"tests pass or approval blocks execution","loop":false,'
            '"loop_max_passes":null,"loop_stop":null,"reasons":["multi-turn auth work"]}'
        )
        result = score_neutral_response(
            stdout,
            {"expected_gear": "X3", "expected_goal": True, "expected_loop": False},
        )
        self.assertTrue(result["primary_pass"])
        self.assertFalse(result["ordinal_underclassification"])

    def test_neutral_scorer_detects_ordinal_underclassification(self) -> None:
        stdout = (
            '{"process":"bounded","risk":"moderate","handoff":false,"goal":false,'
            '"goal_stop":null,"loop":false,"loop_max_passes":null,"loop_stop":null,'
            '"reasons":["limited work"]}'
        )
        result = score_neutral_response(stdout, {"expected_gear": "X4"})
        self.assertTrue(result["ordinal_underclassification"])
        self.assertFalse(result["primary_pass"])

    def test_unscored_goal_handoff_and_loop_do_not_penalize_generic_scenario(self) -> None:
        stdout = (
            '{"process":"governed","risk":"high","handoff":true,"goal":true,'
            '"goal_stop":"tests pass","loop":true,"loop_max_passes":3,'
            '"loop_stop":"validation passes","reasons":["consequential work"]}'
        )
        result = score_neutral_response(
            stdout,
            {"expected_gear": "X3", "expected_risk": "high"},
        )
        self.assertTrue(result["primary_pass"])
        self.assertFalse(result["handoff_applicable"])
        self.assertFalse(result["goal_applicable"])
        self.assertFalse(result["loop_applicable"])

    def test_neutral_scorer_requires_bounded_loop(self) -> None:
        stdout = (
            '{"process":"recovery","risk":"critical","handoff":false,"goal":true,'
            '"goal_stop":"approval or verified recovery","loop":true,'
            '"loop_max_passes":8,"loop_stop":"delta stops shrinking",'
            '"reasons":["repair already failed twice"]}'
        )
        result = score_neutral_response(
            stdout,
            {
                "expected_gear": "X4",
                "expected_risk": "critical",
                "expected_goal": True,
                "expected_loop": True,
            },
        )
        self.assertFalse(result["loop_contract_pass"])

    def test_schedule_is_deterministic_interleaved_and_complete(self) -> None:
        scenarios = all_scenarios()
        first = build_schedule(scenarios, ["plain", "bmadx"], ["medium", "high", "xhigh"], 2, 42)
        second = build_schedule(scenarios, ["plain", "bmadx"], ["medium", "high", "xhigh"], 2, 42)
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(scenarios) * 2 * 3 * 2)
        self.assertGreater(len({(item["arm"], item["effort"]) for item in first[:12]}), 2)

    def test_every_scenario_has_explicit_goal_loop_and_handoff_truth(self) -> None:
        for spec in all_scenarios().values():
            self.assertIn("expected_handoff", spec)
            self.assertIn("expected_goal", spec)
            self.assertIn("expected_loop", spec)

    def test_artifact_stem_identifies_every_cell_dimension(self) -> None:
        stem = artifact_stem(
            "neutral-v1",
            {"arm": "plain", "effort": "xhigh", "repeat_index": 2, "scenario": "x4"},
            model="gpt-5.6-sol",
            date_stamp="2026-07-12",
            seed=42,
        )
        self.assertEqual(
            stem,
            "sol-ab-gpt-5-6-sol-2026-07-12-s42-neutral-v1-plain-xhigh-r2-x4",
        )

    def test_ab_env_clears_inherited_bmad_values_and_pins_treatment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            environ,
            {
                "BMAD_RELEASE_API": "https://inherited.invalid",
                "BMAD_RAW_BASE": "https://inherited.invalid/raw",
                "BMAD_MAX_RETRIES": "99",
            },
        ):
            root = Path(tmpdir)
            home = root / "home"
            fixture = root / "fixture.json"
            fixture.write_text("{}\n", encoding="utf-8")
            plain = ab_env(home, "plain", None)
            treatment = ab_env(home, "bmadx", fixture)
        self.assertNotIn("BMAD_RELEASE_API", plain)
        self.assertNotIn("BMAD_RAW_BASE", plain)
        self.assertNotIn("BMAD_MAX_RETRIES", plain)
        self.assertEqual(treatment["BMAD_RELEASE_API"], fixture.resolve().as_uri())
        self.assertEqual(treatment["BMAD_MAX_RETRIES"], "0")
        self.assertNotIn("BMAD_RAW_BASE", treatment)

    def test_experiment_manifest_changes_with_repeat(self) -> None:
        base = Namespace(
            model="gpt-5.6-sol",
            arms=["plain", "bmadx"],
            efforts=["high"],
            repeat=1,
            seed=42,
            date_stamp="2026-07-12",
            run_label="test",
            case_timeout=180,
        )
        first = experiment_manifest(base, all_scenarios())
        base.repeat = 2
        second = experiment_manifest(base, all_scenarios())
        self.assertNotEqual(first["sha256"], second["sha256"])

    def test_checkpoint_is_atomic_and_requires_exact_case_set_for_complete(self) -> None:
        args = Namespace(
            model="gpt-5.6-sol",
            arms=["plain"],
            efforts=["high"],
            repeat=1,
            seed=42,
            date_stamp="2026-07-12",
            run_label="test",
            case_timeout=180,
        )
        scenarios = {"x1": all_scenarios()["x1"]}
        schedule = build_schedule(scenarios, args.arms, args.efforts, args.repeat, args.seed)
        manifest = experiment_manifest(args, scenarios)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "summary.json"
            write_checkpoint(path, args, schedule, [], manifest, {}, [])
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(payload["complete"])
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_plain_home_has_no_skills_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("run_sol_bmadx_ab.copy_runtime_files"):
                home = setup_home(Path(tmpdir), "plain", "gpt-5.6-sol")
            self.assertFalse((home / "skills").exists())

    def test_bmadx_home_requires_skill_manifest(self) -> None:
        def fake_copy_skills(home: Path) -> None:
            skill = home / "skills" / "bmadx"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: bmadx\n---\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("run_sol_bmadx_ab.copy_runtime_files"), patch(
                "run_sol_bmadx_ab.copy_skills", side_effect=fake_copy_skills
            ):
                home = setup_home(Path(tmpdir), "bmadx", "gpt-5.6-sol")
            self.assertTrue((home / "skills" / "bmadx" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
