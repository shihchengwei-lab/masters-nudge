"""Both Host hooks preserve explicit event facts and audit only a wire return."""

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
    def __init__(self, data_dir: Path, *, evidence_seq: int = 1) -> None:
        self.settings = SimpleNamespace(paths=SimpleNamespace(data_dir=data_dir))
        self.calls: list[str] = []
        self.log_error = lambda _message: None
        self.evidence_seq = evidence_seq

    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome(
            "finding",
            principle="causality",
            anchor="batch owner",
            relationship="讓單一欄位直接擁有責任。",
            evidence_seq=self.evidence_seq,
        )


class NoFindingCore(FakeCore):
    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome("no_finding")


class BrokenStream:
    def write(self, _value):
        raise OSError("wire closed")

    def flush(self):
        pass


class CodexHookFlowTests(unittest.TestCase):
    def test_command_and_result_text_never_trigger_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw))
            adapter = CodexAdapter(core)
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "read-only",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch_preview",
                            "tool_input": {"cmd": "echo build"},
                            "tool_response": {
                                "success": False,
                                "output": "Traceback RuntimeError tests failed",
                            },
                        }
                    ],
                }
            )

        self.assertIsNone(output)
        self.assertEqual(core.calls, [])

    def test_explicit_mutation_returns_grounded_nudge_with_raw_batch(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root, evidence_seq=2)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-batch",
                    "cwd": raw,
                    "prompt": "檢查明確修改",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-batch",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "read",
                            "tool_input": {"path": "owner.py"},
                            "tool_response": "owner source",
                        },
                        {
                            "tool_name": "unknown_host_tool",
                            "tool_input": {
                                "command": "wrapper --apply",
                                "patch": "*** Update File: owner.py\n@@\n-old\n+new",
                            },
                            "tool_response": {"success": True},
                        },
                    ],
                }
            )

        self.assertIsNotNone(output)
        self.assertEqual(output["_masters_nudge"]["evidence_seq"], 2)
        self.assertIn("[tool result seq=1]", core.calls[0])
        self.assertIn("[tool result seq=2]", core.calls[0])
        self.assertIn('"command": "wrapper --apply"', core.calls[0])
        self.assertIn('"patch": "*** Update File: owner.py', core.calls[0])
        self.assertNotIn("category=", core.calls[0])

    def test_codex_native_apply_patch_command_calls_provider_once(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-native-patch",
                    "cwd": raw,
                    "prompt": "修改 app.py",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-native-patch",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {
                                "command": (
                                    "*** Begin Patch\n"
                                    "*** Add File: app.py\n"
                                    "+print('ready')\n"
                                    "*** End Patch"
                                )
                            },
                            "tool_response": "Success. Updated app.py",
                        }
                    ],
                }
            )

        self.assertIsNotNone(output)
        self.assertEqual(len(core.calls), 1)
        self.assertEqual(output["_masters_nudge"]["evidence_seq"], 1)
        self.assertIn('"command": "*** Begin Patch', core.calls[0])

    def test_codex_provider_receives_an_explicit_local_task_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "TASK.md").write_text(
                "A handler result must not replace the current config.",
                encoding="utf-8",
            )
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-task-source",
                    "cwd": raw,
                    "prompt": "Read TASK.md and complete the task.",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-task-source",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {
                                "command": (
                                    "*** Begin Patch\n"
                                    "*** Update File: app.py\n"
                                    "@@\n-old\n+new\n"
                                    "*** End Patch"
                                )
                            },
                            "tool_response": "Success. Updated app.py",
                        }
                    ],
                }
            )

        self.assertIsNotNone(output)
        self.assertIn("source: TASK.md", core.calls[0])
        self.assertIn("must not replace the current config", core.calls[0])

    def test_provider_sequence_must_name_a_visible_record(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw), evidence_seq=3)
            output = CodexAdapter(core).process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "bad-seq",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "unknown",
                            "tool_input": {"diff": "one mutation"},
                            "tool_response": "done",
                        }
                    ],
                }
            )

        self.assertIsNone(output)
        self.assertEqual(len(core.calls), 1)

    def test_no_finding_is_silent_and_creates_no_audit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = NoFindingCore(root)
            output = CodexAdapter(core).process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "silent",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "unknown",
                            "tool_input": {"patch": "change"},
                            "tool_response": "done",
                        }
                    ],
                }
            )

        self.assertIsNone(output)
        self.assertEqual(storage.recent_nudges(root), [])

    def test_wire_flush_commits_audit_and_failed_write_does_not(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            payload = {
                "hook_event_name": "PostToolBatch",
                "session_id": "wire",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "unknown",
                        "tool_input": {"patch": "change"},
                        "tool_response": "done",
                    }
                ],
            }
            output = CodexAdapter(core).process(payload)
            settings = SimpleNamespace(paths=SimpleNamespace(data_dir=root))

            with self.assertRaises(OSError):
                hook_entry._emit_output(output, settings, stream=BrokenStream())
            self.assertEqual(storage.recent_nudges(root), [])

            stream = io.StringIO()
            hook_entry._emit_output(output, settings, stream=stream)
            entries = storage.recent_nudges(root)

        public = json.loads(stream.getvalue())
        self.assertNotIn("_masters_nudge", public)
        self.assertEqual(entries[0]["evidence_seq"], 1)


