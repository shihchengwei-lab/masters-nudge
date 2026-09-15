"""Small host-neutral contracts used by the Nudge runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Literal, Mapping, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]
Decision: TypeAlias = Literal["intervene", "pass", "error"]


@dataclass(frozen=True)
class SessionRef:
    host: HostName
    session_id: str
    cwd: str = ""
    repo_root: str = ""


@dataclass(frozen=True)
class MutationTarget:
    path: str


@dataclass(frozen=True)
class MutationEvidence:
    """Explicit changed paths used only to wake the Provider and show current files."""

    kind: Literal["patch", "diff", "replacement", "content"]
    targets: tuple[MutationTarget, ...] = ()


_PATCH_PATH_RE = re.compile(
    r"^(?:\*\*\* (?:Add|Update|Delete) File:|\+\+\+\s+(?:b/)?)\s*(.+?)\s*$"
)
_TARGET_MAX_COUNT = 16


def _patch_targets(patch: str) -> tuple[MutationTarget, ...]:
    paths: list[MutationTarget] = []
    seen: set[str] = set()
    for line in str(patch or "").splitlines():
        match = _PATCH_PATH_RE.match(line)
        if not match:
            continue
        path = match.group(1).strip().strip('"')
        if not path or path == "/dev/null" or path in seen:
            continue
        seen.add(path)
        paths.append(MutationTarget(path))
        if len(paths) >= _TARGET_MAX_COUNT:
            break
    return tuple(paths)


def _path_target(tool_input: Mapping[object, object]) -> str:
    for key in ("path", "file_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def mutation_evidence_from_input(tool_input: object) -> MutationEvidence | None:
    """Recognize only explicit top-level mutation fields; infer no semantics."""
    if not isinstance(tool_input, Mapping):
        return None
    patch = tool_input.get("patch")
    if isinstance(patch, str) and patch.strip():
        return MutationEvidence("patch", _patch_targets(patch))
    diff = tool_input.get("diff")
    if isinstance(diff, str) and diff.strip():
        return MutationEvidence("diff", _patch_targets(diff))
    target = _path_target(tool_input)
    if (
        target
        and isinstance(tool_input.get("old_string"), str)
        and isinstance(tool_input.get("new_string"), str)
    ):
        return MutationEvidence("replacement", (MutationTarget(target),))
    if target and "content" in tool_input:
        return MutationEvidence("content", (MutationTarget(target),))
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
    decision: Decision
    current_choice: str = ""
    structural_cost: str = ""
    direction: str = ""
    evidence: tuple[str, ...] = ()


def safe_identifier(value: str, fallback: str = "unknown", limit: int = 160) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(value or ""))[:limit]
    return safe or fallback


def find_git_root(cwd: str) -> str:
    try:
        current = Path(cwd or ".").resolve()
    except OSError:
        return ""
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return str(candidate)
    return ""
