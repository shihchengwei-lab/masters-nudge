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
POST_CHANGE_SOURCE_MAX_CHARS = 4000
POST_CHANGE_SOURCE_SCAN_CHARS = 1_000_000
POST_CHANGE_CONTEXT_LINES = 6
POST_CHANGE_LINE_MAX_CHARS = 240
POST_CHANGE_TARGET_MAX_COUNT = 4
POST_CHANGE_RELATION_MAX_LINES = 16
POST_CHANGE_VALUE_REFERENCE_MAX_LINES = 4
POST_CHANGE_VALUE_CONTEXT_LINES = 3
POST_CHANGE_CALLABLE_DECLARATION_SCAN_LINES = 160
POST_CHANGE_CALLABLE_BRIDGE_MAX_LINES = 4
POST_CHANGE_STATE_REFERENCE_MAX_COUNT = 1
POST_CHANGE_PATH_MAX_LINES = 64
POST_CHANGE_INVENTORY_MAX_LINE_NUMBERS = 24
POST_CHANGE_RELATION_LINE_MAX_CHARS = 120
POST_CHANGE_LIFECYCLE_REFERENCE_MAX_COUNT = 2
POST_CHANGE_LIFECYCLE_OCCURRENCE_MAX_LINES = 12
POST_CHANGE_LIFECYCLE_OWNER_MAX_COUNT = 4
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
_QUALIFIED_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_$])"
    r"([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)+)"
    r"(?![A-Za-z0-9_$])"
)
_CALLABLE_DECLARATION_RES = (
    re.compile(r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\("),
    re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    re.compile(
        r"^\s*(?:const\s+|let\s+|var\s+)?"
        r"([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)"
        r"\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"
    ),
)
_BARE_IDENTIFIER_RE = re.compile(
    r"(?<![A-Za-z0-9_$.])([A-Za-z_$][A-Za-z0-9_$]*)(?![A-Za-z0-9_$])"
)
_NON_STATE_IDENTIFIERS = frozenset(
    {
        "as",
        "async",
        "await",
        "break",
        "case",
        "catch",
        "const",
        "continue",
        "def",
        "do",
        "else",
        "false",
        "finally",
        "for",
        "function",
        "if",
        "in",
        "instanceof",
        "let",
        "new",
        "null",
        "return",
        "switch",
        "throw",
        "true",
        "try",
        "typeof",
        "undefined",
        "var",
        "while",
        "with",
        "yield",
    }
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


def _contained_mutation_path(session: Any, target_path: str) -> Path | None:
    boundary_value = str(getattr(session, "repo_root", "") or "").strip()
    cwd_value = str(getattr(session, "cwd", "") or "").strip()
    if not boundary_value:
        boundary_value = cwd_value
    if not boundary_value:
        return None
    try:
        boundary = Path(boundary_value).resolve()
        cwd = Path(cwd_value).resolve() if cwd_value else boundary
        cwd.relative_to(boundary)
        reference = Path(str(target_path or "").strip())
        candidate = (
            reference.resolve()
            if reference.is_absolute()
            else (cwd / reference).resolve()
        )
        candidate.relative_to(boundary)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate if candidate.is_file() else None


def _source_focus_lines(lines: list[str], target: Any) -> tuple[int, ...]:
    found: set[int] = set()
    anchors = getattr(target, "anchors", ())
    if isinstance(anchors, tuple):
        for anchor in (str(value).strip() for value in anchors if str(value).strip()):
            matches: list[int] = []
            for index, line in enumerate(lines):
                value = line.strip()
                if value == anchor or (
                    len(anchor) >= 32 and value.startswith(anchor)
                ):
                    matches.append(index)
            if len(matches) == 1:
                found.add(matches[0])
    if found:
        return tuple(sorted(found))
    try:
        line_hint = int(getattr(target, "line_hint", 0) or 0)
    except (TypeError, ValueError):
        line_hint = 0
    if line_hint > 0:
        return (min(line_hint - 1, max(0, len(lines) - 1)),)
    return (0,)


def _bounded_source_line(line: str) -> str:
    return (
        line
        if len(line) <= POST_CHANGE_LINE_MAX_CHARS
        else line[:POST_CHANGE_LINE_MAX_CHARS] + "…"
    )


def _primary_source_context(lines: list[str], target: Any) -> tuple[str, set[int]]:
    ranges: list[tuple[int, int]] = []
    for focus in _source_focus_lines(lines, target):
        start = max(0, focus - POST_CHANGE_CONTEXT_LINES)
        stop = min(len(lines), focus + POST_CHANGE_CONTEXT_LINES + 1)
        if ranges and start <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], stop))
        else:
            ranges.append((start, stop))
    windows: list[str] = []
    selected: set[int] = set()
    for start, stop in ranges:
        selected.update(range(start, stop))
        numbered = "\n".join(
            f"{index + 1}: {_bounded_source_line(lines[index])}"
            for index in range(start, stop)
        )
        windows.append(f"lines {start + 1}-{stop}:\n{numbered}")
    return "\n...\n".join(windows), selected


