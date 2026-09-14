"""Small host-neutral contracts used by the Nudge runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]
NudgeStatus: TypeAlias = Literal["finding", "no_finding", "error"]
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
class MutationEvidence:
    """A Host-supplied, top-level mutation shape; never an inferred action."""

    kind: Literal["patch", "diff", "replacement", "content"]


def mutation_evidence_from_input(tool_input: object) -> MutationEvidence | None:
    """Recognize only explicit mutation fields in the native top-level input."""
    if not isinstance(tool_input, Mapping):
        return None
    patch = tool_input.get("patch")
    if isinstance(patch, str) and patch.strip():
        return MutationEvidence("patch")
    diff = tool_input.get("diff")
    if isinstance(diff, str) and diff.strip():
        return MutationEvidence("diff")
    path = tool_input.get("path")
    file_path = tool_input.get("file_path")
    has_path = (isinstance(path, str) and bool(path.strip())) or (
        isinstance(file_path, str) and bool(file_path.strip())
    )
    if (
        has_path
        and isinstance(tool_input.get("old_string"), str)
        and isinstance(tool_input.get("new_string"), str)
    ):
        return MutationEvidence("replacement")
    if has_path and "content" in tool_input:
        return MutationEvidence("content")
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
