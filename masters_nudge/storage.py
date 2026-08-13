"""Host-namespaced local state and reaction storage."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import source_context

from .contracts import SessionRef, safe_identifier


TURN_JOURNAL_MAX_CHARS = 8000
TOOL_RECORD_MAX_CHARS = 3000


def session_stem(session: SessionRef) -> str:
    return f"{safe_identifier(session.host)}--{safe_identifier(session.session_id)}"


def reaction_log_path(data_dir: Path, session: SessionRef) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.log"


def state_path(data_dir: Path, session: SessionRef, suffix: str) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.{suffix}.json"


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
        os.replace(temp_path, path)
    finally:
        try:
            handle.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def load_turn_state(data_dir: Path, session: SessionRef) -> dict[str, Any]:
    return _read_json(
        state_path(data_dir, session, "turn"),
        {
            "schema_version": 1,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "task_anchor": "",
            "tool_evidence": "",
        },
    )


def start_turn(
    data_dir: Path,
    session: SessionRef,
    prompt: str,
    *,
    transcript_path: str = "",
) -> None:
    transcript_offset = 0
    if transcript_path:
        try:
            transcript_offset = Path(transcript_path).stat().st_size
        except OSError:
            transcript_offset = 0
    _atomic_write(
        state_path(data_dir, session, "turn"),
        {
            "schema_version": 1,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "cwd": session.cwd,
            "repo_root": session.repo_root,
            "task_anchor": source_context.head_tail(
                prompt, source_context.TASK_ANCHOR_MAX_CHARS
            ),
            "tool_evidence": "",
            "transcript_offset": transcript_offset,
        },
    )


def append_tool_evidence(
    data_dir: Path,
    session: SessionRef,
    record: str,
) -> str:
    state = load_turn_state(data_dir, session)
    bounded_record = source_context.head_tail(record, TOOL_RECORD_MAX_CHARS)
    existing = str(state.get("tool_evidence") or "")
    combined = "\n\n".join(part for part in (existing, bounded_record) if part)
    state.update(
        {
            "schema_version": 1,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id or str(state.get("turn_id") or ""),
            "cwd": session.cwd or str(state.get("cwd") or ""),
            "repo_root": session.repo_root or str(state.get("repo_root") or ""),
            "tool_evidence": source_context.head_tail(
                combined, TURN_JOURNAL_MAX_CHARS
            ),
        }
    )
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return str(state["tool_evidence"])


def append_reaction(
    data_dir: Path,
    session: SessionRef,
    *,
    provider: str,
    model: str,
    reaction: str,
    route_metadata: dict[str, str],
    kind: str = "review",
    reason: str = "stop",
) -> dict[str, Any]:
    if not reaction.strip():
        return {}
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    entry: dict[str, Any] = {
        "schema_version": 1,
        "ts": datetime.now().isoformat(),
        "host": session.host,
        "session_id": session.session_id,
        "turn_id": session.turn_id,
        "kind": kind,
        "reason": reason,
        "provider": provider,
        "model": model,
        "persona": route_metadata.get("effective_lens", "general"),
        **route_metadata,
        "reaction": reaction,
    }
    with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_reaction_entries(data_dir: Path, session: SessionRef) -> list[dict[str, Any]]:
    path = reaction_log_path(data_dir, session)
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                except (TypeError, ValueError):
                    continue
                if isinstance(value, dict):
                    entries.append(value)
    except OSError:
        return []
    return entries


def read_recent_reactions(
    data_dir: Path,
    session: SessionRef,
    max_count: int = 3,
    max_chars: int = 200,
) -> list[str]:
    reactions = [
        str(entry.get("reaction") or "").strip()
        for entry in read_reaction_entries(data_dir, session)
        if entry.get("kind", "review") == "review"
    ]
    reactions = [value for value in reactions if value]
    return [value[:max_chars] for value in reactions[-max_count:]]


def read_legacy_reaction_entries(
    legacy_data_dir: Path, session: SessionRef
) -> list[dict[str, Any]]:
    """Read the pre-Phase-C unnamespaced log without ever writing to it."""
    path = Path(legacy_data_dir) / f"{safe_identifier(session.session_id)}.log"
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                value = json.loads(line)
            except (TypeError, ValueError):
                continue
            if isinstance(value, dict):
                entries.append(value)
    except OSError:
        return []
    return entries


def read_recent_reactions_compatible(
    data_dir: Path,
    legacy_data_dir: Path,
    session: SessionRef,
    max_count: int = 3,
    max_chars: int = 200,
) -> list[str]:
    entries = (
        read_legacy_reaction_entries(legacy_data_dir, session)
        if session.host == "claude_code"
        else []
    )
    entries.extend(read_reaction_entries(data_dir, session))
    entries.sort(key=lambda entry: str(entry.get("ts") or ""))
    reactions = [
        str(entry.get("reaction") or "").strip()
        for entry in entries
        if entry.get("kind", "review") == "review"
    ]
    return [value[:max_chars] for value in reactions if value][-max_count:]


def load_delivery_state(data_dir: Path, session: SessionRef) -> dict[str, str]:
    state = _read_json(state_path(data_dir, session, "delivery"), {"last_ts": ""})
    return {"last_ts": str(state.get("last_ts") or "")}


def latest_pending(data_dir: Path, session: SessionRef) -> dict[str, Any] | None:
    last_ts = load_delivery_state(data_dir, session)["last_ts"]
    pending = [
        entry
        for entry in read_reaction_entries(data_dir, session)
        if str(entry.get("ts") or "") > last_ts
    ]
    return pending[-1] if pending else None


def mark_delivered(data_dir: Path, session: SessionRef, timestamp: str) -> None:
    _atomic_write(
        state_path(data_dir, session, "delivery"),
        {"schema_version": 1, "last_ts": str(timestamp or "")},
    )


def _checkpoint_path(data_dir: Path, session: SessionRef, fingerprint: str) -> Path:
    return (
        Path(data_dir)
        / f"{session_stem(session)}.checkpoints"
        / safe_identifier(fingerprint, "checkpoint", 180)
    )


def claim_checkpoint(data_dir: Path, session: SessionRef, fingerprint: str) -> bool:
    path = _checkpoint_path(data_dir, session, fingerprint)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write("pending\n")
        return True
    except FileExistsError:
        return False
    except OSError:
        return False


def release_checkpoint(data_dir: Path, session: SessionRef, fingerprint: str) -> None:
    try:
        _checkpoint_path(data_dir, session, fingerprint).unlink(missing_ok=True)
    except OSError:
        pass


def complete_checkpoint(data_dir: Path, session: SessionRef, fingerprint: str) -> None:
    try:
        _checkpoint_path(data_dir, session, fingerprint).write_text(
            "delivered\n", encoding="utf-8"
        )
    except OSError:
        pass


def _journal_digest(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:24]


def mark_checkpoint_delivery(
    data_dir: Path,
    session: SessionRef,
    *,
    reason: str,
    tool_evidence: str,
) -> None:
    _atomic_write(
        state_path(data_dir, session, "checkpoint-delivery"),
        {
            "schema_version": 1,
            "turn_id": session.turn_id,
            "reason": reason,
            "tool_evidence_fingerprint": _journal_digest(tool_evidence),
        },
    )


def checkpoint_stop_overlap(
    data_dir: Path,
    session: SessionRef,
    *,
    tool_evidence: str,
) -> bool:
    state = _read_json(
        state_path(data_dir, session, "checkpoint-delivery"), {}
    )
    if not state:
        return False
    recorded_turn = str(state.get("turn_id") or "")
    if recorded_turn and session.turn_id and recorded_turn != session.turn_id:
        return False
    return str(state.get("tool_evidence_fingerprint") or "") == _journal_digest(
        tool_evidence
    )


def load_agentcam_mtime(data_dir: Path, session: SessionRef) -> float:
    state = _read_json(state_path(data_dir, session, "agentcam"), {})
    try:
        return float(state.get("last_mtime") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def save_agentcam_mtime(
    data_dir: Path, session: SessionRef, mtime: float
) -> None:
    _atomic_write(
        state_path(data_dir, session, "agentcam"),
        {"schema_version": 1, "last_mtime": float(mtime)},
    )
