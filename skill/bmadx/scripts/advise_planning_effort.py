#!/usr/bin/env python3
"""Recommend a model-supported planning effort from explicit task signals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "references" / "model-profiles.json"
EFFORT_ORDER = ("high", "xhigh", "max", "ultra")
CRITERIA = {
    "red_zone_or_irreversible": "Red-zone, destructive, or irreversible consequences",
    "cross_system_scope": "Several systems, repositories, or ownership boundaries",
    "ambiguous_ownership_or_requirements": "Unclear owner, requirements, or conflicting evidence",
    "long_horizon_or_compaction": "Long horizon with multiple phases or likely compaction",
    "repeated_failure_or_incident": "Repeated failed attempts, incident, or recovery state",
    "rollback_or_recovery_complexity": "Rollback, migration, or recovery is hard to prove",
    "weak_or_expensive_verification": "Verification is weak, slow, expensive, or indirect",
    "broad_decomposition_pressure": "Planning benefits from broad decomposition or delegated research",
}


def load_profiles(path: Path = PROFILES_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        raise RuntimeError(f"{path}: expected a profiles object")
    return profiles


def normalize_signals(values: list[str]) -> list[str]:
    signals: list[str] = []
    for value in values:
        for item in value.split(","):
            signal = item.strip().lower().replace("-", "_").replace(" ", "_")
            if not signal:
                continue
            if signal not in CRITERIA:
                raise ValueError(f"Unknown planning signal: {item.strip()}")
            if signal not in signals:
                signals.append(signal)
    return signals


def desired_effort(signals: list[str]) -> str:
    count = len(signals)
    if count <= 1:
        return "high"
    if count <= 3:
        return "xhigh"
    if count <= 5:
        return "max"
    if "broad_decomposition_pressure" in signals:
        return "ultra"
    return "max"


def cap_effort(desired: str, supported: list[str]) -> str:
    available = [effort for effort in EFFORT_ORDER if effort in supported]
    if not available:
        raise ValueError("Active model exposes no supported planning effort")
    desired_index = EFFORT_ORDER.index(desired)
    allowed = [effort for effort in available if EFFORT_ORDER.index(effort) <= desired_index]
    return allowed[-1] if allowed else available[0]


def build_report(model: str, signals: list[str], profiles: dict | None = None) -> dict:
    profiles = profiles or load_profiles()
    profile = profiles.get(model)
    if not isinstance(profile, dict):
        raise ValueError(f"Unknown BMADX model profile: {model}")
    desired = desired_effort(signals)
    supported = [str(value) for value in profile.get("supported_reasoning") or []]
    recommended = cap_effort(desired, supported)
    return {
        "model": model,
        "matched_signals": signals,
        "signal_count": len(signals),
        "signal_total": len(CRITERIA),
        "desired_effort": desired,
        "recommended_effort": recommended,
        "capped_by_model": recommended != desired,
        "operator_confirmation_required": recommended in {"max", "ultra"},
        "execution_effort_may_differ": True,
        "note": "Planning advice only; it does not change gear, BMAD gates, execution effort, or Codex config.",
    }


def format_line(report: dict) -> str:
    signals = ", ".join(report["matched_signals"]) or "no escalation signals"
    cap_note = " (model-capped)" if report["capped_by_model"] else ""
    return (
        f"Planning effort: {report['recommended_effort']}{cap_note} - "
        f"{report['signal_count']}/{report['signal_total']} signals: {signals}; "
        "suggestion only."
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend BMADX planning effort")
    parser.add_argument("--model", required=True, help="Active Codex model profile")
    parser.add_argument(
        "--signals",
        action="append",
        default=[],
        help="Comma-separated planning signals; repeatable",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--list-signals", action="store_true", help="List accepted signal names")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_signals:
        print(json.dumps(CRITERIA, indent=2) if args.json else "\n".join(CRITERIA))
        return 0
    try:
        signals = normalize_signals(args.signals)
        report = build_report(args.model.strip().lower(), signals)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else format_line(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
