"""Both host hooks must return the Nudge and audit only a successful wire write."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import claude_checkpoint
import hook_entry
from masters_nudge import claude_adapter, storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import NudgeOutcome, SessionRef


class FakeCore:
    def __init__(self, data_dir: Path) -> None:
        self.settings = SimpleNamespace(
            paths=SimpleNamespace(data_dir=data_dir),
        )
        self.calls: list[str] = []
        self.log_error = lambda _message: None

    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome(
            "finding",
            finding="讓單一欄位直接擁有責任。",
            lens="simplicity",
        )


class CodexHookFlowTests(unittest.TestCase):
    def test_post_tool_use_is_not_treated_as_a_batch(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw))
            output = CodexAdapter(core).process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "old-control-point",
                    "cwd": raw,
                    "tool_name": "apply_patch",
                    "tool_input": {"patch": "*** Update File: app.py"},
                    "tool_response": {"success": True},
                }
            )

        self.assertIsNone(output)
        self.assertEqual(core.calls, [])

    def test_post_tool_batch_returns_one_nudge_for_the_complete_batch(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-flow",
                    "cwd": raw,
                    "prompt": "簡化責任配置",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-flow",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "*** Update File: app.py"},
                            "tool_response": {"success": True},
                        },
                        {
                            "tool_name": "exec_command",
                            "tool_input": {"cmd": "python -m unittest"},
                            "tool_response": "Process exited with code 0",
                        },
                    ],
                }
            )
            self.assertIsNotNone(output)
            self.assertEqual(len(core.calls), 1)
            self.assertIn("*** Update File: app.py", core.calls[0])
            self.assertIn("python -m unittest", core.calls[0])
            self.assertIn("Process exited with code 0", core.calls[0])
            self.assertEqual(storage.recent_nudges(root), [])

            stream = io.StringIO()
            hook_entry._emit_output(output, core.settings, stream=stream)
            public_text = stream.getvalue()
            public = json.loads(public_text)
            audit = storage.recent_nudges(root)

        self.assertIn(
            "讓單一欄位直接擁有責任。",
            public["hookSpecificOutput"]["additionalContext"],
        )
        self.assertNotIn("_masters_nudge", public_text)
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["returned_via"], "PostToolBatch")

    def test_post_tool_batch_rejects_a_partially_malformed_batch(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw))
            output = CodexAdapter(core).process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "malformed-batch",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "*** Update File: app.py"},
                            "tool_response": {"success": True},
                        },
                        {"tool_name": "exec_command", "tool_input": {"cmd": "test"}},
                    ],
                }
            )

        self.assertIsNone(output)
        self.assertEqual(core.calls, [])

    def test_failed_wire_write_does_not_create_an_audit_entry(self):
        class BrokenStream:
            def write(self, _value):
                raise OSError("wire closed")

            def flush(self):
                raise AssertionError("flush should not be reached")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "failed-wire",
                    "cwd": raw,
                    "prompt": "簡化責任配置",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "failed-wire",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "*** Update File: app.py"},
                            "tool_response": {"success": True},
                        },
                        {
                            "tool_name": "exec_command",
                            "tool_input": {"cmd": "python -m unittest"},
                            "tool_response": "Process exited with code 0",
                        }
                    ],
                }
            )

            with self.assertRaises(OSError):
                hook_entry._emit_output(output, core.settings, stream=BrokenStream())

            self.assertEqual(storage.recent_nudges(root), [])
            self.assertEqual(
                storage.load_turn_state(root, SessionRef("codex_cli", "failed-wire", cwd=raw))[
                    "previous_findings"
                ],
                [],
            )


class ClaudeHookFlowTests(unittest.TestCase):
    def test_post_tool_batch_returns_nudge_and_audits_after_flush(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = SimpleNamespace(
                paths=SimpleNamespace(data_dir=root, error_log=root / "error.log"),
            )
            session = SessionRef("claude_code", "claude-flow", cwd=raw)
            storage.start_turn(root, session, "簡化責任配置")
            hook = {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude-flow",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "Edit",
                        "tool_input": {"file_path": "app.py"},
                        "tool_response": "updated",
                    },
                    {
                        "tool_name": "Bash",
                        "tool_input": {"command": "python -m unittest"},
                        "tool_response": "1 test passed",
                    }
                ],
            }
            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=NudgeOutcome(
                        "finding",
                        finding="讓單一欄位直接擁有責任。",
                        lens="simplicity",
                    ),
                ),
            ):
                prepared = claude_checkpoint.prepare_hook(hook)
                self.assertIsNotNone(prepared)
                self.assertEqual(storage.recent_nudges(root), [])
                stream = io.StringIO()
                claude_adapter.emit_json_delivery(prepared, stream=stream)
                audit = storage.recent_nudges(root)
                findings = storage.load_turn_state(root, session)["previous_findings"]

        self.assertIn("讓單一欄位直接擁有責任。", stream.getvalue())
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["returned_via"], "PostToolBatch")
        self.assertEqual(findings, ["讓單一欄位直接擁有責任。"])


if __name__ == "__main__":
    unittest.main()
