#!/usr/bin/env python3
"""Check BMADX health, enforce BMAD dependency, and track local drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SKILL_NAME = "bmadx"
DEPENDENCY_SKILL = "bmad-method-codex"
GEARS = ("X1", "X2", "X3", "X4")
SOFT_GATE_GEARS = {"X1", "X2"}
HARD_GATE_GEARS = {"X3", "X4"}
FAST_PATH_WARNING = (
    "No fresh healthy BMAD snapshot is available; the `X1/X2` decision is using local BMADX state."
)
FAST_PATH_HARD_BLOCKER = "No fresh BMAD check is available for `X3/X4`."
HARD_BLOCK_REMEDIATION = (
    "Restore a complete local bmad-method-codex skill, then rerun the BMADX compact gate."
)
BMAD_REQUIRED_FILES = (
    "SKILL.md",
    "references/skill-manifest.json",
    "scripts/sync_bmad_method.py",
)
ADVISORY_BMAD_REFERENCES = {"latest-release-summary.md"}

ROOT = Path(os.environ.get("BMADX_ROOT", Path(__file__).resolve().parents[1]))
MANIFEST_FILE = Path(
    os.environ.get("BMADX_MANIFEST_FILE", ROOT / "references" / "skill-manifest.json")
)
STATE_FILE = Path(os.environ.get("BMADX_STATE_FILE", ROOT / "state" / "bmadx-state.json"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def remediation_steps() -> list[str]:
    return [HARD_BLOCK_REMEDIATION]


def normalize_gear(value: str | None) -> str | None:
    if value is None:
        return None
    gear = value.strip().upper()
    if not gear:
        return None
    if gear not in GEARS:
        raise argparse.ArgumentTypeError(f"Unsupported gear: {value}")
    return gear


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(payload)
    body["last_updated_at"] = _now_iso()
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def try_write_json(path: Path, payload: dict) -> str | None:
    try:
        write_json(path, payload)
    except OSError as exc:
        return f"Could not persist BMADX state at {path}: {exc}"
    return None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def read_manifest() -> dict:
    data = read_json(MANIFEST_FILE, {})
    return data if isinstance(data, dict) else {}


def discover_bmad_path() -> Path:
    env_path = os.environ.get("BMADX_BMAD_SKILL_PATH")
    if env_path:
        return Path(env_path)

    return codex_home() / "skills" / DEPENDENCY_SKILL


def run_bmad_check(bmad_path: Path) -> dict:
    if not bmad_path.exists():
        return {
            "available": False,
            "path": str(bmad_path),
            "action": "needs_attention",
            "warnings": [f"BMAD dependency is missing at {bmad_path}."],
            "checked_live": True,
            "cache_used": False,
            "status_source": "local-read-only",
        }

    missing = [rel for rel in BMAD_REQUIRED_FILES if not (bmad_path / rel).is_file()]
    manifest = read_json(bmad_path / "references" / "skill-manifest.json", {})
    state = read_json(bmad_path / "state" / "bmad-release-state.json", {})
    skill_version = str(manifest.get("skill_version") or "") if isinstance(manifest, dict) else ""
    warnings: list[str] = []
    if missing:
        warnings.append("BMAD is missing required local files: " + ", ".join(missing))
    if not skill_version:
        warnings.append("BMAD has no readable local skill version.")

    release = state.get("release") if isinstance(state, dict) else {}
    release_tag = str((release or {}).get("tag_name") or "")
    agent_health = state.get("agent_health") if isinstance(state, dict) else {}
    if isinstance(agent_health, dict) and agent_health.get("versions_match") is False:
        warnings.append(
            "BMAD recorded a local skill-version mismatch; review the installation when convenient."
        )

    healthy = not missing and bool(skill_version)
    action = "ok" if healthy and not warnings else "warning" if healthy else "needs_attention"

    return {
        "available": True,
        "healthy": healthy,
        "path": str(bmad_path),
        "action": action,
        "warnings": warnings,
        "release_tag": release_tag,
        "payload": {
            "local_skill_version": skill_version,
            "state_available": bool(state),
        },
        "checked_live": True,
        "cache_used": False,
        "status_source": "local-read-only",
    }


def should_use_fast_path(mode: str, requested_gear: str | None) -> bool:
    return mode in {"check", "report"} and requested_gear in SOFT_GATE_GEARS


def build_fast_path_bmad(bmad_path: Path, cached_healthy_bmad: dict) -> dict:
    cached_release = str(cached_healthy_bmad.get("release_tag") or "")
    if cached_healthy_bmad:
        return {
            "available": True,
            "healthy": True,
            "path": str(bmad_path),
            "action": "ok",
            "warnings": [],
            "release_tag": cached_release,
            "payload": {},
            "checked_live": False,
            "cache_used": True,
            "status_source": "cache",
        }

    return {
        "available": bmad_path.exists(),
        "healthy": False,
        "path": str(bmad_path),
        "action": "warning",
        "warnings": [FAST_PATH_WARNING],
        "release_tag": cached_release,
        "payload": {},
        "checked_live": False,
        "cache_used": False,
        "status_source": "local-only",
    }


def collect_hashes(root: Path, paths: Iterable[str]) -> Tuple[Dict[str, str], List[str]]:
    hashes: Dict[str, str] = {}
    missing: List[str] = []
    for rel in paths:
        target = root / rel
        if not target.exists():
            missing.append(rel)
            continue
        hashes[rel] = file_sha(target)
    return hashes, missing


def collect_bmad_reference_hashes(bmad_root: Path, refs: Iterable[str]) -> Tuple[Dict[str, str], List[str]]:
    hashes: Dict[str, str] = {}
    missing: List[str] = []
    for name in refs:
        target = bmad_root / "references" / "upstream" / name
        if not target.exists():
            missing.append(name)
            continue
        hashes[name] = file_sha(target)
    return hashes, missing


def compute_delta(current: Dict[str, str], previous: Dict[str, str]) -> List[str]:
    changed: List[str] = []
    for key in sorted(set(current) | set(previous)):
        if current.get(key) != previous.get(key):
            changed.append(key)
    return changed


def validate_templates(root: Path, template_checks: dict) -> List[str]:
    failures: List[str] = []
    for rel, required_strings in template_checks.items():
        target = root / rel
        if not target.exists():
            failures.append(f"Missing template: {rel}")
            continue
        content = target.read_text(encoding="utf-8")
        for needle in required_strings:
            if needle not in content:
                failures.append(f"Template {rel} is missing required text: {needle}")
    return failures


def validate_layout_markers(root: Path, tracked_files: Iterable[str], expected_layout_paths: Iterable[str]) -> List[str]:
    failures: List[str] = []
    loaded: List[str] = []
    for rel in tracked_files:
        target = root / rel
        if target.exists():
            try:
                loaded.append(target.read_text(encoding="utf-8"))
            except OSError:
                continue

    haystack = "\n".join(loaded)
    for marker in expected_layout_paths:
        if marker not in haystack:
            failures.append(f"Missing expected BMAD layout marker: {marker}")
    return failures


def build_warnings(
    *,
    bmad: dict,
    missing_local: List[str],
    missing_bmad_refs: List[str],
    template_failures: List[str],
    local_delta: List[str],
    bmad_delta: List[str],
    previous_release: str,
    current_release: str,
    mode: str,
    first_local_run: bool,
    first_bmad_run: bool,
) -> List[str]:
    warnings: List[str] = []

    warnings.extend(bmad.get("warnings", []))

    if missing_local:
        warnings.append("Missing required BMADX files: " + ", ".join(sorted(missing_local)))

    hard_missing_refs = [
        name for name in missing_bmad_refs if name not in ADVISORY_BMAD_REFERENCES
    ]
    if hard_missing_refs:
        warnings.append(
            "Missing required BMAD references: " + ", ".join(sorted(hard_missing_refs))
        )

    warnings.extend(template_failures)

    release_changed = bool(previous_release and current_release and previous_release != current_release)
    if release_changed and mode in {"check", "report"}:
        warnings.append(
            f"Detected a BMAD release change ({previous_release} -> {current_release}). "
            "The local BMAD capability remains usable; review the update when convenient."
        )

    if bmad_delta and mode in {"check", "report"} and not first_bmad_run:
        warnings.append(
            "Detected a change in required BMAD references since the last saved state: "
            + ", ".join(bmad_delta)
        )

    if local_delta and mode in {"check", "report"} and not first_local_run:
        warnings.append(
            "Detected a change in BMADX files since the last saved state: "
            + ", ".join(local_delta)
        )

    return warnings


def get_cached_healthy_bmad(state: dict) -> dict:
    cached = state.get("last_healthy_bmad")
    return cached if isinstance(cached, dict) else {}


def build_local_blockers(
    *,
    missing_local: List[str],
    template_failures: List[str],
    layout_failures: List[str],
) -> List[str]:
    blockers: List[str] = []
    if missing_local:
        blockers.append("Required BMADX files are missing.")
    if template_failures:
        blockers.append("BMADX templates failed validation.")
    if layout_failures:
        blockers.append("Expected BMAD layout markers are missing.")
    return blockers


def build_dependency_blockers(
    *,
    bmad: dict,
    missing_bmad_refs: List[str],
) -> List[str]:
    blockers: List[str] = []
    if not bmad.get("checked_live", True):
        return blockers

    if not bmad.get("available"):
        blockers.append("The BMAD dependency is not available.")
    elif not bmad.get("healthy"):
        blockers.append("The current BMAD check is not healthy.")
        blockers.extend(str(warning) for warning in bmad.get("warnings", []) if warning)

    hard_missing_refs = [
        name for name in missing_bmad_refs if name not in ADVISORY_BMAD_REFERENCES
    ]
    if hard_missing_refs:
        blockers.append("Required BMAD references are missing.")

    return blockers


def build_execution_gate(
    *,
    classification_allowed: bool,
    requested_gear: str | None,
    local_blockers: List[str],
    hard_dependency_blockers: List[str],
) -> Tuple[Dict[str, dict], bool]:
    by_gear: Dict[str, dict] = {}
    for gear in GEARS:
        gear_blockers = list(local_blockers)
        if gear in HARD_GATE_GEARS:
            gear_blockers.extend(hard_dependency_blockers)

        allowed = classification_allowed and not gear_blockers
        by_gear[gear] = {
            "allowed": allowed,
            "gate": "soft" if gear in SOFT_GATE_GEARS else "hard",
            "blockers": gear_blockers,
        }

    if requested_gear:
        return by_gear, by_gear[requested_gear]["allowed"]

    return by_gear, classification_allowed and not local_blockers and not hard_dependency_blockers


def summarize_warning(
    *,
    classification_allowed: bool,
    requested_gear: str | None,
    execution_allowed: bool,
    bmad: dict,
    cached_healthy_bmad: dict,
    execution_blockers: List[str],
    warnings: List[str],
) -> str | None:
    if not classification_allowed:
        return "Local BMADX state needs attention before classification and execution."

    if requested_gear and not execution_allowed:
        if execution_blockers:
            return (
                f"Classification is still allowed, but execution for `{requested_gear}` "
                "is blocked: " + "; ".join(execution_blockers)
            )
        return (
            f"Classification is still allowed, but execution for `{requested_gear}` "
            "is blocked until the local BMAD dependency is repaired and usable."
        )

    if requested_gear in SOFT_GATE_GEARS and not bmad.get("checked_live", True):
        if bmad.get("cache_used"):
            return None
        return FAST_PATH_WARNING

    if not bmad.get("healthy", False):
        cached_at = str(cached_healthy_bmad.get("checked_at") or "")
        if cached_at:
            return (
                "BMAD is not fully healthy right now; for `X1/X2` this remains a warning, "
                f"and the last healthy state was saved at {cached_at}."
            )
        return (
            "BMAD is not fully healthy right now; for `X1/X2` this remains a warning, "
            "and for `X3/X4` it blocks execution."
        )

    if warnings:
        return warnings[0]

    return None


def determine_bmad_status(*, bmad: dict, requested_gear: str | None, execution_allowed: bool) -> str:
    if not bmad.get("checked_live", True):
        return "ok" if bmad.get("cache_used") else "warning"

    if requested_gear in HARD_GATE_GEARS and not execution_allowed:
        return "needs_attention"

    if bmad.get("healthy"):
        return "warning" if bmad.get("warnings") else "ok"

    if requested_gear in SOFT_GATE_GEARS and execution_allowed:
        return "warning"

    return "needs_attention"


def build_remediation(*, requested_gear: str | None, execution_allowed: bool, dependency_blockers: List[str]) -> List[str]:
    if requested_gear in HARD_GATE_GEARS and not execution_allowed:
        return remediation_steps()
    if requested_gear is None and dependency_blockers:
        return remediation_steps()
    return []


def build_gate_decision(
    *,
    requested_gear: str | None,
    local_blockers: List[str],
    dependency_blockers: List[str],
    use_fast_path: bool,
    bmad: dict,
    cached_healthy_bmad: dict,
    warnings: List[str],
) -> dict:
    classification_allowed = len(local_blockers) == 0
    hard_dependency_blockers = list(dependency_blockers)
    if use_fast_path:
        hard_dependency_blockers.append(FAST_PATH_HARD_BLOCKER)

    execution_gate, execution_allowed = build_execution_gate(
        classification_allowed=classification_allowed,
        requested_gear=requested_gear,
        local_blockers=local_blockers,
        hard_dependency_blockers=hard_dependency_blockers,
    )
    requested_execution_blockers = execution_gate[requested_gear]["blockers"] if requested_gear else []
    warning_summary = summarize_warning(
        classification_allowed=classification_allowed,
        requested_gear=requested_gear,
        execution_allowed=execution_allowed,
        bmad=bmad,
        cached_healthy_bmad=cached_healthy_bmad,
        execution_blockers=requested_execution_blockers,
        warnings=warnings,
    )
    bmad_status = determine_bmad_status(
        bmad=bmad,
        requested_gear=requested_gear,
        execution_allowed=execution_allowed,
    )
    remediation = build_remediation(
        requested_gear=requested_gear,
        execution_allowed=execution_allowed,
        dependency_blockers=dependency_blockers,
    )

    action = "ok"
    if not classification_allowed or (requested_gear and not execution_allowed):
        action = "needs_attention"
    elif warnings or warning_summary:
        action = "warning"

    return {
        "classification_allowed": classification_allowed,
        "execution_allowed": execution_allowed,
        "execution_gate": execution_gate,
        "requested_execution_blockers": requested_execution_blockers,
        "warning_summary": warning_summary,
        "bmad_status": bmad_status,
        "remediation": remediation,
        "action": action,
        "current_bmad_ready": bool(bmad.get("healthy") and not dependency_blockers),
    }


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check BMADX health and dependency status")
    parser.add_argument(
        "mode",
        nargs="?",
        default="check",
        choices=("check", "report", "sync"),
        help="Check/report status or sync the saved state",
    )
    parser.add_argument(
        "--gear",
        type=normalize_gear,
        help="Evaluate the execution gate for a specific gear: X1, X2, X3, or X4",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact machine-oriented output for skill routing and benchmarks",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = read_manifest()
    state = read_json(STATE_FILE, {})
    previous_local = state.get("local_hashes", {}) if isinstance(state.get("local_hashes"), dict) else {}
    previous_bmad_refs = state.get("bmad_reference_hashes", {}) if isinstance(state.get("bmad_reference_hashes"), dict) else {}
    previous_release = str(state.get("bmad_release_tag") or "")
    cached_healthy_bmad = get_cached_healthy_bmad(state)
    first_run = not STATE_FILE.exists()
    first_local_run = not bool(previous_local)
    first_bmad_run = not bool(previous_release or previous_bmad_refs)

    tracked_local = manifest.get("tracked_local_files", [])
    template_checks = manifest.get("template_checks", {})
    expected_layout_paths = manifest.get("expected_layout_paths", [])

    local_hashes, missing_local = collect_hashes(ROOT, tracked_local)
    local_delta = compute_delta(local_hashes, previous_local)
    template_failures = validate_templates(ROOT, template_checks if isinstance(template_checks, dict) else {})
    layout_failures = validate_layout_markers(
        ROOT,
        tracked_local if isinstance(tracked_local, list) else [],
        expected_layout_paths if isinstance(expected_layout_paths, list) else [],
    )
    local_blockers = build_local_blockers(
        missing_local=missing_local,
        template_failures=template_failures,
        layout_failures=layout_failures,
    )

    bmad_root = discover_bmad_path()
    use_fast_path = should_use_fast_path(args.mode, args.gear)
    if use_fast_path:
        bmad = build_fast_path_bmad(bmad_root, cached_healthy_bmad)
        bmad_ref_hashes = dict(previous_bmad_refs)
        missing_bmad_refs = []
        bmad_delta = []
        current_release = str(bmad.get("release_tag") or previous_release)
        release_changed = False
    else:
        required_bmad_refs = manifest.get("required_bmad_references", [])
        bmad = run_bmad_check(bmad_root)
        bmad_ref_hashes, missing_bmad_refs = collect_bmad_reference_hashes(bmad_root, required_bmad_refs)
        bmad_delta = compute_delta(bmad_ref_hashes, previous_bmad_refs)
        if first_bmad_run:
            bmad_delta = []
        current_release = str(bmad.get("release_tag") or "")
        release_changed = bool(previous_release and current_release and previous_release != current_release)

    warnings = build_warnings(
        bmad=bmad,
        missing_local=missing_local,
        missing_bmad_refs=missing_bmad_refs,
        template_failures=template_failures,
        local_delta=local_delta,
        bmad_delta=bmad_delta,
        previous_release=previous_release,
        current_release=current_release,
        mode=args.mode,
        first_local_run=first_local_run,
        first_bmad_run=first_bmad_run,
    )
    warnings.extend(layout_failures)

    dependency_blockers = build_dependency_blockers(
        bmad=bmad,
        missing_bmad_refs=missing_bmad_refs,
    )
    gate_decision = build_gate_decision(
        requested_gear=args.gear,
        local_blockers=local_blockers,
        dependency_blockers=dependency_blockers,
        use_fast_path=use_fast_path,
        bmad=bmad,
        cached_healthy_bmad=cached_healthy_bmad,
        warnings=warnings,
    )
    classification_allowed = gate_decision["classification_allowed"]
    execution_allowed = gate_decision["execution_allowed"]
    execution_gate = gate_decision["execution_gate"]
    warning_summary = gate_decision["warning_summary"]
    bmad_status = gate_decision["bmad_status"]
    remediation = gate_decision["remediation"]
    action = gate_decision["action"]

    current_checked_at = _now_iso()
    next_cached_healthy_bmad = dict(cached_healthy_bmad)
    if bmad.get("checked_live", True) and bmad.get("available") and bmad.get("healthy"):
        next_cached_healthy_bmad = {
            "checked_at": current_checked_at,
            "path": str(bmad_root),
            "release_tag": current_release,
            "freshness_known": bool(current_release),
            "action": bmad.get("action", "ok"),
        }

    dependency_baseline_ready = bool(
        bmad.get("checked_live", True)
        and bmad.get("available")
        and bmad.get("healthy")
        and not missing_bmad_refs
    )

    # Healthy read-only checks accept the observed baseline. This makes drift a
    # one-run notice instead of a sticky synchronization requirement.
    accepts_local_baseline = not local_blockers
    accepts_dependency_baseline = dependency_baseline_ready
    state_payload = {
        "skill_version": manifest.get("skill_version", "0.0.0"),
        "bmad_release_tag": current_release if accepts_dependency_baseline else previous_release,
        "local_hashes": local_hashes if accepts_local_baseline else previous_local,
        "bmad_reference_hashes": bmad_ref_hashes if accepts_dependency_baseline else previous_bmad_refs,
        "template_failures": template_failures,
        "layout_failures": layout_failures,
        "last_healthy_bmad": next_cached_healthy_bmad,
    }
    state_write_warning = try_write_json(STATE_FILE, state_payload)

    report = {
        "mode": args.mode,
        "requested_gear": args.gear,
        "first_run": first_run,
        "skill_version": manifest.get("skill_version", "0.0.0"),
        "skill": {
            "name": manifest.get("name", SKILL_NAME),
            "version": manifest.get("skill_version", "0.0.0"),
            "target_codex_profile": manifest.get("target_codex_profile", "unknown"),
        },
        "classification_allowed": classification_allowed,
        "execution_allowed": execution_allowed,
        "warning": warning_summary,
        "bmad_status": bmad_status,
        "cache_used": bool(bmad.get("cache_used")),
        "remediation": remediation,
        "bmad_dependency": {
            "path": str(bmad_root),
            "available": bmad.get("available", False),
            "healthy": bmad.get("healthy", False),
            "action": bmad.get("action", "needs_attention"),
            "release_tag": current_release,
            "freshness_known": bool(current_release),
            "checked_live": bmad.get("checked_live", True),
            "status_source": bmad.get("status_source", "live"),
            "cache_used": bool(bmad.get("cache_used")),
            "cache": {
                "available": bool(next_cached_healthy_bmad),
                "checked_at": next_cached_healthy_bmad.get("checked_at"),
                "release_tag": next_cached_healthy_bmad.get("release_tag"),
            },
        },
        "execution_gate": {
            "current_bmad_ready": gate_decision["current_bmad_ready"],
            "soft_gears": sorted(SOFT_GATE_GEARS),
            "hard_gears": sorted(HARD_GATE_GEARS),
            "by_gear": execution_gate,
        },
        "tracked_file_changes": {
            "local": local_delta,
            "bmad_references": bmad_delta,
        },
        "missing": {
            "local_files": missing_local,
            "bmad_references": missing_bmad_refs,
        },
        "template_failures": template_failures,
        "layout_failures": layout_failures,
        "local_blockers": local_blockers,
        "dependency_blockers": dependency_blockers,
        "warnings": warnings,
        "is_optimal": action == "ok",
        "action": action,
        "state_path": str(STATE_FILE),
        "state_persisted": state_write_warning is None,
        "state_write_warning": state_write_warning,
    }
    compact_report = {
        "skill_version": report["skill_version"],
        "requested_gear": args.gear,
        "classification_allowed": classification_allowed,
        "execution_allowed": execution_allowed,
        "warning": warning_summary,
        "bmad_status": bmad_status,
        "cache_used": bool(bmad.get("cache_used")),
        "remediation": remediation,
    }

    if args.json or args.compact:
        print(json.dumps(compact_report if args.compact else report, indent=2))
    else:
        print(f"Skill: {report['skill']['name']} {report['skill']['version']}")
        print(f"Classification allowed: {'yes' if classification_allowed else 'no'}")
        print(f"Execution allowed: {'yes' if execution_allowed else 'no'}")
        print(f"BMAD dependency: {report['bmad_dependency']['action']}")
        if warning_summary:
            print(f"BMADX_WARNING={warning_summary}")
        if warnings:
            print("BMADX_NOTICE:")
            for warning in warnings:
                print(f"- {warning}")
        if remediation:
            print("BMADX_REMEDIATION:")
            for step in remediation:
                print(f"- {step}")
        if state_write_warning:
            print(f"BMADX_STATE_WARNING={state_write_warning}")
        print(f"BMADX_STATUS={report['action']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
