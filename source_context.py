#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
TASK_SOURCES_MAX_CHARS = 4000
TASK_SOURCE_MAX_CHARS = 3500
PACKET_MAX_CHARS = 12000
CONTRACT_SECTION_MAX_CHARS = 6000
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
_EXCLUDED_TASK_SOURCE_RE = re.compile(
    r"(?:"
    r"\b(?:do\s+not|don't|must\s+not|never)\b"
    r"[^.!?。！？,，;；\r\n]{0,48}\b"
    r"(?:read|open|load|inspect|use|send|include|share|upload|transmit)\b"
    r"|\bwithout\s+(?:reading|opening|loading|using|sending|including|sharing)\b"
    r"|\b(?:ignore|exclude|omit|skip)\b"
    r"|(?:不要|不得|禁止|請勿|勿|不可|無須|不必|不用|別)"
    r"[^.!?。！？,，;；\r\n]{0,48}"
    r"(?:讀取|讀|閱讀|開啟|載入|使用|傳送|傳給|提供|包含|納入|分享|上傳)"
    r"|(?:忽略|略過|排除|跳過)"
    r")",
    re.IGNORECASE,
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


def _reference_is_excluded(task_request: str, start: int, end: int) -> bool:
    text = str(task_request or "")
    clause_start = max(
        (text.rfind(boundary, 0, start) for boundary in ".!?。！？,，;；\r\n"),
        default=-1,
    )
    clause_ends = [
        index
        for boundary in ".!?。！？,，;；\r\n"
        if (index := text.find(boundary, end)) >= 0
    ]
    clause_end = min(clause_ends, default=len(text))
    clause = text[clause_start + 1 : clause_end]
    return bool(_EXCLUDED_TASK_SOURCE_RE.search(clause))


def referenced_task_sources(task_request: str) -> tuple[str, ...]:
    """Return non-negated path-like sources explicitly named by the user."""
    text = str(task_request or "")
    matches = [
        *(match for match in _BACKTICK_REFERENCE_RE.finditer(text)),
        *(match for match in _MARKDOWN_REFERENCE_RE.finditer(text)),
        *(match for match in _PLAIN_REFERENCE_RE.finditer(text)),
    ]
    matches.sort(key=lambda match: (match.start(1), match.end(1)))
    sources: list[str] = []
    seen: set[str] = set()
    for match in matches:
        source = str(match.group(1) or "").strip().strip("<>")
        normalized = _normalized_reference(source)
        if (
            not normalized
            or "://" in normalized
            or not _PATHISH_REFERENCE_RE.search(source)
            or normalized in seen
            or _reference_is_excluded(text, match.start(1), match.end(1))
        ):
            continue
        seen.add(normalized)
        sources.append(source)
    return tuple(sources)


def load_referenced_task_sources(
    task_request: str,
    workspace_root: str,
) -> dict[str, str]:
    """Read bounded, explicitly referenced files that resolve inside the workspace."""
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
            if not candidate.is_file():
                continue
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except (OSError, RuntimeError, ValueError):
            continue
        content = head_tail(content, TASK_SOURCE_MAX_CHARS)
        if content:
            loaded[source] = content
    return loaded


def render_task_sources(task_sources: Any) -> str:
    if not isinstance(task_sources, Mapping):
        return ""
    parts = [
        f"source: {name}\n{head_tail(str(content), TASK_SOURCE_MAX_CHARS)}"
        for name, content in task_sources.items()
        if str(name).strip() and str(content).strip()
    ]
    return head_tail("\n\n".join(parts), TASK_SOURCES_MAX_CHARS)


def _ordered_results(evidence_records: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence_records, (list, tuple)):
        return []
    selected: list[dict[str, Any]] = []
    for record in evidence_records:
        if not isinstance(record, Mapping):
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
                "content": content,
            }
        )
    selected.sort(key=lambda record: record["seq"])
    return selected


def _render_result_records(
    records: list[dict[str, Any]], max_chars: int
) -> str:
    if not records:
        return "[]"
    labels = [f"[tool result seq={record['seq']}]" for record in records]
    separators_size = 2 * (len(records) - 1)
    labels_size = sum(len(label) + 1 for label in labels)
    available = max(1, max_chars - labels_size - separators_size)
    per_record = max(1, available // len(records))
    rendered: list[str] = []
    for label, record in zip(labels, records):
        rendered.append(f"{label}\n{head_tail(record['content'], per_record)}")
    return "\n\n".join(rendered)


def _build_packet(
    *,
    task_anchor: str,
    task_sources: Any,
    evidence_records: Any,
) -> str:
    contract_lines = [
        "task:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "unknown",
    ]
    rendered_sources = render_task_sources(task_sources)
    if rendered_sources:
        contract_lines.extend(("sources:", rendered_sources))
    task_section = _section(
        "task beginning",
        "\n".join(contract_lines),
        CONTRACT_SECTION_MAX_CHARS,
    )
    separator = "\n\n"
    result_label = "decision evidence"
    result_wrapper_chars = len(f"[{result_label}]\n\n[end {result_label}]")
    result_content_max = max(
        1,
        PACKET_MAX_CHARS
        - len(task_section)
        - len(separator)
        - result_wrapper_chars,
    )
    result_content = _render_result_records(
        _ordered_results(evidence_records), result_content_max
    )
    result_section = _section(result_label, result_content, result_content_max)
    packet = separator.join((task_section, result_section))
    return head_tail(packet, PACKET_MAX_CHARS)


def build_checkpoint_packet(
    task_anchor: str,
    task_sources: Any = None,
    evidence_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        evidence_records=evidence_records,
    )
