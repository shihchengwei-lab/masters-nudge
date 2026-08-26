#!/usr/bin/env python3
"""Masters' Nudge — Claude UserPromptSubmit turn-state entry."""

import json
import sys

import persona_config
from masters_nudge import claude_adapter, storage
from masters_nudge.runtime import active_guard


def log_error(msg: str) -> None:
    claude_adapter.log_error("claude-prompt", msg)


def read_hook_input() -> dict:
    """Read JSON hook input from stdin. Returns {} if absent or invalid."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        log_error(f"hook input parse failed: {e}")
        return {}


def build_hook_output() -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": persona_config.FOCUS_REPORT_INSTRUCTION,
        }
    }


def main() -> None:
    if active_guard():
        return
    hook = read_hook_input()
    data_dir = claude_adapter.runtime_settings().paths.data_dir
    session_id = hook.get("session_id", "")
    if not session_id:
        log_error("no session_id in hook input, skipping")
        return

    prompt = hook.get("prompt", "")
    session = claude_adapter.session_from_hook(hook)
    if prompt:
        try:
            storage.start_turn(
                data_dir,
                session,
                str(prompt),
                transcript_path=str(hook.get("transcript_path") or ""),
            )
        except Exception as e:
            log_error(f"turn state save failed: {e}")
            return
    print(json.dumps(build_hook_output(), ensure_ascii=False))



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
