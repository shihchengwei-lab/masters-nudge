"""Structural JSON contracts shared by Nudge transports."""

from __future__ import annotations

import json

from .prompting import has_nudge_prefix, is_principle


def call_result(
    status: str = "error",
    principle: str = "none",
    anchor: str = "",
    relationship: str = "",
    **extra,
) -> dict:
    result = {
        "status": status,
        "principle": principle,
        "anchor": anchor,
        "relationship": relationship,
        **extra,
    }
    if status == "error" and not result.get("error_kind"):
        result["error_kind"] = "invalid_output"
    return result


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
    if obj is None or set(obj) != {
        "status",
        "principle",
        "anchor",
        "relationship",
    }:
        return call_result(raw_output=raw)
    status = obj.get("status")
    principle = obj.get("principle")
    anchor = obj.get("anchor")
    relationship = obj.get("relationship")
    if (
        not isinstance(principle, str)
        or not isinstance(anchor, str)
        or not isinstance(relationship, str)
    ):
        return call_result(raw_output=raw)
    if status == "no_finding":
        return (
            call_result("no_finding", raw_output=raw)
            if principle == "none" and not anchor and not relationship
            else call_result(raw_output=raw)
        )
    anchor = anchor.strip()
    relationship = relationship.strip()
    if (
        status != "finding"
        or not is_principle(principle)
        or not anchor
        or not relationship
        or has_nudge_prefix(relationship)
    ):
        return call_result(raw_output=raw)
    return call_result(
        "finding",
        principle=principle,
        anchor=anchor,
        relationship=relationship,
        raw_output=raw,
    )
