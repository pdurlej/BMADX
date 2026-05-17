"""Validation helpers for BMADX benchmark output.

Keep this module deterministic and model-free: it should only parse runner
stdout/stderr and turn the observed response into validation fields.
"""

from __future__ import annotations

import re


REFERENCE_READ_PATTERN = re.compile(r"/skills/bmadx/references/([^\s\"']+)")
GEAR_PATTERN = re.compile(r"\bX([1-4])\b")
SELECTED_GEAR_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
    r"(?:Choice|Gear|Mode|Classification)(?:\*\*)?[ \t]*:[ \t]*"
    r"(?:`|\*\*)?[^\r\n]*?\b(X[1-4])\b"
)
HANDOFF_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
    r"Handoff(?:\*\*)?[ \t]*:[ \t]*(?:`|\*\*)?[ \t]*"
    r"(yes|no|recommended|not recommended|none)\b"
)
FORBIDDEN_HANDOFF_RUNTIME_PATTERNS = {
    "no_worker_lane_pass": re.compile(r"\b(primary_worker|secondary_workers|worker lane|model lane|lane:)\b", re.I),
    "no_model_name_pass": re.compile(
        r"\b(gpt-oss|kimi|glm|deepseek|minimax|qwen|devstral|gemma|mistral-large|claude|opus)\b",
        re.I,
    ),
    "no_dispatch_command_pass": re.compile(r"\b(dispatch|ollama run|codex exec --oss|run_id|runtime state)\b", re.I),
    "no_platform_surface_pass": re.compile(r"\b(MCP|hook|plugin|subagent|agent zoo)\b", re.I),
}
VALIDATION_CHECKS = (
    "format_pass",
    "token_count_present",
    "token_pass",
    "reference_budget_pass",
    "routing_pass",
    "overreach_pass",
)
HANDOFF_VALIDATION_CHECKS = VALIDATION_CHECKS + (
    "handoff_routing_pass",
    "handoff_not_runtime_pass",
    "no_worker_lane_pass",
    "no_model_name_pass",
    "no_dispatch_command_pass",
    "no_platform_surface_pass",
)
NON_TECH_FAILURE_REASONS = {
    "format_pass": "The answer is too long or unstructured for a non-technical owner to act on safely.",
    "token_count_present": "The benchmark cannot compare cost or verbosity without a token count.",
    "token_pass": "The response exceeded the intended budget for lightweight work.",
    "reference_budget_pass": "The agent read extra reference docs where the happy path should stay compact.",
    "routing_pass": "The agent chose the wrong work mode, which can either overbuild a small task or underprotect a risky one.",
    "overreach_pass": "The agent mentioned forbidden higher gears, creating unnecessary escalation noise for a bounded task.",
    "handoff_routing_pass": "The agent did not make the expected broad-orchestrator handoff decision for this risk shape.",
    "handoff_not_runtime_pass": "The agent leaked orchestration runtime details instead of staying inside the BMADX handoff packet contract.",
    "no_worker_lane_pass": "The handoff suggested worker lanes, which would make BMADX behave like a runtime orchestrator.",
    "no_model_name_pass": "The handoff named specific models, which should remain a receiving orchestrator decision.",
    "no_dispatch_command_pass": "The handoff included dispatch/runtime commands instead of a portable risk-and-proof packet.",
    "no_platform_surface_pass": "The handoff mentioned platform surfaces such as MCP, hooks, plugins, or subagents that BMADX must not install or require.",
}


def parse_token_count(stderr: str) -> int | None:
    match = re.search(r"tokens used\s*\n([0-9 \u00a0]+)", stderr, re.IGNORECASE)
    if not match:
        return None
    digits = match.group(1).replace("\u00a0", "").replace(" ", "")
    return int(digits) if digits.isdigit() else None


def sanitize_stderr(stderr: str) -> str:
    lines = stderr.splitlines()
    sanitized: list[str] = []
    skipping_analytics = False
    resume_prefixes = ("exec", "codex", "tokens used", "thinking", "user", "assistant")
    for line in lines:
        if "codex_analytics::client: events failed" in line:
            sanitized.append("[analytics warning omitted]")
            skipping_analytics = True
            continue
        if skipping_analytics:
            if line.startswith(resume_prefixes):
                skipping_analytics = False
            else:
                continue
        sanitized.append(line)
    return "\n".join(sanitized).rstrip()


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


def detect_selected_gear(stdout: str) -> str | None:
    match = SELECTED_GEAR_PATTERN.search(stdout)
    return match.group(1).upper() if match else None


