#!/usr/bin/env python3
"""Run BMADX routing benchmarks in a clean temporary CODEX_HOME."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from bmadx_benchmark_scenarios import (
    BOUNDARY_SCENARIOS,
    CORE_SCENARIOS,
    HANDOFF_SCENARIOS,
    NON_TECH_SCENARIOS,
)
from bmadx_benchmark_validation import (
    explain_failures_for_non_technical_users,
    parse_token_count,
    sanitize_stderr,
    summarize_validation,
    validate_case,
    validation_failures,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark"
RAW_ROOT = BENCHMARK_ROOT / "raw"
BMADX_SKILL_ROOT = REPO_ROOT / "skill" / "bmadx"
BMAD_METHOD_ROOT = Path.home() / ".codex" / "skills" / "bmad-method-codex"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING = "medium"
HEALTHY_BMAD_RELEASE = {
    "tag_name": "v6.3.0",
    "name": "BMAD v6.3.0",
    "published_at": "2026-01-01T00:00:00Z",
    "html_url": "https://github.com/bmad-code-org/BMAD-METHOD/releases/tag/v6.3.0",
    "body": "Benchmark fixture for deterministic healthy BMAD profile.",
}

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BMADX benchmark scenarios in a clean CODEX_HOME")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Codex model to run in the benchmark CODEX_HOME (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--reasoning",
        default=DEFAULT_REASONING,
        help=f"Codex model reasoning effort (default: {DEFAULT_REASONING})",
    )
    parser.add_argument(
        "--oss",
        action="store_true",
        help="Run through Codex OSS mode for local-provider experiments",
    )
    parser.add_argument(
        "--local-provider",
        choices=("ollama", "lmstudio"),
        default=None,
        help="Local OSS provider to pass to codex exec when --oss is used",
    )
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
    return parser.parse_args(argv)


def build_prompt(scenario_path: Path, *, include_handoff: bool = False) -> str:
    content = scenario_path.read_text(encoding="utf-8")
    task_line = next(
        (line for line in content.splitlines() if line.strip().startswith("Task:")),
        "",
    )
    task = task_line.partition("Task:")[2].strip()
    prompt = (
        "Use $bmadx. Compact gate only. Answer only the BMADX short contract. "
        "No analysis. For X1/X2 do not read refs. "
        "Do not implement/edit/render/inline artifacts. "
    )
    if include_handoff:
        prompt += (
            "If broad orchestrator handoff is relevant, include exactly one `Handoff: yes/no` line. "
            "Do not name models, worker lanes, arbiters, dispatch commands, MCP, hooks, plugins, subagents, or runtime state. "
        )
    return prompt + f"Task: {task}"


def repo_relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def model_slug(model: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", model.strip().lower()).strip("-")
    return slug or "model"


def runner_slug(model: str, *, oss: bool = False, local_provider: str | None = None) -> str:
    slug = model_slug(model)
    if not oss:
        return slug
    provider = model_slug(local_provider or "local")
    return f"{provider}-{slug}"


def summary_path_for(date_stamp: str, model_slug_value: str, profile: str) -> Path:
    return BENCHMARK_ROOT / f"summary-{date_stamp}-{model_slug_value}-{profile}-bmadx.json"


def write_config(codex_home: Path, model: str, reasoning: str) -> None:
    config = '\n'.join(
        [
            f'model = "{model}"',
            f'model_reasoning_effort = "{reasoning}"',
            'personality = "pragmatic"',
            "",
        ]
    )
    codex_home.mkdir(parents=True, exist_ok=True)
    (codex_home / "config.toml").write_text(config, encoding="utf-8")


def copy_runtime_files(codex_home: Path) -> None:
    for name in ("auth.json", "version.json"):
        source = Path.home() / ".codex" / name
        if source.exists():
            shutil.copy2(source, codex_home / name)


def ignore_bmadx_runtime_state(directory: str, names: list[str]) -> set[str]:
    if Path(directory).name != "state":
        return set()
    return {name for name in names if name.endswith(".json")}


def copy_skills(codex_home: Path) -> None:
    skills_dir = codex_home / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        BMADX_SKILL_ROOT,
        skills_dir / "bmadx",
        dirs_exist_ok=True,
        ignore=ignore_bmadx_runtime_state,
    )
    shutil.copytree(
        BMAD_METHOD_ROOT,
        skills_dir / "bmad-method-codex",
        dirs_exist_ok=True,
        ignore=ignore_bmadx_runtime_state,
    )


def write_healthy_bmad_fixture(tmp_root: Path) -> Path:
    fixture = tmp_root / "healthy-bmad-release.json"
    fixture.write_text(json.dumps(HEALTHY_BMAD_RELEASE, indent=2) + "\n", encoding="utf-8")
    return fixture


def benchmark_env(codex_home: Path, profile: str, healthy_release_fixture: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    if profile == "healthy" and healthy_release_fixture is not None:
        env["BMAD_RELEASE_API"] = healthy_release_fixture.resolve().as_uri()
    elif profile == "degraded":
        env["BMAD_RELEASE_API"] = "https://127.0.0.1:9/releases/latest"
        env["BMAD_RAW_BASE"] = "https://127.0.0.1:9/"
        env["BMAD_MAX_RETRIES"] = "0"
    return env


def parse_json_report(stdout: str) -> dict:
    try:
        payload = json.loads(stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"BMADX warmup returned invalid JSON: {exc}") from exc
    return payload if isinstance(payload, dict) else {}


def validate_warmup_payload(profile: str, payload: dict) -> None:
    dependency_healthy = bool((payload.get("bmad_dependency") or {}).get("healthy"))
    if profile == "healthy":
        if payload.get("action") != "ok" or not dependency_healthy:
            raise RuntimeError("Healthy BMADX warmup did not produce an ok, healthy dependency report.")
        return

    if profile == "degraded" and payload.get("action") == "ok" and dependency_healthy:
        raise RuntimeError("Degraded BMADX warmup unexpectedly produced an ok, healthy dependency report.")


def warmup_profile(codex_home: Path, profile: str, healthy_release_fixture: Path | None = None) -> None:
    command = [
        sys.executable,
        str(codex_home / "skills" / "bmadx" / "scripts" / "sync_bmadx.py"),
        "sync",
        "--json",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=benchmark_env(codex_home, profile, healthy_release_fixture),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Warmup BMADX failed for profile {profile}: {result.stderr.strip() or result.stdout.strip()}"
        )
    validate_warmup_payload(profile, parse_json_report(result.stdout))


def build_codex_command(
    prompt: str,
    workdir: Path,
    codex_home: Path,
    *,
    model: str,
    reasoning: str,
    oss: bool = False,
    local_provider: str | None = None,
) -> list[str]:
    command = [
        "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--disable",
        "plugins",
        "--disable",
        "apps",
        "--disable",
        "general_analytics",
        "-m",
        model,
        "-C",
        str(workdir),
        "--add-dir",
        str(codex_home),
        "-s",
        "workspace-write",
        "--skip-git-repo-check",
        "--color",
        "never",
        prompt,
    ]
    if not oss:
        model_index = command.index("-C")
        command[model_index:model_index] = ["-c", f'model_reasoning_effort="{reasoning}"']
    if oss:
        command.insert(command.index("-m"), "--oss")
        if local_provider:
            command.insert(command.index("-m"), local_provider)
            command.insert(command.index(local_provider), "--local-provider")
    return command


def run_case(
    codex_home: Path,
    profile: str,
    scenario_key: str,
    spec: dict,
    workdir: Path,
    healthy_release_fixture: Path | None,
    *,
    model: str,
    reasoning: str,
    oss: bool,
    local_provider: str | None,
    model_slug_value: str,
) -> dict:
    scenario_path = Path(spec["path"])
    prompt = build_prompt(scenario_path, include_handoff=spec.get("expected_handoff") is not None)
    command = build_codex_command(
        prompt,
        workdir,
        codex_home,
        model=model,
        reasoning=reasoning,
        oss=oss,
        local_provider=local_provider,
    )
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=benchmark_env(codex_home, profile, healthy_release_fixture),
        check=False,
    )
    stdout = result.stdout.rstrip() + "\n"
    stderr = sanitize_stderr(result.stderr.rstrip()) + "\n"
    raw_base = RAW_ROOT / f"bmadx-{model_slug_value}-{profile}-{scenario_key}"
    raw_base.with_suffix(".txt").write_text(stdout, encoding="utf-8")
    raw_base.with_suffix(".log").write_text(stdout + "\n--- STDERR ---\n" + stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"codex exec failed for {scenario_key}: {stderr.strip()}")

    lines = [line for line in stdout.splitlines() if line.strip()]
    tokens = parse_token_count(stderr)
    if tokens is None:
        raise RuntimeError(f"codex exec did not report token usage for {scenario_key}")
    validation = validate_case(stdout, stderr, tokens, spec)
    return {
        "case": f"bmadx-{profile}-{scenario_key}",
        "framework": "bmadx",
        "profile": profile,
        "tokens": tokens,
        "model": model,
        "reasoning": reasoning,
        "provider": "oss" if oss else "openai",
        "local_provider": local_provider,
        "mcp_startup": "no servers",
        "response_first_line": lines[0] if lines else "",
        "response_chars": len(stdout),
        "response_lines": len(stdout.splitlines()),
        "expected_gear": validation["expected_gear"],
        "selected_gear": validation["selected_gear"],
        "observed_gears": validation["observed_gears"],
        "format_pass": validation["format_pass"],
        "token_count_present": validation["token_count_present"],
        "token_pass": validation["token_pass"],
        "reference_budget_pass": validation["reference_budget_pass"],
        "routing_pass": validation["routing_pass"],
        "overreach_pass": validation["overreach_pass"],
        "expected_handoff": validation["expected_handoff"],
        "observed_handoff": validation["observed_handoff"],
        "handoff_routing_pass": validation["handoff_routing_pass"],
        "handoff_not_runtime_pass": validation["handoff_not_runtime_pass"],
        "no_worker_lane_pass": validation["no_worker_lane_pass"],
        "no_model_name_pass": validation["no_model_name_pass"],
        "no_dispatch_command_pass": validation["no_dispatch_command_pass"],
        "no_platform_surface_pass": validation["no_platform_surface_pass"],
        "reference_reads": validation["reference_reads"],
        "raw_txt": repo_relative(raw_base.with_suffix(".txt")),
        "raw_log": repo_relative(raw_base.with_suffix(".log")),
    }


def run_scenario_group(
    scenarios: dict[str, dict],
    codex_home: Path,
    profile: str,
    workdir: Path,
    healthy_release_fixture: Path | None,
    *,
    model: str,
    reasoning: str,
    oss: bool,
    local_provider: str | None,
    model_slug_value: str,
) -> list[dict]:
    return [
        run_case(
            codex_home,
            profile,
            scenario_key,
            spec,
            workdir,
            healthy_release_fixture,
            model=model,
            reasoning=reasoning,
            oss=oss,
            local_provider=local_provider,
            model_slug_value=model_slug_value,
        )
        for scenario_key, spec in scenarios.items()
    ]


def build_summary(
    date_stamp: str,
    profile: str,
    core_cases: list[dict],
    boundary_cases: list[dict],
    non_technical_cases: list[dict] | None = None,
    handoff_cases: list[dict] | None = None,
    *,
    model: str,
    reasoning: str,
    oss: bool = False,
    local_provider: str | None = None,
) -> dict:
    non_technical_cases = non_technical_cases or []
    handoff_cases = handoff_cases or []
    token_values = [case["tokens"] for case in core_cases]
    return {
        "generated_at": date_stamp,
        "framework": "bmadx",
        "profile": profile,
        "runner": {
            "model": model,
            "reasoning": reasoning,
            "provider": "oss" if oss else "openai",
            "local_provider": local_provider,
            "reasoning_applied": not oss,
            "mcp_startup": "no servers",
        },
        "baselines": {
            "mixed_summary": repo_relative(BENCHMARK_ROOT / "summary-2026-04-04.json"),
            "mixed_summary_note": "Contains historical BMAD/OMX baselines and prior BMADX degraded rerun.",
        },
        "cases": core_cases,
        "boundary_cases": boundary_cases,
        "non_technical_cases": non_technical_cases,
        "handoff_cases": handoff_cases,
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
            "non_technical": summarize_validation(non_technical_cases),
            "handoff": summarize_validation(handoff_cases)
            | {
                "handoff_routing_pass_count": sum(1 for case in handoff_cases if case["handoff_routing_pass"]),
                "handoff_not_runtime_pass_count": sum(1 for case in handoff_cases if case["handoff_not_runtime_pass"]),
                "no_worker_lane_pass_count": sum(1 for case in handoff_cases if case["no_worker_lane_pass"]),
                "no_model_name_pass_count": sum(1 for case in handoff_cases if case["no_model_name_pass"]),
                "no_dispatch_command_pass_count": sum(1 for case in handoff_cases if case["no_dispatch_command_pass"]),
                "no_platform_surface_pass_count": sum(1 for case in handoff_cases if case["no_platform_surface_pass"]),
            },
        },
        "validation_failures": {
            "core": validation_failures(core_cases),
            "boundary": validation_failures(boundary_cases),
            "non_technical": validation_failures(non_technical_cases),
            "handoff": validation_failures(handoff_cases),
        },
        "non_technical_readout": {
            "what_failed_why_it_matters": explain_failures_for_non_technical_users(
                core_cases + boundary_cases + non_technical_cases + handoff_cases
            )
        },
    }


def main() -> int:
    args = parse_args()
    if args.local_provider and not args.oss:
        raise SystemExit("--local-provider requires --oss")
    model_slug_value = runner_slug(args.model, oss=args.oss, local_provider=args.local_provider)
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bmadx-benchmark-") as tmpdir:
        tmp_root = Path(tmpdir)
        codex_home = tmp_root / "codex-home"
        workdir = tmp_root / "workdir"
        workdir.mkdir(parents=True, exist_ok=True)
        write_config(codex_home, args.model, args.reasoning)
        copy_runtime_files(codex_home)
        copy_skills(codex_home)
        healthy_release_fixture = write_healthy_bmad_fixture(tmp_root) if args.profile == "healthy" else None
        warmup_profile(codex_home, args.profile, healthy_release_fixture)

        run_group_kwargs = {
            "model": args.model,
            "reasoning": args.reasoning,
            "oss": args.oss,
            "local_provider": args.local_provider,
            "model_slug_value": model_slug_value,
        }
        core_cases = run_scenario_group(
            CORE_SCENARIOS,
            codex_home,
            args.profile,
            workdir,
            healthy_release_fixture,
            **run_group_kwargs,
        )
        boundary_cases = run_scenario_group(
            BOUNDARY_SCENARIOS,
            codex_home,
            args.profile,
            workdir,
            healthy_release_fixture,
            **run_group_kwargs,
        )
        non_technical_cases = run_scenario_group(
            NON_TECH_SCENARIOS,
            codex_home,
            args.profile,
            workdir,
            healthy_release_fixture,
            **run_group_kwargs,
        )
        handoff_cases = run_scenario_group(
            HANDOFF_SCENARIOS,
            codex_home,
            args.profile,
            workdir,
            healthy_release_fixture,
            **run_group_kwargs,
        )

    summary = build_summary(
        args.date_stamp,
        args.profile,
        core_cases,
        boundary_cases,
        non_technical_cases,
        handoff_cases,
        model=args.model,
        reasoning=args.reasoning,
        oss=args.oss,
        local_provider=args.local_provider,
    )
    summary_path = summary_path_for(args.date_stamp, model_slug_value, args.profile)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_path": repo_relative(summary_path),
                "core_case_count": len(core_cases),
                "boundary_case_count": len(boundary_cases),
                "non_technical_case_count": len(non_technical_cases),
                "handoff_case_count": len(handoff_cases),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
