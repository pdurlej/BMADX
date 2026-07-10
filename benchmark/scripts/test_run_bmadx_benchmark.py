#!/usr/bin/env python3
"""Unit tests for BMADX benchmark runner seams."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bmadx_benchmark_scenarios import (
    BOUNDARY_SCENARIOS,
    CORE_SCENARIOS,
    GOAL_LOOP_SCENARIOS,
    HANDOFF_SCENARIOS,
    NON_TECH_SCENARIOS,
)
from bmadx_benchmark_validation import (
    detect_goal,
    detect_handoff,
    detect_loop,
    detect_reference_reads,
    detect_selected_gear,
    detect_thinking_effort,
    explain_failures_for_non_technical_users,
    normalize_reasoning_effort,
    parse_token_count,
    sanitize_stderr,
    validate_case,
    validate_goal_loop_runtime_drift,
    validate_handoff_runtime_drift,
    validation_failures,
)
from run_bmadx_benchmark import (
    DEFAULT_GATE_MODE,
    DEFAULT_REASONING,
    DEFAULT_REASONING_POLICY,
    benchmark_env,
    build_codex_command,
    build_prompt,
    build_summary,
    compact_gate_hint,
    copy_skills,
    copy_runtime_files,
    effective_reasoning,
    estimate_cost,
    groups_slug,
    model_slug,
    parse_args,
    parse_groups,
    parse_json_report,
    runner_slug,
    summary_path_for,
    summarize_performance,
    validate_warmup_payload,
    write_healthy_bmad_fixture,
    write_config,
)
from bmadx_model_profiles import (
    advisor_reasoning,
    profile_for_model,
    reasoning_prompt_contract,
    validate_model_options,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_parse_token_count_handles_nbsp(self) -> None:
        stderr = "tokens used\n10\u00a0306\n"
        self.assertEqual(parse_token_count(stderr), 10306)

    def test_parse_token_count_returns_none_when_missing(self) -> None:
        self.assertIsNone(parse_token_count("no usage footer here"))

    def test_sanitize_stderr_omits_analytics_html(self) -> None:
        stderr = """before
2026-04-24 WARN codex_analytics::client: events failed with status 403 Forbidden: <html>
  <body>challenge</body>
