#!/usr/bin/env python3
"""Build a fail-closed post-review arm map from exact blinded response payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from bmadx_value_contract import response_for_review
from build_bmadx_value_review_packet import json_sha, redact_framework_labels


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirm-candidate-count", type=int, required=True)
    return parser.parse_args(argv)


def response_sha(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def build_arm_map(summary: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    if summary.get("complete") is not True:
        raise ValueError("Arm-map construction requires a complete generation summary")
    if summary.get("protocol_id") != packet.get("protocol_id"):
        raise ValueError("Summary and packet protocol IDs differ")

    cases_by_block: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for case in summary.get("cases") or []:
        block_id = f"{case['scenario']}-r{case['repeat_index']}"
        review_payload = redact_framework_labels(
            response_for_review(case.get("response_payload") or {})
        )
        cases_by_block.setdefault(block_id, {}).setdefault(
            response_sha(review_payload), []
        ).append(case)

    entries: list[dict[str, Any]] = []
    used_case_ids: set[str] = set()
    for block in packet.get("blocks") or []:
        block_id = block["block_id"]
        candidates = block.get("candidates") or []
        if len(candidates) != 3:
            raise ValueError(f"Expected exactly three candidates: {block_id}")
        for candidate in candidates:
            digest = response_sha(candidate.get("response"))
            matches = cases_by_block.get(block_id, {}).get(digest, [])
            if len(matches) != 1:
                raise ValueError(
                    f"Arm-map response match is not unique: {block_id} {candidate['candidate_id']}"
                )
            case = matches[0]
            if case["case_id"] in used_case_ids:
                raise ValueError(f"Generation case mapped more than once: {case['case_id']}")
            used_case_ids.add(case["case_id"])
            entries.append(
                {
                    "block_id": block_id,
                    "candidate_id": candidate["candidate_id"],
                    "response_sha256": digest,
                    "case_id": case["case_id"],
                    "arm": case["arm"],
                }
            )

    expected_case_ids = {case["case_id"] for case in summary.get("cases") or []}
    if used_case_ids != expected_case_ids:
        raise ValueError("Arm map does not cover the exact generation case set")
    return {
        "schema": "bmadx_value_arm_map.v1",
        "protocol_id": packet["protocol_id"],
        "method": "exact_redacted_review_payload_sha256",
        "summary_sha256": json_sha(summary),
        "packet_sha256": json_sha(packet),
        "complete": True,
        "candidate_count": len(entries),
        "entries": sorted(entries, key=lambda item: (item["block_id"], item["candidate_id"])),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    arm_map = build_arm_map(summary, packet)
    if args.confirm_candidate_count != arm_map["candidate_count"]:
        raise SystemExit(
            "Refusing arm-map write: pass "
            f"--confirm-candidate-count {arm_map['candidate_count']}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(arm_map, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "candidate_count": arm_map["candidate_count"],
                "packet_sha256": arm_map["packet_sha256"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
