#!/usr/bin/env python3
"""Append content-free reviewer metadata for local diagnostics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TELEMETRY_FILE = "review-telemetry.jsonl"

_RECORD_FIELDS = {
    "schema_version",
    "host",
    "session_id",
    "turn_id",
    "kind",
    "reason",
    "provider",
    "model",
    "configuration_source",
    "domain",
    "persona",
    "stage",
    "primary_lens",
    "effective_lens",
    "override_lens",
    "trigger",
    "route_source",
    "review_trigger",
    "finding_scope",
    "status",
    "input_chars",
    "latency_ms",
    "source_fingerprint",
    "usage",
}
_USAGE_FIELDS = {
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
}


def _safe_record(record: dict[str, Any], now: datetime) -> dict[str, Any]:
    safe = {key: record[key] for key in _RECORD_FIELDS if key in record}
    safe["ts"] = now.isoformat()
    safe["input_chars"] = max(0, int(safe.get("input_chars") or 0))
    safe["latency_ms"] = max(0, int(safe.get("latency_ms") or 0))
    usage = safe.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    safe["usage"] = {
        key: max(0, int(value))
        for key, value in usage.items()
        if key in _USAGE_FIELDS and isinstance(value, (int, float))
    }
    return safe


def record_review(
    base_dir: Path,
    record: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, bool]:
    """Append one sanitized metadata record without starting an experiment."""
    observed_at = now or datetime.now(timezone.utc)
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    base_dir.mkdir(parents=True, exist_ok=True)
    safe = _safe_record(record, observed_at)
    with (base_dir / TELEMETRY_FILE).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe, ensure_ascii=False) + "\n")
    return {"recorded": True}
