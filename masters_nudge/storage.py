"""Minimal cross-hook task state and host-returned Nudge audit."""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import source_context

from .contracts import SessionRef, safe_identifier
from .prompting import delivery_text


MAX_ERROR_LOG_BYTES = 256 * 1024
SETTINGS_FILE = "config.json"


def append_error(error_log: Path, component: str, message: str) -> None:
    """Append one bounded diagnostic line without breaking a host hook."""
    try:
        path = Path(error_log)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > MAX_ERROR_LOG_BYTES:
            with path.open("rb") as handle:
                handle.seek(-(MAX_ERROR_LOG_BYTES // 2), os.SEEK_END)
                handle.readline()
                tail = handle.read()
            path.write_bytes(tail)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"[{datetime.now(timezone.utc).isoformat()}] {component}: {message}\n"
            )
    except Exception:
        pass


def session_stem(session: SessionRef) -> str:
    return f"{safe_identifier(session.host)}--{safe_identifier(session.session_id)}"


def state_path(data_dir: Path, session: SessionRef, suffix: str) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.{suffix}.json"


def audit_path(data_dir: Path, session: SessionRef) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.nudges.jsonl"


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return dict(default)
    return payload if isinstance(payload, dict) else dict(default)


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix=f"{path.stem}-",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(handle.name)
    try:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        for attempt in range(5):
            try:
                os.replace(temp_path, path)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.02 * (attempt + 1))
    finally:
        handle.close()
        temp_path.unlink(missing_ok=True)


def _empty_turn(session: SessionRef) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "host": session.host,
        "session_id": session.session_id,
        "task_anchor": "",
    }


def load_turn_state(data_dir: Path, session: SessionRef) -> dict[str, Any]:
    return _read_json(state_path(data_dir, session, "turn"), _empty_turn(session))


def cleanup_expired_sessions(
    data_dir: Path,
    *,
    max_age_days: int = 30,
    now: float | None = None,
) -> int:
    """Remove stale session data opportunistically; preserve global settings."""
    root = Path(data_dir)
    if not root.exists():
        return 0
    cutoff = (time.time() if now is None else now) - max_age_days * 24 * 60 * 60
    removed = 0
    for path in root.iterdir():
        if not path.is_file() or path.name == SETTINGS_FILE:
            continue
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            continue
    return removed


def start_turn(data_dir: Path, session: SessionRef, prompt: str) -> None:
    cleanup_expired_sessions(data_dir)
    state = _empty_turn(session)
    state.update(
        {
            "task_anchor": source_context.head_tail(
                prompt, source_context.TASK_ANCHOR_MAX_CHARS
            ),
        }
    )
    task_sources = source_context.load_referenced_task_sources(
        prompt,
        session.repo_root or session.cwd,
    )
    if task_sources:
        state["task_sources"] = task_sources
    _atomic_write(state_path(data_dir, session, "turn"), state)
    _atomic_write(
        state_path(data_dir, session, "progress"),
        {
            "schema_version": 1,
            "host": session.host,
            "session_id": session.session_id,
            "last_event_fingerprint": "",
        },
    )


def record_event(data_dir: Path, session: SessionRef, fingerprint: str) -> str:
    """Classify one native batch as first, new, or an exact replay."""
    if not fingerprint:
        return "duplicate"
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    if state.get("last_event_fingerprint") == fingerprint:
        return "duplicate"
    status = "new" if state.get("last_event_fingerprint") else "first"
    state.update(
        {
            "schema_version": 1,
            "host": session.host,
            "session_id": session.session_id,
            "last_event_fingerprint": fingerprint,
        }
    )
    _atomic_write(path, state)
    return status


def append_host_returned_nudge(
    data_dir: Path,
    session: SessionRef,
    *,
    evidence_seq: int,
    principle: str,
    anchor: str,
    relationship: str,
    returned_via: str,
) -> dict[str, Any]:
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "host": session.host,
        "session_id": session.session_id,
        "workspace": str(session.repo_root or session.cwd or ""),
        "evidence_seq": int(evidence_seq),
        "principle": str(principle or "").strip(),
        "anchor": str(anchor or "").strip(),
        "relationship": str(relationship or "").strip(),
        "returned_via": str(returned_via or ""),
    }
    path = audit_path(data_dir, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_recent_returned_nudges(
    data_dir: Path,
    session: SessionRef,
    *,
    limit: int = 3,
) -> tuple[str, ...]:
    """Read Nudge texts successfully returned in this session, oldest first."""
    if limit <= 0:
        return ()
    try:
        lines = audit_path(data_dir, session).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    selected: list[str] = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(entry, dict):
            continue
        relationship = str(entry.get("relationship") or "").strip()
        principle = str(entry.get("principle") or "").strip()
        anchor = str(entry.get("anchor") or "").strip()
        if relationship and principle and anchor:
            text = delivery_text(principle, anchor, relationship)
        else:
            text = relationship or str(entry.get("finding") or "").strip()
        if not text:
            continue
        selected.append(text)
        if len(selected) == limit:
            break
    return tuple(reversed(selected))


def recent_nudges(data_dir: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if limit <= 0:
        return entries
    for path in Path(data_dir).glob("*.nudges.jsonl"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                entry = json.loads(line)
            except (TypeError, ValueError):
                continue
            if isinstance(entry, dict) and (
                entry.get("relationship") or entry.get("finding")
            ):
                entries.append(entry)
    entries.sort(key=lambda entry: str(entry.get("time") or ""), reverse=True)
    return entries[:limit]
