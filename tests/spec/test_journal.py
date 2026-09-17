import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from masters_nudge.contracts import SessionRef, ToolFault
from masters_nudge.storage import Journal


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = SessionRef("s", "host-turn", str(self.root))

    def test_same_round_cannot_have_parallel_judgments_and_new_message_can_proceed(self):
        journal = Journal(self.root)
        journal.start_round(self.session, "first")
        first, _ = journal.begin(self.session)
        with self.assertRaises(ToolFault):
            Journal(self.root).begin(self.session)
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
