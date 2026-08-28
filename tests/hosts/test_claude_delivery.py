import tempfile
import unittest
from pathlib import Path
from unittest import mock

import claude_checkpoint
import claude_stop
from masters_nudge import claude_adapter, storage
from masters_nudge.contracts import ReviewOutcome, SessionRef
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


class TestClaudeCheckpointDeliveryBoundary(unittest.TestCase):
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
            claude_checkpoint.claude_adapter, "RUNTIME", self.settings
        )
        self.runtime_patch.start()
        self.stop_runtime_patch = mock.patch.object(
            claude_stop.claude_adapter, "RUNTIME", self.settings
        )
        self.stop_runtime_patch.start()

    def tearDown(self):
        self.stop_runtime_patch.stop()
        self.runtime_patch.stop()
        self.tmpdir.cleanup()

    def test_checkpoint_entry_does_not_own_routing(self):
        self.assertFalse(hasattr(claude_checkpoint, "lens_router"))

    def test_only_final_claim_fallback_remains_in_shared_claude_adapter(self):
        self.assertFalse(hasattr(claude_stop, "read_latest_assistant_text"))
        self.assertFalse(hasattr(claude_stop, "read_recent_tool_evidence"))
        self.assertTrue(
            callable(claude_checkpoint.claude_adapter.read_latest_assistant_text)
        )
        self.assertFalse(
            hasattr(claude_checkpoint.claude_adapter, "read_recent_tool_evidence")
        )

    def test_reviewer_finding_stays_queued_until_wire_output_flushes(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/test_path.py"},
            "error": "1 failed",
        }
        outcome = ReviewOutcome(
            status="finding",
            finding="先確認路徑前提。",
            reaction_ts="reaction-1",
        )
        with mock.patch.object(
            claude_checkpoint.ReviewCore, "review_once", return_value=outcome
        ):
            self.assertIsNone(claude_checkpoint.prepare_hook(hook))
            prepared = claude_checkpoint.prepare_hook({**hook, "error": "2 failed"})

        self.assertIsNotNone(prepared)
        session = SessionRef("claude_code", "session-1")
        self.assertEqual(storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"], {})

        stream = mock.Mock()
        claude_adapter.emit_json_delivery(
            prepared, delivered_via="claude-checkpoint", stream=stream
        )

        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"]["reaction-1"]
        self.assertEqual(receipt["status"], "emitted")
        stream.flush.assert_called_once_with()

    def test_stop_observes_prior_nudge_without_reviewing_or_emitting(self):
        hook = {
            "session_id": "session-stop",
            "turn_id": "turn-1",
            "cwd": self.tmpdir.name,
            "hook_event_name": "Stop",
            "last_assistant_message": "已完成。",
            "stop_hook_active": False,
        }
        session = SessionRef(
            "claude_code", "session-stop", "turn-1", self.tmpdir.name
        )
        storage.start_turn(
            self.settings.paths.data_dir, session, "完成可靠性修正"
        )
        entry = storage.append_reaction(
            self.settings.paths.data_dir,
            session,
            provider="anthropic",
            model="test-model",
            reaction="讓狀態只歸一個 owner。",
            route_metadata={"effective_lens": "linus"},
        )
        storage.mark_emitted(self.settings.paths.data_dir, session, entry["ts"])
        with mock.patch.object(
            claude_stop, "ReviewCore", create=True
        ) as review_core:
            prepared = claude_stop.prepare_hook(hook)
            active = claude_stop.prepare_hook({**hook, "stop_hook_active": True})

        self.assertIsNone(prepared)
        self.assertIsNone(active)
        review_core.assert_not_called()
        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"][entry["ts"]]
        self.assertEqual(receipt["status"], "injected")
        self.assertEqual(
            receipt["response_observation"]["observation"]["assistant_claim"],
            "已完成。",
        )

    def test_wire_failure_records_failed_and_releases_delivery_claim(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/test_path.py"},
            "error": "1 failed",
        }
        outcome = ReviewOutcome(
            status="finding",
            finding="先確認路徑前提。",
            reaction_ts="reaction-2",
        )
        with mock.patch.object(
            claude_checkpoint.ReviewCore, "review_once", return_value=outcome
        ):
            self.assertIsNone(claude_checkpoint.prepare_hook(hook))
            prepared = claude_checkpoint.prepare_hook({**hook, "error": "2 failed"})

        stream = mock.Mock()
        stream.flush.side_effect = OSError("broken pipe")
        with self.assertRaises(OSError):
            claude_adapter.emit_json_delivery(
                prepared, delivered_via="claude-checkpoint", stream=stream
            )

        session = SessionRef("claude_code", "session-1")
        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"]["reaction-2"]
        self.assertEqual(receipt["status"], "failed")
        retry_claim = storage.claim_delivery(
            self.settings.paths.data_dir, session, prepared.reaction_ts
        )
        self.assertTrue(retry_claim)
        storage.release_delivery_claim(
            self.settings.paths.data_dir,
            session,
            prepared.reaction_ts,
            retry_claim,
        )


if __name__ == "__main__":
    unittest.main()
