"""Host hooks deliver at most one Nudge per task before the next inference."""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import claude_checkpoint
import hook_entry
import source_context
from masters_nudge import claude_adapter, storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import Nudge
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class FakeCore:
    def __init__(self, data_dir: Path, nudge: Nudge | None):
        self.settings = RuntimeSettings(
            "openai",
            "test",
            RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log"),
        )
        self.nudge = nudge
        self.calls = []
        self.errors = []

    def nudge_once(self, observation, **kwargs):
        self.calls.append((observation, kwargs))
        return self.nudge

    def log_error(self, message):
        self.errors.append(message)


def prompt_payload(root: str, session: str = "session") -> dict:
    return {
        "hook_event_name": "UserPromptSubmit",
        "session_id": session,
        "cwd": root,
        "prompt": "Keep one owner",
    }


def mutation_payload(root: str, session: str = "session") -> dict:
    return {
        "hook_event_name": "PostToolBatch",
        "session_id": session,
        "cwd": root,
        "tool_calls": [
            {
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": (
                        "*** Begin Patch\n*** Update File: app.py\n@@\n"
                        "+parallel_owner = True\n*** End Patch"
                    )
                },
                "tool_response": "done",
            }
        ],
    }


class CodexHookFlowTests(unittest.TestCase):
    def test_mutation_sends_task_and_change_then_returns_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(
                Path(raw),
                Nudge(
                    "同一狀態新增了第二個 owner。",
                    ("+parallel_owner = True",),
                ),
            )
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            output = adapter.process(mutation_payload(raw))

        self.assertIsNotNone(output)
        self.assertEqual(len(core.calls), 1)
        observation, kwargs = core.calls[0]
        self.assertIn("[task]\nKeep one owner\n[end task]", observation)
        self.assertIn("[change]\n*** Begin Patch", observation)
        self.assertIn("+parallel_owner = True", observation)
        self.assertNotIn("workspace", observation.lower())
        self.assertEqual(kwargs, {"timeout_sec": 90})
        delivered = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Nudge：同一狀態新增了第二個 owner。", delivered)
        self.assertIn("證據：+parallel_owner = True", delivered)

    def test_null_is_silent(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw), None)
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            output = adapter.process(mutation_payload(raw))
        self.assertIsNone(output)
        self.assertEqual(len(core.calls), 1)

    def test_oversized_observation_fails_open_without_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw), Nudge("message", ("evidence",)))
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            with mock.patch.object(
                source_context,
                "build_observation",
                side_effect=source_context.ObservationTooLargeError("too large"),
            ):
                output = adapter.process(mutation_payload(raw))

        self.assertIsNone(output)
        self.assertEqual(core.calls, [])
        self.assertTrue(any("too large" in message for message in core.errors))

    def test_successful_wire_delivery_prevents_more_nudges_this_turn(self):
        with tempfile.TemporaryDirectory() as raw:
            core = FakeCore(Path(raw), Nudge("message", ("evidence",)))
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            output = adapter.process(mutation_payload(raw))
            stream = io.StringIO()
            hook_entry._emit_output(output, core.settings, stream=stream)
            second = mutation_payload(raw)
            second["tool_calls"][0]["tool_response"] = "done again"
            second_output = adapter.process(second)

        self.assertIsNone(second_output)
        self.assertEqual(len(core.calls), 1)
        self.assertIn("additionalContext", stream.getvalue())


class ClaudeHookFlowTests(unittest.TestCase):
    def test_claude_uses_the_same_task_and_change_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = RuntimeSettings(
                "anthropic",
                "test",
                RuntimePaths(ROOT, root, root, root / "error.log"),
            )
            session = claude_adapter.session_from_hook(
                {"session_id": "claude-session", "cwd": raw}
            )
            storage.start_turn(root, session, "Keep one owner")
            payload = mutation_payload(raw, "claude-session")
            payload["tool_calls"][0]["tool_input"] = {
                "patch": "*** Update File: app.py\n@@\n+parallel_owner = True"
            }
            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    claude_checkpoint,
                    "nudge_checkpoint",
                    return_value=Nudge("message", ("+parallel_owner = True",)),
                ) as provider,
            ):
                prepared = claude_checkpoint.prepare_hook(payload)

        self.assertIsNotNone(prepared)
        observation = provider.call_args.args[0]
        self.assertIn("[task]\nKeep one owner\n[end task]", observation)
        self.assertIn("+parallel_owner = True", observation)
        self.assertNotIn("workspace", observation.lower())
        self.assertEqual(prepared.message, "message")

    def test_claude_oversized_observation_fails_open_before_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = RuntimeSettings(
                "anthropic",
                "test",
                RuntimePaths(ROOT, root, root, root / "error.log"),
            )
            session = claude_adapter.session_from_hook(
                {"session_id": "claude-session", "cwd": raw}
            )
            storage.start_turn(root, session, "Keep one owner")
            payload = mutation_payload(raw, "claude-session")
            with (
                mock.patch.object(claude_adapter, "RUNTIME", settings),
                mock.patch.object(
                    source_context,
                    "build_observation",
                    side_effect=source_context.ObservationTooLargeError("too large"),
                ),
                mock.patch.object(claude_checkpoint, "nudge_checkpoint") as provider,
            ):
                prepared = claude_checkpoint.prepare_hook(payload)

        self.assertIsNone(prepared)
        provider.assert_not_called()


if __name__ == "__main__":
    unittest.main()
