"""Shared reviewer orchestration used by every coding-agent host."""

from __future__ import annotations

import math
import time
from typing import Callable

import lens_router
import persona_config
import review_telemetry

from . import providers, storage
from .contracts import ReviewOutcome, ReviewRequest
from .prompting import (
    MAX_REACTION_CHARS,
    build_router_prompt,
    build_review_input,
    build_system_prompt,
)
from .runtime import REVIEW_TIMEOUT_SEC, RuntimeSettings


ProviderDispatch = Callable[..., dict]


def _merge_usage(*values: object) -> dict[str, int | float]:
    merged: dict[str, int | float] = {}
    for value in values:
        if not isinstance(value, dict):
            continue
        for key, amount in value.items():
            if isinstance(amount, bool) or not isinstance(amount, (int, float)):
                continue
            merged[str(key)] = merged.get(str(key), 0) + amount
    return merged


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
        self.route_schema_path = settings.paths.runtime_dir / "route-schema.json"

    def _review_claimed(
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
        )
        effective_timeout = min(
            timeout_sec or self.settings.timeout_sec,
            REVIEW_TIMEOUT_SEC,
        )
        review_started = time.perf_counter()
        deadline = review_started + effective_timeout
        router_usage: dict[str, int] = {}
        router_latency_ms = 0
        router_input_chars = 0
        result: dict | None = None
        error_stage = ""
        if not route.lens:
            router_prompt = build_router_prompt()
            router_timeout = max(1, math.ceil(deadline - time.perf_counter()))
            router_started = time.perf_counter()
            routed = self.dispatch(
                provider,
                router_prompt,
                request.source_packet,
                model,
                schema_path=self.route_schema_path,
                timeout_sec=router_timeout,
                ollama_url=self.settings.ollama_url,
                log_error=self.log_error,
            )
            router_latency_ms = round((time.perf_counter() - router_started) * 1000)
            router_input_chars = len(router_prompt) + len(request.source_packet)
            if not isinstance(routed, dict):
                routed = {"status": "error", "effective_lens": "none", "finding": ""}
            if persist_reaction:
                storage.append_provider_output(
                    self.settings.paths.data_dir,
                    request.session,
                    stage="router",
                    provider=provider,
                    model=model,
                    result=routed,
                    route_metadata={
                        "stage": route.stage,
                        "effective_lens": str(routed.get("effective_lens") or "none"),
                        "route_source": route.source,
                    },
                    source_fingerprint=request.source_fingerprint,
                )
            router_usage = (
                routed.get("usage") if isinstance(routed.get("usage"), dict) else {}
            )
            routed_status = str(routed.get("status") or "error")
            routed_lens = str(routed.get("effective_lens") or "none").lower()
            if routed_status == "no_finding":
                result = {
                    **routed,
                    "status": "no_finding",
                    "effective_lens": "none",
                    "finding": "",
                    "usage": {},
                }
            elif (
                routed_status == "finding"
                and routed_lens in persona_config.PERSONA_NAMES
            ):
                route = lens_router.ReviewRoute(
                    "automatic", routed_lens, "automatic_router"
                )
            else:
                result = {
                    **routed,
                    "status": "error",
                    "effective_lens": "none",
                    "finding": "",
                    "error_kind": str(routed.get("error_kind") or "invalid_route"),
                }
                error_stage = "router"
        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            route=route,
            log_error=self.log_error,
        ) if result is None else ""
        if result is None and not system_prompt:
            return ReviewOutcome(
                "error",
                effective_lens="none",
                provider=provider,
                model=model,
            )
        review_input = build_review_input(request.source_packet)

        started = time.perf_counter()
        if result is None:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                result = {
                    "status": "error",
                    "effective_lens": "none",
                    "finding": "",
                    "usage": {},
                    "error_kind": "timeout_before_generator",
                    "raw_output": "",
                }
                error_stage = "generator"
            else:
                generator_timeout = max(1, math.ceil(remaining))
                result = self.dispatch(
                    provider,
                    system_prompt,
                    review_input,
                    model,
                    schema_path=self.schema_path,
                    timeout_sec=generator_timeout,
                    ollama_url=self.settings.ollama_url,
                    log_error=self.log_error,
                )
                if not isinstance(result, dict):
                    result = {
                        "status": "error",
                        "effective_lens": "none",
                        "finding": "",
                        "usage": {},
                        "error_kind": "invalid_output",
                        "raw_output": "",
                    }
                if persist_reaction:
                    storage.append_provider_output(
                        self.settings.paths.data_dir,
                        request.session,
                        stage="generator",
                        provider=provider,
                        model=model,
                        result=result,
                        route_metadata={
                            "stage": route.stage,
                            "effective_lens": str(result.get("effective_lens") or "none"),
                            "route_source": route.source,
                        },
                        source_fingerprint=request.source_fingerprint,
                    )
        if not isinstance(result, dict):
            result = {"status": "error", "finding": "", "usage": {}}
        result["usage"] = _merge_usage(router_usage, result.get("usage"))
        latency_ms = router_latency_ms + round((time.perf_counter() - started) * 1000)
        finding = str(result.get("finding") or "").strip()
        status = str(result.get("status") or "error")
        effective_lens = str(result.get("effective_lens") or "none").strip().lower()
        if status not in {"finding", "no_finding", "error"}:
            status = "error"
        if status == "finding" and not finding:
            status = "error"
        if status == "finding" and len(finding) > MAX_REACTION_CHARS:
            status = "error"
        if status == "finding" and effective_lens not in persona_config.PERSONA_NAMES:
            status = "error"
        if (
            status == "finding"
            and route.lens
            and effective_lens != route.lens
        ):
            status = "error"
        if status == "error" and not error_stage:
            error_stage = "generator" if route.lens else "router"
        error_kind = str(result.get("error_kind") or ("invalid_output" if status == "error" else ""))
        if status == "finding" and storage.was_finding_injected(
            self.settings.paths.data_dir, request.session, finding
        ):
            status = "no_finding"
        if status != "finding":
            effective_lens = "none"
        route_fields = {
            "stage": route.stage,
            "effective_lens": effective_lens,
            "route_source": route.source,
        }
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
                "hook_event": request.hook_event,
                "status": status,
                "error_stage": error_stage,
                "error_kind": error_kind,
                "input_chars": router_input_chars + len(system_prompt) + len(review_input),
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
            effective_lens=effective_lens,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            usage=(result.get("usage") or {}) if isinstance(result, dict) else {},
            reaction_ts=reaction_ts,
            error_stage=error_stage,
            error_kind=error_kind,
        )

    def review_once(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool = True,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome | None:
        """Run one canonical review attempt and claim its identity once."""
        token = storage.claim_review_attempt(
            self.settings.paths.data_dir,
            request.session,
            request.kind,
            request.source_fingerprint,
        )
        if not token:
            return None
        try:
            outcome = self._review_claimed(
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
