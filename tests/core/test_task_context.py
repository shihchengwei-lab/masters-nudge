"""Decision snapshots preserve task and workspace boundaries."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import source_context
from masters_nudge.codex_adapter import _task_anchor


class TaskContextTests(unittest.TestCase):
    def test_goal_and_current_request_form_the_task_contract(self):
        anchor = _task_anchor(
            {"goal": {"objective": "Keep one owner"}, "prompt": "Handle empty input"}
        )
        self.assertEqual(anchor, "Goal:\nKeep one owner\n\nCurrent request:\nHandle empty input")

    def test_changed_source_must_stay_inside_workspace(self):
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside:
            root = Path(raw)
            (root / "inside.py").write_text("inside = True\n", encoding="utf-8")
            outside_path = Path(outside) / "secret.py"
            outside_path.write_text("secret = True\n", encoding="utf-8")
            packet = source_context.build_decision_snapshot(
                task_contract="Task",
                task_start="status:\n(clean)",
                workspace_root=raw,
                changed_paths=("inside.py", str(outside_path)),
            )
        self.assertIn("inside = True", packet)
        self.assertNotIn("secret = True", packet)

    def test_snapshot_is_bounded(self):
        packet = source_context.build_decision_snapshot(
            task_contract="T" * 100_000,
            task_start="S" * 100_000,
            workspace_root="",
        )
        self.assertLessEqual(len(packet), source_context.DECISION_SNAPSHOT_MAX_CHARS)


if __name__ == "__main__":
    unittest.main()
