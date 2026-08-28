#!/usr/bin/env python3
"""Masters' Nudge — Claude Stop observation hook.

Records whether the main agent responded after an earlier injected Nudge.
Stop does not call a Provider or emit another Nudge.

Never raises out of main() — hook must not block on our errors.
"""

import json
import os
import sys
from typing import Any

from masters_nudge import claude_adapter, storage
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
    assistant_claim = focus_text.strip()
    storage.observe_injected_response(
        settings.paths.data_dir,
        session,
        event_seq=int(state.get("evidence_seq") or 0),
        observation_kind="stop",
        observation={
            "assistant_claim": assistant_claim
        },
    )
    return None


def main() -> None:
    if active_guard():
        return
    hook = read_hook_input()
    prepare_hook(hook)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
