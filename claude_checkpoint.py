#!/usr/bin/env python3
"""Claude PostToolBatch checkpoint hook for Masters' Nudge."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from typing import Any

import source_context
from masters_nudge import (
    claude_adapter,
    evidence as shared_evidence,
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

MUTATING_TOOLS = {"edit", "write", "bash", "powershell"}
EXIT_CODE_RE = re.compile(r"^Exit code\s+(-?\d+)\b", re.IGNORECASE)


def _response_failure(response: Any) -> tuple[bool, bool]:
    if isinstance(response, dict):
        if isinstance(response.get("is_error"), bool):
            return bool(response["is_error"]), True
        exit_code = response.get("exit_code")
        if isinstance(exit_code, int):
            return exit_code != 0, True
    if isinstance(response, list):
        flags = [
            block.get("is_error")
            for block in response
            if isinstance(block, dict) and isinstance(block.get("is_error"), bool)
        ]
        if flags:
            return any(flags), True
    match = EXIT_CODE_RE.match(str(response or "").strip())
    if match:
        return int(match.group(1)) != 0, True
    return False, False


def normalize_tool_batch(hook: dict[str, Any]) -> list[ToolCompleted]:
    """Translate one documented Claude PostToolBatch payload in call order."""
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
        failed, known = _response_failure(response)
        events.append(
            ToolCompleted(
                session,
                tool_name,
                tool_input=call.get("tool_input") or {},
                tool_output=response,
                failed=failed,
                failure_known=known,
                interrupted=bool(hook.get("is_interrupt")),
                mutating=tool_name.lower() in MUTATING_TOOLS,
                native_event_name="PostToolBatch",
            )
        )
    return events


def review_checkpoint(
    event: dict[str, str],
    *,
    session: SessionRef,
    source_event_seq: int = 0,
) -> ReviewOutcome | None:
    settings = claude_adapter.runtime_settings()
    state = storage.load_turn_state(settings.paths.data_dir, session)
    source_packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        task_sources=state.get("task_sources") or {},
        evidence_records=(
            state.get("evidence_records")
            if isinstance(state.get("evidence_records"), list)
            else []
        ),
    )

    request = ReviewRequest(
        schema_version=1,
        kind="checkpoint",
        reason=event["reason"],
        session=session,
        source_packet=source_packet,
        source_fingerprint=hashlib.sha256(
            (
                f"checkpoint:{event.get('trigger') or event['reason']}\n"
                f"{source_packet}"
            ).encode("utf-8")
        ).hexdigest(),
        source_event_seq=source_event_seq,
        trigger=str(event.get("trigger") or event["reason"]),
        hook_event="PostToolBatch",
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
    tool_events = normalize_tool_batch(hook)
    if not tool_events:
        return None
    settings = claude_adapter.runtime_settings()
    session = tool_events[0].session
    observed = shared_evidence.observe_tool_batch(
        settings.paths.data_dir, tool_events
    )
    event = observed.checkpoint
    if event is None:
        return None
    try:
        outcome = review_checkpoint(
            event,
            session=session,
            source_event_seq=observed.event_seq,
        )
        if outcome is None or outcome.status != "finding" or not outcome.finding:
            return None
        claim_token = storage.claim_delivery(
            settings.paths.data_dir, session, outcome.reaction_ts
        )
        if not claim_token:
            return None
        return claude_adapter.PreparedDelivery(
            output=build_hook_output(
                "PostToolBatch", outcome.finding
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
