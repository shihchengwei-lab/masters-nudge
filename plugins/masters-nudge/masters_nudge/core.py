"""Route one bounded evidence packet through one Nudge Lens."""

from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Callable

import lens_router
import source_context

from . import evidence, providers, storage
from .contracts import NudgeOutcome, ToolCompleted
from .prompting import (
    MAX_NUDGE_CHARS,
    build_nudge_input,
    build_router_prompt,
    build_system_prompt,
)
from .runtime import PROVIDER_TIMEOUT_SEC, RuntimeSettings


ProviderDispatch = Callable[..., dict]
StageObserver = Callable[[str, str, str, float], None]


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
        self.route_schema_path = runtime / "route-schema.json"

    def review_contract_signature(self) -> str:
        """Identify the Provider contract whose completed silence may be reused."""
        try:
            contract = {
                "provider": self.settings.provider,
                "model": self.settings.model,
                "lens": self.settings.lens,
                "ollama_url": self.settings.ollama_url,
                "router_prompt": build_router_prompt(),
                "buddy_prompt": self.prompt_file.read_text(encoding="utf-8"),
                "nudge_schema": self.schema_path.read_text(encoding="utf-8"),
                "route_schema": self.route_schema_path.read_text(encoding="utf-8"),
                "personas": {
                    persona: (self.persona_dir / f"{persona}.txt").read_text(
                        encoding="utf-8"
                    )
                    for persona in sorted(set(lens_router.LENS_PERSONAS.values()))
                },
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
        if observed.reused_generator_no_finding or not observed.eligible:
            return None
        state = observed.turn_state
        packet = source_context.build_checkpoint_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            task_sources=state.get("task_sources") or {},
            workspace_snapshot=str(state.get("workspace_snapshot") or ""),
            previous_findings=state.get("previous_findings") or [],
            evidence_records=state.get("evidence_records") or [],
        )
        session = events[0].session
        observe_stage = storage.provider_stage_observer(
            self.settings.paths.data_dir,
            session,
            evidence_seq=int(state.get("evidence_seq") or 0),
            provider=self.settings.provider,
            model=self.settings.model,
            configured_lens=self.settings.lens,
        )
        outcome = self.nudge_once(
            packet,
            timeout_sec=PROVIDER_TIMEOUT_SEC,
            observe_stage=observe_stage,
        )
        if outcome.status == "no_finding" and outcome.decision_stage == "generator":
            storage.record_completed_generator_no_finding(
                self.settings.paths.data_dir,
                session,
                evidence_seq=int(state.get("evidence_seq") or 0),
                workspace_snapshot=str(state.get("workspace_snapshot") or ""),
                checkpoint_signature=observed.checkpoint_signature,
                contract_signature=contract_signature,
            )
        return outcome

    def _call(
        self,
        stage: str,
        system_prompt: str,
        source_packet: str,
        schema_path,
        timeout_sec: int,
        observe_stage: StageObserver | None,
    ) -> dict:
        started_ns = time.monotonic_ns()
        try:
            result = self.dispatch(
                self.settings.provider,
                system_prompt,
                source_packet,
                self.settings.model,
                schema_path=schema_path,
                timeout_sec=timeout_sec,
                ollama_url=self.settings.ollama_url,
                log_error=self.log_error,
            )
            normalized = result if isinstance(result, dict) else {"status": "error"}
        except Exception:
            self._observe_stage(observe_stage, stage, "error", "", started_ns)
            raise
        self._observe_stage(
            observe_stage,
            stage,
            str(normalized.get("status") or "error"),
            str(normalized.get("lens") or ""),
            started_ns,
        )
        return normalized

    @staticmethod
    def _observe_stage(
        observer: StageObserver | None,
        stage: str,
        status: str,
        lens: str,
        started_ns: int,
    ) -> None:
        if observer is None:
            return
        duration_ms = max(0.0, (time.monotonic_ns() - started_ns) / 1_000_000)
        try:
            observer(stage, status, lens, round(duration_ms, 3))
        except Exception:
            pass

    def nudge_once(
        self,
        source_packet: str,
        timeout_sec: int | None = None,
        observe_stage: StageObserver | None = None,
    ) -> NudgeOutcome:
        timeout = min(timeout_sec or PROVIDER_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC)
        deadline = time.perf_counter() + timeout
        route = lens_router.resolve_nudge_route(self.settings.lens)

        if not route.lens:
            routed = self._call(
                "router",
                build_router_prompt(),
                source_packet,
                self.route_schema_path,
                max(1, math.ceil(deadline - time.perf_counter())),
                observe_stage,
            )
            status = str(routed.get("status") or "error")
            if status == "no_finding":
                return NudgeOutcome("no_finding", decision_stage="router")
            routed_lens = str(routed.get("lens") or "").lower()
            route = lens_router.resolve_nudge_route(routed_lens)
            if status != "finding" or not route.lens:
                return NudgeOutcome("error", decision_stage="router")

        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            route=route,
            log_error=self.log_error,
        )
        remaining = deadline - time.perf_counter()
        if not system_prompt or remaining <= 0:
            return NudgeOutcome("error", decision_stage="generator")
        result = self._call(
            "generator",
            system_prompt,
            build_nudge_input(source_packet),
            self.schema_path,
            max(1, math.ceil(remaining)),
            observe_stage,
        )
        status = str(result.get("status") or "error")
        finding = str(result.get("finding") or "").strip()
        returned_lens = str(result.get("lens") or "").lower()
        if status == "no_finding":
            return NudgeOutcome("no_finding", decision_stage="generator")
        if (
            status != "finding"
            or not finding
            or len(finding) > MAX_NUDGE_CHARS
            or returned_lens != route.lens
        ):
            return NudgeOutcome("error", decision_stage="generator")
        return NudgeOutcome("finding", finding, route.lens, "generator")
