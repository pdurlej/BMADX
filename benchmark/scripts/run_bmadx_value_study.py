#!/usr/bin/env python3
"""Run the frozen, three-arm BMADX decision-value study."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bmadx_benchmark_validation import parse_token_count, sanitize_stderr
from bmadx_value_contract import (
    build_value_prompt,
    parse_value_response,
    validate_value_payload,
)
from run_bmadx_benchmark import (
    BENCHMARK_ROOT,
    BMADX_SKILL_ROOT,
    build_codex_command,
    model_slug,
    source_codex_home,
)
from run_sol_bmadx_ab import sha256_bytes, sha256_file, tree_sha256
from run_sol_bmadx_causal_canary import (
    ARMS,
    REAL_BMAD_SKILL,
    canary_env,
    prepare_snapshot,
    protected_hashes,
    raw_artifact_paths,
)


REPO_ROOT = BENCHMARK_ROOT.parent
DEFAULT_PROTOCOL = BENCHMARK_ROOT / "value-study" / "protocol-v1.json"
FRAMEWORK_LEAKAGE = re.compile(r"(?i)(?:\bbmadx?\b|\bX[1-4]\b|activation nonce)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--confirm-call-count", type=int)
    parser.add_argument("--case-timeout", type=int, default=180)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.case_timeout < 1:
        parser.error("--case-timeout must be >= 1")
    return args


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Value-study protocol must be a JSON object")
    return payload


def deterministic_token(seed: int, material: str, length: int) -> str:
    return hashlib.sha256(f"{seed}:{material}".encode("utf-8")).hexdigest()[:length]


def build_schedule(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    seed = int(protocol["assignment_seed"])
    blocks = [
        (scenario["id"], repeat_index)
        for scenario in protocol["scenarios"]
        for repeat_index in range(1, int(protocol["repeats"]) + 1)
    ]
    random.Random(seed).shuffle(blocks)
    schedule: list[dict[str, Any]] = []
    for scenario_id, repeat_index in blocks:
        arms = list(ARMS)
        block_seed = int(
            deterministic_token(seed, f"{scenario_id}:{repeat_index}:arms", 16), 16
        )
        random.Random(block_seed).shuffle(arms)
        for arm in arms:
            order = len(schedule) + 1
            identity = f"{order}:{scenario_id}:{repeat_index}:{arm}"
            schedule.append(
                {
                    "order": order,
                    "scenario": scenario_id,
                    "repeat_index": repeat_index,
                    "arm": arm,
                    "effort": protocol["effort"],
                    "alias": "wf-" + deterministic_token(seed, identity + ":alias", 10),
                    "nonce": deterministic_token(seed, identity + ":nonce", 32),
                }
            )
    return schedule


def scenario_path(entry: dict[str, Any]) -> Path:
    return REPO_ROOT / str(entry["path"])


def task_from_path(path: Path) -> str:
    line = next(
        (
            value
            for value in path.read_text(encoding="utf-8").splitlines()
            if value.startswith("Task:")
        ),
        "",
    )
    return line.partition("Task:")[2].strip()


def scenario_manifest_sha(protocol: dict[str, Any]) -> str:
    material = "".join(
        f"{entry['id']}:{entry['sha256']}\n" for entry in protocol["scenarios"]
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def load_scenario_audit(protocol: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / protocol["scenario_audit"]["path"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def validate_protocol(
    protocol: dict[str, Any], protocol_path: Path, *, require_audit: bool = False
) -> list[dict[str, Any]]:
    if protocol.get("schema") != "bmadx_value_study.v1":
        raise ValueError("Unsupported value-study schema")
    if protocol.get("model") != "gpt-5.6-sol" or protocol.get("effort") != "high":
        raise ValueError("The v1 value study is frozen to gpt-5.6-sol/high")
    if protocol.get("arms") != list(ARMS):
        raise ValueError("The value-study arm order is not frozen")
    if protocol.get("quality_failures_are_outcomes") is not True:
        raise ValueError("Quality failures must remain outcomes, not integrity stops")
    if protocol.get("integrity_stop_conditions") != [
        "activation_failure",
        "cross_arm_nonce",
        "source_or_provenance_mismatch",
        "protected_filesystem_mutation",
        "transport_failure",
    ]:
        raise ValueError("Integrity stop conditions are not frozen")
    scenarios = protocol.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) < 12:
        raise ValueError(
            "At least 12 independently reviewable scenario clusters are required"
        )
    scenario_ids = [entry.get("id") for entry in scenarios]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("Scenario IDs must be unique")
    for entry in scenarios:
        path = scenario_path(entry)
        if not path.is_file() or sha256_file(path) != entry.get("sha256"):
            raise ValueError(f"Scenario hash mismatch: {entry.get('id')}")
        if not task_from_path(path):
            raise ValueError(f"Scenario has no Task line: {entry.get('id')}")
    manifest_sha = scenario_manifest_sha(protocol)
    if manifest_sha != protocol.get("scenario_manifest_sha256"):
        raise ValueError("Scenario manifest hash mismatch")
    audit = load_scenario_audit(protocol)
    if (
        audit.get("schema") != "bmadx_value_scenario_audit.v1"
        or audit.get("scenario_manifest_sha256") != manifest_sha
    ):
        raise ValueError("Scenario audit does not match the frozen scenario manifest")
    if require_audit and not (
        audit.get("status") == "approved_before_live_run"
        and audit.get("independent_of_bmadx_authorship") is True
        and audit.get("completed_before_live_run") is True
        and isinstance(audit.get("reviewer_id"), str)
        and bool(audit["reviewer_id"].strip())
    ):
        raise ValueError(
            "Independent scenario audit is not approved for live execution"
        )
    rubric = protocol.get("rubric") or {}
    rubric_path = REPO_ROOT / str(rubric.get("path") or "")
    if not rubric_path.is_file() or sha256_file(rubric_path) != rubric.get("sha256"):
        raise ValueError("Review rubric hash mismatch")
    response_schema = protocol.get("response_schema") or {}
    response_schema_path = REPO_ROOT / str(response_schema.get("path") or "")
    if (
        not response_schema_path.is_file()
        or sha256_file(response_schema_path) != response_schema.get("sha256")
    ):
        raise ValueError("Value-response schema hash mismatch")
    review_policy = protocol.get("review_policy") or {}
    synthetic_panel = review_policy.get("synthetic_panel") or {}
    synthetic_panel_path = REPO_ROOT / str(synthetic_panel.get("path") or "")
    required_reviewers = review_policy.get("required_reviewer_ids") or []
    synthetic_panel_payload = (
        json.loads(synthetic_panel_path.read_text(encoding="utf-8"))
        if synthetic_panel_path.is_file()
        else {}
    )
    panel_reviewers = [
        entry.get("reviewer_id")
        for entry in synthetic_panel_payload.get("reviewers") or []
    ]
    if (
        review_policy.get("mode") != "synthetic_model_panel"
        or review_policy.get("minimum_reviewers") != 5
        or review_policy.get("minimum_independent_reviewers") != 5
        or len(required_reviewers) != 5
        or len(set(required_reviewers)) != 5
        or panel_reviewers != required_reviewers
        or synthetic_panel.get("health_required_for_positive_claim") is not True
        or not synthetic_panel_path.is_file()
        or sha256_file(synthetic_panel_path) != synthetic_panel.get("sha256")
    ):
        raise ValueError("Synthetic review policy is not frozen")
    schedule = build_schedule(protocol)
    expected = len(scenarios) * len(ARMS) * int(protocol["repeats"])
    if len(schedule) != expected or protocol.get("expected_call_count") != expected:
        raise ValueError("Expected call count does not match the complete schedule")
    if len({item["alias"] for item in schedule}) != expected:
        raise ValueError("Generated aliases are not unique")
    if len({item["nonce"] for item in schedule}) != expected:
        raise ValueError("Generated nonces are not unique")

    sources = protocol.get("source_hashes") or {}
    if tree_sha256(BMADX_SKILL_ROOT, exclude_runtime_state=True) != sources.get(
        "bmadx_tree_sha256"
    ):
        raise ValueError("BMADX source tree hash mismatch")
    real_bmad = source_codex_home() / "skills" / REAL_BMAD_SKILL
    if tree_sha256(real_bmad, exclude_runtime_state=True) != sources.get(
        "real_bmad_tree_sha256"
    ):
        raise ValueError("Real BMAD source tree hash mismatch")
    if not str(sources.get("real_bmad_release_tag", "")).startswith("v"):
        raise ValueError("Real BMAD release tag is not frozen")

    harness_files = {
        "runner_sha256": Path(__file__),
        "contract_sha256": Path(__file__).with_name("bmadx_value_contract.py"),
        "runtime_helpers_sha256": Path(__file__).with_name(
            "run_sol_bmadx_causal_canary.py"
        ),
        "review_builder_sha256": Path(__file__).with_name(
            "build_bmadx_value_review_packet.py"
        ),
        "analyzer_sha256": Path(__file__).with_name("analyze_bmadx_value_study.py"),
        "synthetic_panel_runner_sha256": Path(__file__).with_name(
            "run_bmadx_synthetic_review_panel.py"
        ),
    }
    for key, path in harness_files.items():
        if sha256_file(path) != (protocol.get("harness_hashes") or {}).get(key):
            raise ValueError(f"Harness hash mismatch: {path.name}")
    tracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            str(protocol_path.relative_to(REPO_ROOT)),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode != 0:
        raise ValueError("Frozen protocol must be tracked by git")
    return schedule


def run_id(protocol: dict[str, Any]) -> str:
    return f"{protocol['protocol_id']}-{model_slug(protocol['model'])}"


def run_root(protocol: dict[str, Any]) -> Path:
    return BENCHMARK_ROOT / "value-study" / "runs" / run_id(protocol)


def case_id(protocol: dict[str, Any], item: dict[str, Any]) -> str:
    return (
        f"{run_id(protocol)}-o{item['order']:03d}-r{item['repeat_index']}"
        f"-{item['arm']}-{item['scenario']}"
    )


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed")
    return result.stdout.strip()


def assert_checkout(run_dir: Path, resume: bool) -> dict[str, Any]:
    status_lines = [
        line for line in git_output("status", "--porcelain").splitlines() if line
    ]
    if resume:
        allowed = f"?? {run_dir.relative_to(REPO_ROOT)}/"
        unexpected = [line for line in status_lines if line != allowed]
        if unexpected:
            raise RuntimeError(
                "Resume checkout contains changes outside the study run directory"
            )
    elif status_lines:
        raise RuntimeError("Value study must start from a clean checkout")
    codex_version = subprocess.run(
        ["codex", "--version"], capture_output=True, text=True, check=False
    )
    if codex_version.returncode != 0:
        raise RuntimeError("Could not read Codex CLI version")
    return {
        "git_sha": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "dirty_at_start": bool(status_lines),
        "resume": resume,
        "codex_cli": codex_version.stdout.strip(),
    }


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(f"{path}.tmp")
    temporary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_case(
    protocol: dict[str, Any],
    item: dict[str, Any],
    scenario: dict[str, Any],
    known_nonces: set[str],
    raw_dir: Path,
    timeout: int,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix=f"bmadx-value-{item['order']:03d}-"
    ) as tmpdir:
        root = Path(tmpdir)
        prepared, setup = prepare_snapshot(root, item, protocol)
        home = root / "runtime-home"
        workdir = root / "workspace"
        shutil.copytree(prepared, home)
        workdir.mkdir()
        task = task_from_path(scenario_path(scenario))
        prompt = build_value_prompt(task, item["alias"])
        command = build_codex_command(
            prompt,
            workdir,
            home,
            model=protocol["model"],
            reasoning=protocol["effort"],
        )
        response_schema_path = REPO_ROOT / protocol["response_schema"]["path"]
        command[-1:-1] = ["--output-schema", str(response_schema_path)]
        protected_before = protected_hashes(home, workdir, item["alias"])
        home_before = tree_sha256(home)
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=canary_env(
                    home,
                    home / "healthy-bmad-release.json"
                    if item["arm"] != "placebo"
                    else None,
                ),
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"codex exec timed out after {timeout}s") from exc
        duration = time.perf_counter() - started
        stdout = result.stdout.rstrip() + "\n"
        stderr = sanitize_stderr(result.stderr.rstrip()) + "\n"
        stem = case_id(protocol, item)
        raw_txt, raw_log = raw_artifact_paths(str(raw_dir / stem))
        raw_txt.parent.mkdir(parents=True, exist_ok=True)
        raw_txt.write_text(stdout, encoding="utf-8")
        raw_log.write_text(stdout + "\n--- STDERR ---\n" + stderr, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"codex exec failed for {stem}: {stderr.strip()}")
        tokens = parse_token_count(stderr)
        if tokens is None:
            raise RuntimeError(f"codex exec did not report token usage for {stem}")
        payload = parse_value_response(stdout)
        contract = validate_value_payload(payload, item["nonce"])
        observed_nonce = (payload or {}).get("activation_nonce")
        cross_arm_nonce = (
            isinstance(observed_nonce, str)
            and observed_nonce in known_nonces
            and observed_nonce != item["nonce"]
        )
        protected_after = protected_hashes(home, workdir, item["alias"])
        payload_text = json.dumps(payload or {}, sort_keys=True)
        return {
            "case_id": stem,
            **item,
            "model": protocol["model"],
            "started_at": started_at,
            "duration_seconds": round(duration, 3),
            "tokens": tokens,
            "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
            "scenario_sha256": sha256_file(scenario_path(scenario)),
            "response_sha256": sha256_bytes(stdout.encode("utf-8")),
            "response_payload": payload,
            "framework_leakage_detected": bool(FRAMEWORK_LEAKAGE.search(payload_text)),
            "cross_arm_nonce": cross_arm_nonce,
            "protected_sha256_before": protected_before,
            "protected_sha256_after": protected_after,
            "protected_filesystem_mutation": protected_before != protected_after,
            "runtime_home_bookkeeping_mutation": home_before != tree_sha256(home),
            "setup": setup,
            **contract,
            "raw_txt": str(raw_txt.relative_to(REPO_ROOT)),
            "raw_log": str(raw_log.relative_to(REPO_ROOT)),
        }


def integrity_stop(case: dict[str, Any]) -> str | None:
    if not case["activation_pass"]:
        return "activation_failure"
    if case["cross_arm_nonce"]:
        return "cross_arm_nonce"
    if case["protected_filesystem_mutation"]:
        return "protected_filesystem_mutation"
    return None


def load_resume(
    summary_path: Path, protocol_sha: str, provenance: dict[str, Any]
) -> dict[str, Any]:
    previous = json.loads(summary_path.read_text(encoding="utf-8"))
    if previous.get("protocol_sha256") != protocol_sha:
        raise RuntimeError("Resume protocol hash mismatch")
    if (previous.get("runtime_provenance") or {}).get("git_sha") != provenance[
        "git_sha"
    ]:
        raise RuntimeError("Resume git SHA mismatch")
    if previous.get("status") == "stopped":
        raise RuntimeError("Integrity-stopped studies cannot be resumed")
    if previous.get("complete") is True:
        raise RuntimeError("Completed studies cannot be resumed")
    return previous


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path = args.protocol.resolve()
    protocol = load_protocol(protocol_path)
    if args.case_timeout != int(protocol["case_timeout_seconds"]):
        raise SystemExit(
            f"Refusing timeout drift: use --case-timeout {protocol['case_timeout_seconds']}"
        )
    schedule = validate_protocol(
        protocol, protocol_path, require_audit=not args.validate_only
    )
    if args.validate_only:
        audit = load_scenario_audit(protocol)
        audit_approved = (
            audit.get("status") == "approved_before_live_run"
            and audit.get("independent_of_bmadx_authorship") is True
            and audit.get("completed_before_live_run") is True
        )
        print(
            json.dumps(
                {
                    "protocol_id": protocol["protocol_id"],
                    "protocol_sha256": sha256_file(protocol_path),
                    "scenario_count": len(protocol["scenarios"]),
                    "repeat_count": protocol["repeats"],
                    "call_count": len(schedule),
                    "scenario_audit_status": audit.get("status"),
                    "status": (
                        "ready_for_live_run"
                        if audit_approved
                        else "valid_but_live_run_requires_approved_scenario_audit"
                    ),
                },
                indent=2,
            )
        )
        return 0
    if args.confirm_call_count != len(schedule):
        raise SystemExit(
            f"Refusing live run: pass --confirm-call-count {len(schedule)}"
        )
    scenarios = {entry["id"]: entry for entry in protocol["scenarios"]}
    root = run_root(protocol)
    summary_path = root / "summary.json"
    provenance = assert_checkout(root, args.resume)
    protocol_sha = sha256_file(protocol_path)
    previous = (
        load_resume(summary_path, protocol_sha, provenance) if args.resume else None
    )
    cases = list((previous or {}).get("cases") or [])
    completed_ids = {case["case_id"] for case in cases}
    known_nonces = {item["nonce"] for item in schedule}
    run_segments = list((previous or {}).get("run_segments") or [])
    run_segments.append(
        {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "resume": args.resume,
            "completed_before": len(cases),
            "completed_after": len(cases),
            "checkout": provenance,
        }
    )
    summary = {
        "schema": "bmadx_value_study_result.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": protocol_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "complete": False,
        "expected_call_count": len(schedule),
        "completed_call_count": len(cases),
        "stop_reason": None,
        "runtime_provenance": (previous or {}).get("runtime_provenance") or provenance,
        "source_hashes": protocol["source_hashes"],
        "harness_hashes": protocol["harness_hashes"],
        "run_segments": run_segments,
        "cases": cases,
    }
    write_summary(summary_path, summary)
    try:
        for item in schedule:
            expected_id = case_id(protocol, item)
            if expected_id in completed_ids:
                continue
            case = run_case(
                protocol,
                item,
                scenarios[item["scenario"]],
                known_nonces,
                root / "raw",
                args.case_timeout,
            )
            cases.append(case)
            summary["completed_call_count"] = len(cases)
            run_segments[-1]["completed_after"] = len(cases)
            reason = integrity_stop(case)
            if reason:
                summary["status"] = "stopped"
                summary["stop_reason"] = reason
                run_segments[-1]["ended_at"] = datetime.now(timezone.utc).isoformat()
                write_summary(summary_path, summary)
                print(
                    json.dumps(
                        {
                            "summary": str(summary_path.relative_to(REPO_ROOT)),
                            "status": "stopped",
                            "reason": reason,
                        },
                        indent=2,
                    )
                )
                return 2
            write_summary(summary_path, summary)
    except Exception as exc:
        summary["status"] = "failed"
        summary["stop_reason"] = f"transport_or_runtime_failure: {exc}"
        run_segments[-1]["ended_at"] = datetime.now(timezone.utc).isoformat()
        write_summary(summary_path, summary)
        print(
            json.dumps(
                {
                    "summary": str(summary_path.relative_to(REPO_ROOT)),
                    "status": "failed",
                    "reason": str(exc),
                },
                indent=2,
            )
        )
        return 1
    summary["status"] = "complete"
    summary["complete"] = True
    run_segments[-1]["ended_at"] = datetime.now(timezone.utc).isoformat()
    write_summary(summary_path, summary)
    print(
        json.dumps(
            {
                "summary": str(summary_path.relative_to(REPO_ROOT)),
                "status": "complete",
                "cases": len(cases),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
