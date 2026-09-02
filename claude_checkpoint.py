#!/usr/bin/env python3
"""Claude PostToolBatch Nudge hook."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from masters_nudge import claude_adapter, prompting
from masters_nudge.contracts import ToolCompleted
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import active_guard


MUTATING_TOOLS = {"edit", "write", "apply_patch", "file_change"}
EXIT_CODE_RE = re.compile(r"^Exit code\s+(-?\d+)\b", re.IGNORECASE)


def _response_failure(response: Any) -> tuple[bool, bool]:
    if isinstance(response, dict):
        if isinstance(response.get("is_error"), bool):
            return True, bool(response["is_error"])
        if isinstance(response.get("exit_code"), int):
            return True, response["exit_code"] != 0
    if isinstance(response, list):
        flags = [
            block.get("is_error")
            for block in response
            if isinstance(block, dict) and isinstance(block.get("is_error"), bool)
        ]
        if flags:
            return True, any(flags)
    match = EXIT_CODE_RE.match(str(response or "").strip())
    return (True, int(match.group(1)) != 0) if match else (False, False)


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
        known, failed = _response_failure(response)
        events.append(
            ToolCompleted(
                session,
                tool_name,
                tool_input=call.get("tool_input") or {},
                tool_output=response,
                failed=failed,
                failure_known=known,
                mutating=tool_name.lower() in MUTATING_TOOLS,
                native_event_name="PostToolBatch",
            )
        )
    return events


def build_hook_output(finding: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolBatch",
            "additionalContext": prompting.delivery_text(finding),
        }
    }


def prepare_hook(hook: dict[str, Any]) -> claude_adapter.PreparedDelivery | None:
    events = normalize_tool_batch(hook)
    if not events:
        return None
    settings = claude_adapter.runtime_settings()
    core = NudgeCore(
        settings,
        log_error=lambda message: claude_adapter.log_error("claude-checkpoint", message),
    )
    try:
        outcome = core.review_tool_batch(events)
    except Exception as exc:
        claude_adapter.log_error("claude-checkpoint", f"Nudge failed: {exc}")
        return None
    if outcome is None or outcome.status != "finding" or not outcome.finding:
        return None
    return claude_adapter.PreparedDelivery(
        output=build_hook_output(outcome.finding),
        session=events[0].session,
        lens=outcome.lens,
        finding=outcome.finding,
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
