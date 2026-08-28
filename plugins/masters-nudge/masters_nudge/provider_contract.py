"""Small result contract shared by reviewer transports."""

from __future__ import annotations

import json
import re

import persona_config

from .prompting import MAX_REACTION_CHARS


TASTE_FINDING_RE = re.compile(r"^.+；別.+，因為.+。$")


def is_taste_finding(
    finding: object,
    max_chars: int = MAX_REACTION_CHARS,
) -> bool:
    value = str(finding or "").strip()
    return bool(
        value
        and len(value) <= max_chars
        and TASTE_FINDING_RE.fullmatch(value)
    )


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


def parse_reaction_result(
    stdout: str,
    max_chars: int = MAX_REACTION_CHARS,
    *,
    require_taste: bool = True,
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
    if not isinstance(obj, dict) or set(obj) != {
        "status",
        "effective_lens",
        "finding",
    }:
        return call_result()
    status = obj.get("status")
    effective_lens = obj.get("effective_lens")
    finding = obj.get("finding")
    if not isinstance(finding, str) or not isinstance(effective_lens, str):
        return call_result()
    if status == "no_finding":
        if effective_lens != "none" or finding:
            return call_result()
        return {
            "status": "no_finding",
            "effective_lens": "none",
            "finding": "",
        }
    if status != "finding":
        return call_result()
    if effective_lens not in persona_config.PERSONA_NAMES:
        return call_result()
    finding = finding.strip()
    if not finding or len(finding) > max_chars:
        return call_result()
    if require_taste and not is_taste_finding(finding, max_chars):
        return call_result()
    return {
        "status": "finding",
        "effective_lens": effective_lens,
        "finding": finding,
    }
