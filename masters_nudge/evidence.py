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
    candidate: bool
    has_failure: bool = False
    checkpoint_records: tuple[dict[str, Any], ...] = ()


def observe_tool_batch(
    data_dir: Path,
    events: list[ToolCompleted],
) -> ToolEvidence:
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")
    workspace = checkpoints.workspace_state(session)
    records: list[dict[str, str]] = []
    actor_sources: list[str] = []
    for event in events:
        actor_source = checkpoints.render_actor_source_record(event)
        if actor_source:
            actor_sources.append(actor_source)
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
    for actor_source in actor_sources:
        state = storage.record_actor_source(
            data_dir,
            session,
            content=actor_source,
        )
    checkpoint_records: list[dict[str, Any]] = []
    for record in records:
        state = storage.record_evidence(
            data_dir,
            session,
            category=record["category"],
            content=record["content"],
        )
        checkpoint_records.append(
            {
                "seq": int(state.get("evidence_seq") or 0),
                **record,
            }
        )
    state = storage.record_workspace_snapshot(
        data_dir,
        session,
        workspace.snapshot,
    )
    has_review_evidence = any(
        record["category"] in {"verification", "failure", "measurement"}
        for record in checkpoint_records
    )
    if not has_review_evidence:
        return ToolEvidence(
            state,
            False,
            checkpoint_records=tuple(checkpoint_records),
        )
    return ToolEvidence(
        state,
        True,
        any(record["category"] == "failure" for record in records),
        tuple(checkpoint_records),
    )
