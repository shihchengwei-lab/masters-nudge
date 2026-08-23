"""Codex CLI hook adapter for the shared Masters' Nudge reviewer core."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

import source_context

from . import checkpoints, storage
from .contracts import (
    PromptSubmitted,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
    TurnStopped,
    find_git_root,
)
from .core import ReviewCore
from .evidence import read_latest_agentcam_report
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


def _pending_output(
    data_dir: Path,
    event_name: str,
    session: SessionRef,
    *,
    event_seq: int = 0,
    current_source_fingerprint: str = "",
) -> tuple[dict[str, Any] | None, bool]:
    pending = storage.latest_pending(
        data_dir,
        session,
        current_event_seq=event_seq,
        current_source_fingerprint=current_source_fingerprint,
    )
    if not pending:
        return None, False
    text = str(pending.get("reaction") or "").strip()
    timestamp = str(pending.get("ts") or "")
    if not text or not timestamp:
        return None, False
    claim_token = storage.claim_delivery(data_dir, session, timestamp)
    if not claim_token:
        return None, True
    output = build_hook_output(event_name, text)
    return (
        _with_delivery_marker(
            output,
            session,
            timestamp,
            event_seq=event_seq,
            event_name=event_name,
            claim_token=claim_token,
        ),
        False,
    )


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


def _tool_record(event: ToolCompleted) -> str:
    state = "failure" if event.failure_known and event.failed else "result"
    return (
        f"[tool {event.tool_name}]\n"
        f"input: {checkpoints.compact_json(event.tool_input)}\n"
        f"{state}: {checkpoints.compact_json(event.tool_output)}"
    )


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def build_hook_output(
    event_name: str,
    text: str,
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    }


class CodexAdapter:
    def __init__(
        self,
        core: ReviewCore,
        *,
        schedule_strategy: Callable[[dict[str, Any]], bool] | None = None,
    ) -> None:
        self.core = core
        self.data_dir = core.settings.paths.data_dir
        self.schedule_strategy = schedule_strategy

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
        output, _delivery_busy = _pending_output(
            self.data_dir,
            "UserPromptSubmit",
            event.session,
        )
        return output

    def _tool(self, event: ToolCompleted) -> dict[str, Any] | None:
        journal = storage.append_tool_evidence(
            self.data_dir, event.session, _tool_record(event)
        )
        changed_lines = (
            checkpoints.get_changed_line_count(event.session.cwd)
            if event.mutating and event.session.cwd
            else None
        )
        transition, objective = checkpoints.goal_transition(event)
        progress = storage.record_tool_progress(
            self.data_dir,
            event.session,
            tool_name=event.tool_name,
            command_family=checkpoints.command_family(event),
            failed=event.failure_known and event.failed,
            mutating=event.mutating,
            changed_lines=changed_lines,
            goal_transition=transition,
            goal_objective=objective,
        )
        event_seq = int(progress.get("event_seq") or 0)
        storage.observe_injected_response(
            self.data_dir,
            event.session,
            event_seq=event_seq,
            observation_kind="tool",
            observation={
                "tool": event.tool_name,
                "command_family": checkpoints.command_family(event),
                "failed": event.failure_known and event.failed,
                "mutating": event.mutating,
                "goal_transition": transition,
            },
        )
        checkpoint = checkpoints.classify_tool(event, changed_lines)
        strategy = checkpoints.classify_strategy(
            progress, changed_line_count=changed_lines
        )
        current_source_fingerprint = str(
            (strategy or checkpoint or {}).get("fingerprint") or ""
        )
        pending_output, delivery_busy = _pending_output(
            self.data_dir,
            event.native_event_name,
            event.session,
            event_seq=event_seq,
            current_source_fingerprint=current_source_fingerprint,
        )
        if delivery_busy:
            return None
        if strategy and strategy["reason"] == "goal-transition":
            checkpoint = strategy
            storage.mark_strategy_reviewed(
                self.data_dir,
                event.session,
                event_seq=event_seq,
                changed_lines=changed_lines,
            )
        elif strategy:
            if pending_output is not None:
                return pending_output
            fingerprint = strategy["fingerprint"]
            if not storage.claim_strategy_run(
                self.data_dir, event.session, fingerprint
            ):
                return None
            if storage.claim_checkpoint(self.data_dir, event.session, fingerprint):
                if self.schedule_strategy:
                    scheduled = self.schedule_strategy(
                        {
                            "session": {
                                "host": event.session.host,
                                "session_id": event.session.session_id,
                                "turn_id": event.session.turn_id,
                                "cwd": event.session.cwd,
                                "repo_root": event.session.repo_root,
                            },
                            "checkpoint": strategy,
                            "journal": journal,
                            "progress": progress,
                            "task_anchor": str(progress.get("task_anchor") or storage.load_turn_state(self.data_dir, event.session).get("task_anchor") or ""),
                            "event_seq": event_seq,
                        }
                    )
                    if not scheduled:
                        storage.release_checkpoint(
                            self.data_dir, event.session, fingerprint
                        )
                        storage.release_strategy_run(
                            self.data_dir, event.session, fingerprint
                        )
                        return pending_output
                    storage.mark_strategy_reviewed(
                        self.data_dir,
                        event.session,
                        event_seq=event_seq,
                        changed_lines=changed_lines,
                    )
                else:
                    storage.mark_strategy_reviewed(
                        self.data_dir,
                        event.session,
                        event_seq=event_seq,
                        changed_lines=changed_lines,
                    )
                    self._run_strategy_payload(
                        {
                            "session": {
                                "host": event.session.host,
                                "session_id": event.session.session_id,
                                "turn_id": event.session.turn_id,
                                "cwd": event.session.cwd,
                                "repo_root": event.session.repo_root,
                            },
                            "checkpoint": strategy,
                            "journal": journal,
                            "progress": progress,
                            "task_anchor": str(storage.load_turn_state(self.data_dir, event.session).get("task_anchor") or ""),
                            "event_seq": event_seq,
                        }
                    )
            else:
                storage.release_strategy_run(
                    self.data_dir, event.session, fingerprint
                )
            return None
        if not checkpoint:
            return pending_output
        fingerprint = checkpoint["fingerprint"]
        if not storage.claim_checkpoint(self.data_dir, event.session, fingerprint):
            return pending_output
        state = storage.load_turn_state(self.data_dir, event.session)
        source_packet = source_context.build_checkpoint_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            event_context=checkpoint["context"],
            workflow_context=source_context.summarize_checkpoint_progress(progress),
            tool_evidence=journal,
        )
        request = ReviewRequest(
            schema_version=1,
            kind=(
                "goal_transition"
                if checkpoint["reason"] == "goal-transition"
                else "checkpoint"
            ),
            reason=checkpoint["reason"],
            session=event.session,
            source_packet=source_packet,
            source_fingerprint=fingerprint,
            routing_evidence=checkpoint["context"],
            source_event_seq=event_seq,
            trigger=str(checkpoint.get("trigger") or checkpoint["reason"]),
            routing_concern=str(checkpoint.get("routing_concern") or ""),
        )
        try:
            outcome = self.core.review(
                request,
                persist_reaction=True,
                mark_delivered=False,
                timeout_sec=self.core.settings.checkpoint_timeout_sec,
            )
        except Exception as exc:
            self.core.log_error(f"Codex checkpoint review failed: {exc}")
            storage.release_checkpoint(self.data_dir, event.session, fingerprint)
            return pending_output
        if outcome.status != "finding" or not outcome.finding:
            storage.release_checkpoint(self.data_dir, event.session, fingerprint)
            return pending_output
        if pending_output is not None:
            old_delivery = pending_output.get(DELIVERY_MARKER_KEY)
            if isinstance(old_delivery, dict):
                storage.mark_delivery(
                    self.data_dir,
                    event.session,
                    str(old_delivery.get("timestamp") or ""),
                    status="expired",
                    event_seq=event_seq,
                    delivered_via="superseded-by-current-checkpoint",
                )
                storage.release_delivery_claim(
                    self.data_dir,
                    event.session,
                    str(old_delivery.get("timestamp") or ""),
                    str(old_delivery.get("claim_token") or ""),
                )
        storage.complete_checkpoint(self.data_dir, event.session, fingerprint)
        output = build_hook_output(
            event.native_event_name,
            outcome.finding,
        )
        timestamp = outcome.reaction_ts
        if not timestamp:
            pending = storage.latest_pending(self.data_dir, event.session)
            timestamp = str((pending or {}).get("ts") or "")
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
            event_seq=event_seq,
            event_name=event.native_event_name,
            claim_token=claim_token,
        )

    def _run_strategy_payload(self, payload: dict[str, Any]) -> None:
        raw_session = payload.get("session") or {}
        session = SessionRef(
            str(raw_session.get("host") or "codex_cli"),  # type: ignore[arg-type]
            str(raw_session.get("session_id") or "unknown"),
            turn_id=str(raw_session.get("turn_id") or ""),
            cwd=str(raw_session.get("cwd") or ""),
            repo_root=str(raw_session.get("repo_root") or ""),
        )
        checkpoint = payload.get("checkpoint") or {}
        task_anchor = str(payload.get("task_anchor") or "")
        event_seq = int(payload.get("event_seq") or 0)
        context = str(checkpoint.get("context") or "")
        source_packet = source_context.build_checkpoint_packet(
            task_anchor=task_anchor,
            event_context=context,
            workflow_context=source_context.summarize_checkpoint_progress(
                payload.get("progress")
                if isinstance(payload.get("progress"), dict)
                else {}
            ),
            tool_evidence=str(payload.get("journal") or ""),
        )
        request = ReviewRequest(
            schema_version=1,
            kind="strategy",
            reason=str(checkpoint.get("reason") or "strategy-review"),
            session=session,
            source_packet=source_packet,
            source_fingerprint=str(checkpoint.get("fingerprint") or ""),
            routing_evidence=context,
            source_event_seq=event_seq,
            trigger=str(checkpoint.get("trigger") or "strategy-review"),
            routing_concern=str(checkpoint.get("routing_concern") or ""),
        )
        try:
            outcome = self.core.review(
                request,
                persist_reaction=True,
                mark_delivered=False,
                timeout_sec=self.core.settings.checkpoint_timeout_sec,
            )
        except Exception as exc:
            self.core.log_error(f"Codex strategy review failed: {exc}")
            storage.release_checkpoint(
                self.data_dir, session, request.source_fingerprint
            )
            storage.release_strategy_run(
                self.data_dir, session, request.source_fingerprint
            )
            return
        if outcome.status == "finding" and outcome.finding:
            storage.complete_checkpoint(
                self.data_dir, session, request.source_fingerprint
            )
        else:
            storage.release_checkpoint(
                self.data_dir, session, request.source_fingerprint
            )
        storage.release_strategy_run(
            self.data_dir, session, request.source_fingerprint
        )

    def _stop(self, event: TurnStopped) -> None:
        if event.stop_hook_active:
            return None
        storage.observe_injected_response(
            self.data_dir,
            event.session,
            observation_kind="stop",
            observation={"assistant_claim": event.final_claim},
        )
        state = storage.load_turn_state(self.data_dir, event.session)
        tool_evidence = str(state.get("tool_evidence") or "")
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
            tool_evidence=tool_evidence,
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
            self.core.review(request, persist_reaction=True)
        except Exception as exc:
            self.core.log_error(f"Codex stop review failed: {exc}")
        return None
