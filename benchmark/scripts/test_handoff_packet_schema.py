#!/usr/bin/env python3
"""Fixture checks for the BMADX broad-orchestrator handoff packet."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "skill" / "bmadx" / "assets" / "schemas" / "broad-handoff-packet.schema.json"
SAMPLE_ROOT = REPO_ROOT / "samples" / "handoff"


class HandoffPacketSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_forbids_runtime_orchestration_keys(self) -> None:
        forbidden = {
            requirement
            for item in self.schema["not"]["anyOf"]
            for requirement in item["required"]
        }
        self.assertIn("model", forbidden)
        self.assertIn("worker_lane", forbidden)
        self.assertIn("dispatch_command", forbidden)
        self.assertIn("mcp", forbidden)
        self.assertIn("subagents", forbidden)
        self.assertIn("runtime_state_path", forbidden)

    def test_samples_match_required_packet_contract(self) -> None:
        required = set(self.schema["required"])
        allowed = set(self.schema["properties"])
        forbidden = {
            requirement
            for item in self.schema["not"]["anyOf"]
            for requirement in item["required"]
        }

        samples = sorted(SAMPLE_ROOT.glob("*.json"))
        self.assertGreaterEqual(len(samples), 2)
        for sample_path in samples:
            with self.subTest(sample=sample_path.name):
                payload = json.loads(sample_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_version"], "bmadx_handoff.v1")
                self.assertEqual(payload["origin"], "bmadx")
                self.assertTrue(required.issubset(payload))
                self.assertFalse(set(payload) - allowed)
                self.assertFalse(set(payload) & forbidden)
                self.assertIn(payload["gear"], {"X3", "X4"})
                self.assertTrue(payload["handoff_recommended"])
                self.assertTrue(payload["proof_required"])
                self.assertTrue(payload["forbidden_changes"])
                self.assertTrue(payload["open_questions"])


if __name__ == "__main__":
    unittest.main()