</html>
exec
tokens used
123
"""
        cleaned = sanitize_stderr(stderr)
        self.assertIn("[analytics warning omitted]", cleaned)
        self.assertNotIn("challenge", cleaned)
        self.assertIn("exec", cleaned)
        self.assertIn("tokens used\n123", cleaned)

    def test_build_prompt_keeps_benchmark_classification_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario = Path(tmpdir) / "scenario.txt"
            scenario.write_text("Intro\nTask: Create a rescue bundle.\n", encoding="utf-8")
            prompt = build_prompt(scenario)
            self.assertIn("Use $bmadx.", prompt)
            self.assertIn("Classify only; run compact gate.", prompt)
            self.assertNotIn("do not run tools", prompt)
            self.assertIn("Start with `Choice: X...`", prompt)
            self.assertIn("Thinking: <low|medium|high|xhigh>", prompt)
            self.assertIn("For gpt-5.5, map X1=medium, X2=medium, X3=high, X4=xhigh", prompt)
            self.assertIn("X2: 2 Plan + 2 Verify lines.", prompt)
            self.assertIn("X1/X2: no refs. No edits.", prompt)
            self.assertIn("Task: Create a rescue bundle.", prompt)

    def test_build_prompt_can_use_precomputed_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario = Path(tmpdir) / "scenario.txt"
            scenario.write_text("Task: Fix a typo.\n", encoding="utf-8")
            prompt = build_prompt(
                scenario,
                gate_report={
                    "requested_gear": "X1",
                    "classification_allowed": True,
                    "execution_allowed": True,
                    "warning": None,
                    "bmad_status": "ok",
                    "cache_used": True,
                    "remediation": [],
                },
            )
            self.assertIn("use precomputed compact gate", prompt)
            self.assertIn("do not run tools", prompt)
            self.assertIn("gear=X1", prompt)
            self.assertIn("class=true", prompt)
            self.assertIn("Task: Fix a typo.", prompt)

    def test_compact_gate_hint_falls_back_to_in_session_gate(self) -> None:
        self.assertEqual(compact_gate_hint(None), "run compact gate.")

    def test_build_prompt_can_request_handoff_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario = Path(tmpdir) / "scenario.txt"
            scenario.write_text("Task: Ask for broad architecture review.\n", encoding="utf-8")
            prompt = build_prompt(scenario, include_handoff=True)
            self.assertIn("Handoff: yes/no", prompt)
            self.assertIn("Do not name models", prompt)
            self.assertIn("Task: Ask for broad architecture review.", prompt)

    def test_build_prompt_can_request_goal_loop_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario = Path(tmpdir) / "scenario.txt"
            scenario.write_text("Task: Continue until tests pass.\n", encoding="utf-8")
            prompt = build_prompt(scenario, include_goal_loop=True)
            self.assertIn("Goal: yes/no", prompt)
            self.assertIn("Loop: yes/no", prompt)
            self.assertIn("not a BMADX gear", prompt)
            self.assertIn("Goal and loop are independent", prompt)
            self.assertIn("one verification pass is insufficient", prompt)
            self.assertIn("numeric maximum", prompt)
            self.assertIn("review -> repair -> validate", prompt)
            self.assertIn("persistent run IDs", prompt)
            self.assertIn("Task: Continue until tests pass.", prompt)

    def test_detect_reference_reads_returns_unique_paths(self) -> None:
        stderr = """
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/gearbox.md"
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/gearbox.md"
        exec /bin/zsh -lc "sed -n '1,220p' /tmp/codex-home/skills/bmadx/references/trigger-matrix.md"
        """
        self.assertEqual(detect_reference_reads(stderr), ["gearbox.md", "trigger-matrix.md"])

    def test_detect_selected_gear_reads_choice_line(self) -> None:
        self.assertEqual(detect_selected_gear("Choice: `X2 — Regular`\nWhy: ..."), "X2")
        self.assertEqual(detect_selected_gear("**Choice:** X3 — Complex\nWhy: ..."), "X3")
        self.assertEqual(detect_selected_gear("**Classification: X4**\nGate: green"), "X4")
        self.assertEqual(detect_selected_gear("**Choice: Rescue Mode (X4/FUBAR)**\nWhy: ..."), "X4")
        self.assertIsNone(detect_selected_gear("Why: This mentions X2 but does not choose it."))

    def test_detect_selected_gear_does_not_cross_lines(self) -> None:
        self.assertIsNone(detect_selected_gear("Choice:\nWhy: mentions X2 incidentally.\n"))

    def test_detect_handoff_reads_contract_line(self) -> None:
        self.assertTrue(detect_handoff("Choice: X3\nHandoff: yes — broad review useful\n"))
        self.assertFalse(detect_handoff("Choice: X3\nHandoff: no — BMADX is enough\n"))
        self.assertTrue(detect_handoff("**Handoff:** recommended\n"))
        self.assertIsNone(detect_handoff("No handoff language here."))

    def test_detect_handoff_does_not_cross_lines(self) -> None:
        self.assertIsNone(detect_handoff("Handoff:\nNo, not in contract form.\n"))

    def test_detect_goal_reads_contract_line(self) -> None:
        self.assertTrue(detect_goal("Choice: X3\nGoal: yes — use /goal.\n"))
        self.assertFalse(detect_goal("Choice: X2\nGoal: no — normal contract is enough.\n"))
        self.assertTrue(detect_goal("**Goal:** recommended\n"))
        self.assertIsNone(detect_goal("No goal language here."))

    def test_detect_loop_reads_contract_line(self) -> None:
        self.assertTrue(detect_loop("Choice: X4\nLoop: yes — max 3 passes.\n"))
        self.assertTrue(detect_loop("Loop: max 2 review/repair/validate passes.\n"))
        self.assertFalse(detect_loop("Loop: no — one verify pass is enough.\n"))
        self.assertIsNone(detect_loop("Loop:\nNo, not in contract form.\n"))

    def test_detect_thinking_effort_reads_contract_line(self) -> None:
        self.assertEqual(detect_thinking_effort("Choice: X3\nThinking: high — suggestion only.\n"), "high")
        self.assertEqual(detect_thinking_effort("**Thinking:** `xhigh` — suggestion only.\n"), "xhigh")
        self.assertEqual(detect_thinking_effort("Thinking: max — suggestion only.\n"), "max")
        self.assertEqual(detect_thinking_effort("Thinking: ultra — suggestion only.\n"), "ultra")

    def test_detect_thinking_effort_normalizes_extra_high(self) -> None:
        self.assertEqual(normalize_reasoning_effort("extra_high"), "xhigh")
        self.assertEqual(detect_thinking_effort("Thinking: extra high — suggestion only.\n"), "xhigh")

    def test_validate_handoff_runtime_drift_blocks_runtime_details(self) -> None:
        clean = validate_handoff_runtime_drift("Handoff: yes — broad review is useful.")
        self.assertTrue(clean["handoff_not_runtime_pass"])
        dirty = validate_handoff_runtime_drift("Handoff: yes. Use primary_worker glm-5.1 and dispatch.")
        self.assertFalse(dirty["handoff_not_runtime_pass"])
        self.assertFalse(dirty["no_worker_lane_pass"])
        self.assertFalse(dirty["no_model_name_pass"])
        self.assertFalse(dirty["no_dispatch_command_pass"])

    def test_validate_goal_loop_runtime_drift_blocks_runtime_details(self) -> None:
        self.assertTrue(validate_goal_loop_runtime_drift("Goal: yes\nLoop: yes — max 3 passes.\n"))
        self.assertFalse(validate_goal_loop_runtime_drift("Goal: yes. Create hooks and subagents with persistent run IDs."))

    def test_validate_case_marks_reference_budget_failure_for_x1(self) -> None:
        stdout = "Choice: `X1 — One-shot`.\nWhy: ...\nNext step: ...\n"
        stderr = 'exec /bin/zsh -lc "sed -n \'1,220p\' /tmp/codex-home/skills/bmadx/references/gearbox.md"\n'
        validation = validate_case(
            stdout,
            stderr,
            8900,
            {
                "expected_gear": "X1",
                "max_lines": 5,
                "max_chars": 650,
                "max_tokens": 9000,
                "allow_reference_reads": False,
            },
        )
        self.assertTrue(validation["format_pass"])
        self.assertTrue(validation["token_count_present"])
        self.assertTrue(validation["token_pass"])
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["reference_budget_pass"])
        self.assertEqual(validation["reference_reads"], ["gearbox.md"])
        self.assertTrue(validation["overreach_pass"])

    def test_validate_case_routes_by_selected_gear_not_incidental_mentions(self) -> None:
        validation = validate_case(
            "Choice: `X2 — Regular`\nWhy: This is not X3.\n",
            "",
            1000,
            {"expected_gear": "X3", "allow_reference_reads": True},
        )
        self.assertEqual(validation["selected_gear"], "X2")
        self.assertIn("X3", validation["observed_gears"])
        self.assertFalse(validation["routing_pass"])

    def test_validate_case_checks_handoff_without_runtime_details(self) -> None:
        validation = validate_case(
            "Choice: X3\nWhy: Auth ownership is unclear.\nHandoff: yes — broad architecture review is useful.\n",
            "",
            1000,
            {"expected_gear": "X3", "expected_handoff": True, "allow_reference_reads": True},
        )
        self.assertTrue(validation["routing_pass"])
        self.assertTrue(validation["handoff_routing_pass"])
        self.assertTrue(validation["handoff_not_runtime_pass"])

    def test_validate_case_checks_expected_thinking_budget(self) -> None:
        validation = validate_case(
            "Choice: X3\nThinking: high — suggestion only.\nWhy: Auth ownership is unclear.\n",
            "",
            1000,
            {"expected_gear": "X3", "expected_reasoning_effort": "high", "allow_reference_reads": True},
        )
        self.assertTrue(validation["thinking_budget_present"])
        self.assertTrue(validation["thinking_budget_pass"])
        self.assertTrue(validation["thinking_budget_no_mutation_pass"])
        self.assertTrue(validation["thinking_budget_supported_value_pass"])

    def test_validate_case_checks_expected_goal_and_loop(self) -> None:
        validation = validate_case(
            "Choice: X4\nThinking: xhigh — suggestion only.\nGoal: yes — stop when validation passes or approval blocks execution.\nLoop: yes — max 3 passes; stop on pass or stale delta.\n",
            "",
            1000,
            {
                "expected_gear": "X4",
                "expected_reasoning_effort": "xhigh",
                "expected_goal": True,
                "expected_loop": True,
                "allow_reference_reads": True,
            },
        )
        self.assertTrue(validation["goal_routing_pass"])
        self.assertTrue(validation["goal_stop_condition_pass"])
        self.assertTrue(validation["loop_contract_pass"])
        self.assertTrue(validation["goal_loop_not_runtime_pass"])

    def test_validate_case_fails_goal_loop_runtime_drift(self) -> None:
        validation = validate_case(
            "Choice: X4\nGoal: yes — create persistent state.\nLoop: yes — dispatch worker lane.\n",
            "",
            1000,
            {"expected_gear": "X4", "expected_goal": True, "expected_loop": True, "allow_reference_reads": True},
        )
        self.assertTrue(validation["goal_routing_pass"])
        self.assertFalse(validation["goal_stop_condition_pass"])
        self.assertFalse(validation["loop_contract_pass"])
        self.assertFalse(validation["goal_loop_not_runtime_pass"])

    def test_validate_case_rejects_unbounded_goal_loop(self) -> None:
        validation = validate_case(
            "Choice: X4\nGoal: yes — keep working.\nLoop: yes — repeat until perfect.\n",
            "",
            1000,
            {"expected_gear": "X4", "expected_goal": True, "expected_loop": True},
        )
        self.assertFalse(validation["goal_stop_condition_pass"])
        self.assertFalse(validation["loop_contract_pass"])

    def test_validate_case_blocks_global_config_mutation(self) -> None:
        validation = validate_case(
            "Choice: X2\nThinking: medium — edit ~/.codex/config.toml to make this global.\n",
            "",
            1000,
            {"expected_gear": "X2", "expected_reasoning_effort": "medium", "allow_reference_reads": False},
        )
        self.assertTrue(validation["thinking_budget_pass"])
        self.assertFalse(validation["thinking_budget_no_mutation_pass"])

    def test_validate_case_rejects_unknown_thinking_value(self) -> None:
        validation = validate_case(
            "Choice: X2\nThinking: extreme — suggestion only.\n",
            "",
            1000,
            {"expected_gear": "X2", "expected_reasoning_effort": "medium", "allow_reference_reads": False},
        )
        self.assertFalse(validation["thinking_budget_pass"])
        self.assertFalse(validation["thinking_budget_supported_value_pass"])

    def test_validate_case_fails_handoff_runtime_drift(self) -> None:
        validation = validate_case(
            "Choice: X3\nHandoff: yes — ask Opus and dispatch a worker lane with glm-5.1.\n",
            "",
            1000,
            {"expected_gear": "X3", "expected_handoff": True, "allow_reference_reads": True},
        )
        self.assertTrue(validation["handoff_routing_pass"])
        self.assertFalse(validation["handoff_not_runtime_pass"])
        self.assertFalse(validation["no_model_name_pass"])

    def test_validate_case_fails_token_pass_when_count_is_missing(self) -> None:
        validation = validate_case(
            "Choice: `X1 — One-shot`.\nWhy: ...\nNext step: ...\n",
            "",
            None,
            {"expected_gear": "X1", "max_tokens": 9000, "allow_reference_reads": False},
        )
        self.assertFalse(validation["token_count_present"])
        self.assertFalse(validation["token_pass"])

    def test_model_is_required_for_reproducible_runs(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args([])
        args = parse_args(["--model", "gpt-5.6-sol"])
        self.assertEqual(args.model, "gpt-5.6-sol")
        self.assertEqual(args.reasoning, DEFAULT_REASONING)
        self.assertEqual(args.reasoning_policy, DEFAULT_REASONING_POLICY)
        self.assertEqual(args.gate_mode, DEFAULT_GATE_MODE)
        self.assertEqual(args.gate_mode, "precomputed")
        self.assertEqual(args.groups, ["core", "boundary", "non_technical", "handoff", "goal_loop"])
        self.assertEqual(args.repeat, 1)

    def test_parse_args_supports_reasoning_policy_gate_mode_groups_and_repeat(self) -> None:
        args = parse_args(
            [
                "--model",
                "gpt-5.6-terra",
                "--reasoning-policy",
                "advisor",
                "--gate-mode",
                "in-session",
                "--groups",
                "core,boundary",
                "--repeat",
                "3",
            ]
        )
        self.assertEqual(args.reasoning_policy, "advisor")
        self.assertEqual(args.gate_mode, "in-session")
        self.assertEqual(args.groups, ["core", "boundary"])
        self.assertEqual(args.repeat, 3)

    def test_parse_groups_rejects_unknown_groups(self) -> None:
        with self.assertRaises(Exception):
            parse_groups("core,unknown")

    def test_groups_slug_distinguishes_canary_from_full_runs(self) -> None:
        self.assertEqual(groups_slug(["core", "boundary", "non_technical", "handoff", "goal_loop"]), "all")
        self.assertEqual(groups_slug(["core", "boundary"]), "core-boundary")
        self.assertEqual(groups_slug(["non_technical", "handoff"]), "non-technical-handoff")

    def test_effective_reasoning_uses_advisor_spec(self) -> None:
        spec = {"expected_gear": "X4", "expected_reasoning_effort": "xhigh"}
        self.assertEqual(effective_reasoning(spec, "medium", "fixed"), "medium")
        self.assertEqual(effective_reasoning(spec, "medium", "advisor"), "xhigh")
        self.assertEqual(effective_reasoning(spec, "medium", "advisor", "gpt-5.6-sol"), "high")

    def test_gpt56_profiles_are_model_aware(self) -> None:
        sol = profile_for_model("gpt-5.6-sol")
        self.assertEqual(sol["status"], "candidate")
        self.assertEqual(advisor_reasoning("gpt-5.6-sol", "X4", "xhigh"), "high")
        self.assertEqual(advisor_reasoning("gpt-5.6-terra", "X4", "high"), "xhigh")
        self.assertIn("ultra", reasoning_prompt_contract("gpt-5.6-sol")[0])
        self.assertNotIn("ultra", reasoning_prompt_contract("gpt-5.6-luna")[0])

    def test_gpt56_profile_rejects_old_cli_and_unsupported_effort(self) -> None:
        failures = validate_model_options("gpt-5.6-luna", "ultra", cli_version="codex-cli 0.143.0")
        self.assertTrue(any("not supported" in failure for failure in failures))
        self.assertTrue(any("requires Codex CLI" in failure for failure in failures))

    def test_model_override_still_supports_gpt54(self) -> None:
        args = parse_args(["--model", "gpt-5.4", "--reasoning", "high"])
        self.assertEqual(args.model, "gpt-5.4")
        self.assertEqual(args.reasoning, "high")
        self.assertFalse(args.oss)
        self.assertIsNone(args.local_provider)

    def test_parse_args_supports_oss_local_provider(self) -> None:
        args = parse_args(["--oss", "--local-provider", "ollama", "--model", "mistral"])
        self.assertTrue(args.oss)
        self.assertEqual(args.local_provider, "ollama")
        self.assertEqual(args.model, "mistral")

    def test_model_slug_is_filename_safe(self) -> None:
        self.assertEqual(model_slug("gpt-5.5"), "gpt-5-5")
        self.assertEqual(model_slug("GPT 5.4 Pro"), "gpt-5-4-pro")

    def test_runner_slug_includes_local_provider_for_oss(self) -> None:
        self.assertEqual(runner_slug("gpt-5.5"), "gpt-5-5")
        self.assertEqual(runner_slug("mistral", oss=True, local_provider="ollama"), "ollama-mistral")

    def test_non_technical_scenarios_cover_red_zones_and_rescue(self) -> None:
        self.assertEqual(CORE_SCENARIOS["x1"]["expected_reasoning_effort"], "medium")
        self.assertEqual(CORE_SCENARIOS["x2"]["expected_reasoning_effort"], "medium")
        self.assertEqual(CORE_SCENARIOS["x3"]["expected_reasoning_effort"], "high")
        self.assertEqual(CORE_SCENARIOS["x4"]["expected_reasoning_effort"], "xhigh")
        self.assertEqual(BOUNDARY_SCENARIOS["x2x3-boundary"]["expected_reasoning_effort"], "high")
        self.assertEqual(NON_TECH_SCENARIOS["pricing-copy"]["expected_gear"], "X1")
        self.assertEqual(NON_TECH_SCENARIOS["pricing-copy"]["expected_reasoning_effort"], "medium")
        self.assertEqual(NON_TECH_SCENARIOS["onboarding-email"]["expected_gear"], "X2")
        self.assertEqual(NON_TECH_SCENARIOS["onboarding-email"]["expected_reasoning_effort"], "medium")
        self.assertEqual(NON_TECH_SCENARIOS["google-login"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["google-login"]["expected_reasoning_effort"], "high")
        self.assertEqual(NON_TECH_SCENARIOS["subscription-billing"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["delete-inactive-users"]["expected_gear"], "X3")
        self.assertEqual(NON_TECH_SCENARIOS["messy-migration-incident"]["expected_gear"], "X4")
        self.assertEqual(NON_TECH_SCENARIOS["messy-migration-incident"]["expected_reasoning_effort"], "xhigh")
        for spec in NON_TECH_SCENARIOS.values():
            self.assertTrue(Path(spec["path"]).exists())

    def test_handoff_scenarios_cover_x3_and_x4(self) -> None:
        self.assertEqual(HANDOFF_SCENARIOS["x3-auth-review-handoff"]["expected_gear"], "X3")
        self.assertTrue(HANDOFF_SCENARIOS["x3-auth-review-handoff"]["expected_handoff"])
        self.assertEqual(HANDOFF_SCENARIOS["x4-migration-review-handoff"]["expected_gear"], "X4")
        self.assertTrue(HANDOFF_SCENARIOS["x4-migration-review-handoff"]["expected_handoff"])
        for spec in HANDOFF_SCENARIOS.values():
            self.assertTrue(Path(spec["path"]).exists())

    def test_goal_loop_scenarios_cover_x3_goal_and_x4_loop(self) -> None:
        self.assertEqual(GOAL_LOOP_SCENARIOS["goal-x3-auth-cleanup"]["expected_gear"], "X3")
        self.assertTrue(GOAL_LOOP_SCENARIOS["goal-x3-auth-cleanup"]["expected_goal"])
        self.assertFalse(GOAL_LOOP_SCENARIOS["goal-x3-auth-cleanup"]["expected_loop"])
        self.assertEqual(GOAL_LOOP_SCENARIOS["loop-x4-migration-repair"]["expected_gear"], "X4")
        self.assertTrue(GOAL_LOOP_SCENARIOS["loop-x4-migration-repair"]["expected_goal"])
        self.assertTrue(GOAL_LOOP_SCENARIOS["loop-x4-migration-repair"]["expected_loop"])
        for spec in GOAL_LOOP_SCENARIOS.values():
            self.assertTrue(Path(spec["path"]).exists())

    def test_summary_path_uses_bmadx_suffix(self) -> None:
        self.assertEqual(
            summary_path_for("2026-05-05", "gpt-5-5", "healthy").name,
            "summary-2026-05-05-gpt-5-5-healthy-fixed-precomputed-all-bmadx.json",
        )
        self.assertEqual(
            summary_path_for(
                "2026-05-05",
                "gpt-5-5",
                "healthy",
                "advisor",
                "in-session",
                "core-boundary",
            ).name,
            "summary-2026-05-05-gpt-5-5-healthy-advisor-in-session-core-boundary-bmadx.json",
        )

    def test_write_config_uses_model_and_reasoning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            write_config(codex_home, "gpt-5.5", "medium")
            config = codex_home.joinpath("config.toml").read_text(encoding="utf-8")
            self.assertIn('model = "gpt-5.5"', config)
            self.assertIn('model_reasoning_effort = "medium"', config)

    def test_codex_command_is_isolated_and_model_explicit(self) -> None:
        command = build_codex_command(
            "prompt",
            Path("/tmp/workdir"),
            Path("/tmp/codex-home"),
            model="gpt-5.5",
            reasoning="medium",
        )
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--disable", command)
        self.assertIn("plugins", command)
        self.assertIn("apps", command)
        self.assertIn("-m", command)
        self.assertIn("gpt-5.5", command)
        self.assertIn('model_reasoning_effort="medium"', command)
        self.assertIn("--add-dir", command)
        self.assertIn("/tmp/codex-home", command)
        self.assertIn("workspace-write", command)

    def test_codex_command_supports_oss_local_provider(self) -> None:
        command = build_codex_command(
            "prompt",
            Path("/tmp/workdir"),
            Path("/tmp/codex-home"),
            model="mistral",
            reasoning="medium",
            oss=True,
            local_provider="ollama",
        )
        self.assertIn("--oss", command)
        self.assertIn("--local-provider", command)
        self.assertIn("ollama", command)
        self.assertIn("-m", command)
        self.assertIn("mistral", command)
        self.assertNotIn('model_reasoning_effort="medium"', command)

    def test_copy_runtime_files_does_not_copy_global_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir)
            copy_runtime_files(codex_home)
            self.assertFalse(codex_home.joinpath(".codex-global-state.json").exists())

    def test_copy_skills_excludes_runtime_state_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_codex_home = root / "source-codex-home"
            bmad_state = source_codex_home / "skills/bmad-method-codex/state"
            bmad_state.mkdir(parents=True)
            bmad_state.joinpath(".gitkeep").write_text("", encoding="utf-8")
            bmad_state.joinpath("bmad-release-state.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            codex_home = root / "benchmark-codex-home"
            with patch.dict(
                "run_bmadx_benchmark.os.environ",
                {"CODEX_HOME": str(source_codex_home)},
            ):
                copy_skills(codex_home)
            self.assertFalse(codex_home.joinpath("skills/bmadx/state/bmadx-state.json").exists())
            self.assertTrue(codex_home.joinpath("skills/bmadx/state/.gitkeep").exists())
            self.assertTrue(codex_home.joinpath("skills/bmad-method-codex/state/.gitkeep").exists())
            self.assertFalse(
                codex_home.joinpath("skills/bmad-method-codex/state/bmad-release-state.json").exists()
            )

    def test_healthy_profile_uses_local_release_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fixture = write_healthy_bmad_fixture(root)
            env = benchmark_env(root / "codex-home", "healthy", fixture)
            self.assertEqual(env["BMAD_RELEASE_API"], fixture.resolve().as_uri())

    def test_parse_json_report_rejects_invalid_json(self) -> None:
        with self.assertRaises(RuntimeError):
            parse_json_report("not json")

    def test_warmup_healthy_profile_requires_ok_json(self) -> None:
        validate_warmup_payload(
            "healthy",
            {"action": "ok", "bmad_dependency": {"healthy": True}},
        )
        with self.assertRaises(RuntimeError):
            validate_warmup_payload(
                "healthy",
                {"action": "warning", "bmad_dependency": {"healthy": True}},
            )

    def test_warmup_degraded_profile_rejects_ok_healthy_json(self) -> None:
        with self.assertRaises(RuntimeError):
            validate_warmup_payload(
                "degraded",
                {"action": "ok", "bmad_dependency": {"healthy": True}},
            )
        validate_warmup_payload(
            "degraded",
            {"action": "warning", "bmad_dependency": {"healthy": False}},
        )

    def test_summary_records_model_and_reasoning(self) -> None:
        summary = build_summary(
            "2026-04-24",
            "healthy",
            [
                {
                    "tokens": 100,
                    "duration_seconds": 12.5,
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": True,
                    "reference_budget_pass": True,
                    "routing_pass": True,
                    "overreach_pass": True,
                    "thinking_budget_present": True,
                    "thinking_budget_pass": True,
                    "thinking_budget_no_mutation_pass": True,
                    "thinking_budget_supported_value_pass": True,
                }
            ],
            [],
            [],
            [],
            model="gpt-5.5",
            reasoning="medium",
            reasoning_policy="advisor",
            gate_mode="precomputed",
            groups=["core"],
            group_slug_value="core",
            repeat=3,
            cost_per_million_tokens=2.0,
        )
        self.assertEqual(summary["runner"]["model"], "gpt-5.5")
        self.assertEqual(summary["runner"]["model_profile"]["status"], "validated-baseline")
        self.assertEqual(summary["runner"]["reasoning"], "medium")
        self.assertEqual(summary["runner"]["reasoning_policy"], "advisor")
        self.assertEqual(summary["runner"]["gate_mode"], "precomputed")
        self.assertEqual(summary["runner"]["groups"], ["core"])
        self.assertEqual(summary["runner"]["group_slug"], "core")
        self.assertEqual(summary["runner"]["repeat"], 3)
        self.assertEqual(summary["runner"]["provider"], "openai")
        self.assertIsNone(summary["runner"]["local_provider"])
        self.assertTrue(summary["runner"]["reasoning_applied"])
        self.assertEqual(summary["validation_summary"]["core"]["token_count_present_count"], 1)
        self.assertEqual(summary["validation_summary"]["core"]["overreach_pass_count"], 1)
        self.assertEqual(summary["validation_summary"]["core"]["thinking_budget_pass_count"], 1)
        self.assertEqual(summary["performance_summary"]["all"]["total_tokens"], 100)
        self.assertEqual(summary["performance_summary"]["all"]["avg_duration_seconds"], 12.5)
        self.assertEqual(summary["cost_estimate"]["estimated_cost"], 0.0002)
        self.assertEqual(summary["validation_failures"]["core"], [])
        self.assertEqual(summary["validation_summary"]["non_technical"]["case_count"], 0)
        self.assertEqual(summary["validation_summary"]["handoff"]["case_count"], 0)
        self.assertEqual(summary["validation_summary"]["goal_loop"]["case_count"], 0)
        self.assertEqual(summary["non_technical_readout"]["what_failed_why_it_matters"], [])

    def test_summary_records_oss_provider(self) -> None:
        summary = build_summary(
            "2026-05-05",
            "healthy",
            [],
            [],
            [],
            [],
            model="mistral",
            reasoning="medium",
            oss=True,
            local_provider="ollama",
        )
        self.assertEqual(summary["runner"]["provider"], "oss")
        self.assertEqual(summary["runner"]["local_provider"], "ollama")
        self.assertFalse(summary["runner"]["reasoning_applied"])

    def test_summarize_performance_records_token_and_latency_stats(self) -> None:
        summary = summarize_performance(
            [
                {"tokens": 100, "duration_seconds": 1.0},
                {"tokens": 300, "duration_seconds": 3.0},
                {"tokens": 200, "duration_seconds": 2.0},
            ]
        )
        self.assertEqual(summary["case_count"], 3)
        self.assertEqual(summary["total_tokens"], 600)
        self.assertEqual(summary["avg_tokens"], 200)
        self.assertEqual(summary["p50_duration_seconds"], 2.0)
        self.assertEqual(summary["max_duration_seconds"], 3.0)

    def test_estimate_cost_is_disabled_without_explicit_price(self) -> None:
        self.assertIsNone(estimate_cost(1000, None))
        self.assertEqual(estimate_cost(1000, 2.0)["estimated_cost"], 0.002)

    def test_validate_case_catches_gpt55_overreach(self) -> None:
        validation = validate_case(
            "Choice: `X2`, but maybe X4 if it gets messy.\n",
            "",
            1000,
            {"expected_gear": "X2", "forbidden_gears": ["X3", "X4"], "allow_reference_reads": False},
        )
        self.assertTrue(validation["routing_pass"])
        self.assertFalse(validation["overreach_pass"])

    def test_validation_failures_names_failed_checks(self) -> None:
        failures = validation_failures(
            [
                {
                    "case": "bmadx-healthy-x1",
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": False,
                    "reference_budget_pass": True,
                    "routing_pass": False,
                    "overreach_pass": True,
                    "thinking_budget_pass": True,
                    "thinking_budget_no_mutation_pass": True,
                    "thinking_budget_supported_value_pass": True,
                    "expected_goal": True,
                    "goal_routing_pass": False,
                    "expected_loop": True,
                    "loop_contract_pass": True,
                    "goal_loop_not_runtime_pass": True,
                }
            ]
        )
        self.assertEqual(
            failures,
            [
                {
                    "case": "bmadx-healthy-x1",
                    "failed_checks": [
                        "token_pass",
                        "routing_pass",
                        "goal_routing_pass",
                        "goal_stop_condition_pass",
                    ],
                }
            ],
        )

    def test_non_technical_failure_explanations_are_plain_language(self) -> None:
        explanations = explain_failures_for_non_technical_users(
            [
                {
                    "case": "bmadx-healthy-google-login",
                    "format_pass": True,
                    "token_count_present": True,
                    "token_pass": True,
                    "reference_budget_pass": True,
                    "routing_pass": False,
                    "overreach_pass": True,
                    "thinking_budget_pass": True,
                    "thinking_budget_no_mutation_pass": True,
                    "thinking_budget_supported_value_pass": True,
                }
            ]
        )
        self.assertEqual(explanations[0]["case"], "bmadx-healthy-google-login")
        self.assertEqual(explanations[0]["what_failed"], ["routing_pass"])
        self.assertIn("wrong work mode", explanations[0]["why_it_matters"][0])


if __name__ == "__main__":
    unittest.main()
