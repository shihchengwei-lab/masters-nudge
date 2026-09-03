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


EVIDENCE_RECORD_MAX_CHARS = 3000
EVIDENCE_PER_CATEGORY = 3
ACTOR_SOURCE_RECORD_MAX_CHARS = 80_000
ACTOR_SOURCE_TOTAL_MAX_CHARS = 256_000
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
        "task_sources": {},
        "workspace_snapshot": "",
        "change_generation": 0,
        "candidate_review_used": False,
        "failure_review_used": False,
        "previous_findings": [],
        "evidence_seq": 0,
        "evidence_records": [],
        "actor_source_seq": 0,
        "actor_source_records": [],
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
            "task_sources": source_context.load_referenced_task_sources(
                prompt, session.repo_root or session.cwd
            ),
        }
    )
    _atomic_write(state_path(data_dir, session, "turn"), state)


def record_evidence(
    data_dir: Path,
    session: SessionRef,
    *,
    category: str,
    content: str,
) -> dict[str, Any]:
    state = load_turn_state(data_dir, session)
    if category not in {"change", "verification", "failure", "measurement"}:
        return state
    rendered = source_context.head_tail(content, EVIDENCE_RECORD_MAX_CHARS)
    if not rendered:
        return state
    sequence = int(state.get("evidence_seq") or 0) + 1
    records = [
        record
        for record in state.get("evidence_records", [])
        if isinstance(record, dict)
    ]
    records.append({"seq": sequence, "category": category, "content": rendered})
    retained: list[dict[str, Any]] = []
    for name in ("change", "verification", "failure", "measurement"):
        retained.extend(
            [record for record in records if record.get("category") == name][
                -EVIDENCE_PER_CATEGORY:
            ]
        )
    retained.sort(key=lambda record: int(record.get("seq") or 0))
    state.update({"evidence_seq": sequence, "evidence_records": retained})
    if category == "change":
        state["change_generation"] = int(state.get("change_generation") or 0) + 1
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return state


def record_actor_source(
    data_dir: Path,
    session: SessionRef,
    *,
    content: str,
) -> dict[str, Any]:
    """Retain bounded source text already returned to the actor."""
    state = load_turn_state(data_dir, session)
    rendered = source_context.head_tail(content, ACTOR_SOURCE_RECORD_MAX_CHARS)
    if not rendered:
        return state
    sequence = int(state.get("actor_source_seq") or 0) + 1
    records = [
        record
        for record in state.get("actor_source_records", [])
        if isinstance(record, dict) and str(record.get("content") or "").strip()
    ]
    records.append({"seq": sequence, "content": rendered})
    retained: list[dict[str, Any]] = []
    used = 0
    for record in reversed(records):
        cost = len(str(record.get("content") or ""))
        if retained and used + cost > ACTOR_SOURCE_TOTAL_MAX_CHARS:
            break
        retained.append(record)
        used += cost
    state["actor_source_seq"] = sequence
    state["actor_source_records"] = list(reversed(retained))
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return state


def record_workspace_snapshot(
    data_dir: Path,
    session: SessionRef,
    snapshot: str,
) -> dict[str, Any]:
    state = load_turn_state(data_dir, session)
    state["workspace_snapshot"] = source_context.head_tail(
        snapshot, source_context.CURRENT_WORKSPACE_MAX_CHARS
    )
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return state


def claim_review_opportunity(
    data_dir: Path,
    session: SessionRef,
    *,
    has_failure: bool,
) -> tuple[dict[str, Any], bool]:
    """Claim the turn's candidate or failure review opportunity."""
    state = load_turn_state(data_dir, session)
    if int(state.get("change_generation") or 0) <= 0:
        return state, False
    key = "failure_review_used" if has_failure else "candidate_review_used"
    if bool(state.get(key)):
        return state, False
    state[key] = True
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return state, True


def append_host_returned_nudge(
    data_dir: Path,
    session: SessionRef,
    *,
    lens: str,
    finding: str,
    returned_via: str,
) -> dict[str, Any]:
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "host": session.host,
        "session_id": session.session_id,
        "workspace": str(session.repo_root or session.cwd or ""),
        "lens": str(lens or ""),
        "finding": str(finding or "").strip(),
        "returned_via": str(returned_via or ""),
    }
    path = audit_path(data_dir, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    state = load_turn_state(data_dir, session)
    findings = [
        str(value).strip()
        for value in state.get("previous_findings", [])
        if str(value).strip()
    ]
    findings.append(entry["finding"])
    retained: list[str] = []
    used = 0
    for value in reversed(findings):
        cost = len(value) + 2
        if retained and used + cost > source_context.PREVIOUS_FINDINGS_MAX_CHARS:
            break
        retained.append(
            source_context.head_tail(value, source_context.PREVIOUS_FINDINGS_MAX_CHARS)
        )
        used += cost
    state["previous_findings"] = list(reversed(retained))
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return entry


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
            if isinstance(entry, dict) and entry.get("finding"):
                entries.append(entry)
    entries.sort(key=lambda entry: str(entry.get("time") or ""), reverse=True)
    return entries[:limit]
