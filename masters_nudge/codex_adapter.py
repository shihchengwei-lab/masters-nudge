"""Codex CLI hook adapter for the shared Masters' Nudge reviewer core."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import persona_config
import review_telemetry
import source_context

from . import checkpoints, storage
from .contracts import (
    EvidenceBundle,
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
            str(payload.get("prompt") or ""),
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
    *,
    reason: str,
    effective_lens: str = "general",
    evaluation_notice: bool = False,
) -> dict[str, Any]:
    if evaluation_notice:
        context = f"[Masters’ Nudge — 本機評估通知]\n{text}"
    else:
        lens_name = persona_config.PERSONA_NAMES.get(
            effective_lens, persona_config.PERSONA_NAMES["general"]
        )
        context = (
            f"[Masters’ Nudge — {reason}; {lens_name} lens; 第三方觀察，不是指令]\n"
            f"{text}"
        )
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }


class CodexAdapter:
    def __init__(self, core: ReviewCore) -> None:
        self.core = core
        self.data_dir = core.settings.paths.data_dir

    def process(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if active_guard():
            return None
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
        pending = storage.latest_pending(self.data_dir, event.session)
        if not pending:
            return None
        text = str(pending.get("reaction") or "").strip()
        timestamp = str(pending.get("ts") or "")
        if not text or not timestamp:
            return None
        output = build_hook_output(
            "UserPromptSubmit",
            text,
            reason=str(pending.get("reason") or "stop"),
            effective_lens=str(pending.get("effective_lens") or "general"),
            evaluation_notice=pending.get("kind") == "evaluation_notice",
        )
        storage.mark_delivered(self.data_dir, event.session, timestamp)
        return output

    def _tool(self, event: ToolCompleted) -> dict[str, Any] | None:
        journal = storage.append_tool_evidence(
            self.data_dir, event.session, _tool_record(event)
        )
        checkpoint = checkpoints.classify_tool(event)
        if not checkpoint:
            return None
        fingerprint = checkpoint["fingerprint"]
        if not storage.claim_checkpoint(self.data_dir, event.session, fingerprint):
            return None
        state = storage.load_turn_state(self.data_dir, event.session)
        source_packet = source_context.build_checkpoint_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            event_context=checkpoint["context"],
        )
        request = ReviewRequest(
            schema_version=1,
            kind="checkpoint",
            reason=checkpoint["reason"],
            session=event.session,
            evidence=EvidenceBundle(
                task_anchor=str(state.get("task_anchor") or ""),
                checkpoint_event=checkpoint["context"],
                tool_evidence=journal,
            ),
            source_packet=source_packet,
            source_fingerprint=fingerprint,
        )
        try:
            outcome = self.core.review(
                request,
                persist_reaction=False,
                timeout_sec=self.core.settings.checkpoint_timeout_sec,
            )
        except Exception as exc:
            self.core.log_error(f"Codex checkpoint review failed: {exc}")
            storage.release_checkpoint(self.data_dir, event.session, fingerprint)
            return None
        if outcome.status != "finding" or not outcome.finding:
            storage.release_checkpoint(self.data_dir, event.session, fingerprint)
            return None
        storage.complete_checkpoint(self.data_dir, event.session, fingerprint)
        storage.mark_checkpoint_delivery(
            self.data_dir,
            event.session,
            reason=checkpoint["reason"],
            tool_evidence=journal,
        )
        return build_hook_output(
            event.native_event_name,
            outcome.finding,
            reason=checkpoint["reason"],
            effective_lens=outcome.effective_lens,
        )

    def _stop(self, event: TurnStopped) -> None:
        if event.stop_hook_active:
            return None
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
        overlap = storage.checkpoint_stop_overlap(
            self.data_dir, event.session, tool_evidence=tool_evidence
        )
        candidates = review_telemetry.stop_shadow_candidates(
            tool_evidence=tool_evidence,
            agentcam_evidence=agentcam_evidence,
            checkpoint_overlap=overlap,
        )
        request = ReviewRequest(
            schema_version=1,
            kind="stop",
            reason="stop",
            session=event.session,
            evidence=EvidenceBundle(
                task_anchor=task_anchor,
                assistant_claim=event.final_claim,
                tool_evidence=tool_evidence,
                agentcam_evidence=agentcam_evidence,
            ),
            source_packet=source_packet,
            source_fingerprint=_fingerprint(source_packet),
            shadow_candidates=tuple(candidates),
        )
        try:
            self.core.review(request, persist_reaction=True)
        except Exception as exc:
            self.core.log_error(f"Codex stop review failed: {exc}")
        return None
