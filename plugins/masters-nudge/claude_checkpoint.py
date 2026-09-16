#!/usr/bin/env python3
"""Claude PostToolBatch Nudge hook."""

from __future__ import annotations

import json
import sys
from typing import Any

import source_context
from masters_nudge import claude_adapter, evidence, prompting, storage
from masters_nudge.contracts import (
    Nudge,
    ToolCompleted,
    completed_mutation_from_input,
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
                mutation=completed_mutation_from_input(tool_input),
                native_event_name="PostToolBatch",
            )
        )
    return events


def nudge_checkpoint(observation: str) -> Nudge | None:
    settings = claude_adapter.runtime_settings()
    core = NudgeCore(
        settings,
        log_error=lambda message: claude_adapter.log_error("claude-checkpoint", message),
    )
    return core.nudge_once(observation, timeout_sec=PROVIDER_TIMEOUT_SEC)


def build_hook_output(
    message: str,
    evidence_items: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolBatch",
            "additionalContext": prompting.delivery_text(message, evidence_items),
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
    if storage.nudge_delivered(settings.paths.data_dir, events[0].session):
        return None
    state = observed.turn_state
    session = events[0].session
    try:
        observation = source_context.build_observation(
            str(state.get("task_anchor") or ""),
            events,
        )
    except (source_context.ObservationTooLargeError, ValueError) as exc:
        claude_adapter.log_error("claude-checkpoint", f"Nudge skipped: {exc}")
        return None
    try:
        nudge = nudge_checkpoint(observation)
    except Exception as exc:
        claude_adapter.log_error("claude-checkpoint", f"Nudge failed: {exc}")
        return None
    if nudge is None:
        return None
    return claude_adapter.PreparedDelivery(
        output=build_hook_output(nudge.message, nudge.evidence),
        session=events[0].session,
        message=nudge.message,
        evidence=nudge.evidence,
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
