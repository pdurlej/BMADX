#!/usr/bin/env python3
"""Run BMADX routing benchmarks in a clean temporary CODEX_HOME."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark"
RAW_ROOT = BENCHMARK_ROOT / "raw"
SCENARIO_ROOT = BENCHMARK_ROOT / "scenarios"
BMADX_SKILL_ROOT = REPO_ROOT / "skill" / "bmadx"
BMAD_METHOD_ROOT = Path.home() / ".codex" / "skills" / "bmad-method-codex"

CORE_SCENARIOS = {
    "x1": {
        "path": SCENARIO_ROOT / "scenario-x1.txt",
        "expected_gear": "X1",
        "max_lines": 5,
        "max_chars": 650,
        "max_tokens": 9000,
        "allow_reference_reads": False,
    },
    "x2": {
        "path": SCENARIO_ROOT / "scenario-x2.txt",
        "expected_gear": "X2",
        "max_lines": 12,
        "max_chars": 1000,
        "max_tokens": 10000,
        "allow_reference_reads": False,
    },
    "x3": {
        "path": SCENARIO_ROOT / "scenario-x3.txt",
        "expected_gear": "X3",
        "allow_reference_reads": True,
    },
    "x4": {
        "path": SCENARIO_ROOT / "scenario-x4.txt",
        "expected_gear": "X4",
        "allow_reference_reads": True,
    },
}
BOUNDARY_SCENARIOS = {
    "x2x3-boundary": {
        "path": SCENARIO_ROOT / "scenario-x2x3-boundary.txt",
        "expected_gear": "X3",
        "allow_reference_reads": True,
    }
}
REFERENCE_READ_PATTERN = re.compile(r"/skills/bmadx/references/([^\s\"']+)")
GEAR_PATTERN = re.compile(r"\bX([1-4])\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BMADX benchmark scenarios in a clean CODEX_HOME")
    parser.add_argument(
        "--profile",
        choices=("healthy", "degraded"),
        default="healthy",
        help="BMAD dependency profile for the benchmark run",
    )
    parser.add_argument(
        "--date-stamp",
        default=str(date.today()),
        help="Date stamp used in output file names (default: today)",
    )
    return parser.parse_args()


def build_prompt(scenario_path: Path) -> str:
    content = scenario_path.read_text(encoding="utf-8")
    task_line = next(
        (line for line in content.splitlines() if line.strip().startswith("Task:")),
        "",
    )
    task = task_line.partition("Task:")[2].strip()
    return (
        "Use $bmadx. Pick the lightest safe mode for this task, "
        "justify the choice briefly, and describe the next step. "
        "Do not implement anything. "
        f"Task: {task}"
    )


def parse_token_count(stderr: str) -> int:
    match = re.search(r"tokens used\s*\n([0-9 \u00a0]+)", stderr, re.IGNORECASE)
    if not match:
        return 0
    digits = match.group(1).replace("\u00a0", "").replace(" ", "")
    return int(digits) if digits.isdigit() else 0


def detect_reference_reads(text: str) -> list[str]:
    seen = []
    for match in REFERENCE_READ_PATTERN.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


def detect_observed_gears(stdout: str) -> list[str]:
    seen = []
    for digit in GEAR_PATTERN.findall(stdout):
        gear = f"X{digit}"
        if gear not in seen:
            seen.append(gear)
    return seen


def validate_case(stdout: str, stderr: str, tokens: int, spec: dict) -> dict:
    response = stdout.strip()
    lines = [line for line in response.splitlines() if line.strip()]
    observed_gears = detect_observed_gears(stdout)
    reference_reads = detect_reference_reads(stderr)
    expected_gear = str(spec.get("expected_gear") or "")

    format_pass = True
    if spec.get("max_lines") is not None:
        format_pass = format_pass and len(lines) <= int(spec["max_lines"])
    if spec.get("max_chars") is not None:
        format_pass = format_pass and len(response) <= int(spec["max_chars"])

    token_pass = True
    if spec.get("max_tokens") is not None:
        token_pass = tokens <= int(spec["max_tokens"])

    allow_reference_reads = bool(spec.get("allow_reference_reads", True))
    reference_budget_pass = allow_reference_reads or not reference_reads
    routing_pass = expected_gear in observed_gears if expected_gear else True

    return {
        "expected_gear": expected_gear,
        "observed_gears": observed_gears,
        "reference_reads": reference_reads,
        "format_pass": format_pass,
        "token_pass": token_pass,
        "reference_budget_pass": reference_budget_pass,
        "routing_pass": routing_pass,
    }


def summarize_validation(cases: list[dict]) -> dict:
    if not cases:
        return {
            "case_count": 0,
            "format_pass_count": 0,
            "token_pass_count": 0,
            "reference_budget_pass_count": 0,
            "routing_pass_count": 0,
        }
    return {
        "case_count": len(cases),
        "format_pass_count": sum(1 for case in cases if case["format_pass"]),
        "token_pass_count": sum(1 for case in cases if case["token_pass"]),
        "reference_budget_pass_count": sum(1 for case in cases if case["reference_budget_pass"]),
        "routing_pass_count": sum(1 for case in cases if case["routing_pass"]),
    }


def repo_relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def write_config(codex_home: Path) -> None:
    config = '\n'.join(
        [
            'model = "gpt-5.4"',
            'model_reasoning_effort = "medium"',
            'personality = "pragmatic"',
            "",
        ]
    )
    codex_home.mkdir(parents=True, exist_ok=True)
    (codex_home / "config.toml").write_text(config, encoding="utf-8")


def copy_runtime_files(codex_home: Path) -> None:
    for name in ("auth.json", "version.json", ".codex-global-state.json"):
        source = Path.home() / ".codex" / name
        if source.exists():
            shutil.copy2(source, codex_home / name)


def copy_skills(codex_home: Path) -> None:
    skills_dir = codex_home / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BMADX_SKILL_ROOT, skills_dir / "bmadx", dirs_exist_ok=True)
    shutil.copytree(BMAD_METHOD_ROOT, skills_dir / "bmad-method-codex", dirs_exist_ok=True)


def benchmark_env(codex_home: Path, profile: str) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    if profile == "degraded":
        env["BMAD_RELEASE_API"] = "https://127.0.0.1:9/releases/latest"
        env["BMAD_RAW_BASE"] = "https://127.0.0.1:9/"
        env["BMAD_MAX_RETRIES"] = "0"
    return env


def warmup_profile(codex_home: Path, profile: str) -> None:
    command = [
        "python3",
        str(codex_home / "skills" / "bmadx" / "scripts" / "sync_bmadx.py"),
        "sync",
        "--json",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=benchmark_env(codex_home, profile),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Warmup BMADX failed for profile {profile}: {result.stderr.strip() or result.stdout.strip()}"
        )


def run_case(codex_home: Path, profile: str, scenario_key: str, spec: dict, workdir: Path) -> dict:
    scenario_path = Path(spec["path"])
    prompt = build_prompt(scenario_path)
    command = [
        "codex",
        "exec",
        "-C",
        str(workdir),
        "-s",
        "read-only",
        "--skip-git-repo-check",
        "--color",
        "never",
        prompt,
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=benchmark_env(codex_home, profile),
        check=False,
    )
    stdout = result.stdout.rstrip() + "\n"
    stderr = result.stderr.rstrip() + "\n"
    raw_base = RAW_ROOT / f"bmadx-{profile}-{scenario_key}"
    raw_base.with_suffix(".txt").write_text(stdout, encoding="utf-8")
    raw_base.with_suffix(".log").write_text(stdout + "\n--- STDERR ---\n" + stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"codex exec failed for {scenario_key}: {stderr.strip()}")

    lines = [line for line in stdout.splitlines() if line.strip()]
    tokens = parse_token_count(stderr)
    validation = validate_case(stdout, stderr, tokens, spec)
    return {
        "case": f"bmadx-{profile}-{scenario_key}",
        "framework": "bmadx",
        "profile": profile,
        "tokens": tokens,
        "reasoning": "medium",
        "mcp_startup": "no servers",
        "response_first_line": lines[0] if lines else "",
        "response_chars": len(stdout),
        "response_lines": len(stdout.splitlines()),
        "expected_gear": validation["expected_gear"],
        "observed_gears": validation["observed_gears"],
        "format_pass": validation["format_pass"],
        "token_pass": validation["token_pass"],
        "reference_budget_pass": validation["reference_budget_pass"],
        "routing_pass": validation["routing_pass"],
        "reference_reads": validation["reference_reads"],
        "raw_txt": repo_relative(raw_base.with_suffix(".txt")),
        "raw_log": repo_relative(raw_base.with_suffix(".log")),
    }


def build_summary(date_stamp: str, profile: str, core_cases: list[dict], boundary_cases: list[dict]) -> dict:
    token_values = [case["tokens"] for case in core_cases]
    return {
        "generated_at": date_stamp,
        "framework": "bmadx",
        "profile": profile,
        "runner": {
            "model": "gpt-5.4",
            "reasoning": "medium",
            "mcp_startup": "no servers",
        },
        "baselines": {
            "mixed_summary": repo_relative(BENCHMARK_ROOT / "summary-2026-04-04.json"),
            "mixed_summary_note": "Contains historical BMAD/OMX baselines and prior BMADX degraded rerun.",
        },
        "cases": core_cases,
        "boundary_cases": boundary_cases,
        "framework_averages": {
            "bmadx": {
                "avg_tokens": sum(token_values) / len(token_values) if token_values else 0,
                "min_tokens": min(token_values) if token_values else 0,
                "max_tokens": max(token_values) if token_values else 0,
                "case_count": len(token_values),
            }
        },
        "validation_summary": {
            "core": summarize_validation(core_cases),
            "boundary": summarize_validation(boundary_cases),
        },
    }


def main() -> int:
    args = parse_args()
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bmadx-benchmark-") as tmpdir:
        tmp_root = Path(tmpdir)
        codex_home = tmp_root / "codex-home"
        workdir = tmp_root / "workdir"
        workdir.mkdir(parents=True, exist_ok=True)
        write_config(codex_home)
        copy_runtime_files(codex_home)
        copy_skills(codex_home)
        warmup_profile(codex_home, args.profile)

        core_cases = []
        for scenario_key, spec in CORE_SCENARIOS.items():
            core_cases.append(run_case(codex_home, args.profile, scenario_key, spec, workdir))
        boundary_cases = []
        for scenario_key, spec in BOUNDARY_SCENARIOS.items():
            boundary_cases.append(run_case(codex_home, args.profile, scenario_key, spec, workdir))

    summary = build_summary(args.date_stamp, args.profile, core_cases, boundary_cases)
    summary_path = BENCHMARK_ROOT / f"summary-{args.date_stamp}-{args.profile}-bmad.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_path": repo_relative(summary_path),
                "core_case_count": len(core_cases),
                "boundary_case_count": len(boundary_cases),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
