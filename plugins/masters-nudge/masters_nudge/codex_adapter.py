"""Translate Codex hook payloads to the host-neutral Nudge core."""

from __future__ import annotations

from collections.abc import Mapping
import json
import re
from pathlib import Path
from typing import Any

import source_context

from . import prompting, storage
from .contracts import (
    MutationEvidence,
    SessionRef,
    ToolCompleted,
    find_git_root,
    mutation_evidence_from_input,
)
from .core import NudgeCore
from .evidence import observe_tool_batch
from .runtime import PROVIDER_TIMEOUT_SEC, active_guard


AUDIT_MARKER_KEY = "_masters_nudge"
POST_TOOL_BATCH_EVENT = "PostToolBatch"
GOAL_CONTEXT_RE = re.compile(
    r"<codex_internal_context\s+source=[\"']goal[\"'][^>]*>"
    r".*?<objective>\s*(.*?)\s*</objective>",
    re.IGNORECASE | re.DOTALL,
)
CODEX_APPLY_PATCH_OPERATIONS = (
    "*** Add File:",
    "*** Update File:",
    "*** Delete File:",
)


def _codex_mutation_evidence(
    tool_name: str, tool_input: object
) -> MutationEvidence | None:
    direct = mutation_evidence_from_input(tool_input)
    if direct is not None:
        return direct
    if tool_name != "apply_patch" or not isinstance(tool_input, Mapping):
        return None
    command = tool_input.get("command")
    if not isinstance(command, str):
        return None
    lines = command.strip().splitlines()
    if (
        len(lines) < 3
        or lines[0] != "*** Begin Patch"
        or lines[-1] != "*** End Patch"
        or not any(line.startswith(CODEX_APPLY_PATCH_OPERATIONS) for line in lines[1:-1])
    ):
        return None
    return mutation_evidence_from_input({"patch": command})


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
        tool_name = item["tool_name"]
        tool_input = item["tool_input"]
        events.append(
            ToolCompleted(
                session,
                tool_name,
                tool_input=tool_input,
                tool_output=response,
                mutation=_codex_mutation_evidence(tool_name, tool_input),
                native_event_name=event_name,
            )
        )
    return events


def build_hook_output(
    event_name: str,
    current_choice: str,
    structural_cost: str,
    direction: str,
    evidence: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": prompting.delivery_text(
                current_choice, structural_cost, direction, evidence
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
        if storage.intervention_delivered(self.data_dir, session):
            return None
        changed_paths = tuple(
            target.path
            for event in events
            if event.mutation is not None
            for target in event.mutation.targets
            if target.path
        )
        snapshot = source_context.build_decision_snapshot(
            task_contract=str(observed.turn_state.get("task_anchor") or ""),
            task_start=str(observed.turn_state.get("task_start_workspace") or ""),
            workspace_root=session.repo_root or session.cwd,
            changed_paths=changed_paths,
        )
        try:
            outcome = self.core.nudge_once(
                snapshot,
                timeout_sec=PROVIDER_TIMEOUT_SEC,
                workspace_root=session.repo_root or session.cwd,
            )
        except Exception as exc:
            self.core.log_error(f"Codex Nudge failed: {exc}")
            return None
        if outcome.decision != "intervene":
            return None
        output = build_hook_output(
            event_name,
            outcome.current_choice,
            outcome.structural_cost,
            outcome.direction,
            outcome.evidence,
        )
        output[AUDIT_MARKER_KEY] = {
            "session": session,
            "current_choice": outcome.current_choice,
            "structural_cost": outcome.structural_cost,
            "direction": outcome.direction,
            "evidence": outcome.evidence,
            "returned_via": event_name,
        }
        return output
