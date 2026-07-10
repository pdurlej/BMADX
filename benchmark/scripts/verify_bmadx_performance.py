#!/usr/bin/env python3
"""Verify BMADX performance benchmark summaries."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

VALIDATION_FIELDS = (
    "format_pass",
    "token_count_present",
    "reference_budget_pass",
    "routing_pass",
    "overreach_pass",
    "thinking_budget_present",
    "thinking_budget_pass",
    "thinking_budget_no_mutation_pass",
    "thinking_budget_supported_value_pass",
    "goal_routing_pass",
    "goal_stop_condition_pass",
    "loop_contract_pass",
    "goal_loop_not_runtime_pass",
    "handoff_routing_pass",
    "handoff_not_runtime_pass",
    "no_worker_lane_pass",
    "no_model_name_pass",
    "no_dispatch_command_pass",
    "no_platform_surface_pass",
)

TOKEN_CAPS = {
    "X1": 9000,
    "X2": 10000,
}

CLAIM_METRICS = (
    ("total_tokens", ("performance_summary", "all", "total_tokens")),
    ("avg_tokens", ("performance_summary", "all", "avg_tokens")),
    ("avg_duration_seconds", ("performance_summary", "all", "avg_duration_seconds")),
    ("p95_duration_seconds", ("performance_summary", "all", "p95_duration_seconds")),
    ("max_duration_seconds", ("performance_summary", "all", "max_duration_seconds")),
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify BMADX benchmark performance summaries")
    parser.add_argument("summaries", nargs="+", type=Path)
    parser.add_argument(
        "--mode",
        choices=("baseline", "claim"),
        default="baseline",
        help="baseline requires safety/validation gates; claim also requires advisor to improve or hold metrics",
    )
    parser.add_argument(
        "--require-model",
        default="",
        help="Optional exact model requirement; omitted by default so each observed model is verified independently",
    )
    parser.add_argument("--require-profiles", default="")
    parser.add_argument("--require-policies", default="")
    parser.add_argument("--require-gate-mode", default="")
    parser.add_argument("--require-group-slug", default="")
    parser.add_argument(
        "--token-cap-mode",
        choices=("warn", "strict"),
        default="warn",
        help="warn records X1/X2 token cap overages without failing baseline; strict fails on token caps",
    )
    parser.add_argument("--min-repeat", type=int, default=1)
    parser.add_argument("--json", action="store_true", help="Print machine-readable report")
    return parser.parse_args(argv)


def split_csv(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def load_summary(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    payload["_path"] = str(path)
    return payload


def all_cases(summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for key in ("cases", "boundary_cases", "non_technical_cases", "handoff_cases", "goal_loop_cases"):
        cases.extend(summary.get(key) or [])
    return cases


def nested(summary: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = summary
    for key in path:
        value = value[key]
    return value


def validate_case(case: dict[str, Any], *, enforce_token_caps: bool) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    name = str(case.get("case") or "<unnamed>")

    if not isinstance(case.get("tokens"), int):
        failures.append(f"{name}: tokens missing or not an integer")
    if not isinstance(case.get("duration_seconds"), (int, float)):
        failures.append(f"{name}: duration_seconds missing")

    for field in VALIDATION_FIELDS:
        if field in case and case[field] is not True:
            failures.append(f"{name}: {field}=false")

    if case.get("token_pass") is not True:
        target = failures if enforce_token_caps else warnings
        target.append(f"{name}: token_pass=false")

    expected_gear = case.get("expected_gear")
    if expected_gear in TOKEN_CAPS and isinstance(case.get("tokens"), int):
        cap = TOKEN_CAPS[expected_gear]
        if case["tokens"] > cap:
            target = failures if enforce_token_caps else warnings
            target.append(f"{name}: {expected_gear} tokens {case['tokens']} exceed cap {cap}")

    return failures, warnings


def recorded_failure_is_token_only(failure: Any) -> bool:
    if isinstance(failure, dict):
        failed_checks = failure.get("failed_checks") or []
        return bool(failed_checks) and set(failed_checks) <= {"token_pass"}
    return False


def validate_summary(
    summary: dict[str, Any],
    *,
    required_model: str,
    required_gate_mode: str,
    required_group_slug: str,
    min_repeat: int,
    enforce_token_caps: bool,
) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    path = summary.get("_path", "<summary>")
    runner = summary.get("runner") or {}

    if required_model and runner.get("model") != required_model:
        failures.append(f"{path}: model {runner.get('model')!r} != {required_model!r}")

    if required_gate_mode and runner.get("gate_mode") != required_gate_mode:
        failures.append(f"{path}: gate_mode {runner.get('gate_mode')!r} != {required_gate_mode!r}")

    if required_group_slug and runner.get("group_slug") != required_group_slug:
        failures.append(f"{path}: group_slug {runner.get('group_slug')!r} != {required_group_slug!r}")

    repeat = runner.get("repeat")
    if not isinstance(repeat, int) or repeat < min_repeat:
        failures.append(f"{path}: repeat {repeat!r} < {min_repeat}")

    if not all_cases(summary):
        failures.append(f"{path}: no benchmark cases")

    for case in all_cases(summary):
        case_failures, case_warnings = validate_case(case, enforce_token_caps=enforce_token_caps)
        failures.extend(case_failures)
        warnings.extend(case_warnings)

    recorded_failures = summary.get("validation_failures") or {}
    for group, group_failures in recorded_failures.items():
        if group_failures:
            token_only = [failure for failure in group_failures if recorded_failure_is_token_only(failure)]
            non_token = [failure for failure in group_failures if not recorded_failure_is_token_only(failure)]
            if non_token or enforce_token_caps:
                failures.append(f"{path}: validation_failures.{group} is not empty")
            if token_only and not enforce_token_caps:
                warnings.append(f"{path}: validation_failures.{group} contains token cap warnings")

    return failures, warnings


def validate_required_coverage(
    summaries: list[dict[str, Any]],
    *,
    required_profiles: set[str],
    required_policies: set[str],
) -> list[str]:
    failures: list[str] = []
    summaries_by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for summary in summaries:
        model = str((summary.get("runner") or {}).get("model") or "<missing-model>")
        summaries_by_model[model].append(summary)

    for model, model_summaries in sorted(summaries_by_model.items()):
        observed_profiles = {summary.get("profile") for summary in model_summaries}
        observed_policies = {
            (summary.get("runner") or {}).get("reasoning_policy") for summary in model_summaries
        }

        for profile in sorted(required_profiles - observed_profiles):
            failures.append(f"{model}: missing required profile: {profile}")
        for policy in sorted(required_policies - observed_policies):
            failures.append(f"{model}: missing required reasoning policy: {policy}")

        if required_profiles and required_policies:
            observed_pairs = {
                (summary.get("profile"), (summary.get("runner") or {}).get("reasoning_policy"))
                for summary in model_summaries
            }
            for profile in sorted(required_profiles):
                for policy in sorted(required_policies):
                    if (profile, policy) not in observed_pairs:
                        failures.append(
                            f"{model}: missing required profile/policy pair: {profile}/{policy}"
                        )

    return failures


def claim_failures(summaries: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    grouped: dict[tuple[Any, Any, Any], dict[str, dict[str, Any]]] = defaultdict(dict)
    for summary in summaries:
        runner = summary.get("runner") or {}
        key = (
            str(runner.get("model") or "<missing-model>"),
            str(summary.get("profile") or "<missing-profile>"),
            str(runner.get("group_slug") or "<missing-group>"),
        )
        policy = str(runner.get("reasoning_policy") or "<missing-policy>")
        grouped[key][policy] = summary

    for (model, profile, group_slug), by_policy in sorted(grouped.items()):
        fixed = by_policy.get("fixed")
        advisor = by_policy.get("advisor")
        if not fixed or not advisor:
            failures.append(
                f"{model}/{profile}/{group_slug}: missing fixed/advisor pair for claim comparison"
            )
            continue
        for metric_name, path in CLAIM_METRICS:
            fixed_value = nested(fixed, path)
            advisor_value = nested(advisor, path)
            if advisor_value > fixed_value:
                failures.append(
                    f"{model}/{profile}/{group_slug}: advisor {metric_name} {advisor_value} exceeds fixed {fixed_value}"
                )

    return failures


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    summaries = [load_summary(path) for path in args.summaries]
    baseline_failures: list[str] = []
    token_cap_warnings: list[str] = []
    enforce_token_caps = args.token_cap_mode == "strict" or args.mode == "claim"
    for summary in summaries:
        summary_failures, summary_warnings = validate_summary(
            summary,
            required_model=args.require_model,
            required_gate_mode=args.require_gate_mode,
            required_group_slug=args.require_group_slug,
            min_repeat=args.min_repeat,
            enforce_token_caps=enforce_token_caps,
        )
        baseline_failures.extend(summary_failures)
        token_cap_warnings.extend(summary_warnings)
    baseline_failures.extend(
        validate_required_coverage(
            summaries,
            required_profiles=split_csv(args.require_profiles),
            required_policies=split_csv(args.require_policies),
        )
    )

    claim_checks = claim_failures(summaries)
    return {
        "baseline_pass": not baseline_failures,
        "claim_pass": not baseline_failures and not claim_checks,
        "mode": args.mode,
        "summary_count": len(summaries),
        "models": sorted(
            {str((summary.get("runner") or {}).get("model") or "<missing-model>") for summary in summaries}
        ),
        "baseline_failures": baseline_failures,
        "token_cap_warnings": token_cap_warnings,
        "claim_failures": claim_checks,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2) + "\n")
    else:
        print(f"baseline_pass={str(report['baseline_pass']).lower()}")
        print(f"claim_pass={str(report['claim_pass']).lower()}")
        for failure in report["baseline_failures"]:
            print(f"baseline_failure: {failure}")
        for warning in report["token_cap_warnings"]:
            print(f"token_cap_warning: {warning}")
        for failure in report["claim_failures"]:
            print(f"claim_failure: {failure}")

    if args.mode == "claim":
        return 0 if report["claim_pass"] else 1
    return 0 if report["baseline_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
