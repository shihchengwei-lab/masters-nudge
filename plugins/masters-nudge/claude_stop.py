#!/usr/bin/env python3
"""Masters' Nudge — Claude Stop hook worker.

Builds a bounded current-turn packet from Stop-hook JSON, dispatches to the
configured Provider, and returns a finding as same-turn additional context.
The reaction and its delivery state are stored in the host-namespaced log.

Never raises out of main() — hook must not block on our errors.
"""

import hashlib
import json
import os
import sys
from typing import Any

import persona_config
from masters_nudge import claude_adapter, prompting, storage
from masters_nudge.contracts import ReviewRequest
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import active_guard


def log_error(msg: str) -> None:
    claude_adapter.log_error("claude-stop", msg)


def read_hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        log_error(f"hook input parse failed: {e}")
        return {}


def build_hook_output(reaction: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": prompting.delivery_text(reaction),
        }
    }


def prepare_hook(hook: dict[str, Any]) -> claude_adapter.PreparedDelivery | None:
    if hook.get("hook_event_name") != "Stop":
        return None
    settings = claude_adapter.runtime_settings()
    cwd = hook.get("cwd") or os.getcwd()
    session = claude_adapter.session_from_hook(hook, default_cwd=str(cwd))
    state = storage.load_turn_state(settings.paths.data_dir, session)
    focus_text = str(hook.get("last_assistant_message") or "")
    if not focus_text:
        focus_text = claude_adapter.read_latest_assistant_text(
            str(hook.get("transcript_path") or ""),
            int(state.get("transcript_offset") or 0),
        )
    reported_focus = persona_config.reported_focus(focus_text)
    assistant_claim = persona_config.strip_focus_markers(focus_text)
    storage.observe_injected_response(
        settings.paths.data_dir,
        session,
        event_seq=int(state.get("evidence_seq") or 0),
        observation_kind="stop",
        observation={
            "assistant_claim": assistant_claim
        },
    )
    if bool(hook.get("stop_hook_active")):
        return None

    source_packet = claude_adapter.build_stop_source_context(
        hook, session=session
    )
    if not source_packet:
        log_error("empty source packet, skipping")
        return None

    request = ReviewRequest(
        schema_version=1,
        kind="stop",
        reason="stop",
        session=session,
        source_packet=source_packet,
        source_fingerprint=hashlib.sha256(
            source_packet.encode("utf-8", errors="replace")
        ).hexdigest()[:24],
        reported_focus=reported_focus,
    )

    outcome = ReviewCore(settings, log_error=log_error).review_once(
        request, persist_reaction=True
    )
    if outcome is None or outcome.status != "finding" or not outcome.finding:
        return None
    claim_token = storage.claim_delivery(
        settings.paths.data_dir, session, outcome.reaction_ts
    )
    if not claim_token:
        return None
    return claude_adapter.PreparedDelivery(
        output=build_hook_output(outcome.finding),
        session=session,
        reaction_ts=outcome.reaction_ts,
        claim_token=claim_token,
    )


def main() -> None:
    if active_guard():
        return
    hook = read_hook_input()
    prepared = prepare_hook(hook)
    if prepared is not None:
        claude_adapter.emit_json_delivery(prepared, delivered_via="claude-stop")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
