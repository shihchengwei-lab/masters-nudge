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
    workspace_revision_signature: str = ""
    checkpoint_signature: str = ""


def _checkpoint_signature(
    *,
    workspace_revision_signature: str,
    contract_signature: str,
    actor_source_records: Any,
    records: list[dict[str, str]],
) -> str:
    if not workspace_revision_signature or not contract_signature or not records:
        return ""
    encoded = json.dumps(
        {
            "workspace_revision_signature": workspace_revision_signature,
            "contract_signature": contract_signature,
            "actor_source": sorted(
                {
                    str(record.get("content") or "")
                    for record in actor_source_records
                    if isinstance(record, dict) and record.get("content")
                }
            )
            if isinstance(actor_source_records, list)
            else [],
            "records": records,
        },
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
    has_review_evidence = any(
        record["category"] in {"verification", "failure", "measurement"}
        for record in records
    )
    if not has_review_evidence:
        return ToolEvidence(state, False)
    workspace_revision_signature = str(
        state.get("workspace_revision_signature") or ""
    )
    checkpoint_signature = _checkpoint_signature(
        workspace_revision_signature=workspace_revision_signature,
        contract_signature=contract_signature,
        actor_source_records=state.get("actor_source_records") or [],
        records=records,
    )
    state, eligible = storage.review_admitted(
        data_dir,
        session,
        checkpoint_signature=checkpoint_signature,
    )
    return ToolEvidence(
        state,
        eligible,
        workspace_revision_signature,
        checkpoint_signature,
    )
