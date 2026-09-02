"""Recognize observable results worth offering to one Nudge Lens."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import source_context

from .contracts import ToolCompleted


RESULT_MAX_CHARS = 5000
CHANGE_MAX_CHARS = 2200
VALIDATION_RE = re.compile(
    r"\b(?:pytest|unittest|vitest|jest|eslint|mocha|node\s+--test|"
    r"npx\s+(?:eslint|mocha|jest|vitest)|cargo\s+test|go\s+test|dotnet\s+test|"
    r"flutter\s+test|(?:npm|pnpm|yarn)\s+(?:run\s+)?(?:test|lint)|"
    r"build|verify)\b",
    re.IGNORECASE,
)
MEASUREMENT_RE = re.compile(r"\b(?:benchmark|bench|profile|trace)\b", re.IGNORECASE)
FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b|\btests? failed\b|"
    r"Traceback \(most recent call last\):|"
    r"\b(?:AssertionError|ImportError|TypeError|RuntimeError|SyntaxError):",
    re.IGNORECASE,
)
NAVIGATION_RE = re.compile(
    r"^(?:rg|grep|find|ls|dir|sed|head|tail|type|cat|get-content|get-childitem|"
    r"read|open|view|search)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class WorkspaceState:
    snapshot: str
    revision_signature: str


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _compact(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except (TypeError, ValueError):
            text = str(value or "")
    return source_context.head_tail(text.strip(), RESULT_MAX_CHARS)


def _command(event: ToolCompleted) -> str:
    if isinstance(event.tool_input, dict):
        return str(
            event.tool_input.get("command")
            or event.tool_input.get("cmd")
            or event.tool_input.get("patch")
            or ""
        ).strip()
    return str(event.tool_input or "").strip()


def evidence_category(event: ToolCompleted) -> str:
    command = _command(event)
    semantic = f"{event.tool_name} {command}"
    output = _compact(event.tool_output)
    if NAVIGATION_RE.search(command) and not (
        VALIDATION_RE.search(semantic) or MEASUREMENT_RE.search(semantic)
    ):
        return ""
    if event.failure_known and event.failed:
        return "failure"
    if MEASUREMENT_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "measurement"
    if VALIDATION_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "verification"
    if event.mutating or re.search(
        r"(?:apply_patch|file_change|write_file|edit_file|^edit$|^write$)",
        event.tool_name,
        re.IGNORECASE,
    ):
        return "change"
    return ""


def _untracked_files(cwd: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return []
    return [value for value in result.stdout.split("\0") if value] if result.returncode == 0 else []


def _untracked_state(session) -> tuple[str, list[tuple[str, str]]]:
    if not session.cwd:
        return "", []
    root = Path(session.cwd).resolve()
    paths = _untracked_files(session.cwd)
    paths.sort()
    rendered: list[str] = []
    signatures: list[tuple[str, str]] = []
    for index, relative in enumerate(paths):
        display_path = relative.replace("\\", "/")
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
            signature = _file_sha256(candidate)
        except (OSError, ValueError):
            continue
        signatures.append((display_path, signature))
        if index < 3:
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            bounded = source_context.head_tail(content, 700)
            rendered.append(f"untracked_file: {display_path}\n{bounded}")
    return "\n\n".join(rendered), signatures


def workspace_state(session) -> WorkspaceState:
    if not session.cwd:
        return WorkspaceState("", "")
    try:
        result = subprocess.run(
            ["git", "diff", "--binary", "--unified=1", "HEAD", "--"],
            cwd=session.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return WorkspaceState("", "")
    if result.returncode != 0:
        return WorkspaceState("", "")
    untracked_snapshot, untracked_signatures = _untracked_state(session)
    combined = "\n\n".join(
        value for value in (result.stdout.strip(), untracked_snapshot) if value
    )
    revision = json.dumps(
        {
            "tracked_diff": result.stdout,
            "untracked_files": untracked_signatures,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return WorkspaceState(
        source_context.head_tail(combined, CHANGE_MAX_CHARS),
        hashlib.sha256(revision).hexdigest(),
    )


def working_diff(session) -> str:
    return workspace_state(session).snapshot


def render_evidence_record(event: ToolCompleted) -> str:
    """Preserve the real command and result; do not infer semantic scope."""
    category = evidence_category(event)
    command = _command(event)
    result = _compact(event.tool_output)
    parts: list[str] = []
    if command:
        parts.append(f"actual_command:\n{source_context.head_tail(command, 1800)}")
    if result:
        parts.append(f"result:\n{result}")
    return "\n\n".join(parts)
