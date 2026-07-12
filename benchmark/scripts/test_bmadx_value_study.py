#!/usr/bin/env python3
"""Deterministic tests for the blinded BMADX decision-value study."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analyze_bmadx_value_study import analyze
from bmadx_value_contract import (
    REVIEW_DIMENSIONS,
    build_value_prompt,
    candidate_id,
    validate_value_payload,
)
from build_bmadx_value_review_packet import build_packet, json_sha
from run_bmadx_value_study import (
    DEFAULT_PROTOCOL,
    build_schedule,
    load_protocol,
    load_resume,
    scenario_path,
    task_from_path,
    validate_protocol,
)


BLINDING_KEY = bytes.fromhex("11" * 32)


def response_payload(nonce: str) -> dict:
    return {
        "activation_nonce": nonce,
        "process": "bounded",
        "risk": "moderate",
        "handoff": False,
        "goal": False,
        "goal_stop": None,
        "loop": False,
        "loop_max_passes": None,
        "loop_stop": None,
        "recommended_actions": [
            "Inspect the existing pattern",
            "Make the bounded change",
        ],
        "verification": ["Run focused tests"],
        "safeguards": ["Review the resulting diff"],
        "operator_questions": [],
        "reasons": ["The task is limited and reversible"],
    }


def synthetic_summary(protocol: dict) -> dict:
    cases = []
    for item in build_schedule(protocol):
        token_by_arm = {"placebo": 100, "bmadx_stub": 105, "bmadx_real": 110}
        duration_by_arm = {"placebo": 10.0, "bmadx_stub": 10.5, "bmadx_real": 11.0}
        cases.append(
            {
                "case_id": f"case-{item['order']:03d}-{item['arm']}",
                **item,
                "tokens": token_by_arm[item["arm"]],
                "duration_seconds": duration_by_arm[item["arm"]],
                "response_payload": response_payload(item["nonce"]),
                "activation_pass": True,
                "cross_arm_nonce": False,
                "protected_filesystem_mutation": False,
                "framework_leakage_detected": False,
                "response_contract_pass": True,
            }
        )
    return {
        "complete": True,
        "protocol_id": protocol["protocol_id"],
        "expected_call_count": len(cases),
        "completed_call_count": len(cases),
        "cases": cases,
    }


def synthetic_reviews(protocol: dict, summary: dict, packet: dict) -> list[dict]:
    case_by_candidate = {}
    for case in summary["cases"]:
        block_id = f"{case['scenario']}-r{case['repeat_index']}"
        case_by_candidate[candidate_id(BLINDING_KEY, block_id, case["case_id"])] = case
    reviews = []
    for reviewer_index in range(3):
        blocks = []
        for block in packet["blocks"]:
            candidate_reviews = []
            preferred = []
            for candidate in block["candidates"]:
                arm = case_by_candidate[candidate["candidate_id"]]["arm"]
                score = {"placebo": 4, "bmadx_stub": 5, "bmadx_real": 6}[arm]
                ceremony = {"placebo": 2, "bmadx_stub": 2, "bmadx_real": 2}[arm]
                candidate_reviews.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        **{
                            dimension: ceremony
                            if dimension == "ceremony_burden"
                            else score
                            for dimension in REVIEW_DIMENSIONS
                        },
                        "safety_omission": False,
                        "fatal_flaw": False,
                        "notes": "",
                    }
                )
                if arm == "bmadx_real":
                    preferred.append(candidate["candidate_id"])
            blocks.append(
                {
                    "block_id": block["block_id"],
                    "candidate_reviews": candidate_reviews,
                    "preferred_candidate_ids": preferred,
                }
            )
        reviews.append(
            {
                "schema": "bmadx_value_review.v1",
                "protocol_id": protocol["protocol_id"],
                "packet_sha256": json_sha(packet),
                "reviewer_id": f"reviewer-{reviewer_index + 1}",
                "independent_of_bmadx_authorship": reviewer_index < 2,
                "mapping_was_not_available": True,
                "blocks": blocks,
            }
        )
    return reviews


class BmadxValueStudyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protocol = load_protocol(DEFAULT_PROTOCOL)

    def test_prompt_is_neutral_and_nonce_is_not_exposed(self) -> None:
        prompt = build_value_prompt("Fix the task.", "wf-1234567890")
        self.assertIn("$wf-1234567890", prompt)
        self.assertNotIn("bmadx", prompt.lower())
        self.assertNotIn("BMAD", prompt)
        self.assertNotIn("X1", prompt)
        self.assertNotIn("deadbeef", prompt)

    def test_response_contract_accepts_bounded_shape(self) -> None:
        payload = response_payload("a" * 32)
        result = validate_value_payload(payload, "a" * 32)
        self.assertTrue(result["activation_pass"])
        self.assertTrue(result["response_contract_pass"])

    def test_response_contract_keeps_quality_separate_from_activation(self) -> None:
        payload = response_payload("a" * 32)
        payload["verification"] = []
        result = validate_value_payload(payload, "a" * 32)
        self.assertTrue(result["activation_pass"])
        self.assertFalse(result["response_contract_pass"])

    def test_schedule_is_complete_deterministic_and_unique(self) -> None:
        first = build_schedule(self.protocol)
        second = build_schedule(self.protocol)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 162)
        self.assertEqual(len({item["alias"] for item in first}), 162)
        self.assertEqual(len({item["nonce"] for item in first}), 162)
        cells = {
            (item["scenario"], item["repeat_index"], item["arm"]) for item in first
        }
        self.assertEqual(len(cells), 162)

    def test_scenarios_do_not_prompt_for_framework_shaped_answers(self) -> None:
        for entry in self.protocol["scenarios"]:
            task = task_from_path(scenario_path(entry))
            self.assertNotIn("BMAD", task)
            self.assertNotIn("Explain the workflow", task)
            self.assertNotIn("bounded loop", task)

    def test_protocol_validates_against_frozen_sources(self) -> None:
        completed = type("Completed", (), {"returncode": 0})()
        with patch("run_bmadx_value_study.subprocess.run", return_value=completed):
            schedule = validate_protocol(self.protocol, DEFAULT_PROTOCOL)
        self.assertEqual(len(schedule), 162)

    def test_live_protocol_validation_requires_independent_scenario_audit(self) -> None:
        completed = type("Completed", (), {"returncode": 0})()
        with patch("run_bmadx_value_study.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "scenario audit"):
                validate_protocol(self.protocol, DEFAULT_PROTOCOL, require_audit=True)

    def test_resume_preserves_full_previous_summary(self) -> None:
        previous = {
            "protocol_sha256": "abc",
            "runtime_provenance": {"git_sha": "deadbeef"},
            "status": "failed",
            "complete": False,
            "cases": [{"case_id": "case-1"}],
            "run_segments": [{"completed_after": 1}],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "summary.json"
            path.write_text(json.dumps(previous), encoding="utf-8")
            loaded = load_resume(path, "abc", {"git_sha": "deadbeef"})
        self.assertEqual(loaded, previous)

    def test_review_packet_hides_arms_cases_aliases_and_nonces(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, template = build_packet(self.protocol, summary, BLINDING_KEY)
        encoded = json.dumps(packet)
        self.assertNotIn('"arm"', encoded)
        self.assertNotIn('"case_id"', encoded)
        self.assertNotIn('"activation_nonce"', encoded)
        self.assertNotIn('"alias"', encoded)
        self.assertEqual(len(packet["blocks"]), 54)
        self.assertEqual(len(template["blocks"]), 54)

    def test_candidate_mapping_cannot_be_rebuilt_with_the_wrong_key(self) -> None:
        expected = candidate_id(BLINDING_KEY, "scenario-r1", "case-1")
        wrong = candidate_id(bytes.fromhex("22" * 32), "scenario-r1", "case-1")
        self.assertNotEqual(expected, wrong)

    def test_review_packet_redacts_and_retains_framework_leakage(self) -> None:
        summary = synthetic_summary(self.protocol)
        summary["cases"][0]["framework_leakage_detected"] = True
        summary["cases"][0]["response_payload"]["reasons"] = ["Use BMADX X3"]
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        encoded = json.dumps(packet)
        self.assertNotIn("BMADX", encoded)
        self.assertNotIn("X3", encoded)
        self.assertIn('"blindability_failure": true', encoded)

    def test_analysis_reports_positive_value_only_when_tradeoffs_pass(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        result = analyze(self.protocol, summary, packet, reviews, BLINDING_KEY)
        self.assertEqual(result["verdict"], "positive_value_added")
        self.assertTrue(all(result["positive_gates"].values()))
        self.assertEqual(
            result["comparisons"]["bmadx_real_vs_placebo"]["net_blinded_preference"],
            1.0,
        )

    def test_analysis_blocks_positive_verdict_on_excessive_token_cost(self) -> None:
        summary = synthetic_summary(self.protocol)
        for case in summary["cases"]:
            if case["arm"] == "bmadx_real":
                case["tokens"] = 200
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        result = analyze(self.protocol, summary, packet, reviews, BLINDING_KEY)
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["positive_gates"]["token_overhead_acceptable"])

    def test_analysis_requires_blind_mapping_attestation(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        reviews[0]["mapping_was_not_available"] = False
        with self.assertRaisesRegex(ValueError, "mapping"):
            analyze(self.protocol, summary, packet, reviews, BLINDING_KEY)

    def test_analysis_rejects_wrong_blinding_key(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        with self.assertRaisesRegex(ValueError, "Blinding key"):
            analyze(
                self.protocol,
                summary,
                packet,
                reviews,
                bytes.fromhex("22" * 32),
            )


if __name__ == "__main__":
    unittest.main()
