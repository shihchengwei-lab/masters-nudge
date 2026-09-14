#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
PACKET_MAX_CHARS = 12000
CONTRACT_SECTION_MAX_CHARS = 6000
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"


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
    evidence_records: Any,
) -> str:
    contract_lines = [
        "task:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "unknown",
    ]
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
    evidence_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        evidence_records=evidence_records,
    )
