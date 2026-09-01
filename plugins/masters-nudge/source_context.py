#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
TASK_SOURCES_MAX_CHARS = 8000
TASK_SOURCE_MAX_CHARS = 6000
PACKET_MAX_CHARS = 12000
CONTRACT_SECTION_MAX_CHARS = 6000
CURRENT_RESULT_SECTION_MAX_CHARS = 5800
CURRENT_WORKSPACE_MAX_CHARS = 2200
PREVIOUS_FINDINGS_MAX_CHARS = 600
PACKET_TASK_SOURCE_MAX_CHARS = 3200
PACKET_RESULT_RECORD_MAX_CHARS = 1600
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"

_BACKTICK_REFERENCE_RE = re.compile(r"`([^`\r\n]+)`")
_MARKDOWN_REFERENCE_RE = re.compile(r"\[[^\]]+\]\(([^)\r\n]+)\)")
_PLAIN_REFERENCE_RE = re.compile(
    r"(?<![\w./\\-])((?:(?:[A-Za-z]:)?[./\\])?[\w.-]+"
    r"(?:[/\\][\w.-]+)*\.[A-Za-z0-9]{1,16})(?![\w./\\-])"
)
_PATHISH_REFERENCE_RE = re.compile(
    r"(?:[/\\]|\.[A-Za-z0-9][A-Za-z0-9._-]{0,15}$)"
)


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


def _normalized_reference(value: str) -> str:
    return str(value or "").strip().strip("<>").replace("\\", "/").lower()


def referenced_task_sources(task_request: str) -> tuple[str, ...]:
    """Return path-like sources the user explicitly named in the task request."""
    candidates = [
        *(_BACKTICK_REFERENCE_RE.findall(str(task_request or ""))),
        *(_MARKDOWN_REFERENCE_RE.findall(str(task_request or ""))),
        *(_PLAIN_REFERENCE_RE.findall(str(task_request or ""))),
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


def load_referenced_task_sources(
    task_request: str,
    workspace_root: str,
) -> dict[str, str]:
    """Read explicitly referenced relative files that are inside the workspace."""
    loaded: dict[str, str] = {}
    if not str(workspace_root or "").strip():
        return loaded
    try:
        root = Path(workspace_root).resolve()
    except (OSError, RuntimeError):
        return loaded
    for source in referenced_task_sources(task_request):
        reference = Path(source)
        if reference.is_absolute():
            continue
        try:
            candidate = (root / reference).resolve()
            candidate.relative_to(root)
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except (OSError, RuntimeError, ValueError):
            continue
        content = head_tail(content, TASK_SOURCE_MAX_CHARS)
        if content:
            loaded[source] = content
    return loaded


def render_task_sources(task_sources: Any) -> str:
    if isinstance(task_sources, Mapping):
        parts = [
            f"source: {name}\n{head_tail(str(content), PACKET_TASK_SOURCE_MAX_CHARS)}"
            for name, content in task_sources.items()
            if str(name).strip() and str(content).strip()
        ]
        return head_tail("\n\n".join(parts), TASK_SOURCES_MAX_CHARS)
    return head_tail(str(task_sources or ""), TASK_SOURCES_MAX_CHARS)


def _records(evidence_records: Any, category: str) -> list[dict[str, Any]]:
    if not isinstance(evidence_records, list):
        return []
    selected: list[dict[str, Any]] = []
    for record in evidence_records:
        if not isinstance(record, Mapping):
            continue
        if str(record.get("category") or "") != category:
            continue
        content = str(record.get("content") or "").strip()
        if not content:
            continue
        try:
            seq = int(record.get("seq") or 0)
        except (TypeError, ValueError):
            continue
        selected.append(
            {
                "seq": seq,
                "category": category,
                "content": content,
            }
        )
    return selected


def _render_result_records(records: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for record in records:
        rendered.append(
            head_tail(
                f"[evidence seq={record['seq']} category={record['category']}]\n"
                f"{record['content']}",
                PACKET_RESULT_RECORD_MAX_CHARS,
            )
        )
    return "\n\n".join(rendered) if rendered else "[]"


def _current_results(evidence_records: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    limits = {"change": 1, "verification": 2, "failure": 2, "measurement": 2}
    for category, limit in limits.items():
        records.extend(_records(evidence_records, category)[-limit:])
    records.sort(key=lambda record: record["seq"])
    return records


def _render_previous_findings(previous_findings: Any) -> str:
    if not isinstance(previous_findings, list):
        return ""
    values = [str(value).strip() for value in previous_findings if str(value).strip()]
    return head_tail(
        "\n".join(f"- {value}" for value in values),
        PREVIOUS_FINDINGS_MAX_CHARS,
    )


def _build_packet(
    *,
    task_anchor: str,
    task_sources: Any,
    workspace_snapshot: str,
    previous_findings: Any,
    evidence_records: Any,
) -> str:
    contract_lines = [
        "task:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "unknown",
    ]
    rendered_sources = render_task_sources(task_sources)
    if rendered_sources:
        contract_lines.extend(("sources:", rendered_sources))

    result_lines = [_render_result_records(_current_results(evidence_records))]
    findings = _render_previous_findings(previous_findings)
    packet = "\n\n".join(
        part
        for part in (
            _section(
                "contract",
                "\n".join(contract_lines),
                CONTRACT_SECTION_MAX_CHARS,
            ),
            _section(
                "previous findings",
                findings,
                PREVIOUS_FINDINGS_MAX_CHARS,
            ),
            _section(
                "current workspace",
                workspace_snapshot,
                CURRENT_WORKSPACE_MAX_CHARS,
            ),
            _section(
                "current result",
                "\n".join(result_lines),
                CURRENT_RESULT_SECTION_MAX_CHARS,
            ),
        )
        if part
    )
    return head_tail(packet, PACKET_MAX_CHARS)


def build_checkpoint_packet(
    task_anchor: str,
    task_sources: Any = "",
    workspace_snapshot: str = "",
    previous_findings: Any = None,
    evidence_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        workspace_snapshot=workspace_snapshot,
        previous_findings=previous_findings,
        evidence_records=evidence_records,
    )
