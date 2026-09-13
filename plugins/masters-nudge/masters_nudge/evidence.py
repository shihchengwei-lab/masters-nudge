"""Collect bounded observable evidence from one native tool batch."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

from . import checkpoints, storage
from .contracts import ToolCompleted


ACTOR_RESULT_CATEGORIES = frozenset({"verification", "failure", "measurement"})


@dataclass(frozen=True)
class ToolEvidence:
    turn_state: dict[str, Any]
    eligible: bool
    fingerprint: str
    batch_records: tuple[dict[str, Any], ...] = ()


def _batch_fingerprint(events: list[ToolCompleted]) -> str:
    values = [checkpoints.tool_event_fingerprint(event) for event in events]
    if len(values) == 1:
        return values[0]
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()[:24]


def _renumber(records: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {**record, "seq": index}
        for index, record in enumerate(records, start=1)
    )


def observe_tool_batch(data_dir: Path, events: list[ToolCompleted]) -> ToolEvidence:
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")
    fingerprint = _batch_fingerprint(events)
    event_status = storage.record_event(data_dir, session, fingerprint)
    if event_status == "duplicate":
        return ToolEvidence(
            storage.load_turn_state(data_dir, session), False, fingerprint, ()
        )
    state = storage.load_turn_state(data_dir, session)
    batch_records: list[dict[str, Any]] = []
    has_change = False
    has_actor_result = False
    last_mutating = max(
        (index for index, event in enumerate(events) if event.mutating),
        default=-1,
    )
    for index, event in enumerate(events):
        engineering_category = checkpoints.evidence_category(event)
        has_change = has_change or engineering_category == "change"
        has_actor_result = (
            has_actor_result or engineering_category in ACTOR_RESULT_CATEGORIES
        )
        category = engineering_category or "observation"
        content = checkpoints.render_evidence_record(
            event,
            include_current_diff=index == last_mutating,
        )
        record = {"seq": index + 1, "category": category, "content": content}
        batch_records.append(record)
    if state.get("nudge_pending_validation"):
        latest_change = next(
            (
                record
                for record in reversed(batch_records)
                if record["category"] == "change"
            ),
            None,
        )
        if latest_change is not None:
            state = storage.set_pending_change(data_dir, session, latest_change)
        pending_change = state.get("pending_change")
        if has_actor_result and isinstance(pending_change, dict):
            resolved_records = (
                [pending_change]
                + [
                    record
                    for record in batch_records
                    if record["category"] in ACTOR_RESULT_CATEGORIES
                ]
            )
            state = storage.set_nudge_pending_validation(data_dir, session, False)
            renumbered = _renumber(resolved_records)
            return ToolEvidence(state, True, fingerprint, renumbered)
        return ToolEvidence(state, False, fingerprint, tuple(batch_records))
    eligible = has_change
    return ToolEvidence(state, eligible, fingerprint, _renumber(batch_records))
