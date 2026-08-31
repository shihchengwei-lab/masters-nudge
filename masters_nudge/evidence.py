"""Collect bounded observable evidence from one native tool batch."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

from . import checkpoints, storage
from .contracts import ToolCompleted


@dataclass(frozen=True)
class ToolEvidence:
    turn_state: dict[str, Any]
    eligible: bool
    fingerprint: str


def _batch_fingerprint(events: list[ToolCompleted]) -> str:
    values = [checkpoints.tool_event_fingerprint(event) for event in events]
    if len(values) == 1:
        return values[0]
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()[:24]


def observe_tool_batch(data_dir: Path, events: list[ToolCompleted]) -> ToolEvidence:
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")
    fingerprint = _batch_fingerprint(events)
    if not storage.record_event(data_dir, session, fingerprint):
        return ToolEvidence(storage.load_turn_state(data_dir, session), False, fingerprint)
    state = storage.load_turn_state(data_dir, session)
    eligible = False
    for event in events:
        category = checkpoints.evidence_category(event)
        if not category:
            continue
        eligible = True
        state = storage.record_evidence(
            data_dir,
            session,
            category=category,
            content=checkpoints.render_evidence_record(event),
        )
    return ToolEvidence(state, eligible, fingerprint)
