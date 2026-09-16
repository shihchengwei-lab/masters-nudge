"""Load-bearing state and audit behavior for one optional Nudge."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from masters_nudge import evidence, storage
from masters_nudge.contracts import (
    CompletedMutation,
    Nudge,
    SessionRef,
    ToolCompleted,
)


class LoadBearingCoreTests(unittest.TestCase):
    def test_nudge_expresses_only_message_and_evidence(self):
        self.assertEqual(list(Nudge.__dataclass_fields__), ["message", "evidence"])

    def test_exact_event_replay_is_the_only_event_duplicate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session")
            event = ToolCompleted(
                session,
                "apply_patch",
                tool_input={"patch": "*** Update File: app.py"},
                tool_output="done",
                mutation=CompletedMutation("*** Update File: app.py"),
            )
            first = evidence.observe_tool_batch(root, [event])
            replay = evidence.observe_tool_batch(root, [event])

        self.assertTrue(first.eligible)
        self.assertFalse(replay.eligible)

    def test_successful_delivery_marks_turn_and_writes_exact_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session", cwd=raw)
            storage.start_turn(root, session, "Keep one owner")
            storage.append_host_returned_nudge(
                root,
                session,
                message="兩個欄位表示同一個狀態。",
                evidence=("isSent", "isMarkedAsSent"),
                returned_via="PostToolBatch",
            )

            entries = storage.recent_nudges(root)
            delivered = storage.nudge_delivered(root, session)

        self.assertTrue(delivered)
        self.assertEqual(entries[0]["message"], "兩個欄位表示同一個狀態。")
        self.assertNotIn("decision", entries[0])
        self.assertNotIn("reframe", entries[0])
        self.assertNotIn("invariant", entries[0])

    def test_new_turn_resets_delivery_and_stores_exact_task(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session", cwd=raw)
            long_task = "T" * 50_000
            storage.start_turn(root, session, "First")
            storage.append_host_returned_nudge(
                root,
                session,
                message="message",
                evidence=("evidence",),
                returned_via="PostToolBatch",
            )
            storage.start_turn(root, session, long_task)
            state = storage.load_turn_state(root, session)
            delivered = storage.nudge_delivered(root, session)

        self.assertFalse(delivered)
        self.assertEqual(state["task_anchor"], long_task)
        self.assertNotIn("task_start_workspace", state)


if __name__ == "__main__":
    unittest.main()
