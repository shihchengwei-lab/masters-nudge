#!/usr/bin/env python3
"""Goal persistence, delivery receipt, and strategy checkpoint tests."""

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


HERE = Path(__file__).resolve().parents[2]


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        "openai", "test-model", 60, 15,
        RuntimePaths(HERE, root / "data", root / "error.log"),
    )


class FakeCore:
    def __init__(self, settings: RuntimeSettings) -> None:
        self.settings = settings
        self.calls = []
        self.log_error = lambda _message: None

    def review(self, request, **_kwargs):
        self.calls.append(request)
        return ReviewOutcome("no_finding", effective_lens="beck")

    def review_once(self, request, **kwargs):
        return self.review(request, **kwargs)


class DeliveryLifecycleTests(unittest.TestCase):
    def test_stop_does_not_review_or_start_detached_coordination(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            core = FakeCore(settings)
            adapter = CodexAdapter(core)
            session = SessionRef("codex_cli", "stop-order", "turn", str(root))
            storage.start_turn(settings.paths.data_dir, session, "修正完整行為")

            adapter.process(
                {
                    "hook_event_name": "Stop",
                    "session_id": session.session_id,
                    "turn_id": session.turn_id,
                    "cwd": session.cwd,
                    "last_assistant_message": "已完成",
                    "stop_hook_active": False,
                }
            )

            self.assertFalse(hasattr(storage, "wait_for_strategy_idle"))
            self.assertEqual(core.calls, [])

    def test_back_to_back_reactions_have_distinct_sortable_ids(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            first = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="第一則。",
                route_metadata={"effective_lens": "beck"},
            )
            second = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="第二則。",
                route_metadata={"effective_lens": "beck"},
            )

            self.assertLess(first["ts"], second["ts"])

    def test_review_status_is_visible_but_not_queued_for_injection(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s", "t", str(root))
            entry = storage.append_reaction(
                root,
                session,
                provider="grok",
                model="",
                reaction="Reviewer 逾時（90 秒）；本輪沒有 Nudge。",
                route_metadata={"effective_lens": "fowler"},
                kind="review_status",
            )

        self.assertEqual(entry["delivery_status"], "")

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
            self.assertEqual(receipt["status"], "emitted")
            storage.observe_injected_response(
                settings.paths.data_dir,
                session,
                event_seq=6,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )
            receipt = storage.load_delivery_state(settings.paths.data_dir, session)[
                "receipts"
            ][entry["ts"]]
            self.assertEqual(receipt["status"], "injected")
            self.assertEqual(receipt["event_seq"], 5)
            self.assertEqual(receipt["delivered_via"], "PostToolUse")

    def test_injected_question_records_first_observable_model_action(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "response")
            entry = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="這個修正實際改變了哪一段驗證流程？",
                route_metadata={"effective_lens": "carmack"},
                source_event_seq=3,
                source_fingerprint="change-a",
            )
            storage.mark_emitted(
                root,
                session,
                entry["ts"],
                event_seq=4,
                delivered_via="PostToolUse",
            )

            storage.observe_injected_response(
                root,
                session,
                event_seq=5,
                observation_kind="tool",
                observation={
                    "tool": "exec_command",
                    "command_family": "python -m unittest",
                    "failed": False,
                    "mutating": False,
                },
            )
            storage.observe_injected_response(
                root,
                session,
                event_seq=6,
                observation_kind="tool",
                observation={"tool": "apply_patch"},
            )

            receipt = storage.load_delivery_state(root, session)["receipts"][entry["ts"]]
            self.assertEqual(receipt["response_observation"]["event_seq"], 5)
            self.assertEqual(receipt["response_observation"]["kind"], "tool")
            self.assertEqual(
                receipt["response_observation"]["observation"]["command_family"],
                "python -m unittest",
            )
            observations = [
                value
                for value in storage.read_audit_entries(root, session)
                if value.get("kind") == "response_observation"
            ]
            self.assertEqual(len(observations), 1)

    def test_queued_nudge_is_never_selected_by_storage(self):
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
            self.assertFalse(hasattr(storage, "latest_pending"))
            self.assertNotIn(
                entry["ts"], storage.load_delivery_state(root, session)["receipts"]
            )

    def test_delivering_newer_nudge_does_not_reclassify_older_queue_entry(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            older = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="較舊觀察。",
                route_metadata={"effective_lens": "beck"},
            )
            newer = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="較新觀察。",
                route_metadata={"effective_lens": "beck"},
            )

            storage.mark_emitted(root, session, newer["ts"], event_seq=4)
            storage.observe_injected_response(
                root,
                session,
                event_seq=5,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )

            receipts = storage.load_delivery_state(root, session)["receipts"]
            self.assertNotIn(older["ts"], receipts)
            self.assertEqual(receipts[newer["ts"]]["status"], "injected")

    def test_recent_injected_findings_ignore_non_delivered_reviews(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            injected = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="第一個盲點。",
                route_metadata={"effective_lens": "carmack"},
            )
            failed = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="第二個盲點。",
                route_metadata={"effective_lens": "fowler"},
            )
            storage.mark_emitted(root, session, injected["ts"])
            storage.observe_injected_response(
                root,
                session,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )
            storage.mark_delivery(
                root,
                session,
                failed["ts"],
                status="failed",
            )

            recent = storage.read_recent_injected_findings(root, session, limit=3)

        self.assertEqual(("第一個盲點。",), recent)

    def test_recent_injected_findings_preserve_injection_order_and_limit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            for persona in ("beck", "fowler", "linus"):
                entry = storage.append_reaction(
                    root,
                    session,
                    provider="anthropic",
                    model="opus",
                    reaction=f"{persona} 的盲點。",
                    route_metadata={"effective_lens": persona},
                )
                storage.mark_emitted(root, session, entry["ts"])
                storage.observe_injected_response(
                    root,
                    session,
                    observation_kind="tool",
                    observation={"tool": "exec_command"},
                )

            recent = storage.read_recent_injected_findings(root, session, limit=2)

        self.assertEqual(("fowler 的盲點。", "linus 的盲點。"), recent)

    def test_review_attempt_identity_is_session_scoped_and_terminal(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            other = SessionRef("codex_cli", "other")

            token = storage.claim_review_attempt(root, session, "strategy", "first")
            self.assertTrue(token)
            self.assertFalse(
                storage.claim_review_attempt(root, session, "strategy", "first")
            )
            self.assertTrue(
                storage.claim_review_attempt(root, session, "strategy", "second")
            )
            self.assertTrue(
                storage.claim_review_attempt(root, other, "strategy", "first")
            )
            storage.finish_review_attempt(
                root, session, "strategy", "first", token, "no_finding"
            )
            self.assertFalse(
                storage.claim_review_attempt(root, session, "strategy", "first")
            )

class LongGoalReplayTests(unittest.TestCase):
    def test_first_semantic_change_creates_one_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)
            event = {
                "hook_event_name": "PostToolUse",
                "session_id": "normal-change",
                "turn_id": "t",
                "cwd": str(root),
                "tool_name": "apply_patch",
                "tool_input": {"command": "*** Begin Patch\n+change\n*** End Patch"},
                "tool_response": {"success": True},
            }

            adapter.process(event)
            adapter.process(event)

            self.assertEqual(len(core.calls), 1)
            self.assertEqual(core.calls[0].trigger, "evidence-ready")

    def test_each_new_verification_result_opens_one_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)
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
            self.assertEqual(len(core.calls), 3)
            self.assertEqual(
                {call.trigger for call in core.calls}, {"evidence-ready"}
            )

    def test_each_failure_result_opens_one_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)
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
            self.assertEqual([call.kind for call in core.calls], ["checkpoint"] * 2)
            self.assertEqual(core.calls[-1].trigger, "evidence-ready")

    def test_each_new_change_and_verification_can_be_reviewed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)

            def event(name, command, output):
                return {
                    "hook_event_name": "PostToolUse",
                    "session_id": "first-change",
                    "turn_id": "t",
                    "cwd": str(root),
                    "tool_name": name,
                    "tool_input": {"command": command},
                    "tool_response": {"exit_code": 0, "output": output},
                }

            adapter.process(event("apply_patch", "apply_patch first", "changed"))
            adapter.process(event("exec_command", "python -m pytest tests/a.py", "1 passed"))
            self.assertEqual([call.trigger for call in core.calls], ["evidence-ready"] * 2)

            adapter.process(event("apply_patch", "apply_patch second", "changed"))
            adapter.process(event("exec_command", "python -m pytest tests/b.py", "1 passed"))
            self.assertEqual(len(core.calls), 4)

            adapter.process(event("apply_patch", "apply_patch third", "changed"))
            adapter.process(event("exec_command", "python -m pytest tests/c.py", "1 passed"))
            self.assertEqual(
                [call.trigger for call in core.calls],
                ["evidence-ready"] * 6,
            )

    def test_goal_completion_does_not_create_a_late_review(self):
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
            self.assertEqual(core.calls, [])

    def test_old_turn_queued_nudge_does_not_create_goal_transition_review(self):
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
            self.assertEqual(core.calls, [])
            self.assertIsNone(output)

    def test_each_new_semantic_result_can_open_a_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(settings_for(root))
            adapter = CodexAdapter(core)
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
            self.assertEqual(len(core.calls), 8)
            self.assertEqual(
                {call.trigger for call in core.calls}, {"evidence-ready"}
            )

    def test_manual_stage_forces_each_existing_lens(self):
        cases = (
            ("review", "linus"),
            ("reliability", "lamport"),
            ("performance", "carmack"),
        )
        for stage, expected in cases:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                persona_config.save_stage(root, stage)
                route = lens_router.resolve_review_route(root, environ={})
                self.assertEqual(route.lens, expected)


if __name__ == "__main__":
    unittest.main()
