#!/usr/bin/env python3
"""Mid-work Masters' Nudge checkpoint hook.

Classifies high-value PostToolUse/PostToolUseFailure events, waits for the same
side-review model as the Stop hook, and returns additionalContext directly to
the main Claude agent in that event.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import source_context
from masters_nudge import (
    claude_adapter,
    checkpoints as shared_checkpoints,
    prompting,
    storage,
)
from masters_nudge.contracts import (
    ReviewOutcome,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
)
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import active_guard

MUTATING_TOOLS = {"Edit", "Write", "Bash", "PowerShell"}


def normalize_tool_event(hook: dict[str, Any]) -> ToolCompleted | None:
    """Translate a Claude hook payload into the host-neutral tool event."""
    event_name = hook.get("hook_event_name", "")
    tool_name = hook.get("tool_name", "")
    tool_input = hook.get("tool_input") or {}
    if event_name not in {"PostToolUse", "PostToolUseFailure"}:
        return None
    failed = event_name == "PostToolUseFailure"
    output = hook.get("error", "") if failed else hook.get("tool_response", "")
    return ToolCompleted(
        claude_adapter.session_from_hook(hook),
        str(tool_name),
        tool_input=tool_input,
        tool_output=output,
        failed=failed,
        failure_known=failed,
        interrupted=bool(hook.get("is_interrupt")),
        mutating=tool_name in MUTATING_TOOLS,
        native_event_name=str(event_name),
    )


def review_checkpoint(
    event: dict[str, str],
    *,
    session: SessionRef,
) -> ReviewOutcome | None:
    settings = claude_adapter.runtime_settings()
    state = storage.load_turn_state(settings.paths.data_dir, session)
    source_packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        event_context=event["context"],
        task_sources=state.get("task_sources") or {},
        change_evidence=str(state.get("change_evidence") or ""),
        verification_evidence=str(state.get("verification_evidence") or ""),
        failure_history=(
            ""
            if event["reason"] == "test-fail"
            else str(state.get("failure_history") or "")
        ),
    )

    request = ReviewRequest(
        schema_version=1,
        kind="checkpoint",
        reason=event["reason"],
        session=session,
        source_packet=source_packet,
        source_fingerprint=event["fingerprint"],
        routing_evidence=event["context"],
        routing_concern=event.get("routing_concern", ""),
    )
    return ReviewCore(
        settings,
        log_error=lambda message: claude_adapter.log_error(
            "claude-checkpoint", message
        ),
    ).review_once(
        request,
        persist_reaction=True,
        timeout_sec=settings.checkpoint_timeout_sec,
    )


def build_hook_output(
    event_name: str,
    reaction: str,
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": prompting.delivery_text(reaction),
        }
    }


def prepare_hook(hook: dict[str, Any]) -> claude_adapter.PreparedDelivery | None:
    tool_event = normalize_tool_event(hook)
    if tool_event is None:
        return None
    settings = claude_adapter.runtime_settings()
    session = tool_event.session
    state = storage.load_turn_state(settings.paths.data_dir, session)
    category = shared_checkpoints.evidence_category(tool_event)
    task_source = None
    if not category and not (tool_event.failure_known and tool_event.failed):
        task_source = source_context.capture_referenced_task_source(
            str(state.get("task_anchor") or ""),
            tool_event.tool_input,
            tool_event.tool_output,
        )
    if category or task_source:
        state = storage.record_turn_evidence(
            settings.paths.data_dir,
            session,
            record=(
                shared_checkpoints.render_evidence_record(tool_event)
                if category
                else ""
            ),
            category=category,
            task_source=task_source,
        )

    storage.observe_injected_response(
        settings.paths.data_dir,
        session,
        event_seq=int(state.get("evidence_seq") or 0),
        observation_kind="tool",
        observation={
            "tool": tool_event.tool_name,
            "failed": tool_event.failure_known and tool_event.failed,
            "mutating": tool_event.mutating,
        },
    )

    event = shared_checkpoints.classify_tool(tool_event)
    if event is None:
        return None
    try:
        outcome = review_checkpoint(event, session=session)
        if outcome is None or outcome.status != "finding" or not outcome.finding:
            return None
        claim_token = storage.claim_delivery(
            settings.paths.data_dir, session, outcome.reaction_ts
        )
        if not claim_token:
            return None
        return claude_adapter.PreparedDelivery(
            output=build_hook_output(
                str(hook.get("hook_event_name") or "PostToolUse"), outcome.finding
            ),
            session=session,
            reaction_ts=outcome.reaction_ts,
            claim_token=claim_token,
        )
    except Exception as exc:
        claude_adapter.log_error(
            "claude-checkpoint", f"checkpoint processing failed: {exc}"
        )
        return None


def main() -> None:
    if active_guard():
        return
    try:
        raw = sys.stdin.read()
        hook = json.loads(raw) if raw.strip() else {}
    except (TypeError, ValueError) as exc:
        claude_adapter.log_error(
            "claude-checkpoint", f"checkpoint hook input parse failed: {exc}"
        )
        return
    if not isinstance(hook, dict):
        return
    prepared = prepare_hook(hook)
    if prepared is not None:
        claude_adapter.emit_json_delivery(
            prepared, delivered_via="claude-checkpoint"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        claude_adapter.log_error(
            "claude-checkpoint", f"checkpoint main failed: {exc}"
        )
        sys.exit(0)
