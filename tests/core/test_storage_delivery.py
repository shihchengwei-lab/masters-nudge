"""Delivery selection must not confuse audit events with Nudge reactions."""

import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import storage
from masters_nudge.contracts import SessionRef


class StorageDeliveryTests(unittest.TestCase):
    def test_wire_flush_is_only_emitted_until_a_later_host_event_confirms_injection(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            session = SessionRef("codex_cli", "delivery-confirmation")
            reaction = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="哪個完成條件仍缺少直接證據？",
                route_metadata={"effective_lens": "linus"},
            )

            storage.mark_emitted(
                data_dir,
                session,
                reaction["ts"],
                event_seq=4,
                delivered_via="Stop",
            )
            emitted = storage.load_delivery_state(data_dir, session)["receipts"][
                reaction["ts"]
            ]
            self.assertEqual(emitted["status"], "emitted")
            self.assertEqual(storage.read_recent_injected_findings(data_dir, session), ())

            storage.observe_injected_response(
                data_dir,
                session,
                event_seq=5,
                observation_kind="stop",
                observation={"assistant_claim": "我會再檢查一次。"},
            )
            injected = storage.load_delivery_state(data_dir, session)["receipts"][
                reaction["ts"]
            ]

        self.assertEqual(injected["status"], "injected")
        self.assertEqual(injected["response_observation"]["kind"], "stop")

    def test_concurrent_receipt_updates_preserve_every_reaction(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            session = SessionRef("codex_cli", "concurrent-delivery")
            first = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="第一則。",
                route_metadata={"effective_lens": "beck"},
            )
            second = storage.append_reaction(
                data_dir,
                session,
                provider="anthropic",
                model="opus",
                reaction="第二則。",
                route_metadata={"effective_lens": "fowler"},
            )
            original_load = storage.load_delivery_state

            def slow_load(*args, **kwargs):
                state = original_load(*args, **kwargs)
                time.sleep(0.05)
                return state

            threads = [
                threading.Thread(
                    target=storage.mark_delivery,
                    args=(data_dir, session, entry["ts"]),
                    kwargs={"status": "emitted", "delivered_via": "test"},
                )
                for entry in (first, second)
            ]
            with mock.patch.object(storage, "load_delivery_state", side_effect=slow_load):
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=2)

            self.assertTrue(all(not thread.is_alive() for thread in threads))
            receipts = original_load(data_dir, session)["receipts"]

        self.assertEqual(set(receipts), {first["ts"], second["ts"]})

    def test_response_observation_only_updates_an_emitted_reaction(self):
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
            storage.mark_emitted(
                data_dir,
                session,
                delivered["ts"],
                event_seq=2,
                delivered_via="test",
            )
            queued = storage.append_reaction(
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

            receipts = storage.load_delivery_state(data_dir, session)["receipts"]

        self.assertEqual("injected", receipts[delivered["ts"]]["status"])
        self.assertNotIn(queued["ts"], receipts)

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
            storage.mark_emitted(data_dir, session, reaction["ts"])
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
            [
                "review",
                "delivery_receipt",
                "delivery_receipt",
                "response_observation",
            ],
        )


if __name__ == "__main__":
    unittest.main()
