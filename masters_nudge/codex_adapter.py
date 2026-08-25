"""Codex CLI hook adapter for the shared Masters' Nudge reviewer core."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import source_context

from . import prompting, storage
from .contracts import (
    PromptSubmitted,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
    TurnStopped,
    find_git_root,
)
from .core import ReviewCore
from .evidence import (
    finish_tool_review,
    observe_tool_event,
    read_latest_agentcam_report,
)
from .runtime import active_guard


MUTATING_TOOLS = {
    "apply_patch",
    "Bash",
    "PowerShell",
    "shell_command",
    "exec_command",
}
FAILURE_TEXT_RE = re.compile(
    r"(?:process|command)\s+(?:exited|failed).*?(?:code|status)\s*[:=]?\s*(-?\d+)"
    r"|(?:exit|status)\s*code\s*[:=]\s*(-?\d+)",
    re.IGNORECASE | re.DOTALL,
)

DELIVERY_MARKER_KEY = "_masters_nudge_delivery"
GOAL_CONTEXT_RE = re.compile(
    r"<codex_internal_context\s+source=[\"']goal[\"'][^>]*>"
    r".*?<objective>\s*(.*?)\s*</objective>",
    re.IGNORECASE | re.DOTALL,
)


def _goal_from_transcript(transcript_path: str) -> str:
    if not transcript_path:
        return ""
    try:
        raw = Path(transcript_path).read_text(encoding="utf-8")
    except OSError:
        return ""
    objective = ""
    for line in raw.splitlines():
        try:
            item = json.loads(line)
        except (TypeError, ValueError):
            continue
        payload = item.get("payload") if isinstance(item, dict) else None
        if not isinstance(payload, dict) or payload.get("role") != "user":
            continue
        content = payload.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "input_text":
                continue
            match = GOAL_CONTEXT_RE.search(str(block.get("text") or ""))
            if match:
                objective = match.group(1).strip()
    return objective


def _prompt_text(payload: dict[str, Any]) -> str:
    prompt = str(payload.get("prompt") or "").strip()
    if prompt:
        return prompt
    goal = payload.get("goal")
    if isinstance(goal, dict):
        objective = str(goal.get("objective") or "").strip()
        if objective:
            return objective
    objective = str(payload.get("objective") or "").strip()
    if objective:
        return objective
    return _goal_from_transcript(str(payload.get("transcript_path") or ""))


def _with_delivery_marker(
    output: dict[str, Any], session: SessionRef, timestamp: str, *, event_seq: int = 0,
    event_name: str = "", claim_token: str = "",
) -> dict[str, Any]:
    if timestamp:
        output[DELIVERY_MARKER_KEY] = {
            "session": session,
            "timestamp": timestamp,
            "event_seq": int(event_seq or 0),
            "event_name": event_name,
            "claim_token": claim_token,
        }
    return output


def _session(payload: dict[str, Any]) -> SessionRef:
    cwd = str(payload.get("cwd") or "")
    return SessionRef(
        "codex_cli",
        str(payload.get("session_id") or "unknown"),
        turn_id=str(payload.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )


def _failure_signal(value: Any) -> tuple[bool, bool]:
    """Return (known, failed) from structured Codex tool responses."""
    if isinstance(value, dict):
        known = False
        failed = False
        for key, item in value.items():
            normalized = str(key).lower().replace("_", "")
            if normalized in {"exitcode", "returncode", "statuscode"}:
                try:
                    failed = failed or int(item) != 0
                    known = True
                except (TypeError, ValueError):
                    pass
            elif normalized in {"iserror", "failed"} and isinstance(item, bool):
                known = True
                failed = failed or item
            elif normalized == "success" and isinstance(item, bool):
                known = True
                failed = failed or not item
            elif normalized == "status" and str(item).lower() in {
                "success",
                "ok",
                "failed",
                "failure",
                "error",
            }:
                known = True
                failed = failed or str(item).lower() in {
                    "failed",
                    "failure",
                    "error",
                }
            child_known, child_failed = _failure_signal(item)
            known = known or child_known
            failed = failed or child_failed
        return known, failed
    if isinstance(value, list):
        pairs = [_failure_signal(item) for item in value]
        return any(pair[0] for pair in pairs), any(pair[1] for pair in pairs)
    if isinstance(value, str):
        match = FAILURE_TEXT_RE.search(value)
        if not match:
            return False, False
        code = next((part for part in match.groups() if part is not None), "0")
        return True, int(code) != 0
    return False, False


def normalize_event(payload: dict[str, Any]):
    session = _session(payload)
    event_name = str(payload.get("hook_event_name") or "")
    if event_name == "UserPromptSubmit":
        return PromptSubmitted(
            session,
            _prompt_text(payload),
            transcript_path=str(payload.get("transcript_path") or ""),
        )
    if event_name in {"PostToolUse", "PostToolUseFailure"}:
        explicit_failure = event_name == "PostToolUseFailure"
        response = (
            payload.get("error", "")
            if explicit_failure
            else payload.get("tool_response", "")
        )
        known, failed = (
            (True, True) if explicit_failure else _failure_signal(response)
        )
        tool_name = str(payload.get("tool_name") or "unknown")
        return ToolCompleted(
            session,
            tool_name,
            tool_input=payload.get("tool_input") or {},
            tool_output=response,
            failed=failed,
            failure_known=known,
            interrupted=bool(payload.get("is_interrupt")),
            mutating=tool_name in MUTATING_TOOLS,
            native_event_name=event_name,
        )
    if event_name == "Stop":
        return TurnStopped(
            session,
            str(payload.get("last_assistant_message") or ""),
            stop_hook_active=bool(payload.get("stop_hook_active")),
            transcript_path=str(payload.get("transcript_path") or ""),
        )
    return None


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def build_hook_output(
    event_name: str,
    text: str,
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": prompting.delivery_text(text),
        }
    }


def build_stop_hook_output(text: str) -> dict[str, Any]:
    return {"decision": "block", "reason": prompting.delivery_text(text)}


class CodexAdapter:
    def __init__(self, core: ReviewCore) -> None:
        self.core = core
        self.data_dir = core.settings.paths.data_dir

    def process(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if active_guard():
            return None
        event_name = str(payload.get("hook_event_name") or "")
        if event_name in {"PostToolUse", "PostToolUseFailure"}:
            session = _session(payload)
            state = storage.load_turn_state(self.data_dir, session)
            if not state.get("task_anchor"):
                recovered_prompt = _prompt_text(payload)
                if recovered_prompt:
                    storage.start_turn(
                        self.data_dir,
                        session,
                        recovered_prompt,
                        transcript_path=str(payload.get("transcript_path") or ""),
                    )
        event = normalize_event(payload)
        if isinstance(event, PromptSubmitted):
            return self._prompt(event)
        if isinstance(event, ToolCompleted):
            return self._tool(event)
        if isinstance(event, TurnStopped):
            return self._stop(event)
        return None

    def _prompt(self, event: PromptSubmitted) -> dict[str, Any] | None:
        storage.start_turn(
            self.data_dir,
            event.session,
            event.prompt,
            transcript_path=event.transcript_path,
        )
        return None

    def _tool(self, event: ToolCompleted) -> dict[str, Any] | None:
        observed = observe_tool_event(self.data_dir, event)
        checkpoint = observed.checkpoint
        if not checkpoint:
            return None
        source_packet = source_context.build_checkpoint_packet(
            task_anchor=str(observed.turn_state.get("task_anchor") or ""),
            event_context=checkpoint["context"],
            task_sources=observed.turn_state.get("task_sources") or {},
            evidence_records=(
                observed.turn_state.get("evidence_records")
                if isinstance(observed.turn_state.get("evidence_records"), list)
                else []
            ),
        )
        request = ReviewRequest(
            schema_version=1,
            kind=observed.review_kind,
            reason=checkpoint["reason"],
            session=event.session,
            source_packet=source_packet,
            source_fingerprint=_fingerprint(
                f"{observed.review_kind}:{checkpoint.get('trigger') or checkpoint['reason']}\n"
                f"{source_packet}"
            ),
            routing_evidence=checkpoint["context"],
            source_event_seq=observed.event_seq,
            trigger=str(checkpoint.get("trigger") or checkpoint["reason"]),
            routing_concern=str(checkpoint.get("routing_concern") or ""),
        )
        try:
            outcome = self.core.review_once(
                request,
                persist_reaction=True,
                timeout_sec=self.core.settings.checkpoint_timeout_sec,
            )
        except Exception as exc:
            self.core.log_error(f"Codex checkpoint review failed: {exc}")
            return None
        finish_tool_review(
            self.data_dir,
            event,
            observed,
            review_ran=outcome is not None,
        )
        if outcome is None or outcome.status != "finding" or not outcome.finding:
            return None
        output = build_hook_output(
            event.native_event_name,
            outcome.finding,
        )
        timestamp = outcome.reaction_ts
        if not timestamp:
            return None
        claim_token = ""
        if timestamp:
            claim_token = storage.claim_delivery(
                self.data_dir, event.session, timestamp
            )
            if not claim_token:
                return None
        return _with_delivery_marker(
            output,
            event.session,
            timestamp,
            event_seq=observed.event_seq,
            event_name=event.native_event_name,
            claim_token=claim_token,
        )

    def _stop(self, event: TurnStopped) -> dict[str, Any] | None:
        progress = storage.load_progress_state(self.data_dir, event.session)
        event_seq = int(progress.get("event_seq") or 0)
        storage.observe_injected_response(
            self.data_dir,
            event.session,
            event_seq=event_seq,
            observation_kind="stop",
            observation={"assistant_claim": event.final_claim},
        )
        if event.stop_hook_active:
            return None
        state = storage.load_turn_state(self.data_dir, event.session)
        agentcam_evidence = ""
        report = read_latest_agentcam_report(
            event.session.cwd, log_error=self.core.log_error
        )
        if report and float(report["mtime"]) > storage.load_agentcam_mtime(
            self.data_dir, event.session
        ):
            agentcam_evidence = source_context.extract_agentcam_evidence(
                str(report["content"])
            )
            storage.save_agentcam_mtime(
                self.data_dir, event.session, float(report["mtime"])
            )
        task_anchor = str(state.get("task_anchor") or "")
        source_packet = source_context.build_stop_packet(
            task_anchor=task_anchor,
            last_assistant_message=event.final_claim,
            task_sources=state.get("task_sources") or {},
            evidence_records=(
                state.get("evidence_records")
                if isinstance(state.get("evidence_records"), list)
                else []
            ),
            agentcam_evidence=agentcam_evidence,
        )
        if not source_packet:
            return None
        request = ReviewRequest(
            schema_version=1,
            kind="stop",
            reason="stop",
            session=event.session,
            source_packet=source_packet,
            source_fingerprint=_fingerprint(source_packet),
        )
        try:
            outcome = self.core.review_once(request, persist_reaction=True)
        except Exception as exc:
            self.core.log_error(f"Codex stop review failed: {exc}")
            return None
        if outcome is None or outcome.status != "finding" or not outcome.finding:
            return None
        timestamp = outcome.reaction_ts
        if not timestamp:
            return None
        claim_token = storage.claim_delivery(self.data_dir, event.session, timestamp)
        if not claim_token:
            return None
        return _with_delivery_marker(
            build_stop_hook_output(outcome.finding),
            event.session,
            timestamp,
            event_seq=event_seq,
            event_name="Stop",
            claim_token=claim_token,
        )
