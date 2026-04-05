#!/usr/bin/env python3
"""Unit tests for benchmark validation helpers."""

from __future__ import annotations

import unittest

from run_bmadx_benchmark import detect_reference_reads, parse_token_count, validate_case


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
        stdout = "Wybór: `X1 — One-shot`.\nUzasadnienie: ...\nNastępny krok: ...\n"
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


if __name__ == "__main__":
    unittest.main()
