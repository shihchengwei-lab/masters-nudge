"""Long tasks retain their stated goal and explicitly named task source."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from masters_nudge import storage
from types import SimpleNamespace

from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import SessionRef


class TaskContextTests(unittest.TestCase):
    def test_task_source_is_read_once_when_the_turn_starts(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            task_file = root / "TASK.md"
            task_file.write_text("原始驗收：只保留必要責任。", encoding="utf-8")
            session = SessionRef("codex_cli", "task-source", cwd=raw, repo_root=raw)

            storage.start_turn(root / "data", session, "依照 `TASK.md` 執行")
            task_file.write_text("工作途中被改寫的內容", encoding="utf-8")
            state = storage.load_turn_state(root / "data", session)

        self.assertEqual(
            state["task_sources"],
            {"TASK.md": "原始驗收：只保留必要責任。"},
        )

    def test_plain_explicit_task_path_is_read_without_markdown_punctuation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "TASK.md").write_text(
                "白話路徑也必須成為任務證據。", encoding="utf-8"
            )
            session = SessionRef("codex_cli", "plain-task", cwd=raw, repo_root=raw)

            storage.start_turn(root / "data", session, "請依照 TASK.md 執行")
            state = storage.load_turn_state(root / "data", session)

        self.assertEqual(
            state["task_sources"],
            {"TASK.md": "白話路徑也必須成為任務證據。"},
        )

    def test_codex_recovers_an_explicit_goal_from_the_transcript(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = Path(raw) / "session.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "payload": {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": (
                                        '<codex_internal_context source="goal">'
                                        "<objective>持續刪除不承重機制</objective>"
                                        "</codex_internal_context>"
                                    ),
                                }
                            ],
                        }
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            data = Path(raw) / "data"
            core = SimpleNamespace(
                settings=SimpleNamespace(paths=SimpleNamespace(data_dir=data)),
                log_error=lambda _message: None,
            )
            CodexAdapter(core).process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "long-goal",
                    "cwd": raw,
                    "prompt": "",
                    "transcript_path": str(transcript),
                }
            )
            state = storage.load_turn_state(
                data,
                SessionRef("codex_cli", "long-goal", cwd=raw),
            )

        self.assertEqual(state["task_anchor"], "持續刪除不承重機制")


if __name__ == "__main__":
    unittest.main()
