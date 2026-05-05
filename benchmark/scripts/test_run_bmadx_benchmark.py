#!/usr/bin/env python3
"""Unit tests for benchmark validation helpers."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from run_bmadx_benchmark import (
    DEFAULT_MODEL,
    DEFAULT_REASONING,
    NON_TECH_SCENARIOS,
    benchmark_env,
    build_codex_command,
    build_prompt,
    build_summary,
    copy_runtime_files,
    detect_reference_reads,
    detect_selected_gear,
    explain_failures_for_non_technical_users,
    model_slug,
    parse_args,
    parse_json_report,
    parse_token_count,
    sanitize_stderr,
    summary_path_for,
    validate_case,
    validate_warmup_payload,
    validation_failures,
    write_healthy_bmad_fixture,
    write_config,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_parse_token_count_handles_nbsp(self) -> None:
        stderr = "tokens used\n10\u00a0306\n"
        self.assertEqual(parse_token_count(stderr), 10306)

    def test_parse_token_count_returns_none_when_missing(self) -> None:
        self.assertIsNone(parse_token_count("no usage footer here"))

    def test_sanitize_stderr_omits_analytics_html(self) -> None:
        stderr = """before
2026-04-24 WARN codex_analytics::client: events failed with status 403 Forbidden: <html>
  <body>challenge</body>
