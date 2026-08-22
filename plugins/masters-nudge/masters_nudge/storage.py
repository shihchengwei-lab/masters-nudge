"""Host-namespaced local state and reaction storage."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import source_context

from .contracts import SessionRef, safe_identifier


TURN_JOURNAL_MAX_CHARS = 8000
TOOL_RECORD_MAX_CHARS = 3000
PROGRESS_EVENT_LIMIT = 12
PENDING_MAX_EVENT_AGE = 6
ATOMIC_REPLACE_ATTEMPTS = 5
STRATEGY_RUN_STALE_SEC = 300
MAX_ERROR_LOG_BYTES = 256 * 1024


def append_error(error_log: Path, component: str, message: str) -> None:
    """Append one bounded runtime error record; hook callers remain fail-open."""
    try:
        error_log = Path(error_log)
        error_log.parent.mkdir(parents=True, exist_ok=True)
        if error_log.exists():
            size = error_log.stat().st_size
            if size > MAX_ERROR_LOG_BYTES:
                keep = size // 2
                with error_log.open("rb") as handle:
                    handle.seek(size - keep)
                    handle.readline()
                    tail = handle.read()
                with error_log.open("wb") as handle:
                    handle.write(tail)
        with error_log.open("a", encoding="utf-8") as handle:
            handle.write(
                f"[{datetime.now().isoformat()}] {component}: {message}\n"
            )
    except Exception:
        pass


def session_stem(session: SessionRef) -> str:
    return f"{safe_identifier(session.host)}--{safe_identifier(session.session_id)}"


def reaction_log_path(data_dir: Path, session: SessionRef) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.log"


def state_path(data_dir: Path, session: SessionRef, suffix: str) -> Path:
    return Path(data_dir) / f"{session_stem(session)}.{suffix}.json"


def _reaction_timestamp() -> str:
    """Return a sortable identifier even when the Windows wall clock is coarse."""
    return (
        f"{datetime.now().isoformat()}-"
        f"{time.perf_counter_ns():020d}-{os.getpid():06d}"
    )


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
        for attempt in range(ATOMIC_REPLACE_ATTEMPTS):
            try:
                os.replace(temp_path, path)
                break
            except PermissionError:
                if attempt + 1 >= ATOMIC_REPLACE_ATTEMPTS:
                    raise
                time.sleep(0.02 * (attempt + 1))
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
    source_event_seq: int = 0,
    source_fingerprint: str = "",
    finding_scope: str = "candidate",
) -> dict[str, Any]:
    if not reaction.strip():
        return {}
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    normalized_scope = (
        finding_scope
        if finding_scope in {"local", "candidate", "trajectory"}
        else "local"
    )
    entry: dict[str, Any] = {
        "schema_version": 2,
        "ts": _reaction_timestamp(),
        "host": session.host,
        "session_id": session.session_id,
        "turn_id": session.turn_id,
        "workspace": _normalized_workspace(session.repo_root or session.cwd),
        "kind": kind,
        "reason": reason,
        "provider": provider,
        "model": model,
        "persona": route_metadata.get("effective_lens", "general"),
        **route_metadata,
        "reaction": reaction,
        "source_event_seq": int(source_event_seq or 0),
        "source_fingerprint": str(source_fingerprint or ""),
        "finding_scope": normalized_scope,
        "generated_at": datetime.now().isoformat(),
        "delivery_status": "" if kind == "review_status" else "queued",
        "delivered_at": "",
        "delivered_via": "",
    }
    with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _normalized_workspace(value: str) -> str:
    try:
        return os.path.normcase(str(Path(value).expanduser().resolve())) if value else ""
    except OSError:
        return os.path.normcase(str(Path(value).expanduser().absolute())) if value else ""


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
                if isinstance(value, dict) and value.get("kind") != "delivery_receipt":
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


def load_delivery_state(data_dir: Path, session: SessionRef) -> dict[str, Any]:
    state = _read_json(
        state_path(data_dir, session, "delivery"),
        {"last_ts": "", "receipts": {}},
    )
    receipts = state.get("receipts")
    return {
        "last_ts": str(state.get("last_ts") or ""),
        "receipts": receipts if isinstance(receipts, dict) else {},
    }


def read_recent_injected_personas(
    data_dir: Path,
    session: SessionRef,
    *,
    limit: int = 2,
) -> tuple[str, ...]:
    """Return personas for the latest successfully injected reviews."""
    if limit <= 0:
        return ()
    personas_by_ts = {
        str(entry.get("ts") or ""): str(entry.get("persona") or "").strip()
        for entry in read_reaction_entries(data_dir, session)
        if entry.get("kind", "review") == "review"
    }
    injected: list[tuple[str, int, str]] = []
    receipts = load_delivery_state(data_dir, session)["receipts"]
    for order, (reaction_ts, receipt) in enumerate(receipts.items()):
        if not isinstance(receipt, dict) or receipt.get("status") != "injected":
            continue
        persona = personas_by_ts.get(str(reaction_ts), "")
        if not persona:
            continue
        injected.append((str(receipt.get("delivered_at") or ""), order, persona))
    injected.sort(key=lambda item: (item[0], item[1]))
    return tuple(persona for _delivered_at, _order, persona in injected[-limit:])


def latest_pending(
    data_dir: Path,
    session: SessionRef,
    *,
    current_event_seq: int = 0,
    current_source_fingerprint: str = "",
) -> dict[str, Any] | None:
    delivery = load_delivery_state(data_dir, session)
    last_ts = delivery["last_ts"]
    pending = [
        entry
        for entry in read_reaction_entries(data_dir, session)
        if entry.get("kind", "review") not in {"review_status", "delivery_receipt"}
        if str(entry.get("ts") or "") > last_ts
    ]
    if not pending:
        return None
    candidate = pending[-1]
    candidate_source = str(candidate.get("source_fingerprint") or "")
    if candidate_source and current_source_fingerprint:
        if candidate_source != current_source_fingerprint:
            if candidate.get("finding_scope") == "trajectory":
                return candidate
            mark_delivery(
                data_dir,
                session,
                str(candidate.get("ts") or ""),
                status="superseded",
                event_seq=current_event_seq,
                delivered_via="source-state-changed",
            )
            return None
        return candidate
    source_seq = int(candidate.get("source_event_seq") or 0)
    if current_event_seq and source_seq and current_event_seq - source_seq > PENDING_MAX_EVENT_AGE:
        mark_delivery(
            data_dir,
            session,
            str(candidate.get("ts") or ""),
            status="expired",
            event_seq=current_event_seq,
            delivered_via="",
        )
        return None
    return candidate


def mark_delivery(
    data_dir: Path,
    session: SessionRef,
    timestamp: str,
    *,
    status: str,
    event_seq: int = 0,
    delivered_via: str = "",
) -> None:
    if not timestamp:
        return
    state = load_delivery_state(data_dir, session)
    now = datetime.now().isoformat()
    receipt = {
        "status": status,
        "event_seq": int(event_seq or 0),
        "delivered_at": now,
        "delivered_via": delivered_via,
    }
    superseded: list[tuple[str, dict[str, Any]]] = []
    if status in {"injected", "expired", "superseded"}:
        for entry in read_reaction_entries(data_dir, session):
            entry_ts = str(entry.get("ts") or "")
            if not entry_ts or not (state["last_ts"] < entry_ts < timestamp):
                continue
            if entry_ts in state["receipts"]:
                continue
            older_receipt = {
                "status": "superseded",
                "event_seq": int(event_seq or 0),
                "delivered_at": now,
                "delivered_via": "newer-nudge-selected",
            }
            state["receipts"][entry_ts] = older_receipt
            superseded.append((entry_ts, older_receipt))
    state["schema_version"] = 2
    if status in {"injected", "expired", "superseded"}:
        state["last_ts"] = timestamp
    state["receipts"][timestamp] = receipt
    _atomic_write(state_path(data_dir, session, "delivery"), state)
    with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
        for reaction_ts, value in [*superseded, (timestamp, receipt)]:
            entry = {
                "schema_version": 2,
                "ts": value["delivered_at"],
                "host": session.host,
                "session_id": session.session_id,
                "turn_id": session.turn_id,
                "workspace": _normalized_workspace(session.repo_root or session.cwd),
                "kind": "delivery_receipt",
                "reaction_ts": reaction_ts,
                "delivery_status": value["status"],
                "delivery_event_seq": value["event_seq"],
                "delivered_at": value["delivered_at"],
                "delivered_via": value["delivered_via"],
            }
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def mark_delivered(
    data_dir: Path,
    session: SessionRef,
    timestamp: str,
    *,
    event_seq: int = 0,
    delivered_via: str = "",
) -> None:
    mark_delivery(
        data_dir,
        session,
        timestamp,
        status="injected",
        event_seq=event_seq,
        delivered_via=delivered_via,
    )


def record_tool_progress(
    data_dir: Path,
    session: SessionRef,
    *,
    tool_name: str,
    command_family: str,
    failed: bool,
    mutating: bool,
    changed_lines: int | None = None,
    goal_transition: str = "",
    goal_objective: str = "",
) -> dict[str, Any]:
    path = state_path(data_dir, session, "progress")
    state = _read_json(
        path,
        {
            "schema_version": 1,
            "event_seq": 0,
            "last_strategy_event_seq": 0,
            "changed_lines_at_strategy": 0,
            "recent": [],
            "goal_objective": "",
        },
    )
    event_seq = int(state.get("event_seq") or 0) + 1
    recent = state.get("recent") if isinstance(state.get("recent"), list) else []
    meaningful = bool(mutating or command_family or goal_transition)
    recent.append(
        {
            "event_seq": event_seq,
            "tool": tool_name,
            "command_family": command_family,
            "failed": bool(failed),
            "mutating": bool(mutating),
            "meaningful": meaningful,
            "changed_lines": changed_lines,
            "goal_transition": goal_transition,
        }
    )
    state.update(
        {
            "schema_version": 1,
            "event_seq": event_seq,
            "recent": recent[-PROGRESS_EVENT_LIMIT:],
        }
    )
    if goal_objective:
        state["goal_objective"] = source_context.head_tail(goal_objective, 1000)
    _atomic_write(path, state)
    return state


def mark_strategy_reviewed(
    data_dir: Path,
    session: SessionRef,
    *,
    event_seq: int,
    changed_lines: int | None,
) -> None:
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    state["last_strategy_event_seq"] = int(event_seq or 0)
    if changed_lines is not None:
        state["changed_lines_at_strategy"] = int(changed_lines)
    _atomic_write(path, state)


def mark_shader_research_reviewed(
    data_dir: Path,
    session: SessionRef,
    *,
    fingerprint: str,
    projection_state: dict[str, Any],
) -> None:
    """Cache only a rebuildable source fingerprint and its compact projection."""
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    state["shader_research_fingerprint"] = str(fingerprint or "")
    state["shader_research_state"] = projection_state
    _atomic_write(path, state)


def shader_research_gap_is_unchanged(
    data_dir: Path,
    session: SessionRef,
    *,
    gap_key: str,
    evidence_fingerprint: str,
) -> bool:
    if not gap_key or not evidence_fingerprint:
        return False
    state = _read_json(state_path(data_dir, session, "progress"), {})
    gaps = state.get("shader_research_gaps")
    if not isinstance(gaps, dict):
        return False
    entry = gaps.get(gap_key)
    return bool(
        isinstance(entry, dict)
        and str(entry.get("evidence_fingerprint") or "") == evidence_fingerprint
    )


def mark_shader_research_gap_reviewed(
    data_dir: Path,
    session: SessionRef,
    *,
    gap_key: str,
    evidence_fingerprint: str,
    source_fingerprint: str,
) -> None:
    if not gap_key or not evidence_fingerprint:
        return
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    gaps = state.get("shader_research_gaps")
    if not isinstance(gaps, dict):
        gaps = {}
    gaps[str(gap_key)] = {
        "evidence_fingerprint": str(evidence_fingerprint),
        "source_fingerprint": str(source_fingerprint or ""),
        "reviewed_at": datetime.now().isoformat(),
    }
    if len(gaps) > 32:
        ordered = sorted(
            gaps.items(), key=lambda item: str(item[1].get("reviewed_at") or "")
        )
        gaps = dict(ordered[-32:])
    state["shader_research_gaps"] = gaps
    _atomic_write(path, state)


def mark_shader_research_gap_suppressed(
    data_dir: Path,
    session: SessionRef,
    *,
    gap_key: str,
    evidence_fingerprint: str,
    source_fingerprint: str,
) -> None:
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    raw = state.get("shader_research_suppressions")
    suppressions = raw if isinstance(raw, list) else []
    suppressions.append({
        "gap_key": str(gap_key or ""),
        "evidence_fingerprint": str(evidence_fingerprint or ""),
        "source_fingerprint": str(source_fingerprint or ""),
        "reason": "unchanged-evidence-gap",
        "suppressed_at": datetime.now().isoformat(),
    })
    state["shader_research_suppressions"] = suppressions[-24:]
    _atomic_write(path, state)


def _strategy_run_path(data_dir: Path, session: SessionRef) -> Path:
    return state_path(data_dir, session, "strategy-run")


def claim_strategy_run(
    data_dir: Path, session: SessionRef, fingerprint: str
) -> bool:
    """Allow at most one detached strategy provider call per session."""
    path = _strategy_run_path(data_dir, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = _read_json(path, {})
        started_at = float(existing.get("started_at") or 0.0)
    except (TypeError, ValueError):
        started_at = 0.0
    if started_at and time.time() - started_at > STRATEGY_RUN_STALE_SEC:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return False
    payload = {
        "schema_version": 1,
        "fingerprint": str(fingerprint or ""),
        "started_at": time.time(),
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")
        return True
    except FileExistsError:
        return False
    except OSError:
        return False


def release_strategy_run(
    data_dir: Path, session: SessionRef, fingerprint: str = ""
) -> None:
    path = _strategy_run_path(data_dir, session)
    if fingerprint:
        current = _read_json(path, {})
        if str(current.get("fingerprint") or "") != str(fingerprint):
            return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


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
