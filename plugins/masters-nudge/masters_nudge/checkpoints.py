"""Recognize observable results worth sending to the Nudge Provider."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import source_context

from .contracts import ToolCompleted


RESULT_MAX_CHARS = 5000


def _compact(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except (TypeError, ValueError):
            text = str(value or "")
    return source_context.head_tail(text.strip(), RESULT_MAX_CHARS)


def tool_event_fingerprint(event: ToolCompleted) -> str:
    raw = json.dumps(
        {
            "tool": event.tool_name,
            "input": event.tool_input,
            "output": event.tool_output,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def render_evidence_record(event: ToolCompleted) -> str:
    """Preserve the native input and result without semantic rewriting."""
    tool_input = _compact(event.tool_input)
    result = _compact(event.tool_output)
    parts: list[str] = [f"tool: {event.tool_name}"]
    post_change_sources = source_context.render_post_change_sources(
        event.session, event.mutation
    )
    if post_change_sources:
        parts.append(
            "[post-change source context]\n"
            f"{post_change_sources}\n"
            "[end post-change source context]"
        )
    if tool_input and tool_input != "{}":
        parts.append(f"actual_input:\n{tool_input}")
    if result:
        parts.append(f"result:\n{result}")
    return "\n\n".join(parts)
