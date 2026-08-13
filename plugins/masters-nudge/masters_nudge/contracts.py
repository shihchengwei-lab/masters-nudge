"""Stable, host-neutral contracts used by adapters and the reviewer core."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias


HostName: TypeAlias = Literal["claude_code", "codex_cli"]
ReviewKind: TypeAlias = Literal["checkpoint", "stop"]
ReviewStatus: TypeAlias = Literal["finding", "no_finding", "error"]


@dataclass(frozen=True)
class SessionRef:
    host: HostName
    session_id: str
    turn_id: str = ""
    cwd: str = ""
    repo_root: str = ""


@dataclass(frozen=True)
class PromptSubmitted:
    session: SessionRef
    prompt: str
    transcript_path: str = ""
    kind: Literal["prompt_submitted"] = "prompt_submitted"


@dataclass(frozen=True)
class ToolCompleted:
    session: SessionRef
    tool_name: str
    tool_input: object = field(default_factory=dict)
    tool_output: object = ""
    failed: bool = False
    failure_known: bool = False
    interrupted: bool = False
    mutating: bool = False
    native_event_name: str = "PostToolUse"
    kind: Literal["tool_completed"] = "tool_completed"


@dataclass(frozen=True)
class TurnStopped:
    session: SessionRef
    final_claim: str
    stop_hook_active: bool = False
    transcript_path: str = ""
    kind: Literal["turn_stopped"] = "turn_stopped"


NormalizedHookEvent: TypeAlias = PromptSubmitted | ToolCompleted | TurnStopped


@dataclass(frozen=True)
class EvidenceBundle:
    task_anchor: str = ""
    checkpoint_event: str = ""
    assistant_claim: str = ""
    tool_evidence: str = ""
    agentcam_evidence: str = ""


@dataclass(frozen=True)
class ReviewRequest:
    schema_version: int
    kind: ReviewKind
    reason: str
    session: SessionRef
    evidence: EvidenceBundle
    source_packet: str
    source_fingerprint: str
    shadow_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewOutcome:
    status: ReviewStatus
    finding: str = ""
    effective_lens: str = "general"
    provider: str = ""
    model: str = ""
    latency_ms: int = 0
    usage: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Delivery:
    text: str = ""
    reason: str = ""
    effective_lens: str = "general"
    event_name: str = ""
    is_evaluation_notice: bool = False
    timestamp: str = ""


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
