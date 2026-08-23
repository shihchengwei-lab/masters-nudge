"""Delivery selection must not confuse audit events with Nudge reactions."""

import tempfile
import unittest
from pathlib import Path

from masters_nudge import storage
from masters_nudge.contracts import SessionRef


class StorageDeliveryTests(unittest.TestCase):
    def test_response_observation_does_not_hide_a_pending_reaction(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            session = SessionRef("codex_cli", "delivery-selection")
            delivered = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="先驗證目前的失敗假設。",
                route_metadata={"effective_lens": "beck"},
                source_event_seq=1,
            )
            storage.mark_delivered(
                data_dir,
                session,
                delivered["ts"],
                event_seq=2,
                delivered_via="test",
            )
            pending = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="哪個邊界條件尚未被測試？",
                route_metadata={"effective_lens": "beck"},
                source_event_seq=3,
            )
            storage.observe_injected_response(
                data_dir,
                session,
                event_seq=4,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )

            selected = storage.latest_pending(data_dir, session, current_event_seq=4)

        self.assertIsNotNone(selected)
        self.assertEqual(selected["ts"], pending["ts"])
        self.assertEqual(selected["kind"], "review")

    def test_reaction_reader_excludes_audit_events_but_audit_reader_keeps_them(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            session = SessionRef("codex_cli", "reader-separation")
            reaction = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="哪個證據會推翻目前方向？",
                route_metadata={"effective_lens": "beck"},
            )
            storage.mark_delivered(data_dir, session, reaction["ts"])
            storage.observe_injected_response(
                data_dir,
                session,
                event_seq=1,
                observation_kind="tool",
                observation={"tool": "apply_patch"},
            )

            reactions = storage.read_reaction_entries(data_dir, session)
            audit = storage.read_audit_entries(data_dir, session)

        self.assertEqual([entry["kind"] for entry in reactions], ["review"])
        self.assertEqual(
            [entry["kind"] for entry in audit],
            ["review", "delivery_receipt", "response_observation"],
        )


if __name__ == "__main__":
    unittest.main()
