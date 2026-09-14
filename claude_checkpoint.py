#!/usr/bin/env python3
"""Claude PostToolBatch Nudge hook."""

from __future__ import annotations

import json
import sys
from typing import Any

import source_context
from masters_nudge import claude_adapter, evidence, prompting, storage
from masters_nudge.contracts import (
    NudgeOutcome,
    ToolCompleted,
    mutation_evidence_from_input,
)
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import PROVIDER_TIMEOUT_SEC, active_guard


def normalize_tool_batch(hook: dict[str, Any]) -> list[ToolCompleted]:
    if hook.get("hook_event_name") != "PostToolBatch":
        return []
    calls = hook.get("tool_calls")
    if not isinstance(calls, list):
        return []
    session = claude_adapter.session_from_hook(hook)
    events: list[ToolCompleted] = []
    for call in calls:
        if not isinstance(call, dict):
            continue
        tool_name = str(call.get("tool_name") or "")
        if not tool_name:
            continue
        response = call.get("tool_response", "")
        tool_input = call.get("tool_input")
        if tool_input is None:
            tool_input = {}
        events.append(
            ToolCompleted(
                session,
                tool_name,
                tool_input=tool_input,
                tool_output=response,
                mutation=mutation_evidence_from_input(tool_input),
                native_event_name="PostToolBatch",
            )
        )
    return events


def nudge_checkpoint(source_packet: str) -> NudgeOutcome:
    settings = claude_adapter.runtime_settings()
    core = NudgeCore(
        settings,
        log_error=lambda message: claude_adapter.log_error("claude-checkpoint", message),
    )
    return core.nudge_once(source_packet, timeout_sec=PROVIDER_TIMEOUT_SEC)


def build_hook_output(
    status: str, principle: str, anchor: str, relationship: str
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolBatch",
            "additionalContext": prompting.delivery_text(
                status, principle, anchor, relationship
            ),
        }
    }


def prepare_hook(hook: dict[str, Any]) -> claude_adapter.PreparedDelivery | None:
    events = normalize_tool_batch(hook)
    if not events:
        return None
    settings = claude_adapter.runtime_settings()
    observed = evidence.observe_tool_batch(settings.paths.data_dir, events)
    if not observed.eligible:
        return None
    state = observed.turn_state
    packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        task_sources=state.get("task_sources") or {},
        evidence_records=list(observed.batch_records),
    )
    review_input = prompting.build_review_input(
        packet,
        storage.read_recent_returned_nudges(
            settings.paths.data_dir,
            events[0].session,
            limit=3,
        ),
    )
    try:
        outcome = nudge_checkpoint(review_input)
    except Exception as exc:
        claude_adapter.log_error("claude-checkpoint", f"Nudge failed: {exc}")
        return None
    visible_sequences = {record["seq"] for record in observed.batch_records}
    if (
        not prompting.is_delivery_status(outcome.status)
        or not outcome.relationship
        or outcome.evidence_seq not in visible_sequences
    ):
        return None
    return claude_adapter.PreparedDelivery(
        output=build_hook_output(
            outcome.status,
            outcome.principle,
            outcome.anchor,
            outcome.relationship,
        ),
        session=events[0].session,
        status=outcome.status,
        principle=outcome.principle,
        evidence_seq=outcome.evidence_seq,
        anchor=outcome.anchor,
        relationship=outcome.relationship,
        returned_via="PostToolBatch",
    )


def main() -> None:
    if active_guard():
        return
    try:
        value = json.loads(sys.stdin.read() or "{}")
    except (TypeError, ValueError) as exc:
        claude_adapter.log_error("claude-checkpoint", f"invalid input: {exc}")
        return
    if isinstance(value, dict):
        prepared = prepare_hook(value)
        if prepared is not None:
            claude_adapter.emit_json_delivery(prepared)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        claude_adapter.log_error("claude-checkpoint", f"main failed: {exc}")