def _reference_pattern(reference: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9_$]){re.escape(reference)}(?![A-Za-z0-9_$])"
    )


def _distance_to_lines(index: int, selected: set[int]) -> int:
    return min((abs(index - value) for value in selected), default=0)


def _data_flow_references(
    line: str, callable_references: tuple[str, ...]
) -> tuple[str, ...]:
    """Return value-like qualified names without treating enum constants as flow."""
    found: list[str] = []
    seen: set[str] = set()
    for match in _QUALIFIED_REFERENCE_RE.finditer(line):
        value = match.group(1)
        root = value.split(".", 1)[0].lstrip("_$")
        if (
            value in callable_references
            or value in seen
            or not root
            or not root[0].islower()
        ):
            continue
        seen.add(value)
        found.append(value)
    return tuple(found)


def _nearby_callable_declaration(
    lines: list[str], call_index: int
) -> tuple[str, int] | None:
    start = max(0, call_index - POST_CHANGE_CALLABLE_DECLARATION_SCAN_LINES)
    for index in range(call_index - 1, start - 1, -1):
        for pattern in _CALLABLE_DECLARATION_RES:
            match = pattern.search(lines[index])
            if match is not None:
                return match.group(1), index
    return None


def _call_reference_pattern(reference: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9_$]){re.escape(reference)}\s*\("
    )


def _assignment_pattern(reference: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9_$]){re.escape(reference)}\s*=(?!=|>)"
    )


