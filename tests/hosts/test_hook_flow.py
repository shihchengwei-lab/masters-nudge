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
from masters_nudge.core import NudgeCore


class FakeCore:
    def __init__(self, data_dir: Path) -> None:
        self.settings = SimpleNamespace(
            paths=SimpleNamespace(data_dir=data_dir),
            provider="openai",
            model="test-model",
            lens="simplicity",
        )
        self.calls: list[str] = []
        self.log_error = lambda _message: None

    def review_contract_signature(self) -> str:
        return "test-contract"

    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome(
            "finding",
            finding="讓單一欄位直接擁有責任。",
            lens="simplicity",
        )

    def review_tool_batch(self, events):
        return NudgeCore.review_tool_batch(self, events)


class SilentCore(FakeCore):
    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome("no_finding")


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

    def test_identical_completed_checkpoint_is_suppressed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = SilentCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "reused-silence",
                    "cwd": raw,
                    "prompt": "檢查驗證結果",
                }
            )
            checkpoint = {
                "hook_event_name": "PostToolBatch",
                "session_id": "reused-silence",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "exec_command",
                        "tool_input": {"cmd": "python -m unittest"},
                        "tool_response": "Process exited with code 0",
                    }
                ],
            }

            first = adapter.process(checkpoint)
            second = adapter.process(checkpoint)
            state = storage.load_turn_state(
                root, SessionRef("codex_cli", "reused-silence", cwd=raw)
            )

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertEqual(len(core.calls), 1)
        self.assertEqual(state["evidence_seq"], 2)
        self.assertIn("checkpoint_signature", state["review_admission"])

    def test_pending_command_does_not_consume_the_completed_checkpoint(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = SilentCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "pending-check",
                    "cwd": raw,
                    "prompt": "完成測試後提供第二意見",
                }
            )
            base = {
                "hook_event_name": "PostToolBatch",
                "session_id": "pending-check",
                "cwd": raw,
            }
            pending = {
                **base,
                "tool_calls": [
                    {
                        "tool_name": "exec_command",
                        "tool_input": {"cmd": "python -m unittest"},
                        "tool_response": {
                            "output": "Script running with cell ID 9\nWall time 31.0 seconds"
                        },
                    }
                ],
            }
            completed = {
                **base,
                "tool_calls": [
                    {
                        "tool_name": "exec_command",
                        "tool_input": {"cmd": "python -m unittest"},
                        "tool_response": "Process exited with code 0; 83 tests passed",
                    }
                ],
            }

            adapter.process(pending)
            pending_state = storage.load_turn_state(
                root, SessionRef("codex_cli", "pending-check", cwd=raw)
            )
            adapter.process(completed)

        self.assertEqual(pending_state["evidence_seq"], 0)
        self.assertEqual(pending_state["review_admission"], {})
        self.assertEqual(len(core.calls), 1)

    def test_navigation_is_saved_without_calling_the_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "source-only",
                    "cwd": raw,
                    "prompt": "檢查 Client 選項傳遞",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "source-only",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "exec_command",
                            "tool_input": {
                                "cmd": "Get-Content lib/dispatcher/client.js"
                            },
                            "tool_response": "class Client extends DispatcherBase {}",
                        }
                    ],
                }
            )
            state = storage.load_turn_state(
                root,
                SessionRef("codex_cli", "source-only", cwd=raw),
            )

        self.assertIsNone(output)
        self.assertEqual(core.calls, [])
        self.assertEqual(len(state["actor_source_records"]), 1)

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
    def test_same_decision_generation_suppresses_a_repeated_verification(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            runtime = Path(__file__).resolve().parents[2]
            settings = SimpleNamespace(
                paths=SimpleNamespace(
                    data_dir=root,
                    runtime_dir=runtime,
                    error_log=root / "error.log",
                ),
                provider="openai",
                model="test-model",
                lens="simplicity",
                ollama_url="http://localhost:11434",
            )
            hook = {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude-reused-silence",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "Bash",
                        "tool_input": {"command": "python -m unittest"},
                        "tool_response": "Exit code 0\n10 passed",
                    }
                ],
            }
            storage.start_turn(
                root,
                SessionRef("claude_code", "claude-reused-silence", cwd=raw),
                "檢查驗證結果",
            )

            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    NudgeCore,
                    "nudge_once",
                    return_value=NudgeOutcome("no_finding"),
                ) as checkpoint,
            ):
                first = claude_checkpoint.prepare_hook(hook)
                second = claude_checkpoint.prepare_hook(hook)
            state = storage.load_turn_state(
                root,
                SessionRef("claude_code", "claude-reused-silence", cwd=raw),
            )

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertEqual(checkpoint.call_count, 1)
        self.assertEqual(state["evidence_seq"], 2)
        self.assertEqual(len(state["review_admission"]["checkpoint_signature"]), 64)

    def test_post_tool_batch_returns_nudge_and_audits_after_flush(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = SimpleNamespace(
                paths=SimpleNamespace(
                    data_dir=root,
                    runtime_dir=Path(__file__).resolve().parents[2],
                    error_log=root / "error.log",
                ),
                provider="openai",
                model="test-model",
                lens="simplicity",
                ollama_url="http://localhost:11434",
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
            def checkpoint(_core, packet, timeout_sec=None):
                self.assertIn("evidence seq=2", packet)
                return NudgeOutcome(
                    "finding",
                    finding="讓單一欄位直接擁有責任。",
                    lens="simplicity",
                )

            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    NudgeCore,
                    "nudge_once",
                    autospec=True,
                    side_effect=checkpoint,
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
