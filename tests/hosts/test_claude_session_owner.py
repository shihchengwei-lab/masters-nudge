import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import claude_checkpoint
import claude_prompt
import claude_stop
import masters_nudge
from masters_nudge import claude_adapter, contracts
from masters_nudge.contracts import ReviewOutcome, SessionRef
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


class TestClaudeSessionOwner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        root = Path(self.tmpdir.name)
        self.settings = RuntimeSettings(
            "anthropic",
            "test-model",
            60,
            15,
            RuntimePaths(Path(__file__).parent, root, root / "error.log"),
        )
        self.runtime_patch = mock.patch.object(
            claude_adapter, "RUNTIME", self.settings
        )
        self.runtime_patch.start()

    def tearDown(self):
        self.runtime_patch.stop()
        self.tmpdir.cleanup()

    def test_adapter_maps_hook_identity_in_one_place(self):
        hook = {
            "session_id": "session-1",
            "turn_id": "turn-2",
            "cwd": "/workspace/project",
        }
        with mock.patch.object(
            claude_adapter, "find_git_root", return_value="/workspace/project"
        ) as find_root:
            session = claude_adapter.session_from_hook(hook)

        self.assertEqual(
            session,
            SessionRef(
                "claude_code",
                "session-1",
                turn_id="turn-2",
                cwd="/workspace/project",
                repo_root="/workspace/project",
            ),
        )
        find_root.assert_called_once_with("/workspace/project")

    def test_entrypoints_do_not_own_session_mapping(self):
        for module in (claude_prompt, claude_checkpoint, claude_stop):
            source = inspect.getsource(module)
            self.assertNotIn("SessionRef(", source, module.__name__)
            self.assertNotIn("find_git_root(", source, module.__name__)

    def test_checkpoint_reuses_normalized_event_session(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/test_path.py"},
            "error": "1 failed",
        }
        session = SessionRef("claude_code", "session-1")
        outcome = ReviewOutcome(
            status="finding",
            finding="先確認路徑前提。",
            reaction_ts="reaction-1",
        )
        with (
            mock.patch.object(
                claude_adapter, "session_from_hook", return_value=session
            ) as session_from_hook,
            mock.patch.object(
                claude_checkpoint.ReviewCore, "review_once", return_value=outcome
            ) as review,
        ):
            self.assertIsNone(claude_checkpoint.prepare_hook(hook))
            prepared = claude_checkpoint.prepare_hook({**hook, "error": "2 failed"})

        self.assertIs(prepared.session, session)
        self.assertIs(review.call_args.args[0].session, session)
        self.assertEqual(session_from_hook.call_count, 2)
        self.assertEqual(session_from_hook.call_args_list[0].args[0], hook)

    def test_stop_source_context_accepts_the_callers_session(self):
        hook = {"session_id": "session-1", "transcript_path": ""}
        session = SessionRef("claude_code", "session-1", cwd="/workspace")
        with (
            mock.patch.object(claude_adapter, "session_from_hook") as session_from_hook,
            mock.patch.object(
                claude_adapter.storage,
                "load_turn_state",
                return_value={"task_anchor": "task", "transcript_offset": 0},
            ) as load_state,
        ):
            claude_adapter.build_stop_source_context(hook, session=session)

        session_from_hook.assert_not_called()
        self.assertIs(load_state.call_args.args[1], session)

    def test_stop_fallback_never_reads_before_current_turn_offset(self):
        transcript = Path(self.tmpdir.name) / "session.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {"content": "OLD TURN SECRET"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        offset = transcript.stat().st_size
        hook = {"session_id": "session-1", "transcript_path": str(transcript)}
        session = SessionRef("claude_code", "session-1")
        with (
            mock.patch.object(
                claude_adapter.storage,
                "load_turn_state",
                return_value={"task_anchor": "current task", "transcript_offset": offset},
            ),
            mock.patch.object(
                claude_adapter, "read_latest_assistant_text"
            ) as current_turn_fallback,
        ):
            source = claude_adapter.build_stop_source_context(hook, session=session)

        current_turn_fallback.assert_called_once_with(str(transcript), offset)
        self.assertNotIn("OLD TURN SECRET", source)
        self.assertIn("current task", source)

    def test_internal_session_consumers_require_the_owned_session(self):
        checkpoint_session = inspect.signature(
            claude_checkpoint.review_checkpoint
        ).parameters["session"]
        self.assertNotIn(
            "hook", inspect.signature(claude_checkpoint.review_checkpoint).parameters
        )
        stop_session = inspect.signature(
            claude_adapter.build_stop_source_context
        ).parameters["session"]

        self.assertIs(checkpoint_session.default, inspect.Parameter.empty)
        self.assertIs(stop_session.default, inspect.Parameter.empty)

    def test_package_root_does_not_reexport_internal_contracts(self):
        self.assertFalse(hasattr(masters_nudge, "__all__"))
        for name in (
            "NormalizedHookEvent",
            "PromptSubmitted",
            "ReviewOutcome",
            "ReviewRequest",
            "SessionRef",
            "ToolCompleted",
            "TurnStopped",
        ):
            self.assertFalse(hasattr(masters_nudge, name), name)

    def test_unused_normalized_hook_event_alias_is_removed(self):
        self.assertFalse(hasattr(contracts, "NormalizedHookEvent"))


if __name__ == "__main__":
    unittest.main()
