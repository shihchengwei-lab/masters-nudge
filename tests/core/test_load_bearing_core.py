"""Load-bearing state and audit behavior for one advisory intervention."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from masters_nudge import evidence, storage
from masters_nudge.contracts import (
    MutationEvidence,
    MutationTarget,
    NudgeOutcome,
    SessionRef,
    ToolCompleted,
)


class LoadBearingCoreTests(unittest.TestCase):
    def test_outcome_expresses_only_the_decision_and_advice(self):
        self.assertEqual(
            list(NudgeOutcome.__dataclass_fields__),
            ["decision", "current_choice", "structural_cost", "direction", "evidence"],
        )

    def test_exact_event_replay_is_the_only_event_duplicate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session")
            event = ToolCompleted(
                session,
                "apply_patch",
                tool_input={"patch": "*** Update File: app.py"},
                tool_output="done",
                mutation=MutationEvidence("patch", (MutationTarget("app.py"),)),
            )
            first = evidence.observe_tool_batch(root, [event])
            replay = evidence.observe_tool_batch(root, [event])

        self.assertTrue(first.eligible)
        self.assertFalse(replay.eligible)

    def test_successful_delivery_marks_the_turn_and_writes_audit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session", cwd=raw)
            storage.start_turn(root, session, "Keep one owner")
            storage.append_host_returned_nudge(
                root,
                session,
                current_choice="新增第二個 owner",
                structural_cost="責任可能分歧",
                direction="沿用既有 owner",
                evidence=("src/state.ts:owner",),
                returned_via="PostToolBatch",
            )

            entries = storage.recent_nudges(root)
            delivered = storage.intervention_delivered(root, session)

        self.assertTrue(delivered)
        self.assertEqual(entries[0]["decision"], "intervene")
        self.assertEqual(entries[0]["direction"], "沿用既有 owner")

    def test_new_turn_resets_delivery_state_and_captures_workspace_start(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "session", cwd=raw)
            storage.start_turn(root, session, "First")
            storage.append_host_returned_nudge(
                root,
                session,
                current_choice="choice",
                structural_cost="cost",
                direction="direction",
                evidence=("app.py:owner",),
                returned_via="PostToolBatch",
            )
            storage.start_turn(root, session, "Second")
            state = storage.load_turn_state(root, session)
            delivered = storage.intervention_delivered(root, session)

        self.assertFalse(delivered)
        self.assertEqual(state["task_anchor"], "Second")
        self.assertIn("task_start_workspace", state)


if __name__ == "__main__":
    unittest.main()
