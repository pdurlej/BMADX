#!/usr/bin/env python3
"""Tests for the local Codex model compatibility checker."""

from __future__ import annotations

import json
import subprocess
import unittest

from check_codex_compat import build_report, parse_version


def catalog() -> str:
    efforts = {
        "gpt-5.6-sol": ["low", "medium", "high", "xhigh", "max", "ultra"],
        "gpt-5.6-terra": ["low", "medium", "high", "xhigh", "max", "ultra"],
        "gpt-5.6-luna": ["low", "medium", "high", "xhigh", "max"],
    }
    return json.dumps(
        {
            "models": [
                {
                    "slug": model,
                    "default_reasoning_level": "low" if model.endswith("sol") else "medium",
                    "supported_reasoning_levels": [{"effort": effort} for effort in model_efforts],
                }
                for model, model_efforts in efforts.items()
            ]
        }
    )


class RunnerStub:
    def __init__(self, version: str = "codex-cli 0.144.1", model_catalog: str | None = None) -> None:
        self.version = version
        self.model_catalog = model_catalog or catalog()

    def __call__(self, command, capture_output, text, check, timeout):
        stdout = self.version if command[-1] == "--version" else self.model_catalog
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


class CheckCodexCompatTests(unittest.TestCase):
    def test_parse_version(self) -> None:
        self.assertEqual(parse_version("codex-cli 0.144.1"), (0, 144, 1))

    def test_current_catalog_is_ready(self) -> None:
        report = build_report(RunnerStub())
        self.assertTrue(report["gpt56_ready"])
        self.assertTrue(report["models"]["gpt-5.6-sol"]["catalog_matches_profile"])

    def test_old_cli_is_reported_without_reading_auth(self) -> None:
        report = build_report(RunnerStub(version="codex-cli 0.143.0"))
        self.assertFalse(report["gpt56_ready"])
        self.assertTrue(any("requires Codex CLI" in warning for warning in report["warnings"]))

    def test_catalog_drift_is_reported(self) -> None:
        payload = json.loads(catalog())
        payload["models"][0]["supported_reasoning_levels"] = [{"effort": "medium"}]
        report = build_report(RunnerStub(model_catalog=json.dumps(payload)))
        self.assertFalse(report["gpt56_ready"])
        self.assertTrue(any("differ" in warning for warning in report["warnings"]))

    def test_catalog_effort_order_is_not_semantic_drift(self) -> None:
        payload = json.loads(catalog())
        for model in payload["models"]:
            model["supported_reasoning_levels"].reverse()
        report = build_report(RunnerStub(model_catalog=json.dumps(payload)))
        self.assertTrue(report["gpt56_ready"])


if __name__ == "__main__":
    unittest.main()
