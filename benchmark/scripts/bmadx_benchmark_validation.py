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
GOAL_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
    r"Goal(?:\*\*)?[ \t]*:[ \t]*(?:`|\*\*)?[ \t]*"
    r"(yes|no|recommended|not recommended|none)\b"
)
LOOP_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
    r"Loop(?:\*\*)?[ \t]*:[ \t]*(?:`|\*\*)?[ \t]*([^\r\n]+)"
)
THINKING_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
    r"Thinking(?:\*\*)?[ \t]*:[ \t]*(?:`|\*\*)?[ \t]*"
    r"(?:`|\*\*)?[ \t]*(minimal|low|medium|high|xhigh|extra[_ -]?high|x[_ -]?high|[a-z][a-z0-9_-]*)\b"
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
FORBIDDEN_GOAL_LOOP_RUNTIME_PATTERN = re.compile(
    r"\b(primary_worker|secondary_workers|worker lane|model lane|lane:|dispatch|"
    r"run_id|run ids?|runtime state|persistent state|persistent run ids?|MCP|"
    r"hooks?|plugins?|subagents?|workers?|agent zoo|"
    r"auto-merge|automerge|auto-deploy|autodeploy|daemon|scheduler)\b",
    re.I,
)
FORBIDDEN_THINKING_MUTATION_PATTERN = re.compile(
    r"(~/.codex/config\.toml|CODEX_HOME.*/config\.toml|"
    r"persist(?:ent|ently)?.*reasoning|write_config|set.*default.*reasoning|"
    r"mutate.*config|edit.*config\.toml)",
    re.I,
)
SUPPORTED_REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh"}
VALIDATION_CHECKS = (
    "format_pass",
    "token_count_present",
    "token_pass",
    "reference_budget_pass",
    "routing_pass",
    "overreach_pass",
    "thinking_budget_pass",
    "thinking_budget_no_mutation_pass",
    "thinking_budget_supported_value_pass",
)
HANDOFF_VALIDATION_CHECKS = VALIDATION_CHECKS + (
    "handoff_routing_pass",
    "handoff_not_runtime_pass",
    "no_worker_lane_pass",
    "no_model_name_pass",
    "no_dispatch_command_pass",
    "no_platform_surface_pass",
)
GOAL_LOOP_VALIDATION_CHECKS = (
    "goal_routing_pass",
    "loop_contract_pass",
    "goal_loop_not_runtime_pass",
)
NON_TECH_FAILURE_REASONS = {
    "format_pass": "The answer is too long or unstructured for a non-technical owner to act on safely.",
    "token_count_present": "The benchmark cannot compare cost or verbosity without a token count.",
    "token_pass": "The response exceeded the intended budget for lightweight work.",
    "reference_budget_pass": "The agent read extra reference docs where the happy path should stay compact.",
    "routing_pass": "The agent chose the wrong work mode, which can either overbuild a small task or underprotect a risky one.",
    "overreach_pass": "The agent mentioned forbidden higher gears, creating unnecessary escalation noise for a bounded task.",
    "thinking_budget_pass": "The suggested reasoning effort does not match the task's risk and process weight.",
    "thinking_budget_no_mutation_pass": "The answer tried to make reasoning effort a persistent config change instead of a per-task suggestion.",
    "thinking_budget_supported_value_pass": "The answer used a non-canonical reasoning effort instead of minimal, low, medium, high, or xhigh.",
    "handoff_routing_pass": "The agent did not make the expected broad-orchestrator handoff decision for this risk shape.",
    "handoff_not_runtime_pass": "The agent leaked orchestration runtime details instead of staying inside the BMADX handoff packet contract.",
    "no_worker_lane_pass": "The handoff suggested worker lanes, which would make BMADX behave like a runtime orchestrator.",
    "no_model_name_pass": "The handoff named specific models, which should remain a receiving orchestrator decision.",
    "no_dispatch_command_pass": "The handoff included dispatch/runtime commands instead of a portable risk-and-proof packet.",
    "no_platform_surface_pass": "The handoff mentioned platform surfaces such as MCP, hooks, plugins, or subagents that BMADX must not install or require.",
    "goal_routing_pass": "The agent did not make the expected `/goal` recommendation for a longer Codex task.",
    "loop_contract_pass": "The agent did not make the expected bounded repair-loop decision.",
    "goal_loop_not_runtime_pass": "The goal or loop answer drifted into runtime machinery instead of staying a small Codex-thread contract.",
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


def detect_goal(stdout: str) -> bool | None:
    match = GOAL_PATTERN.search(stdout)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value in {"yes", "recommended"}:
        return True
    if value in {"no", "not recommended", "none"}:
        return False
    return None


def detect_loop(stdout: str) -> bool | None:
    match = LOOP_PATTERN.search(stdout)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value.startswith(("yes", "bounded", "max ")):
        return True
    if value.startswith(("no", "none", "not recommended", "not needed")):
        return False
    return None


def normalize_reasoning_effort(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return {
        "extra_high": "xhigh",
        "x_high": "xhigh",
    }.get(normalized, normalized)


def detect_thinking_effort(stdout: str) -> str | None:
    match = THINKING_PATTERN.search(stdout)
    if not match:
        return None
    return normalize_reasoning_effort(match.group(1))


def validate_handoff_runtime_drift(stdout: str) -> dict:
    result = {}
    for key, pattern in FORBIDDEN_HANDOFF_RUNTIME_PATTERNS.items():
        result[key] = pattern.search(stdout) is None
    result["handoff_not_runtime_pass"] = all(result.values())
    return result


def validate_goal_loop_runtime_drift(stdout: str) -> bool:
    return FORBIDDEN_GOAL_LOOP_RUNTIME_PATTERN.search(stdout) is None


def validate_case(stdout: str, stderr: str, tokens: int | None, spec: dict) -> dict:
    response = stdout.strip()
    lines = [line for line in response.splitlines() if line.strip()]
    observed_gears = detect_observed_gears(stdout)
    selected_gear = detect_selected_gear(stdout)
    reference_reads = detect_reference_reads(stderr)
    expected_gear = str(spec.get("expected_gear") or "")
    forbidden_gears = set(spec.get("forbidden_gears") or [])
    expected_handoff = spec.get("expected_handoff")
    expected_goal = spec.get("expected_goal")
    expected_loop = spec.get("expected_loop")
    expected_reasoning_effort = normalize_reasoning_effort(spec.get("expected_reasoning_effort"))
    observed_reasoning_effort = detect_thinking_effort(stdout)
    observed_goal = detect_goal(stdout)
    observed_loop = detect_loop(stdout)
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
    goal_routing_pass = (
        observed_goal == bool(expected_goal)
        if expected_goal is not None
        else True
    )
    loop_contract_pass = (
        observed_loop == bool(expected_loop)
        if expected_loop is not None
        else True
    )
    goal_loop_not_runtime_pass = (
        validate_goal_loop_runtime_drift(stdout)
        if expected_goal is not None or expected_loop is not None
        else True
    )
    thinking_budget_present = observed_reasoning_effort is not None
    thinking_budget_supported_value_pass = (
        observed_reasoning_effort in SUPPORTED_REASONING_EFFORTS
        if thinking_budget_present
        else expected_reasoning_effort is None
    )
    thinking_budget_pass = (
        observed_reasoning_effort == expected_reasoning_effort
        if expected_reasoning_effort
        else True
    )
    thinking_budget_no_mutation_pass = FORBIDDEN_THINKING_MUTATION_PATTERN.search(stdout) is None

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
        "expected_goal": expected_goal,
        "observed_goal": observed_goal,
        "goal_routing_pass": goal_routing_pass,
        "expected_loop": expected_loop,
        "observed_loop": observed_loop,
        "loop_contract_pass": loop_contract_pass,
        "goal_loop_not_runtime_pass": goal_loop_not_runtime_pass,
        "expected_reasoning_effort": expected_reasoning_effort,
        "observed_reasoning_effort": observed_reasoning_effort,
        "thinking_budget_present": thinking_budget_present,
        "thinking_budget_pass": thinking_budget_pass,
        "thinking_budget_no_mutation_pass": thinking_budget_no_mutation_pass,
        "thinking_budget_supported_value_pass": thinking_budget_supported_value_pass,
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
            "thinking_budget_present_count": 0,
            "thinking_budget_pass_count": 0,
            "thinking_budget_no_mutation_pass_count": 0,
            "thinking_budget_supported_value_pass_count": 0,
            "goal_routing_pass_count": 0,
            "loop_contract_pass_count": 0,
            "goal_loop_not_runtime_pass_count": 0,
        }
    return {
        "case_count": len(cases),
        "format_pass_count": sum(1 for case in cases if case["format_pass"]),
        "token_count_present_count": sum(1 for case in cases if case.get("token_count_present")),
        "token_pass_count": sum(1 for case in cases if case["token_pass"]),
        "reference_budget_pass_count": sum(1 for case in cases if case["reference_budget_pass"]),
        "routing_pass_count": sum(1 for case in cases if case["routing_pass"]),
        "overreach_pass_count": sum(1 for case in cases if case["overreach_pass"]),
        "thinking_budget_present_count": sum(1 for case in cases if case.get("thinking_budget_present")),
        "thinking_budget_pass_count": sum(1 for case in cases if case.get("thinking_budget_pass")),
        "thinking_budget_no_mutation_pass_count": sum(
            1 for case in cases if case.get("thinking_budget_no_mutation_pass")
        ),
        "thinking_budget_supported_value_pass_count": sum(
            1 for case in cases if case.get("thinking_budget_supported_value_pass")
        ),
        "goal_routing_pass_count": sum(1 for case in cases if case.get("goal_routing_pass")),
        "loop_contract_pass_count": sum(1 for case in cases if case.get("loop_contract_pass")),
        "goal_loop_not_runtime_pass_count": sum(
            1 for case in cases if case.get("goal_loop_not_runtime_pass")
        ),
    }


def validation_failures(cases: list[dict]) -> list[dict]:
    failures = []
    for case in cases:
        checks = list(VALIDATION_CHECKS)
        if case.get("expected_handoff") is not None:
            checks.extend(check for check in HANDOFF_VALIDATION_CHECKS if check not in checks)
        if case.get("expected_goal") is not None or case.get("expected_loop") is not None:
            checks.extend(GOAL_LOOP_VALIDATION_CHECKS)
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
