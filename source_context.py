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
DECISION_SECTION_MAX_CHARS = 6000
SUPPORTING_SECTION_MAX_CHARS = 9800
PACKET_TASK_SOURCE_MAX_CHARS = 3200
PACKET_INSPECTION_RECORD_MAX_CHARS = 700
PACKET_CHANGE_RECORD_MAX_CHARS = 1400
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
_PRIORITY_SOURCE_HEADING_RE = re.compile(
    r"\b(?:problem|issue|bug|expected|requirements?|acceptance|reproduc\w*|"
    r"behavior|behaviour|observable|input|output)\b"
    r"|(?:問題|預期|需求|驗收|重現|行為|輸入|輸出)",
    re.IGNORECASE,
)
_EVIDENCE_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?(?:[A-Za-z0-9_.-]+[/\\])+[A-Za-z0-9_.-]+"
    r"|(?<![A-Za-z0-9_.-])[A-Za-z0-9_.-]+\."
    r"(?:py|js|jsx|ts|tsx|go|rs|java|rb|md|toml|json|yaml|yml)",
    re.IGNORECASE,
)

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


def _task_source_excerpt(content: str) -> str:
    """Keep contract-bearing Markdown sections instead of bulk implementation notes."""
    content = str(content or "").strip()
    if len(content) <= PACKET_TASK_SOURCE_MAX_CHARS:
        return content
    sections = re.split(r"(?=^#{1,6}\s+.+$)", content, flags=re.MULTILINE)
    selected: list[str] = []
    for index, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        heading = section.splitlines()[0]
        if (index == 0 and not heading.startswith("#")) or _PRIORITY_SOURCE_HEADING_RE.search(
            heading
        ):
            selected.append(head_tail(section, 1000))
    excerpt = "\n\n".join(selected)
    return head_tail(excerpt or content, PACKET_TASK_SOURCE_MAX_CHARS)


def render_task_sources(task_sources: Any) -> str:
    if isinstance(task_sources, Mapping):
        parts = [
            f"source: {name}\n{_task_source_excerpt(str(content))}"
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


def _evidence_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for match in _EVIDENCE_PATH_RE.findall(str(text or "")):
        normalized = match.strip("'\"`<>[](){},:;").replace("\\", "/").lower()
        if normalized:
            paths.add(normalized)
    return paths


def _path_affinity(left: set[str], right: set[str]) -> int:
    if not left or not right:
        return 0
    exact = len(left & right)
    left_names = {path.rsplit("/", 1)[-1] for path in left}
    right_names = {path.rsplit("/", 1)[-1] for path in right}
    return (exact * 4) + len(left_names & right_names)


def _select_relevant_inspections(
    inspections: list[dict[str, Any]], context: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Prefer sources tied to the active approach or its latest outcome."""
    target_paths: set[str] = set()
    for record in context:
        target_paths.update(_evidence_paths(record["content"]))
        target_paths.update(_evidence_paths(record["scope"]))
    if not target_paths:
        return inspections[-2:]
    ranked = [
        (_path_affinity(_evidence_paths(record["content"]), target_paths), record)
        for record in inspections
    ]
    relevant = [item for item in ranked if item[0] > 0]
    relevant.sort(key=lambda item: (item[0], item[1]["seq"]), reverse=True)
    return sorted((record for _score, record in relevant[:2]), key=lambda record: record["seq"])


def _approach_outcome_pairs(
    changes: list[dict[str, Any]], outcomes: list[dict[str, Any]]
) -> str:
    pairs: list[str] = []
    ordered_changes = sorted(changes, key=lambda record: record["seq"])
    ordered_outcomes = sorted(outcomes, key=lambda record: record["seq"])
    for index, change in enumerate(ordered_changes):
        next_change_seq = (
            ordered_changes[index + 1]["seq"]
            if index + 1 < len(ordered_changes)
            else None
        )
        candidates = [
            outcome
            for outcome in ordered_outcomes
            if outcome["seq"] > change["seq"]
            and (next_change_seq is None or outcome["seq"] < next_change_seq)
        ]
        if candidates:
            pairs.append(
                f"  - evidence #{change['seq']} -> evidence #{candidates[-1]['seq']}"
            )
    return "\n".join(pairs[-2:]) if pairs else "[]"


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
    open_failures, _closed_failures = _partition_failures(failures, verifications)
    outcomes = sorted(verifications + failures, key=lambda record: record["seq"])
    latest_change = changes[-1:] if changes else []
    latest_outcome = outcomes[-1:] if outcomes else []
    latest_contradiction = open_failures[-1:] if open_failures else []
    decision_record_seqs = {
        record["seq"]
        for record in latest_change + latest_outcome + latest_contradiction
    }

    decision_lines = [
        "observable_goal:",
        head_tail(task_anchor, TASK_ANCHOR_MAX_CHARS) or "  unknown",
        "current_approach:",
        _render_current_records(
            latest_change, limit=1, max_chars=PACKET_CHANGE_RECORD_MAX_CHARS
        ),
        "latest_outcome:",
        _render_current_records(
            latest_outcome, limit=1, max_chars=PACKET_FAILURE_RECORD_MAX_CHARS
        ),
        "unresolved_contradiction:",
        (
            f"  evidence #{latest_contradiction[0]['seq']} remains open"
            if latest_contradiction
            else "[]"
        ),
        "recent_approach_outcome_pairs:",
        _approach_outcome_pairs(changes, outcomes),
    ]

    supporting_lines = ["contract_excerpt:"]
    rendered_sources = render_task_sources(task_sources)
    if rendered_sources:
        supporting_lines.append(rendered_sources)
    else:
        supporting_lines.append("[]")
    relevant_inspections = _select_relevant_inspections(
        inspections, latest_change + latest_outcome + latest_contradiction
    )
    supporting_lines.extend((
        "approach_relevant_source:",
        _render_current_records(
            relevant_inspections,
            limit=2,
            max_chars=PACKET_INSPECTION_RECORD_MAX_CHARS,
        ),
        "semantic_change:",
        _render_current_records(
            [record for record in changes if record["seq"] not in decision_record_seqs],
            limit=1,
            max_chars=PACKET_CHANGE_RECORD_MAX_CHARS,
        ),
        "discriminating_results:",
        _render_current_records(
            [record for record in outcomes if record["seq"] not in decision_record_seqs],
            limit=3,
            max_chars=PACKET_FAILURE_RECORD_MAX_CHARS,
        ),
    ))
    if agentcam_evidence.strip():
        supporting_lines.extend(
            (
                "external_runtime_evidence:",
                head_tail(agentcam_evidence, PACKET_RUNTIME_EVIDENCE_MAX_CHARS),
            )
        )
    if completion_claim.strip():
        supporting_lines.extend(
            (
                "completion_claim_context:",
                head_tail(completion_claim, STOP_ASSISTANT_MAX_CHARS),
            )
        )
    packet = "\n\n".join(
        (
            _section(
                "decision frame",
                "\n".join(decision_lines),
                DECISION_SECTION_MAX_CHARS,
            ),
            _section(
                "supporting evidence",
                "\n".join(supporting_lines),
                SUPPORTING_SECTION_MAX_CHARS,
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
