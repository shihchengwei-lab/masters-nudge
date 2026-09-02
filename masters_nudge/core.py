"""Review one bounded evidence packet through one selected Nudge Lens."""

from __future__ import annotations

import hashlib
import json
from typing import Callable

import source_context

from . import evidence, providers, storage
from .contracts import NudgeOutcome, ToolCompleted
from .lenses import LENSES
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

    def review_contract_signature(self) -> str:
        """Identify the effective Provider contract whose silence may be reused."""
        spec = LENSES.get(self.settings.lens)
        if spec is None:
            self.log_error("review contract requires one selected lens")
            return ""
        try:
            contract = {
                "provider": self.settings.provider,
                "model": self.settings.model,
                "lens": self.settings.lens,
                "ollama_url": self.settings.ollama_url,
                "buddy_prompt": self.prompt_file.read_text(encoding="utf-8"),
                "nudge_schema": self.schema_path.read_text(encoding="utf-8"),
                "persona": (self.persona_dir / f"{spec.persona}.txt").read_text(
                    encoding="utf-8"
                ),
            }
        except OSError as exc:
            self.log_error(f"review contract unavailable: {exc}")
            return ""
        encoded = json.dumps(
            contract,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def review_tool_batch(
        self, events: list[ToolCompleted]
    ) -> NudgeOutcome | None:
        """Run one host-neutral review flow for a completed tool batch."""
        contract_signature = self.review_contract_signature()
        observed = evidence.observe_tool_batch(
            self.settings.paths.data_dir,
            events,
            contract_signature=contract_signature,
        )
        if not observed.eligible:
            return None
        state = observed.turn_state
        packet = source_context.build_checkpoint_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            task_sources=state.get("task_sources") or {},
            workspace_snapshot=str(state.get("workspace_snapshot") or ""),
            actor_source_records=state.get("actor_source_records") or [],
            previous_findings=state.get("previous_findings") or [],
            evidence_records=state.get("evidence_records") or [],
        )
        outcome = self.nudge_once(packet, timeout_sec=PROVIDER_TIMEOUT_SEC)
        if outcome.status in {"finding", "no_finding"}:
            storage.record_completed_review(
                self.settings.paths.data_dir,
                events[0].session,
                workspace_revision_signature=observed.workspace_revision_signature,
                contract_signature=contract_signature,
                evidence_classes=observed.evidence_classes,
            )
        return outcome

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