class ClaudeHookFlowTests(unittest.TestCase):
    def settings(self, data_dir: Path):
        return SimpleNamespace(
            paths=SimpleNamespace(data_dir=data_dir, error_log=data_dir / "error.log")
        )

    def test_claude_normalizer_uses_the_same_explicit_mutation_contract(self):
        events = claude_checkpoint.normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude-normalize",
                "tool_calls": [
                    {
                        "tool_name": "EditPreview",
                        "tool_input": {"text": "proposal"},
                        "tool_response": {"is_error": False},
                    },
                    {
                        "tool_name": "Anything",
                        "tool_input": {"file_path": "a.py", "content": ""},
                        "tool_response": {"is_error": True},
                    },
                ],
            }
        )

        self.assertIsNone(events[0].mutation)
        self.assertEqual(events[1].mutation.kind, "content")
        self.assertFalse(hasattr(events[1], "failed"))

    def test_claude_prepares_only_a_visible_grounded_finding(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = self.settings(root)
            storage.start_turn(root, SessionRef("claude_code", "claude", cwd=raw), "task")
            hook = {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "Anything",
                        "tool_input": {"diff": "diff --git a/a.py b/a.py"},
                        "tool_response": "done",
                    }
                ],
            }
            with (
                mock.patch.object(claude_adapter, "runtime_settings", return_value=settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=NudgeOutcome(
                        "finding",
                        "causality",
                        "owner",
                        "責任缺少單一擁有者。",
                        evidence_seq=1,
                    ),
                ),
            ):
                prepared = claude_checkpoint.prepare_hook(hook)

        self.assertIsNotNone(prepared)
        self.assertEqual(prepared.evidence_seq, 1)

    def test_claude_audits_only_after_successful_flush(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = self.settings(root)
            prepared = claude_adapter.PreparedDelivery(
                output={"hookSpecificOutput": {"additionalContext": "nudge"}},
                session=SessionRef("claude_code", "wire", cwd=raw),
                principle="causality",
                evidence_seq=1,
                anchor="owner",
                relationship="責任缺少單一擁有者。",
                returned_via="PostToolBatch",
            )
            with mock.patch.object(claude_adapter, "runtime_settings", return_value=settings):
                with self.assertRaises(OSError):
                    claude_adapter.emit_json_delivery(prepared, BrokenStream())
                self.assertEqual(storage.recent_nudges(root), [])

                stream = io.StringIO()
                claude_adapter.emit_json_delivery(prepared, stream)
                entries = storage.recent_nudges(root)

        self.assertEqual(entries[0]["evidence_seq"], 1)


if __name__ == "__main__":
    unittest.main()
