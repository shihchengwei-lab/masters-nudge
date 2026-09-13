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
from masters_nudge import claude_adapter, evidence, storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import NudgeOutcome, SessionRef, ToolCompleted


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
            principle="causality",
            anchor="batch owner",
            relationship="讓單一欄位直接擁有責任。",
        )


class NoFindingCore(FakeCore):
    def nudge_once(self, source_packet: str, timeout_sec=None) -> NudgeOutcome:
        self.calls.append(source_packet)
        return NudgeOutcome("no_finding")


class CodexHookFlowTests(unittest.TestCase):
    def test_no_finding_returns_silence_without_creating_nudge_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = NoFindingCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-silent",
                    "cwd": raw,
                    "prompt": "簡化責任配置",
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-silent",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "change"},
                            "tool_response": {"success": True},
                        }
                    ],
                }
            )
            session = SessionRef("codex_cli", "codex-silent", cwd=raw)

            self.assertIsNone(output)
            self.assertEqual(storage.recent_nudges(root), [])
            self.assertFalse(
                storage.load_turn_state(root, session)["nudge_pending_validation"]
            )

    def test_actor_result_replays_the_deferred_change_to_the_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-deferred-change",
                    "cwd": raw,
                    "prompt": "檢查修改後的實際結果",
                }
            )
            session = SessionRef("codex_cli", "codex-deferred-change", cwd=raw)
            storage.append_host_returned_nudge(
                root,
                session,
                principle="causality",
                anchor="owner",
                relationship="目前的責任可能分散。",
                returned_via="PostToolBatch",
            )

            deferred = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-deferred-change",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "latest implementation decision"},
                            "tool_response": "change completed",
                        }
                    ],
                }
            )
            reviewed = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-deferred-change",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "pytest -q"},
                            "tool_response": {"exit_code": 0, "output": "1 passed"},
                        }
                    ],
                }
            )

        self.assertIsNone(deferred)
        self.assertIsNotNone(reviewed)
        self.assertEqual(len(core.calls), 1)
        self.assertIn("change completed", core.calls[0])
        self.assertIn("1 passed", core.calls[0])
        self.assertLess(
            core.calls[0].index("change completed"),
            core.calls[0].index("1 passed"),
        )

    def test_read_and_failure_only_batches_do_not_call_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-success-status-code",
                    "cwd": raw,
                    "prompt": "檢查快取流程",
                }
            )
            first = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-success-status-code",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "read",
                            "tool_input": {"path": "first.js"},
                            "tool_response": {"exit_code": 0, "output": "first source"},
                        }
                    ],
                }
            )
            second = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-success-status-code",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "Get-Content cache.js"},
                            "tool_response": {
                                "exit_code": 0,
                                "output": "if (statusCode = 304) { return cached }",
                            },
                        }
                    ],
                }
            )
            third = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-success-status-code",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "Get-Content missing.js"},
                            "tool_response": {
                                "exit_code": 1,
                                "output": "file not found",
                            },
                        }
                    ],
                }
            )

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertIsNone(third)
        self.assertEqual(len(core.calls), 0)

    def test_no_finding_then_test_results_do_not_call_provider_again(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = NoFindingCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-no-finding-tests",
                    "cwd": raw,
                    "prompt": "修改後執行多次檢查",
                }
            )

            changed = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-no-finding-tests",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "change owner"},
                            "tool_response": "changed",
                        }
                    ],
                }
            )
            first_test = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-no-finding-tests",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "pytest -q"},
                            "tool_response": {"exit_code": 0, "output": "1 passed"},
                        }
                    ],
                }
            )
            second_test = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-no-finding-tests",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "python verify.py"},
                            "tool_response": {"exit_code": 1, "output": "failed"},
                        }
                    ],
                }
            )

        self.assertIsNone(changed)
        self.assertIsNone(first_test)
        self.assertIsNone(second_test)
        self.assertEqual(len(core.calls), 1)

    def test_provider_receives_only_the_latest_three_returned_nudges_for_deduplication(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            payload = {
                "hook_event_name": "UserPromptSubmit",
                "session_id": "codex-dedup",
                "cwd": raw,
                "prompt": "檢查責任配置",
            }
            adapter.process(payload)
            session = SessionRef("codex_cli", "codex-dedup", cwd=raw)
            for index in range(4):
                storage.append_host_returned_nudge(
                    root,
                    session,
                    principle="causality",
                    anchor=f"owner-{index}",
                    relationship=f"relationship-{index}",
                    returned_via="PostToolBatch",
                )
                evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "apply_patch",
                            tool_input={"patch": f"accepted-change-{index}"},
                            tool_output="changed",
                            mutating=True,
                        )
                    ],
                )
                evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "exec_command",
                            tool_input={"cmd": f"pytest -q -k cycle_{index}"},
                            tool_output="1 passed",
                        )
                    ],
                )

            adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-dedup",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "current-change"},
                            "tool_response": "current-result",
                        }
                    ],
                }
            )

        self.assertNotIn("relationship-0", core.calls[0])
        for index in range(1, 4):
            self.assertIn(f"relationship-{index}", core.calls[0])
        self.assertLess(
            core.calls[0].index("relationship-3"),
            core.calls[0].index("current-result"),
        )

    def test_change_uses_related_source_without_prior_read_carryover(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "owner.py").write_text(
                """def decide(base, target):
    return resolve(base, target)

def choose(context, options):
    return decide(context.base, options.target)
""",
                encoding="utf-8",
            )
            core = FakeCore(root)
            adapter = CodexAdapter(core)
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "codex-read-gate",
                    "cwd": raw,
                    "prompt": "檢查責任配置",
                }
            )
            first = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-read-gate",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "read",
                            "tool_input": {"path": "first.py"},
                            "tool_response": "first source",
                        }
                    ],
                }
            )
            second = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-read-gate",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "read",
                            "tool_input": {"path": "second.py"},
                            "tool_response": "second source",
                        }
                    ],
                }
            )
            changed = adapter.process(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "codex-read-gate",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {
                                "patch": """*** Update File: owner.py
@@
-    return old_path(options.target)
+    return decide(context.base, options.target)
"""
                            },
                            "tool_response": "changed",
                        }
                    ],
                }
            )

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertIsNotNone(changed)
        self.assertEqual(len(core.calls), 1)
        self.assertNotIn("first source", core.calls[0])
        self.assertNotIn("second source", core.calls[0])
        self.assertIn("related_source:", core.calls[0])
        self.assertIn("reference: decide", core.calls[0])
        self.assertIn("def decide(base, target):", core.calls[0])
        self.assertIn("return resolve(base, target)", core.calls[0])

    def test_post_tool_batch_returns_one_nudge_with_every_ordered_result(self):
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
                            "tool_name": "read",
                            "tool_input": {"path": "app.py"},
                            "tool_response": "first-result",
                        },
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {"patch": "second-change"},
                            "tool_response": {"success": True},
                        },
                    ],
                }
            )
            self.assertIsNotNone(output)
            self.assertEqual(len(core.calls), 1)
            self.assertLess(
                core.calls[0].index("first-result"),
                core.calls[0].index("second-change"),
            )
            self.assertEqual(storage.recent_nudges(root), [])

            stream = io.StringIO()
            hook_entry._emit_output(output, core.settings, stream=stream)
            public_text = stream.getvalue()
            public = json.loads(public_text)
            audit = storage.recent_nudges(root)
            turn_state = storage.load_turn_state(
                root, SessionRef("codex_cli", "codex-flow", cwd=raw)
            )

        self.assertIn(
            "causality warning: batch owner — 讓單一欄位直接擁有責任。",
            public["hookSpecificOutput"]["additionalContext"],
        )
        self.assertNotIn(
            "獨立第二意見",
            public["hookSpecificOutput"]["additionalContext"],
        )
        self.assertNotIn("_masters_nudge", public_text)
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["principle"], "causality")
        self.assertEqual(audit[0]["anchor"], "batch owner")
        self.assertEqual(audit[0]["relationship"], "讓單一欄位直接擁有責任。")
        self.assertEqual(audit[0]["returned_via"], "PostToolBatch")
        self.assertTrue(turn_state["nudge_pending_validation"])

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
                            "tool_input": {
                                "patch": (
                                    "*** Update File: app.py\n@@\n"
                                    "-owner = old\n+owner = direct\n"
                                )
                            },
                            "tool_response": {"success": True},
                        }
                    ],
                }
            )

            with self.assertRaises(OSError):
                hook_entry._emit_output(output, core.settings, stream=BrokenStream())

            self.assertEqual(storage.recent_nudges(root), [])
            self.assertFalse(
                storage.load_turn_state(
                    root, SessionRef("codex_cli", "failed-wire", cwd=raw)
                )["nudge_pending_validation"]
            )


