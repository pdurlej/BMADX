#!/usr/bin/env python3
"""Unit tests for benchmark validation helpers."""

from __future__ import annotations

import unittest

from pathlib import Path
import tempfile

from run_bmadx_benchmark import (
    DEFAULT_MODEL,
    DEFAULT_REASONING,
    build_summary,
    detect_reference_reads,
    model_slug,
    parse_args,
    parse_token_count,
    write_config,
    validate_case,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_parse_token_count_handles_nbsp(self) -> None:
        stderr = "tokens used\n10\u00a0306\n"
        self.assertEqual(parse_token_count(stderr), 10306)

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

    def test_summary_records_model_and_reasoning(self) -> None:
        summary = build_summary(
            "2026-04-24",
            "healthy",
            [{"tokens": 100, "format_pass": True, "token_pass": True, "reference_budget_pass": True, "routing_pass": True, "overreach_pass": True}],
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
