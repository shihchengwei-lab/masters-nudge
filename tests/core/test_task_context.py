"""Task and completed mutation are preserved without workspace reconstruction."""

from __future__ import annotations

import unittest

import source_context
from masters_nudge.codex_adapter import _task_anchor
from masters_nudge.contracts import CompletedMutation, SessionRef, ToolCompleted


class TaskContextTests(unittest.TestCase):
    def test_goal_and_current_request_form_the_task_contract(self):
        anchor = _task_anchor(
            {"goal": {"objective": "Keep one owner"}, "prompt": "Handle empty input"}
        )
        self.assertEqual(
            anchor,
            "Goal:\nKeep one owner\n\nCurrent request:\nHandle empty input",
        )

    def test_replacement_keeps_before_and_after_text(self):
        mutation = CompletedMutation(
            "path: state.ts\n"
            "[before]\nconst sent = false;\n[end before]\n"
            "[after]\nconst sent = request.sent;\n[end after]"
        )
        event = ToolCompleted(
            SessionRef("codex_cli", "session"),
            "Edit",
            mutation=mutation,
        )

        observation = source_context.build_observation("Keep one owner", [event])

        self.assertIn("path: state.ts", observation)
        self.assertIn("[before]\nconst sent = false;", observation)
        self.assertIn("[after]\nconst sent = request.sent;", observation)

    def test_missing_task_or_change_is_not_reconstructed(self):
        session = SessionRef("codex_cli", "session")
        with self.assertRaises(ValueError):
            source_context.build_observation("", [])
        with self.assertRaises(ValueError):
            source_context.build_observation("Task", [ToolCompleted(session, "Read")])


if __name__ == "__main__":
    unittest.main()