def _state_relationship_context(
    lines: list[str],
    target_references: tuple[str, ...],
    value_focuses: list[tuple[str, list[int]]],
) -> tuple[str, ...]:
    context_indexes: set[int] = set()
    excluded = {
        reference.split(".", 1)[0]
        for reference, _ in value_focuses
    }
    candidates: list[tuple[str, int]] = []
    seen: set[str] = set()
    for _, focuses in value_focuses:
        for focus in focuses:
            start = max(0, focus - POST_CHANGE_VALUE_CONTEXT_LINES)
            stop = min(len(lines), focus + POST_CHANGE_VALUE_CONTEXT_LINES + 1)
            context_indexes.update(range(start, stop))
    for index in sorted(context_indexes):
        line = lines[index]
        for match in _BARE_IDENTIFIER_RE.finditer(line):
            value = match.group(1)
            suffix = line[match.end() :].lstrip()
            if (
                value in seen
                or value in excluded
                or value in target_references
                or value in _NON_STATE_IDENTIFIERS
                or value[:1].isupper()
                or suffix.startswith("(")
            ):
                continue
            seen.add(value)
            candidates.append((value, index))

    ranked: list[tuple[int, int, str, int, list[int]]] = []
    for order, (reference, occurrence_index) in enumerate(candidates):
        pattern = _assignment_pattern(reference)
        assignments = [
            index for index, line in enumerate(lines) if pattern.search(line)
        ]
        if assignments:
            ranked.append(
                (len(assignments), order, reference, occurrence_index, assignments)
            )
    ranked.sort()

    rendered: list[str] = []
    for _, _, reference, occurrence_index, assignments in ranked[
        :POST_CHANGE_STATE_REFERENCE_MAX_COUNT
    ]:
        assignment_index = min(
            assignments,
            key=lambda index: (abs(index - occurrence_index), index),
        )
        parts = [
            f"state reference `{reference}` at line {occurrence_index + 1}:\n"
            f"{occurrence_index + 1}: {_bounded_source_line(lines[occurrence_index])}",
            f"state assignment `{reference}` at line {assignment_index + 1}:\n"
            f"{assignment_index + 1}: {_bounded_source_line(lines[assignment_index])}",
        ]
        owner = _nearby_callable_declaration(lines, assignment_index)
        if owner is not None:
            owner_reference, declaration_index = owner
            owner_calls = [
                index
                for index, line in enumerate(lines)
                if index != declaration_index
                and _call_reference_pattern(owner_reference).search(line)
            ]
            if owner_calls:
                owner_call = min(owner_calls)
                parts.extend(
                    (
                        f"state owner declaration `{owner_reference}` at line "
                        f"{declaration_index + 1}:\n"
                        f"{declaration_index + 1}: "
                        f"{_bounded_source_line(lines[declaration_index])}",
                        f"state owner call `{owner_reference}` at line "
                        f"{owner_call + 1}:\n"
                        f"{owner_call + 1}: {_bounded_source_line(lines[owner_call])}",
                    )
                )
        rendered.append("\n\n".join(parts))
    return tuple(rendered)


def _relationship_details(
    lines: list[str], target: Any, primary_lines: set[int]
) -> dict[str, Any] | None:
    references = getattr(target, "references", ())
    if not isinstance(references, tuple) or not references:
        return None
    candidates: list[tuple[int, int, int, str]] = []
    for reference_order, raw_reference in enumerate(references):
        reference = str(raw_reference or "").strip()
        if not reference:
            continue
        pattern = _reference_pattern(reference)
        for index, line in enumerate(lines):
            if index in primary_lines or not pattern.search(line):
                continue
            values = _data_flow_references(line, references)
            if values:
                candidates.append(
                    (
                        _distance_to_lines(index, primary_lines),
                        reference_order,
                        index,
                        reference,
                    )
                )
    if not candidates:
        return None
    candidates.sort()
    _, _, direct_index, direct_reference = candidates[0]
    value_reference = _data_flow_references(
        lines[direct_index], references
    )[0]
    value_pattern = _reference_pattern(value_reference)
    value_occurrences = tuple(
        index for index, line in enumerate(lines) if value_pattern.search(line)
    )

    bridge_reference = ""
    bridge_declaration = -1
    bridge_calls: tuple[int, ...] = ()
    bridge_call = -1
    declaration = _nearby_callable_declaration(lines, direct_index)
    if declaration is not None:
        bridge_reference, bridge_declaration = declaration
        bridge_pattern = _call_reference_pattern(bridge_reference)
        bridge_calls = tuple(
            index
            for index, line in enumerate(lines)
            if index != bridge_declaration and bridge_pattern.search(line)
        )
        if bridge_calls:
            value_lines = set(value_occurrences) - {direct_index}
            bridge_call = min(
                bridge_calls,
                key=lambda index: (
                    _distance_to_lines(index, value_lines),
                    index,
                ),
            )

    value_focuses = [(value_reference, list(value_occurrences))]
    state_groups = _state_relationship_context(
        lines, references, value_focuses
    )
    state_reference = ""
    state_assignments: tuple[int, ...] = ()
    state_owner = ""
    state_owner_calls: tuple[int, ...] = ()
    if state_groups:
        state_match = re.search(r"state reference `([^`]+)`", state_groups[0])
        owner_match = re.search(r"state owner declaration `([^`]+)`", state_groups[0])
        if state_match is not None:
            state_reference = state_match.group(1)
            assignment_pattern = _assignment_pattern(state_reference)
            state_assignments = tuple(
                index
                for index, line in enumerate(lines)
                if assignment_pattern.search(line)
            )
        if owner_match is not None:
            state_owner = owner_match.group(1)
            owner_pattern = _call_reference_pattern(state_owner)
            state_owner_calls = tuple(
                index for index, line in enumerate(lines) if owner_pattern.search(line)
            )

    return {
        "direct_reference": direct_reference,
        "direct_index": direct_index,
        "direct_occurrences": tuple(
            index
            for index, line in enumerate(lines)
            if _reference_pattern(direct_reference).search(line)
        ),
        "value_reference": value_reference,
        "value_occurrences": value_occurrences,
        "bridge_reference": bridge_reference,
        "bridge_declaration": bridge_declaration,
        "bridge_calls": bridge_calls,
        "bridge_call": bridge_call,
        "state_groups": state_groups,
        "state_reference": state_reference,
        "state_assignments": state_assignments,
        "state_owner": state_owner,
        "state_owner_calls": state_owner_calls,
    }


