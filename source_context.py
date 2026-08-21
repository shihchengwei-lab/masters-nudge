#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any


TASK_ANCHOR_MAX_CHARS = 2000
CHECKPOINT_EVENT_MAX_CHARS = 3000
CHECKPOINT_AGENT_CONTEXT_MAX_CHARS = 1200
CHECKPOINT_BOTTLENECK_MAX_CHARS = 4300
CHECKPOINT_WORKFLOW_MAX_CHARS = 1800
CHECKPOINT_MECHANISM_MAX_CHARS = 3500
CHECKPOINT_TENSION_MAX_CHARS = 2200
SHADER_TASK_ANCHOR_MAX_CHARS = 1000
SHADER_DECISION_MATERIAL_MAX_CHARS = 4200
SHADER_DIRECT_EVIDENCE_MAX_CHARS = 2600
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
    workflow_context: str = "",
    tool_evidence: str = "",
) -> str:
    bounded_event = head_tail(event_context, CHECKPOINT_EVENT_MAX_CHARS)
    bounded_agent = head_tail(
        assistant_context, CHECKPOINT_AGENT_CONTEXT_MAX_CHARS
    )
    bottleneck_parts = []
    if bounded_agent:
        bottleneck_parts.append(f"visible agent explanation:\n{bounded_agent}")
    if bounded_event:
        bottleneck_parts.append(f"latest classified bottleneck:\n{bounded_event}")
    tension_parts = []
    if task_anchor:
        tension_parts.append(f"target still in force:\n{task_anchor}")
    if bounded_event:
        tension_parts.append(
            f"latest evidence not yet reconciled:\n{bounded_event}"
        )
    parts = [
        _section("task anchor", task_anchor, TASK_ANCHOR_MAX_CHARS),
        _section(
            "current bottleneck model",
            "\n\n".join(bottleneck_parts),
            CHECKPOINT_BOTTLENECK_MAX_CHARS,
        ),
        _section(
            "repeated explanation and workflow evidence",
            workflow_context,
            CHECKPOINT_WORKFLOW_MAX_CHARS,
        ),
        _section(
            "failed or no-change mechanisms",
            tool_evidence,
            CHECKPOINT_MECHANISM_MAX_CHARS,
        ),
        _section(
            "unresolved contradiction",
            "\n\n".join(tension_parts),
            CHECKPOINT_TENSION_MAX_CHARS,
        ),
    ]
    return "\n\n".join(part for part in parts if part)


def build_shader_research_packet(
    change: str,
    projection: str,
    *,
    task_anchor: str = "",
    tool_evidence: str = "",
) -> str:
    """Present bounded decision material, not an undifferentiated tool journal."""
    parts = [
        _section("research target", task_anchor, SHADER_TASK_ANCHOR_MAX_CHARS),
        _section("new research-state delta", change, 1600),
        _section(
            "candidate decision material",
            projection,
            SHADER_DECISION_MATERIAL_MAX_CHARS,
        ),
        _section(
            "latest direct evidence",
            tool_evidence,
            SHADER_DIRECT_EVIDENCE_MAX_CHARS,
        ),
    ]
    return "\n\n".join(part for part in parts if part)


def summarize_checkpoint_progress(progress: dict[str, Any]) -> str:
    """Render bounded, factual workflow recurrence without inferring intent."""
    raw_recent = progress.get("recent")
    recent = raw_recent[-8:] if isinstance(raw_recent, list) else []
    recent = [item for item in recent if isinstance(item, dict)]
    if not recent:
        return ""

    families = [
        str(item.get("command_family") or item.get("tool") or "tool")
        for item in recent
    ]
    counts = Counter(families)
    repeated = [(family, count) for family, count in counts.items() if count >= 2]
    failed = [item for item in recent if item.get("failed")]

    stable_counts: list[tuple[dict[str, Any], int]] = []
    previous_changed_lines: int | None = None
    for item in recent:
        value = item.get("changed_lines")
        if not item.get("mutating") or not isinstance(value, int):
            continue
        if previous_changed_lines == value:
            stable_counts.append((item, value))
        previous_changed_lines = value

    lines: list[str] = []
    if repeated:
        lines.append("repeated workflow families:")
        lines.extend(f"- {family} ×{count}" for family, count in repeated)
    if failed:
        lines.append("failed events:")
        for item in failed:
            family = str(item.get("command_family") or item.get("tool") or "tool")
            lines.append(f"- #{item.get('event_seq')} {family} (failed)")
    if stable_counts:
        lines.append("no changed-line movement (aggregate count only):")
        for item, value in stable_counts:
            family = str(item.get("command_family") or item.get("tool") or "tool")
            lines.append(f"- #{item.get('event_seq')} {family}: {value} lines")
    lines.append("recent workflow:")
    for item, family in zip(recent, families):
        flags = []
        if item.get("failed"):
            flags.append("failed")
        if item.get("goal_transition"):
            flags.append(f"goal={item['goal_transition']}")
        lines.append(
            f"- #{item.get('event_seq')} {family} {' '.join(flags)}".rstrip()
        )
    return head_tail("\n".join(lines), CHECKPOINT_WORKFLOW_MAX_CHARS)


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
