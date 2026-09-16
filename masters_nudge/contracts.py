"""Small host-neutral contracts used by the Nudge runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Literal, Mapping, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]


@dataclass(frozen=True)
class SessionRef:
    host: HostName
    session_id: str
    cwd: str = ""
    repo_root: str = ""


@dataclass(frozen=True)
class CompletedMutation:
    """The exact mutation reported by a completed write tool."""

    change: str = ""


def _path_target(tool_input: Mapping[object, object]) -> str:
    for key in ("path", "file_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def completed_mutation_from_input(tool_input: object) -> CompletedMutation | None:
    """Recognize only explicit top-level mutation fields; infer no semantics."""
    if not isinstance(tool_input, Mapping):
        return None
    patch = tool_input.get("patch")
    if isinstance(patch, str) and patch.strip():
        change = patch.strip()
        return CompletedMutation(change)
    diff = tool_input.get("diff")
    if isinstance(diff, str) and diff.strip():
        change = diff.strip()
        return CompletedMutation(change)
    target = _path_target(tool_input)
    if (
        target
        and isinstance(tool_input.get("old_string"), str)
        and isinstance(tool_input.get("new_string"), str)
    ):
        change = (
            f"path: {target}\n"
            f"[before]\n{tool_input['old_string']}\n[end before]\n"
            f"[after]\n{tool_input['new_string']}\n[end after]"
        )
        return CompletedMutation(change)
    if target and "content" in tool_input:
        content = tool_input.get("content")
        if not isinstance(content, str):
            return None
        change = f"path: {target}\n[content]\n{content}\n[end content]"
        return CompletedMutation(change)
    return None


@dataclass(frozen=True)
class ToolCompleted:
    session: SessionRef
    tool_name: str
    tool_input: object = field(default_factory=dict)
    tool_output: object = ""
    mutation: CompletedMutation | None = None
    native_event_name: str = "PostToolBatch"


@dataclass(frozen=True)
class Nudge:
    message: str
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
