"""Recognize observable results worth sending to the Nudge Provider."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

import source_context

from .contracts import ToolCompleted


RESULT_MAX_CHARS = 5000
CHANGE_MAX_CHARS = 2200
VALIDATION_RE = re.compile(
    r"(?<![\\/])\b(?:pytest|unittest|vitest|jest|cargo\s+test|go\s+test|dotnet\s+test|"
    r"flutter\s+test|node\s+--test|(?:npx\s+)?borp|"
    r"npm\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|"
    r"build|verify)\b(?![\\/])",
    re.IGNORECASE,
)
MEASUREMENT_RE = re.compile(
    r"(?<![\\/])\b(?:benchmark|bench|profile|trace)\b(?![\\/])",
    re.IGNORECASE,
)
FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b|\btests? failed\b|"
    r"Traceback \(most recent call last\):|"
    r"\b(?:AssertionError|ImportError|TypeError|RuntimeError|SyntaxError):",
    re.IGNORECASE,
)
NAVIGATION_RE = re.compile(
    r"^(?:rg|grep|find|ls|dir|sed|head|tail|type|cat|get-content|read|open|view|search)\b|"
    r"^git\s+(?:diff|status|show|log)\b",
    re.IGNORECASE,
)
NAVIGATION_TOOL_RE = re.compile(
    r"(?:^|_)(?:read|view|search|find|list|glob|grep)(?:$|_)",
    re.IGNORECASE,
)
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


def tool_event_fingerprint(event: ToolCompleted) -> str:
    raw = json.dumps(
        {
            "tool": event.tool_name,
            "input": event.tool_input,
            "output": event.tool_output,
            "failed": event.failed,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def evidence_category(event: ToolCompleted) -> str:
    command = _command(event)
    semantic = f"{event.tool_name} {command}"
    output = _compact(event.tool_output)
    mutating = event.mutating or bool(
        re.search(
            r"(?:apply_patch|file_change|write_file|edit_file|^edit$|^write$)",
            event.tool_name,
            re.IGNORECASE,
        )
    )
    if mutating:
        return "failure" if event.failure_known and event.failed else "change"
    if NAVIGATION_RE.search(command) or NAVIGATION_TOOL_RE.search(event.tool_name):
        return ""
    if event.failure_known and event.failed:
        return "failure"
    if MEASUREMENT_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "measurement"
    if VALIDATION_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "verification"
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


def _requested_path(event: ToolCompleted) -> str:
    if isinstance(event.tool_input, dict):
        value = event.tool_input.get("path") or event.tool_input.get("file_path")
        if value:
            return str(value).replace("\\", "/")
    match = re.search(r"\*\*\* Add File:\s*([^\r\n]+)", _command(event))
    return match.group(1).strip().replace("\\", "/") if match else ""


def _untracked_snapshot(event: ToolCompleted) -> str:
    if not event.session.cwd:
        return ""
    root = Path(event.session.cwd).resolve()
    paths = _untracked_files(event.session.cwd)
    requested = _requested_path(event)
    paths.sort(key=lambda value: (value.replace("\\", "/") != requested, value))
    rendered: list[str] = []
    for relative in paths[:3]:
        display_path = relative.replace("\\", "/")
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        rendered.append(
            f"untracked_file: {display_path}\n"
            f"{source_context.head_tail(content, 700)}"
        )
    return "\n\n".join(rendered)


def _working_diff(event: ToolCompleted) -> str:
    if not event.session.cwd:
        return ""
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=1", "HEAD", "--"],
            cwd=event.session.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    combined = "\n\n".join(
        value for value in (result.stdout.strip(), _untracked_snapshot(event)) if value
    )
    return source_context.head_tail(combined, CHANGE_MAX_CHARS)


def render_evidence_record(
    event: ToolCompleted, *, include_current_diff: bool = True
) -> str:
    """Preserve the real command and result; do not infer semantic scope."""
    category = evidence_category(event)
    command = _command(event)
    remaining_input = event.tool_input
    if command and isinstance(event.tool_input, Mapping):
        remaining_input = {
            key: value
            for key, value in event.tool_input.items()
            if key not in {"command", "cmd", "patch"}
        }
    tool_input = _compact(remaining_input)
    result = _compact(event.tool_output)
    parts: list[str] = [f"tool: {event.tool_name}"]
    if command:
        parts.append(f"actual_command:\n{source_context.head_tail(command, 1800)}")
    if tool_input and tool_input != "{}":
        parts.append(f"actual_input:\n{tool_input}")
    if category == "change" and include_current_diff:
        related_source = source_context.related_source_for_change(
            event.session.repo_root or event.session.cwd,
            event.tool_input,
        )
        if related_source:
            parts.append(f"related_source:\n{related_source}")
        diff = _working_diff(event)
        if diff:
            parts.append(f"current_diff:\n{diff}")
    if result:
        parts.append(f"result:\n{result}")
    return "\n\n".join(parts)
