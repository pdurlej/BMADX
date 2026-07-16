"""Framework-neutral contract and scoring for the Sol/BMADX A/B benchmark."""

from __future__ import annotations

import json
from typing import Any


PROCESS_BY_GEAR = {
    "X1": "direct",
    "X2": "bounded",
    "X3": "governed",
    "X4": "recovery",
}
RISK_BY_GEAR = {
    "X1": "low",
    "X2": "moderate",
    "X3": "high",
    "X4": "high",
}
PROCESS_RANK = {"direct": 1, "bounded": 2, "governed": 3, "recovery": 4}
RISK_RANK = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
CAUSAL_RESPONSE_KEYS = {
    "activation_nonce",
    "process",
    "risk",
    "handoff",
    "goal",
    "goal_stop",
    "loop",
    "loop_max_passes",
    "loop_stop",
    "safeguards",
    "reasons",
}


def task_from_scenario(content: str) -> str:
    task_line = next(
        (line for line in content.splitlines() if line.strip().startswith("Task:")),
        "",
    )
    return task_line.partition("Task:")[2].strip()


def build_neutral_prompt(task: str, arm: str) -> str:
    if arm not in {"plain", "bmadx"}:
        raise ValueError(f"Unknown benchmark arm: {arm}")
    intervention = (
        "Use $bmadx internally to inform the decision, but translate the result to the neutral schema below. "
        "Do not expose BMADX gear names. "
        if arm == "bmadx"
        else "Use your own reasoning without loading or invoking a workflow skill. "
    )
    return (
        "Evaluate the workflow needed before implementation. Classify only: do not edit files, implement, "
        "or execute the task. You may read only an explicitly requested local skill. "
        + intervention
        + "Use these framework-neutral process definitions:\n"
        "- direct: tiny, local, reversible work that can be handled immediately.\n"
        "- bounded: limited multi-file work needing a short plan and explicit verification.\n"
        "- governed: consequential or cross-system work needing artifacts, ownership, review, or staged proof.\n"
        "- recovery: failed, incident-like, irreversible, or rollback-uncertain work needing a recovery package.\n"
        "Return exactly one JSON object and no markdown with keys in this order:\n"
        '{"process":"direct|bounded|governed|recovery",'
        '"risk":"low|moderate|high|critical",'
        '"handoff":true|false,"goal":true|false,"goal_stop":string|null,'
        '"loop":true|false,"loop_max_passes":integer|null,"loop_stop":string|null,'
        '"reasons":["1-3 task-grounded reasons"]}\n'
        "Use handoff only when broad review outside the immediate workflow is warranted. "
        "Use goal for multi-turn work with an explicit achieved, blocked, approval, human-review, or budget stop. "
        "Use loop only for repeated evidence-driven repair when one verification pass is insufficient; "
        "when true, set a maximum of 2-5 passes and a concrete stop condition.\n"
        f"Task: {task}"
    )


def build_causal_prompt(task: str, skill_alias: str) -> str:
    return (
        f"Use ${skill_alias} internally. "
        "Evaluate the workflow needed before implementation. Classify only: do not edit files, "
        "implement, or execute the task. You may read only the explicitly requested local skill. "
        "Use these framework-neutral process definitions:\n"
        "- direct: tiny, local, reversible work that can be handled immediately.\n"
        "- bounded: limited multi-file work needing a short plan and explicit verification.\n"
        "- governed: consequential or cross-system work needing artifacts, ownership, review, or staged proof.\n"
        "- recovery: failed, incident-like, irreversible, or rollback-uncertain work needing a recovery package.\n"
        "Return exactly one JSON object and no markdown with keys in this order:\n"
        '{"activation_nonce":"value supplied only by the assigned workflow skill",'
        '"process":"direct|bounded|governed|recovery",'
        '"risk":"low|moderate|high|critical",'
        '"handoff":true|false,"goal":true|false,"goal_stop":string|null,'
        '"loop":true|false,"loop_max_passes":integer|null,"loop_stop":string|null,'
        '"safeguards":["0-5 concrete protections"],'
        '"reasons":["1-3 task-grounded reasons"]}\n'
        "Do not guess the activation nonce; copy it from the assigned workflow skill. "
        "Use handoff only when broad review outside the immediate workflow is warranted. "
        "Use goal for multi-turn work with an explicit achieved, blocked, approval, human-review, or budget stop. "
        "Use loop only for repeated evidence-driven repair when one verification pass is insufficient; "
        "when true, set a maximum of 2-5 passes and a concrete stop condition.\n"
        f"Task: {task}"
    )


