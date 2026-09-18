import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from masters_nudge.contracts import SessionRef, ToolFault
from masters_nudge.storage import Journal


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = SessionRef("s", "host-turn", str(self.root))

    def test_same_round_judgments_follow_one_causal_chain(self):
        journal = Journal(self.root)
        journal.start_round(self.session, "first")
        first, _ = journal.begin(self.session)

        entered = threading.Event()
        finished = threading.Event()
        result = {}

        def begin_second():
            entered.set()
            try:
                result["value"] = Journal(self.root).begin(self.session)
            except Exception as exc:
                result["error"] = exc
            finally:
                finished.set()

        worker = threading.Thread(target=begin_second)
        worker.start()
        self.assertTrue(entered.wait(1))
        self.assertFalse(finished.wait(0.1), "second judgment must wait for the first fact")
        self.assertTrue(journal.finish(self.session, first, "silence", {"raw_output": "first"}))
        self.assertTrue(finished.wait(2))
        worker.join()
        self.assertNotIn("error", result)
        second, _ = result["value"]
        self.assertNotEqual(first, second)
        self.assertTrue(journal.finish(self.session, second, "silence", {"raw_output": "second"}))

        with journal.connect() as db:
            kinds = [row[0] for row in db.execute("SELECT kind FROM journal_events ORDER BY seq")]
        self.assertEqual(kinds, [
            "round_started", "judgment_started", "judgment_finished",
            "judgment_started", "judgment_finished",
        ])

    def test_new_message_can_proceed_while_old_result_becomes_historical(self):
        journal = Journal(self.root)
        journal.start_round(self.session, "first")
        first, _ = journal.begin(self.session)
        journal.start_round(self.session, "latest")
        second, task = Journal(self.root).begin(self.session)
        self.assertNotEqual(first, second)
        self.assertEqual(task["request"], "latest")
        self.assertFalse(journal.finish(self.session, first, "feedback", {"raw_output": "old"}))
        self.assertTrue(journal.finish(self.session, second, "silence", {"raw_output": "new"}))
        # The Provider result remains a result; eligibility for delivery is separate.
        old = next(row for row in journal.recent() if row["id"] == first)
        self.assertEqual(old["outcome"], "feedback")
        self.assertEqual(old["delivered"], 0)
        self.assertFalse(journal.finish(self.session, second, "feedback", {"raw_output": "duplicate"}))

    def test_expired_judgment_becomes_fault_and_does_not_block_later_work(self):
        journal = Journal(self.root)
        journal.start_round(self.session, "first")
        first, _ = journal.begin(self.session)

        with self.assertRaisesRegex(ToolFault, "前一個 Provider 判斷超過本輪時限"):
            Journal(self.root, hook_timeout_sec=0).begin(self.session)

        old = next(row for row in journal.recent() if row["id"] == first)
        self.assertEqual(old["outcome"], "fault")
        second, _ = journal.begin(self.session)
        self.assertNotEqual(first, second)
        self.assertTrue(journal.finish(self.session, second, "silence", {}))

    def test_upgrade_keeps_old_evidence_and_current_quota(self):
        with sqlite3.connect(self.root / "feedback.sqlite3") as db:
            db.executescript("""
                CREATE TABLE rounds(session TEXT PRIMARY KEY,turn TEXT,goal TEXT,request TEXT);
                CREATE TABLE attempts(id TEXT PRIMARY KEY,session TEXT,turn TEXT,started REAL,
                    finished REAL,outcome TEXT,delivered INTEGER NOT NULL DEFAULT 0,
                    detail TEXT NOT NULL DEFAULT '{}');
                INSERT INTO rounds VALUES('s','host-turn','goal','old request');
            """)
            for n in range(2):
                db.execute("INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?)",
                           (str(n), "s", "host-turn", n, n+0.1, "silence", 0, json.dumps({"original": n})))
        db.close()
        journal = Journal(self.root)
        self.assertIsNone(journal.begin(self.session))
        self.assertEqual({row["detail"]["original"] for row in journal.recent()}, {0, 1})
        journal.start_round(self.session, "new request")
        self.assertIsNotNone(journal.begin(self.session))
        self.assertEqual(len(Journal(self.root).recent()), 3)
