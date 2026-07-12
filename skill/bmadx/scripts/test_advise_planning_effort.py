#!/usr/bin/env python3
"""Tests for the criteria-based BMADX planning-effort advisor."""

from __future__ import annotations

import unittest

from advise_planning_effort import build_report, desired_effort, format_line, normalize_signals


PROFILES = {
    "gpt-5.5": {"supported_reasoning": ["low", "medium", "high", "xhigh"]},
    "gpt-5.6-sol": {
        "supported_reasoning": ["low", "medium", "high", "xhigh", "max", "ultra"]
    },
    "gpt-5.6-luna": {
        "supported_reasoning": ["low", "medium", "high", "xhigh", "max"]
    },
}


class PlanningEffortAdvisorTests(unittest.TestCase):
    def test_thresholds(self) -> None:
        self.assertEqual(desired_effort([]), "high")
        self.assertEqual(desired_effort(list(PROFILE_SIGNALS)[:2]), "xhigh")
        self.assertEqual(desired_effort(list(PROFILE_SIGNALS)[:4]), "max")

    def test_ultra_requires_six_signals_and_broad_decomposition(self) -> None:
        signals = list(normalize_signals([",".join(list(PROFILE_SIGNALS)[:6])]))
        self.assertEqual(desired_effort(signals), "max")
        signals[-1] = "broad_decomposition_pressure"
        self.assertEqual(desired_effort(signals), "ultra")

    def test_sol_can_recommend_ultra(self) -> None:
        signals = list(PROFILE_SIGNALS)
        report = build_report("gpt-5.6-sol", signals, PROFILES)
        self.assertEqual(report["recommended_effort"], "ultra")
        self.assertTrue(report["operator_confirmation_required"])

    def test_luna_caps_ultra_to_max(self) -> None:
        report = build_report("gpt-5.6-luna", list(PROFILE_SIGNALS), PROFILES)
        self.assertEqual(report["desired_effort"], "ultra")
        self.assertEqual(report["recommended_effort"], "max")
        self.assertTrue(report["capped_by_model"])

    def test_gpt55_caps_max_to_xhigh(self) -> None:
        signals = list(PROFILE_SIGNALS)[:5]
        report = build_report("gpt-5.5", signals, PROFILES)
        self.assertEqual(report["desired_effort"], "max")
        self.assertEqual(report["recommended_effort"], "xhigh")

    def test_normalization_deduplicates_and_rejects_unknown_signals(self) -> None:
        self.assertEqual(
            normalize_signals(["cross-system-scope,cross_system_scope"]),
            ["cross_system_scope"],
        )
        with self.assertRaises(ValueError):
            normalize_signals(["unknown"])

    def test_display_line_reports_y_of_x(self) -> None:
        report = build_report("gpt-5.6-sol", list(PROFILE_SIGNALS)[:3], PROFILES)
        line = format_line(report)
        self.assertIn("Planning effort: xhigh", line)
        self.assertIn("3/8 signals", line)

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_report("unknown", [], PROFILES)


PROFILE_SIGNALS = (
    "red_zone_or_irreversible",
    "cross_system_scope",
    "ambiguous_ownership_or_requirements",
    "long_horizon_or_compaction",
    "repeated_failure_or_incident",
    "rollback_or_recovery_complexity",
    "weak_or_expensive_verification",
    "broad_decomposition_pressure",
)


if __name__ == "__main__":
    unittest.main()
