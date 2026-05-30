"""Scenario specs for the BMADX benchmark runner."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = REPO_ROOT / "benchmark" / "scenarios"

CORE_SCENARIOS = {
    "x1": {
        "path": SCENARIO_ROOT / "scenario-x1.txt",
        "expected_gear": "X1",
        "expected_reasoning_effort": "low",
        "forbidden_gears": ["X3", "X4"],
        "max_lines": 5,
        "max_chars": 650,
        "max_tokens": 9000,
        "allow_reference_reads": False,
    },
    "x2": {
        "path": SCENARIO_ROOT / "scenario-x2.txt",
        "expected_gear": "X2",
        "expected_reasoning_effort": "medium",
        "forbidden_gears": ["X3", "X4"],
        "max_lines": 12,
        "max_chars": 1000,
        "max_tokens": 10000,
        "allow_reference_reads": False,
    },
    "x3": {
        "path": SCENARIO_ROOT / "scenario-x3.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "forbidden_gears": ["X4"],
        "allow_reference_reads": True,
    },
    "x4": {
        "path": SCENARIO_ROOT / "scenario-x4.txt",
        "expected_gear": "X4",
        "expected_reasoning_effort": "xhigh",
        "allow_reference_reads": True,
    },
}

BOUNDARY_SCENARIOS = {
    "x2x3-boundary": {
        "path": SCENARIO_ROOT / "scenario-x2x3-boundary.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "allow_reference_reads": True,
    }
}

NON_TECH_SCENARIOS = {
    "pricing-copy": {
        "path": SCENARIO_ROOT / "scenario-nontech-pricing-copy.txt",
        "expected_gear": "X1",
        "expected_reasoning_effort": "low",
        "forbidden_gears": ["X3", "X4"],
        "max_lines": 5,
        "max_chars": 650,
        "max_tokens": 9000,
        "allow_reference_reads": False,
    },
    "onboarding-email": {
        "path": SCENARIO_ROOT / "scenario-nontech-onboarding-email.txt",
        "expected_gear": "X2",
        "expected_reasoning_effort": "medium",
        "forbidden_gears": ["X3", "X4"],
        "max_lines": 12,
        "max_chars": 1000,
        "max_tokens": 10000,
        "allow_reference_reads": False,
    },
    "google-login": {
        "path": SCENARIO_ROOT / "scenario-nontech-google-login.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "forbidden_gears": ["X4"],
        "allow_reference_reads": True,
    },
    "subscription-billing": {
        "path": SCENARIO_ROOT / "scenario-nontech-subscription-billing.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "forbidden_gears": ["X4"],
        "allow_reference_reads": True,
    },
    "delete-inactive-users": {
        "path": SCENARIO_ROOT / "scenario-nontech-delete-inactive-users.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "forbidden_gears": ["X4"],
        "allow_reference_reads": True,
    },
    "messy-migration-incident": {
        "path": SCENARIO_ROOT / "scenario-nontech-messy-migration-incident.txt",
        "expected_gear": "X4",
        "expected_reasoning_effort": "xhigh",
        "allow_reference_reads": True,
    },
}

HANDOFF_SCENARIOS = {
    "x3-auth-review-handoff": {
        "path": SCENARIO_ROOT / "scenario-handoff-x3-auth-review.txt",
        "expected_gear": "X3",
        "expected_reasoning_effort": "high",
        "expected_handoff": True,
        "forbidden_gears": ["X4"],
        "allow_reference_reads": True,
    },
    "x4-migration-review-handoff": {
        "path": SCENARIO_ROOT / "scenario-handoff-x4-migration-review.txt",
        "expected_gear": "X4",
        "expected_reasoning_effort": "xhigh",
        "expected_handoff": True,
        "allow_reference_reads": True,
    },
}
