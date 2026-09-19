"""Durable terminal facts for rounds, eligible patches and Provider results."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .contracts import FEEDBACK_LIMIT, SILENCE_LIMIT, SessionRef, ToolFault, json_text


class Journal:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "feedback.sqlite3"
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS rounds(
                    session TEXT PRIMARY KEY, turn TEXT NOT NULL, goal TEXT NOT NULL, request TEXT NOT NULL,
                    round_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS attempts(
                    id TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT NOT NULL,
                    started REAL NOT NULL, finished REAL, outcome TEXT, delivered INTEGER NOT NULL DEFAULT 0,
                    detail TEXT NOT NULL DEFAULT '{}', round_id TEXT NOT NULL,
                    batch_id TEXT);
                CREATE TABLE IF NOT EXISTS batches(
                    id TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT NOT NULL,
                    received REAL NOT NULL, payload TEXT NOT NULL, round_id TEXT NOT NULL);
            """)
            db.execute("BEGIN IMMEDIATE")
            for table in ("rounds", "attempts"):
                columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
                if "round_id" not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN round_id TEXT NOT NULL DEFAULT ''")
            attempt_columns = {row["name"] for row in db.execute("PRAGMA table_info(attempts)")}
            if "batch_id" not in attempt_columns:
                db.execute("ALTER TABLE attempts ADD COLUMN batch_id TEXT")
            batch_columns = {row["name"] for row in db.execute("PRAGMA table_info(batches)")}
            if "id" not in batch_columns:
                db.execute("ALTER TABLE batches ADD COLUMN id TEXT")
            if "round_id" not in batch_columns:
                db.execute("ALTER TABLE batches ADD COLUMN round_id TEXT NOT NULL DEFAULT ''")
            db.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS attempts_batch_id "
                "ON attempts(batch_id) WHERE batch_id IS NOT NULL"
            )
            for row in db.execute("SELECT session,turn FROM rounds WHERE round_id=''").fetchall():
                round_id = uuid.uuid4().hex
                db.execute("UPDATE rounds SET round_id=? WHERE session=?", (round_id, row["session"]))
                db.execute("UPDATE attempts SET round_id=? WHERE session=? AND turn=? AND round_id=''",
                           (round_id, row["session"], row["turn"]))
            for row in db.execute("SELECT rowid FROM batches WHERE id IS NULL OR id=''").fetchall():
                db.execute("UPDATE batches SET id=? WHERE rowid=?", (uuid.uuid4().hex, row["rowid"]))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def start_round(self, session: SessionRef, request: str, goal: str = ""):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM rounds WHERE session=?", (session.session_id,)).fetchone()
            original = goal or (old["goal"] if old else request)
            db.execute(
                "INSERT OR REPLACE INTO rounds(session,turn,goal,request,round_id) VALUES(?,?,?,?,?)",
                (session.session_id, session.turn_id, original, request, uuid.uuid4().hex),
            )

    def begin(self, session: SessionRef, payload: object) -> tuple[str, dict] | None:
        """Record one eligible patch; no Provider attempt exists before its terminal result."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM rounds WHERE session=?", (session.session_id,)).fetchone()
            if row is None:
                raise ToolFault("input", "缺少本輪使用者要求事件")
            if row["turn"] != session.turn_id:
                return None
            unresolved = db.execute(
                "SELECT b.id FROM batches b LEFT JOIN attempts a ON a.batch_id=b.id "
                "WHERE b.round_id=? AND a.id IS NULL LIMIT 1",
                (row["round_id"],),
            ).fetchone()
            if unresolved is not None:
                raise ToolFault("interrupted", "前一次 Provider 判斷沒有完成，本輪工具故障")
            counts = {item["outcome"]: item["n"] for item in db.execute(
                "SELECT outcome, COUNT(*) n FROM attempts WHERE round_id=? GROUP BY outcome",
                (row["round_id"],),
            )}
            if counts.get("feedback", 0) >= FEEDBACK_LIMIT or counts.get("silence", 0) >= SILENCE_LIMIT:
                return None
            batch_id = uuid.uuid4().hex
            attempt = uuid.uuid4().hex
            started = time.time()
            db.execute(
                "INSERT INTO batches(id,session,turn,received,payload,round_id) VALUES(?,?,?,?,?,?)",
                (batch_id, session.session_id, session.turn_id, started, json_text(payload), row["round_id"]),
            )
            return attempt, {**dict(row), "batch_id": batch_id, "started": started}

    def finish(
        self, session: SessionRef, attempt: str, task: dict, outcome: str, detail: dict,
    ) -> bool:
        """Atomically add one terminal Provider fact for the batch that caused it."""
        batch_id = task.get("batch_id")
        round_id = task.get("round_id")
        if not isinstance(batch_id, str) or not isinstance(round_id, str):
            return False
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            batch = db.execute(
                "SELECT * FROM batches WHERE id=? AND round_id=?",
                (batch_id, round_id),
            ).fetchone()
            existing = db.execute(
                "SELECT 1 FROM attempts WHERE id=? OR batch_id=? LIMIT 1",
                (attempt, batch_id),
            ).fetchone()
            if batch is None or existing is not None:
                return False
            finished = time.time()
            db.execute(
                "INSERT INTO attempts("
                "id,session,turn,started,finished,outcome,delivered,detail,round_id,batch_id"
                ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    attempt, batch["session"], batch["turn"], task.get("started", batch["received"]),
                    finished, outcome, 0, json_text(detail), round_id, batch_id,
                ),
            )
            current = db.execute(
                "SELECT round_id FROM rounds WHERE session=?",
                (session.session_id,),
            ).fetchone()
            return bool(current and current["round_id"] == round_id)

    def delivered(self, attempt: str):
        with self.connect() as db:
            db.execute("UPDATE attempts SET delivered=1 WHERE id=? AND outcome='feedback'", (attempt,))

    def unresolved(self) -> list[dict]:
        with self.connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT b.* FROM batches b LEFT JOIN attempts a ON a.batch_id=b.id "
                "WHERE b.round_id<>'' AND a.id IS NULL ORDER BY b.received"
            )]

    def recent(self, limit: int = 20) -> list[dict]:
        with self.connect() as db:
            return [dict(row) | {"detail": json.loads(row["detail"])} for row in db.execute(
                "SELECT * FROM attempts ORDER BY started DESC LIMIT ?",
                (max(0, min(limit, 200)),),
            )]


def append_error(path: Path, component: str, message: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json_text({"time": time.time(), "component": component, "message": message}) + "\n")


def recent_nudges(data_dir: Path, *, limit: int = 20) -> list[dict]:
    if not (data_dir / "feedback.sqlite3").exists():
        return []
    return Journal(data_dir).recent(limit)
