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
    evidence_classes: tuple[str, ...] = ()
    workspace_revision_signature: str = ""


def observe_tool_batch(
    data_dir: Path,
    events: list[ToolCompleted],
    *,
    contract_signature: str = "",
) -> ToolEvidence:
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")
    workspace = checkpoints.workspace_state(session)
    records: list[dict[str, str]] = []
    for event in events:
        category = checkpoints.evidence_category(event)
        if not category:
            continue
        records.append(
            {
                "category": category,
                "content": checkpoints.render_evidence_record(event),
            }
        )
    state = storage.load_turn_state(data_dir, session)
    for record in records:
        state = storage.record_evidence(
            data_dir,
            session,
            category=record["category"],
            content=record["content"],
        )
    state = storage.record_workspace_state(
        data_dir,
        session,
        workspace.snapshot,
        workspace.revision_signature,
    )
    evidence_classes = tuple(
        category
        for category in ("verification", "failure", "measurement")
        if any(record["category"] == category for record in records)
    )
    if not evidence_classes:
        return ToolEvidence(state, False)
    state, eligible = storage.review_admitted(
        data_dir,
        session,
        workspace_revision_signature=str(
            state.get("workspace_revision_signature") or ""
        ),
        contract_signature=contract_signature,
        evidence_classes=evidence_classes,
    )
    return ToolEvidence(
        state,
        eligible,
        evidence_classes,
        str(state.get("workspace_revision_signature") or ""),
    )
