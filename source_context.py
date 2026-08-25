#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import re
from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
TASK_SOURCES_MAX_CHARS = 8000
TASK_SOURCE_MAX_CHARS = 6000
CHECKPOINT_EVENT_MAX_CHARS = 3000
INSPECTION_RECORD_MAX_CHARS = 2000
STOP_ASSISTANT_MAX_CHARS = 2500
AGENTCAM_EVIDENCE_MAX_CHARS = 2000
PACKET_MAX_CHARS = 16000
UNIVERSAL_SECTION_MAX_CHARS = 7200
SOFTWARE_SECTION_MAX_CHARS = 8400
PACKET_INSPECTION_RECORD_MAX_CHARS = 700
PACKET_CHANGE_RECORD_MAX_CHARS = 500
PACKET_VERIFICATION_RECORD_MAX_CHARS = 600
PACKET_FAILURE_RECORD_MAX_CHARS = 1000
PACKET_RUNTIME_EVIDENCE_MAX_CHARS = 700
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"

_BACKTICK_REFERENCE_RE = re.compile(r"`([^`\r\n]+)`")
_MARKDOWN_REFERENCE_RE = re.compile(r"\[[^\]]+\]\(([^)\r\n]+)\)")
_PATHISH_REFERENCE_RE = re.compile(
    r"(?:[/\\]|\.[A-Za-z0-9][A-Za-z0-9._-]{0,15}$)"
)
_CONTENT_READ_RE = re.compile(r"\b(?:get-content|cat|type|sed)\b", re.IGNORECASE)
_INSPECTION_COMMAND_RE = re.compile(
    r"\b(?:get-content|cat|type|sed|rg|grep)\b|\bgit\s+diff\b",
    re.IGNORECASE,
)
_DIRECT_READ_TOOLS = {"read", "read_file", "read_text_file"}

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


def capture_inspection_evidence(
    tool_name: str,
    tool_input: Any,
    tool_output: Any,
) -> str:
    """Keep successful source content while omitting the operation that read it."""
    leaf_tool = str(tool_name or "").lower().split("__")[-1]
    direct_read = (
        leaf_tool in _DIRECT_READ_TOOLS
        and isinstance(tool_input, Mapping)
        and bool(tool_input.get("file_path") or tool_input.get("path"))
    )
    if isinstance(tool_input, Mapping):
        command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    else:
        command = str(tool_input or "")
    shell_read = bool(command and _INSPECTION_COMMAND_RE.search(command))
    if not (direct_read or shell_read):
        return ""
    sources: list[str] = []
    if direct_read and isinstance(tool_input, Mapping):
        source = str(tool_input.get("file_path") or tool_input.get("path") or "").strip()
        if source:
            sources.append(source)
    if command:
        tokens = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^\s|;&]+)', command)
        for token_parts in tokens:
            token = next((part.strip() for part in token_parts if part.strip()), "")
            token = token.rstrip(",:")
            if (
                token
                and not token.startswith("-")
                and _PATHISH_REFERENCE_RE.search(token)
                and token not in sources
            ):
                sources.append(token)
            if len(sources) >= 4:
                break
    content = head_tail(_compact(tool_output), INSPECTION_RECORD_MAX_CHARS)
    if not content:
        return ""
    source_block = (
        "source:\n" + "\n".join(f"- {source}" for source in sources) + "\n"
        if sources
        else ""
    )
    return f"{source_block}inspection:\n{content}"


def render_task_sources(task_sources: Any) -> str:
    if isinstance(task_sources, Mapping):
        parts = [
            f"source: {name}\n{content}"
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
                "scope": str(record.get("scope") or "").strip(),
                "content": content,
            }
        )
    return selected


def _record_refs(records: list[dict[str, Any]]) -> str:
    if not records:
        return "[]"
    return "\n".join(f"  - evidence #{record['seq']}" for record in records)


def _render_current_records(
    records: list[dict[str, Any]], *, limit: int, max_chars: int
) -> str:
    rendered: list[str] = []
    for record in records[-limit:]:
        scope = f"\nscope: {record['scope']}" if record["scope"] else ""
        rendered.append(
            f"[evidence #{record['seq']}]{scope}\n"
            f"{head_tail(record['content'], max_chars)}"
        )
    return "\n\n".join(rendered) if rendered else "[]"


