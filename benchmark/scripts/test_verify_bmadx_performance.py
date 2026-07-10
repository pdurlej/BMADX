#!/usr/bin/env python3
"""Unit tests for BMADX performance verifier."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from verify_bmadx_performance import build_report, parse_args


def passing_case(name: str, gear: str, tokens: int = 1000, duration: float = 1.0) -> dict:
    return {
        "case": name,
        "tokens": tokens,
        "duration_seconds": duration,
        "expected_gear": gear,
        "format_pass": True,
        "token_count_present": True,
        "token_pass": True,
        "reference_budget_pass": True,
        "routing_pass": True,
        "overreach_pass": True,
        "thinking_budget_present": True,
        "thinking_budget_pass": True,
        "thinking_budget_no_mutation_pass": True,
        "thinking_budget_supported_value_pass": True,
        "goal_stop_condition_pass": True,
        "handoff_routing_pass": True,
        "handoff_not_runtime_pass": True,
        "no_worker_lane_pass": True,
        "no_model_name_pass": True,
        "no_dispatch_command_pass": True,
        "no_platform_surface_pass": True,
    }


def summary(
    policy: str,
    profile: str = "healthy",
    *,
    model: str = "gpt-5.5",
    total_tokens: int = 1000,
    avg_duration: float = 1.0,
) -> dict:
    return {
        "generated_at": "2026-06-02",
        "profile": profile,
        "runner": {
            "model": model,
            "reasoning_policy": policy,
            "gate_mode": "precomputed",
            "group_slug": "all",
            "repeat": 2,
        },
        "cases": [passing_case(f"{profile}-{policy}-x1", "X1", total_tokens, avg_duration)],
        "boundary_cases": [],
        "non_technical_cases": [],
        "handoff_cases": [],
        "performance_summary": {
            "all": {
                "total_tokens": total_tokens,
                "avg_tokens": total_tokens,
                "avg_duration_seconds": avg_duration,
                "p95_duration_seconds": avg_duration,
                "max_duration_seconds": avg_duration,
            }
        },
        "validation_failures": {
            "core": [],
            "boundary": [],
            "non_technical": [],
            "handoff": [],
        },
    }


def write_summary(root: Path, name: str, payload: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class VerifyBmadxPerformanceTests(unittest.TestCase):
    def test_baseline_passes_for_required_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = [
                write_summary(root, "healthy-fixed.json", summary("fixed", "healthy")),
                write_summary(root, "healthy-advisor.json", summary("advisor", "healthy", total_tokens=900)),
                write_summary(root, "degraded-fixed.json", summary("fixed", "degraded")),
                write_summary(root, "degraded-advisor.json", summary("advisor", "degraded", total_tokens=900)),
            ]
            args = parse_args(
                [
                    *map(str, paths),
                    "--require-profiles",
                    "healthy,degraded",
                    "--require-policies",
                    "fixed,advisor",
                    "--require-gate-mode",
                    "precomputed",
                    "--require-group-slug",
                    "all",
                    "--min-repeat",
                    "2",
                ]
            )
            report = build_report(args)
            self.assertTrue(report["baseline_pass"])

    def test_baseline_fails_on_wrong_gate_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = summary("fixed")
            payload["runner"]["gate_mode"] = "in-session"
            path = write_summary(root, "fixed.json", payload)
            report = build_report(parse_args([str(path), "--require-gate-mode", "precomputed"]))
            self.assertFalse(report["baseline_pass"])
            self.assertTrue(any("gate_mode 'in-session'" in failure for failure in report["baseline_failures"]))

    def test_baseline_warns_on_x1_token_cap_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = summary("fixed", total_tokens=12000)
            payload["cases"][0]["token_pass"] = False
            path = write_summary(root, "fixed.json", payload)
            report = build_report(parse_args([str(path)]))
            self.assertTrue(report["baseline_pass"])
            self.assertTrue(any("tokens 12000 exceed cap 9000" in warning for warning in report["token_cap_warnings"]))

    def test_baseline_can_fail_on_x1_token_cap_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = summary("fixed", total_tokens=12000)
            payload["cases"][0]["token_pass"] = False
            path = write_summary(root, "fixed.json", payload)
            report = build_report(parse_args([str(path), "--token-cap-mode", "strict"]))
            self.assertFalse(report["baseline_pass"])
            self.assertTrue(any("tokens 12000 exceed cap 9000" in failure for failure in report["baseline_failures"]))

    def test_claim_fails_when_advisor_is_slower_or_more_expensive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fixed = write_summary(root, "fixed.json", summary("fixed", total_tokens=1000, avg_duration=1.0))
            advisor = write_summary(root, "advisor.json", summary("advisor", total_tokens=1100, avg_duration=2.0))
            report = build_report(parse_args([str(fixed), str(advisor), "--mode", "claim"]))
            self.assertTrue(report["baseline_pass"])
            self.assertFalse(report["claim_pass"])
            self.assertTrue(any("advisor total_tokens" in failure for failure in report["claim_failures"]))
            self.assertTrue(any("advisor avg_duration_seconds" in failure for failure in report["claim_failures"]))

    def test_claim_passes_when_advisor_holds_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fixed = write_summary(root, "fixed.json", summary("fixed", total_tokens=1000, avg_duration=2.0))
            advisor = write_summary(root, "advisor.json", summary("advisor", total_tokens=900, avg_duration=1.0))
            report = build_report(parse_args([str(fixed), str(advisor), "--mode", "claim"]))
            self.assertTrue(report["baseline_pass"])
            self.assertTrue(report["claim_pass"])

    def test_claim_never_pairs_different_models(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fixed = write_summary(
                root,
                "sol-fixed.json",
                summary("fixed", model="gpt-5.6-sol"),
            )
            advisor = write_summary(
                root,
                "terra-advisor.json",
                summary("advisor", model="gpt-5.6-terra", total_tokens=900),
            )
            report = build_report(parse_args([str(fixed), str(advisor), "--mode", "claim"]))
            self.assertFalse(report["claim_pass"])
            self.assertEqual(report["models"], ["gpt-5.6-sol", "gpt-5.6-terra"])
            self.assertTrue(any("missing fixed/advisor pair" in failure for failure in report["claim_failures"]))

    def test_claim_handles_missing_model_metadata_without_sort_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing = summary("fixed")
            del missing["runner"]["model"]
            fixed = write_summary(root, "missing-fixed.json", missing)
            advisor = write_summary(root, "sol-advisor.json", summary("advisor", model="gpt-5.6-sol"))
            report = build_report(parse_args([str(fixed), str(advisor), "--mode", "claim"]))
            self.assertFalse(report["claim_pass"])
            self.assertIn("<missing-model>", report["models"])


if __name__ == "__main__":
    unittest.main()
