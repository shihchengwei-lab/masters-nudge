"""Structural JSON contracts shared by Nudge transports."""

from __future__ import annotations

import json


def call_result(
    decision: str = "error",
    current_choice: str = "",
    structural_cost: str = "",
    direction: str = "",
    evidence: list[str] | None = None,
    **extra,
) -> dict:
    result = {
        "decision": decision,
        "current_choice": current_choice,
        "structural_cost": structural_cost,
        "direction": direction,
        "evidence": list(evidence or []),
        **extra,
    }
    if decision == "error" and not result.get("error_kind"):
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
    required = {"decision", "current_choice", "structural_cost", "direction", "evidence"}
    if obj is None or set(obj) != required:
        return call_result(raw_output=raw)
    decision = obj.get("decision")
    current_choice = obj.get("current_choice")
    structural_cost = obj.get("structural_cost")
    direction = obj.get("direction")
    evidence = obj.get("evidence")
    if (
        not isinstance(current_choice, str)
        or not isinstance(structural_cost, str)
        or not isinstance(direction, str)
        or not isinstance(evidence, list)
        or any(not isinstance(item, str) for item in evidence)
    ):
        return call_result(raw_output=raw)
    fields = (current_choice.strip(), structural_cost.strip(), direction.strip())
    cleaned_evidence = [item.strip() for item in evidence if item.strip()]
    if decision == "pass":
        return (
            call_result("pass", raw_output=raw)
            if not any(fields) and not cleaned_evidence
            else call_result(raw_output=raw)
        )
    if decision != "intervene" or not all(fields) or not cleaned_evidence:
        return call_result(raw_output=raw)
    return call_result(
        "intervene",
        current_choice=fields[0],
        structural_cost=fields[1],
        direction=fields[2],
        evidence=cleaned_evidence,
        raw_output=raw,
    )
