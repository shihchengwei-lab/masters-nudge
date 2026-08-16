#!/usr/bin/env python3
"""Long-goal workflow, delivery receipt, and strategy checkpoint tests."""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import hook_entry
import lens_router
import persona_config
from masters_nudge import storage
from masters_nudge.codex_adapter import CodexAdapter, _with_delivery_marker
from masters_nudge.contracts import ReviewOutcome, SessionRef
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parent


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        "openai", "test-model", 60, 15,
        RuntimePaths(HERE, root / "data", root / "legacy", root / "error.log"),
    )


class FakeCore:
    def __init__(self, settings: RuntimeSettings) -> None:
        self.settings = settings
        self.calls = []
        self.log_error = lambda _message: None

    def review(self, request, **_kwargs):
        self.calls.append(request)
        return ReviewOutcome("no_finding", effective_lens="beck")


class DeliveryLifecycleTests(unittest.TestCase):
    def test_receipt_records_generation_and_actual_injection_event(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            session = SessionRef("codex_cli", "s", "t", str(root))
            entry = storage.append_reaction(
                settings.paths.data_dir,
                session,
                provider="openai",
                model="m",
                reaction="先確認交付邊界。",
                route_metadata={"effective_lens": "linus"},
                source_event_seq=4,
            )
            self.assertEqual(entry["delivery_status"], "queued")
            output = _with_delivery_marker(
                {"hookSpecificOutput": {"hookEventName": "PostToolUse"}},
                session,
                entry["ts"],
                event_seq=5,
                event_name="PostToolUse",
            )
            hook_entry._emit_output(output, settings, io.StringIO())
            receipt = storage.load_delivery_state(settings.paths.data_dir, session)[
                "receipts"
            ][entry["ts"]]
            self.assertEqual(receipt["status"], "injected")
            self.assertEqual(receipt["event_seq"], 5)
            self.assertEqual(receipt["delivered_via"], "PostToolUse")

    def test_stale_pending_nudge_expires_instead_of_being_injected_late(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            entry = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="過時提醒",
                route_metadata={"effective_lens": "beck"},
                source_event_seq=1,
            )
            self.assertIsNone(
                storage.latest_pending(root, session, current_event_seq=8)
            )
            receipt = storage.load_delivery_state(root, session)["receipts"][entry["ts"]]
            self.assertEqual(receipt["status"], "expired")


class LongGoalReplayTests(unittest.TestCase):
    def test_repeated_command_family_schedules_one_detached_strategy_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            scheduled = []
            adapter = CodexAdapter(
                core, schedule_strategy=lambda work: scheduled.append(work) or True
            )
            for index in range(3):
                adapter.process(
                    {
                        "hook_event_name": "PostToolUse",
                        "session_id": "s",
                        "turn_id": "t",
                        "cwd": str(root),
                        "tool_name": "shell_command",
                        "tool_input": {"command": "python verify_claims.py --round 9"},
                        "tool_response": {"exit_code": 0, "output": f"pass {index}"},
                    }
                )
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(
                scheduled[0]["checkpoint"]["trigger"], "repeated-command-family"
            )
            self.assertEqual(core.calls, [])

    def test_second_failure_escalates_from_event_review_to_strategy_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            scheduled = []
            adapter = CodexAdapter(
                core, schedule_strategy=lambda work: scheduled.append(work) or True
            )
            for output in ("first failure", "different failure"):
                adapter.process(
                    {
                        "hook_event_name": "PostToolUseFailure",
                        "session_id": "s",
                        "turn_id": "t",
                        "cwd": str(root),
                        "tool_name": "shell_command",
                        "tool_input": {"command": "python verify.py"},
                        "error": output,
                    }
                )
            self.assertEqual(len(core.calls), 1)
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(
                scheduled[0]["checkpoint"]["trigger"], "repeated-failure-family"
            )

    def test_goal_completion_is_reviewed_before_the_final_response(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(root),
                    "tool_name": "update_goal",
                    "tool_input": {"status": "complete"},
                    "tool_response": {"success": True},
                }
            )
            self.assertEqual(core.calls[0].kind, "goal_transition")
            self.assertEqual(core.calls[0].trigger, "goal-complete")

    def test_pending_nudge_does_not_hide_a_goal_transition_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            session = SessionRef("codex_cli", "s", "old", str(root))
            storage.append_reaction(
                settings.paths.data_dir,
                session,
                provider="openai",
                model="m",
                reaction="舊策略提醒",
                route_metadata={"effective_lens": "beck"},
            )
            core = FakeCore(settings)
            output = CodexAdapter(core).process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "s",
                    "turn_id": "new",
                    "cwd": str(root),
                    "tool_name": "update_goal",
                    "tool_input": {"status": "complete"},
                    "tool_response": {"success": True},
                }
            )
            self.assertEqual(core.calls[0].kind, "goal_transition")
            self.assertIn(
                "舊策略提醒", output["hookSpecificOutput"]["additionalContext"]
            )

    def test_eight_healthy_events_schedule_only_one_review_not_eight_nudges(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            scheduled = []
            adapter = CodexAdapter(
                core, schedule_strategy=lambda work: scheduled.append(work) or True
            )
            for index in range(8):
                adapter.process(
                    {
                        "hook_event_name": "PostToolUse",
                        "session_id": "healthy",
                        "turn_id": "t",
                        "cwd": str(root),
                        "tool_name": f"verify_step_{index}",
                        "tool_input": {"step": index},
                        "tool_response": {"success": True},
                    }
                )
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(
                scheduled[0]["checkpoint"]["trigger"], "meaningful-event-budget"
            )

    def test_strategy_signals_route_to_distinct_existing_lenses(self):
        cases = {
            "trigger: repeated-command-family": "beck",
            "local proxy improved but acceptance criteria did not": "jeff",
            "trigger: goal-complete": "linus",
            "trigger: diff-growth": "fowler",
            "duplicate delivery after retry": "lamport",
            "benchmark latency 20ms": "carmack",
        }
        for evidence, expected in cases.items():
            with self.subTest(evidence=evidence):
                root = Path(tempfile.mkdtemp())
                persona_config.save_stage(root, "build")
                route = lens_router.resolve_review_route(
                    root,
                    evidence,
                    environ={},
                )
                self.assertEqual(route.effective_lens, expected)


if __name__ == "__main__":
    unittest.main()
