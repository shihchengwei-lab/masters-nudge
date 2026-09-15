"""Collect bounded observable evidence from one native tool batch."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import json

from . import storage
from .contracts import ToolCompleted


@dataclass(frozen=True)
class ToolEvidence:
    turn_state: dict[str, Any]
    eligible: bool
    fingerprint: str


def _batch_fingerprint(events: list[ToolCompleted]) -> str:
    raw = json.dumps(
        [
            {"tool": event.tool_name, "input": event.tool_input, "output": event.tool_output}
            for event in events
        ],
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


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
            storage.load_turn_state(data_dir, session), False, fingerprint
        )
    state = storage.load_turn_state(data_dir, session)
    eligible = any(event.mutation is not None for event in events)
    return ToolEvidence(state, eligible, fingerprint)
