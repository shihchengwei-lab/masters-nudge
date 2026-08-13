#!/usr/bin/env python3
"""Local, content-free review telemetry and bounded shadow evaluation.

The shadow policy never changes whether a review runs. It only labels calls
that a future cost policy might skip, then closes the evaluation on a fixed
date and emits a deterministic report for manual review.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TELEMETRY_FILE = "review-telemetry.jsonl"
STATE_FILE = "shadow-evaluation.json"
REPORT_FILE = "shadow-evaluation.md"
DEFAULT_EVALUATION_DAYS = 7
DEFAULT_TARGET_CALLS = 300

_RECORD_FIELDS = {
    "schema_version",
    "host",
    "session_id",
    "turn_id",
    "kind",
    "reason",
    "provider",
    "model",
    "persona",
    "stage",
    "primary_lens",
    "effective_lens",
    "override_lens",
    "trigger",
    "route_source",
    "status",
    "input_chars",
    "latency_ms",
    "source_fingerprint",
    "shadow_candidates",
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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def configured_evaluation_days() -> int:
    return _positive_int(
        os.environ.get("MASTERS_NUDGE_SHADOW_EVALUATION_DAYS")
        or os.environ.get("BUDDY_SHADOW_EVALUATION_DAYS"),
        DEFAULT_EVALUATION_DAYS,
    )


def configured_target_calls() -> int:
    return _positive_int(
        os.environ.get("MASTERS_NUDGE_SHADOW_TARGET_CALLS")
        or os.environ.get("BUDDY_SHADOW_TARGET_CALLS"),
        DEFAULT_TARGET_CALLS,
    )


def stop_shadow_candidates(
    *, tool_evidence: str, agentcam_evidence: str, checkpoint_overlap: bool
) -> list[str]:
    """Return observation-only labels; callers must still dispatch the review."""
    candidates: list[str] = []
    if not tool_evidence.strip() and not agentcam_evidence.strip():
        candidates.append("no_new_evidence")
    if checkpoint_overlap:
        candidates.append("checkpoint_stop_overlap")
    return candidates


def _safe_record(record: dict[str, Any], now: datetime) -> dict[str, Any]:
    safe = {key: record[key] for key in _RECORD_FIELDS if key in record}
    safe["ts"] = now.isoformat()
    safe["input_chars"] = max(0, int(safe.get("input_chars") or 0))
    safe["latency_ms"] = max(0, int(safe.get("latency_ms") or 0))
    safe["shadow_candidates"] = [
        str(item)
        for item in safe.get("shadow_candidates", [])
        if isinstance(item, str) and item
    ]
    usage = safe.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    safe["usage"] = {
        key: max(0, int(value))
        for key, value in usage.items()
        if key in _USAGE_FIELDS and isinstance(value, (int, float))
    }
    return safe


def _load_state(path: Path) -> dict[str, Any] | None:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return state if isinstance(state, dict) else None


def _save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _read_window_records(path: Path, started_at: datetime, due_at: datetime) -> list[dict]:
    records: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return records
    for line in lines:
        try:
            item = json.loads(line)
            ts = _parse_iso(str(item.get("ts") or ""))
        except (TypeError, ValueError):
            continue
        if started_at <= ts <= due_at:
            records.append(item)
    return records


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = {"finding": 0, "no_finding": 0, "error": 0}
    usage_totals = {field: 0 for field in sorted(_USAGE_FIELDS)}
    candidates: dict[str, dict[str, int | str]] = {}
    kinds: dict[str, int] = {}
    reasons: dict[str, int] = {}
    models: dict[str, int] = {}
    total_input_chars = 0
    total_latency_ms = 0

    for record in records:
        status = str(record.get("status") or "error")
        if status not in statuses:
            status = "error"
        statuses[status] += 1
        for field, bucket in (
            ("kind", kinds),
            ("reason", reasons),
            ("model", models),
        ):
            label = str(record.get(field) or "unknown")
            bucket[label] = bucket.get(label, 0) + 1
        total_input_chars += int(record.get("input_chars") or 0)
        total_latency_ms += int(record.get("latency_ms") or 0)
        for key, value in (record.get("usage") or {}).items():
            if key in usage_totals and isinstance(value, (int, float)):
                usage_totals[key] += int(value)
        for name in record.get("shadow_candidates") or []:
            bucket = candidates.setdefault(
                str(name),
                {
                    "call_count": 0,
                    "finding_count": 0,
                    "no_finding_count": 0,
                    "error_count": 0,
                },
            )
            bucket["call_count"] = int(bucket["call_count"]) + 1
            key = f"{status}_count"
            bucket[key] = int(bucket[key]) + 1

    for bucket in candidates.values():
        if int(bucket["finding_count"]) > 0:
            bucket["decision"] = "shadow_fail"
        elif int(bucket["call_count"]) < 20:
            bucket["decision"] = "insufficient_candidate_samples"
        elif int(bucket["error_count"]) > 0:
            bucket["decision"] = "needs_error_review"
        else:
            bucket["decision"] = "eligible_for_manual_review"

    input_tokens = usage_totals["input_tokens"]
    cached_tokens = usage_totals["cached_input_tokens"]
    cache_ratio = round(cached_tokens / input_tokens, 4) if input_tokens else None
    return {
        "total_calls": len(records),
        "statuses": statuses,
        "usage_totals": usage_totals,
        "cached_input_ratio": cache_ratio,
        "kinds": kinds,
        "reasons": reasons,
        "models": models,
        "total_input_chars": total_input_chars,
        "average_latency_ms": round(total_latency_ms / len(records)) if records else None,
        "candidates": candidates,
    }


def _render_report(state: dict[str, Any]) -> str:
    summary = state["summary"]
    lines = [
        "# Masters’ Nudge shadow evaluation",
        "",
        f"- Status: `{state['status']}`",
        f"- Window: `{state['started_at']}` to `{state['due_at']}`",
        f"- Target calls: {state['target_calls']}",
        f"- Observed calls: {summary['total_calls']}",
        "- Enforcement: disabled; this report never enables skipping automatically",
        "",
        "## Call outcomes",
        "",
        f"- finding: {summary['statuses']['finding']}",
        f"- no_finding: {summary['statuses']['no_finding']}",
        f"- error: {summary['statuses']['error']}",
        f"- cached input ratio: {summary['cached_input_ratio']}",
        f"- input characters: {summary['total_input_chars']}",
        f"- average latency ms: {summary['average_latency_ms']}",
        "",
        "## Token usage reported by CLI",
        "",
        *[
            f"- {name}: {value}"
            for name, value in sorted(summary["usage_totals"].items())
        ],
        "",
        "## Models",
        "",
        *[
            f"- {name}: {count}"
            for name, count in sorted(summary["models"].items())
        ],
        "",
        "## Shadow candidates",
        "",
    ]
    if not summary["candidates"]:
        lines.append("No candidate calls were observed.")
    else:
        for name, bucket in sorted(summary["candidates"].items()):
            lines.append(
                f"- `{name}`: {bucket['decision']} "
                f"({bucket['call_count']} calls; {bucket['finding_count']} findings; "
                f"{bucket['error_count']} errors)"
            )
    lines.extend(
        [
            "",
            "A single finding makes that candidate `shadow_fail`. "
            "Any activation requires an explicit manual decision.",
            "",
        ]
    )
    return "\n".join(lines)


def _append_notice(
    base_dir: Path,
    session_id: str,
    state: dict[str, Any],
    now: datetime,
    *,
    log_path: Path | None = None,
) -> None:
    if not session_id:
        return
    summary = state["summary"]
    if state["status"] == "insufficient_samples":
        reaction = (
            f"Shadow 評估已到期：僅 {summary['total_calls']}/{state['target_calls']} 次，"
            "樣本不足；報告已產生，未自動延長或啟用。"
        )
    else:
        failed = sum(
            1
            for bucket in summary["candidates"].values()
            if bucket["decision"] == "shadow_fail"
        )
        reaction = (
            f"Shadow 評估已到期：{summary['total_calls']} 次 review、"
            f"{failed} 項 shadow fail；報告已產生，未自動啟用。"
        )
    entry = {
        "ts": now.isoformat(),
        "session_id": session_id,
        "kind": "evaluation_notice",
        "persona": "general",
        "reaction": reaction,
    }
    with (log_path or base_dir / f"{session_id}.log").open(
        "a", encoding="utf-8"
    ) as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_review(
    base_dir: Path,
    record: dict[str, Any],
    *,
    now: datetime | None = None,
    evaluation_days: int | None = None,
    target_calls: int | None = None,
    notice_log_path: Path | None = None,
) -> dict[str, Any]:
    """Append metadata and close the fixed shadow window when it becomes due."""
    now = now or _utc_now()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    evaluation_days = _positive_int(
        evaluation_days, configured_evaluation_days()
    )
    target_calls = _positive_int(target_calls, configured_target_calls())
    base_dir.mkdir(parents=True, exist_ok=True)

    telemetry_path = base_dir / TELEMETRY_FILE
    safe = _safe_record(record, now)
    with telemetry_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe, ensure_ascii=False) + "\n")

    state_path = base_dir / STATE_FILE
    state = _load_state(state_path)
    if state_path.exists() and state is None:
        raise ValueError(f"shadow evaluation state is invalid: {state_path}")
    if state is None:
        due_at = now + timedelta(days=evaluation_days)
        state = {
            "schema_version": 1,
            "started_at": now.isoformat(),
            "due_at": due_at.isoformat(),
            "evaluation_days": evaluation_days,
            "target_calls": target_calls,
            "status": "collecting",
            "notice_emitted": False,
        }
        _save_state(state_path, state)

    if state.get("status") != "collecting":
        return {"evaluation_due": False, "state": state}

    due_at = _parse_iso(str(state["due_at"]))
    if now < due_at:
        return {"evaluation_due": False, "state": state}

    started_at = _parse_iso(str(state["started_at"]))
    records = _read_window_records(telemetry_path, started_at, due_at)
    summary = _summarize(records)
    state["status"] = (
        "ready_for_review"
        if summary["total_calls"] >= int(state["target_calls"])
        else "insufficient_samples"
    )
    state["completed_at"] = now.isoformat()
    state["summary"] = summary
    (base_dir / REPORT_FILE).write_text(_render_report(state), encoding="utf-8")
    if not state.get("notice_emitted"):
        _append_notice(
            base_dir,
            str(safe.get("session_id") or ""),
            state,
            now,
            log_path=notice_log_path,
        )
        state["notice_emitted"] = True
    _save_state(state_path, state)
    return {"evaluation_due": True, "state": state}
