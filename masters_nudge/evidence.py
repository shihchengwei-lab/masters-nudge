"""Host-neutral evidence helpers that do not depend on transcript formats."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import source_context

from . import checkpoints, storage
from .contracts import ReviewKind, ToolCompleted


@dataclass(frozen=True)
class ToolReviewState:
    turn_state: dict[str, Any]
    checkpoint: dict[str, str] | None
    review_kind: ReviewKind
    event_seq: int


def observe_tool_event(data_dir: Path, event: ToolCompleted) -> ToolReviewState:
    """Record one host-neutral tool event and select any due review."""
    turn_state = storage.load_turn_state(data_dir, event.session)
    event_fingerprint = checkpoints.tool_event_fingerprint(event)
    prior_progress = storage.load_progress_state(data_dir, event.session)
    recent = (
        prior_progress.get("recent")
        if isinstance(prior_progress.get("recent"), list)
        else []
    )
    if recent and recent[-1].get("event_fingerprint") == event_fingerprint:
        return ToolReviewState(
            turn_state=turn_state,
            checkpoint=None,
            review_kind="checkpoint",
            event_seq=int(prior_progress.get("event_seq") or 0),
        )
    category = checkpoints.evidence_category(event)
    task_source = None
    if not category and not (event.failure_known and event.failed):
        task_source = source_context.capture_referenced_task_source(
            str(turn_state.get("task_anchor") or ""),
            event.tool_input,
            event.tool_output,
        )
    if category or task_source:
        turn_state = storage.record_turn_evidence(
            data_dir,
            event.session,
            record=checkpoints.render_evidence_record(event) if category else "",
            category=category,
            scope=checkpoints.evidence_scope(event),
            task_source=task_source,
        )

    transition, _objective = checkpoints.goal_transition(event)
    progress = storage.record_tool_progress(
        data_dir,
        event.session,
        failed=category == "failure",
        goal_transition=transition,
        evidence_category=category,
        failure_family=checkpoints.failure_family(event),
        event_fingerprint=event_fingerprint,
    )
    event_seq = int(progress.get("event_seq") or 0)
    if category or transition:
        storage.observe_injected_response(
            data_dir,
            event.session,
            event_seq=event_seq,
            observation_kind="semantic-event",
            observation={
                "evidence_category": category,
                "evidence_scope": checkpoints.evidence_scope(event),
                "failed": category == "failure",
                "goal_transition": transition,
            },
        )

    strategy = checkpoints.classify_strategy(progress)
    checkpoint = strategy
    review_kind: ReviewKind = "checkpoint"
    if strategy:
        checkpoint = strategy
        review_kind = "strategy"
    intervention_status, barrier_seq = storage.latest_intervention_state(
        data_dir, event.session
    )
    if checkpoint and intervention_status in {"queued", "emitted"}:
        checkpoint = None
    elif (
        checkpoint
        and intervention_status == "injected"
        and not checkpoints.semantic_cycle_after(progress, barrier_seq)
    ):
        checkpoint = None
    if strategy and checkpoint:
        storage.mark_strategy_reviewed(
            data_dir,
            event.session,
            event_seq=event_seq,
            midturn=review_kind == "strategy",
        )
    return ToolReviewState(
        turn_state=turn_state,
        checkpoint=checkpoint,
        review_kind=review_kind,
        event_seq=event_seq,
    )