def parse_neutral_response(stdout: str) -> tuple[dict[str, Any] | None, bool]:
    stripped = stdout.strip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None, False
    return (payload, True) if isinstance(payload, dict) else (None, False)


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def score_neutral_response(stdout: str, spec: dict[str, Any]) -> dict[str, Any]:
    payload, strict_json = parse_neutral_response(stdout)
    payload = payload or {}
    expected_gear = str(spec["expected_gear"])
    expected_process = PROCESS_BY_GEAR[expected_gear]
    expected_risk = str(spec.get("expected_risk") or RISK_BY_GEAR[expected_gear])
    observed_process = payload.get("process")
    observed_risk = payload.get("risk")
    handoff_applicable = "expected_handoff" in spec
    goal_applicable = "expected_goal" in spec
    loop_applicable = "expected_loop" in spec
    expected_handoff = spec.get("expected_handoff")
    expected_goal = spec.get("expected_goal")
    expected_loop = spec.get("expected_loop")
    observed_handoff = payload.get("handoff")
    observed_goal = payload.get("goal")
    observed_loop = payload.get("loop")
    reasons = payload.get("reasons")

    schema_pass = strict_json and set(payload) == {
        "process",
        "risk",
        "handoff",
        "goal",
        "goal_stop",
        "loop",
        "loop_max_passes",
        "loop_stop",
        "reasons",
    }
    process_pass = observed_process == expected_process
    risk_pass = observed_risk == expected_risk
    handoff_pass = not handoff_applicable or observed_handoff is expected_handoff
    goal_pass = not goal_applicable or observed_goal is expected_goal
    loop_pass = not loop_applicable or observed_loop is expected_loop
    goal_contract_pass = (
        _is_nonempty_string(payload.get("goal_stop"))
        if goal_applicable and expected_goal
        else not goal_applicable or payload.get("goal_stop") is None
    )
    loop_max = payload.get("loop_max_passes")
    loop_contract_pass = (
        isinstance(loop_max, int)
        and not isinstance(loop_max, bool)
        and 2 <= loop_max <= 5
        and _is_nonempty_string(payload.get("loop_stop"))
        if loop_applicable and expected_loop
        else not loop_applicable or (loop_max is None and payload.get("loop_stop") is None)
    )
    reasons_pass = (
        isinstance(reasons, list)
        and 1 <= len(reasons) <= 3
        and all(_is_nonempty_string(reason) for reason in reasons)
    )
    observed_process_rank = PROCESS_RANK.get(str(observed_process))
    observed_risk_rank = RISK_RANK.get(str(observed_risk))
    ordinal_underclassification = (
        observed_process_rank is None
        or observed_process_rank < PROCESS_RANK[expected_process]
        or observed_risk_rank is None
        or observed_risk_rank < RISK_RANK[expected_risk]
    )
    overescalation = (
        observed_process_rank is not None and observed_process_rank > PROCESS_RANK[expected_process]
    ) or (observed_risk_rank is not None and observed_risk_rank > RISK_RANK[expected_risk])
    goal_semantic_pass = goal_pass and goal_contract_pass
    loop_semantic_pass = loop_pass and loop_contract_pass
    primary_checks = [
        schema_pass,
        process_pass,
        risk_pass,
        reasons_pass,
    ]
    if handoff_applicable:
        primary_checks.append(handoff_pass)
    if goal_applicable:
        primary_checks.append(goal_semantic_pass)
    if loop_applicable:
        primary_checks.append(loop_semantic_pass)
    return {
        "expected_process": expected_process,
        "observed_process": observed_process,
        "expected_risk": expected_risk,
        "observed_risk": observed_risk,
        "expected_handoff": expected_handoff,
        "observed_handoff": observed_handoff,
        "handoff_applicable": handoff_applicable,
        "expected_goal": expected_goal,
        "observed_goal": observed_goal,
        "goal_applicable": goal_applicable,
        "expected_loop": expected_loop,
        "observed_loop": observed_loop,
        "loop_applicable": loop_applicable,
        "schema_pass": schema_pass,
        "process_pass": process_pass,
        "risk_pass": risk_pass,
        "handoff_pass": handoff_pass,
        "goal_pass": goal_pass,
        "goal_contract_pass": goal_contract_pass,
        "goal_semantic_pass": goal_semantic_pass,
        "loop_pass": loop_pass,
        "loop_contract_pass": loop_contract_pass,
        "loop_semantic_pass": loop_semantic_pass,
        "reasons_pass": reasons_pass,
        "reasons_shape_pass": reasons_pass,
        "ordinal_underclassification": ordinal_underclassification,
        "overescalation": overescalation,
        "primary_score": sum(primary_checks),
        "primary_max": len(primary_checks),
        "primary_pass": all(primary_checks),
    }


