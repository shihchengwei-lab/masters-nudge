"""Small host-neutral contracts used by the Nudge runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]
NudgeStatus: TypeAlias = Literal["finding", "no_finding", "error"]
DecisionStage: TypeAlias = Literal["", "router", "generator"]
POST_TOOL_BATCH_EVENT = "PostToolBatch"


@dataclass(frozen=True)
class SessionRef:
    host: HostName
    session_id: str
    cwd: str = ""
    repo_root: str = ""


@dataclass(frozen=True)
class ToolCompleted:
    session: SessionRef
    tool_name: str
    tool_input: object = field(default_factory=dict)
    tool_output: object = ""
    failed: bool = False
    failure_known: bool = False
    mutating: bool = False
    native_event_name: str = POST_TOOL_BATCH_EVENT


@dataclass(frozen=True)
class NudgeOutcome:
    status: NudgeStatus
    finding: str = ""
    lens: str = ""
    decision_stage: DecisionStage = ""


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
