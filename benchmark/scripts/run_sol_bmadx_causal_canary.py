#!/usr/bin/env python3
"""Run the frozen three-arm Sol/BMADX causal canary protocol."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bmadx_benchmark_validation import parse_token_count, sanitize_stderr
from run_bmadx_benchmark import (
    BENCHMARK_ROOT,
    RAW_ROOT,
    BMADX_SKILL_ROOT,
    build_codex_command,
    copy_runtime_files,
    model_slug,
    repo_relative,
    source_codex_home,
    write_config,
    write_healthy_bmad_fixture,
)
from run_sol_bmadx_ab import (
    BMAD_ENV_KEYS,
    all_scenarios,
    sha256_bytes,
    sha256_file,
    tree_sha256,
)
from sol_bmadx_ab_contract import build_causal_prompt, score_causal_response, task_from_scenario


DEFAULT_PROTOCOL = BENCHMARK_ROOT / "protocols" / "sol-bmadx-causal-canary-v1.2.json"
REAL_BMAD_SKILL = "bmad-method-codex"
ARMS = ("placebo", "bmadx_stub", "bmadx_real")
STUB_REFERENCES = (
    "docs_reference_workflow_map.md",
    "docs_reference_commands.md",
    "docs_reference_agents.md",
    "docs_reference_modules.md",
    "latest-release-summary.md",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--case-timeout", type=int, default=180)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Development-only escape hatch; frozen canary runs must start clean.",
    )
    args = parser.parse_args(argv)
    if args.case_timeout < 1:
        parser.error("--case-timeout must be >= 1")
    return args


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Protocol must be a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any], scenarios: dict[str, dict]) -> None:
    if protocol.get("schema") != "sol_bmadx_causal_canary.v1.2":
        raise ValueError("Unsupported causal canary protocol schema")
    if protocol.get("model") != "gpt-5.6-sol" or protocol.get("effort") != "high":
        raise ValueError("Canary model and effort must remain frozen at gpt-5.6-sol/high")
    if protocol.get("filesystem_mutation_scope") != [
        "workspace",
        "assigned_skill",
        "bmad_dependency",
    ]:
        raise ValueError("Canary filesystem mutation scope is not frozen")
    if protocol.get("schedule") != "scenario-stratified arm shuffle; safety-critical placebo last":
        raise ValueError("Canary schedule policy is not frozen")
    assignments = protocol.get("assignments")
    if not isinstance(assignments, list) or len(assignments) != protocol.get("expected_call_count"):
        raise ValueError("Assignment count does not match expected_call_count")
    expected_orders = list(range(1, len(assignments) + 1))
    if [item.get("order") for item in assignments] != expected_orders:
        raise ValueError("Assignments must be ordered consecutively")
    aliases = [item.get("alias") for item in assignments]
    nonces = [item.get("nonce") for item in assignments]
    if len(set(aliases)) != len(aliases) or not all(isinstance(value, str) for value in aliases):
        raise ValueError("Every assignment needs a unique string alias")
    if len(set(nonces)) != len(nonces) or not all(
        isinstance(value, str) and len(value) == 32 for value in nonces
    ):
        raise ValueError("Every assignment needs a unique 128-bit hexadecimal nonce")
    try:
        if any(int(value, 16) < 0 for value in nonces):
            raise ValueError
    except ValueError as exc:
        raise ValueError("Every nonce must be hexadecimal") from exc

    scenario_protocol = protocol.get("scenarios")
    if not isinstance(scenario_protocol, dict):
        raise ValueError("Protocol scenarios are missing")
    expected_cells = {
        (arm, scenario) for arm in ARMS for scenario in scenario_protocol
    }
    observed_cells = {(item.get("arm"), item.get("scenario")) for item in assignments}
    if observed_cells != expected_cells or len(assignments) != len(expected_cells):
        raise ValueError("Assignments must contain exactly one complete arm-by-scenario matrix")
    for item in assignments:
        if item.get("effort") != protocol["effort"] or item.get("repeat_index") != 1:
            raise ValueError("Assignment effort and repeat index must match the frozen protocol")
    for scenario, metadata in scenario_protocol.items():
        if metadata.get("safety_critical"):
            scenario_arms = [
                item["arm"]
                for item in assignments
                if item.get("scenario") == scenario
            ]
            if scenario_arms[-1:] != ["placebo"]:
                raise ValueError(f"Safety-critical placebo must run last: {scenario}")
    for scenario, metadata in scenario_protocol.items():
        if scenario not in scenarios:
            raise ValueError(f"Unknown protocol scenario: {scenario}")
        if sha256_file(Path(scenarios[scenario]["path"])) != metadata.get("sha256"):
            raise ValueError(f"Scenario hash mismatch: {scenario}")

    source_hashes = protocol.get("source_hashes") or {}
    if not isinstance(source_hashes.get("real_bmad_release_tag"), str) or not source_hashes[
        "real_bmad_release_tag"
    ].startswith("v"):
        raise ValueError("Real BMAD release tag is not frozen")
    if tree_sha256(BMADX_SKILL_ROOT, exclude_runtime_state=True) != source_hashes.get(
        "bmadx_tree_sha256"
    ):
        raise ValueError("BMADX source tree hash does not match the frozen protocol")
    real_bmad = source_codex_home() / "skills" / REAL_BMAD_SKILL
    if tree_sha256(real_bmad, exclude_runtime_state=True) != source_hashes.get(
        "real_bmad_tree_sha256"
    ):
        raise ValueError("Real BMAD source tree hash does not match the frozen protocol")
    harness_hashes = protocol.get("harness_hashes") or {}
    harness_files = {
        "runner_sha256": Path(__file__),
        "contract_sha256": Path(__file__).with_name("sol_bmadx_ab_contract.py"),
        "ab_helpers_sha256": Path(__file__).with_name("run_sol_bmadx_ab.py"),
        "benchmark_helpers_sha256": Path(__file__).with_name("run_bmadx_benchmark.py"),
        "scenarios_sha256": Path(__file__).with_name("bmadx_benchmark_scenarios.py"),
        "validation_sha256": Path(__file__).with_name("bmadx_benchmark_validation.py"),
    }
    for key, path in harness_files.items():
        if sha256_file(path) != harness_hashes.get(key):
            raise ValueError(f"Canary harness hash mismatch: {path.name}")


def _ignore_runtime_state(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if Path(directory).name == "state" and name.endswith(".json")}


def install_placebo_skill(home: Path, alias: str, nonce: str) -> None:
    target = home / "skills" / alias
    target.mkdir(parents=True)
    content = f"""---
