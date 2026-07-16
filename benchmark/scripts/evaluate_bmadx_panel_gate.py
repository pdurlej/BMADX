#!/usr/bin/env python3
"""Evaluate whether a completed synthetic panel is eligible for unblinding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_panel_gate(
    panel: dict[str, Any], summary: dict[str, Any]
) -> dict[str, Any]:
    if panel.get("schema") != "bmadx_synthetic_review_panel.v1":
        raise ValueError("Unsupported panel protocol")
    if summary.get("schema") != "bmadx_synthetic_panel_summary.v1":
        raise ValueError("Unsupported panel summary")
    reviewers = summary.get("reviewers") or []
    expected_ids = {item.get("reviewer_id") for item in panel.get("reviewers") or []}
    actual_ids = {item.get("reviewer_id") for item in reviewers}
    if len(expected_ids) != 5 or actual_ids != expected_ids:
        raise ValueError("Panel summary does not contain the exact frozen reviewers")
    if summary.get("expected_call_count") != panel.get("expected_call_count"):
        raise ValueError("Panel call count provenance mismatch")
    thresholds = panel["health_thresholds"]
    minimum_jaccard = float(thresholds["minimum_order_stability_preference_jaccard"])
    maximum_delta = float(
        thresholds["maximum_order_stability_mean_absolute_score_delta"]
    )
    failures = []
    for reviewer in reviewers:
        jaccard = float(reviewer["order_stability_preference_jaccard"])
        delta = float(reviewer["order_stability_mean_absolute_score_delta"])
        expected_healthy = (
            reviewer.get("stability_block_count")
            == panel.get("stability_blocks_per_reviewer")
            and jaccard >= minimum_jaccard
            and delta <= maximum_delta
        )
        if bool(reviewer.get("healthy")) != expected_healthy:
            raise ValueError("Reviewer health flag does not match frozen thresholds")
        if not expected_healthy:
            failures.append(
                {
                    "reviewer_id": reviewer["reviewer_id"],
                    "preference_jaccard": jaccard,
                    "minimum_preference_jaccard": minimum_jaccard,
                    "mean_absolute_score_delta": delta,
                    "maximum_mean_absolute_score_delta": maximum_delta,
                }
            )
    complete = (
        summary.get("complete") is True
        and summary.get("completed_call_count") == panel.get("expected_call_count")
    )
    eligible = complete and not failures and summary.get("healthy") is True
    if bool(summary.get("healthy")) != (not failures):
        raise ValueError("Panel health flag does not match reviewer health")
    return {
        "schema": "bmadx_panel_gate_result.v1",
        "status": "eligible_for_unblinding" if eligible else "blocked_unhealthy_panel",
        "complete": complete,
        "eligible_for_unblinding": eligible,
        "unblinding_performed": False,
        "positive_value_claim_allowed": False,
        "scientific_call_count": summary.get("completed_call_count"),
        "provider_attempt_count": summary.get("provider_attempt_count"),
        "retried_call_count": summary.get("retried_call_count"),
        "healthy_reviewer_count": len(reviewers) - len(failures),
        "required_healthy_reviewer_count": len(reviewers),
        "failed_reviewers": failures,
        "claim_boundary": (
            "Synthetic panel health is a prerequisite. This gate does not itself "
            "measure BMADX value and cannot support human novice outcomes."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-protocol", type=Path, required=True)
    parser.add_argument("--panel-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    panel = json.loads(args.panel_protocol.read_text(encoding="utf-8"))
    summary = json.loads(args.panel_summary.read_text(encoding="utf-8"))
    result = evaluate_panel_gate(panel, summary)
    result["panel_protocol_sha256"] = sha256_file(args.panel_protocol)
    result["panel_summary_sha256"] = sha256_file(args.panel_summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