def _inventory_entry(
    label: str,
    indexes: tuple[int, ...],
    scan_complete: bool,
) -> str:
    shown = indexes[:POST_CHANGE_INVENTORY_MAX_LINE_NUMBERS]
    line_numbers = ", ".join(str(index + 1) for index in shown) or "none"
    if scan_complete and len(shown) == len(indexes):
        coverage = f"all {len(shown)}/{len(indexes)}"
    else:
        coverage = f"showing {len(shown)}/{len(indexes)}"
    return (
        f"reference `{label}`: {coverage} same-file occurrences "
        f"at lines {line_numbers}"
    )


def _render_relation_code_range(
    lines: list[str], start: int, stop: int, max_chars: int
) -> str:
    selected = [
        (index, lines[index].strip())
        for index in range(max(0, start), min(len(lines), stop))
        if lines[index].strip()
        and not lines[index].lstrip().startswith(("//", "#", "/*", "*"))
    ]
    for line_limit in (POST_CHANGE_RELATION_LINE_MAX_CHARS, 100, 80, 60, 40):
        rendered = "\n".join(
            f"{index + 1}: "
            + (value if len(value) <= line_limit else value[:line_limit] + "…")
            for index, value in selected
        )
        if len(rendered) <= max_chars:
            return rendered
    return head_tail(rendered, max_chars)


def _selected_occurrences(indexes: tuple[int, ...], focus: int) -> tuple[int, ...]:
    if len(indexes) <= POST_CHANGE_VALUE_REFERENCE_MAX_LINES:
        return indexes
    ranked = sorted(indexes, key=lambda index: (abs(index - focus), index))
    selected = {indexes[0], indexes[-1], *ranked[:2]}
    return tuple(sorted(selected))[:POST_CHANGE_VALUE_REFERENCE_MAX_LINES]


def _render_selected_source_lines(
    lines: list[str], indexes: tuple[int, ...], max_chars: int
) -> str:
    selected = [(index, lines[index].strip()) for index in indexes]
    rendered = ""
    for line_limit in (POST_CHANGE_RELATION_LINE_MAX_CHARS, 100, 80, 60, 40, 24):
        rendered = "\n".join(
            f"{index + 1}: "
            + (value if len(value) <= line_limit else value[:line_limit] + "…")
            for index, value in selected
        )
        if len(rendered) <= max_chars:
            return rendered
    return head_tail(rendered, max_chars)