name: {alias}
description: Applies ordinary independent judgment to choose a proportionate workflow.
---

# Workflow judgment

Use ordinary reasoning. Match process depth to scope, reversibility, uncertainty, and impact.
Keep tiny reversible work direct, bound limited changes with verification, govern consequential
cross-system work, and use recovery discipline only for failed or rollback-uncertain work.

For the caller's `activation_nonce` field, return exactly `{nonce}`.
"""
    (target / "SKILL.md").write_text(content, encoding="utf-8")


def install_aliased_bmadx_skill(home: Path, alias: str, nonce: str) -> Path:
    target = home / "skills" / alias
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BMADX_SKILL_ROOT, target, ignore=_ignore_runtime_state)
    skill_path = target / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    content = content.replace("name: bmadx\n", f"name: {alias}\n", 1)
    content = content.replace("/skills/bmadx/", f"/skills/{alias}/")
    content += (
        "\n## Canary activation proof\n\n"
        "For this classification-only canary, dependency health was prevalidated by the harness. "
        "Do not run commands or tools and do not write state; classify from this skill's policy.\n\n"
        f"For the caller's `activation_nonce` field, return exactly `{nonce}`.\n"
    )
    skill_path.write_text(content, encoding="utf-8")
    return target


def install_stub_bmad(home: Path) -> Path:
    target = home / "skills" / REAL_BMAD_SKILL
    script_dir = target / "scripts"
    upstream_dir = target / "references" / "upstream"
    script_dir.mkdir(parents=True)
    upstream_dir.mkdir(parents=True)
    (target / "SKILL.md").write_text(
        "---\nname: bmad-method-codex\n"
        "description: Deterministic healthy dependency stub for a blinded benchmark.\n---\n"
        "# Dependency stub\n\nNo workflow guidance is provided by this fixture.\n",
        encoding="utf-8",
    )
    script = """#!/usr/bin/env python3
