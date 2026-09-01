"""Collect bounded observable evidence from one native tool batch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import checkpoints, storage
from .contracts import ToolCompleted


@dataclass(frozen=True)
class ToolEvidence:
    turn_state: dict[str, Any]
    eligible: bool


def observe_tool_batch(data_dir: Path, events: list[ToolCompleted]) -> ToolEvidence:
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")
    state = storage.record_workspace_snapshot(
        data_dir, session, checkpoints.working_diff(session)
    )
    eligible = False
    for event in events:
        category = checkpoints.evidence_category(event)
        if not category:
            continue
        eligible = eligible or category != "change"
        state = storage.record_evidence(
            data_dir,
            session,
            category=category,
            content=checkpoints.render_evidence_record(event),
        )
    return ToolEvidence(state, eligible)
