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


class DeliveryLifecycleTests(unittest.TestCase):
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
                reaction="Reviewer 逾時（120 秒）；本輪沒有 Nudge。",
                route_metadata={"effective_lens": "karis"},
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
                reaction="這個候選實際減少了哪一段 GPU 工作？",
                route_metadata={"effective_lens": "carmack"},
                source_event_seq=3,
                source_fingerprint="candidate-a",
                finding_scope="candidate",
            )
            storage.mark_delivered(
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
                    "command_family": "node --test",
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
                "node --test",
            )
            observations = [
                value
                for value in storage.read_reaction_entries(root, session)
                if value.get("kind") == "response_observation"
            ]
            self.assertEqual(len(observations), 1)

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

    def test_delivering_newer_nudge_marks_older_pending_as_superseded(self):
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

            storage.mark_delivered(root, session, newer["ts"], event_seq=4)

            receipts = storage.load_delivery_state(root, session)["receipts"]
            self.assertEqual(receipts[older["ts"]]["status"], "superseded")
            self.assertEqual(receipts[newer["ts"]]["status"], "injected")

    def test_recent_injected_personas_ignore_non_delivered_reviews(self):
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
            expired = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="第二個盲點。",
                route_metadata={"effective_lens": "karis"},
            )
            storage.mark_delivered(root, session, injected["ts"])
            storage.mark_delivery(
                root,
                session,
                expired["ts"],
                status="expired",
            )

            recent = storage.read_recent_injected_personas(root, session, limit=2)

        self.assertEqual(("carmack",), recent)

    def test_recent_injected_personas_preserve_injection_order_and_limit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            for persona in ("carmack", "karis", "quilez"):
                entry = storage.append_reaction(
                    root,
                    session,
                    provider="anthropic",
                    model="opus",
                    reaction=f"{persona} 的盲點。",
                    route_metadata={"effective_lens": persona},
                )
                storage.mark_delivered(root, session, entry["ts"])

            recent = storage.read_recent_injected_personas(root, session, limit=2)

        self.assertEqual(("karis", "quilez"), recent)

    def test_strategy_single_flight_is_session_scoped_and_releasable(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            other = SessionRef("codex_cli", "other")

            self.assertTrue(storage.claim_strategy_run(root, session, "first"))
            self.assertFalse(storage.claim_strategy_run(root, session, "second"))
            self.assertTrue(storage.claim_strategy_run(root, other, "other"))
            storage.release_strategy_run(root, session)
            self.assertTrue(storage.claim_strategy_run(root, session, "third"))

    def test_shader_pending_uses_source_freshness_instead_of_event_age(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            entry = storage.append_reaction(
                root,
                session,
                provider="grok",
                model="",
                reaction="新證據仍指向同一個成本轉移。",
                route_metadata={"effective_lens": "carmack"},
                reason="shader-research-change",
                source_event_seq=1,
                source_fingerprint="research-a",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=20,
                current_source_fingerprint="research-a",
            )

            self.assertEqual(pending["ts"], entry["ts"])

    def test_shader_trajectory_finding_survives_research_source_change(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            entry = storage.append_reaction(
                root,
                session,
                provider="grok",
                model="",
                reaction="候選仍只消除抵達 sample 後的片元工作。",
                route_metadata={"effective_lens": "akenine_moller"},
                reason="shader-research-change",
                source_fingerprint="research-old",
                finding_scope="trajectory",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=20,
                current_source_fingerprint="research-new",
            )

            self.assertEqual(pending["ts"], entry["ts"])
            self.assertEqual(pending["finding_scope"], "trajectory")
            receipts = storage.load_delivery_state(root, session)["receipts"]
            self.assertNotIn(entry["ts"], receipts)

            storage.mark_delivered(
                root,
                session,
                pending["ts"],
                event_seq=21,
                delivered_via="PostToolUse",
            )

            receipt = storage.load_delivery_state(root, session)["receipts"][entry["ts"]]
            self.assertEqual(receipt["status"], "injected")
            self.assertEqual(receipt["delivered_via"], "PostToolUse")

    def test_shader_candidate_question_survives_recent_source_change(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            entry = storage.append_reaction(
                root,
                session,
                provider="grok",
                model="",
                reaction="這次變更是否仍保留相同的效能瓶頸？",
                route_metadata={"effective_lens": "carmack"},
                reason="shader-research-change",
                source_event_seq=1,
                source_fingerprint="research-old",
                finding_scope="candidate",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=4,
                current_source_fingerprint="research-new",
            )

            self.assertEqual(pending["ts"], entry["ts"])
            self.assertNotIn(
                entry["ts"], storage.load_delivery_state(root, session)["receipts"]
            )

    def test_shader_candidate_question_expires_after_event_window(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "s")
            entry = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="這次變更是否仍保留相同的效能瓶頸？",
                route_metadata={"effective_lens": "carmack"},
                reason="shader-research-change",
                source_event_seq=1,
                source_fingerprint="research-old",
                finding_scope="candidate",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=8,
                current_source_fingerprint="research-new",
            )

            self.assertIsNone(pending)
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

    def test_eight_healthy_events_do_not_schedule_without_semantic_change(self):
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
            self.assertEqual(scheduled, [])

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
                    checkpoint=True,
                )
                self.assertEqual(route.effective_lens, expected)


if __name__ == "__main__":
    unittest.main()
