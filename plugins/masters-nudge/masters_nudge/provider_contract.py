"""Structural result contracts shared by reviewer transports."""

from __future__ import annotations

import json

import persona_config

from .prompting import MAX_REACTION_CHARS


def call_result(
    status: str = "error",
    finding: str = "",
    effective_lens: str = "none",
    **extra,
) -> dict:
    result = {
        "status": status,
        "effective_lens": effective_lens,
        "finding": finding,
        "usage": {},
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


def parse_reaction_result(
    stdout: str,
    max_chars: int = MAX_REACTION_CHARS,
) -> dict:
    """Validate only the final Nudge's mechanical output contract."""
    obj, raw = _decode_object(stdout)
    if obj is None or set(obj) != {"status", "effective_lens", "finding"}:
        return call_result(raw_output=raw)
    status = obj.get("status")
    effective_lens = obj.get("effective_lens")
    finding = obj.get("finding")
    if not isinstance(effective_lens, str) or not isinstance(finding, str):
        return call_result(raw_output=raw)
    if status == "no_finding":
        if effective_lens != "none" or finding:
            return call_result(raw_output=raw)
        return {
            "status": "no_finding",
            "effective_lens": "none",
            "finding": "",
            "raw_output": raw,
        }
    finding = finding.strip()
    if (
        status != "finding"
        or effective_lens not in persona_config.LENS_PERSONAS
        or not finding
        or len(finding) > max_chars
    ):
        return call_result(raw_output=raw)
    return {
        "status": "finding",
        "effective_lens": effective_lens,
        "finding": finding,
        "raw_output": raw,
    }


def parse_route_result(stdout: str) -> dict:
    """Validate the Router's lens-only output contract."""
    obj, raw = _decode_object(stdout)
    if obj is None or set(obj) != {"status", "effective_lens"}:
        return call_result(raw_output=raw)
    status = obj.get("status")
    effective_lens = obj.get("effective_lens")
    if status == "no_finding" and effective_lens == "none":
        return {
            "status": "no_finding",
            "effective_lens": "none",
            "finding": "",
            "raw_output": raw,
        }
    if status == "finding" and effective_lens in persona_config.LENS_PERSONAS:
        return {
            "status": "finding",
            "effective_lens": effective_lens,
            "finding": "",
            "raw_output": raw,
        }
    return call_result(raw_output=raw)
