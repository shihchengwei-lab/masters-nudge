"""Shared reviewer orchestration used by every coding-agent host."""

from __future__ import annotations

import time
from typing import Callable

import lens_router
import review_telemetry

from . import providers, storage
from .contracts import ReviewOutcome, ReviewRequest
from .prompting import (
    build_review_input,
    build_system_prompt,
    lens_focus_prompt,
    route_metadata,
)
from .runtime import REVIEW_TIMEOUT_SEC, RuntimeSettings


CHECKPOINT_PROMPT = """

# CURRENT STATE CHECKPOINT

Current timing: the main agent has reached a state checkpoint.
"""

STRATEGY_PROMPT = """

# TRAJECTORY CHECKPOINT

Current timing: the main agent has completed a change-and-validation cycle.
"""

GOAL_TRANSITION_PROMPT = """

# GOAL TRANSITION

Current timing: the main agent is transitioning the task goal.
"""

STOP_PROMPT = """

# COMPLETION BOUNDARY

Current timing: the main agent is about to close the task.
"""

ProviderDispatch = Callable[..., dict]


class ReviewCore:
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
        self.prompt_file = settings.paths.runtime_dir / "buddy-prompt.txt"
        self.persona_dir = settings.paths.runtime_dir / "personas"
        self.schema_path = settings.paths.runtime_dir / "reaction-schema.json"

    def review(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        provider = self.settings.provider
        model = self.settings.model
        configuration_source = self.settings.configuration_source
        route = lens_router.resolve_review_route(
            self.settings.paths.data_dir,
            reported_focus=request.reported_focus,
            stopping=request.kind == "stop",
        )
        route_fields = route_metadata(route)
        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            route=route,
            log_error=self.log_error,
        )
        if not system_prompt:
            return ReviewOutcome(
                "error",
                effective_lens=route.effective_lens,
                provider=provider,
                model=model,
            )
        if request.kind == "checkpoint":
            system_prompt += CHECKPOINT_PROMPT
        elif request.kind == "strategy":
            system_prompt += STRATEGY_PROMPT
        elif request.kind == "goal_transition":
            system_prompt += GOAL_TRANSITION_PROMPT
        elif request.kind == "stop":
            system_prompt += STOP_PROMPT
        system_prompt += lens_focus_prompt(route.effective_lens)

        review_input = build_review_input(
            request.source_packet,
            storage.read_recent_injected_findings(
                self.settings.paths.data_dir,
                request.session,
                limit=3,
            ),
        )

        effective_timeout = min(
            timeout_sec or self.settings.timeout_sec,
            REVIEW_TIMEOUT_SEC,
        )
        started = time.perf_counter()
        result = self.dispatch(
            provider,
            system_prompt,
            review_input,
            model,
            schema_path=self.schema_path,
            timeout_sec=effective_timeout,
            ollama_url=self.settings.ollama_url,
            log_error=self.log_error,
        )
        if not isinstance(result, dict):
            result = {"status": "error", "finding": "", "usage": {}}
        latency_ms = round((time.perf_counter() - started) * 1000)
        finding = str(result.get("finding") or "").strip()
        status = str(result.get("status") or "error")
        if status not in {"finding", "no_finding", "error"}:
            status = "error"
        if status == "finding" and not finding:
            status = "error"
        reaction_ts = ""
        if persist_reaction and status == "finding":
            entry = storage.append_reaction(
                self.settings.paths.data_dir,
                request.session,
                provider=provider,
                model=model,
                reaction=finding,
                route_metadata={
                    **route_fields,
                    "review_trigger": request.trigger or request.reason,
                    **(
                        {
                            "completion_basis": "unclear"
                        }
                        if request.trigger in {"goal-complete", "goal-blocked"}
                        else {}
                    ),
                },
                reason=request.reason,
                source_event_seq=request.source_event_seq,
                source_fingerprint=request.source_fingerprint,
            )
            reaction_ts = str((entry or {}).get("ts") or "")
        elif persist_reaction and status == "error":
            error_kind = str(result.get("error_kind") or "error")
            status_text = (
                f"Reviewer 逾時（{effective_timeout} 秒）；本輪沒有 Nudge。"
                if error_kind == "timeout" or error_kind.startswith("timeout_")
                else "Reviewer 呼叫失敗；本輪沒有 Nudge。"
            )
            storage.append_reaction(
                self.settings.paths.data_dir,
                request.session,
                provider=provider,
                model=model,
                reaction=status_text,
                route_metadata={
                    **route_fields,
                    "review_trigger": request.trigger or request.reason,
                },
                kind="review_status",
                reason=request.reason,
                source_event_seq=request.source_event_seq,
                source_fingerprint=request.source_fingerprint,
            )

        try:
            telemetry_record = {
                "schema_version": request.schema_version,
                "host": request.session.host,
                "turn_id": request.session.turn_id,
                "session_id": request.session.session_id,
                "kind": request.kind,
                "reason": request.reason,
                "provider": provider,
                "model": model,
                "configuration_source": configuration_source,
                **route_fields,
                "review_trigger": request.trigger or request.reason,
                "status": status,
                "input_chars": len(system_prompt) + len(review_input),
                "latency_ms": latency_ms,
                "source_fingerprint": request.source_fingerprint,
                "usage": result.get("usage") if isinstance(result, dict) else {},
            }
            review_telemetry.record_review(
                self.settings.paths.data_dir,
                telemetry_record,
            )
        except Exception as exc:
            self.log_error(f"review telemetry failed: {exc}")

        return ReviewOutcome(
            status,  # type: ignore[arg-type]
            finding=finding if status == "finding" else "",
            effective_lens=route.effective_lens,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            usage=(result.get("usage") or {}) if isinstance(result, dict) else {},
            reaction_ts=reaction_ts,
        )

    def review_once(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool = True,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome | None:
        """Run exactly one Provider call for a canonical review identity."""
        token = storage.claim_review_attempt(
            self.settings.paths.data_dir,
            request.session,
            request.kind,
            request.source_fingerprint,
        )
        if not token:
            return None
        try:
            outcome = self.review(
                request,
                persist_reaction=persist_reaction,
                timeout_sec=timeout_sec,
            )
        except Exception:
            storage.finish_review_attempt(
                self.settings.paths.data_dir,
                request.session,
                request.kind,
                request.source_fingerprint,
                token,
                "error",
            )
            raise
        storage.finish_review_attempt(
            self.settings.paths.data_dir,
            request.session,
            request.kind,
            request.source_fingerprint,
            token,
            outcome.status,
        )
        return outcome
