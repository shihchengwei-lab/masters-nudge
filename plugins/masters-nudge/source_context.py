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
CHECKPOINT_SECTION_MAX_CHARS = 5800
CURRENT_WORKSPACE_MAX_CHARS = 2200
WORKSPACE_DIFF_LEGEND = (
    "diff legend: '-' means removed/not current; '+' means present/current"
)
WORKSPACE_SNAPSHOT_MAX_CHARS = (
    CURRENT_WORKSPACE_MAX_CHARS - len(WORKSPACE_DIFF_LEGEND) - 1
)
PREVIOUS_FINDINGS_MAX_CHARS = 600
PACKET_TASK_SOURCE_MAX_CHARS = 3200
PACKET_CHECKPOINT_RECORD_MAX_CHARS = 1600
ACTOR_SOURCE_SECTION_MAX_CHARS = 2400
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
_CONTEXT_TOKEN_RE = re.compile(
    r"[A-Za-z_$][A-Za-z0-9_$]{3,}|[\u3400-\u9fff]{2,}"
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
    if not isinstance(evidence_records, (list, tuple)):
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


def _render_checkpoint_records(records: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for record in records:
        content = record["content"]
        if record["category"] == "change":
            content = f"current batch change; current workspace unavailable:\n{content}"
        rendered.append(
            head_tail(
                f"[evidence seq={record['seq']} category={record['category']}]\n"
                f"{content}",
                PACKET_CHECKPOINT_RECORD_MAX_CHARS,
            )
        )
    return "\n\n".join(rendered) if rendered else "[]"


def _checkpoint_results(
    checkpoint_records: Any, *, workspace_available: bool
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not workspace_available:
        records.extend(_records(checkpoint_records, "change"))
    for category in ("verification", "failure", "measurement"):
        records.extend(_records(checkpoint_records, category))
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


def _context_tokens(value: str) -> set[str]:
    return {
        token.casefold()
        for token in _CONTEXT_TOKEN_RE.findall(str(value or ""))
        if len(token) >= 4 or ord(token[0]) > 127
    }


def _actor_source_candidates(
    actor_source_records: Any,
    *,
    query: str,
) -> list[tuple[int, int, str, frozenset[str]]]:
    if not isinstance(actor_source_records, list):
        return []
    query_tokens = _context_tokens(query)
    if not query_tokens:
        return []
    folded_query = query.casefold()
    candidates: list[tuple[int, int, str, frozenset[str]]] = []
    for record in actor_source_records:
        if not isinstance(record, Mapping):
            continue
        content = str(record.get("content") or "").strip()
        if not content:
            continue
        try:
            sequence = int(record.get("seq") or 0)
        except (TypeError, ValueError):
            sequence = 0
        command = ""
        result = content
        marker = "\n\nresult:\n"
        if content.startswith("actual_command:\n") and marker in content:
            command, result = content[len("actual_command:\n") :].split(marker, 1)
        lines = result.splitlines()
        intervals: list[tuple[int, int]] = []
        for index, line in enumerate(lines):
            folded = line.casefold()
            if any(token in folded for token in query_tokens):
                start = max(0, index - 1)
                end = min(len(lines), index + 2)
                if (
                    intervals
                    and start <= intervals[-1][1]
                    and end - intervals[-1][0] <= 5
                ):
                    intervals[-1] = (intervals[-1][0], max(intervals[-1][1], end))
                else:
                    intervals.append((start, end))
        for start, end in intervals:
            excerpt = "\n".join(lines[start:end]).strip()
            if not excerpt:
                continue
            if excerpt.casefold() in folded_query:
                continue
            covered = {
                token for token in query_tokens if token in excerpt.casefold()
            }
            score = sum(
                min(len(token), 24) * min(folded_query.count(token), 8)
                for token in covered
            )
            rendered = (
                f"[actor source seq={sequence}]\n"
                f"command: {head_tail(command, 320)}\n"
                f"{excerpt}"
            )
            candidates.append((score, sequence, rendered, frozenset(covered)))
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidates


def render_actor_source_context(
    actor_source_records: Any,
    *,
    query: str,
    max_chars: int = ACTOR_SOURCE_SECTION_MAX_CHARS,
) -> str:
    """Select coherent excerpts only from source text already shown to the actor."""
    selected: list[str] = []
    seen_excerpts: set[str] = set()
    covered_tokens: set[str] = set()
    used = 0
    for _score, _sequence, candidate, candidate_tokens in _actor_source_candidates(
        actor_source_records,
        query=query,
    ):
        excerpt_key = candidate.split("\n", 2)[-1].strip().casefold()
        if (
            not excerpt_key
            or excerpt_key in seen_excerpts
            or (selected and candidate_tokens <= covered_tokens)
        ):
            continue
        bounded = head_tail(candidate, min(900, max_chars))
        cost = len(bounded) + (2 if selected else 0)
        if selected and used + cost > max_chars:
            continue
        if not selected and len(bounded) > max_chars:
            bounded = head_tail(bounded, max_chars)
            cost = len(bounded)
        selected.append(bounded)
        seen_excerpts.add(excerpt_key)
        covered_tokens.update(candidate_tokens)
        used += cost
        if used >= max_chars:
            break
    return "\n\n".join(selected)


def _build_packet(
    *,
    task_anchor: str,
    task_sources: Any,
    workspace_snapshot: str,
    actor_source_records: Any,
    previous_findings: Any,
    checkpoint_records: Any,
) -> str:
    contract_lines = [
        "task:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "unknown",
    ]
    rendered_sources = render_task_sources(task_sources)
    if rendered_sources:
        contract_lines.extend(("sources:", rendered_sources))

    current_workspace = str(workspace_snapshot or "").strip()
    result_content = _render_checkpoint_records(
        _checkpoint_results(
            checkpoint_records,
            workspace_available=bool(current_workspace),
        )
    )
    actor_query = "\n".join(
        (
            task_anchor,
            current_workspace,
            result_content,
        )
    )
    actor_content = render_actor_source_context(
        actor_source_records,
        query=actor_query,
    )
    findings = _render_previous_findings(previous_findings)
    contract_section = _section(
        "contract",
        "\n".join(contract_lines),
        CONTRACT_SECTION_MAX_CHARS,
    )
    findings_section = _section(
        "previous findings",
        findings,
        PREVIOUS_FINDINGS_MAX_CHARS,
    )
    workspace_section = _section(
        "current workspace — authoritative",
        (
            f"{WORKSPACE_DIFF_LEGEND}\n{current_workspace}"
            if current_workspace
            else ""
        ),
        CURRENT_WORKSPACE_MAX_CHARS,
    )
    base_sections = [
        part
        for part in (contract_section, findings_section, workspace_section)
        if part
    ]
    source_label = (
        "actor-observed source context — prior observations, non-authoritative"
    )
    checkpoint_label = "current checkpoint — triggering batch"
    source_overhead = len(f"[{source_label}]\n\n[end {source_label}]")
    checkpoint_overhead = len(
        f"[{checkpoint_label}]\n\n[end {checkpoint_label}]"
    )
    protected_checkpoint = min(
        len(result_content), PACKET_CHECKPOINT_RECORD_MAX_CHARS
    )
    source_budget = min(
        ACTOR_SOURCE_SECTION_MAX_CHARS,
        max(
            0,
            PACKET_MAX_CHARS
            - len("\n\n".join(base_sections))
            - source_overhead
            - checkpoint_overhead
            - protected_checkpoint
            - 4,
        ),
    )
    actor_section = _section(
        source_label,
        actor_content,
        source_budget,
    )
    fixed_sections = [
        part
        for part in (
            contract_section,
            findings_section,
            actor_section,
            workspace_section,
        )
        if part
    ]
    fixed_packet = "\n\n".join(fixed_sections)
    separator_chars = 2 if fixed_packet else 0
    checkpoint_budget = min(
        CHECKPOINT_SECTION_MAX_CHARS,
        max(
            0,
            PACKET_MAX_CHARS
            - len(fixed_packet)
            - separator_chars
            - checkpoint_overhead,
        ),
    )
    checkpoint_section = _section(
        checkpoint_label,
        result_content,
        checkpoint_budget,
    )
    return "\n\n".join(
        part for part in (*fixed_sections, checkpoint_section) if part
    )


def build_checkpoint_packet(
    task_anchor: str,
    task_sources: Any = "",
    workspace_snapshot: str = "",
    actor_source_records: Any = None,
    previous_findings: Any = None,
    checkpoint_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        workspace_snapshot=workspace_snapshot,
        actor_source_records=actor_source_records,
        previous_findings=previous_findings,
        checkpoint_records=checkpoint_records,
    )
