#!/usr/bin/env python3
"""Mid-work Masters' Nudge checkpoint hook.

Classifies high-value PostToolUse/PostToolUseFailure events, calls the same
side-review model as the Stop-hook worker, and returns a non-blocking
additionalContext nudge directly to the main Claude agent.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

import source_context
from masters_nudge import claude_adapter, checkpoints as shared_checkpoints, storage
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
    hook: dict[str, Any],
    event: dict[str, str],
    *,
    session: SessionRef | None = None,
) -> ReviewOutcome:
    settings = claude_adapter.runtime_settings()
    transcript_path = str(hook.get("transcript_path") or "")
    session = session or claude_adapter.session_from_hook(hook)
    state = storage.load_turn_state(settings.paths.data_dir, session)
    assistant_context = claude_adapter.read_latest_assistant_text(
        transcript_path, int(state.get("transcript_offset") or 0)
    )
    source_packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        event_context=event["context"],
        assistant_context=assistant_context,
    )

    request = ReviewRequest(
        schema_version=1,
        kind="checkpoint",
        reason=event["reason"],
        session=session,
        source_packet=source_packet,
        source_fingerprint=event["fingerprint"],
        routing_evidence=event["context"],
    )
    return ReviewCore(
        settings,
        log_error=lambda message: claude_adapter.log_error(
            "claude-checkpoint", message
        ),
    ).review(
        request,
        persist_reaction=True,
        timeout_sec=settings.checkpoint_timeout_sec,
    )


@dataclass(frozen=True)
class PreparedCheckpoint:
    output: dict[str, Any]
    session: SessionRef
    fingerprint: str
    reaction_ts: str
    reason: str
    tool_evidence: str


def build_hook_output(
    event_name: str,
    reaction: str,
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": reaction,
        }
    }


def prepare_hook(hook: dict[str, Any]) -> PreparedCheckpoint | None:
    tool_event = normalize_tool_event(hook)
    if tool_event is None:
        return None
    event = shared_checkpoints.classify_tool(tool_event)
    if event is None:
        return None

    settings = claude_adapter.runtime_settings()
    session = tool_event.session
    if not storage.claim_checkpoint(
        settings.paths.data_dir, session, event["fingerprint"]
    ):
        return None
    try:
        outcome = review_checkpoint(hook, event, session=session)
        if outcome.status != "finding" or not outcome.finding:
            storage.release_checkpoint(
                settings.paths.data_dir, session, event["fingerprint"]
            )
            return None
        turn_state = storage.load_turn_state(settings.paths.data_dir, session)
        transcript_path = str(hook.get("transcript_path") or "")
        tool_evidence = claude_adapter.read_recent_tool_evidence(
            transcript_path, int(turn_state.get("transcript_offset") or 0)
        )
        return PreparedCheckpoint(
            output=build_hook_output(
                str(hook.get("hook_event_name") or "PostToolUse"), outcome.finding
            ),
            session=session,
            fingerprint=event["fingerprint"],
            reaction_ts=outcome.reaction_ts,
            reason=event["reason"],
            tool_evidence=tool_evidence,
        )
    except Exception as exc:
        claude_adapter.log_error(
            "claude-checkpoint", f"checkpoint processing failed: {exc}"
        )
        storage.release_checkpoint(
            settings.paths.data_dir, session, event["fingerprint"]
        )
        return None


def emit_prepared(
    prepared: PreparedCheckpoint,
    *,
    stream: Any = None,
) -> None:
    """Write and flush the hook response before recording an injected receipt."""
    target = stream if stream is not None else sys.stdout
    settings = claude_adapter.runtime_settings()
    try:
        target.write(json.dumps(prepared.output, ensure_ascii=False) + "\n")
        target.flush()
    except Exception:
        try:
            if prepared.reaction_ts:
                storage.mark_delivery(
                    settings.paths.data_dir,
                    prepared.session,
                    prepared.reaction_ts,
                    status="failed",
                    delivered_via="claude-checkpoint",
                )
        finally:
            storage.release_checkpoint(
                settings.paths.data_dir, prepared.session, prepared.fingerprint
            )
        raise
    # The host has received the bytes. Complete the de-duplication claim before
    # receipt persistence so a local receipt failure cannot cause re-injection.
    storage.complete_checkpoint(
        settings.paths.data_dir, prepared.session, prepared.fingerprint
    )
    if prepared.reaction_ts:
        storage.mark_delivered(
            settings.paths.data_dir,
            prepared.session,
            prepared.reaction_ts,
            delivered_via="claude-checkpoint",
        )
    storage.mark_checkpoint_delivery(
        settings.paths.data_dir,
        prepared.session,
        reason=prepared.reason,
        tool_evidence=prepared.tool_evidence,
    )


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
        emit_prepared(prepared)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        claude_adapter.log_error(
            "claude-checkpoint", f"checkpoint main failed: {exc}"
        )
        sys.exit(0)
