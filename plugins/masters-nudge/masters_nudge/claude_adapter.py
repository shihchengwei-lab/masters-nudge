"""Shared Claude Code runtime and transcript ownership.

The three native Claude hook entries translate payloads and delivery only;
Claude's transcript format and runtime settings live here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import source_context

from . import storage
from .contracts import SessionRef, find_git_root
from .runtime import RuntimeSettings


RUNTIME = RuntimeSettings.from_env(Path(__file__).resolve().parent.parent, host="claude_code")

TRANSCRIPT_CHAR_BUDGET = 6000
PER_MESSAGE_MAX_CHARS = 5000
MIN_REMAINING_TO_INCLUDE = 400
TOOL_OUTPUT_TAIL_CHARS = 2000


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


def parse_transcript_entry(obj: dict) -> tuple[str, str, list[str]] | None:
    typ = obj.get("type")
    if typ not in ("user", "assistant"):
        return None
    prefix = "user" if typ == "user" else "claude"
    content = (obj.get("message", {}) or {}).get("content", "")
    text_parts: list[str] = []
    tool_results: list[str] = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_result":
                raw = block.get("content", "")
                if isinstance(raw, list):
                    tool_results.append("\n".join(
                        item.get("text", "")
                        for item in raw
                        if isinstance(item, dict) and item.get("type") == "text"
                    ))
                else:
                    tool_results.append(str(raw))
    else:
        text_parts.append(str(content))
    return prefix, "\n".join(part for part in text_parts if part).strip(), tool_results


def _read_transcript_entries(
    transcript_path: str, start_offset: int | None = None
) -> list[tuple[str, str, list[str]]]:
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
    entries: list[tuple[str, str, list[str]]] = []
    for line in lines:
        try:
            obj = json.loads(line.strip())
        except Exception:
            continue
        parsed = parse_transcript_entry(obj)
        if parsed is not None:
            entries.append(parsed)
    return entries


def read_recent_transcript(transcript_path: str) -> str:
    selected: list[tuple[str, str, list[str]]] = []
    remaining = TRANSCRIPT_CHAR_BUDGET
    for prefix, text, tool_results in reversed(_read_transcript_entries(transcript_path)):
        if not text:
            selected.append((prefix, "", tool_results))
            continue
        snippet = "…" + text[-PER_MESSAGE_MAX_CHARS:] if len(text) > PER_MESSAGE_MAX_CHARS else text
        if len(snippet) <= remaining:
            selected.append((prefix, snippet, tool_results))
            remaining -= len(snippet)
            continue
        if remaining >= MIN_REMAINING_TO_INCLUDE:
            selected.append((prefix, "…" + text[-(remaining - 1):], tool_results))
        break
    selected.reverse()
    transcript_lines: list[str] = []
    tool_buffer: list[str] = []
    for prefix, snippet, tool_results in selected:
        if snippet:
            transcript_lines.append(f"{prefix}: {snippet}")
        tool_buffer.extend(tool_results)
    out: list[str] = []
    if transcript_lines:
        out.append(
            "[transcript — 從最新往回填，總長 ≤ "
            f"{TRANSCRIPT_CHAR_BUDGET} 字；單則超過 {PER_MESSAGE_MAX_CHARS} 字者以…起頭]"
        )
        out.extend(transcript_lines)
        out.append("[end transcript]")
    if tool_buffer:
        out.append(
            "[tool output — 工具回傳合併後尾部 "
            f"{TOOL_OUTPUT_TAIL_CHARS} 字；非對話本身]"
        )
        out.append("\n".join(tool_buffer)[-TOOL_OUTPUT_TAIL_CHARS:])
        out.append("[end tool output]")
    return "\n".join(out)


def read_recent_tool_evidence(transcript_path: str, start_offset: int = 0) -> str:
    entries = _read_transcript_entries(
        transcript_path, start_offset if start_offset > 0 else None
    )
    return "\n".join(
        result for _, _, results in entries for result in results if result
    )


def read_latest_assistant_text(transcript_path: str, start_offset: int = 0) -> str:
    entries = _read_transcript_entries(
        transcript_path, start_offset if start_offset > 0 else None
    )
    for prefix, text, _ in reversed(entries):
        if prefix == "claude" and text:
            return text
    return ""


def build_stop_source_context(
    hook: dict,
    agentcam_content: str = "",
    *,
    session: SessionRef,
) -> dict:
    settings = runtime_settings()
    transcript_path = str(hook.get("transcript_path") or "")
    state = storage.load_turn_state(settings.paths.data_dir, session)
    offset = int(state.get("transcript_offset") or 0)
    last_assistant = str(hook.get("last_assistant_message") or "")
    if not last_assistant:
        last_assistant = read_latest_assistant_text(transcript_path, offset)
    tool_evidence = read_recent_tool_evidence(transcript_path, offset)
    agentcam_evidence = source_context.extract_agentcam_evidence(agentcam_content)

    if not any((last_assistant, tool_evidence, agentcam_evidence)):
        packet = read_recent_transcript(transcript_path)
    else:
        packet = source_context.build_stop_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            last_assistant_message=last_assistant,
            tool_evidence=tool_evidence,
            agentcam_evidence=agentcam_evidence,
        )
    overlap = storage.checkpoint_stop_overlap(
        settings.paths.data_dir, session, tool_evidence=tool_evidence
    )
    return {
        "packet": packet,
        "task_anchor": str(state.get("task_anchor") or ""),
        "assistant_claim": last_assistant,
        "tool_evidence": tool_evidence,
        "agentcam_evidence": agentcam_evidence,
        "checkpoint_overlap": overlap,
    }
