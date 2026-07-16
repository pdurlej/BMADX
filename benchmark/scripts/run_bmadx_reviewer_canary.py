#!/usr/bin/env python3
"""Run schema-only reviewer canaries without inspecting candidate scores."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from run_bmadx_synthetic_review_panel import (
    build_prompt,
    command_for_call,
    load_json,
    normalize_candidate_aliases,
    normalize_candidate_ids,
    normalize_candidate_order,
    normalize_judgment_keys,
    ordered_block,
    parse_runtime_output,
    validate_judgment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canary-protocol", type=Path, required=True)
    parser.add_argument("--panel-protocol", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--confirm-call-count", type=int, required=True)
    parser.add_argument("--case-timeout", type=int, default=240)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    canary = load_json(args.canary_protocol)
    panel = load_json(args.panel_protocol)
    packet = load_json(args.packet)
    schema = canary.get("schema")
    if schema == "bmadx_reviewer_selection_canary.v1":
        candidates = canary.get("candidate_reviewers") or []
        protocol_valid = (
            canary.get("selection_rule")
            == "first_reviewer_in_frozen_order_with_all_schema_valid_calls"
            and canary.get("scores_must_not_influence_selection") is True
        )
    elif schema == "bmadx_panel_schema_preflight.v1":
        candidates = panel.get("reviewers") or []
        protocol_valid = (
            canary.get("execution_rule") == "every_reviewer_must_pass_every_call"
            and canary.get("scores_must_not_influence_acceptance") is True
            and canary.get("panel_protocol_sha256") == sha256_file(args.panel_protocol)
        )
    else:
        raise ValueError("Unsupported reviewer-canary protocol")
    reviewer = next(
        (item for item in candidates if item.get("reviewer_id") == args.reviewer_id),
        None,
    )
    raw_calls = canary.get("canary_calls")
    if raw_calls is None:
        canary_calls = [
            {"lane": "primary", "block_id": block_id}
            for block_id in (canary.get("canary_block_ids") or [])
        ]
    else:
        canary_calls = raw_calls
    if (
        not protocol_valid
        or reviewer is None
        or args.confirm_call_count != len(canary_calls)
        or any(
            not isinstance(item, dict)
            or item.get("lane") not in {"primary", "stability"}
            or not isinstance(item.get("block_id"), str)
            for item in canary_calls
        )
    ):
        raise ValueError("Reviewer-selection canary is not frozen")
    packet_by_id = {block["block_id"]: block for block in packet["blocks"]}
    if {item["block_id"] for item in canary_calls} - set(packet_by_id):
        raise ValueError("Canary references an unknown packet block")
    prompt_path = Path(panel["prompt"]["path"])
    if not prompt_path.is_absolute():
        prompt_path = Path(__file__).resolve().parents[2] / prompt_path
    if sha256_file(prompt_path) != panel["prompt"]["sha256"]:
        raise ValueError("Synthetic-review prompt hash mismatch")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = args.output_dir / "raw"
    raw_dir.mkdir()
    records: list[dict[str, Any]] = []
    for canary_call in canary_calls:
        lane = canary_call["lane"]
        block_id = canary_call["block_id"]
        call = {
            "lane": lane,
            "reviewer": reviewer,
            "reviewer_id": reviewer["reviewer_id"],
            "block_id": block_id,
        }
        block = ordered_block(panel, packet_by_id[block_id], call)
        prompt = build_prompt(prompt_text, packet, block)
        command, env = command_for_call(call, prompt)
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="bmadx-canary-") as tempdir:
            result = subprocess.run(
                command,
                cwd=tempdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=args.case_timeout,
                check=False,
            )
        judgment = parse_runtime_output(result.stdout)
        normalizations = normalize_judgment_keys(judgment)
        normalizations.extend(normalize_candidate_aliases(judgment, block))
        normalizations.extend(normalize_candidate_ids(judgment, block))
        normalizations.extend(normalize_candidate_order(judgment, block))
        validation = validate_judgment(judgment, block)
        valid = result.returncode == 0 and validation["valid"]
        raw_stem = f"{lane}--{block_id}"
        (raw_dir / f"{raw_stem}.stdout").write_text(result.stdout, encoding="utf-8")
        (raw_dir / f"{raw_stem}.stderr").write_text(
            "[stderr omitted; verify stderr_sha256 in canary-summary.json]\n",
            encoding="utf-8",
        )
        records.append(
            {
                "lane": lane,
                "block_id": block_id,
                "valid": valid,
                "returncode": result.returncode,
                "duration_seconds": round(time.monotonic() - started, 3),
                "validation_errors": validation["errors"],
                "normalizations": normalizations,
                "judgment_sha256": hashlib.sha256(
                    json.dumps(judgment, sort_keys=True).encode()
                ).hexdigest()
                if judgment is not None
                else None,
                "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
            }
        )
        if not valid:
            break
    complete = len(records) == len(canary_calls) and all(
        item["valid"] for item in records
    )
    summary = {
        "schema": "bmadx_reviewer_canary_summary.v1",
        "canary_protocol_sha256": sha256_file(args.canary_protocol),
        "panel_protocol_sha256": sha256_file(args.panel_protocol),
        "packet_sha256": sha256_file(args.packet),
        "reviewer_id": reviewer["reviewer_id"],
        "family": reviewer["family"],
        "model": reviewer["model"],
        "scores_inspected_for_selection": False,
        "complete": complete,
        "calls": records,
    }
    (args.output_dir / "canary-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
