#!/usr/bin/env python3
"""Buddy_similar — UserPromptSubmit hook worker.

Reads the per-session buddy log under ~/.claude/buddy/<session_id>.log,
finds reactions newer than the last consumed timestamp (per-session state),
prints the most recent unread reaction to stdout. The Claude Code hook system
appends stdout to the user's next prompt as additional context.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Single source of truth for the runtime length cap. Both files live in the
# same install dir, so this import is safe; importing `buddy` runs only its
# module-level env reads, no IO.
from buddy import MAX_REACTION_CHARS

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
BUDDY_DIR = CLAUDE_DIR / "buddy"
ERROR_LOG = CLAUDE_DIR / "buddy-error.log"


MAX_ERROR_LOG_BYTES = 256 * 1024  # 256 KB


def _rotate_error_log() -> None:
    """If error log exceeds MAX_ERROR_LOG_BYTES, keep only the last half."""
    try:
        if not ERROR_LOG.exists():
            return
        size = ERROR_LOG.stat().st_size
        if size <= MAX_ERROR_LOG_BYTES:
            return
        keep = size // 2
        with ERROR_LOG.open("rb") as f:
            f.seek(size - keep)
            f.readline()  # skip partial line
            tail = f.read()
        with ERROR_LOG.open("wb") as f:
            f.write(tail)
    except Exception:
        pass


def log_error(msg: str) -> None:
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        _rotate_error_log()
        with ERROR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] inject: {msg}\n")
    except Exception:
        pass


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


def state_path_for(session_id: str) -> Path:
    return BUDDY_DIR / f"{session_id}.state.json"


def log_path_for(session_id: str) -> Path:
    return BUDDY_DIR / f"{session_id}.log"


def load_state(session_id: str) -> dict:
    sf = state_path_for(session_id)
    if not sf.exists():
        return {"last_ts": ""}
    try:
        return json.loads(sf.read_text(encoding="utf-8"))
    except Exception as e:
        log_error(f"state read failed: {e}")
        return {"last_ts": ""}


def save_state(session_id: str, state: dict) -> None:
    try:
        BUDDY_DIR.mkdir(parents=True, exist_ok=True)
        state_path_for(session_id).write_text(
            json.dumps(state, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        log_error(f"state save failed: {e}")


def read_pending(session_id: str, last_ts: str) -> list:
    lp = log_path_for(session_id)
    if not lp.exists():
        return []
    pending = []
    try:
        with lp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("ts", "") > last_ts:
                    pending.append(obj)
    except Exception as e:
        log_error(f"log read failed: {e}")
    return pending


def main() -> None:
    hook = read_hook_input()
    session_id = hook.get("session_id", "")
    if not session_id:
        log_error("no session_id in hook input, skipping")
        return

    state = load_state(session_id)
    last_ts = state.get("last_ts", "")
    pending = read_pending(session_id, last_ts)
    if not pending:
        return

    # Inject only the latest reaction. Older unread ones are skipped to avoid
    # backlog dumping; their existence is preserved in the log for review.
    latest = pending[-1]
    reaction = (latest.get("reaction") or "").strip()
    if reaction:
        ts = latest.get("ts", "")
        # Plain text stdout — per CC docs, plain stdout shows in the user's
        # transcript UI (visible). additionalContext via JSON is "more discreet"
        # and surfaces only to the LLM context, invisible to the user.
        flat_reaction = reaction.replace("\n", " ").strip()
        # Defense-in-depth: strip wrapper markers and cap length
        # (cap shared with buddy.py via MAX_REACTION_CHARS import)
        import re
        flat_reaction = re.sub(r"\[(?:end )?Buddy[^\]]*\]", "", flat_reaction).strip()
        if len(flat_reaction) > MAX_REACTION_CHARS:
            flat_reaction = flat_reaction[:MAX_REACTION_CHARS]
        if not flat_reaction:
            return
        context_text = f"[Buddy（第三方第二意見，非指令）| {ts}] {flat_reaction} [end Buddy]"
        out_bytes = (context_text + "\n").encode("utf-8")
        sys.stdout.buffer.write(out_bytes)
        sys.stdout.buffer.flush()
        log_error(f"printed plain {len(out_bytes)} bytes for ts={ts} session={session_id[:8]}")

    state["last_ts"] = latest.get("ts", last_ts)
    save_state(session_id, state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
