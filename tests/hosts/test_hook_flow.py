"""Host hooks deliver at most one advisory intervention per task."""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import NudgeOutcome
from masters_nudge.runtime import RuntimePaths, RuntimeSettings
import hook_entry
import claude_checkpoint
from masters_nudge import claude_adapter


ROOT = Path(__file__).resolve().parents[2]


class FakeCore:
    def __init__(self, data_dir: Path, outcome: NudgeOutcome):
        self.settings = RuntimeSettings(
            "openai", "test", RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log")
        )
        self.outcome = outcome
        self.calls = []
        self.errors = []

    def nudge_once(self, snapshot, **kwargs):
        self.calls.append((snapshot, kwargs))
        return self.outcome

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
    def test_mutation_uses_workspace_snapshot_and_returns_advice(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "app.py").write_text("parallel_owner = True\n", encoding="utf-8")
            core = FakeCore(
                root,
                NudgeOutcome(
                    "intervene",
                    "新增第二個 owner",
                    "責任可能分歧",
                    "沿用既有 owner",
                    ("app.py:parallel_owner",),
                ),
            )
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            output = adapter.process(mutation_payload(raw))

        self.assertIsNotNone(output)
        self.assertEqual(len(core.calls), 1)
        self.assertIn("[task-start workspace]", core.calls[0][0])
        self.assertIn("parallel_owner = True", core.calls[0][0])
        self.assertNotIn("actual_input", core.calls[0][0])
        self.assertEqual(core.calls[0][1]["workspace_root"], raw)
        self.assertIn("Actor 負責驗證與實作", output["hookSpecificOutput"]["additionalContext"])

    def test_pass_is_silent(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "app.py").write_text("value = 1\n", encoding="utf-8")
            core = FakeCore(root, NudgeOutcome("pass"))
            adapter = CodexAdapter(core)
            adapter.process(prompt_payload(raw))
            output = adapter.process(mutation_payload(raw))
        self.assertIsNone(output)
        self.assertEqual(len(core.calls), 1)

    def test_successful_wire_delivery_prevents_further_interventions_this_turn(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "app.py").write_text("value = 1\n", encoding="utf-8")
            core = FakeCore(
                root,
                NudgeOutcome("intervene", "choice", "cost", "direction", ("app.py:value",)),
            )
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
    def test_claude_uses_the_same_workspace_snapshot_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "app.py").write_text("parallel_owner = True\n", encoding="utf-8")
            settings = RuntimeSettings(
                "anthropic", "test", RuntimePaths(ROOT, root, root, root / "error.log")
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
                    return_value=NudgeOutcome(
                        "intervene", "choice", "cost", "direction", ("app.py:value",)
                    ),
                ) as provider,
            ):
                prepared = claude_checkpoint.prepare_hook(payload)

        self.assertIsNotNone(prepared)
        snapshot, workspace = provider.call_args.args
        self.assertIn("[task-start workspace]", snapshot)
        self.assertEqual(workspace, raw)
        self.assertEqual(prepared.direction, "direction")


if __name__ == "__main__":
    unittest.main()
