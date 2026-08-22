#!/usr/bin/env python3
"""Mid-work Masters' Nudge checkpoint hook.

Classifies high-value PostToolUse/PostToolUseFailure events, calls the same
side-review model as the Stop-hook worker, and returns a non-blocking
additionalContext nudge directly to the main Claude agent.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import claude_stop
import lens_router
import source_context
from masters_nudge import checkpoints as shared_checkpoints, storage
from masters_nudge.contracts import (
    EvidenceBundle,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
    find_git_root,
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
    cwd = str(hook.get("cwd") or "")
    return ToolCompleted(
        SessionRef(
            "claude_code",
            str(hook.get("session_id") or "unknown"),
            turn_id=str(hook.get("turn_id") or ""),
            cwd=cwd,
            repo_root=find_git_root(cwd),
        ),
        str(tool_name),
        tool_input=tool_input,
        tool_output=output,
        failed=failed,
        failure_known=failed,
        interrupted=bool(hook.get("is_interrupt")),
        mutating=tool_name in MUTATING_TOOLS,
        native_event_name=str(event_name),
    )


def generate_nudge(
    hook: dict[str, Any],
    event: dict[str, str],
    route: lens_router.ReviewRoute | None = None,
) -> str:
    settings = claude_stop._RUNTIME
    route = route or lens_router.resolve_review_route(
        settings.paths.data_dir, event["context"]
    )
    session_id = str(hook.get("session_id") or "unknown")
    transcript_path = str(hook.get("transcript_path") or "")
    cwd = str(hook.get("cwd") or "")
    session = SessionRef(
        "claude_code",
        session_id,
        turn_id=str(hook.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )
    state = storage.load_turn_state(settings.paths.data_dir, session)
    assistant_context = claude_stop.read_latest_assistant_text(
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
        evidence=EvidenceBundle(
            task_anchor=str(state.get("task_anchor") or ""),
            checkpoint_event=event["context"],
            assistant_claim=assistant_context,
        ),
        source_packet=source_packet,
        source_fingerprint=event["fingerprint"],
    )
    outcome = ReviewCore(settings, log_error=claude_stop.log_error).review(
        request,
        persist_reaction=True,
        timeout_sec=settings.checkpoint_timeout_sec,
    )
    if outcome.status == "finding" and outcome.reaction_ts:
        storage.mark_delivered(
            settings.paths.data_dir,
            session,
            outcome.reaction_ts,
            delivered_via="claude-checkpoint",
        )
    return outcome.finding


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


def process_hook(hook: dict[str, Any]) -> dict[str, Any] | None:
    tool_event = normalize_tool_event(hook)
    if tool_event is None:
        return None
    event = shared_checkpoints.classify_tool(tool_event)
    if event is None:
        return None

    settings = claude_stop._RUNTIME
    session_id = str(hook.get("session_id") or "unknown")
    cwd = str(hook.get("cwd") or "")
    session = SessionRef(
        "claude_code",
        session_id,
        turn_id=str(hook.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )
    if not storage.claim_checkpoint(
        settings.paths.data_dir, session, event["fingerprint"]
    ):
        return None
    try:
        route = lens_router.resolve_review_route(
            settings.paths.data_dir, event["context"]
        )
        reaction = generate_nudge(hook, event, route)
        if not reaction:
            storage.release_checkpoint(
                settings.paths.data_dir, session, event["fingerprint"]
            )
            return None
        storage.complete_checkpoint(
            settings.paths.data_dir, session, event["fingerprint"]
        )
        turn_state = storage.load_turn_state(settings.paths.data_dir, session)
        transcript_path = str(hook.get("transcript_path") or "")
        tool_evidence = claude_stop.read_recent_tool_evidence(
            transcript_path, int(turn_state.get("transcript_offset") or 0)
        )
        storage.mark_checkpoint_delivery(
            settings.paths.data_dir,
            session,
            reason=event["reason"],
            tool_evidence=tool_evidence,
        )
        return build_hook_output(
            str(hook.get("hook_event_name") or "PostToolUse"),
            reaction,
        )
    except Exception as exc:
        claude_stop.log_error(f"checkpoint processing failed: {exc}")
        storage.release_checkpoint(
            settings.paths.data_dir, session, event["fingerprint"]
        )
        return None


def main() -> None:
    if active_guard():
        return
    try:
        raw = sys.stdin.read()
        hook = json.loads(raw) if raw.strip() else {}
    except (TypeError, ValueError) as exc:
        claude_stop.log_error(f"checkpoint hook input parse failed: {exc}")
        return
    if not isinstance(hook, dict):
        return
    output = process_hook(hook)
    if output is not None:
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        claude_stop.log_error(f"checkpoint main failed: {exc}")
        sys.exit(0)
