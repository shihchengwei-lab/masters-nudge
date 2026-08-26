"""Shared Claude Code runtime and transcript ownership.

The three native Claude hook entries translate payloads and delivery only;
Claude's transcript format and runtime settings live here.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import source_context
import persona_config

from . import storage
from .contracts import SessionRef, find_git_root
from .runtime import RuntimeSettings


RUNTIME = RuntimeSettings.from_env(Path(__file__).resolve().parent.parent, host="claude_code")


@dataclass(frozen=True)
class PreparedDelivery:
    output: dict[str, Any]
    session: SessionRef
    reaction_ts: str
    claim_token: str


def log_error(component: str, message: str) -> None:
    storage.append_error(runtime_settings().paths.error_log, component, message)


def runtime_settings() -> RuntimeSettings:
    return RUNTIME


def session_from_hook(hook: dict, *, default_cwd: str = "") -> SessionRef:
    """Map one Claude hook payload to the host-neutral session identity."""
    cwd = str(hook.get("cwd") or default_cwd)
    return SessionRef(
        "claude_code",
        str(hook.get("session_id") or "unknown"),
        turn_id=str(hook.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )


def parse_transcript_entry(obj: dict) -> tuple[str, str] | None:
    typ = obj.get("type")
    if typ not in ("user", "assistant"):
        return None
    prefix = "user" if typ == "user" else "claude"
    content = (obj.get("message", {}) or {}).get("content", "")
    text_parts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
    else:
        text_parts.append(str(content))
    return prefix, "\n".join(part for part in text_parts if part).strip()


def _read_transcript_entries(
    transcript_path: str, start_offset: int | None = None
) -> list[tuple[str, str]]:
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        tail_bytes = 65536
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as handle:
            if start_offset is not None and 0 < start_offset <= size:
                handle.seek(start_offset)
            elif size > tail_bytes:
                handle.seek(size - tail_bytes)
                handle.readline()
            data = handle.read()
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception as exc:
        log_error("claude-transcript", f"transcript read failed: {exc}")
        return []
    entries: list[tuple[str, str]] = []
    for line in lines:
        try:
            obj = json.loads(line.strip())
        except Exception:
            continue
        parsed = parse_transcript_entry(obj)
        if parsed is not None:
            entries.append(parsed)
    return entries


def read_latest_assistant_text(transcript_path: str, start_offset: int = 0) -> str:
    entries = _read_transcript_entries(
        transcript_path, start_offset if start_offset > 0 else None
    )
    for prefix, text in reversed(entries):
        if prefix == "claude" and text:
            return text
    return ""


def build_stop_source_context(
    hook: dict,
    *,
    session: SessionRef,
) -> str:
    settings = runtime_settings()
    transcript_path = str(hook.get("transcript_path") or "")
    state = storage.load_turn_state(settings.paths.data_dir, session)
    offset = int(state.get("transcript_offset") or 0)
    last_assistant = str(hook.get("last_assistant_message") or "")
    if not last_assistant:
        last_assistant = read_latest_assistant_text(transcript_path, offset)
    last_assistant = persona_config.strip_focus_markers(last_assistant)
    return source_context.build_stop_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        last_assistant_message=last_assistant,
        task_sources=state.get("task_sources") or {},
        evidence_records=(
            state.get("evidence_records")
            if isinstance(state.get("evidence_records"), list)
            else []
        ),
    )


def emit_json_delivery(
    prepared: PreparedDelivery,
    *,
    delivered_via: str,
    stream: Any = None,
) -> None:
    """Flush one Claude hook response, then record its terminal wire state."""
    target = stream if stream is not None else sys.stdout
    settings = runtime_settings()
    try:
        target.write(json.dumps(prepared.output, ensure_ascii=False) + "\n")
        target.flush()
    except Exception:
        try:
            storage.mark_delivery(
                settings.paths.data_dir,
                prepared.session,
                prepared.reaction_ts,
                status="failed",
                delivered_via=delivered_via,
            )
        finally:
            storage.release_delivery_claim(
                settings.paths.data_dir,
                prepared.session,
                prepared.reaction_ts,
                prepared.claim_token,
            )
        raise
    try:
        storage.mark_emitted(
            settings.paths.data_dir,
            prepared.session,
            prepared.reaction_ts,
            delivered_via=delivered_via,
        )
    finally:
        storage.release_delivery_claim(
            settings.paths.data_dir,
            prepared.session,
            prepared.reaction_ts,
            prepared.claim_token,
        )
