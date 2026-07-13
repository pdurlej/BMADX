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
    REAL_BMAD_SKILL,
    build_schedule,
    load_protocol,
    load_resume,
    scenario_path,
    task_from_path,
    validate_protocol,
)
from run_sol_bmadx_ab import tree_sha256
from run_bmadx_synthetic_review_panel import (
    DEFAULT_PANEL,
    DEFAULT_REVIEW_AMENDMENT,
    build_panel_schedule,
    command_for_call,
    normalize_judgment_keys,
    normalize_candidate_ids,
    ordered_block,
    parse_runtime_output,
    validate_judgment,
    validate_review_amendment,
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
    reviewers = [
        ("minimax-m3", "minimax", "ollama/minimax-m3:cloud"),
        ("deepseek-v4-pro", "deepseek", "ollama/deepseek-v4-pro:cloud"),
        ("qwen-35", "qwen", "ollama/qwen3.5:cloud"),
        ("glm-52", "glm", "ollama/glm-5.2:cloud"),
        ("kimi-k27-code", "kimi", "ollama/kimi-k2.7-code:cloud"),
    ]
    panel_sha = protocol["review_policy"]["synthetic_panel"]["sha256"]
    for reviewer_id, family, model_id in reviewers:
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
                "reviewer_id": reviewer_id,
                "reviewer_kind": "synthetic_model",
                "model_family": family,
                "model_id": model_id,
                "runtime": "pi",
                "runtime_version": "0.78.0",
                "panel_protocol_sha256": panel_sha,
                "independent_of_bmadx_authorship": True,
                "mapping_was_not_available": True,
                "blocks": blocks,
            }
        )
    return reviews


