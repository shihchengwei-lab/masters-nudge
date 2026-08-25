"""Host-neutral evidence helpers that do not depend on transcript formats."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import source_context

from . import checkpoints, storage
from .contracts import ReviewKind, ToolCompleted, find_git_root


AGENTCAM_REPORT_READ_CHARS = 65536


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
    inspection = ""
    if not category and not (event.failure_known and event.failed):
        task_source = source_context.capture_referenced_task_source(
            str(turn_state.get("task_anchor") or ""),
            event.tool_input,
            event.tool_output,
        )
        if not task_source:
            inspection = source_context.capture_inspection_evidence(
                event.tool_name,
                event.tool_input,
                event.tool_output,
            )
            if inspection:
                category = "inspection"
    if category or task_source:
        turn_state = storage.record_turn_evidence(
            data_dir,
            event.session,
            record=(
                inspection
                if category == "inspection"
                else checkpoints.render_evidence_record(event)
                if category
                else ""
            ),
            category=category,
            scope=checkpoints.evidence_scope(event),
            task_source=task_source,
        )

    transition, objective = checkpoints.goal_transition(event)
    progress = storage.record_tool_progress(
        data_dir,
        event.session,
        tool_name=event.tool_name,
        command_family=checkpoints.command_family(event),
        failed=category == "failure",
        mutating=event.mutating,
        goal_transition=transition,
        goal_objective=objective,
        evidence_category=category,
        evidence_scope=checkpoints.evidence_scope(event),
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
        review_kind = (
            "goal_transition"
            if strategy["reason"] == "goal-transition"
            else "strategy"
        )
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
        )
    if checkpoint and checkpoint["reason"] == "goal-transition":
        review_kind = "goal_transition"
    return ToolReviewState(
        turn_state=turn_state,
        checkpoint=checkpoint,
        review_kind=review_kind,
        event_seq=event_seq,
    )


def read_latest_agentcam_report(
    cwd: str, *, log_error: Callable[[str], None] | None = None
) -> dict[str, object] | None:
    root = find_git_root(cwd)
    if not root:
        return None
    runs_dir = Path(root) / ".git" / "agentcam" / "runs"
    if not runs_dir.is_dir():
        return None
    try:
        candidates = list(runs_dir.glob("*/AGENT_RUN_REPORT.md"))
        newest = max(candidates, key=lambda path: path.stat().st_mtime)
        content = newest.read_text(encoding="utf-8", errors="replace")
        mtime = newest.stat().st_mtime
    except (OSError, ValueError) as exc:
        if log_error:
            log_error(f"agentcam report read failed: {exc}")
        return None
    return {
        "path": str(newest),
        "content": source_context.head_tail(content, AGENTCAM_REPORT_READ_CHARS),
        "mtime": mtime,
    }