class ClaudeHookFlowTests(unittest.TestCase):
    def test_no_finding_returns_silence_without_creating_nudge_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = SimpleNamespace(
                paths=SimpleNamespace(data_dir=root, error_log=root / "error.log"),
            )
            session = SessionRef("claude_code", "claude-silent", cwd=raw)
            storage.start_turn(root, session, "簡化責任配置")
            hook = {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude-silent",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "Edit",
                        "tool_input": {
                            "file_path": "app.py",
                            "old_string": "owner = old",
                            "new_string": "owner = direct",
                        },
                        "tool_response": "updated",
                    }
                ],
            }
            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=NudgeOutcome("no_finding"),
                ),
            ):
                prepared = claude_checkpoint.prepare_hook(hook)
                self.assertIsNone(prepared)

            self.assertEqual(storage.recent_nudges(root), [])
            self.assertFalse(
                storage.load_turn_state(root, session)["nudge_pending_validation"]
            )

    def test_provider_receives_latest_returned_nudges_for_deduplication(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = SimpleNamespace(
                paths=SimpleNamespace(data_dir=root, error_log=root / "error.log"),
            )
            session = SessionRef("claude_code", "claude-dedup", cwd=raw)
            storage.start_turn(root, session, "檢查責任配置")
            storage.append_host_returned_nudge(
                root,
                session,
                principle="predictability",
                anchor="old-owner",
                relationship="old-relationship",
                returned_via="PostToolBatch",
            )
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "Edit",
                        tool_input={
                            "file_path": "accepted.py",
                            "old_string": "owner = old",
                            "new_string": "owner = accepted",
                        },
                        tool_output="accepted change",
                        mutating=True,
                    )
                ],
            )
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "pytest -q"},
                        tool_output="1 passed",
                    )
                ],
            )
            hook = {
                "hook_event_name": "PostToolBatch",
                "session_id": "claude-dedup",
                "cwd": raw,
                "tool_calls": [
                    {
                        "tool_name": "Edit",
                        "tool_input": {
                            "file_path": "current.py",
                            "old_string": "owner = old",
                            "new_string": "owner = current",
                        },
                        "tool_response": "current-result",
                    }
                ],
            }
            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=NudgeOutcome("no_finding"),
                ) as provider,
            ):
                claude_checkpoint.prepare_hook(hook)

        packet = provider.call_args.args[0]
        self.assertIn("old-relationship", packet)
        self.assertLess(
            packet.index("old-relationship"), packet.index("current-result")
        )

    def test_change_uses_related_source_without_prior_read_carryover(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "owner.py").write_text(
                """function decide(base, target) {
  return resolve(base, target)
}

function choose(context, options) {
  return decide(context.base, options.target)
}
""",
                encoding="utf-8",
            )
            settings = SimpleNamespace(
                paths=SimpleNamespace(data_dir=root, error_log=root / "error.log"),
            )
            session = SessionRef("claude_code", "claude-read-gate", cwd=raw)
            storage.start_turn(root, session, "檢查責任配置")

            def hook(path: str) -> dict:
                return {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "claude-read-gate",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "Read",
                            "tool_input": {"file_path": path},
                            "tool_response": f"source from {path}",
                        }
                    ],
                }

            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=NudgeOutcome("no_finding"),
                ) as provider,
            ):
                self.assertIsNone(claude_checkpoint.prepare_hook(hook("first.py")))
                self.assertIsNone(claude_checkpoint.prepare_hook(hook("second.py")))
                changed = claude_checkpoint.prepare_hook(
                    {
                        "hook_event_name": "PostToolBatch",
                        "session_id": "claude-read-gate",
                        "cwd": raw,
                        "tool_calls": [
                            {
                                "tool_name": "Edit",
                                "tool_input": {
                                    "file_path": "owner.py",
                                    "old_string": "return oldPath(options.target)",
                                    "new_string": "return decide(context.base, options.target)",
                                },
                                "tool_response": "changed",
                            }
                        ],
                    }
                )

        self.assertIsNone(changed)
        provider.assert_called_once()
        packet = provider.call_args.args[0]
        self.assertNotIn("source from first.py", packet)
        self.assertNotIn("source from second.py", packet)
        self.assertIn("related_source:", packet)
        self.assertIn("reference: decide", packet)
        self.assertIn("function decide(base, target)", packet)
        self.assertIn("return resolve(base, target)", packet)

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
                        "tool_input": {
                            "file_path": "app.py",
                            "old_string": "owner = old",
                            "new_string": "owner = direct",
                        },
                        "tool_response": "updated",
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
                        principle="causality",
                        anchor="batch owner",
                        relationship="讓單一欄位直接擁有責任。",
                    ),
                ),
            ):
                prepared = claude_checkpoint.prepare_hook(hook)
                self.assertIsNotNone(prepared)
                self.assertEqual(storage.recent_nudges(root), [])
                stream = io.StringIO()
                claude_adapter.emit_json_delivery(prepared, stream=stream)
                audit = storage.recent_nudges(root)
                turn_state = storage.load_turn_state(root, session)

        self.assertIn(
            "causality warning: batch owner — 讓單一欄位直接擁有責任。",
            stream.getvalue(),
        )
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["principle"], "causality")
        self.assertEqual(audit[0]["anchor"], "batch owner")
        self.assertEqual(audit[0]["relationship"], "讓單一欄位直接擁有責任。")
        self.assertEqual(audit[0]["returned_via"], "PostToolBatch")
        self.assertTrue(turn_state["nudge_pending_validation"])


if __name__ == "__main__":
    unittest.main()