def _callable_declaration_indexes(
    lines: list[str], reference: str
) -> tuple[int, ...]:
    indexes: list[int] = []
    for index, line in enumerate(lines):
        for pattern in _CALLABLE_DECLARATION_RES:
            match = pattern.search(line)
            if match is not None and match.group(1) == reference:
                indexes.append(index)
                break
    return tuple(indexes)


def _callable_body_stop(lines: list[str], declaration_index: int) -> int:
    balance = 0
    saw_open = False
    stop_limit = min(
        len(lines),
        declaration_index + POST_CHANGE_CALLABLE_DECLARATION_SCAN_LINES,
    )
    for index in range(declaration_index, stop_limit):
        balance += lines[index].count("{") - lines[index].count("}")
        saw_open = saw_open or "{" in lines[index]
        if saw_open and balance <= 0:
            return index + 1
    return min(len(lines), declaration_index + POST_CHANGE_RELATION_MAX_LINES)


def _lifecycle_receiver(
    lines: list[str], references: tuple[str, ...]
) -> tuple[str, tuple[int, ...]] | None:
    for raw_reference in references:
        reference = str(raw_reference or "").strip()
        if "." not in reference:
            continue
        receiver = reference.rsplit(".", 1)[0]
        root = receiver.split(".", 1)[0].lstrip("_$")
        if not root or not root[0].islower():
            continue
        occurrences = tuple(
            index
            for index, line in enumerate(lines)
            if _reference_pattern(receiver).search(line)
        )
        assignments = tuple(
            index
            for index, line in enumerate(lines)
            if _assignment_pattern(receiver).search(line)
        )
        if occurrences and assignments:
            return receiver, occurrences
    return None


def _owner_call_details(
    lines: list[str], reference: str, declaration_indexes: tuple[int, ...]
) -> tuple[tuple[str, int, int], ...]:
    declaration_set = set(declaration_indexes)
    calls = [
        index
        for index, line in enumerate(lines)
        if index not in declaration_set
        and _call_reference_pattern(reference).search(line)
    ]
    details: list[tuple[str, int, int]] = []
    seen_owners: set[str] = set()
    for call_index in calls:
        owner = _nearby_callable_declaration(lines, call_index)
        if owner is None or owner[0] in seen_owners:
            continue
        seen_owners.add(owner[0])
        details.append((owner[0], owner[1], call_index))
    return tuple(details)


def _local_callable_relationships(
    lines: list[str], references: tuple[str, ...]
) -> tuple[dict[str, Any], ...]:
    ranked: list[tuple[int, int, int, dict[str, Any]]] = []
    seen: set[str] = set()
    for order, raw_reference in enumerate(references):
        reference = str(raw_reference or "").strip()
        if not reference or reference in seen:
            continue
        seen.add(reference)
        declarations = _callable_declaration_indexes(lines, reference)
        if not declarations:
            continue
        body_stop = _callable_body_stop(lines, declarations[0])
        occurrences = tuple(
            index
            for index, line in enumerate(lines)
            if _reference_pattern(reference).search(line)
        )
        owners = _owner_call_details(lines, reference, declarations)
        details = {
            "reference": reference,
            "declarations": declarations,
            "body_stop": body_stop,
            "occurrences": occurrences,
            "owners": owners,
        }
        ranked.append(
            (
                -min(len(owners), 2),
                body_stop - declarations[0],
                order,
                details,
            )
        )
    ranked.sort(key=lambda value: (value[0], value[1], value[2]))
    return tuple(
        value[3] for value in ranked[:POST_CHANGE_LIFECYCLE_REFERENCE_MAX_COUNT]
    )


def _selected_lifecycle_occurrences(
    indexes: tuple[int, ...], primary_lines: set[int]
) -> tuple[int, ...]:
    if len(indexes) <= POST_CHANGE_LIFECYCLE_OCCURRENCE_MAX_LINES:
        return indexes
    ranked = sorted(
        indexes,
        key=lambda index: (_distance_to_lines(index, primary_lines), index),
    )
    selected = {
        indexes[0],
        indexes[-1],
        *ranked[: POST_CHANGE_LIFECYCLE_OCCURRENCE_MAX_LINES - 2],
    }
    return tuple(sorted(selected))[:POST_CHANGE_LIFECYCLE_OCCURRENCE_MAX_LINES]


