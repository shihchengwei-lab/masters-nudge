"""Host-namespaced local state and reaction storage."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import source_context

from .contracts import SessionRef, safe_identifier


EVIDENCE_RECORD_MAX_CHARS = 3000
EVIDENCE_RECORDS_MAX = 24
EVIDENCE_CATEGORY_LIMITS = {
    "change": 6,
    "verification": 6,
    "failure": 8,
}
PROGRESS_EVENT_LIMIT = 12
ATOMIC_REPLACE_ATTEMPTS = 5
DELIVERY_CLAIM_STALE_SEC = 120
REVIEW_ATTEMPT_STALE_SEC = 300
SESSION_WRITE_LOCK_STALE_SEC = 30
SESSION_WRITE_LOCK_WAIT_SEC = 5
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


def _claim_path(
    data_dir: Path, session: SessionRef, namespace: str, key: str
) -> Path:
    digest = hashlib.sha256(str(key).encode("utf-8")).hexdigest()[:32]
    return (
        Path(data_dir)
        / f"{session_stem(session)}.{safe_identifier(namespace)}-claims"
        / digest
    )


def _claim_once(
    data_dir: Path,
    session: SessionRef,
    namespace: str,
    key: str,
    *,
    stale_sec: int = DELIVERY_CLAIM_STALE_SEC,
) -> str:
    """Atomically reserve one session-scoped side effect across hook processes."""
    if not key:
        return ""
    path = _claim_path(data_dir, session, namespace, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()}-{time.perf_counter_ns()}"
    for _attempt in range(2):
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(token + "\n")
            return token
        except FileExistsError:
            try:
                stale = time.time() - path.stat().st_mtime > stale_sec
            except OSError:
                return ""
            if not stale:
                return ""
            try:
                path.unlink()
            except OSError:
                return ""
        except OSError:
            return ""
    return ""


def _release_claim(
    data_dir: Path,
    session: SessionRef,
    namespace: str,
    key: str,
    token: str,
) -> None:
    if not key or not token:
        return
    path = _claim_path(data_dir, session, namespace, key)
    try:
        if path.read_text(encoding="utf-8").strip() != token:
            return
        path.unlink(missing_ok=True)
        try:
            path.parent.rmdir()
        except OSError:
            pass
    except OSError:
        pass


def claim_delivery(data_dir: Path, session: SessionRef, timestamp: str) -> str:
    return _claim_once(data_dir, session, "delivery", timestamp)


def release_delivery_claim(
    data_dir: Path, session: SessionRef, timestamp: str, token: str
) -> None:
    _release_claim(data_dir, session, "delivery", timestamp, token)


@contextmanager
def _session_write_lock(data_dir: Path, session: SessionRef) -> Iterator[None]:
    """Serialize short read-modify-write updates to one session's state."""
    key = "delivery-state"
    deadline = time.monotonic() + SESSION_WRITE_LOCK_WAIT_SEC
    token = ""
    while not token:
        token = _claim_once(
            data_dir,
            session,
            "state-write",
            key,
            stale_sec=SESSION_WRITE_LOCK_STALE_SEC,
        )
        if token:
            break
        if time.monotonic() >= deadline:
            raise TimeoutError("timed out acquiring session delivery-state lock")
        time.sleep(0.01)
    try:
        yield
    finally:
        _release_claim(data_dir, session, "state-write", key, token)


def _review_attempt_path(
    data_dir: Path,
    session: SessionRef,
    kind: str,
    fingerprint: str,
) -> Path:
    identity = json.dumps(
        {
            "turn_id": session.turn_id,
            "kind": str(kind or "review"),
            "source_fingerprint": str(fingerprint or ""),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return Path(data_dir) / f"{session_stem(session)}.review-attempts" / f"{digest}.json"


def claim_review_attempt(
    data_dir: Path,
    session: SessionRef,
    kind: str,
    fingerprint: str,
) -> str:
    """Claim one Provider call for a canonical session/turn/kind/source identity."""
    path = _review_attempt_path(data_dir, session, kind, fingerprint)
    path.parent.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()}-{time.perf_counter_ns()}"
    payload = {
        "schema_version": 1,
        "token": token,
        "host": session.host,
        "session_id": session.session_id,
        "turn_id": session.turn_id,
        "kind": str(kind or "review"),
        "source_fingerprint": str(fingerprint or ""),
        "status": "pending",
        "started_at": time.time(),
        "started_at_iso": datetime.now().isoformat(),
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")
        return token
    except FileExistsError:
        existing = _read_json(path, {})
        try:
            started_at = float(existing.get("started_at") or 0.0)
        except (TypeError, ValueError):
            started_at = 0.0
        if (
            existing.get("status") == "pending"
            and started_at
            and time.time() - started_at > REVIEW_ATTEMPT_STALE_SEC
        ):
            existing["status"] = "abandoned"
            existing["completed_at"] = datetime.now().isoformat()
            _atomic_write(path, existing)
        return ""
    except OSError:
        return ""


def finish_review_attempt(
    data_dir: Path,
    session: SessionRef,
    kind: str,
    fingerprint: str,
    token: str,
    status: str,
) -> None:
    if status not in {"finding", "no_finding", "error"}:
        raise ValueError(f"invalid review attempt status: {status}")
    path = _review_attempt_path(data_dir, session, kind, fingerprint)
    current = _read_json(path, {})
    if current.get("token") != token or current.get("status") != "pending":
        return
    current["status"] = status
    current["completed_at"] = datetime.now().isoformat()
    _atomic_write(path, current)


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
            "schema_version": 4,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "task_anchor": "",
            "task_sources": {},
            "evidence_seq": 0,
            "evidence_records": [],
        },
    )