def synthetic_panel_summary(protocol: dict, packet: dict, reviews: list[dict]) -> dict:
    return {
        "schema": "bmadx_synthetic_panel_summary.v1",
        "protocol_id": protocol["protocol_id"],
        "packet_sha256": json_sha(packet),
        "panel_protocol_sha256": protocol["review_policy"]["synthetic_panel"][
            "sha256"
        ],
        "complete": True,
        "healthy": True,
        "expected_call_count": 325,
        "completed_call_count": 325,
        "runtime_versions": {"pi": "0.78.0"},
        "reviewers": [
            {
                "reviewer_id": review["reviewer_id"],
                "family": review["model_family"],
                "model_id": review["model_id"],
                "healthy": True,
                "primary_review_sha256": json_sha(review),
            }
            for review in reviews
        ],
    }


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
        actual_sha256_file = __import__(
            "run_bmadx_value_study"
        ).sha256_file

        def frozen_external_bmad_hash(path: Path, **kwargs: object) -> str:
            if Path(path).name == REAL_BMAD_SKILL:
                return self.protocol["source_hashes"]["real_bmad_tree_sha256"]
            return tree_sha256(path, **kwargs)

        def frozen_generation_harness_hash(path: Path) -> str:
            if Path(path).name == "run_bmadx_synthetic_review_panel.py":
                return self.protocol["harness_hashes"][
                    "synthetic_panel_runner_sha256"
                ]
            return actual_sha256_file(path)

        with patch(
            "run_bmadx_value_study.subprocess.run", return_value=completed
        ), patch(
            "run_bmadx_value_study.tree_sha256",
            side_effect=frozen_external_bmad_hash,
        ), patch(
            "run_bmadx_value_study.sha256_file",
            side_effect=frozen_generation_harness_hash,
        ):
            schedule = validate_protocol(self.protocol, DEFAULT_PROTOCOL)
        self.assertEqual(len(schedule), 162)

    def test_review_runner_amendment_binds_current_runner(self) -> None:
        amendment = json.loads(DEFAULT_REVIEW_AMENDMENT.read_text(encoding="utf-8"))
        validate_review_amendment(amendment, DEFAULT_PROTOCOL, DEFAULT_PANEL)

    def test_live_protocol_validation_requires_independent_scenario_audit(self) -> None:
        completed = type("Completed", (), {"returncode": 0})()
        pending_audit = {
            "schema": "bmadx_value_scenario_audit.v1",
            "scenario_manifest_sha256": self.protocol["scenario_manifest_sha256"],
            "status": "pending_independent_review",
        }
        with patch(
            "run_bmadx_value_study.subprocess.run", return_value=completed
        ), patch(
            "run_bmadx_value_study.load_scenario_audit", return_value=pending_audit
        ):
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

    def test_synthetic_panel_schedule_has_frozen_lane_counts(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        panel = json.loads(
            (DEFAULT_PROTOCOL.parent / "synthetic-panel-v1.json").read_text(
                encoding="utf-8"
            )
        )
        schedule = build_panel_schedule(panel, packet)
        self.assertEqual(len(schedule), 325)
        self.assertEqual(sum(call["lane"] == "primary" for call in schedule), 270)
        self.assertEqual(sum(call["lane"] == "stability" for call in schedule), 55)
        self.assertEqual(sum(call["runtime"] == "pi" for call in schedule), 325)

    def test_synthetic_panel_is_five_family_pi_ollama_only(self) -> None:
        panel = json.loads(
            (DEFAULT_PROTOCOL.parent / "synthetic-panel-v1.json").read_text(
                encoding="utf-8"
            )
        )
        reviewers = panel["reviewers"]
        self.assertEqual(len(reviewers), 5)
        self.assertEqual(len({reviewer["family"] for reviewer in reviewers}), 5)
        self.assertTrue(all(reviewer["runtime"] == "pi" for reviewer in reviewers))
        self.assertTrue(
            all(reviewer["model"].startswith("ollama/") for reviewer in reviewers)
        )
        self.assertNotIn("opencode", json.dumps(panel).lower())
        self.assertNotIn("antigravity", json.dumps(panel).lower())

    def test_stability_lane_changes_candidate_order(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        panel = json.loads(
            (DEFAULT_PROTOCOL.parent / "synthetic-panel-v1.json").read_text(
                encoding="utf-8"
            )
        )
        reviewer = panel["reviewers"][0]
        primary_call = {
            "lane": "primary",
            "reviewer": reviewer,
            "block_id": packet["blocks"][0]["block_id"],
        }
        stability_call = {**primary_call, "lane": "stability"}
        primary = ordered_block(panel, packet["blocks"][0], primary_call)
        stability = ordered_block(panel, packet["blocks"][0], stability_call)
        self.assertNotEqual(
            [candidate["candidate_id"] for candidate in primary["candidates"]],
            [candidate["candidate_id"] for candidate in stability["candidates"]],
        )

    def test_runtime_parser_uses_final_pi_assistant_message(self) -> None:
        payload = {"block_id": "b", "candidate_reviews": [], "preferred_candidate_ids": []}
        partial = {
            "type": "message_update",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "partial"}],
            },
        }
        final = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": json.dumps(payload)}],
            },
        }
        stdout = json.dumps(partial) + "\n" + json.dumps(final)
        self.assertEqual(parse_runtime_output(stdout), payload)

    def test_runtime_parser_accepts_single_json_fence(self) -> None:
        payload = {"block_id": "b", "candidate_reviews": [], "preferred_candidate_ids": []}
        final = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": f"```json\n{json.dumps(payload)}\n```"}
                ],
            },
        }
        self.assertEqual(parse_runtime_output(json.dumps(final)), payload)

    def test_runtime_parser_uses_complete_thinking_when_final_text_is_empty(self) -> None:
        payload = {"block_id": "b", "candidate_reviews": [], "preferred_candidate_ids": []}
        final = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "thinking",
                        "thinking": f"```json\n{json.dumps(payload)}\n```",
                    }
                ],
            },
        }
        self.assertEqual(parse_runtime_output(json.dumps(final)), payload)

    def test_runtime_parser_does_not_extract_json_from_mixed_thinking(self) -> None:
        payload = {"block_id": "b", "candidate_reviews": [], "preferred_candidate_ids": []}
        final = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "thinking",
                        "thinking": f"analysis first\n{json.dumps(payload)}",
                    }
                ],
            },
        }
        self.assertIsNone(parse_runtime_output(json.dumps(final)))

    def test_runtime_normalizes_one_unambiguous_numeric_dimension_key(self) -> None:
        judgment = {
            "candidate_reviews": [
                {
                    "candidate_id": "candidate-1",
                    **{
                        dimension: 6
                        for dimension in REVIEW_DIMENSIONS
                        if dimension != "actionability"
                    },
                    "actionality": 7,
                    "safety_omission": False,
                    "fatal_flaw": False,
                    "notes": "",
                }
            ]
        }
        normalizations = normalize_judgment_keys(judgment)
        self.assertEqual(judgment["candidate_reviews"][0]["actionability"], 7)
        self.assertNotIn("actionality", judgment["candidate_reviews"][0])
        self.assertEqual(normalizations[0]["target_key"], "actionability")

    def test_runtime_does_not_normalize_ambiguous_or_non_numeric_keys(self) -> None:
        judgment = {
            "candidate_reviews": [
                {
                    "candidate_id": "candidate-1",
                    "actionalty": "7",
                    "actonability": 6,
                }
            ]
        }
        self.assertEqual(normalize_judgment_keys(judgment), [])
        self.assertNotIn("actionability", judgment["candidate_reviews"][0])

    def test_runtime_normalizes_generic_rubric_suffix_alias(self) -> None:
        judgment = {
            "candidate_reviews": [
                {
                    "candidate_id": "candidate-1",
                    **{
                        dimension: 6
                        for dimension in REVIEW_DIMENSIONS
                        if dimension != "safeguard_coverage"
                    },
                    "safeguards": 7,
                    "safety_omission": False,
                    "fatal_flaw": False,
                    "notes": "",
                }
            ]
        }
        normalizations = normalize_judgment_keys(judgment)
        self.assertEqual(judgment["candidate_reviews"][0]["safeguard_coverage"], 7)
        self.assertEqual(normalizations[0]["source_stem"], "safeguard")
        self.assertEqual(normalizations[0]["target_stem"], "safeguard")

    def test_runtime_normalizes_one_unique_candidate_id_typo(self) -> None:
        block = {
            "candidates": [
                {"candidate_id": "candidate-3f4a9cba0481"},
                {"candidate_id": "candidate-bae827b74208"},
            ]
        }
        judgment = {
            "candidate_reviews": [
                {"candidate_id": "candidate-3f4c9cba0481"},
                {"candidate_id": "candidate-bae827b74208"},
            ],
            "preferred_candidate_ids": ["candidate-3f4c9cba0481"],
        }
        normalizations = normalize_candidate_ids(judgment, block)
        self.assertEqual(
            judgment["candidate_reviews"][0]["candidate_id"],
            "candidate-3f4a9cba0481",
        )
        self.assertEqual(
            judgment["preferred_candidate_ids"], ["candidate-3f4a9cba0481"]
        )
        self.assertEqual(normalizations[0]["edit_distance"], 1)

    def test_runtime_does_not_normalize_ambiguous_candidate_id(self) -> None:
        block = {
            "candidates": [
                {"candidate_id": "candidate-aaa1"},
                {"candidate_id": "candidate-aaa2"},
            ]
        }
        judgment = {
            "candidate_reviews": [{"candidate_id": "candidate-aaa3"}],
            "preferred_candidate_ids": ["candidate-aaa3"],
        }
        self.assertEqual(normalize_candidate_ids(judgment, block), [])
        self.assertEqual(
            judgment["candidate_reviews"][0]["candidate_id"], "candidate-aaa3"
        )

    def test_synthetic_runtime_command_is_isolated_pi_only(self) -> None:
        panel = json.loads(
            (DEFAULT_PROTOCOL.parent / "synthetic-panel-v1.json").read_text(
                encoding="utf-8"
            )
        )
        call = {"reviewer": panel["reviewers"][0], "runtime": "pi"}
        command, _ = command_for_call(call, "judge this")
        self.assertEqual(command[0], "pi")
        self.assertIn("--no-tools", command)
        self.assertIn("--no-extensions", command)
        self.assertIn("--no-skills", command)
        self.assertIn("--no-context-files", command)
        self.assertNotIn("opencode", command)

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
        panel = synthetic_panel_summary(self.protocol, packet, reviews)
        result = analyze(
            self.protocol, summary, packet, reviews, BLINDING_KEY, panel
        )
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
        panel = synthetic_panel_summary(self.protocol, packet, reviews)
        result = analyze(
            self.protocol, summary, packet, reviews, BLINDING_KEY, panel
        )
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["positive_gates"]["token_overhead_acceptable"])

    def test_analysis_requires_blind_mapping_attestation(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        reviews[0]["mapping_was_not_available"] = False
        panel = synthetic_panel_summary(self.protocol, packet, reviews)
        with self.assertRaisesRegex(ValueError, "mapping"):
            analyze(self.protocol, summary, packet, reviews, BLINDING_KEY, panel)

    def test_analysis_rejects_wrong_blinding_key(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        panel = synthetic_panel_summary(self.protocol, packet, reviews)
        with self.assertRaisesRegex(ValueError, "Blinding key"):
            analyze(
                self.protocol,
                summary,
                packet,
                reviews,
                bytes.fromhex("22" * 32),
                panel,
            )

    def test_analysis_rejects_unhealthy_synthetic_panel(self) -> None:
        summary = synthetic_summary(self.protocol)
        packet, _ = build_packet(self.protocol, summary, BLINDING_KEY)
        reviews = synthetic_reviews(self.protocol, summary, packet)
        panel = synthetic_panel_summary(self.protocol, packet, reviews)
        panel["healthy"] = False
        with self.assertRaisesRegex(ValueError, "unhealthy"):
            analyze(self.protocol, summary, packet, reviews, BLINDING_KEY, panel)


if __name__ == "__main__":
    unittest.main()