def _structured_lifecycle_context(
    lines: list[str],
    target: Any,
    primary_lines: set[int],
    scan_complete: bool,
    max_chars: int,
) -> str:
    references = getattr(target, "references", ())
    if not isinstance(references, tuple) or not references:
        return ""
    receiver = _lifecycle_receiver(lines, references)
    callables = _local_callable_relationships(lines, references)
    if receiver is None and not callables:
        return ""

    inventory_label = (
        "complete same-file lexical inventories"
        if scan_complete
        else "bounded same-file lexical inventories"
    )
    inventory = [f"[{inventory_label}]"]
    if receiver is not None:
        inventory.append(_inventory_entry(receiver[0], receiver[1], scan_complete))
    for details in callables:
        inventory.append(
            _inventory_entry(
                str(details["reference"]),
                details["occurrences"],
                scan_complete,
            )
        )
    inventory.append(f"[end {inventory_label}]")
    inventory_text = "\n".join(inventory)

    state_text = ""
    if receiver is not None:
        state_indexes = _selected_lifecycle_occurrences(
            receiver[1], primary_lines
        )
        state_text = (
            "[lifecycle state occurrences]\n"
            + _render_selected_source_lines(
                lines, state_indexes, max(1, (max_chars * 2) // 5)
            )
            + "\n[end lifecycle state occurrences]"
        )

    callable_groups: list[str] = []
    owners_per_callable = max(
        1,
        POST_CHANGE_LIFECYCLE_OWNER_MAX_COUNT // max(1, len(callables)),
    )
    for details in callables:
        reference = str(details["reference"])
        declaration_index = int(details["declarations"][0])
        body_stop = int(details["body_stop"])
        group = [
            f"[local callable source `{reference}`]",
            _render_relation_code_range(
                lines,
                declaration_index,
                body_stop,
                max(1, max_chars // 4),
            ),
            f"[end local callable source `{reference}`]",
        ]
        for owner_reference, owner_index, call_index in details["owners"][
            :owners_per_callable
        ]:
            group.extend(
                (
                    f"callsite owner `{owner_reference}` for `{reference}` "
                    f"at line {owner_index + 1}:",
                    f"{owner_index + 1}: {_bounded_source_line(lines[owner_index])}",
                    f"{call_index + 1}: {_bounded_source_line(lines[call_index])}",
                )
            )
        callable_groups.append("\n".join(group))

    inventory_budget = max(1, max_chars // 5)
    state_budget = max(1, (max_chars * 2) // 5)
    callable_budget = max(1, max_chars - inventory_budget - state_budget - 4)
    parts = [head_tail(inventory_text, inventory_budget)]
    if state_text:
        parts.append(head_tail(state_text, state_budget))
    if callable_groups:
        separator_size = 2 * (len(callable_groups) - 1)
        per_callable = max(
            1,
            (callable_budget - separator_size) // len(callable_groups),
        )
        parts.append(
            "\n\n".join(
                head_tail(group, per_callable) for group in callable_groups
            )
        )
    return head_tail("\n\n".join(parts), max_chars)


def _structured_relationship_context(
    lines: list[str],
    target: Any,
    primary_lines: set[int],
    scan_complete: bool,
    max_chars: int,
) -> str:
    details = _relationship_details(lines, target, primary_lines)
    if details is None:
        return ""

    inventory_label = (
        "complete same-file lexical inventories"
        if scan_complete
        else "bounded same-file lexical inventories"
    )
    inventory = [
        f"[{inventory_label}]",
        _inventory_entry(
            str(details["direct_reference"]),
            details["direct_occurrences"],
            scan_complete,
        ),
        _inventory_entry(
            str(details["value_reference"]),
            details["value_occurrences"],
            scan_complete,
        ),
    ]
    bridge_reference = str(details["bridge_reference"])
    if bridge_reference:
        bridge_indexes = tuple(
            sorted(
                {
                    int(details["bridge_declaration"]),
                    *details["bridge_calls"],
                }
            )
        )
        inventory.append(
            _inventory_entry(bridge_reference, bridge_indexes, scan_complete)
        )
    state_reference = str(details["state_reference"])
    if state_reference:
        inventory.append(
            _inventory_entry(
                state_reference + " =",
                details["state_assignments"],
                scan_complete,
            )
        )
    state_owner = str(details["state_owner"])
    if state_owner:
        inventory.append(
            _inventory_entry(
                state_owner + "()",
                details["state_owner_calls"],
                scan_complete,
            )
        )
    inventory.append(f"[end {inventory_label}]")
    inventory_text = "\n".join(inventory)

    bridge_call = int(details["bridge_call"])
    direct_index = int(details["direct_index"])
    bridge_declaration = int(details["bridge_declaration"])
    value_occurrences = [
        index
        for index in details["value_occurrences"]
        if index != direct_index
    ]

    bridge_text = ""
    if bridge_declaration >= 0:
        bridge_parts = [
            f"nearby callable declaration `{bridge_reference}` at line "
            f"{bridge_declaration + 1}:\n"
            f"{bridge_declaration + 1}: "
            f"{_bounded_source_line(lines[bridge_declaration])}"
        ]
        related_bridge_calls = [
            index
            for index in details["bridge_calls"]
            if any(
                abs(index - value_index) <= POST_CHANGE_PATH_MAX_LINES
                for value_index in value_occurrences
            )
        ]
        if not related_bridge_calls and bridge_call >= 0:
            related_bridge_calls = [bridge_call]
        for index in related_bridge_calls[:POST_CHANGE_CALLABLE_BRIDGE_MAX_LINES]:
            bridge_parts.append(
                f"callable bridge `{bridge_reference}` at line {index + 1}:\n"
                f"{index + 1}: {_bounded_source_line(lines[index])}"
            )
        bridge_text = "\n\n".join(bridge_parts)

    state_text = "\n\n".join(details["state_groups"])
    if state_text:
        state_text = (
            "[state initialization references]\n"
            + state_text
            + "\n[end state initialization references]"
        )

    selected_values = _selected_occurrences(
        details["value_occurrences"], direct_index
    )
    value_text = (
        "[selected value-flow source]\n"
        + _render_selected_source_lines(
            lines,
            selected_values,
            max(1, (max_chars * 3) // 10),
        )
        + "\n[end selected value-flow source]"
    )

    upstream_text = ""
    if bridge_call >= 0 and value_occurrences:
        related_calls = [
            index
            for index in details["bridge_calls"]
            if any(
                abs(index - value_index) <= POST_CHANGE_PATH_MAX_LINES
                for value_index in value_occurrences
            )
        ]
        related_values = [
            index
            for index in value_occurrences
            if any(
                abs(index - call_index) <= POST_CHANGE_PATH_MAX_LINES
                for call_index in related_calls
            )
        ]
        if related_calls and related_values:
            path_start = min(*related_calls, *related_values)
            path_stop = max(*related_calls, *related_values)
            if path_stop - path_start > POST_CHANGE_PATH_MAX_LINES:
                value_index, call_index = min(
                    (
                        (value_index, call_index)
                        for value_index in related_values
                        for call_index in related_calls
                    ),
                    key=lambda pair: (abs(pair[0] - pair[1]), pair),
                )
                path_start = min(value_index, call_index)
                path_stop = max(value_index, call_index)
            upstream_start = max(0, path_start - 2)
            upstream_stop = min(len(lines), path_stop + 1)
            upstream_text = (
                "[contiguous upstream-to-bridge source]\n"
                + _render_relation_code_range(
                    lines,
                    upstream_start,
                    upstream_stop,
                    max(1, (max_chars * 9) // 20),
                )
                + "\n[end contiguous upstream-to-bridge source]"
            )

    downstream_text = ""
    if bridge_declaration >= 0:
        downstream_start = min(bridge_declaration, direct_index)
        downstream_stop = max(bridge_declaration, direct_index) + 1
        if downstream_stop - downstream_start <= POST_CHANGE_PATH_MAX_LINES:
            downstream_text = (
                "[contiguous bridge-to-anchor source]\n"
                + _render_relation_code_range(
                    lines,
                    downstream_start,
                    downstream_stop,
                    max(1, max_chars // 4),
                )
                + "\n[end contiguous bridge-to-anchor source]"
            )

    inventory_budget = max(1, max_chars // 5)
    bridge_budget = max(1, (max_chars * 3) // 20)
    state_budget = max(1, (max_chars * 3) // 20)
    parts = [head_tail(inventory_text, inventory_budget)]
    if bridge_text:
        parts.append(head_tail(bridge_text, bridge_budget))
    if state_text:
        parts.append(head_tail(state_text, state_budget))
    parts.append(value_text)
    if upstream_text:
        parts.append(upstream_text)
    if downstream_text:
        parts.append(downstream_text)
    return head_tail("\n\n".join(parts), max_chars)


def _render_source_window(
    path: Path, display_path: str, target: Any, max_chars: int
) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            content = handle.read(POST_CHANGE_SOURCE_SCAN_CHARS + 1)
    except (OSError, RuntimeError):
        return ""
    if not content or "\x00" in content:
        return ""
    lines = content[:POST_CHANGE_SOURCE_SCAN_CHARS].splitlines()
    if not lines:
        return ""

    primary, primary_lines = _primary_source_context(lines, target)
    source_header = f"source: {display_path}\n"
    relationship_label = "[same-file relationship context]\n"
    relationship_end = "\n[end same-file relationship context]"
    relationship_budget = max(
        1,
        max_chars - len(source_header + relationship_label + relationship_end),
    )
    relationship = _structured_relationship_context(
        lines,
        target,
        primary_lines,
        len(content) <= POST_CHANGE_SOURCE_SCAN_CHARS,
        relationship_budget,
    )
    if not relationship:
        relationship = _structured_lifecycle_context(
            lines,
            target,
            primary_lines,
            len(content) <= POST_CHANGE_SOURCE_SCAN_CHARS,
            relationship_budget,
        )
    if not relationship:
        return head_tail(source_header + primary, max_chars)
    rendered = (
        source_header
        + relationship_label
        + relationship
        + relationship_end
    )
    return head_tail(rendered, max_chars)


def render_post_change_sources(session: Any, mutation: Any) -> str:
    """Render bounded current source only for explicit mutation targets."""
    targets = getattr(mutation, "targets", ())
    if not isinstance(targets, tuple):
        return ""
    selected_targets = targets[:POST_CHANGE_TARGET_MAX_COUNT]
    selected: list[tuple[Path, str, Any]] = []
    for target in selected_targets:
        target_path = str(getattr(target, "path", "") or "").strip()
        if not target_path:
            continue
        candidate = _contained_mutation_path(session, target_path)
        if candidate is None:
            continue
        selected.append((candidate, target_path, target))
    if not selected:
        return ""
    separators_size = 2 * (len(selected) - 1)
    per_source = max(
        1,
        (POST_CHANGE_SOURCE_MAX_CHARS - separators_size) // len(selected),
    )
    rendered: list[str] = []
    for candidate, target_path, target in selected:
        source_window = _render_source_window(
            candidate, target_path, target, per_source
        )
        if source_window:
            rendered.append(source_window)
    if not rendered:
        return ""
    return head_tail("\n\n".join(rendered), POST_CHANGE_SOURCE_MAX_CHARS)


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
