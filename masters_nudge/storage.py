"""Append-only facts for rounds, judgments, quotas and audit evidence."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .contracts import FEEDBACK_LIMIT, SILENCE_LIMIT, SessionRef, ToolFault, json_text
from .runtime import HOOK_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC

FINALIZATION_RESERVE_SEC = 20


class Journal:
    def __init__(self, directory: Path, *, hook_timeout_sec: float = HOOK_TIMEOUT_SEC,
                 provider_timeout_sec: float = PROVIDER_TIMEOUT_SEC, poll_interval: float = 0.05):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "feedback.sqlite3"
        self.hook_timeout_sec = hook_timeout_sec
        self.provider_timeout_sec = provider_timeout_sec
        self.poll_interval = poll_interval
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS rounds(
                    session TEXT PRIMARY KEY, turn TEXT NOT NULL, goal TEXT NOT NULL, request TEXT NOT NULL,
                    round_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS attempts(
                    id TEXT PRIMARY KEY, session TEXT NOT NULL, turn TEXT NOT NULL,
                    started REAL NOT NULL, finished REAL, outcome TEXT, delivered INTEGER NOT NULL DEFAULT 0,
                    detail TEXT NOT NULL DEFAULT '{}', round_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS batches(
                    session TEXT NOT NULL, turn TEXT NOT NULL, received REAL NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS journal_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    session TEXT NOT NULL, round_id TEXT NOT NULL, turn TEXT NOT NULL,
                    happened REAL NOT NULL, kind TEXT NOT NULL, attempt TEXT, payload TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS journal_events_session_seq
                    ON journal_events(session, seq);
                CREATE INDEX IF NOT EXISTS journal_events_attempt_seq
                    ON journal_events(attempt, seq);
            """)
            db.execute("BEGIN IMMEDIATE")
            for table in ("rounds", "attempts"):
                columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
                if "round_id" not in columns:
                    db.execute(f"ALTER TABLE {table} ADD COLUMN round_id TEXT NOT NULL DEFAULT ''")
            for row in db.execute("SELECT session,turn FROM rounds WHERE round_id='' ").fetchall():
                round_id = uuid.uuid4().hex
                db.execute("UPDATE rounds SET round_id=? WHERE session=?", (round_id, row["session"]))
                db.execute("UPDATE attempts SET round_id=? WHERE session=? AND turn=? AND round_id=''",
                           (round_id, row["session"], row["turn"]))
            self._migrate_legacy(db)

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

    @staticmethod
    def _decode(value: str) -> object:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def _payload(cls, value: str) -> dict:
        loaded = cls._decode(value)
        if not isinstance(loaded, dict):
            return {}
        return loaded

    @staticmethod
    def _append(db, *, session: str, round_id: str, turn: str, kind: str,
                happened: float | None = None, attempt: str | None = None, payload: object = None):
        db.execute(
            "INSERT INTO journal_events(session,round_id,turn,happened,kind,attempt,payload) "
            "VALUES(?,?,?,?,?,?,?)",
            (session, round_id, turn, time.time() if happened is None else happened,
             kind, attempt, json_text({} if payload is None else payload)),
        )

    def _migrate_legacy(self, db):
        if db.execute("SELECT 1 FROM journal_events LIMIT 1").fetchone():
            return
        for row in db.execute("SELECT * FROM rounds ORDER BY rowid").fetchall():
            self._append(db, session=row["session"], round_id=row["round_id"], turn=row["turn"],
                         kind="round_started", happened=0,
                         payload={"goal": row["goal"], "request": row["request"]})
        for row in db.execute("SELECT * FROM batches ORDER BY received,rowid").fetchall():
            current = db.execute("SELECT round_id FROM rounds WHERE session=?", (row["session"],)).fetchone()
            self._append(db, session=row["session"], round_id=current["round_id"] if current else "",
                         turn=row["turn"], kind="batch_received", happened=row["received"],
                         payload=self._decode(row["payload"]))
        for row in db.execute("SELECT * FROM attempts ORDER BY started,id").fetchall():
            self._append(db, session=row["session"], round_id=row["round_id"], turn=row["turn"],
                         kind="judgment_started", happened=row["started"], attempt=row["id"])
            if row["outcome"] is not None:
                self._append(db, session=row["session"], round_id=row["round_id"], turn=row["turn"],
                             kind="judgment_finished", happened=row["finished"] or row["started"],
                             attempt=row["id"],
                             payload={"outcome": row["outcome"], "detail": self._payload(row["detail"])})
            if row["delivered"]:
                self._append(db, session=row["session"], round_id=row["round_id"], turn=row["turn"],
                             kind="feedback_delivered", happened=row["finished"] or row["started"],
                             attempt=row["id"])

    def _current_round(self, db, session_id: str) -> dict | None:
        row = db.execute(
            "SELECT * FROM journal_events WHERE session=? AND kind='round_started' ORDER BY seq DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        payload = self._payload(row["payload"])
        return {"session": row["session"], "turn": row["turn"],
                "goal": payload.get("goal", ""), "request": payload.get("request", ""),
                "round_id": row["round_id"]}

    def _round_attempts(self, db, round_id: str) -> list[dict]:
        attempts: dict[str, dict] = {}
        rows = db.execute(
            "SELECT * FROM journal_events WHERE round_id=? AND kind IN "
            "('judgment_started','judgment_finished','feedback_delivered') ORDER BY seq",
            (round_id,),
        )
        for row in rows:
            if row["kind"] == "judgment_started":
                attempts[row["attempt"]] = {
                    "id": row["attempt"], "session": row["session"], "turn": row["turn"],
                    "started": row["happened"], "finished": None, "outcome": None,
                    "delivered": 0, "detail": {}, "round_id": row["round_id"],
                }
            elif row["attempt"] in attempts and row["kind"] == "judgment_finished":
                payload = self._payload(row["payload"])
                attempts[row["attempt"]].update(
                    finished=row["happened"], outcome=payload.get("outcome"),
                    detail=payload.get("detail") if isinstance(payload.get("detail"), dict) else {},
                )
            elif row["attempt"] in attempts and row["kind"] == "feedback_delivered":
                attempts[row["attempt"]]["delivered"] = 1
        return list(attempts.values())

    def start_round(self, session: SessionRef, request: str, goal: str = ""):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = self._current_round(db, session.session_id)
            original = goal or (old["goal"] if old else request)
            round_id = uuid.uuid4().hex
            self._append(db, session=session.session_id, round_id=round_id, turn=session.turn_id,
                         kind="round_started", payload={"goal": original, "request": request})
            db.execute("INSERT OR REPLACE INTO rounds(session,turn,goal,request,round_id) VALUES(?,?,?,?,?)",
                       (session.session_id, session.turn_id, original, request, round_id))

    def record_batch(self, session: SessionRef, payload: object):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = self._current_round(db, session.session_id)
            received = time.time()
            self._append(db, session=session.session_id,
                         round_id=current["round_id"] if current else "", turn=session.turn_id,
                         kind="batch_received", happened=received, payload=payload)
            db.execute("INSERT INTO batches VALUES(?,?,?,?)",
                       (session.session_id, session.turn_id, received, json_text(payload)))

    def _close_expired(self, db, attempt: dict):
        detail = {"fault": {"kind": "timeout", "detail": "前一個 Provider 判斷超過本輪時限"}}
        self._append(db, session=attempt["session"], round_id=attempt["round_id"],
                     turn=attempt["turn"], kind="judgment_finished", attempt=attempt["id"],
                     payload={"outcome": "fault", "detail": detail})
        db.execute("UPDATE attempts SET finished=?,outcome='fault',detail=? WHERE id=? AND outcome IS NULL",
                   (time.time(), json_text(detail), attempt["id"]))

    @staticmethod
    def _raise_attempt_fault(attempt: dict):
        fault = attempt["detail"].get("fault", {})
        raise ToolFault(fault.get("kind", "interrupted"),
                        fault.get("detail", "前一個 Provider 判斷未正常完成"))

    def begin(self, session: SessionRef) -> tuple[str, dict] | None:
        waiting_for = None
        wait_started = time.monotonic()
        while True:
            should_wait = False
            expired = False
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                current = self._current_round(db, session.session_id)
                if current is None:
                    raise ToolFault("input", "缺少本輪使用者要求事件")
                if current["turn"] != session.turn_id:
                    return None
                attempts = self._round_attempts(db, current["round_id"])
                active = next((item for item in attempts if item["outcome"] is None), None)
                if active:
                    waiting_for = active["id"]
                    if time.time() >= active["started"] + self.hook_timeout_sec:
                        self._close_expired(db, active)
                        expired = True
                    else:
                        should_wait = True
                else:
                    if waiting_for:
                        prior = next(item for item in attempts if item["id"] == waiting_for)
                        if prior["outcome"] == "fault":
                            self._raise_attempt_fault(prior)
                    counts = {outcome: sum(item["outcome"] == outcome for item in attempts)
                              for outcome in ("feedback", "silence")}
                    if counts["feedback"] >= FEEDBACK_LIMIT or counts["silence"] >= SILENCE_LIMIT:
                        return None
                    elapsed = time.monotonic() - wait_started
                    remaining = self.hook_timeout_sec - elapsed - FINALIZATION_RESERVE_SEC
                    if remaining <= 0:
                        raise ToolFault("timeout", "等待前一個 Provider 判斷後，本次呼叫已無足夠時間")
                    attempt = uuid.uuid4().hex
                    started = time.time()
                    self._append(db, session=session.session_id, round_id=current["round_id"],
                                 turn=session.turn_id, kind="judgment_started", happened=started,
                                 attempt=attempt)
                    db.execute("INSERT INTO attempts(id,session,turn,started,round_id) VALUES(?,?,?,?,?)",
                               (attempt, session.session_id, session.turn_id, started, current["round_id"]))
                    return attempt, {**current, "provider_timeout_sec": min(self.provider_timeout_sec, remaining)}
            if expired:
                raise ToolFault("timeout", "前一個 Provider 判斷超過本輪時限")
            if should_wait:
                time.sleep(self.poll_interval)

    def finish(self, session: SessionRef, attempt: str, outcome: str, detail: dict) -> bool:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            started = db.execute(
                "SELECT * FROM journal_events WHERE attempt=? AND kind='judgment_started' "
                "ORDER BY seq LIMIT 1", (attempt,),
            ).fetchone()
            terminal = db.execute(
                "SELECT 1 FROM journal_events WHERE attempt=? AND kind='judgment_finished' LIMIT 1",
                (attempt,),
            ).fetchone()
            if started is None or terminal is not None:
                return False
            finished = time.time()
            self._append(db, session=started["session"], round_id=started["round_id"],
                         turn=started["turn"], kind="judgment_finished", happened=finished,
                         attempt=attempt, payload={"outcome": outcome, "detail": detail})
            db.execute("UPDATE attempts SET finished=?,outcome=?,detail=? WHERE id=? AND outcome IS NULL",
                       (finished, outcome, json_text(detail), attempt))
            current = self._current_round(db, session.session_id)
            return bool(current and current["round_id"] == started["round_id"])

    def delivered(self, attempt: str):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            started = db.execute(
                "SELECT * FROM journal_events WHERE attempt=? AND kind='judgment_started' "
                "ORDER BY seq LIMIT 1", (attempt,),
            ).fetchone()
            finished = db.execute(
                "SELECT payload FROM journal_events WHERE attempt=? AND kind='judgment_finished' "
                "ORDER BY seq DESC LIMIT 1", (attempt,),
            ).fetchone()
            already = db.execute(
                "SELECT 1 FROM journal_events WHERE attempt=? AND kind='feedback_delivered' LIMIT 1",
                (attempt,),
            ).fetchone()
            if (started is None or finished is None or already is not None
                    or self._payload(finished["payload"]).get("outcome") != "feedback"):
                return
            self._append(db, session=started["session"], round_id=started["round_id"],
                         turn=started["turn"], kind="feedback_delivered", attempt=attempt)
            db.execute("UPDATE attempts SET delivered=1 WHERE id=?", (attempt,))

    def recent(self, limit: int = 20) -> list[dict]:
        with self.connect() as db:
            starts = db.execute(
                "SELECT DISTINCT round_id FROM journal_events WHERE kind='judgment_started'"
            ).fetchall()
            attempts = []
            for row in starts:
                attempts.extend(self._round_attempts(db, row["round_id"]))
            attempts.sort(key=lambda item: item["started"], reverse=True)
            return attempts[:max(0, min(limit, 200))]


def append_error(path: Path, component: str, message: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json_text({"time": time.time(), "component": component, "message": message}) + "\n")


def recent_nudges(data_dir: Path, *, limit: int = 20) -> list[dict]:
    if not (data_dir / "feedback.sqlite3").exists():
        return []
    return Journal(data_dir).recent(limit)
