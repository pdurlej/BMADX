#!/usr/bin/env python3
"""Render the BMADX FUBAR scaffold bundle from local templates."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "assets" / "templates"

TEMPLATE_OUTPUTS = {
    "AGENTS.repo.md": "AGENTS.md",
    "core-bmad-master.customize.yaml": "core-bmad-master.customize.yaml",
    "bmm-dev.customize.yaml": "bmm-dev.customize.yaml",
    "trigger-matrix.md": "bmadx-trigger-matrix.md",
    "verify-matrix.md": "bmadx-verify-matrix.md",
    "rollout-checklist.md": "bmadx-rollout-checklist.md",
    "subagent-policy.md": "bmadx-subagent-policy.md",
}

OPTIONAL_TEMPLATE_OUTPUTS = {
    "bmm-architect.customize.yaml": "bmm-architect.customize.yaml",
}


def render_text(template: str, variables: dict[str, str]) -> str:
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def write_rendered(template_name: str, output_name: str, variables: dict[str, str], output_dir: Path) -> str:
    source = TEMPLATE_ROOT / template_name
    content = render_text(source.read_text(encoding="utf-8"), variables)
    target = output_dir / output_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render BMADX FUBAR bundle")
    parser.add_argument("--project-name", required=True, help="Project name used in templates")
    parser.add_argument("--project-path", default=str(Path.cwd()), help="Project path for the bundle")
    parser.add_argument("--output-dir", required=True, help="Output directory for rendered bundle")
    parser.add_argument("--include-architect", action="store_true", help="Include optional architect customize snippet")
    parser.add_argument("--json", action="store_true", help="Print JSON manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    generated_at = datetime.now(timezone.utc).isoformat()

    variables = {
        "project_name": args.project_name,
        "project_path": str(Path(args.project_path).resolve()),
        "generated_at": generated_at,
        "bmadx_skill_path": str(ROOT),
        "bmad_skill_path": str(Path.home() / ".codex" / "skills" / "bmad-method-codex"),
    }

    rendered = {}
    for template_name, output_name in TEMPLATE_OUTPUTS.items():
        rendered[template_name] = write_rendered(template_name, output_name, variables, output_dir)

    if args.include_architect:
        for template_name, output_name in OPTIONAL_TEMPLATE_OUTPUTS.items():
            rendered[template_name] = write_rendered(template_name, output_name, variables, output_dir)

    manifest = {
        "project_name": args.project_name,
        "project_path": variables["project_path"],
        "output_dir": str(output_dir),
        "generated_at": generated_at,
        "rendered_files": rendered,
    }

    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"Rendered BMADX FUBAR bundle to {output_dir}")
        for path in rendered.values():
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