def _new_progress_state(session: SessionRef) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "host": session.host,
        "session_id": session.session_id,
        "turn_id": session.turn_id,
        "event_seq": 0,
        "last_strategy_event_seq": 0,
        "midturn_review_attempts": 0,
        "recent": [],
    }


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
    task_sources = source_context.load_referenced_task_sources(
        prompt,
        session.repo_root or session.cwd,
    )
    _atomic_write(
        state_path(data_dir, session, "turn"),
        {
            "schema_version": 4,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "cwd": session.cwd,
            "repo_root": session.repo_root,
            "task_anchor": source_context.head_tail(
                prompt, source_context.TASK_ANCHOR_MAX_CHARS
            ),
            "task_sources": task_sources,
            "evidence_seq": 0,
            "evidence_records": [],
            "transcript_offset": transcript_offset,
        },
    )
    _atomic_write(
        state_path(data_dir, session, "progress"),
        _new_progress_state(session),
    )


def record_turn_evidence(
    data_dir: Path,
    session: SessionRef,
    *,
    record: str = "",
    category: str = "",
    scope: str = "",
    task_source: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Persist only decision-relevant evidence, separated by evidentiary role."""
    state = load_turn_state(data_dir, session)
    task_sources = state.get("task_sources")
    task_sources = dict(task_sources) if isinstance(task_sources, dict) else {}
    if task_source:
        source_name, source_content = task_source
        if source_name and source_name not in task_sources and source_content:
            task_sources[source_name] = source_context.head_tail(
                source_content, source_context.TASK_SOURCE_MAX_CHARS
            )

    evidence_categories = {"change", "verification", "failure"}
    if category not in evidence_categories:
        category = ""
    evidence_seq = int(state.get("evidence_seq") or 0)
    records = state.get("evidence_records")
    records = list(records) if isinstance(records, list) else []
    if category and record:
        evidence_seq += 1
        records.append(
            {
                "seq": evidence_seq,
                "category": category,
                "scope": source_context.head_tail(scope, 160),
                "content": source_context.head_tail(
                    record, EVIDENCE_RECORD_MAX_CHARS
                ),
            }
        )
        retained: list[dict[str, Any]] = []
        for evidence_category, limit in EVIDENCE_CATEGORY_LIMITS.items():
            category_records = [
                item
                for item in records
                if isinstance(item, dict)
                and item.get("category") == evidence_category
            ]
            retained.extend(category_records[-limit:])
        records = sorted(
            retained,
            key=lambda item: int(item.get("seq") or 0),
        )[-EVIDENCE_RECORDS_MAX:]
    state.update(
        {
            "schema_version": 4,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id or str(state.get("turn_id") or ""),
            "cwd": session.cwd or str(state.get("cwd") or ""),
            "repo_root": session.repo_root or str(state.get("repo_root") or ""),
            "task_sources": task_sources,
            "evidence_seq": evidence_seq,
            "evidence_records": records,
        }
    )
    state.pop("change_evidence", None)
    state.pop("verification_evidence", None)
    state.pop("failure_history", None)
    _atomic_write(state_path(data_dir, session, "turn"), state)
    return state


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
) -> dict[str, Any]:
    if not reaction.strip():
        return {}
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
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
        **route_metadata,
        "reaction": reaction,
        "source_event_seq": int(source_event_seq or 0),
        "source_fingerprint": str(source_fingerprint or ""),
        "generated_at": datetime.now().isoformat(),
        "delivery_status": "" if kind == "review_status" else "queued",
        "delivered_at": "",
        "delivered_via": "",
    }
    with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def append_provider_output(
    data_dir: Path,
    session: SessionRef,
    *,
    stage: str,
    provider: str,
    model: str,
    result: dict[str, Any],
    route_metadata: dict[str, str],
    source_fingerprint: str = "",
) -> dict[str, Any]:
    """Preserve one provider-stage result for local prompt diagnostics."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    deviations = result.get("contract_deviations")
    entry: dict[str, Any] = {
        "schema_version": 1,
        "ts": _reaction_timestamp(),
        "host": session.host,
        "session_id": session.session_id,
        "turn_id": session.turn_id,
        "workspace": _normalized_workspace(session.repo_root or session.cwd),
        "kind": "provider_output",
        "provider_stage": str(stage or ""),
        "provider": provider,
        "model": model,
        **route_metadata,
        "status": str(result.get("status") or "error"),
        "error_kind": str(result.get("error_kind") or ""),
        "contract_deviations": [
            str(value) for value in deviations if str(value).strip()
        ] if isinstance(deviations, (list, tuple)) else [],
        "raw_output": str(result.get("raw_output") or ""),
        "source_fingerprint": str(source_fingerprint or ""),
        "generated_at": datetime.now().isoformat(),
    }
    with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _normalized_workspace(value: str) -> str:
    try:
        return os.path.normcase(str(Path(value).expanduser().resolve())) if value else ""
    except OSError:
        return os.path.normcase(str(Path(value).expanduser().absolute())) if value else ""


def read_audit_entries(data_dir: Path, session: SessionRef) -> list[dict[str, Any]]:
    """Return every valid event from the append-only session audit log."""
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


def read_reaction_entries(data_dir: Path, session: SessionRef) -> list[dict[str, Any]]:
    """Return only agent-visible reactions, excluding delivery audit events."""
    return [
        entry
        for entry in read_audit_entries(data_dir, session)
        if entry.get("kind", "review")
        in {"review", "review_status"}
    ]


def load_delivery_state(data_dir: Path, session: SessionRef) -> dict[str, Any]:
    state = _read_json(
        state_path(data_dir, session, "delivery"),
        {"receipts": {}},
    )
    receipts = state.get("receipts")
    return {
        "receipts": receipts if isinstance(receipts, dict) else {},
    }


def read_recent_injected_findings(
    data_dir: Path,
    session: SessionRef,
    *,
    limit: int = 3,
) -> tuple[str, ...]:
    """Return findings for the latest successfully injected reviews."""
    if limit <= 0:
        return ()
    findings_by_ts = {
        str(entry.get("ts") or ""): str(entry.get("reaction") or "").strip()
        for entry in read_reaction_entries(data_dir, session)
        if entry.get("kind", "review") == "review"
    }
    injected: list[tuple[str, int, str]] = []
    receipts = load_delivery_state(data_dir, session)["receipts"]
    for order, (reaction_ts, receipt) in enumerate(receipts.items()):
        if not isinstance(receipt, dict) or receipt.get("status") != "injected":
            continue
        finding = findings_by_ts.get(str(reaction_ts), "")
        if not finding:
            continue
        injected.append(
            (
                str(
                    receipt.get("injected_at")
                    or receipt.get("delivered_at")
                    or ""
                ),
                order,
                finding,
            )
        )
    injected.sort(key=lambda item: (item[0], item[1]))
    return tuple(finding for _injected_at, _order, finding in injected[-limit:])


def latest_intervention_state(
    data_dir: Path, session: SessionRef
) -> tuple[str, int]:
    """Return the newest finding's delivery state and response boundary."""
    entries = [
        entry
        for entry in read_reaction_entries(data_dir, session)
        if entry.get("kind", "review") == "review"
        and (
            not session.turn_id
            or str(entry.get("turn_id") or "") == session.turn_id
        )
    ]
    if not entries:
        return "", 0
    latest = entries[-1]
    reaction_ts = str(latest.get("ts") or "")
    receipt = load_delivery_state(data_dir, session)["receipts"].get(reaction_ts)
    if not isinstance(receipt, dict):
        return "queued", int(latest.get("source_event_seq") or 0)
    status = str(receipt.get("status") or "")
    if status != "injected":
        return status, int(receipt.get("event_seq") or 0)
    response = receipt.get("response_observation")
    response_seq = (
        int(response.get("event_seq") or 0) if isinstance(response, dict) else 0
    )
    return status, response_seq or int(receipt.get("event_seq") or 0)


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
    with _session_write_lock(data_dir, session):
        state = load_delivery_state(data_dir, session)
        now = datetime.now().isoformat()
        previous = state["receipts"].get(timestamp)
        previous = previous if isinstance(previous, dict) else {}
        receipt = {
            **previous,
            "turn_id": session.turn_id,
            "status": status,
            "event_seq": int(event_seq or 0),
            "delivered_at": now,
            "delivered_via": delivered_via,
        }
        if status == "emitted":
            receipt["emitted_at"] = now
        elif status == "injected":
            receipt["injected_at"] = now
        state["schema_version"] = 3
        state["receipts"][timestamp] = receipt
        _atomic_write(state_path(data_dir, session, "delivery"), state)
        with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
            for reaction_ts, value in [(timestamp, receipt)]:
                entry = {
                    "schema_version": 3,
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


def mark_emitted(
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
        status="emitted",
        event_seq=event_seq,
        delivered_via=delivered_via,
    )


def observe_injected_response(
    data_dir: Path,
    session: SessionRef,
    *,
    event_seq: int = 0,
    observation_kind: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    """Confirm delivery only when a later host event exposes the model's response."""
    normalized_observation = {
        str(key): (
            source_context.head_tail(value, 1000)
            if isinstance(value, str)
            else value
        )
        for key, value in observation.items()
        if isinstance(value, (str, int, float, bool)) or value is None
    }
    with _session_write_lock(data_dir, session):
        state = load_delivery_state(data_dir, session)
        eligible: list[tuple[str, dict[str, Any]]] = []
        for reaction_ts, receipt in state["receipts"].items():
            if not isinstance(receipt, dict) or receipt.get("status") not in {
                "emitted",
                "injected",
            }:
                continue
            if session.turn_id and str(receipt.get("turn_id") or "") != session.turn_id:
                continue
            if isinstance(receipt.get("response_observation"), dict):
                continue
            delivery_seq = int(receipt.get("event_seq") or 0)
            if event_seq and delivery_seq and event_seq < delivery_seq:
                continue
            eligible.append((str(reaction_ts), receipt))
        if not eligible:
            return {}

        reaction_ts, receipt = eligible[-1]
        observed_at = datetime.now().isoformat()
        response = {
            "event_seq": int(event_seq or receipt.get("event_seq") or 0),
            "observed_at": observed_at,
            "kind": str(observation_kind or "host-event"),
            "observation": normalized_observation,
        }
        receipt["status"] = "injected"
        receipt["injected_at"] = observed_at
        receipt["delivered_at"] = observed_at
        receipt["response_observation"] = response
        state["receipts"][reaction_ts] = receipt
        _atomic_write(state_path(data_dir, session, "delivery"), state)

        delivery_entry = {
            "schema_version": 3,
            "ts": observed_at,
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "workspace": _normalized_workspace(session.repo_root or session.cwd),
            "kind": "delivery_receipt",
            "reaction_ts": reaction_ts,
            "delivery_status": "injected",
            "delivery_event_seq": response["event_seq"],
            "delivered_at": observed_at,
            "delivered_via": str(receipt.get("delivered_via") or "host-event"),
        }
        response_entry = {
            "schema_version": 2,
            "ts": response["observed_at"],
            "host": session.host,
            "session_id": session.session_id,
            "turn_id": session.turn_id,
            "workspace": _normalized_workspace(session.repo_root or session.cwd),
            "kind": "response_observation",
            "reaction_ts": reaction_ts,
            "observation_event_seq": response["event_seq"],
            "observation_kind": response["kind"],
            "observation": normalized_observation,
        }
        with reaction_log_path(data_dir, session).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(delivery_entry, ensure_ascii=False) + "\n")
            handle.write(json.dumps(response_entry, ensure_ascii=False) + "\n")
        return response


def load_progress_state(data_dir: Path, session: SessionRef) -> dict[str, Any]:
    return _read_json(
        state_path(data_dir, session, "progress"),
        _new_progress_state(session),
    )


def record_tool_progress(
    data_dir: Path,
    session: SessionRef,
    *,
    failed: bool,
    goal_transition: str = "",
    evidence_category: str = "",
    failure_family: str = "",
    event_fingerprint: str = "",
) -> dict[str, Any]:
    path = state_path(data_dir, session, "progress")
    state = load_progress_state(data_dir, session)
    event_seq = int(state.get("event_seq") or 0) + 1
    recent = state.get("recent") if isinstance(state.get("recent"), list) else []
    recent.append(
        {
            "event_seq": event_seq,
            "failed": bool(failed),
            "goal_transition": goal_transition,
            "evidence_category": evidence_category,
            "failure_family": failure_family,
            "event_fingerprint": event_fingerprint,
        }
    )
    state.update(
        {
            "schema_version": 1,
            "event_seq": event_seq,
            "recent": recent[-PROGRESS_EVENT_LIMIT:],
        }
    )
    _atomic_write(path, state)
    return state


def mark_strategy_reviewed(
    data_dir: Path,
    session: SessionRef,
    *,
    event_seq: int,
    midturn: bool = False,
) -> None:
    path = state_path(data_dir, session, "progress")
    state = _read_json(path, {})
    state["last_strategy_event_seq"] = int(event_seq or 0)
    if midturn:
        state["midturn_review_attempts"] = (
            int(state.get("midturn_review_attempts") or 0) + 1
        )
    _atomic_write(path, state)