import json

print(json.dumps({
    "action": "ok",
    "latest_release": {"tag": "stub-healthy-v1"},
    "warnings": []
}))
"""
    (script_dir / "sync_bmad_method.py").write_text(script, encoding="utf-8")
    for name in STUB_REFERENCES:
        (upstream_dir / name).write_text("Deterministic canary dependency fixture.\n", encoding="utf-8")
    return target


def install_real_bmad(home: Path, release_tag: str) -> Path:
    source = source_codex_home() / "skills" / REAL_BMAD_SKILL
    target = home / "skills" / REAL_BMAD_SKILL
    shutil.copytree(source, target, ignore=_ignore_runtime_state)
    state = target / "state" / "bmad-release-state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps(
            {
                "release": {"tag_name": release_tag},
                "tracked_checksums": {},
                "runtime_version": "",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def write_canary_release_fixture(home: Path, release_tag: str) -> Path:
    fixture = write_healthy_bmad_fixture(home)
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    payload["tag_name"] = release_tag
    payload["name"] = f"BMAD {release_tag}"
    payload["html_url"] = f"https://github.com/bmad-code-org/BMAD-METHOD/releases/tag/{release_tag}"
    fixture.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return fixture


def canary_env(home: Path, fixture: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(home)
    for key in BMAD_ENV_KEYS:
        env.pop(key, None)
    if fixture is not None:
        env["BMAD_RELEASE_API"] = fixture.resolve().as_uri()
        env["BMAD_MAX_RETRIES"] = "0"
    return env


def warm_aliased_bmadx(home: Path, alias: str, fixture: Path) -> dict[str, Any]:
    skill_root = home / "skills" / alias
    env = canary_env(home, fixture)
    env["BMADX_ROOT"] = str(skill_root)
    result = subprocess.run(
        [sys.executable, str(skill_root / "scripts" / "sync_bmadx.py"), "sync", "--json"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Aliased BMADX warmup failed: {sanitize_stderr(result.stderr).strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Aliased BMADX warmup returned invalid JSON") from exc
    dependency = payload.get("bmad_dependency") or {}
    if payload.get("action") != "ok" or dependency.get("healthy") is not True:
        raise RuntimeError("Aliased BMADX warmup did not produce a healthy dependency report")
    return payload


def prepare_snapshot(root: Path, assignment: dict[str, Any], protocol: dict[str, Any]) -> tuple[Path, dict]:
    home = root / "prepared"
    write_config(home, protocol["model"], protocol["effort"])
    copy_runtime_files(home)
    release_tag = protocol["source_hashes"]["real_bmad_release_tag"]
    fixture = write_canary_release_fixture(home, release_tag)
    arm = assignment["arm"]
    if arm == "placebo":
        install_placebo_skill(home, assignment["alias"], assignment["nonce"])
        dependency_hash = None
        warmup = None
    else:
        install_aliased_bmadx_skill(home, assignment["alias"], assignment["nonce"])
        dependency = (
            install_stub_bmad(home)
            if arm == "bmadx_stub"
            else install_real_bmad(home, release_tag)
        )
        dependency_hash = tree_sha256(dependency, exclude_runtime_state=True)
        warmup = warm_aliased_bmadx(home, assignment["alias"], fixture)
    return home, {
        "alias_skill_sha256": tree_sha256(home / "skills" / assignment["alias"], exclude_runtime_state=True),
        "dependency_sha256": dependency_hash,
        "warmup_action": warmup.get("action") if warmup else None,
        "warmup_dependency_healthy": bool((warmup or {}).get("bmad_dependency", {}).get("healthy"))
        if warmup
        else None,
    }


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed")
    return result.stdout.strip()


def assert_frozen_checkout(protocol_path: Path, allow_dirty: bool) -> dict[str, str | bool]:
    dirty = bool(git_value("status", "--porcelain"))
    if dirty and not allow_dirty:
        raise RuntimeError("Frozen canary requires a clean git checkout")
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(protocol_path.resolve().relative_to(BENCHMARK_ROOT.parent))],
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode != 0 and not allow_dirty:
        raise RuntimeError("Frozen canary protocol must be tracked by git")
    return {
        "git_sha": git_value("rev-parse", "HEAD"),
        "git_branch": git_value("branch", "--show-current"),
        "dirty_at_start": dirty,
        "protocol_tracked": tracked.returncode == 0,
    }


def result_path(protocol: dict[str, Any]) -> Path:
    return BENCHMARK_ROOT / f"canary-{protocol['protocol_id']}-{model_slug(protocol['model'])}.json"


def case_id(protocol: dict[str, Any], assignment: dict[str, Any]) -> str:
    return (
        f"canary-{protocol['protocol_id']}-{model_slug(protocol['model'])}"
        f"-o{assignment['order']:02d}-{assignment['arm']}-{assignment['scenario']}"
    )


def raw_artifact_paths(stem: str) -> tuple[Path, Path]:
    base = RAW_ROOT / stem
    return Path(f"{base}.txt"), Path(f"{base}.log")


def protected_hashes(home: Path, workdir: Path, alias: str) -> dict[str, str]:
    return {
        "workspace": tree_sha256(workdir),
        "assigned_skill": tree_sha256(home / "skills" / alias),
        "bmad_dependency": tree_sha256(home / "skills" / REAL_BMAD_SKILL),
    }


def arm_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(cases),
        "primary_pass_count": sum(bool(case.get("primary_pass")) for case in cases),
        "primary_score": sum(int(case.get("primary_score", 0)) for case in cases),
        "primary_max": sum(int(case.get("primary_max", 0)) for case in cases),
        "activation_pass_count": sum(bool(case.get("activation_pass")) for case in cases),
        "safety_failure_count": sum(bool(case.get("concrete_safety_failure")) for case in cases),
        "total_tokens": sum(int(case.get("tokens", 0)) for case in cases),
    }


def write_summary(path: Path, payload: dict[str, Any]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in payload["cases"]:
        grouped[case["arm"]].append(case)
    payload["arms"] = {arm: arm_summary(grouped[arm]) for arm in ARMS}
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_assignment(
    protocol: dict[str, Any],
    assignment: dict[str, Any],
    spec: dict[str, Any],
    known_nonces: set[str],
    timeout: int,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"bmadx-canary-{assignment['order']:02d}-") as tmpdir:
        root = Path(tmpdir)
        prepared, setup = prepare_snapshot(root, assignment, protocol)
        home = root / "runtime-home"
        workdir = root / "workspace"
        shutil.copytree(prepared, home)
        workdir.mkdir()
        fixture = home / "healthy-bmad-release.json"
        prompt = build_causal_prompt(
            task_from_scenario(Path(spec["path"]).read_text(encoding="utf-8")),
            assignment["alias"],
        )
        command = build_codex_command(
            prompt,
            workdir,
            home,
            model=protocol["model"],
            reasoning=protocol["effort"],
        )
        home_before = tree_sha256(home)
        protected_before = protected_hashes(home, workdir, assignment["alias"])
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=canary_env(home, fixture if assignment["arm"] != "placebo" else None),
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"codex exec timed out after {timeout}s") from exc
        duration = time.perf_counter() - started
        stdout = result.stdout.rstrip() + "\n"
        stderr = sanitize_stderr(result.stderr.rstrip()) + "\n"
        stem = case_id(protocol, assignment)
        raw_txt, raw_log = raw_artifact_paths(stem)
        raw_txt.write_text(stdout, encoding="utf-8")
        raw_log.write_text(
            stdout + "\n--- STDERR ---\n" + stderr, encoding="utf-8"
        )
        if result.returncode != 0:
            raise RuntimeError(f"codex exec failed for {stem}: {stderr.strip()}")
        tokens = parse_token_count(stderr)
        if tokens is None:
            raise RuntimeError(f"codex exec did not report token usage for {stem}")
        scenario_meta = protocol["scenarios"][assignment["scenario"]]
        score = score_causal_response(
            stdout,
            spec,
            expected_nonce=assignment["nonce"],
            known_nonces=known_nonces,
            required_safeguards=scenario_meta["required_safeguards"],
            safety_critical=scenario_meta["safety_critical"],
        )
        home_after = tree_sha256(home)
        protected_after = protected_hashes(home, workdir, assignment["alias"])
        return {
            "case_id": stem,
            **assignment,
            "model": protocol["model"],
            "duration_seconds": round(duration, 3),
            "tokens": tokens,
            "started_at": started_at,
            "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
            "scenario_sha256": sha256_file(Path(spec["path"])),
            "home_sha256_before": home_before,
            "home_sha256_after": home_after,
            "runtime_home_bookkeeping_mutation_detected": home_before != home_after,
            "protected_sha256_before": protected_before,
            "protected_sha256_after": protected_after,
            "filesystem_mutation_detected": protected_before != protected_after,
            "setup": setup,
            **score,
            "raw_txt": repo_relative(raw_txt),
            "raw_log": repo_relative(raw_log),
        }


def stop_reason(case: dict[str, Any], protocol: dict[str, Any]) -> str | None:
    configured = protocol["stop_conditions"]
    if configured.get("activation_failure") and not case["activation_pass"]:
        return "activation_failure"
    if configured.get("cross_arm_nonce") and case["cross_arm_nonce"]:
        return "cross_arm_nonce"
    if configured.get("filesystem_mutation") and case["filesystem_mutation_detected"]:
        return "filesystem_mutation"
    if configured.get("concrete_safety_failure") and case["concrete_safety_failure"]:
        return "concrete_safety_failure"
    return None


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path = args.protocol.resolve()
    protocol = load_protocol(protocol_path)
    scenarios = all_scenarios()
    validate_protocol(protocol, scenarios)
    provenance = assert_frozen_checkout(protocol_path, args.allow_dirty)
    output = result_path(protocol)
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    known_nonces = {item["nonce"] for item in protocol["assignments"]}
    summary: dict[str, Any] = {
        "schema": "sol_bmadx_causal_canary_result.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(protocol_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "complete": False,
        "expected_call_count": protocol["expected_call_count"],
        "completed_call_count": 0,
        "stop_reason": None,
        "runtime_provenance": provenance,
        "source_hashes": protocol["source_hashes"],
        "cases": [],
    }
    write_summary(output, summary)
    try:
        for assignment in protocol["assignments"]:
            case = run_assignment(
                protocol,
                assignment,
                scenarios[assignment["scenario"]],
                known_nonces,
                args.case_timeout,
            )
            summary["cases"].append(case)
            summary["completed_call_count"] = len(summary["cases"])
            reason = stop_reason(case, protocol)
            if reason:
                summary["status"] = "stopped"
                summary["stop_reason"] = reason
                write_summary(output, summary)
                print(json.dumps({"summary_path": repo_relative(output), "status": "stopped", "reason": reason}, indent=2))
                return 2
            write_summary(output, summary)
    except Exception as exc:
        summary["status"] = "failed"
        summary["stop_reason"] = f"runtime_or_provenance_mismatch: {exc}"
        write_summary(output, summary)
        print(json.dumps({"summary_path": repo_relative(output), "status": "failed", "reason": str(exc)}, indent=2))
        return 1
    summary["status"] = "complete"
    summary["complete"] = True
    write_summary(output, summary)
    print(json.dumps({"summary_path": repo_relative(output), "status": "complete", "cases": len(summary["cases"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