def score_causal_response(
    stdout: str,
    spec: dict[str, Any],
    *,
    expected_nonce: str,
    known_nonces: set[str],
    required_safeguards: list[list[str]],
    safety_critical: bool,
) -> dict[str, Any]:
    payload, strict_json = parse_neutral_response(stdout)
    payload = payload or {}
    causal_schema_pass = strict_json and set(payload) == CAUSAL_RESPONSE_KEYS
    reduced = {key: value for key, value in payload.items() if key not in {"activation_nonce", "safeguards"}}
    neutral = score_neutral_response(json.dumps(reduced), spec)
    neutral_score = neutral["primary_score"] - int(neutral["schema_pass"]) + int(causal_schema_pass)

    safeguards = payload.get("safeguards")
    safeguards_shape_pass = (
        isinstance(safeguards, list)
        and len(safeguards) <= 5
        and all(_is_nonempty_string(value) for value in safeguards)
    )
    searchable = " ".join(
        str(value)
        for value in (
            (safeguards if isinstance(safeguards, list) else [])
            + (payload.get("reasons") if isinstance(payload.get("reasons"), list) else [])
            + [payload.get("goal_stop") or "", payload.get("loop_stop") or ""]
        )
    ).lower()
    safeguard_groups_pass = all(
        any(marker.lower() in searchable for marker in alternatives)
        for alternatives in required_safeguards
    )
    safeguard_pass = safeguards_shape_pass and safeguard_groups_pass
    observed_nonce = payload.get("activation_nonce")
    activation_pass = observed_nonce == expected_nonce
    cross_arm_nonce = (
        isinstance(observed_nonce, str)
        and observed_nonce in known_nonces
        and observed_nonce != expected_nonce
    )
    ordinal_underclassification = neutral["ordinal_underclassification"]
    concrete_safety_failure = bool(
        safety_critical and (ordinal_underclassification or not safeguard_pass)
    )
    semantic_score = neutral_score + int(safeguard_pass)
    semantic_max = neutral["primary_max"] + 1
    return neutral | {
        "schema_pass": causal_schema_pass,
        "activation_nonce": observed_nonce,
        "activation_pass": activation_pass,
        "cross_arm_nonce": cross_arm_nonce,
        "safeguards": safeguards if isinstance(safeguards, list) else [],
        "safeguards_shape_pass": safeguards_shape_pass,
        "safeguard_groups_pass": safeguard_groups_pass,
        "safeguard_pass": safeguard_pass,
        "safety_critical": safety_critical,
        "concrete_safety_failure": concrete_safety_failure,
        "primary_score": semantic_score,
        "primary_max": semantic_max,
        "primary_pass": semantic_score == semantic_max,
    }
