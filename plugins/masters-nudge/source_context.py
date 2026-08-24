#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import re
from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
TASK_SOURCES_MAX_CHARS = 8000
TASK_SOURCE_MAX_CHARS = 6000
CHECKPOINT_EVENT_MAX_CHARS = 3000
CHANGE_EVIDENCE_MAX_CHARS = 3000
VERIFICATION_EVIDENCE_MAX_CHARS = 3500
FAILURE_HISTORY_MAX_CHARS = 3500
STOP_ASSISTANT_MAX_CHARS = 2500
AGENTCAM_EVIDENCE_MAX_CHARS = 2000
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"

_BACKTICK_REFERENCE_RE = re.compile(r"`([^`\r\n]+)`")
_MARKDOWN_REFERENCE_RE = re.compile(r"\[[^\]]+\]\(([^)\r\n]+)\)")
_PATHISH_REFERENCE_RE = re.compile(
    r"(?:[/\\]|\.[A-Za-z0-9][A-Za-z0-9._-]{0,15}$)"
)
_CONTENT_READ_RE = re.compile(r"\b(?:get-content|cat|type|sed)\b", re.IGNORECASE)

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


def _section(label: str, content: str, max_chars: int) -> str:
    content = head_tail(content, max_chars)
    if not content:
        return ""
    return f"[{label}]\n{content}\n[end {label}]"


def _compact(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    try:
        import json

        return json.dumps(value, ensure_ascii=False, sort_keys=True).strip()
    except (TypeError, ValueError):
        return str(value or "").strip()


def _normalized_reference(value: str) -> str:
    return str(value or "").strip().strip("<>").replace("\\", "/").lower()


def _reads_reference(tool_input: Any, source: str) -> bool:
    """Accept explicit content reads, not navigation that merely names a file."""
    normalized_source = _normalized_reference(source)
    if not normalized_source:
        return False
    if isinstance(tool_input, Mapping):
        for key in ("file_path", "path"):
            candidate = _normalized_reference(tool_input.get(key, ""))
            if candidate == normalized_source or candidate.endswith(
                f"/{normalized_source}"
            ):
                return True
        command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    else:
        command = str(tool_input or "")
    source_token = re.compile(
        rf"(?<![A-Za-z0-9._-]){re.escape(normalized_source)}(?![A-Za-z0-9._-])"
    )
    for segment in re.split(r"(?:&&|\|\||[;|])", command):
        normalized_segment = _normalized_reference(segment)
        if (
            source_token.search(normalized_segment)
            and _CONTENT_READ_RE.search(segment)
        ):
            return True
    return False


def referenced_task_sources(task_request: str) -> tuple[str, ...]:
    """Return path-like sources the user explicitly named in the task request."""
    candidates = [
        *(_BACKTICK_REFERENCE_RE.findall(str(task_request or ""))),
        *(_MARKDOWN_REFERENCE_RE.findall(str(task_request or ""))),
    ]
    sources: list[str] = []
    seen: set[str] = set()
    for raw in candidates:
        source = str(raw or "").strip().strip("<>")
        normalized = _normalized_reference(source)
        if (
            not normalized
            or "://" in normalized
            or not _PATHISH_REFERENCE_RE.search(source)
            or normalized in seen
        ):
            continue
        seen.add(normalized)
        sources.append(source)
    return tuple(sources)


def capture_referenced_task_source(
    task_request: str,
    tool_input: Any,
    tool_output: Any,
) -> tuple[str, str] | None:
    """Promote a successful read only when it names a task-referenced source."""
    for source in referenced_task_sources(task_request):
        if _reads_reference(tool_input, source):
            content = head_tail(_compact(tool_output), TASK_SOURCE_MAX_CHARS)
            if content:
                return source, content
    return None


def render_task_sources(task_sources: Any) -> str:
    if isinstance(task_sources, Mapping):
        parts = [
            f"source: {name}\n{content}"
            for name, content in task_sources.items()
            if str(name).strip() and str(content).strip()
        ]
        return head_tail("\n\n".join(parts), TASK_SOURCES_MAX_CHARS)
    return head_tail(str(task_sources or ""), TASK_SOURCES_MAX_CHARS)


def build_checkpoint_packet(
    task_anchor: str,
    event_context: str,
    task_sources: Any = "",
    change_evidence: str = "",
    verification_evidence: str = "",
    failure_history: str = "",
) -> str:
    parts = [
        _section("task request", task_anchor, TASK_ANCHOR_MAX_CHARS),
        _section(
            "referenced task sources",
            render_task_sources(task_sources),
            TASK_SOURCES_MAX_CHARS,
        ),
        _section("checkpoint event", event_context, CHECKPOINT_EVENT_MAX_CHARS),
        _section("change evidence", change_evidence, CHANGE_EVIDENCE_MAX_CHARS),
        _section(
            "verification evidence",
            verification_evidence,
            VERIFICATION_EVIDENCE_MAX_CHARS,
        ),
        _section(
            "failure history",
            failure_history,
            FAILURE_HISTORY_MAX_CHARS,
        ),
    ]
    return "\n\n".join(part for part in parts if part)


def build_stop_packet(
    task_anchor: str,
    last_assistant_message: str,
    task_sources: Any = "",
    change_evidence: str = "",
    verification_evidence: str = "",
    failure_history: str = "",
    agentcam_evidence: str = "",
) -> str:
    parts = [
        _section("task request", task_anchor, TASK_ANCHOR_MAX_CHARS),
        _section(
            "referenced task sources",
            render_task_sources(task_sources),
            TASK_SOURCES_MAX_CHARS,
        ),
        _section("change evidence", change_evidence, CHANGE_EVIDENCE_MAX_CHARS),
        _section(
            "verification evidence",
            verification_evidence,
            VERIFICATION_EVIDENCE_MAX_CHARS,
        ),
        _section(
            "failure history",
            failure_history,
            FAILURE_HISTORY_MAX_CHARS,
        ),
        _section(
            "agent final claim", last_assistant_message, STOP_ASSISTANT_MAX_CHARS
        ),
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
