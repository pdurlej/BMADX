"""Model-profile policy for BMADX benchmarks.

The Codex model catalog owns runtime capability. This module owns only the
BMADX policy layered on top of that capability: candidate status and the
reasoning effort suggested for each gear.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_PROFILES_PATH = REPO_ROOT / "skill" / "bmadx" / "references" / "model-profiles.json"


def load_model_profiles(path: Path = MODEL_PROFILES_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        raise RuntimeError(f"{path}: expected a profiles object")
    return payload


def profile_for_model(model: str) -> dict[str, Any] | None:
    profiles = load_model_profiles()["profiles"]
    profile = profiles.get(model.strip().lower())
    return dict(profile) if isinstance(profile, dict) else None


def supported_reasoning_efforts(model: str) -> tuple[str, ...]:
    profile = profile_for_model(model)
    if not profile:
        return ()
    return tuple(str(value) for value in profile.get("supported_reasoning") or ())


def advisor_reasoning(model: str, gear: str, fallback: str) -> str:
    profile = profile_for_model(model)
    if not profile:
        return fallback
    mapping = profile.get("advisor_by_gear") or {}
    return str(mapping.get(gear) or fallback)


def reasoning_prompt_contract(model: str) -> tuple[str, str]:
    profile = profile_for_model(model)
    if not profile:
        return "low|medium|high|xhigh", "X1/X2=medium, X3=high, X4=xhigh"
    allowed = "|".join(str(value) for value in profile.get("supported_reasoning") or ())
    mapping = profile.get("advisor_by_gear") or {}
    rendered_mapping = ", ".join(
        f"{gear}={mapping.get(gear, 'unconfigured')}" for gear in ("X1", "X2", "X3", "X4")
    )
    return allowed, rendered_mapping


def profile_snapshot(model: str) -> dict[str, Any]:
    profile = profile_for_model(model)
    if not profile:
        return {"model": model, "status": "unprofiled"}
    return {
        "model": model,
        "status": profile.get("status"),
        "minimum_codex_cli": profile.get("minimum_codex_cli"),
        "default_reasoning": profile.get("default_reasoning"),
        "supported_reasoning": profile.get("supported_reasoning"),
        "advisor_by_gear": profile.get("advisor_by_gear"),
    }


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)", value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def validate_model_options(
    model: str,
    reasoning: str,
    *,
    cli_version: str | None = None,
) -> list[str]:
    profile = profile_for_model(model)
    if not profile:
        return []

    failures: list[str] = []
    supported = supported_reasoning_efforts(model)
    if reasoning not in supported:
        failures.append(
            f"reasoning {reasoning!r} is not supported by {model}; choose one of: {', '.join(supported)}"
        )
    advisor_mapping = profile.get("advisor_by_gear") or {}
    for gear in ("X1", "X2", "X3", "X4"):
        if gear not in advisor_mapping:
            failures.append(f"profile advisor mapping for {model} is missing {gear}")
    for gear, effort in advisor_mapping.items():
        if effort not in supported:
            failures.append(
                f"profile advisor value {effort!r} for {model}/{gear} is outside supported reasoning"
            )

    minimum = profile.get("minimum_codex_cli")
    if minimum and cli_version:
        observed_version = parse_version(cli_version)
        minimum_version = parse_version(str(minimum))
        if observed_version is None:
            failures.append(f"could not parse Codex CLI version from {cli_version!r}")
        elif minimum_version and observed_version < minimum_version:
            failures.append(
                f"{model} requires Codex CLI >= {minimum}; observed {'.'.join(map(str, observed_version))}"
            )
    return failures
