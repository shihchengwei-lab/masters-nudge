#!/usr/bin/env python3
"""Masters' Nudge — UserPromptSubmit hook worker.

Reads the host-namespaced local reaction log and prints the most recent queued
reaction to stdout. The Claude Code hook system appends stdout to the user's
next prompt as additional context.
"""

import json
import sys

from masters_nudge import claude_adapter, storage
from masters_nudge.contracts import SessionRef, find_git_root
from masters_nudge.prompting import MAX_REACTION_CHARS
from masters_nudge.runtime import active_guard

def build_context_text(entry: dict, reaction: str) -> str:
    """Return the bounded Nudge without authority-signalling metadata."""
    timestamp = str(entry.get("ts") or "")
    if entry.get("kind") == "evaluation_notice":
        return f"[Masters’ Nudge 系統通知 | {timestamp}]\n{reaction}"
    return reaction


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
    cwd = str(hook.get("cwd") or "")
    session = SessionRef(
        "claude_code",
        str(session_id),
        turn_id=str(hook.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )
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

    latest = storage.latest_pending(data_dir, session)
    if not latest:
        return

    reaction = (latest.get("reaction") or "").strip()
    if reaction:
        ts = latest.get("ts", "")
        is_evaluation_notice = latest.get("kind") == "evaluation_notice"
        # Plain text stdout. Lands as a `UserPromptSubmit hook success:`
        # system-reminder visible only to the main agent's context — NOT
        # to the user's terminal. The user sees Masters' Nudge via buddy_window.py
        # instead. (CC docs once described plain stdout as user-visible;
        # empirically it isn't, and the floating window exists because of
        # that asymmetry. See README "Two visibility channels".)
        flat_reaction = reaction.replace("\n", " ").strip()
        # Defense-in-depth: strip wrapper markers and cap length
        # (cap shared with the reviewer core via masters_nudge.prompting)
        import re
        flat_reaction = re.sub(
            r"\[(?:end )?(?:Buddy|Masters[’'] Nudge)[^\]]*\]",
            "",
            flat_reaction,
        ).strip()
        max_chars = 160 if is_evaluation_notice else MAX_REACTION_CHARS
        if len(flat_reaction) > max_chars:
            flat_reaction = flat_reaction[:max_chars]
        if not flat_reaction:
            return
        context_text = build_context_text(latest, flat_reaction)
        out_bytes = (context_text + "\n").encode("utf-8")
        sys.stdout.buffer.write(out_bytes)
        sys.stdout.buffer.flush()
        log_error(f"printed plain {len(out_bytes)} bytes for ts={ts} session={session_id[:8]}")

    delivered_ts = str(latest.get("ts") or "")
    storage.mark_delivered(data_dir, session, delivered_ts)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
