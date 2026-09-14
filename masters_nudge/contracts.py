"""Small host-neutral contracts used by the Nudge runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Literal, Mapping, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]
NudgeStatus: TypeAlias = Literal[
    "contract_warning", "taste_nudge", "no_finding", "error"
]
NudgePrinciple: TypeAlias = Literal[
    "validity", "causality", "predictability", "none"
]


@dataclass(frozen=True)
class SessionRef:
    host: HostName
    session_id: str
    cwd: str = ""
    repo_root: str = ""


@dataclass(frozen=True)
class MutationTarget:
    """An explicit file target plus bounded facts supplied by the mutation."""

    path: str
    line_hint: int = 0
    anchors: tuple[str, ...] = ()
    references: tuple[str, ...] = ()


@dataclass(frozen=True)
class MutationEvidence:
    """A Host-supplied, top-level mutation shape; never an inferred action."""

    kind: Literal["patch", "diff", "replacement", "content"]
    targets: tuple[MutationTarget, ...] = ()


_PATCH_OPERATION_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$"
)
_UNIFIED_DIFF_PATH_RE = re.compile(r"^\+\+\+\s+(?:b/)?(.+?)\s*$")
_UNIFIED_DIFF_HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)")
_TARGET_MAX_COUNT = 8
_ANCHOR_MAX_COUNT = 8
_ANCHOR_MAX_CHARS = 240
_REFERENCE_MAX_COUNT = 16
_CALLABLE_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_$])"
    r"([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)"
    r"\s*\("
)
_NON_REFERENCE_CALLS = frozenset(
    {
        "catch",
        "for",
        "if",
        "new",
        "return",
        "switch",
        "throw",
        "while",
        "with",
    }
)


def _bounded_anchors(lines: list[str]) -> tuple[str, ...]:
    anchors: list[str] = []
    seen: set[str] = set()
    for line in lines:
        value = line.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        anchors.append(value[:_ANCHOR_MAX_CHARS])
        if len(anchors) >= _ANCHOR_MAX_COUNT:
            break
    return tuple(anchors)


def _bounded_callable_references(lines: list[str]) -> tuple[str, ...]:
    """Keep callable names explicitly present anywhere in the mutation text."""
    references: list[str] = []
    seen: set[str] = set()
    for line in lines:
        for match in _CALLABLE_REFERENCE_RE.finditer(str(line or "")):
            value = match.group(1)
            if value in _NON_REFERENCE_CALLS or value in seen:
                continue
            seen.add(value)
            references.append(value)
            if len(references) >= _REFERENCE_MAX_COUNT:
                return tuple(references)
    return tuple(references)


def _patch_targets(patch: str) -> tuple[MutationTarget, ...]:
    """Extract only file paths and hunk anchors explicitly present in a patch."""
    targets: list[MutationTarget] = []
    current_path = ""
    line_hint = 0
    added_lines: list[str] = []
    context_lines: list[str] = []

    def append_current() -> None:
        nonlocal current_path, line_hint, added_lines, context_lines
        path = current_path.strip().strip('"')
        if path and path != "/dev/null" and len(targets) < _TARGET_MAX_COUNT:
            targets.append(
                MutationTarget(
                    path,
                    line_hint,
                    _bounded_anchors([*added_lines, *context_lines]),
                    _bounded_callable_references([*added_lines, *context_lines]),
                )
            )
        current_path = ""
        line_hint = 0
        added_lines = []
        context_lines = []

    for line in str(patch or "").splitlines():
        operation = _PATCH_OPERATION_RE.match(line)
        if operation:
            append_current()
            current_path = operation.group(1)
            continue
        unified_path = _UNIFIED_DIFF_PATH_RE.match(line)
        if unified_path:
            append_current()
            current_path = unified_path.group(1)
            continue
        if not current_path:
            continue
        hunk = _UNIFIED_DIFF_HUNK_RE.match(line)
        if hunk and not line_hint:
            line_hint = int(hunk.group(1))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:])
        elif line.startswith(" "):
            context_lines.append(line[1:])
    append_current()
    return tuple(targets)


def _path_target(tool_input: Mapping[object, object]) -> str:
    for key in ("path", "file_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def mutation_evidence_from_input(tool_input: object) -> MutationEvidence | None:
    """Recognize only explicit mutation fields in the native top-level input."""
    if not isinstance(tool_input, Mapping):
        return None
    patch = tool_input.get("patch")
    if isinstance(patch, str) and patch.strip():
        return MutationEvidence("patch", _patch_targets(patch))
    diff = tool_input.get("diff")
    if isinstance(diff, str) and diff.strip():
        return MutationEvidence("diff", _patch_targets(diff))
    target_path = _path_target(tool_input)
    has_path = bool(target_path)
    if (
        has_path
        and isinstance(tool_input.get("old_string"), str)
        and isinstance(tool_input.get("new_string"), str)
    ):
        new_string = str(tool_input.get("new_string") or "")
        return MutationEvidence(
            "replacement",
            (
                MutationTarget(
                    target_path,
                    anchors=_bounded_anchors(new_string.splitlines()),
                    references=_bounded_callable_references(new_string.splitlines()),
                ),
            ),
        )
    if has_path and "content" in tool_input:
        content = tool_input.get("content")
        anchors = (
            _bounded_anchors(content.splitlines())
            if isinstance(content, str)
            else ()
        )
        return MutationEvidence(
            "content",
            (
                MutationTarget(
                    target_path,
                    anchors=anchors,
                    references=(
                        _bounded_callable_references(content.splitlines())
                        if isinstance(content, str)
                        else ()
                    ),
                ),
            ),
        )
    return None


@dataclass(frozen=True)
class ToolCompleted:
    session: SessionRef
    tool_name: str
    tool_input: object = field(default_factory=dict)
    tool_output: object = ""
    mutation: MutationEvidence | None = None
    native_event_name: str = "PostToolBatch"


@dataclass(frozen=True)
class NudgeOutcome:
    status: NudgeStatus
    principle: NudgePrinciple = "none"
    anchor: str = ""
    relationship: str = ""
    evidence_seq: int = 0


def safe_identifier(value: str, fallback: str = "unknown", limit: int = 160) -> str:
    """Return a path-safe identifier without importing a host implementation."""
    import re

    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(value or ""))[:limit]
    return safe or fallback


def find_git_root(cwd: str) -> str:
    """Best-effort repository identity used as metadata, never as evidence text."""
    try:
        current = Path(cwd or ".").resolve()
    except OSError:
        return ""
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return str(candidate)
    return ""
