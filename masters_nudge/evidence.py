"""Collect bounded observable evidence from one native tool batch."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import checkpoints, storage
from .contracts import ToolCompleted


@dataclass(frozen=True)
class ToolEvidence:
    turn_state: dict[str, Any]
    eligible: bool
    checkpoint_signature: str = ""
    reused_generator_no_finding: bool = False


def _checkpoint_signature(
    workspace_snapshot: str, records: list[dict[str, str]]
) -> str:
    if not records:
        return ""
    encoded = json.dumps(
        {"workspace_snapshot": workspace_snapshot, "records": records},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    state = storage.record_workspace_snapshot(
        data_dir, session, checkpoints.working_diff(session)
    )
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
    eligible = any(record["category"] != "change" for record in records)
    checkpoint_signature = _checkpoint_signature(
        str(state.get("workspace_snapshot") or ""), records
    )
    if eligible:
        state, reused = storage.reuse_completed_generator_no_finding(
            data_dir,
            session,
            checkpoint_signature=checkpoint_signature,
            contract_signature=contract_signature,
        )
        if reused:
            return ToolEvidence(
                state,
                False,
                checkpoint_signature,
                reused_generator_no_finding=True,
            )
    for record in records:
        state = storage.record_evidence(
            data_dir,
            session,
            category=record["category"],
            content=record["content"],
        )
    return ToolEvidence(state, eligible, checkpoint_signature)
