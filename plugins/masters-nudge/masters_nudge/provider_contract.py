"""Small result contract shared by reviewer transports."""

from __future__ import annotations

import json

from .prompting import MAX_REACTION_CHARS


def call_result(status: str = "error", finding: str = "", **extra) -> dict:
    result = {"status": status, "finding": finding, "usage": {}, **extra}
    if status == "error" and not result.get("error_kind"):
        result["error_kind"] = "invalid_output"
    return result


def parse_reaction_result(
    stdout: str, max_chars: int = MAX_REACTION_CHARS
) -> dict:
    stdout = str(stdout or "").strip()
    if not stdout:
        return call_result()
    try:
        obj = json.loads(stdout)
    except (TypeError, ValueError):
        return call_result()
    if isinstance(obj, dict) and "structured_output" in obj:
        obj = obj.get("structured_output")
    if not isinstance(obj, dict) or set(obj) != {"status", "finding"}:
        return call_result()
    status = obj.get("status")
    finding = obj.get("finding")
    if not isinstance(finding, str):
        return call_result()
    if status == "no_finding":
        return {"status": "no_finding", "finding": ""}
    if status != "finding":
        return call_result()
    finding = finding.strip()
    if not finding or len(finding) > max_chars:
        return call_result()
    return {"status": "finding", "finding": finding}
