#!/usr/bin/env python3
"""Run a matched, framework-neutral Sol plain-vs-BMADX benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from bmadx_benchmark_scenarios import (
    BOUNDARY_SCENARIOS,
    CORE_SCENARIOS,
    GOAL_LOOP_SCENARIOS,
    HANDOFF_SCENARIOS,
    NON_TECH_SCENARIOS,
)
from bmadx_benchmark_validation import parse_token_count, sanitize_stderr
from run_bmadx_benchmark import (
    BENCHMARK_ROOT,
    RAW_ROOT,
    benchmark_env,
    build_codex_command,
    copy_runtime_files,
    copy_skills,
    model_slug,
    repo_relative,
    warmup_profile,
    write_config,
    write_healthy_bmad_fixture,
)
from sol_bmadx_ab_contract import build_neutral_prompt, score_neutral_response, task_from_scenario


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_EFFORTS = ("medium", "high", "xhigh")
DEFAULT_ARMS = ("plain", "bmadx")
DEFAULT_CASE_TIMEOUT = 180
BMAD_ENV_KEYS = ("BMAD_RELEASE_API", "BMAD_RAW_BASE", "BMAD_MAX_RETRIES")


def all_scenarios() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for group in (
        CORE_SCENARIOS,
        BOUNDARY_SCENARIOS,
        NON_TECH_SCENARIOS,
        HANDOFF_SCENARIOS,
        GOAL_LOOP_SCENARIOS,
    ):
        merged.update(group)
    merged = {
        scenario: {
            **spec,
            "expected_handoff": spec.get("expected_handoff", False),
            "expected_goal": spec.get("expected_goal", False),
            "expected_loop": spec.get("expected_loop", False),
        }
        for scenario, spec in merged.items()
    }
    expected_risks = {
        "x1": "low",
        "x2": "moderate",
        "x3": "moderate",
        "x4": "high",
        "x2x3-boundary": "moderate",
        "pricing-copy": "low",
        "onboarding-email": "low",
        "google-login": "high",
        "subscription-billing": "high",
        "delete-inactive-users": "high",
        "messy-migration-incident": "critical",
        "x3-auth-review-handoff": "high",
        "x4-migration-review-handoff": "critical",
        "goal-x3-auth-cleanup": "high",
        "loop-x4-migration-repair": "critical",
    }
    for scenario, expected_risk in expected_risks.items():
        merged[scenario] = dict(merged[scenario], expected_risk=expected_risk)
    return merged


def comma_choices(raw: str, allowed: tuple[str, ...], label: str) -> list[str]:
    values = [value.strip() for value in raw.split(",") if value.strip()]
    unknown = sorted(set(values) - set(allowed))
    if unknown:
        raise argparse.ArgumentTypeError(f"Unknown {label}: {', '.join(unknown)}")
    return values or list(allowed)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--efforts", default=",".join(DEFAULT_EFFORTS))
    parser.add_argument("--arms", default=",".join(DEFAULT_ARMS))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--seed", type=int, default=560712)
    parser.add_argument("--date-stamp", default=str(date.today()))
    parser.add_argument("--run-label", default="neutral-v2")
    parser.add_argument("--case-timeout", type=int, default=DEFAULT_CASE_TIMEOUT)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        args.efforts = comma_choices(args.efforts, DEFAULT_EFFORTS, "efforts")
        args.arms = comma_choices(args.arms, DEFAULT_ARMS, "arms")
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if args.repeat < 1:
        parser.error("--repeat must be >= 1")
    if args.case_timeout < 1:
        parser.error("--case-timeout must be >= 1")
    if not args.run_label.replace("-", "").replace("_", "").isalnum():
        parser.error("--run-label must contain only letters, digits, hyphens, or underscores")
    return args


def build_schedule(
    scenarios: dict[str, dict], arms: list[str], efforts: list[str], repeat: int, seed: int
) -> list[dict]:
    schedule = [
        {"arm": arm, "effort": effort, "repeat_index": repeat_index, "scenario": scenario}
        for repeat_index in range(1, repeat + 1)
        for scenario in scenarios
        for effort in efforts
        for arm in arms
    ]
    random.Random(seed).shuffle(schedule)
    return schedule


def artifact_stem(
    run_label: str,
    item: dict,
    *,
    model: str | None = None,
    date_stamp: str | None = None,
    seed: int | None = None,
) -> str:
    provenance = ""
    if model and date_stamp and seed is not None:
        provenance = f"-{model_slug(model)}-{date_stamp}-s{seed}"
    return (
        f"sol-ab{provenance}-{run_label}-{item['arm']}-{item['effort']}"
        f"-r{item['repeat_index']}-{item['scenario']}"
    )


def summary_path(date_stamp: str, run_label: str, model: str = DEFAULT_MODEL) -> Path:
    return BENCHMARK_ROOT / f"ab-summary-{date_stamp}-{model_slug(model)}-{run_label}.json"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def tree_sha256(root: Path, *, exclude_runtime_state: bool = False) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = path.relative_to(root)
        if path.name == "auth.json":
            continue
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if exclude_runtime_state and "state" in relative.parts:
            continue
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def ab_env(home: Path, arm: str, fixture: Path | None) -> dict[str, str]:
    env = benchmark_env(home, "healthy")
    for key in BMAD_ENV_KEYS:
        env.pop(key, None)
    if arm == "bmadx":
        if fixture is None:
            raise RuntimeError("BMADX treatment requires a pinned healthy fixture")
        env["BMAD_RELEASE_API"] = fixture.resolve().as_uri()
        env["BMAD_MAX_RETRIES"] = "0"
    return env


def scenario_manifest(scenarios: dict[str, dict]) -> dict:
    return {
        key: {
            "sha256": sha256_file(Path(spec["path"])),
            "expected_process_gear": spec["expected_gear"],
            "expected_risk": spec["expected_risk"],
            "expected_handoff": spec["expected_handoff"],
            "expected_goal": spec["expected_goal"],
            "expected_loop": spec["expected_loop"],
        }
        for key, spec in sorted(scenarios.items())
    }


def experiment_manifest(args: argparse.Namespace, scenarios: dict[str, dict]) -> dict:
    payload = {
        "schema": "sol_bmadx_ab.v2",
        "model": args.model,
        "arms": args.arms,
        "efforts": args.efforts,
        "repeat": args.repeat,
        "seed": args.seed,
        "date_stamp": args.date_stamp,
        "run_label": args.run_label,
        "case_timeout": args.case_timeout,
        "scenarios": scenario_manifest(scenarios),
        "contract_sha256": sha256_file(Path(__file__).with_name("sol_bmadx_ab_contract.py")),
        "runner_sha256": sha256_file(Path(__file__)),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"sha256": sha256_bytes(encoded), "payload": payload}


def setup_home(root: Path, arm: str, model: str) -> Path:
    home = root / f"codex-home-{arm}"
    write_config(home, model, DEFAULT_EFFORTS[0])
    copy_runtime_files(home)
    if arm == "bmadx":
        copy_skills(home)
        if not (home / "skills" / "bmadx" / "SKILL.md").is_file():
            raise RuntimeError("BMADX treatment home is missing skills/bmadx/SKILL.md")
    elif (home / "skills").exists():
        raise RuntimeError("Plain control home unexpectedly contains skills")
    return home


def cell_summary(cases: list[dict]) -> dict:
    count = len(cases)
    return {
        "case_count": count,
        "primary_pass_count": sum(case["primary_pass"] for case in cases),
        "primary_score": sum(case["primary_score"] for case in cases),
        "primary_max": sum(case["primary_max"] for case in cases),
        "ordinal_underclassification_count": sum(
            case["ordinal_underclassification"] for case in cases
        ),
        "overescalation_count": sum(case["overescalation"] for case in cases),
        "process_pass_count": sum(case["process_pass"] for case in cases),
        "risk_pass_count": sum(case["risk_pass"] for case in cases),
        "handoff_applicable_count": sum(case["handoff_applicable"] for case in cases),
        "handoff_pass_count": sum(
            case["handoff_pass"] for case in cases if case["handoff_applicable"]
        ),
        "goal_applicable_count": sum(case["goal_applicable"] for case in cases),
        "goal_pass_count": sum(case["goal_pass"] for case in cases if case["goal_applicable"]),
        "loop_applicable_count": sum(case["loop_applicable"] for case in cases),
        "loop_pass_count": sum(case["loop_pass"] for case in cases if case["loop_applicable"]),
        "total_tokens": sum(case["tokens"] for case in cases),
        "avg_tokens": sum(case["tokens"] for case in cases) / count if count else 0,
        "avg_duration_seconds": sum(case["duration_seconds"] for case in cases) / count if count else 0,
    }


def build_summary(
    args: argparse.Namespace,
    schedule: list[dict],
    cases: list[dict],
    complete: bool,
    manifest: dict,
    provenance: dict,
    segments: list[dict],
) -> dict:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for case in cases:
        grouped[(case["arm"], case["effort"])].append(case)
    return {
        "generated_at": args.date_stamp,
        "experiment": "plain-sol-vs-bmadx-pinned-healthy-neutral-v2",
        "experiment_manifest": manifest,
        "complete": complete,
        "runner": {
            "model": args.model,
            "arms": args.arms,
            "efforts": args.efforts,
            "repeat": args.repeat,
            "seed": args.seed,
            "run_label": args.run_label,
            "schedule_case_count": len(schedule),
            "completed_case_count": len(cases),
            "order": "deterministic shuffled interleaving",
            "run_segments": segments,
        },
        "runtime_provenance": provenance,
        "primary_contract": {
            "framework_neutral": True,
            "bmadx_labels_exposed": False,
            "plain_skill_loaded": False,
            "bmad_dependency": "pinned healthy fixture in every BMADX model-call environment",
            "treatment_setup_verified": "BMADX SKILL.md present; plain skills directory absent",
            "skill_injection_log_note": "Codex does not expose hidden skill injection as a shell read event",
            "score_max_per_case": 7,
            "score_note": "fixed denominator; goal and loop each combine decision plus contract",
        },
        "cells": {
            f"{arm}-{effort}": cell_summary(grouped[(arm, effort)])
            for effort in args.efforts
            for arm in args.arms
        },
        "cases": cases,
    }


def expected_case_ids(args: argparse.Namespace, schedule: list[dict]) -> set[str]:
    return {
        artifact_stem(
            args.run_label,
            item,
            model=args.model,
            date_stamp=args.date_stamp,
            seed=args.seed,
        )
        for item in schedule
    }


def write_checkpoint(
    path: Path,
    args: argparse.Namespace,
    schedule: list[dict],
    cases: list[dict],
    manifest: dict,
    provenance: dict,
    segments: list[dict],
) -> None:
    case_ids = [case["case_id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("Checkpoint contains duplicate case IDs")
    expected_ids = expected_case_ids(args, schedule)
    if not set(case_ids).issubset(expected_ids):
        raise RuntimeError("Checkpoint contains case IDs outside the experiment manifest")
    complete = set(case_ids) == expected_ids
    payload = build_summary(args, schedule, cases, complete, manifest, provenance, segments)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_case(
    item: dict,
    spec: dict,
    home: Path,
    workdir: Path,
    fixture: Path | None,
    args: argparse.Namespace,
) -> dict:
    scenario_path = Path(spec["path"])
    task = task_from_scenario(scenario_path.read_text(encoding="utf-8"))
    prompt = build_neutral_prompt(task, item["arm"])
    command = build_codex_command(
        prompt,
        workdir,
        home,
        model=args.model,
        reasoning=item["effort"],
    )
    home_before = tree_sha256(home)
    workspace_before = tree_sha256(workdir)
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=ab_env(home, item["arm"], fixture),
            check=False,
            timeout=args.case_timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"codex exec timed out after {args.case_timeout}s") from exc
    duration = time.perf_counter() - started
    stdout = result.stdout.rstrip() + "\n"
    stderr = sanitize_stderr(result.stderr.rstrip()) + "\n"
    case_id = artifact_stem(
        args.run_label,
        item,
        model=args.model,
        date_stamp=args.date_stamp,
        seed=args.seed,
    )
    raw_base = RAW_ROOT / case_id
    raw_base.with_suffix(".txt").write_text(stdout, encoding="utf-8")
    raw_base.with_suffix(".log").write_text(stdout + "\n--- STDERR ---\n" + stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"codex exec failed for {case_id}: {stderr.strip()}")
    tokens = parse_token_count(stderr)
    if tokens is None:
        raise RuntimeError(f"codex exec did not report token usage for {case_id}")
    score = score_neutral_response(stdout, spec)
    return {
        "case_id": case_id,
        **item,
        "model": args.model,
        "tokens": tokens,
        "duration_seconds": round(duration, 3),
        "started_at": started_at,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "scenario_sha256": sha256_file(scenario_path),
        "home_sha256_before": home_before,
        "home_sha256_after": tree_sha256(home),
        "workspace_sha256_before": workspace_before,
        "workspace_sha256_after": tree_sha256(workdir),
        "filesystem_mutation_detected": (
            home_before != tree_sha256(home) or workspace_before != tree_sha256(workdir)
        ),
        **score,
        "raw_txt": repo_relative(raw_base.with_suffix(".txt")),
        "raw_log": repo_relative(raw_base.with_suffix(".log")),
    }


def main() -> int:
    args = parse_args()
    scenarios = all_scenarios()
    schedule = build_schedule(scenarios, args.arms, args.efforts, args.repeat, args.seed)
    manifest = experiment_manifest(args, scenarios)
    output_path = summary_path(args.date_stamp, args.run_label, args.model)
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    cases: list[dict] = []
    segments: list[dict] = []
    previous_provenance: dict | None = None
    if args.resume and output_path.exists():
        previous = json.loads(output_path.read_text(encoding="utf-8"))
        previous_manifest = (previous.get("experiment_manifest") or {}).get("sha256")
        if previous_manifest != manifest["sha256"]:
            raise RuntimeError("Resume manifest mismatch; use a new run label for a changed experiment")
        cases = list(previous.get("cases") or [])
        segments = list((previous.get("runner") or {}).get("run_segments") or [])
        previous_provenance = previous.get("runtime_provenance") or {}
    case_ids = [case["case_id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("Resume summary contains duplicate case IDs")
    if not set(case_ids).issubset(expected_case_ids(args, schedule)):
        raise RuntimeError("Resume summary contains cases outside the current manifest")
    completed = {case["case_id"] for case in cases}

    with tempfile.TemporaryDirectory(prefix="bmadx-sol-ab-") as tmpdir:
        root = Path(tmpdir)
        homes_root = root / "base-homes"
        homes_root.mkdir()
        homes = {arm: setup_home(homes_root, arm, args.model) for arm in args.arms}
        fixture: Path | None = None
        warmup_payload: dict = {}
        if "bmadx" in homes:
            fixture = write_healthy_bmad_fixture(root)
            warmup_payload = warmup_profile(homes["bmadx"], "healthy", fixture)
        codex_version = subprocess.run(
            ["codex", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        ).stdout.strip()
        provenance = {
            "codex_version": codex_version,
            "fixture_sha256": sha256_file(fixture) if fixture else None,
            "bmadx_tree_sha256": (
                tree_sha256(
                    homes["bmadx"] / "skills" / "bmadx", exclude_runtime_state=True
                )
                if "bmadx" in homes
                else None
            ),
            "bmad_tree_sha256": (
                tree_sha256(
                    homes["bmadx"] / "skills" / "bmad-method-codex",
                    exclude_runtime_state=True,
                )
                if "bmadx" in homes
                else None
            ),
            "warmup": {
                "action": warmup_payload.get("action"),
                "dependency_healthy": bool(
                    (warmup_payload.get("bmad_dependency") or {}).get("healthy")
                ),
                "dependency_tag": (warmup_payload.get("bmad_dependency") or {}).get("tag_name"),
            },
        }
        if previous_provenance and previous_provenance != provenance:
            raise RuntimeError("Resume runtime provenance mismatch; do not mix environments")
        segment_started = datetime.now(timezone.utc).isoformat()
        segments.append(
            {
                "segment": len(segments) + 1,
                "started_at": segment_started,
                "completed_before": len(cases),
                "manifest_sha256": manifest["sha256"],
            }
        )
        for index, item in enumerate(schedule, start=1):
            case_id = artifact_stem(
                args.run_label,
                item,
                model=args.model,
                date_stamp=args.date_stamp,
                seed=args.seed,
            )
            if case_id in completed:
                continue
            print(f"[{index}/{len(schedule)}] {item['arm']} {item['effort']} {item['scenario']}", flush=True)
            case_root = root / "cases" / case_id
            call_home = case_root / "codex-home"
            workdir = case_root / "workspace"
            shutil.copytree(homes[item["arm"]], call_home)
            workdir.mkdir(parents=True)
            call_fixture = None
            if item["arm"] == "bmadx" and fixture is not None:
                call_fixture = call_home / "benchmark-healthy-bmad-release.json"
                shutil.copy2(fixture, call_fixture)
            cases.append(
                run_case(
                    item,
                    scenarios[item["scenario"]],
                    call_home,
                    workdir,
                    call_fixture,
                    args,
                )
            )
            segments[-1]["completed_after"] = len(cases)
            write_checkpoint(output_path, args, schedule, cases, manifest, provenance, segments)

        segments[-1]["completed_after"] = len(cases)
        segments[-1]["ended_at"] = datetime.now(timezone.utc).isoformat()

    write_checkpoint(output_path, args, schedule, cases, manifest, provenance, segments)
    print(json.dumps({"summary_path": repo_relative(output_path), "cases": len(cases)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
