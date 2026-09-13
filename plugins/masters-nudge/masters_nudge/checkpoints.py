"""Recognize observable results worth sending to the Nudge Provider."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

import source_context

from .contracts import ToolCompleted


RESULT_MAX_CHARS = 5000
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
        if event.failure_known and event.failed:
            return "failure"
        return (
            "change"
            if source_context.has_attributable_change(event.tool_input)
            else ""
        )
    if NAVIGATION_RE.search(command) or NAVIGATION_TOOL_RE.search(event.tool_name):
        return ""
    if event.failure_known and event.failed:
        return "failure"
    if MEASUREMENT_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "measurement"
    if VALIDATION_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "verification"
    return ""


def render_evidence_record(event: ToolCompleted) -> str:
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
    if category == "change":
        related_source = source_context.related_source_for_change(
            event.session.repo_root or event.session.cwd,
            event.tool_input,
        )
        if related_source:
            parts.append(f"related_source:\n{related_source}")
    if result:
        parts.append(f"result:\n{result}")
    return "\n\n".join(parts)
