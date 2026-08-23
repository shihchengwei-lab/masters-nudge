"""Focused tests for the optional Tk observation window."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import buddy_window


class WindowPollingTests(unittest.TestCase):
    def test_poll_logs_each_distinct_failure_once_and_keeps_loop_alive(self):
        window = object.__new__(buddy_window.BuddyWindow)
        window.current_log = None
        window.root = mock.Mock()
        window._find_active_log = mock.Mock(side_effect=OSError("read blocked"))

        with mock.patch.object(buddy_window.storage, "append_error") as append_error:
            buddy_window.BuddyWindow._poll(window)
            buddy_window.BuddyWindow._poll(window)

        append_error.assert_called_once()
        self.assertEqual(append_error.call_args.args[1], "window-poll")
        self.assertIn("read blocked", append_error.call_args.args[2])
        self.assertEqual(window.root.after.call_count, 2)

    def test_read_failure_is_logged_without_advancing_offset(self):
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / "missing.log"
            window = object.__new__(buddy_window.BuddyWindow)
            window.current_log = missing
            window.last_offset = 17

            with mock.patch.object(buddy_window.storage, "append_error") as append_error:
                buddy_window.BuddyWindow._read_new(window)

        append_error.assert_called_once()
        self.assertEqual(append_error.call_args.args[1], "window-read")
        self.assertEqual(window.last_offset, 17)

    def test_removed_window_state_is_not_reintroduced(self):
        source = Path(buddy_window.__file__).read_text(encoding="utf-8")

        self.assertNotIn("idle_source_frames", source)
        self.assertNotIn("review_source_frames", source)
        self.assertNotIn("last_reaction =", source)
        self.assertEqual(source.count("self.stage_selection ="), 1)


if __name__ == "__main__":
    unittest.main()
