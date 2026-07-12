#!/usr/bin/env python3
"""Build an arm-blinded review packet from a completed BMADX value study."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from bmadx_value_contract import REVIEW_DIMENSIONS, candidate_id, response_for_review
from run_bmadx_value_study import (
    FRAMEWORK_LEAKAGE,
    REPO_ROOT,
    load_protocol,
    scenario_path,
    task_from_path,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--blinding-key-file", type=Path, required=True)
    return parser.parse_args(argv)


def json_sha(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_blinding_key(path: Path) -> bytes:
    value = path.read_text(encoding="ascii").strip()
    if len(value) != 64:
        raise ValueError("Blinding key must contain exactly 32 bytes encoded as hex")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("Blinding key must be hexadecimal") from exc


def redact_framework_labels(value: Any) -> Any:
    if isinstance(value, str):
        return FRAMEWORK_LEAKAGE.sub("[internal label redacted]", value)
    if isinstance(value, list):
        return [redact_framework_labels(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_framework_labels(item) for key, item in value.items()}
    return value


def build_packet(
    protocol: dict[str, Any], summary: dict[str, Any], blinding_key: bytes
) -> tuple[dict, dict]:
    if summary.get("complete") is not True or summary.get(
        "completed_call_count"
    ) != summary.get("expected_call_count"):
        raise ValueError("Blinded review requires a complete integrity-healthy study")
    if summary.get("protocol_id") != protocol.get("protocol_id"):
        raise ValueError("Summary and protocol IDs differ")
    cases = list(summary.get("cases") or [])
    if any(
        not case.get("activation_pass") or case.get("protected_filesystem_mutation")
        for case in cases
    ):
        raise ValueError("Summary contains an integrity failure")
    rubric_path = REPO_ROOT / protocol["rubric"]["path"]
    rubric_bytes = rubric_path.read_bytes()
    rubric_sha = hashlib.sha256(rubric_bytes).hexdigest()
    if rubric_sha != protocol["rubric"]["sha256"]:
        raise ValueError("Review rubric hash mismatch")
    rubric = json.loads(rubric_bytes)
    if tuple(rubric.get("dimensions") or {}) != REVIEW_DIMENSIONS:
        raise ValueError("Review rubric dimensions do not match the response contract")

    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for case in cases:
        grouped[(case["scenario"], int(case["repeat_index"]))].append(case)
    scenario_map = {entry["id"]: entry for entry in protocol["scenarios"]}
    expected_blocks = {
        (scenario_id, repeat_index)
        for scenario_id in scenario_map
        for repeat_index in range(1, int(protocol["repeats"]) + 1)
    }
    if set(grouped) != expected_blocks or len(cases) != int(
        protocol["expected_call_count"]
    ):
        raise ValueError(
            "Summary does not contain the exact frozen scenario-repeat matrix"
        )
    blocks = []
    template_blocks = []
    for scenario_id, repeat_index in sorted(grouped):
        block_id = f"{scenario_id}-r{repeat_index}"
        block_cases = grouped[(scenario_id, repeat_index)]
        if len(block_cases) != 3 or {case["arm"] for case in block_cases} != set(
            protocol["arms"]
        ):
            raise ValueError(
                f"Block is not a complete three-arm comparison: {block_id}"
            )
        candidates = [
            {
                "candidate_id": candidate_id(blinding_key, block_id, case["case_id"]),
                "response": redact_framework_labels(
                    response_for_review(case.get("response_payload") or {})
                ),
                "blindability_failure": bool(case.get("framework_leakage_detected")),
            }
            for case in block_cases
        ]
        order_seed = int.from_bytes(
            hashlib.sha256(blinding_key + f":{block_id}:order".encode()).digest()[:8]
        )
        random.Random(order_seed).shuffle(candidates)
        blocks.append(
            {
                "block_id": block_id,
                "scenario_id": scenario_id,
                "repeat_index": repeat_index,
                "task": task_from_path(scenario_path(scenario_map[scenario_id])),
                "candidates": candidates,
            }
        )
        template_blocks.append(
            {
                "block_id": block_id,
                "candidate_reviews": [
                    {
                        "candidate_id": candidate["candidate_id"],
                        **{dimension: None for dimension in REVIEW_DIMENSIONS},
                        "safety_omission": None,
                        "fatal_flaw": None,
                        "notes": "",
                    }
                    for candidate in candidates
                ],
                "preferred_candidate_ids": [],
            }
        )
    packet = {
        "schema": "bmadx_value_review_packet.v1",
        "protocol_id": protocol["protocol_id"],
        "blinding_key_sha256": hashlib.sha256(blinding_key).hexdigest(),
        "rubric_sha256": rubric_sha,
        "rubric": rubric,
        "blocks": blocks,
    }
    packet_sha = json_sha(packet)
    template = {
        "schema": "bmadx_value_review.v1",
        "protocol_id": protocol["protocol_id"],
        "packet_sha256": packet_sha,
        "reviewer_id": "replace-with-pseudonymous-id",
        "independent_of_bmadx_authorship": None,
        "mapping_was_not_available": None,
        "blocks": template_blocks,
    }
    return packet, template


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol = load_protocol(args.protocol)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    packet, template = build_packet(
        protocol, summary, read_blinding_key(args.blinding_key_file)
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = args.output_dir / "review-packet.json"
    template_path = args.output_dir / "review-template.json"
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    template_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"packet": str(packet_path), "template": str(template_path)}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
