"""Structural JSON contract shared by Nudge transports."""

from __future__ import annotations

import json


_MISSING = object()


def call_result(nudge: object = _MISSING, **extra: object) -> dict:
    """Represent valid silence, one Nudge, or an internal transport error."""
    if nudge is _MISSING:
        return {"nudge": None, "error_kind": "invalid_output", **extra}
    return {"nudge": nudge, **extra}


def _decode_object(stdout: str) -> tuple[dict | None, str]:
    raw = str(stdout or "").strip()
    if not raw:
        return None, raw
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return None, raw
    if isinstance(value, dict) and "structured_output" in value:
        value = value.get("structured_output")
    return (value if isinstance(value, dict) else None), raw


def parse_nudge_result(stdout: str) -> dict:
    obj, raw = _decode_object(stdout)
    if obj is None or set(obj) != {"nudge"}:
        return call_result(raw_output=raw)
    nudge = obj.get("nudge")
    if nudge is None:
        return call_result(None, raw_output=raw)
    if not isinstance(nudge, dict) or set(nudge) != {"message", "evidence"}:
        return call_result(raw_output=raw)
    message = nudge.get("message")
    evidence = nudge.get("evidence")
    if (
        not isinstance(message, str)
        or not message.strip()
        or not isinstance(evidence, list)
        or not evidence
        or any(not isinstance(item, str) or not item.strip() for item in evidence)
    ):
        return call_result(raw_output=raw)
    return call_result(
        {
            "message": message.strip(),
            "evidence": [item.strip() for item in evidence],
        },
        raw_output=raw,
    )