def _partition_failures(
    failures: list[dict[str, Any]], verifications: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[tuple[dict[str, Any], dict[str, Any]]]]:
    """Close a failure only after a newer verification of the same known scope."""
    latest_by_scope = {
        record["scope"]: record
        for record in verifications
        if record["scope"]
    }
    open_failures: list[dict[str, Any]] = []
    closed: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for failure in failures:
        later = latest_by_scope.get(failure["scope"]) if failure["scope"] else None
        if later and int(later["seq"]) > int(failure["seq"]):
            closed.append((failure, later))
        else:
            open_failures.append(failure)
    return open_failures, closed


def _build_packet(
    *,
    task_anchor: str,
    task_sources: Any,
    evidence_records: Any,
    event_context: str = "",
    completion_claim: str = "",
    agentcam_evidence: str = "",
) -> str:
    inspections = _records(evidence_records, "inspection")
    changes = _records(evidence_records, "change")
    verifications = _records(evidence_records, "verification")
    failures = _records(evidence_records, "failure")
    open_failures, closed_failures = _partition_failures(failures, verifications)

    universal_lines = [
        "task_contract:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "  unknown",
    ]
    rendered_sources = render_task_sources(task_sources)
    if rendered_sources:
        universal_lines.extend(("referenced_sources:", rendered_sources))
    universal_lines.extend(
        (
            "current_state:",
            f"  latest_evidence_seq: {max((record['seq'] for record in inspections + changes + verifications + failures), default=0)}",
            f"  change_evidence: {'present' if changes else 'none'}",
            "verified_facts:",
            _record_refs(verifications[-3:]),
        )
    )
    if open_failures:
        universal_lines.extend(("open_issues:", _record_refs(open_failures[-3:])))
    else:
        universal_lines.append("open_issues: []")
    universal_lines.append("closed_hypotheses:")
    if closed_failures:
        universal_lines.extend(
            f"  - evidence #{failure['seq']} closed by evidence #{verification['seq']}"
            for failure, verification in closed_failures[-3:]
        )
    else:
        universal_lines.append("[]")
    if event_context.strip():
        universal_lines.extend(
            ("review_event:", head_tail(event_context, CHECKPOINT_EVENT_MAX_CHARS))
        )
    if completion_claim.strip():
        universal_lines.extend(
            ("completion_claim:", head_tail(completion_claim, STOP_ASSISTANT_MAX_CHARS))
        )

    software_lines = [
        "relevant_sources:",
        _render_current_records(
            inspections, limit=2, max_chars=PACKET_INSPECTION_RECORD_MAX_CHARS
        ),
        "relevant_changes:",
        _render_current_records(
            changes, limit=2, max_chars=PACKET_CHANGE_RECORD_MAX_CHARS
        ),
    ]
    if agentcam_evidence.strip():
        software_lines.extend(
            (
                "external_runtime_evidence:",
                head_tail(agentcam_evidence, PACKET_RUNTIME_EVIDENCE_MAX_CHARS),
            )
        )
    software_lines.extend((
        "verification:",
        _render_current_records(
            verifications, limit=3, max_chars=PACKET_VERIFICATION_RECORD_MAX_CHARS
        ),
        "active_failures:",
        _render_current_records(
            open_failures, limit=3, max_chars=PACKET_FAILURE_RECORD_MAX_CHARS
        ),
    ))
    packet = "\n\n".join(
        (
            _section(
                "universal task state",
                "\n".join(universal_lines),
                UNIVERSAL_SECTION_MAX_CHARS,
            ),
            _section(
                "software engineering evidence",
                "\n".join(software_lines),
                SOFTWARE_SECTION_MAX_CHARS,
            ),
        )
    )
    return head_tail(packet, PACKET_MAX_CHARS)


def build_checkpoint_packet(
    task_anchor: str,
    event_context: str,
    task_sources: Any = "",
    evidence_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        evidence_records=evidence_records,
        event_context=event_context,
    )


def build_stop_packet(
    task_anchor: str,
    last_assistant_message: str,
    task_sources: Any = "",
    evidence_records: Any = None,
    agentcam_evidence: str = "",
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        evidence_records=evidence_records,
        completion_claim=last_assistant_message,
        agentcam_evidence=agentcam_evidence,
    )


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
