#!/usr/bin/env python3
"""Unit tests for benchmark validation helpers."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from run_bmadx_benchmark import (
    DEFAULT_MODEL,
    DEFAULT_REASONING,
    benchmark_env,
    build_codex_command,
    build_prompt,
    build_summary,
    copy_runtime_files,
    detect_reference_reads,
    model_slug,
    parse_args,
    parse_token_count,
    sanitize_stderr,
    validate_case,
    write_healthy_bmad_fixture,
    write_config,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_parse_token_count_handles_nbsp(self) -> None:
        stderr = "tokens used\n10\u00a0306\n"
        self.assertEqual(parse_token_count(stderr), 10306)

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
        self.assertTrue(validation["token_pass"])
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["reference_budget_pass"])
        self.assertEqual(validation["reference_reads"], ["gearbox.md"])
        self.assertTrue(validation["overreach_pass"])

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

    def test_summary_records_model_and_reasoning(self) -> None:
        summary = build_summary(
            "2026-04-24",
            "healthy",
            [
                {
                    "tokens": 100,
                    "format_pass": True,
                    "token_pass": True,
                    "reference_budget_pass": True,
                    "routing_pass": True,
                    "overreach_pass": True,
                }
            ],
            [],
            model="gpt-5.5",
            reasoning="medium",
        )
        self.assertEqual(summary["runner"]["model"], "gpt-5.5")
        self.assertEqual(summary["runner"]["reasoning"], "medium")
        self.assertEqual(summary["validation_summary"]["core"]["overreach_pass_count"], 1)

    def test_validate_case_catches_gpt55_overreach(self) -> None:
        validation = validate_case(
            "Choice: `X2`, but maybe X4 if it gets messy.\n",
            "",
            1000,
            {"expected_gear": "X2", "forbidden_gears": ["X3", "X4"], "allow_reference_reads": False},
        )
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["overreach_pass"])


if __name__ == "__main__":
    unittest.main()
