"""Translate Codex hook payloads to the host-neutral Nudge core."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import source_context

from . import prompting, storage
from .contracts import SessionRef, ToolCompleted, find_git_root
from .core import NudgeCore
from .evidence import observe_tool_batch
from .runtime import PROVIDER_TIMEOUT_SEC, active_guard


MUTATING_TOOLS = {"apply_patch", "file_change", "edit", "write"}
FAILURE_TEXT_RE = re.compile(
    r"^(?:process|command)\s+(?:exited|failed)[^\r\n]*?"
    r"(?:code|status)\s*[:=]?\s*(-?\d+)\b"
    r"|^exit\s+code\s*[:=]?\s*(-?\d+)\b",
    re.IGNORECASE | re.MULTILINE,
)
AUDIT_MARKER_KEY = "_masters_nudge"
POST_TOOL_BATCH_EVENT = "PostToolBatch"
GOAL_CONTEXT_RE = re.compile(
    r"<codex_internal_context\s+source=[\"']goal[\"'][^>]*>"
    r".*?<objective>\s*(.*?)\s*</objective>",
    re.IGNORECASE | re.DOTALL,
)


def _goal_from_transcript(transcript_path: str) -> str:
    if not transcript_path:
        return ""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    objective = ""
    for line in lines:
        try:
            item = json.loads(line)
        except (TypeError, ValueError):
            continue
        payload = item.get("payload") if isinstance(item, dict) else None
        if not isinstance(payload, dict) or payload.get("role") != "user":
            continue
        for block in payload.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "input_text":
                continue
            match = GOAL_CONTEXT_RE.search(str(block.get("text") or ""))
            if match:
                objective = match.group(1).strip()
    return objective


def _task_anchor(payload: dict[str, Any]) -> str:
    goal = payload.get("goal")
    objective = (
        str(goal.get("objective") or "").strip()
        if isinstance(goal, dict)
        else str(payload.get("objective") or "").strip()
    )
    if not objective:
        objective = _goal_from_transcript(str(payload.get("transcript_path") or ""))
    prompt = str(payload.get("prompt") or "").strip()
    if objective and prompt and prompt != objective:
        return f"Goal:\n{objective}\n\nCurrent request:\n{prompt}"
    return objective or prompt


def _session(payload: dict[str, Any]) -> SessionRef:
    cwd = str(payload.get("cwd") or "")
    return SessionRef(
        "codex_cli",
        str(payload.get("session_id") or "unknown"),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )


def _structured_failure_signal(value: Any) -> tuple[bool, bool]:
    if isinstance(value, dict):
        known = failed = False
        for key, item in value.items():
            normalized = str(key).lower().replace("_", "")
            if normalized in {"exitcode", "returncode"}:
                try:
                    failed = failed or int(item) != 0
                    known = True
                except (TypeError, ValueError):
                    pass
            elif normalized in {"iserror", "failed"} and isinstance(item, bool):
                known, failed = True, failed or item
            elif normalized == "success" and isinstance(item, bool):
                known, failed = True, failed or not item
            if isinstance(item, (dict, list)):
                child_known, child_failed = _structured_failure_signal(item)
                known, failed = known or child_known, failed or child_failed
        return known, failed
    if isinstance(value, list):
        values = [_structured_failure_signal(item) for item in value]
        return any(item[0] for item in values), any(item[1] for item in values)
    return False, False


def _text_failure_signal(value: Any) -> tuple[bool, bool]:
    if isinstance(value, str):
        match = FAILURE_TEXT_RE.search(value)
        if match:
            code = next((part for part in match.groups() if part is not None), "0")
            return True, int(code) != 0
    elif isinstance(value, dict):
        values = [_text_failure_signal(item) for item in value.values()]
        return any(item[0] for item in values), any(item[1] for item in values)
    elif isinstance(value, list):
        values = [_text_failure_signal(item) for item in value]
        return any(item[0] for item in values), any(item[1] for item in values)
    return False, False


def _failure_signal(value: Any) -> tuple[bool, bool]:
    structured = _structured_failure_signal(value)
    return structured if structured[0] else _text_failure_signal(value)


def normalize_tool_batch(payload: dict[str, Any]) -> list[ToolCompleted] | None:
    event_name = str(payload.get("hook_event_name") or "")
    if event_name != POST_TOOL_BATCH_EVENT:
        return []
    tool_calls = payload.get("tool_calls")
    if not isinstance(tool_calls, list):
        return None
    session = _session(payload)
    events: list[ToolCompleted] = []
    for item in tool_calls:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("tool_name"), str)
            or not item["tool_name"].strip()
            or "tool_input" not in item
            or "tool_response" not in item
        ):
            return None
        response = item["tool_response"]
        known, failed = _failure_signal(response)
        tool_name = item["tool_name"]
        events.append(
            ToolCompleted(
                session,
                tool_name,
                tool_input=item["tool_input"],
                tool_output=response,
                failed=failed,
                failure_known=known,
                mutating=tool_name.lower().split("__")[-1] in MUTATING_TOOLS,
                native_event_name=event_name,
            )
        )
    return events


def build_hook_output(
    event_name: str, principle: str, anchor: str, relationship: str
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": prompting.delivery_text(
                principle, anchor, relationship
            ),
        }
    }


class CodexAdapter:
    def __init__(self, core: NudgeCore) -> None:
        self.core = core
        self.data_dir = core.settings.paths.data_dir

    def process(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if active_guard():
            return None
        event_name = str(payload.get("hook_event_name") or "")
        session = _session(payload)
        if event_name == "UserPromptSubmit":
            anchor = _task_anchor(payload)
            if anchor:
                storage.start_turn(self.data_dir, session, anchor)
            return None
        events = normalize_tool_batch(payload)
        if events is None:
            self.core.log_error("Codex PostToolBatch ignored: malformed tool_calls")
            return None
        if not events:
            return None
        state = storage.load_turn_state(self.data_dir, session)
        if not state.get("task_anchor"):
            anchor = _task_anchor(payload)
            if anchor:
                storage.start_turn(self.data_dir, session, anchor)
        observed = observe_tool_batch(self.data_dir, events)
        if not observed.eligible:
            return None
        packet = source_context.build_checkpoint_packet(
            task_anchor=str(observed.turn_state.get("task_anchor") or ""),
            task_sources=observed.turn_state.get("task_sources") or {},
            evidence_records=list(observed.batch_records),
        )
        review_input = prompting.build_review_input(
            packet,
            storage.read_recent_returned_nudges(
                self.data_dir,
                session,
                limit=3,
            ),
        )
        try:
            outcome = self.core.nudge_once(
                review_input,
                timeout_sec=PROVIDER_TIMEOUT_SEC,
            )
        except Exception as exc:
            self.core.log_error(f"Codex Nudge failed: {exc}")
            return None
        if outcome.status != "finding" or not outcome.relationship:
            return None
        output = build_hook_output(
            event_name,
            outcome.principle,
            outcome.anchor,
            outcome.relationship,
        )
        output[AUDIT_MARKER_KEY] = {
            "session": session,
            "principle": outcome.principle,
            "anchor": outcome.anchor,
            "relationship": outcome.relationship,
            "returned_via": event_name,
        }
        return output
