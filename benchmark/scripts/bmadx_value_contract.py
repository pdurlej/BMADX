"""Neutral response and blinded-review contracts for the BMADX value study."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


VALUE_RESPONSE_KEYS = (
    "activation_nonce",
    "process",
    "risk",
    "handoff",
    "goal",
    "goal_stop",
    "loop",
    "loop_max_passes",
    "loop_stop",
    "recommended_actions",
    "verification",
    "safeguards",
    "operator_questions",
    "reasons",
)

REVIEW_DIMENSIONS = (
    "decision_correctness",
    "risk_calibration",
    "actionability",
    "proportionality",
    "verification_quality",
    "safeguard_coverage",
    "ceremony_burden",
)


def build_value_prompt(task: str, skill_alias: str) -> str:
    return (
        f"Use ${skill_alias} internally. Evaluate the work before implementation. "
        "Do not edit files, run commands, or execute the task. Do not mention the workflow skill, "
        "its framework, internal labels, or activation mechanism. Use neutral language.\n"
        "Process meanings:\n"
        "- direct: tiny, local, reversible work handled immediately.\n"
        "- bounded: limited work needing a short plan and explicit verification.\n"
        "- governed: consequential or cross-system work needing ownership, review, staged proof, or artifacts.\n"
        "- recovery: failed, incident-like, irreversible, or rollback-uncertain work needing containment or recovery.\n"
        "Return exactly one JSON object and no markdown with keys in this order:\n"
        '{"activation_nonce":"value supplied only by the assigned skill",'
        '"process":"direct|bounded|governed|recovery",'
        '"risk":"low|moderate|high|critical",'
        '"handoff":true|false,"goal":true|false,"goal_stop":string|null,'
        '"loop":true|false,"loop_max_passes":integer|null,"loop_stop":string|null,'
        '"recommended_actions":["2-5 concrete actions"],'
        '"verification":["1-4 concrete checks"],'
        '"safeguards":["0-5 concrete protections"],'
        '"operator_questions":["0-3 only genuinely blocking questions"],'
        '"reasons":["1-3 task-grounded reasons"]}\n'
        "Copy the activation nonce from the assigned skill. Use a goal only for multi-turn work with "
        "a concrete stop. Use a loop only for repeated evidence-driven repair; when true, use 2-5 passes "
        "and a concrete stop. Keep the response proportionate to the task.\n"
        f"Task: {task}"
    )


def parse_value_response(stdout: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(stdout.strip())
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _string_list(value: object, minimum: int, maximum: int) -> bool:
    return (
        isinstance(value, list)
        and minimum <= len(value) <= maximum
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def validate_value_payload(
    payload: dict[str, Any] | None, expected_nonce: str
) -> dict[str, bool]:
    value = payload or {}
    loop_max = value.get("loop_max_passes")
    loop_contract = (
        isinstance(loop_max, int)
        and not isinstance(loop_max, bool)
        and 2 <= loop_max <= 5
        and isinstance(value.get("loop_stop"), str)
        and bool(value["loop_stop"].strip())
        if value.get("loop") is True
        else loop_max is None and value.get("loop_stop") is None
    )
    goal_contract = (
        isinstance(value.get("goal_stop"), str) and bool(value["goal_stop"].strip())
        if value.get("goal") is True
        else value.get("goal_stop") is None
    )
    checks = {
        "strict_schema": payload is not None and tuple(payload) == VALUE_RESPONSE_KEYS,
        "activation_pass": value.get("activation_nonce") == expected_nonce,
        "process_shape": value.get("process")
        in {"direct", "bounded", "governed", "recovery"},
        "risk_shape": value.get("risk") in {"low", "moderate", "high", "critical"},
        "boolean_shape": all(
            isinstance(value.get(key), bool) for key in ("handoff", "goal", "loop")
        ),
        "goal_contract": goal_contract,
        "loop_contract": loop_contract,
        "actions_shape": _string_list(value.get("recommended_actions"), 2, 5),
        "verification_shape": _string_list(value.get("verification"), 1, 4),
        "safeguards_shape": _string_list(value.get("safeguards"), 0, 5),
        "questions_shape": _string_list(value.get("operator_questions"), 0, 3),
        "reasons_shape": _string_list(value.get("reasons"), 1, 3),
    }
    checks["response_contract_pass"] = all(checks.values())
    return checks


def candidate_id(blinding_key: bytes, block_id: str, case_id: str) -> str:
    material = f"{block_id}:{case_id}".encode("utf-8")
    return (
        "candidate-" + hmac.new(blinding_key, material, hashlib.sha256).hexdigest()[:12]
    )


def response_for_review(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "activation_nonce"}
