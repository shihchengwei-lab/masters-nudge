"""Review one bounded evidence packet through one selected Nudge Lens."""

from __future__ import annotations

from typing import Callable

import source_context

from . import evidence, providers, storage
from .contracts import NudgeOutcome, ToolCompleted
from .prompting import MAX_NUDGE_CHARS, build_nudge_input, build_system_prompt
from .runtime import PROVIDER_TIMEOUT_SEC, RuntimeSettings


ProviderDispatch = Callable[..., dict]


class NudgeCore:
    def __init__(
        self,
        settings: RuntimeSettings,
        *,
        dispatch: ProviderDispatch | None = None,
        log_error: Callable[[str], None] | None = None,
    ) -> None:
        self.settings = settings
        self.dispatch = dispatch or providers.dispatch_call_result
        self.log_error = log_error or (lambda _message: None)
        runtime = settings.paths.runtime_dir
        self.prompt_file = runtime / "buddy-prompt.txt"
        self.persona_dir = runtime / "personas"
        self.schema_path = runtime / "nudge-schema.json"

    def review_tool_batch(
        self, events: list[ToolCompleted]
    ) -> NudgeOutcome | None:
        """Run one host-neutral review flow for a completed tool batch."""
        observed = evidence.observe_tool_batch(
            self.settings.paths.data_dir,
            events,
        )
        if not observed.candidate:
            return None
        state, admitted = storage.claim_review_slot(
            self.settings.paths.data_dir,
            events[0].session,
            has_failure=observed.has_failure,
        )
        if not admitted:
            return None
        packet = source_context.build_checkpoint_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            task_sources=state.get("task_sources") or {},
            workspace_snapshot=str(state.get("workspace_snapshot") or ""),
            actor_source_records=state.get("actor_source_records") or [],
            previous_findings=state.get("previous_findings") or [],
            checkpoint_records=observed.checkpoint_records,
        )
        return self.nudge_once(packet, timeout_sec=PROVIDER_TIMEOUT_SEC)

    def _call(
        self,
        system_prompt: str,
        source_packet: str,
        timeout_sec: int,
    ) -> dict:
        result = self.dispatch(
            self.settings.provider,
            system_prompt,
            source_packet,
            self.settings.model,
            schema_path=self.schema_path,
            timeout_sec=timeout_sec,
            ollama_url=self.settings.ollama_url,
            log_error=self.log_error,
        )
        return result if isinstance(result, dict) else {"status": "error"}

    def nudge_once(
        self,
        source_packet: str,
        timeout_sec: int | None = None,
    ) -> NudgeOutcome:
        timeout = min(timeout_sec or PROVIDER_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC)
        lens = self.settings.lens
        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            lens=lens,
            log_error=self.log_error,
        )
        if not system_prompt:
            return NudgeOutcome("error")
        result = self._call(
            system_prompt,
            build_nudge_input(source_packet),
            timeout,
        )
        status = str(result.get("status") or "error")
        finding = str(result.get("finding") or "").strip()
        returned_lens = str(result.get("lens") or "").lower()
        if status == "no_finding":
            return NudgeOutcome("no_finding")
        if (
            status != "finding"
            or not finding
            or len(finding) > MAX_NUDGE_CHARS
            or returned_lens != lens
        ):
            return NudgeOutcome("error")
        return NudgeOutcome("finding", finding, lens)
