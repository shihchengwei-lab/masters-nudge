#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


TASK_ANCHOR_MAX_CHARS = 2000
CHECKPOINT_EVENT_MAX_CHARS = 3000
CHECKPOINT_AGENT_CONTEXT_MAX_CHARS = 1200
STOP_ASSISTANT_MAX_CHARS = 2500
TOOL_EVIDENCE_MAX_CHARS = 2000
AGENTCAM_EVIDENCE_MAX_CHARS = 2000
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"

AGENTCAM_SECTION_NAMES = {
    "risk flags",
    "changed files",
    "exit code detail",
    "test status",
    "test results",
    "tests",
    "verification",
}


def head_tail(text: str, max_chars: int) -> str:
    """Keep both ends of long evidence with an explicit middle-cut marker."""
    text = str(text or "").strip()
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars <= len(TRUNCATION_MARKER):
        return text[:max_chars]

    available = max_chars - len(TRUNCATION_MARKER)
    head_chars = max(1, (available * 2) // 5)
    tail_chars = available - head_chars
    return text[:head_chars] + TRUNCATION_MARKER + text[-tail_chars:]


def _safe_session_id(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id or ""))[:160]
    return safe or "unknown"


def source_state_path(state_dir: Path, session_id: str) -> Path:
    return Path(state_dir) / f"{_safe_session_id(session_id)}.source.json"


def load_source_state(state_dir: Path, session_id: str) -> dict:
    path = source_state_path(state_dir, session_id)
    if not path.exists():
        return {"task_anchor": "", "transcript_offset": 0}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {"task_anchor": "", "transcript_offset": 0}
    if not isinstance(state, dict):
        return {"task_anchor": "", "transcript_offset": 0}
    try:
        transcript_offset = max(0, int(state.get("transcript_offset") or 0))
    except (TypeError, ValueError):
        transcript_offset = 0
    return {
        "task_anchor": str(state.get("task_anchor") or ""),
        "transcript_offset": transcript_offset,
    }


def save_source_state(
    state_dir: Path,
    session_id: str,
    prompt: str,
    transcript_path: str = "",
) -> None:
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    transcript_offset = 0
    if transcript_path:
        try:
            transcript_offset = os.path.getsize(transcript_path)
        except OSError:
            transcript_offset = 0
    state = {
        "task_anchor": head_tail(prompt, TASK_ANCHOR_MAX_CHARS),
        "transcript_offset": transcript_offset,
    }
    path = source_state_path(state_dir, session_id)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(temp_path, path)


def _section(label: str, content: str, max_chars: int) -> str:
    content = head_tail(content, max_chars)
    if not content:
        return ""
    return f"[{label}]\n{content}\n[end {label}]"


def build_checkpoint_packet(
    task_anchor: str,
    event_context: str,
    assistant_context: str = "",
) -> str:
    parts = [
        _section("task anchor", task_anchor, TASK_ANCHOR_MAX_CHARS),
        _section(
            "checkpoint evidence", event_context, CHECKPOINT_EVENT_MAX_CHARS
        ),
        _section(
            "recent agent context",
            assistant_context,
            CHECKPOINT_AGENT_CONTEXT_MAX_CHARS,
        ),
    ]
    return "\n\n".join(part for part in parts if part)


def build_stop_packet(
    task_anchor: str,
    last_assistant_message: str,
    tool_evidence: str = "",
    agentcam_evidence: str = "",
) -> str:
    parts = [
        _section("task anchor", task_anchor, TASK_ANCHOR_MAX_CHARS),
        _section(
            "agent final claim", last_assistant_message, STOP_ASSISTANT_MAX_CHARS
        ),
        _section("tool evidence", tool_evidence, TOOL_EVIDENCE_MAX_CHARS),
        _section(
            "agentcam evidence", agentcam_evidence, AGENTCAM_EVIDENCE_MAX_CHARS
        ),
    ]
    return "\n\n".join(part for part in parts if part)


def _normalize_heading(heading: str) -> str:
    heading = re.sub(r"[`*_]", "", heading).strip().lower()
    return re.sub(r"\s+", " ", heading)


def extract_agentcam_evidence(report: str) -> str:
    """Select objective agentcam sections instead of tail-cropping the report."""
    selected: list[str] = []
    current: list[str] | None = None
    for line in str(report or "").splitlines():
        heading_match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading_match:
            if current:
                selected.append("\n".join(current).strip())
            heading = _normalize_heading(heading_match.group(1))
            current = [line] if heading in AGENTCAM_SECTION_NAMES else None
            continue
        if current is not None:
            current.append(line)
    if current:
        selected.append("\n".join(current).strip())
    return head_tail("\n\n".join(part for part in selected if part), AGENTCAM_EVIDENCE_MAX_CHARS)
