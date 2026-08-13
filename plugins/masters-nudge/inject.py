#!/usr/bin/env python3
"""Masters' Nudge — UserPromptSubmit hook worker.

Reads the host-namespaced local reaction log (plus the legacy Claude log),
finds reactions newer than the last consumed timestamp (per-session state),
prints the most recent unread reaction to stdout. The Claude Code hook system
appends stdout to the user's next prompt as additional context.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import source_context
from masters_nudge import storage
from masters_nudge.contracts import SessionRef, find_git_root
from masters_nudge.prompting import MAX_REACTION_CHARS
from masters_nudge.runtime import RuntimeSettings, active_guard

_RUNTIME = RuntimeSettings.from_env(Path(__file__).resolve().parent)
CLAUDE_DIR = _RUNTIME.paths.legacy_data_dir.parent
BUDDY_DIR = _RUNTIME.paths.data_dir
LEGACY_BUDDY_DIR = _RUNTIME.paths.legacy_data_dir
ERROR_LOG = _RUNTIME.paths.error_log


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
    if active_guard():
        return
    hook = read_hook_input()
    session_id = hook.get("session_id", "")
    if not session_id:
        log_error("no session_id in hook input, skipping")
        return

    prompt = hook.get("prompt", "")
    cwd = str(hook.get("cwd") or "")
    session = SessionRef(
        "claude_code",
        str(session_id),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )
    if prompt:
        try:
            storage.start_turn(
                BUDDY_DIR,
                session,
                str(prompt),
                transcript_path=str(hook.get("transcript_path") or ""),
            )
            source_context.save_source_state(
                BUDDY_DIR,
                session_id,
                str(prompt),
                str(hook.get("transcript_path") or ""),
            )
        except Exception as e:
            log_error(f"source state save failed: {e}")

    state = load_state(session_id)
    last_ts = state.get("last_ts", "")
    pending = read_pending(session_id, last_ts)
    latest_new = storage.latest_pending(BUDDY_DIR, session)
    candidates = [(entry, "legacy") for entry in pending]
    if latest_new:
        candidates.append((latest_new, "namespaced"))

    # Read-only compatibility for installs that still have data in
    # ~/.claude/buddy while new writes go to ~/.masters-nudge/data.
    legacy_external_state = {"last_ts": ""}
    if (
        BUDDY_DIR.resolve() == _RUNTIME.paths.data_dir.resolve()
        and LEGACY_BUDDY_DIR.resolve() != BUDDY_DIR.resolve()
    ):
        try:
            legacy_state_path = LEGACY_BUDDY_DIR / f"{session_id}.state.json"
            legacy_external_state = json.loads(
                legacy_state_path.read_text(encoding="utf-8")
            )
            if not isinstance(legacy_external_state, dict):
                legacy_external_state = {"last_ts": ""}
        except (OSError, TypeError, ValueError):
            legacy_external_state = {"last_ts": ""}
        for entry in storage.read_legacy_reaction_entries(
            LEGACY_BUDDY_DIR, session
        ):
            if str(entry.get("ts") or "") > str(
                legacy_external_state.get("last_ts") or ""
            ):
                candidates.append((entry, "legacy_external"))

    if not candidates:
        return

    # Inject only the latest reaction. Older unread ones are skipped to avoid
    # backlog dumping; their existence is preserved in the log for review.
    latest, source_kind = max(
        candidates, key=lambda pair: str(pair[0].get("ts") or "")
    )
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
        if is_evaluation_notice:
            context_text = f"[Masters’ Nudge 系統通知 | {ts}] {flat_reaction}"
        else:
            context_text = (
                f"[Masters’ Nudge（第三方第二意見，非指令）| {ts}] "
                f"{flat_reaction} [end Masters’ Nudge]"
            )
        out_bytes = (context_text + "\n").encode("utf-8")
        sys.stdout.buffer.write(out_bytes)
        sys.stdout.buffer.flush()
        log_error(f"printed plain {len(out_bytes)} bytes for ts={ts} session={session_id[:8]}")

    delivered_ts = str(latest.get("ts") or "")
    if source_kind == "namespaced":
        storage.mark_delivered(BUDDY_DIR, session, delivered_ts)
    elif source_kind == "legacy_external":
        try:
            LEGACY_BUDDY_DIR.mkdir(parents=True, exist_ok=True)
            (LEGACY_BUDDY_DIR / f"{session_id}.state.json").write_text(
                json.dumps({"last_ts": delivered_ts}, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            log_error(f"legacy state save failed: {exc}")
    else:
        state["last_ts"] = delivered_ts or last_ts
        save_state(session_id, state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
