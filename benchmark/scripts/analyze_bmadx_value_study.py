#!/usr/bin/env python3
"""Analyze blinded BMADX value-study reviews and operational trade-offs."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from bmadx_value_contract import REVIEW_DIMENSIONS, candidate_id
from build_bmadx_value_arm_map import response_sha
from build_bmadx_value_review_packet import json_sha, read_blinding_key
from run_bmadx_value_study import load_protocol


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--review", type=Path, action="append", required=True)
    parser.add_argument("--panel-summary", type=Path)
    parser.add_argument("--review-amendment", type=Path)
    unblinding = parser.add_mutually_exclusive_group(required=True)
    unblinding.add_argument("--blinding-key-file", type=Path)
    unblinding.add_argument("--arm-map", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def bootstrap_cluster_ci(
    values: dict[str, list[float]], seed: int, samples: int
) -> list[float]:
    clusters = sorted(values)
    if not clusters:
        return [0.0, 0.0]
    cluster_means = {cluster: mean(values[cluster]) for cluster in clusters}
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        selected = [rng.choice(clusters) for _ in clusters]
        draws.append(mean([cluster_means[cluster] for cluster in selected]))
    draws.sort()
    lower = draws[int(0.025 * (samples - 1))]
    upper = draws[int(0.975 * (samples - 1))]
    return [round(lower, 6), round(upper, 6)]


def validate_inputs(
    protocol: dict[str, Any],
    summary: dict[str, Any],
    packet: dict[str, Any],
    reviews: list[dict[str, Any]],
    blinding_key: bytes | None,
    panel_summary: dict[str, Any] | None = None,
    arm_map: dict[str, Any] | None = None,
    review_amendment: dict[str, Any] | None = None,
    protocol_sha256: str | None = None,
    review_amendment_sha256: str | None = None,
) -> None:
    if summary.get("complete") is not True:
        raise ValueError("Analysis requires a complete integrity-healthy study")
    if packet.get("rubric_sha256") != (protocol.get("rubric") or {}).get("sha256"):
        raise ValueError("Review packet rubric hash mismatch")
    if (blinding_key is None) == (arm_map is None):
        raise ValueError("Provide exactly one unblinding mechanism")
    if blinding_key is not None and packet.get("blinding_key_sha256") != hashlib.sha256(
        blinding_key
    ).hexdigest():
        raise ValueError("Blinding key does not match the review packet")
    if arm_map is not None and (
        arm_map.get("schema") != "bmadx_value_arm_map.v1"
        or arm_map.get("complete") is not True
        or arm_map.get("protocol_id") != protocol.get("protocol_id")
        or arm_map.get("summary_sha256") != json_sha(summary)
        or arm_map.get("packet_sha256") != json_sha(packet)
    ):
        raise ValueError("Arm-map provenance mismatch")
    if not reviews or len(reviews) < int(
        protocol["review_policy"]["minimum_reviewers"]
    ):
        raise ValueError("Insufficient blinded reviewers")
    reviewer_ids = [review.get("reviewer_id") for review in reviews]
    if len(set(reviewer_ids)) != len(reviewer_ids):
        raise ValueError("Reviewer IDs must be unique")
    independent = sum(
        review.get("independent_of_bmadx_authorship") is True for review in reviews
    )
    if independent < int(protocol["review_policy"]["minimum_independent_reviewers"]):
        raise ValueError("Insufficient reviewers independent of BMADX authorship")
    if any(review.get("mapping_was_not_available") is not True for review in reviews):
        raise ValueError(
            "Every reviewer must attest that the arm mapping was unavailable"
        )
    packet_hash = json_sha(packet)
    review_policy = json.loads(json.dumps(protocol.get("review_policy") or {}))
    if review_amendment is not None:
        required_ids = review_amendment.get("required_reviewer_ids") or []
        retained = review_amendment.get("retained_prior_replacements") or []
        retained_by_source = {
            item.get("from_reviewer_id"): item
            for item in retained
            if isinstance(item, dict)
        }
        if (
            review_amendment.get("schema") != "bmadx_review_runner_amendment.v1"
            or review_amendment.get("amendment_id")
            != "resume-after-ollama-transport-outage-v1.13"
            or review_amendment.get("value_protocol_sha256") != protocol_sha256
            or review_amendment.get("restart_panel_from_zero") is not False
            or review_amendment.get("resume_stopped_checkpoint") is not True
            or review_amendment.get("changes_models_or_call_counts") is not False
            or review_amendment.get("changes_provider_attempt_count_policy")
            is not True
            or review_amendment.get("generation_outputs_unchanged") is not True
            or review_amendment.get(
                "normalizes_only_unique_distance_one_boolean_flag_keys"
            )
            is not True
            or retained_by_source.get("deepseek-v4-pro", {}).get("to_reviewer_id")
            != "mistral-large-3"
            or retained_by_source.get("minimax-m3", {}).get("to_reviewer_id")
            != "gemma-4-31b"
            or retained_by_source.get("kimi-k27-code", {}).get("to_reviewer_id")
            != "nemotron-3-ultra"
            or review_amendment.get(
                "maximum_provider_attempts_per_scientific_call"
            )
            != 4
            or review_amendment.get("maximum_schema_attempts_per_scientific_call")
            != 2
            or review_amendment.get("transport_failures_do_not_consume_schema_attempts")
            is not True
            or review_amendment.get("retries_only_without_valid_judgment") is not True
            or review_amendment.get("failed_attempts_remain_auditable") is not True
            or len(required_ids) != 5
            or len(set(required_ids)) != 5
        ):
            raise ValueError("Review-only amendment provenance mismatch")
        review_policy["required_reviewer_ids"] = required_ids
        review_policy.setdefault("synthetic_panel", {})["sha256"] = review_amendment[
            "panel_protocol_sha256"
        ]
    if review_policy.get("mode") == "synthetic_model_panel":
        required_ids = set(review_policy.get("required_reviewer_ids") or [])
        if set(reviewer_ids) != required_ids:
            raise ValueError("Synthetic panel does not contain the exact frozen reviewers")
        panel_ref = review_policy.get("synthetic_panel") or {}
        if panel_summary is None:
            raise ValueError("Synthetic panel summary is required")
        if (
            panel_summary.get("schema") != "bmadx_synthetic_panel_summary.v1"
            or panel_summary.get("complete") is not True
            or panel_summary.get("healthy") is not True
        ):
            raise ValueError("Synthetic panel is incomplete or unhealthy")
        if (
            panel_summary.get("protocol_id") != protocol.get("protocol_id")
            or panel_summary.get("packet_sha256") != packet_hash
            or panel_summary.get("panel_protocol_sha256") != panel_ref.get("sha256")
            or (
                review_amendment is not None
                and panel_summary.get("review_amendment_sha256")
                != review_amendment_sha256
            )
        ):
            raise ValueError("Synthetic panel provenance mismatch")
        panel_reviewers = {
            entry.get("reviewer_id"): entry
            for entry in panel_summary.get("reviewers") or []
        }
        if set(panel_reviewers) != required_ids:
            raise ValueError("Synthetic panel summary reviewer set mismatch")
        for review in reviews:
            reviewer_id = review["reviewer_id"]
            panel_entry = panel_reviewers[reviewer_id]
            if (
                review.get("reviewer_kind") != "synthetic_model"
                or review.get("model_family") != panel_entry.get("family")
                or review.get("model_id") != panel_entry.get("model_id")
                or review.get("panel_protocol_sha256") != panel_ref.get("sha256")
                or (
                    review_amendment is not None
                    and review.get("review_amendment_sha256")
                    != review_amendment_sha256
                )
                or panel_entry.get("healthy") is not True
                or panel_entry.get("primary_review_sha256") != json_sha(review)
            ):
                raise ValueError(f"Synthetic reviewer provenance mismatch: {reviewer_id}")
    block_candidates = {
        block["block_id"]: {
            candidate["candidate_id"] for candidate in block["candidates"]
        }
        for block in packet["blocks"]
    }
    for review in reviews:
        if review.get("packet_sha256") != packet_hash:
            raise ValueError("Review packet hash mismatch")
        reviewed_blocks = {
            block["block_id"]: block for block in review.get("blocks") or []
        }
        if set(reviewed_blocks) != set(block_candidates):
            raise ValueError("Review does not cover the exact packet block set")
        for block_id, expected_candidates in block_candidates.items():
            block = reviewed_blocks[block_id]
            candidate_reviews = block.get("candidate_reviews") or []
            if {
                entry.get("candidate_id") for entry in candidate_reviews
            } != expected_candidates:
                raise ValueError(f"Review candidate set mismatch: {block_id}")
            preferred = block.get("preferred_candidate_ids") or []
            if not preferred or not set(preferred).issubset(expected_candidates):
                raise ValueError(f"Invalid preferred candidate set: {block_id}")
            for entry in candidate_reviews:
                if any(
                    not isinstance(entry.get(dimension), int)
                    or isinstance(entry.get(dimension), bool)
                    or not 1 <= entry[dimension] <= 7
                    for dimension in REVIEW_DIMENSIONS
                ):
                    raise ValueError(f"Invalid review dimension score: {block_id}")
                if not isinstance(entry.get("safety_omission"), bool) or not isinstance(
                    entry.get("fatal_flaw"), bool
                ):
                    raise ValueError(f"Invalid binary review field: {block_id}")


def analyze(
    protocol: dict[str, Any],
    summary: dict[str, Any],
    packet: dict[str, Any],
    reviews: list[dict[str, Any]],
    blinding_key: bytes | None,
    panel_summary: dict[str, Any] | None = None,
    arm_map: dict[str, Any] | None = None,
    review_amendment: dict[str, Any] | None = None,
    protocol_sha256: str | None = None,
    review_amendment_sha256: str | None = None,
) -> dict[str, Any]:
    validate_inputs(
        protocol,
        summary,
        packet,
        reviews,
        blinding_key,
        panel_summary,
        arm_map,
        review_amendment,
        protocol_sha256,
        review_amendment_sha256,
    )
    cases_by_id = {case["case_id"]: case for case in summary["cases"]}
    if arm_map is not None:
        entries = arm_map.get("entries") or []
        if len(entries) != len(cases_by_id):
            raise ValueError("Arm map does not cover the exact generation case count")
        packet_candidates = {
            candidate["candidate_id"]: (block["block_id"], response_sha(candidate["response"]))
            for block in packet["blocks"]
            for candidate in block["candidates"]
        }
        if {entry.get("candidate_id") for entry in entries} != set(packet_candidates):
            raise ValueError("Arm map does not cover the exact blinded candidate set")
        candidate_to_case = {}
        for entry in entries:
            case = cases_by_id.get(entry.get("case_id"))
            block_id = (
                f"{case['scenario']}-r{case['repeat_index']}" if case is not None else None
            )
            packet_block, packet_response_sha = packet_candidates[entry["candidate_id"]]
            if (
                case is None
                or entry.get("arm") != case.get("arm")
                or entry.get("block_id") != block_id
                or entry.get("block_id") != packet_block
                or entry.get("response_sha256") != packet_response_sha
                or entry.get("candidate_id") in candidate_to_case
            ):
                raise ValueError("Arm-map candidate mapping mismatch")
            candidate_to_case[entry["candidate_id"]] = case
    else:
        candidate_to_case = {}
        assert blinding_key is not None
        for case in summary["cases"]:
            block_id = f"{case['scenario']}-r{case['repeat_index']}"
            candidate_to_case[candidate_id(blinding_key, block_id, case["case_id"])] = case

    dimension_values: dict[str, dict[str, list[float]]] = {
        arm: {dimension: [] for dimension in REVIEW_DIMENSIONS}
        for arm in protocol["arms"]
    }
    safety: dict[str, list[float]] = defaultdict(list)
    fatal: dict[str, list[float]] = defaultdict(list)
    preference_deltas: dict[tuple[str, str], dict[str, list[float]]] = {
        ("bmadx_real", "placebo"): defaultdict(list),
        ("bmadx_stub", "placebo"): defaultdict(list),
        ("bmadx_real", "bmadx_stub"): defaultdict(list),
    }
    preferences_by_block: dict[str, list[set[str]]] = defaultdict(list)
    for review in reviews:
        for block in review["blocks"]:
            preferred = set(block["preferred_candidate_ids"])
            preferences_by_block[block["block_id"]].append(preferred)
            credit = 1.0 / len(preferred)
            arm_credit = {arm: 0.0 for arm in protocol["arms"]}
            scenario_id = block["block_id"].rsplit("-r", 1)[0]
            for entry in block["candidate_reviews"]:
                case = candidate_to_case[entry["candidate_id"]]
                arm = case["arm"]
                if entry["candidate_id"] in preferred:
                    arm_credit[arm] += credit
                for dimension in REVIEW_DIMENSIONS:
                    dimension_values[arm][dimension].append(float(entry[dimension]))
                safety[arm].append(float(entry["safety_omission"]))
                fatal[arm].append(float(entry["fatal_flaw"]))
            for (treatment, control), clusters in preference_deltas.items():
                clusters[scenario_id].append(
                    arm_credit[treatment] - arm_credit[control]
                )

    thresholds = protocol["decision_thresholds"]
    preference_agreements = []
    for preferred_sets in preferences_by_block.values():
        for left_index, left in enumerate(preferred_sets):
            for right in preferred_sets[left_index + 1 :]:
                preference_agreements.append(len(left & right) / len(left | right))
    preference_agreement = round(mean(preference_agreements), 6)
    comparisons = {}
    for (treatment, control), clusters in preference_deltas.items():
        values = [value for cluster in clusters.values() for value in cluster]
        comparisons[f"{treatment}_vs_{control}"] = {
            "net_blinded_preference": round(mean(values), 6),
            "scenario_cluster_bootstrap_95_ci": bootstrap_cluster_ci(
                clusters,
                int(protocol["analysis_seed"]),
                int(protocol["bootstrap_samples"]),
            ),
        }

    arm_metrics = {}
    for arm in protocol["arms"]:
        arm_cases = [case for case in summary["cases"] if case["arm"] == arm]
        arm_metrics[arm] = {
            "dimensions": {
                dimension: round(mean(dimension_values[arm][dimension]), 6)
                for dimension in REVIEW_DIMENSIONS
            },
            "safety_omission_rate": round(mean(safety[arm]), 6),
            "fatal_flaw_rate": round(mean(fatal[arm]), 6),
            "median_tokens": statistics.median(case["tokens"] for case in arm_cases),
            "median_duration_seconds": statistics.median(
                case["duration_seconds"] for case in arm_cases
            ),
            "response_contract_pass_rate": round(
                mean([float(case["response_contract_pass"]) for case in arm_cases]), 6
            ),
            "framework_leakage_rate": round(
                mean([float(case["framework_leakage_detected"]) for case in arm_cases]),
                6,
            ),
        }

    real = arm_metrics["bmadx_real"]
    placebo = arm_metrics["placebo"]
    primary = comparisons["bmadx_real_vs_placebo"]
    tradeoffs = {
        "token_ratio_real_to_placebo": round(
            ratio(real["median_tokens"], placebo["median_tokens"]) or 0.0, 6
        ),
        "latency_ratio_real_to_placebo": round(
            ratio(real["median_duration_seconds"], placebo["median_duration_seconds"])
            or 0.0,
            6,
        ),
        "ceremony_burden_delta": round(
            real["dimensions"]["ceremony_burden"]
            - placebo["dimensions"]["ceremony_burden"],
            6,
        ),
        "safety_omission_rate_delta": round(
            real["safety_omission_rate"] - placebo["safety_omission_rate"], 6
        ),
        "fatal_flaw_rate_delta": round(
            real["fatal_flaw_rate"] - placebo["fatal_flaw_rate"], 6
        ),
        "framework_leakage_rate_delta": round(
            real["framework_leakage_rate"] - placebo["framework_leakage_rate"], 6
        ),
    }
    positive_gates = {
        "minimum_net_preference": primary["net_blinded_preference"]
        >= float(thresholds["minimum_net_preference"]),
        "reviewer_preference_agreement": preference_agreement
        >= float(thresholds["minimum_preference_agreement"]),
        "preference_ci_above_zero": primary["scenario_cluster_bootstrap_95_ci"][0] > 0,
        "safety_noninferior": tradeoffs["safety_omission_rate_delta"]
        <= float(thresholds["maximum_safety_omission_delta"]),
        "fatal_flaw_noninferior": tradeoffs["fatal_flaw_rate_delta"]
        <= float(thresholds["maximum_fatal_flaw_delta"]),
        "framework_leakage_noninferior": tradeoffs["framework_leakage_rate_delta"]
        <= float(thresholds["maximum_framework_leakage_delta"]),
        "token_overhead_acceptable": tradeoffs["token_ratio_real_to_placebo"]
        <= float(thresholds["maximum_token_ratio"]),
        "latency_overhead_acceptable": tradeoffs["latency_ratio_real_to_placebo"]
        <= float(thresholds["maximum_latency_ratio"]),
        "ceremony_overhead_acceptable": tradeoffs["ceremony_burden_delta"]
        <= float(thresholds["maximum_ceremony_delta"]),
    }
    if all(positive_gates.values()):
        verdict = "positive_value_added"
    elif (
        primary["scenario_cluster_bootstrap_95_ci"][1] < 0
        or tradeoffs["safety_omission_rate_delta"]
        > float(thresholds["maximum_safety_omission_delta"])
        or tradeoffs["fatal_flaw_rate_delta"]
        > float(thresholds["maximum_fatal_flaw_delta"])
        or tradeoffs["framework_leakage_rate_delta"]
        > float(thresholds["maximum_framework_leakage_delta"])
    ):
        verdict = "negative_or_harmful"
    else:
        verdict = "inconclusive"
    return {
        "schema": "bmadx_value_analysis.v1",
        "protocol_id": protocol["protocol_id"],
        "verdict": verdict,
        "primary_estimand": "bmadx_real_vs_placebo blinded preference",
        "positive_gates": positive_gates,
        "comparisons": comparisons,
        "arm_metrics": arm_metrics,
        "tradeoffs": tradeoffs,
        "reviewer_preference_pairwise_jaccard": preference_agreement,
        "reviewer_count": len(reviews),
        "synthetic_panel_healthy": panel_summary.get("healthy")
        if panel_summary is not None
        else None,
        "scenario_cluster_count": len(protocol["scenarios"]),
        "case_count": len(summary["cases"]),
        "unblinding_method": "arm_map" if arm_map is not None else "blinding_key",
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol = load_protocol(args.protocol)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    reviews = [json.loads(path.read_text(encoding="utf-8")) for path in args.review]
    panel_summary = (
        json.loads(args.panel_summary.read_text(encoding="utf-8"))
        if args.panel_summary
        else None
    )
    review_amendment = (
        json.loads(args.review_amendment.read_text(encoding="utf-8"))
        if args.review_amendment
        else None
    )
    arm_map = (
        json.loads(args.arm_map.read_text(encoding="utf-8")) if args.arm_map else None
    )
    result = analyze(
        protocol,
        summary,
        packet,
        reviews,
        read_blinding_key(args.blinding_key_file) if args.blinding_key_file else None,
        panel_summary,
        arm_map,
        review_amendment,
        sha256_file(args.protocol),
        sha256_file(args.review_amendment) if args.review_amendment else None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps({"output": str(args.output), "verdict": result["verdict"]}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
