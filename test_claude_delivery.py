import tempfile
import unittest
from pathlib import Path
from unittest import mock

import claude_checkpoint
import claude_stop
from masters_nudge import storage
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

    def tearDown(self):
        self.runtime_patch.stop()
        self.tmpdir.cleanup()

    def test_checkpoint_entry_does_not_own_routing(self):
        self.assertFalse(hasattr(claude_checkpoint, "lens_router"))

    def test_transcript_helpers_have_one_shared_claude_owner(self):
        self.assertFalse(hasattr(claude_stop, "read_latest_assistant_text"))
        self.assertFalse(hasattr(claude_stop, "read_recent_tool_evidence"))
        self.assertTrue(
            callable(claude_checkpoint.claude_adapter.read_latest_assistant_text)
        )
        self.assertTrue(
            callable(claude_checkpoint.claude_adapter.read_recent_tool_evidence)
        )

    def test_reviewer_finding_stays_queued_until_wire_output_flushes(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }
        outcome = ReviewOutcome(
            status="finding",
            finding="先確認路徑前提。",
            reaction_ts="reaction-1",
        )
        with mock.patch.object(
            claude_checkpoint.ReviewCore, "review", return_value=outcome
        ):
            prepared = claude_checkpoint.prepare_hook(hook)

        self.assertIsNotNone(prepared)
        session = SessionRef("claude_code", "session-1")
        self.assertEqual(storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"], {})

        stream = mock.Mock()
        claude_checkpoint.emit_prepared(prepared, stream=stream)

        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"]["reaction-1"]
        self.assertEqual(receipt["status"], "injected")
        stream.flush.assert_called_once_with()

    def test_wire_failure_records_failed_and_releases_checkpoint_claim(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }
        outcome = ReviewOutcome(
            status="finding",
            finding="先確認路徑前提。",
            reaction_ts="reaction-2",
        )
        with mock.patch.object(
            claude_checkpoint.ReviewCore, "review", return_value=outcome
        ):
            prepared = claude_checkpoint.prepare_hook(hook)

        stream = mock.Mock()
        stream.flush.side_effect = OSError("broken pipe")
        with self.assertRaises(OSError):
            claude_checkpoint.emit_prepared(prepared, stream=stream)

        session = SessionRef("claude_code", "session-1")
        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"]["reaction-2"]
        self.assertEqual(receipt["status"], "failed")
        self.assertTrue(storage.claim_checkpoint(
            self.settings.paths.data_dir, session, prepared.fingerprint
        ))


if __name__ == "__main__":
    unittest.main()
