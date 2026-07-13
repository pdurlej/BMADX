#!/usr/bin/env python3
"""Run the frozen cross-model synthetic review panel for the BMADX value study."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from bmadx_value_contract import REVIEW_DIMENSIONS
from build_bmadx_value_review_packet import json_sha
from run_bmadx_value_study import DEFAULT_PROTOCOL, REPO_ROOT, load_protocol


DEFAULT_PANEL = REPO_ROOT / "benchmark/value-study/synthetic-panel-v1.json"
DEFAULT_REVIEW_AMENDMENT = (
    REPO_ROOT / "benchmark/value-study/review-runner-amendment-v1.5.json"
)
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--panel-protocol", type=Path, default=DEFAULT_PANEL)
    parser.add_argument(
        "--review-amendment", type=Path, default=DEFAULT_REVIEW_AMENDMENT
    )
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--confirm-call-count", type=int)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--case-timeout", type=int, default=240)
    args = parser.parse_args(argv)
    if args.case_timeout < 1:
        parser.error("--case-timeout must be >= 1")
    if not args.validate_only and (args.packet is None or args.output_dir is None):
        parser.error("live execution requires --packet and --output-dir")
    return args


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version_tuple(value: str) -> tuple[int, int, int]:
    match = VERSION.search(value)
    if not match:
        raise ValueError(f"Cannot parse runtime version: {value!r}")
    return tuple(int(part) for part in match.groups())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def validate_panel_protocol(
    panel: dict[str, Any], value_protocol: dict[str, Any]
) -> None:
    if panel.get("schema") != "bmadx_synthetic_review_panel.v1":
        raise ValueError("Unsupported synthetic-panel schema")
    runtime = panel.get("runtime") or {}
    if runtime.get("primary") != "pi_ollama_only":
        raise ValueError("Synthetic-panel runtime routing is not frozen")
    if runtime.get("automatic_retries") != 0:
        raise ValueError("Synthetic panel must fail closed without automatic retries")
    if not all(
        runtime.get(key) is True
        for key in (
            "fresh_session_per_call",
            "project_context_disabled",
            "tools_disabled",
        )
    ):
        raise ValueError("Synthetic-panel runtime isolation is not frozen")
    reviewers = panel.get("reviewers") or []
    if len(reviewers) != 5:
        raise ValueError("Synthetic panel requires exactly five reviewers")
    reviewer_ids = [entry.get("reviewer_id") for entry in reviewers]
    families = [entry.get("family") for entry in reviewers]
    if len(set(reviewer_ids)) != 5 or len(set(families)) != 5:
        raise ValueError("Reviewer IDs and model families must be unique")
    if any(entry.get("runtime") != "pi" for entry in reviewers):
        raise ValueError("Synthetic panel requires five Pi reviewers")
    if any(not str(entry.get("model", "")).startswith("ollama/") for entry in reviewers):
        raise ValueError("Synthetic panel requires Ollama-backed reviewer models")
    blocks = len(value_protocol.get("scenarios") or []) * int(
        value_protocol.get("repeats", 0)
    )
    if blocks != panel.get("expected_blocks"):
        raise ValueError("Synthetic-panel block count does not match value study")
    primary = blocks * len(reviewers)
    stability = int(panel["stability_blocks_per_reviewer"]) * len(reviewers)
    expected = primary + stability
    frozen = (
        panel.get("expected_primary_call_count"),
        panel.get("expected_stability_call_count"),
        panel.get("expected_call_count"),
    )
    if frozen != (primary, stability, expected):
        raise ValueError("Synthetic-panel call counts are not internally consistent")
    claim_rules = panel.get("claim_rules") or {}
    if not all(
        claim_rules.get(key) is True
        for key in (
            "one_vote_per_model_family",
            "stability_calls_are_not_votes",
            "unhealthy_panel_blocks_positive_claim",
            "synthetic_evidence_does_not_claim_human_novice_outcomes",
        )
    ):
        raise ValueError("Synthetic-panel claim boundaries are not frozen")
    prompt = panel.get("prompt") or {}
    prompt_path = REPO_ROOT / str(prompt.get("path") or "")
    if not prompt_path.is_file() or sha256_file(prompt_path) != prompt.get("sha256"):
        raise ValueError("Synthetic-review prompt hash mismatch")


def validate_review_amendment(
    amendment: dict[str, Any], protocol_path: Path, panel_path: Path
) -> None:
    expected = {
        "schema": "bmadx_review_runner_amendment.v1",
        "amendment_id": "pi-final-thinking-judgment-fallback-v1.5",
        "value_protocol_sha256": sha256_file(protocol_path),
        "panel_protocol_sha256": sha256_file(panel_path),
        "previous_amendment_sha256": (
            "e0c5bc38454e37792f4de59152c2dc0f375b053d17adcb4824b59d21b0a2d495"
        ),
        "amended_runner_sha256": sha256_file(Path(__file__)),
        "valid_votes_before_amendment": 78,
        "invalid_canary_calls_before_amendment": 1,
        "restart_panel_from_zero": True,
        "changes_candidate_order": False,
        "changes_rubric_or_scoring": False,
        "changes_models_or_call_counts": False,
        "normalizes_only_one_unambiguous_numeric_dimension_key": True,
        "canonicalizes_only_frozen_generic_rubric_suffixes": True,
        "normalizes_only_unique_distance_one_candidate_ids": True,
        "uses_complete_final_thinking_only_when_text_is_empty": True,
    }
    if any(amendment.get(key) != value for key, value in expected.items()):
        raise ValueError("Synthetic review-runner amendment is not frozen")


def deterministic_seed(seed: int, material: str) -> int:
    digest = hashlib.sha256(f"{seed}:{material}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def selected_blocks(
    block_ids: list[str], count: int, seed: int, reviewer_id: str, lane: str
) -> set[str]:
    values = list(block_ids)
    random.Random(deterministic_seed(seed, f"{reviewer_id}:{lane}")).shuffle(values)
    return set(values[:count])


def build_panel_schedule(
    panel: dict[str, Any], packet: dict[str, Any]
) -> list[dict[str, Any]]:
    blocks = sorted(packet.get("blocks") or [], key=lambda value: value["block_id"])
    if len(blocks) != int(panel["expected_blocks"]):
        raise ValueError("Review packet does not have the frozen block count")
    block_ids = [block["block_id"] for block in blocks]
    seed = int(panel["assignment_seed"])
    schedule: list[dict[str, Any]] = []
    for reviewer in panel["reviewers"]:
        reviewer_id = reviewer["reviewer_id"]
        stability = selected_blocks(
            block_ids,
            int(panel["stability_blocks_per_reviewer"]),
            seed,
            reviewer_id,
            "stability",
        )
        for block in blocks:
            schedule.append(
                {
                    "call_id": f"primary--{reviewer_id}--{block['block_id']}",
                    "lane": "primary",
                    "reviewer": reviewer,
                    "block_id": block["block_id"],
                    "runtime": reviewer["runtime"],
                }
            )
            if block["block_id"] in stability:
                schedule.append(
                    {
                        "call_id": f"stability--{reviewer_id}--{block['block_id']}",
                        "lane": "stability",
                        "reviewer": reviewer,
                        "block_id": block["block_id"],
                        "runtime": reviewer["runtime"],
                    }
                )
    random.Random(seed).shuffle(schedule)
    if len(schedule) != int(panel["expected_call_count"]):
        raise ValueError("Generated synthetic-panel schedule has the wrong size")
    return schedule


def ordered_block(
    panel: dict[str, Any], packet_block: dict[str, Any], call: dict[str, Any]
) -> dict[str, Any]:
    candidates = list(packet_block["candidates"])
    seed = deterministic_seed(
        int(panel["assignment_seed"]),
        f"{call['reviewer']['reviewer_id']}:{call['block_id']}:primary-order",
    )
    random.Random(seed).shuffle(candidates)
    if call["lane"] == "stability":
        candidates = candidates[1:] + candidates[:1]
    return {
        "block_id": packet_block["block_id"],
        "task": packet_block["task"],
        "rubric": packet_block.get("rubric"),
        "candidates": candidates,
    }


def build_prompt(
    prompt_text: str, packet: dict[str, Any], block: dict[str, Any]
) -> str:
    payload = {
        "block_id": block["block_id"],
        "task": block["task"],
        "rubric": packet["rubric"],
        "candidates": block["candidates"],
    }
    return prompt_text.rstrip() + "\n\nJSON input:\n" + json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    )


def judgment_from_text(text: str) -> dict[str, Any] | None:
    candidate = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*\n([\s\S]*?)\n```", candidate)
    if fenced:
        candidate = fenced.group(1).strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return (
        value
        if isinstance(value, dict)
        and "block_id" in value
        and "candidate_reviews" in value
        else None
    )


def parse_runtime_output(stdout: str) -> dict[str, Any] | None:
    direct = judgment_from_text(stdout)
    if direct is not None:
        return direct
    pi_final: str | None = None
    pi_thinking: str | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            event.get("type") == "message_end"
            and isinstance(event.get("message"), dict)
            and event["message"].get("role") == "assistant"
        ):
            content = event["message"].get("content") or []
            pi_final = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
            pi_thinking = "".join(
                item.get("thinking", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "thinking"
            )
    return judgment_from_text(pi_final or "") or judgment_from_text(pi_thinking or "")


def dimension_key_stem(value: str) -> str:
    for suffix in (
        "_quality",
        "_coverage",
        "_burden",
        "_calibration",
        "_correctness",
    ):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break
    return value.removesuffix("s")


def normalize_judgment_keys(judgment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if judgment is None:
        return []
    allowed = set(REVIEW_DIMENSIONS) | {
        "candidate_id",
        "safety_omission",
        "fatal_flaw",
        "notes",
    }
    normalizations = []
    for index, review in enumerate(judgment.get("candidate_reviews") or []):
        if not isinstance(review, dict):
            continue
        missing = [dimension for dimension in REVIEW_DIMENSIONS if dimension not in review]
        unknown_numeric = [
            key
            for key, value in review.items()
            if key not in allowed
            and isinstance(value, int)
            and not isinstance(value, bool)
            and 1 <= value <= 7
        ]
        if len(missing) != 1 or len(unknown_numeric) != 1:
            continue
        source = unknown_numeric[0]
        target = missing[0]
        source_stem = dimension_key_stem(source)
        target_stem = dimension_key_stem(target)
        similarity = difflib.SequenceMatcher(None, source_stem, target_stem).ratio()
        if similarity < 0.85:
            continue
        review[target] = review.pop(source)
        normalizations.append(
            {
                "candidate_index": index,
                "source_key": source,
                "target_key": target,
                "source_stem": source_stem,
                "target_stem": target_stem,
                "similarity": round(similarity, 6),
            }
        )
    return normalizations


def edit_distance_at_most_one(left: str, right: str) -> bool:
    if left == right or abs(len(left) - len(right)) > 1:
        return False
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right, strict=True)) == 1
    shorter, longer = (left, right) if len(left) < len(right) else (right, left)
    short_index = 0
    long_index = 0
    edits = 0
    while short_index < len(shorter) and long_index < len(longer):
        if shorter[short_index] == longer[long_index]:
            short_index += 1
            long_index += 1
            continue
        edits += 1
        long_index += 1
        if edits > 1:
            return False
    return True


def normalize_candidate_ids(
    judgment: dict[str, Any] | None, block: dict[str, Any]
) -> list[dict[str, Any]]:
    if judgment is None:
        return []
    expected = [candidate["candidate_id"] for candidate in block["candidates"]]
    reviews = judgment.get("candidate_reviews") or []
    observed = {
        review.get("candidate_id")
        for review in reviews
        if isinstance(review, dict) and review.get("candidate_id") in expected
    }
    normalizations = []
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            continue
        source = review.get("candidate_id")
        if not isinstance(source, str) or source in expected:
            continue
        matches = [
            candidate_id
            for candidate_id in expected
            if candidate_id not in observed
            and edit_distance_at_most_one(source, candidate_id)
        ]
        if len(matches) != 1:
            continue
        target = matches[0]
        review["candidate_id"] = target
        preferred = judgment.get("preferred_candidate_ids") or []
        judgment["preferred_candidate_ids"] = [
            target if candidate_id == source else candidate_id
            for candidate_id in preferred
        ]
        observed.add(target)
        normalizations.append(
            {
                "candidate_index": index,
                "source_candidate_id": source,
                "target_candidate_id": target,
                "edit_distance": 1,
            }
        )
    return normalizations


def validate_judgment(
    judgment: dict[str, Any] | None, block: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    value = judgment or {}
    if value.get("block_id") != block["block_id"]:
        errors.append("block_id")
    expected = [candidate["candidate_id"] for candidate in block["candidates"]]
    reviews = value.get("candidate_reviews") or []
    observed = [entry.get("candidate_id") for entry in reviews if isinstance(entry, dict)]
    if observed != expected:
        errors.append("candidate_order_or_set")
    for entry in reviews:
        if not isinstance(entry, dict):
            errors.append("candidate_review_shape")
            continue
        for dimension in REVIEW_DIMENSIONS:
            score = entry.get(dimension)
            if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 7:
                errors.append(f"score:{dimension}")
        if not isinstance(entry.get("safety_omission"), bool):
            errors.append("safety_omission")
        if not isinstance(entry.get("fatal_flaw"), bool):
            errors.append("fatal_flaw")
        if not isinstance(entry.get("notes"), str):
            errors.append("notes")
    preferred = value.get("preferred_candidate_ids") or []
    if not preferred or not set(preferred).issubset(set(expected)):
        errors.append("preferred_candidate_ids")
    if value.get("confidence") not in {"low", "moderate", "high"}:
        errors.append("confidence")
    return {"valid": not errors, "errors": sorted(set(errors))}


def runtime_version(command: str) -> str:
    result = subprocess.run(
        [command, "--version"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"{command} --version failed")
    return (result.stdout or result.stderr).strip()


def validate_runtimes(panel: dict[str, Any]) -> dict[str, str]:
    versions = {"pi": runtime_version("pi")}
    runtime = panel["runtime"]
    if version_tuple(versions["pi"]) < version_tuple(runtime["minimum_pi_version"]):
        raise RuntimeError("Pi is older than the frozen panel minimum")
    for reviewer in panel["reviewers"]:
        pi_provider, pi_model = reviewer["model"].split("/", 1)
        if pi_provider != "ollama":
            raise RuntimeError("Pi primary reviewers must use Ollama")
        result = subprocess.run(
            ["pi", "--list-models", pi_model],
            capture_output=True,
            text=True,
            check=False,
        )
        model_listing = result.stdout + result.stderr
        if result.returncode != 0 or pi_model not in model_listing:
            raise RuntimeError(f"Pi primary model unavailable: {pi_model}")
    return versions


def command_for_call(call: dict[str, Any], prompt: str) -> tuple[list[str], dict[str, str]]:
    reviewer = call["reviewer"]
    env = os.environ.copy()
    pi_provider, pi_model = reviewer["model"].split("/", 1)
    command = [
        "pi",
        "--provider",
        pi_provider,
        "--model",
        pi_model,
        "--thinking",
        reviewer.get("variant") or "high",
        "--mode",
        "json",
        "--print",
        "--no-session",
        "--no-tools",
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-context-files",
        prompt,
    ]
    return command, env


def candidate_scores(judgment: dict[str, Any]) -> dict[str, list[int]]:
    return {
        entry["candidate_id"]: [entry[dimension] for dimension in REVIEW_DIMENSIONS]
        for entry in judgment["candidate_reviews"]
    }


def comparison_metrics(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    left_preferred = set(left["preferred_candidate_ids"])
    right_preferred = set(right["preferred_candidate_ids"])
    union = left_preferred | right_preferred
    jaccard = len(left_preferred & right_preferred) / len(union) if union else 0.0
    left_scores = candidate_scores(left)
    right_scores = candidate_scores(right)
    deltas = [
        abs(left_score - right_score)
        for candidate_id in left_scores
        for left_score, right_score in zip(
            left_scores[candidate_id], right_scores[candidate_id], strict=True
        )
    ]
    return {
        "preference_jaccard": jaccard,
        "mean_absolute_score_delta": sum(deltas) / len(deltas),
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def finalize(
    panel: dict[str, Any],
    panel_sha: str,
    packet: dict[str, Any],
    calls: list[dict[str, Any]],
    output_dir: Path,
    versions: dict[str, str],
    amendment_sha: str,
    runner_sha: str,
) -> dict[str, Any]:
    by_key = {
        (call["lane"], call["reviewer_id"], call["block_id"]): call
        for call in calls
        if call.get("status") == "complete"
    }
    packet_sha = json_sha(packet)
    reviews_dir = output_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    reviewer_summaries = []
    thresholds = panel["health_thresholds"]
    for reviewer in panel["reviewers"]:
        reviewer_id = reviewer["reviewer_id"]
        primary = [
            value
            for (lane, current, _), value in by_key.items()
            if lane == "primary" and current == reviewer_id
        ]
        blocks = [value["judgment"] for value in sorted(primary, key=lambda x: x["block_id"])]
        review = {
            "schema": "bmadx_value_review.v1",
            "protocol_id": packet["protocol_id"],
            "packet_sha256": packet_sha,
            "reviewer_id": reviewer_id,
            "reviewer_kind": "synthetic_model",
            "model_family": reviewer["family"],
            "model_id": reviewer["model"],
            "runtime": reviewer["runtime"],
            "runtime_version": versions[reviewer["runtime"]],
            "panel_protocol_sha256": panel_sha,
            "review_amendment_sha256": amendment_sha,
            "panel_runner_sha256": runner_sha,
            "independent_of_bmadx_authorship": True,
            "mapping_was_not_available": True,
            "blocks": blocks,
        }
        review_path = reviews_dir / f"{reviewer_id}.json"
        review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        stability_metrics = []
        for block in packet["blocks"]:
            block_id = block["block_id"]
            base = by_key.get(("primary", reviewer_id, block_id))
            stability = by_key.get(("stability", reviewer_id, block_id))
            if base and stability:
                stability_metrics.append(
                    comparison_metrics(base["judgment"], stability["judgment"])
                )
        stability_jaccard = mean(
            [value["preference_jaccard"] for value in stability_metrics]
        )
        stability_delta = mean(
            [value["mean_absolute_score_delta"] for value in stability_metrics]
        )
        healthy = (
            len(primary) == int(panel["expected_blocks"])
            and len(stability_metrics) == int(panel["stability_blocks_per_reviewer"])
            and stability_jaccard
            >= float(thresholds["minimum_order_stability_preference_jaccard"])
            and stability_delta
            <= float(thresholds["maximum_order_stability_mean_absolute_score_delta"])
        )
        reviewer_summaries.append(
            {
                "reviewer_id": reviewer_id,
                "family": reviewer["family"],
                "model_id": reviewer["model"],
                "healthy": bool(healthy),
                "primary_review_sha256": json_sha(review),
                "stability_block_count": len(stability_metrics),
                "order_stability_preference_jaccard": round(stability_jaccard, 6),
                "order_stability_mean_absolute_score_delta": round(stability_delta, 6),
            }
        )
    return {
        "schema": "bmadx_synthetic_panel_summary.v1",
        "protocol_id": packet["protocol_id"],
        "packet_sha256": packet_sha,
        "panel_protocol_sha256": panel_sha,
        "review_amendment_sha256": amendment_sha,
        "panel_runner_sha256": runner_sha,
        "complete": len(calls) == int(panel["expected_call_count"])
        and all(call.get("status") == "complete" for call in calls),
        "healthy": all(entry["healthy"] for entry in reviewer_summaries),
        "expected_call_count": int(panel["expected_call_count"]),
        "completed_call_count": sum(call.get("status") == "complete" for call in calls),
        "runtime_versions": versions,
        "reviewers": reviewer_summaries,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    value_protocol = load_protocol(args.protocol)
    panel = load_json(args.panel_protocol)
    amendment = load_json(args.review_amendment)
    validate_panel_protocol(panel, value_protocol)
    validate_review_amendment(amendment, args.protocol, args.panel_protocol)
    amendment_sha = sha256_file(args.review_amendment)
    runner_sha = sha256_file(Path(__file__))
    versions = validate_runtimes(panel)
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "valid",
                    "expected_call_count": panel["expected_call_count"],
                    "runtime_versions": versions,
                    "review_amendment_sha256": amendment_sha,
                    "panel_runner_sha256": runner_sha,
                },
                indent=2,
            )
        )
        return 0
    if args.confirm_call_count != int(panel["expected_call_count"]):
        raise SystemExit(
            f"Refusing live panel: pass --confirm-call-count {panel['expected_call_count']}"
        )
    packet = load_json(args.packet)
    if packet.get("protocol_id") != value_protocol.get("protocol_id"):
        raise ValueError("Packet and value-study protocol differ")
    schedule = build_panel_schedule(panel, packet)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "panel-checkpoint.json"
    panel_sha = sha256_file(args.panel_protocol)
    packet_sha = json_sha(packet)
    calls: list[dict[str, Any]] = []
    if args.resume:
        checkpoint = load_json(checkpoint_path)
        if checkpoint.get("panel_protocol_sha256") != panel_sha or checkpoint.get(
            "packet_sha256"
        ) != packet_sha or checkpoint.get("review_amendment_sha256") != amendment_sha:
            raise ValueError("Resume provenance mismatch")
        calls = list(checkpoint.get("calls") or [])
    elif checkpoint_path.exists():
        raise RuntimeError("Output directory already contains a panel checkpoint")
    complete_ids = {
        call["call_id"] for call in calls if call.get("status") == "complete"
    }
    packet_blocks = {block["block_id"]: block for block in packet["blocks"]}
    prompt_text = (REPO_ROOT / panel["prompt"]["path"]).read_text(encoding="utf-8")
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bmadx-panel-") as temp_root:
        temp = Path(temp_root)
        work_dir = temp / "workspace"
        work_dir.mkdir()
        for call in schedule:
            if call["call_id"] in complete_ids:
                continue
            block = ordered_block(panel, packet_blocks[call["block_id"]], call)
            prompt = build_prompt(prompt_text, packet, block)
            command, env = command_for_call(call, prompt)
            started = time.monotonic()
            try:
                result = subprocess.run(
                    command,
                    cwd=work_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=args.case_timeout,
                    check=False,
                )
                stdout = result.stdout
                stderr = result.stderr
                returncode = result.returncode
            except subprocess.TimeoutExpired as exc:
                stdout = (
                    exc.stdout.decode()
                    if isinstance(exc.stdout, bytes)
                    else (exc.stdout or "")
                )
                stderr = (
                    exc.stderr.decode()
                    if isinstance(exc.stderr, bytes)
                    else (exc.stderr or "")
                )
                returncode = 124
            judgment = parse_runtime_output(stdout)
            normalizations = normalize_judgment_keys(judgment)
            normalizations.extend(normalize_candidate_ids(judgment, block))
            validation = validate_judgment(judgment, block)
            record = {
                "call_id": call["call_id"],
                "lane": call["lane"],
                "reviewer_id": call["reviewer"]["reviewer_id"],
                "family": call["reviewer"]["family"],
                "model_id": call["reviewer"]["model"],
                "runtime": call["runtime"],
                "block_id": call["block_id"],
                "status": "complete"
                if returncode == 0 and validation["valid"]
                else "failed",
                "duration_seconds": round(time.monotonic() - started, 3),
                "returncode": returncode,
                "validation_errors": validation["errors"],
                "normalizations": normalizations,
                "stderr_present": bool(stderr),
                "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest(),
                "judgment": judgment,
            }
            (raw_dir / f"{call['call_id']}.stdout").write_text(
                stdout, encoding="utf-8"
            )
            (raw_dir / f"{call['call_id']}.stderr").write_text(
                "[stderr omitted; verify stderr_sha256 in panel-checkpoint.json]\n",
                encoding="utf-8",
            )
            calls = [item for item in calls if item["call_id"] != call["call_id"]]
            calls.append(record)
            checkpoint_path.write_text(
                json.dumps(
                    {
                        "schema": "bmadx_synthetic_panel_checkpoint.v1",
                        "panel_protocol_sha256": panel_sha,
                        "packet_sha256": packet_sha,
                        "review_amendment_sha256": amendment_sha,
                        "calls": calls,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            if record["status"] != "complete":
                print(json.dumps(record, indent=2))
                return 1
    summary = finalize(
        panel,
        panel_sha,
        packet,
        calls,
        output_dir,
        versions,
        amendment_sha,
        runner_sha,
    )
    (output_dir / "panel-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["complete"] and summary["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
