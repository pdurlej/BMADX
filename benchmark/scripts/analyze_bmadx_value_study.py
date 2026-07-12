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
from build_bmadx_value_review_packet import json_sha, read_blinding_key
from run_bmadx_value_study import load_protocol


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--review", type=Path, action="append", required=True)
    parser.add_argument("--panel-summary", type=Path)
    parser.add_argument("--blinding-key-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


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
    blinding_key: bytes,
    panel_summary: dict[str, Any] | None = None,
) -> None:
    if summary.get("complete") is not True:
        raise ValueError("Analysis requires a complete integrity-healthy study")
    if packet.get("rubric_sha256") != (protocol.get("rubric") or {}).get("sha256"):
        raise ValueError("Review packet rubric hash mismatch")
    if packet.get("blinding_key_sha256") != hashlib.sha256(blinding_key).hexdigest():
        raise ValueError("Blinding key does not match the review packet")
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
    review_policy = protocol.get("review_policy") or {}
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
    blinding_key: bytes,
    panel_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_inputs(
        protocol, summary, packet, reviews, blinding_key, panel_summary
    )
    candidate_to_case = {}
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
    result = analyze(
        protocol,
        summary,
        packet,
        reviews,
        read_blinding_key(args.blinding_key_file),
        panel_summary,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps({"output": str(args.output), "verdict": result["verdict"]}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