def detect_handoff(stdout: str) -> bool | None:
    match = HANDOFF_PATTERN.search(stdout)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value in {"yes", "recommended"}:
        return True
    if value in {"no", "not recommended", "none"}:
        return False
    return None


def validate_handoff_runtime_drift(stdout: str) -> dict:
    result = {}
    for key, pattern in FORBIDDEN_HANDOFF_RUNTIME_PATTERNS.items():
        result[key] = pattern.search(stdout) is None
    result["handoff_not_runtime_pass"] = all(result.values())
    return result


def validate_case(stdout: str, stderr: str, tokens: int | None, spec: dict) -> dict:
    response = stdout.strip()
    lines = [line for line in response.splitlines() if line.strip()]
    observed_gears = detect_observed_gears(stdout)
    selected_gear = detect_selected_gear(stdout)
    reference_reads = detect_reference_reads(stderr)
    expected_gear = str(spec.get("expected_gear") or "")
    forbidden_gears = set(spec.get("forbidden_gears") or [])
    expected_handoff = spec.get("expected_handoff")
    token_count_present = tokens is not None

    format_pass = True
    if spec.get("max_lines") is not None:
        format_pass = format_pass and len(lines) <= int(spec["max_lines"])
    if spec.get("max_chars") is not None:
        format_pass = format_pass and len(response) <= int(spec["max_chars"])

    token_pass = token_count_present
    if spec.get("max_tokens") is not None:
        token_pass = token_pass and int(tokens) <= int(spec["max_tokens"])

    allow_reference_reads = bool(spec.get("allow_reference_reads", True))
    reference_budget_pass = allow_reference_reads or not reference_reads
    routing_pass = selected_gear == expected_gear if expected_gear else True
    overreach_pass = not any(gear in forbidden_gears for gear in observed_gears)
    observed_handoff = detect_handoff(stdout)
    handoff_routing_pass = (
        observed_handoff == bool(expected_handoff)
        if expected_handoff is not None
        else True
    )
    handoff_runtime = validate_handoff_runtime_drift(stdout) if expected_handoff is not None else {
        "handoff_not_runtime_pass": True,
        "no_worker_lane_pass": True,
        "no_model_name_pass": True,
        "no_dispatch_command_pass": True,
        "no_platform_surface_pass": True,
    }

    return {
        "expected_gear": expected_gear,
        "selected_gear": selected_gear,
        "observed_gears": observed_gears,
        "reference_reads": reference_reads,
        "format_pass": format_pass,
        "token_count_present": token_count_present,
        "token_pass": token_pass,
        "reference_budget_pass": reference_budget_pass,
        "routing_pass": routing_pass,
        "overreach_pass": overreach_pass,
        "expected_handoff": expected_handoff,
        "observed_handoff": observed_handoff,
        "handoff_routing_pass": handoff_routing_pass,
        **handoff_runtime,
    }


def summarize_validation(cases: list[dict]) -> dict:
    if not cases:
        return {
            "case_count": 0,
            "format_pass_count": 0,
            "token_count_present_count": 0,
            "token_pass_count": 0,
            "reference_budget_pass_count": 0,
            "routing_pass_count": 0,
            "overreach_pass_count": 0,
        }
    return {
        "case_count": len(cases),
        "format_pass_count": sum(1 for case in cases if case["format_pass"]),
        "token_count_present_count": sum(1 for case in cases if case.get("token_count_present")),
        "token_pass_count": sum(1 for case in cases if case["token_pass"]),
        "reference_budget_pass_count": sum(1 for case in cases if case["reference_budget_pass"]),
        "routing_pass_count": sum(1 for case in cases if case["routing_pass"]),
        "overreach_pass_count": sum(1 for case in cases if case["overreach_pass"]),
    }


def validation_failures(cases: list[dict]) -> list[dict]:
    failures = []
    for case in cases:
        checks = HANDOFF_VALIDATION_CHECKS if case.get("expected_handoff") is not None else VALIDATION_CHECKS
        failed_checks = [check for check in checks if not case.get(check)]
        if failed_checks:
            failures.append(
                {
                    "case": case.get("case", "unknown"),
                    "failed_checks": failed_checks,
                }
            )
    return failures


def explain_failures_for_non_technical_users(cases: list[dict]) -> list[dict]:
    explanations = []
    for failure in validation_failures(cases):
        failed_checks = failure["failed_checks"]
        explanations.append(
            {
                "case": failure["case"],
                "what_failed": failed_checks,
                "why_it_matters": [
                    NON_TECH_FAILURE_REASONS.get(check, "The benchmark found a validation problem.")
                    for check in failed_checks
                ],
            }
        )
    return explanations
