"""Host-neutral evidence helpers that do not depend on transcript formats."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import source_context

from . import checkpoints, storage
from .contracts import ToolCompleted


@dataclass(frozen=True)
class ToolReviewState:
    turn_state: dict[str, Any]
    checkpoint: dict[str, str] | None
    event_seq: int


def _batch_fingerprint(events: list[ToolCompleted]) -> str:
    fingerprints = [checkpoints.tool_event_fingerprint(event) for event in events]
    if len(fingerprints) == 1:
        return fingerprints[0]
    return hashlib.sha256("\n".join(fingerprints).encode("utf-8")).hexdigest()[:24]


def observe_tool_batch(
    data_dir: Path, events: list[ToolCompleted]
) -> ToolReviewState:
    """Record one native tool batch and open at most one evidence window."""
    if not events:
        raise ValueError("tool batch must contain at least one event")
    session = events[0].session
    if any(event.session != session for event in events[1:]):
        raise ValueError("tool batch events must share one session")

    turn_state = storage.load_turn_state(data_dir, session)
    event_fingerprint = _batch_fingerprint(events)
    prior_progress = storage.load_progress_state(data_dir, session)
    if prior_progress.get("last_event_fingerprint") == event_fingerprint:
        return ToolReviewState(
            turn_state=turn_state,
            checkpoint=None,
            event_seq=int(prior_progress.get("event_seq") or 0),
        )
    categories: list[str] = []
    transitions: list[str] = []
    scopes: list[str] = []
    for event in events:
        category = checkpoints.evidence_category(event)
        task_source = None
        if not category and not (event.failure_known and event.failed):
            task_source = source_context.capture_referenced_task_source(
                str(turn_state.get("task_anchor") or ""),
                event.tool_input,
                event.tool_output,
            )
        scope = checkpoints.evidence_scope(event)
        if category or task_source:
            turn_state = storage.record_turn_evidence(
                data_dir,
                session,
                record=(
                    checkpoints.render_evidence_record(event) if category else ""
                ),
                category=category,
                scope=scope,
                task_source=task_source,
            )
        transition, _objective = checkpoints.goal_transition(event)
        if category:
            categories.append(category)
            scopes.append(scope)
        if transition:
            transitions.append(transition)

    progress = storage.record_tool_progress(
        data_dir,
        session,
        event_fingerprint=event_fingerprint,
    )
    event_seq = int(progress.get("event_seq") or 0)
    if categories or transitions:
        storage.observe_injected_response(
            data_dir,
            session,
            event_seq=event_seq,
            observation_kind="semantic-batch",
            observation={
                "evidence_categories": ", ".join(categories),
                "evidence_scopes": ", ".join(scope for scope in scopes if scope),
                "failed": "failure" in categories,
                "goal_transitions": ", ".join(transitions),
            },
        )

    checkpoint = (
        {
            "reason": "evidence-review",
            "trigger": "evidence-ready",
            "context": f"evidence_categories: {', '.join(categories)}",
            "fingerprint": event_fingerprint,
        }
        if categories
        else None
    )
    intervention_status, _barrier_seq = storage.latest_intervention_state(
        data_dir, session
    )
    if checkpoint and intervention_status in {"queued", "emitted"}:
        checkpoint = None
    return ToolReviewState(
        turn_state=turn_state,
        checkpoint=checkpoint,
        event_seq=event_seq,
    )


def observe_tool_event(data_dir: Path, event: ToolCompleted) -> ToolReviewState:
    """Treat a host's single-tool control point as a one-item batch."""
    return observe_tool_batch(data_dir, [event])
