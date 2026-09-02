"""Structural JSON contracts shared by Nudge transports."""

from __future__ import annotations

import json

from .lenses import LENSES
from .prompting import MAX_NUDGE_CHARS


def call_result(
    status: str = "error",
    finding: str = "",
    lens: str = "none",
    **extra,
) -> dict:
    result = {"status": status, "lens": lens, "finding": finding, **extra}
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


def parse_nudge_result(stdout: str, max_chars: int = MAX_NUDGE_CHARS) -> dict:
    obj, raw = _decode_object(stdout)
    if obj is None or set(obj) != {"status", "lens", "finding"}:
        return call_result(raw_output=raw)
    status = obj.get("status")
    lens = obj.get("lens")
    finding = obj.get("finding")
    if not isinstance(lens, str) or not isinstance(finding, str):
        return call_result(raw_output=raw)
    if status == "no_finding":
        return (
            call_result("no_finding", lens="none", raw_output=raw)
            if lens == "none" and not finding
            else call_result(raw_output=raw)
        )
    finding = finding.strip()
    if (
        status != "finding"
        or lens not in LENSES
        or not finding
        or len(finding) > max_chars
    ):
        return call_result(raw_output=raw)
    return call_result("finding", finding, lens, raw_output=raw)
