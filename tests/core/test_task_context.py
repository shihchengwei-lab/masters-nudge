"""Task context stays bounded, explicit, and batch-local."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import source_context
from masters_nudge import contracts, evidence, storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import SessionRef, ToolCompleted


class TaskContextTests(unittest.TestCase):
    def test_packet_keeps_every_native_result_in_order_without_categories(self):
        session = SessionRef("codex_cli", "ordered")
        inputs = (
            {"cmd": "Get-Content owner.py"},
            {"patch": "change-two"},
            {"cmd": "pytest -q"},
            {"file_path": "flag.py", "content": "enabled = True"},
        )
        events = [
            ToolCompleted(
                session,
                f"tool-{index}",
                tool_input=tool_input,
                tool_output=f"result-{index}",
                mutation=contracts.mutation_evidence_from_input(tool_input),
            )
            for index, tool_input in enumerate(inputs, start=1)
        ]
        with tempfile.TemporaryDirectory() as raw:
            observed = evidence.observe_tool_batch(Path(raw), events)
            packet = source_context.build_checkpoint_packet(
                task_anchor="task",
                evidence_records=observed.batch_records,
            )

        self.assertTrue(observed.eligible)
        markers = [
            marker
            for index in range(1, 5)
            for marker in (f"[tool result seq={index}]", f"result-{index}")
        ]
        positions = [packet.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("category=", packet)

    def test_single_result_uses_packet_space_left_by_the_actual_task(self):
        middle = "RELATION_OWNER_MUST_SURVIVE"
        event = ToolCompleted(
            SessionRef("codex_cli", "dynamic-single"),
            "read",
            tool_input={"path": "owner.py"},
            tool_output=("source-head\n" * 180) + middle + ("source-tail\n" * 180),
        )
        with tempfile.TemporaryDirectory() as raw:
            observed = evidence.observe_tool_batch(Path(raw), [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor="檢查 owner",
                evidence_records=observed.batch_records,
            )

        self.assertIn(middle, packet)
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)

    def test_multiple_results_share_remaining_packet_space(self):
        first_middle = "FIRST_RELATION_MUST_SURVIVE"
        second_middle = "SECOND_RELATION_MUST_SURVIVE"
        records = [
            {"seq": 1, "content": ("a" * 1700) + first_middle + ("b" * 1700)},
            {"seq": 2, "content": ("c" * 1700) + second_middle + ("d" * 1700)},
        ]
        packet = source_context.build_checkpoint_packet(
            task_anchor="檢查資料與控制流程的關係",
            evidence_records=records,
        )
        self.assertIn(first_middle, packet)
        self.assertIn(second_middle, packet)
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)

    def test_large_task_and_batch_obey_the_packet_limit(self):
        records = [
            {"seq": index, "content": "x" * 10000}
            for index in range(1, 5)
        ]
        packet = source_context.build_checkpoint_packet(
            task_anchor="task " * 1000,
            evidence_records=records,
        )
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)
        for index in range(1, 5):
            self.assertIn(f"[tool result seq={index}]", packet)

    def test_packet_uses_current_batch_without_prior_batch_history(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "clean-boundaries", cwd=raw)
            storage.start_turn(root, session, "保留乾淨的開頭與結尾")
            evidence.observe_tool_batch(
                root,
                [ToolCompleted(session, "read", {"path": "old.py"}, "prior-batch-result")],
            )
            current = evidence.observe_tool_batch(
                root,
                [ToolCompleted(session, "read", {"path": "current.py"}, "current-batch-result")],
            )
            packet = source_context.build_checkpoint_packet(
                task_anchor=current.turn_state["task_anchor"],
                evidence_records=current.batch_records,
            )

        self.assertIn("current-batch-result", packet)
        self.assertNotIn("prior-batch-result", packet)

    def test_task_path_mentions_never_read_the_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "TASK.md").write_text("must stay private", encoding="utf-8")
            session = SessionRef("codex_cli", "no-read", cwd=raw, repo_root=raw)
            storage.start_turn(root / "data", session, "不要讀 TASK.md")
            state = storage.load_turn_state(root / "data", session)

        self.assertNotIn("task_sources", state)
        self.assertNotIn("must stay private", json.dumps(state, ensure_ascii=False))

    def test_exact_replay_is_not_eligible(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "replay")
            tool_input = {"patch": "same change"}
            event = ToolCompleted(
                session,
                "unknown",
                tool_input,
                "same result",
                mutation=contracts.mutation_evidence_from_input(tool_input),
            )
            first = evidence.observe_tool_batch(root, [event])
            replay = evidence.observe_tool_batch(root, [event])

        self.assertTrue(first.eligible)
        self.assertFalse(replay.eligible)
        self.assertEqual(replay.batch_records, ())

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
