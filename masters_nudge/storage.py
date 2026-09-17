"""One durable journal owns round identity, attempts, quotas and evidence."""
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
                    round_id TEXT NOT NULL, pending_events TEXT NOT NULL DEFAULT '');
                CREATE TABLE IF NOT EXISTS attempts(
                    id TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT NOT NULL,
                    started REAL NOT NULL, finished REAL, outcome TEXT, delivered INTEGER NOT NULL DEFAULT 0,
                    detail TEXT NOT NULL DEFAULT '{}', round_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS batches(
                    session TEXT NOT NULL, turn TEXT NOT NULL, received REAL NOT NULL, payload TEXT NOT NULL);
            """)
            # Preserve journals created before user messages owned round identity.
            db.execute("BEGIN IMMEDIATE")
            for table in ("rounds", "attempts"):
                columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
                if "round_id" not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN round_id TEXT NOT NULL DEFAULT ''")
            round_columns = {row["name"] for row in db.execute("PRAGMA table_info(rounds)")}
            if "pending_events" not in round_columns:
                db.execute("ALTER TABLE rounds ADD COLUMN pending_events TEXT NOT NULL DEFAULT ''")
            for row in db.execute("SELECT session,turn FROM rounds WHERE round_id=''").fetchall():
                round_id = uuid.uuid4().hex
                db.execute("UPDATE rounds SET round_id=? WHERE session=?", (round_id, row["session"]))
                db.execute("UPDATE attempts SET round_id=? WHERE session=? AND turn=? AND round_id=''",
                           (round_id, row["session"], row["turn"]))

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
            db.execute("INSERT OR REPLACE INTO rounds(session,turn,goal,request,round_id,pending_events) "
                       "VALUES(?,?,?,?,?,?)",
                       (session.session_id, session.turn_id, original, request, uuid.uuid4().hex, ""))

    def record_batch(self, session: SessionRef, payload: object):
        with self.connect() as db:
            db.execute("INSERT INTO batches VALUES(?,?,?,?)",
                       (session.session_id, session.turn_id, time.time(), json_text(payload)))

    def events_for_judgment(self, session: SessionRef, payload: list[dict],
                            *, has_modification: bool) -> list[dict] | None:
        """Delay the first explicit change until the following tool batch."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM rounds WHERE session=?", (session.session_id,)).fetchone()
            if row is None:
                raise ToolFault("input", "缺少本輪使用者要求事件")
            if row["turn"] != session.turn_id:
                return None
            if row["pending_events"]:
                pending = json.loads(row["pending_events"])
                db.execute("UPDATE rounds SET pending_events='' WHERE session=?", (session.session_id,))
                return [*pending, *payload]
            attempted = db.execute("SELECT 1 FROM attempts WHERE round_id=? LIMIT 1",
                                   (row["round_id"],)).fetchone()
            if attempted:
                return payload if has_modification else None
            if has_modification:
                db.execute("UPDATE rounds SET pending_events=? WHERE session=?",
                           (json_text(payload), session.session_id))
            return None

    def begin(self, session: SessionRef) -> tuple[str, dict] | None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM rounds WHERE session=?", (session.session_id,)).fetchone()
            if row is None:
                raise ToolFault("input", "缺少本輪使用者要求事件")
            if row["turn"] != session.turn_id:
                return None
            counts = {r["outcome"]: r["n"] for r in db.execute(
                "SELECT outcome, COUNT(*) n FROM attempts WHERE round_id=? GROUP BY outcome",
                (row["round_id"],))}
            if counts.get("feedback", 0) >= FEEDBACK_LIMIT or counts.get("silence", 0) >= SILENCE_LIMIT:
                return None
            if counts.get(None, 0):
                raise ToolFault("interrupted", "本輪有尚未完成或中斷的判斷，不能重複呼叫")
            attempt = uuid.uuid4().hex
            db.execute("INSERT INTO attempts(id,session,turn,started,round_id) VALUES(?,?,?,?,?)",
                       (attempt, session.session_id, session.turn_id, time.time(), row["round_id"]))
            return attempt, dict(row)

    def finish(self, session: SessionRef, attempt: str, outcome: str, detail: dict) -> bool:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT 1 FROM rounds r JOIN attempts a ON r.round_id=a.round_id "
                             "WHERE r.session=? AND a.id=?", (session.session_id, attempt)).fetchone()
            current = row is not None
            updated = db.execute("UPDATE attempts SET finished=?,outcome=?,detail=? WHERE id=? AND outcome IS NULL",
                       (time.time(), outcome, json_text(detail), attempt))
            return current and updated.rowcount == 1

    def delivered(self, attempt: str):
        with self.connect() as db:
            db.execute("UPDATE attempts SET delivered=1 WHERE id=? AND outcome='feedback'", (attempt,))

    def recent(self, limit: int = 20) -> list[dict]:
        with self.connect() as db:
            return [dict(row) | {"detail": json.loads(row["detail"])} for row in db.execute(
                "SELECT * FROM attempts ORDER BY started DESC LIMIT ?", (max(0, min(limit, 200)),))]


def append_error(path: Path, component: str, message: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json_text({"time": time.time(), "component": component, "message": message}) + "\n")


def recent_nudges(data_dir: Path, *, limit: int = 20) -> list[dict]:
    if not (data_dir / "feedback.sqlite3").exists():
        return []
    return Journal(data_dir).recent(limit)