</html>
exec
tokens used
123
"""
        cleaned = sanitize_stderr(stderr)
        self.assertIn("[analytics warning omitted]", cleaned)
        self.assertNotIn("challenge", cleaned)
        self.assertIn("exec", cleaned)
        self.assertIn("tokens used\n123", cleaned)

    def test_build_prompt_keeps_benchmark_classification_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario = Path(tmpdir) / "scenario.txt"
            scenario.write_text("Intro\nTask: Create a rescue bundle.\n", encoding="utf-8")
            prompt = build_prompt(scenario)
            self.assertIn("Use $bmadx.", prompt)
            self.assertIn("Compact gate only.", prompt)
            self.assertIn("No analysis. For X1/X2 do not read refs.", prompt)
            self.assertIn("Do not implement/edit/render/inline artifacts.", prompt)
            self.assertIn("Task: Create a rescue bundle.", prompt)

    def test_detect_reference_reads_returns_unique_paths(self) -> None:
        stderr = """
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/gearbox.md"
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/gearbox.md"
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/trigger-matrix.md"
        """
        self.assertEqual(detect_reference_reads(stderr), ["gearbox.md", "trigger-matrix.md"])

    def test_detect_selected_gear_reads_choice_line(self) -> None:
        self.assertEqual(detect_selected_gear("Choice: `X2 — Regular`\nWhy: ..."), "X2")
        self.assertIsNone(detect_selected_gear("Why: This mentions X2 but does not choose it."))

    def test_validate_case_marks_reference_budget_failure_for_x1(self) -> None:
        stdout = "Choice: `X1 — One-shot`.\nWhy: ...\nNext step: ...\n"
        stderr = 'exec /bin/zsh -lc "sed -n \'1,220p\' /tmp/codex-home/skills/bmadx/references/gearbox.md"\n'
        validation = validate_case(
            stdout,
            stderr,
            8900,
            {
                "expected_gear": "X1",
                "max_lines": 5,
                "max_chars": 650,
                "max_tokens": 9000,
                "allow_reference_reads": False,
            },
        )
        self.assertTrue(validation["format_pass"])
        self.assertTrue(validation["token_count_present"])
        self.assertTrue(validation["token_pass"])
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["reference_budget_pass"])
        self.assertEqual(validation["reference_reads"], ["gearbox.md"])
        self.assertTrue(validation["overreach_pass"])

    def test_validate_case_routes_by_selected_gear_not_incidental_mentions(self) -> None:
        validation = validate_case(
            "Choice: `X2 — Regular`\nWhy: This is not X3.\n",
            "",
            1000,
            {"expected_gear": "X3", "allow_reference_reads": True},
        )
        self.assertEqual(validation["selected_gear"], "X2")
        self.assertIn("X3", validation["observed_gears"])
        self.assertFalse(validation["routing_pass"])

    def test_validate_case_fails_token_pass_when_count_is_missing(self) -> None:
        validation = validate_case(
            "Choice: `X1 — One-shot`.\nWhy: ...\nNext step: ...\n",
            "",
            None,
            {"expected_gear": "X1", "max_tokens": 9000, "allow_reference_reads": False},
        )
        self.assertFalse(validation["token_count_present"])
        self.assertFalse(validation["token_pass"])

    def test_default_model_is_gpt55(self) -> None:
        args = parse_args([])
        self.assertEqual(args.model, DEFAULT_MODEL)
        self.assertEqual(args.model, "gpt-5.5")
        self.assertEqual(args.reasoning, DEFAULT_REASONING)

    def test_model_override_still_supports_gpt54(self) -> None:
        args = parse_args(["--model", "gpt-5.4", "--reasoning", "high"])
        self.assertEqual(args.model, "gpt-5.4")
        self.assertEqual(args.reasoning, "high")

    def test_model_slug_is_filename_safe(self) -> None:
        self.assertEqual(model_slug("gpt-5.5"), "gpt-5-5")
        self.assertEqual(model_slug("GPT 5.4 Pro"), "gpt-5-4-pro")

    def test_non_technical_scenarios_cover_red_zones_and_rescue(self) -> None:
        self.assertEqual(NON_TECH_SCENARIOS["pricing-copy"]["expected_gear"], "X1")
        self.assertEqual(NON_TECH_SCENARIOS["onboarding-email"]["expected_gear"], "X2")
        self.assertEqual(NON_TECH_SCENARIOS["google-login"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["subscription-billing"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["delete-inactive-users"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["messy-migration-incident"]["expected_gear"], "X4")
        for spec in NON_TECH_SCENARIOS.values():
            self.assertTrue(Path(spec["path"]).exists())

    def test_summary_path_uses_bmadx_suffix(self) -> None:
        self.assertEqual(
            summary_path_for("2026-05-05", "gpt-5-5", "healthy").name,
            "summary-2026-05-05-gpt-5-5-healthy-bmadx.json",
        )

    def test_write_config_uses_model_and_reasoning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            write_config(codex_home, "gpt-5.5", "medium")
            config = codex_home.joinpath("config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "gpt-5.5"', config)
            self.assertIn('model_reasoning_effort = "medium"', config)

    def test_codex_command_is_isolated_and_model_explicit(self) -> None:
        command = build_codex_command(
            "prompt",
            Path("/tmp/workdir"),
            Path("/tmp/codex-home"),
            model="gpt-5.5",
            reasoning="medium",
        )
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--disable", command)
        self.assertIn("plugins", command)
        self.assertIn("apps", command)
        self.assertIn("general_analytics", command)
        self.assertIn("-m", command)
        self.assertIn("gpt-5.5", command)
        self.assertIn('model_reasoning_effort="medium"', command)
        self.assertIn("--add-dir", command)
        self.assertIn("/tmp/codex-home", command)
        self.assertIn("workspace-write", command)

    def test_copy_runtime_files_does_not_copy_global_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            copy_runtime_files(codex_home)
            self.assertFalse(codex_home.joinpath(".codex-global-state.json").exists())

    def test_healthy_profile_uses_local_release_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fixture = write_healthy_bmad_fixture(root)
            env = benchmark_env(root / "codex-home", "healthy", fixture)
            self.assertEqual(env["BMAD_RELEASE_API"], fixture.resolve().as_uri())

    def test_parse_json_report_rejects_invalid_json(self) -> None:
        with self.assertRaises(RuntimeError):
            parse_json_report("not json")

    def test_warmup_healthy_profile_requires_ok_json(self) -> None:
        validate_warmup_payload(
            "healthy",
            {"action": "ok", "bmad_dependency": {"healthy": True}},
        )
        with self.assertRaises(RuntimeError):
            validate_warmup_payload(
                "healthy",
                {"action": "warning", "bmad_dependency": {"healthy": True}},
            )

    def test_warmup_degraded_profile_rejects_ok_healthy_json(self) -> None:
        with self.assertRaises(RuntimeError):
            validate_warmup_payload(
                "degraded",
                {"action": "ok", "bmad_dependency": {"healthy": True}},
            )
        validate_warmup_payload(
            "degraded",
            {"action": "warning", "bmad_dependency": {"healthy": False}},
        )

    def test_summary_records_model_and_reasoning(self) -> None:
        summary = build_summary(
            "2026-04-24",
            "healthy",
            [
                {
                    "tokens": 100,
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": True,
                    "reference_budget_pass": True,
                    "routing_pass": True,
                    "overreach_pass": True,
                }
            ],
            [],
            [],
            model="gpt-5.5",
            reasoning="medium",
        )
        self.assertEqual(summary["runner"]["model"], "gpt-5.5")
        self.assertEqual(summary["runner"]["reasoning"], "medium")
        self.assertEqual(summary["validation_summary"]["core"]["token_count_present_count"], 1)
        self.assertEqual(summary["validation_summary"]["core"]["overreach_pass_count"], 1)
        self.assertEqual(summary["validation_failures"]["core"], [])
        self.assertEqual(summary["validation_summary"]["non_technical"]["case_count"], 0)
        self.assertEqual(summary["non_technical_readout"]["what_failed_why_it_matters"], [])

    def test_validate_case_catches_gpt55_overreach(self) -> None:
        validation = validate_case(
            "Choice: `X2`, but maybe X4 if it gets messy.\n",
            "",
            1000,
            {"expected_gear": "X2", "forbidden_gears": ["X3", "X4"], "allow_reference_reads": False},
        )
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["overreach_pass"])

    def test_validation_failures_names_failed_checks(self) -> None:
        failures = validation_failures(
            [
                {
                    "case": "bmadx-healthy-x1",
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": False,
                    "reference_budget_pass": True,
                    "routing_pass": False,
                    "overreach_pass": True,
                }
            ]
        )
        self.assertEqual(
            failures,
            [
                {
                    "case": "bmadx-healthy-x1",
                    "failed_checks": ["token_pass", "routing_pass"],
                }
            ],
        )

    def test_non_technical_failure_explanations_are_plain_language(self) -> None:
        explanations = explain_failures_for_non_technical_users(
            [
                {
                    "case": "bmadx-healthy-google-login",
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": True,
                    "reference_budget_pass": True,
                    "routing_pass": False,
                    "overreach_pass": True,
                }
            ]
        )
        self.assertEqual(explanations[0]["case"], "bmadx-healthy-google-login")
        self.assertEqual(explanations[0]["what_failed"], ["routing_pass"])
        self.assertIn("wrong work mode", explanations[0]["why_it_matters"][0])


if __name__ == "__main__":
    unittest.main()
