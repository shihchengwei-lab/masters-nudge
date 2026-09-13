#!/usr/bin/env python3
"""Deterministic source selection for Masters' Nudge evidence packets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


TASK_ANCHOR_MAX_CHARS = 2000
TASK_SOURCES_MAX_CHARS = 8000
TASK_SOURCE_MAX_CHARS = 6000
PACKET_MAX_CHARS = 12000
CONTRACT_SECTION_MAX_CHARS = 6000
PACKET_TASK_SOURCE_MAX_CHARS = 3200
RELATED_SOURCE_MAX_CHARS = 4000
RELATED_SOURCE_MAX_REFERENCES = 16
RELATED_SOURCE_CONTEXT_LINES = 3
RELATED_SOURCE_MAX_DEFINITION_LINES = 80
RELATED_SOURCE_MAX_FILE_BYTES = 1_000_000
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
_PATCH_PATH_RE = re.compile(
    r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to):\s*(.+?)\s*$",
    re.MULTILINE,
)
_MEMBER_ACCESS_RE = re.compile(
    r"(?<![\w$])(?:[A-Za-z_$][\w$]*\.)+[A-Za-z_$][\w$]*"
)
_CALL_IDENTIFIER_RE = re.compile(r"(?<![\w$])([A-Za-z_$][\w$]*)\s*\(")
_NON_CALL_IDENTIFIERS = frozenset(
    {
        "catch",
        "class",
        "def",
        "for",
        "function",
        "if",
        "match",
        "new",
        "return",
        "sizeof",
        "switch",
        "while",
    }
)


@dataclass(frozen=True)
class _ChangeReference:
    name: str
    kind: str


@dataclass(frozen=True)
class _SourceLink:
    reference: _ChangeReference
    resolution: str
    path: str = ""
    start: int = 0
    end: int = 0
    lines: tuple[str, ...] = ()


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


def _nested_strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Mapping):
        values: list[str] = []
        for item in value.values():
            values.extend(_nested_strings(item))
        return tuple(values)
    if isinstance(value, (list, tuple)):
        values = []
        for item in value:
            values.extend(_nested_strings(item))
        return tuple(values)
    return ()


def _changed_path_values(tool_input: Any) -> tuple[str, ...]:
    values: list[str] = []
    if isinstance(tool_input, Mapping):
        for key in ("path", "file_path"):
            path = tool_input.get(key)
            if isinstance(path, str) and path.strip():
                values.append(path.strip())
    for text in _nested_strings(tool_input):
        values.extend(_PATCH_PATH_RE.findall(text))
    return tuple(dict.fromkeys(values))


def changed_paths_for_change(
    workspace_root: str, tool_input: Any
) -> tuple[str, ...]:
    """Return changed paths that resolve inside the current workspace."""
    if not str(workspace_root or "").strip():
        return ()
    try:
        root = Path(workspace_root).resolve()
    except (OSError, RuntimeError):
        return ()
    paths: list[str] = []
    for value in _changed_path_values(tool_input):
        try:
            raw_path = Path(value)
            candidate = (
                raw_path.resolve()
                if raw_path.is_absolute()
                else (root / raw_path).resolve()
            )
            relative = candidate.relative_to(root).as_posix()
        except (OSError, RuntimeError, ValueError):
            continue
        if relative != "." and relative not in paths:
            paths.append(relative)
    return tuple(paths)


def has_attributable_change(tool_input: Any) -> bool:
    """Return whether a mutation input contains content attributable to this call."""
    if isinstance(tool_input, str):
        return bool(tool_input.strip())
    if isinstance(tool_input, Mapping):
        for key, value in tool_input.items():
            if key in {"path", "file_path"}:
                continue
            if key in {"patch", "command", "cmd"} and isinstance(value, str):
                text = value.strip()
                if not text:
                    continue
                if key != "patch" or _patch_change_lines(text) or not _PATCH_PATH_RE.search(text):
                    return True
            elif key in {
                "old_string",
                "new_string",
                "content",
                "text",
                "diff",
            }:
                if any(part.strip() for part in _nested_strings(value)):
                    return True
            elif isinstance(value, (Mapping, list, tuple)):
                if has_attributable_change(value):
                    return True
        return False
    if isinstance(tool_input, (list, tuple)):
        return any(has_attributable_change(value) for value in tool_input)
    return False


def _patch_change_lines(text: str) -> tuple[str, ...]:
    return tuple(
        line[1:]
        for line in str(text or "").splitlines()
        if len(line) > 1
        and line[0] in {"+", "-"}
        and not line.startswith(("+++", "---"))
    )


def _change_fragments(tool_input: Any) -> tuple[str, ...]:
    if isinstance(tool_input, str):
        changed = _patch_change_lines(tool_input)
        return changed or (tool_input,)
    if isinstance(tool_input, Mapping):
        fragments: list[str] = []
        for key, value in tool_input.items():
            if key in {"path", "file_path"}:
                continue
            if key in {"patch", "command", "cmd"} and isinstance(value, str):
                fragments.extend(_patch_change_lines(value))
            elif key in {"old_string", "new_string", "content", "text", "diff"}:
                fragments.extend(_nested_strings(value))
            elif isinstance(value, (Mapping, list, tuple)):
                fragments.extend(_change_fragments(value))
        return tuple(fragments)
    if isinstance(tool_input, (list, tuple)):
        fragments = []
        for value in tool_input:
            fragments.extend(_change_fragments(value))
        return tuple(fragments)
    return ()


def _added_change_fragments(tool_input: Any) -> tuple[str, ...]:
    if isinstance(tool_input, str):
        return tuple(
            line[1:]
            for line in tool_input.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
    if isinstance(tool_input, Mapping):
        fragments: list[str] = []
        for key, value in tool_input.items():
            if key in {"path", "file_path", "old_string"}:
                continue
            if key in {"patch", "command", "cmd", "diff"} and isinstance(value, str):
                fragments.extend(_added_change_fragments(value))
            elif key in {"new_string", "content", "text"}:
                fragments.extend(_nested_strings(value))
            elif isinstance(value, (Mapping, list, tuple)):
                fragments.extend(_added_change_fragments(value))
        return tuple(fragments)
    if isinstance(tool_input, (list, tuple)):
        fragments = []
        for value in tool_input:
            fragments.extend(_added_change_fragments(value))
        return tuple(fragments)
    return ()


def _change_references(tool_input: Any) -> tuple[tuple[_ChangeReference, ...], int]:
    fragments = _added_change_fragments(tool_input) or _change_fragments(tool_input)
    text = "\n".join(fragments)
    references: list[_ChangeReference] = []
    seen: set[tuple[str, str]] = set()
    matches: list[tuple[int, _ChangeReference]] = []
    for match in _CALL_IDENTIFIER_RE.finditer(text):
        name = match.group(1)
        if name not in _NON_CALL_IDENTIFIERS and len(name) >= 3:
            matches.append((match.start(), _ChangeReference(name, "call")))
    for match in _MEMBER_ACCESS_RE.finditer(text):
        name = match.group(0)
        if name.count(".") >= 2:
            matches.append((match.start(), _ChangeReference(name, "owner")))
    for _position, reference in sorted(matches, key=lambda item: item[0]):
        key = (reference.name, reference.kind)
        if key in seen:
            continue
        seen.add(key)
        references.append(reference)
    omitted = max(0, len(references) - RELATED_SOURCE_MAX_REFERENCES)
    return tuple(references[:RELATED_SOURCE_MAX_REFERENCES]), omitted


def _identifier_aliases(identifier: str) -> tuple[str, ...]:
    parts = identifier.split(".")
    if len(parts) < 3:
        return (identifier,)
    return tuple(".".join(parts[index:]) for index in range(len(parts) - 1))


def _identifier_in_text(identifier: str, text: str) -> bool:
    return any(alias in text for alias in _identifier_aliases(identifier))


def _call_definition_strength(identifier: str, line: str) -> int:
    escaped = re.escape(identifier)
    explicit = (
        rf"\b(?:async\s+)?(?:function|def|class)\s+{escaped}\b",
        rf"\b(?:const|let|var)\s+{escaped}\s*=",
        rf"\b(?:self|this|_self)\.{escaped}\s*=",
    )
    if any(re.search(pattern, line) for pattern in explicit):
        return 2
    method = re.compile(
        rf"^\s*(?:(?:public|private|protected|static|async|override|virtual|final)\s+)*"
        rf"{escaped}\s*(?:<[^>]+>)?\([^)]*\)\s*(?::[^{{]+)?\s*{{\s*$"
    )
    return 1 if method.search(line) else 0


def _owner_occurrence_score(identifier: str, line: str) -> tuple[int, int]:
    aliases = tuple(
        alias for alias in _identifier_aliases(identifier) if alias in line
    )
    if not aliases:
        return 0, 0
    first_occurrence = min(line.index(alias) for alias in aliases)
    assignments = tuple(re.finditer(r"(?<![=!<>])=(?!=|>)", line))
    strength = 2 if any(match.start() < first_occurrence for match in assignments) else 1
    specificity = max(alias.count(".") + 1 for alias in aliases)
    return strength, specificity


def _source_window(
    lines: list[str], index: int, reference_kind: str
) -> tuple[int, int]:
    start = max(0, index - RELATED_SOURCE_CONTEXT_LINES)
    fallback_end = min(len(lines), index + RELATED_SOURCE_CONTEXT_LINES + 1)
    if reference_kind != "call":
        return start, fallback_end

    limit = min(len(lines), index + RELATED_SOURCE_MAX_DEFINITION_LINES)
    declaration = lines[index]
    if "{" in declaration:
        depth = 0
        opened = False
        for position in range(index, limit):
            depth += lines[position].count("{") - lines[position].count("}")
            opened = opened or "{" in lines[position]
            if opened and depth <= 0:
                return start, position + 1

    stripped = declaration.lstrip()
    if re.match(r"(?:async\s+)?(?:def|class)\s+", stripped):
        indentation = len(declaration) - len(stripped)
        for position in range(index + 1, limit):
            candidate = lines[position]
            if not candidate.strip():
                continue
            candidate_indent = len(candidate) - len(candidate.lstrip())
            if candidate_indent <= indentation:
                return start, position
        return start, limit
    return start, fallback_end


def _resolve_reference(
    reference: _ChangeReference,
    files: tuple[tuple[str, list[str]], ...],
    added_lines: frozenset[str],
) -> _SourceLink:
    matches: list[tuple[int, int, str, int, list[str]]] = []
    for relative, lines in files:
        for index, line in enumerate(lines):
            if line.strip() in added_lines:
                continue
            if reference.kind == "call":
                strength = _call_definition_strength(reference.name, line)
                if not strength:
                    continue
                specificity = 1
            else:
                strength, specificity = _owner_occurrence_score(reference.name, line)
                if not strength:
                    continue
            start, end = _source_window(lines, index, reference.kind)
            matches.append((strength, specificity, relative, start, lines[start:end]))
    if not matches:
        return _SourceLink(reference, "unresolved")
    matches.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
    _strength, _specificity, relative, start, lines = matches[0]
    return _SourceLink(
        reference,
        "resolved",
        relative,
        start,
        start + len(lines),
        tuple(lines),
    )


def _added_change_lines(tool_input: Any) -> frozenset[str]:
    added: set[str] = set()
    if isinstance(tool_input, Mapping):
        new_string = tool_input.get("new_string")
        if isinstance(new_string, str):
            added.update(
                line.strip() for line in new_string.splitlines() if line.strip()
            )
    for text in _nested_strings(tool_input):
        for line in text.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:].strip()
                if content:
                    added.add(content)
    return frozenset(added)


def _workspace_text_file(root: Path, value: str) -> tuple[str, list[str]] | None:
    try:
        raw_path = Path(value)
        candidate = (
            raw_path.resolve()
            if raw_path.is_absolute()
            else (root / raw_path).resolve()
        )
        relative = candidate.relative_to(root).as_posix()
        if (
            not candidate.is_file()
            or candidate.stat().st_size > RELATED_SOURCE_MAX_FILE_BYTES
        ):
            return None
        raw = candidate.read_bytes()
    except (OSError, RuntimeError, ValueError):
        return None
    if b"\0" in raw:
        return None
    return relative, raw.decode("utf-8", errors="replace").splitlines()


def related_source_for_change(workspace_root: str, tool_input: Any) -> str:
    """Resolve bounded changed-file source links for direct change dependencies."""
    if not str(workspace_root or "").strip():
        return ""
    try:
        root = Path(workspace_root).resolve()
    except (OSError, RuntimeError):
        return ""
    references, omitted = _change_references(tool_input)
    if not references:
        return ""
    added_lines = _added_change_lines(tool_input)
    files: list[tuple[str, list[str]]] = []
    for value in changed_paths_for_change(str(root), tool_input):
        resolved = _workspace_text_file(root, value)
        if resolved is not None:
            files.append(resolved)
    links = tuple(
        _resolve_reference(reference, tuple(files), added_lines)
        for reference in references
    )
    coverage = f"coverage: references={len(links)} omitted={omitted}"
    blocks: list[str] = [coverage]
    for link in links:
        block = (
            f"reference: {link.reference.name}\n"
            f"kind: {link.reference.kind}\n"
            f"resolution: {link.resolution}"
        )
        if link.resolution == "resolved":
            numbered = "\n".join(
                f"{line_number}: {line}"
                for line_number, line in enumerate(link.lines, start=link.start + 1)
            )
            block += (
                f"\nsource: {link.path}:lines {link.start + 1}-{link.end}\n"
                f"{numbered}"
            )
        blocks.append(block)
    separators = 2 * (len(blocks) - 1)
    coverage_budget = len(coverage)
    link_budget = max(
        1,
        (RELATED_SOURCE_MAX_CHARS - coverage_budget - separators) // len(links),
    )
    bounded = [coverage, *(head_tail(block, link_budget) for block in blocks[1:])]
    return "\n\n".join(bounded)[:RELATED_SOURCE_MAX_CHARS]


def render_task_sources(task_sources: Any) -> str:
    if isinstance(task_sources, Mapping):
        parts = [
            f"source: {name}\n{head_tail(str(content), PACKET_TASK_SOURCE_MAX_CHARS)}"
            for name, content in task_sources.items()
            if str(name).strip() and str(content).strip()
        ]
        return head_tail("\n\n".join(parts), TASK_SOURCES_MAX_CHARS)
    return head_tail(str(task_sources or ""), TASK_SOURCES_MAX_CHARS)


def _ordered_results(evidence_records: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence_records, (list, tuple)):
        return []
    selected: list[dict[str, Any]] = []
    for record in evidence_records:
        if not isinstance(record, Mapping):
            continue
        category = str(record.get("category") or "observation")
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
    selected.sort(key=lambda record: record["seq"])
    return selected


def _render_result_records(
    records: list[dict[str, Any]], max_chars: int
) -> str:
    if not records:
        return "[]"
    labels = [
        f"[tool result seq={record['seq']} category={record['category']}]"
        for record in records
    ]
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
    task_sources: Any = "",
    evidence_records: Any = None,
) -> str:
    return _build_packet(
        task_anchor=task_anchor,
        task_sources=task_sources,
        evidence_records=evidence_records,
    )
