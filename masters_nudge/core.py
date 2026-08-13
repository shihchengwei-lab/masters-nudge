"""Shared reviewer orchestration used by every coding-agent host."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import lens_router
import persona_config
import review_telemetry

from . import providers, storage
from .contracts import ReviewOutcome, ReviewRequest
from .prompting import build_system_prompt, route_metadata, sanitize_reaction
from .runtime import RuntimeSettings


CHECKPOINT_PROMPT = """

# 工作途中 checkpoint

輸入末尾是 Masters’ Nudge 剛收到的工具事件，
比可能延遲寫入的 transcript 更新。只針對此事件揭露的一個最高價值問題
給主 Agent 一句 nudge；證據不足時可以不反應。不要要求使用者處理，
不要寫成批准、阻擋或完成判定。
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

    def _route_dir(self) -> Path:
        current = self.settings.paths.data_dir
        legacy = self.settings.paths.legacy_data_dir
        if not (current / persona_config.CONFIG_FILE).exists() and (
            legacy / persona_config.CONFIG_FILE
        ).exists():
            return legacy
        return current

    def review(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        route = lens_router.resolve_review_route(
            self._route_dir(), request.source_packet
        )
        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            data_dir=self._route_dir(),
            route=route,
            log_error=self.log_error,
        )
        if not system_prompt:
            return ReviewOutcome(
                "error",
                effective_lens=route.effective_lens,
                provider=self.settings.provider,
                model=self.settings.model,
            )
        if request.kind == "checkpoint":
            system_prompt += CHECKPOINT_PROMPT

        recent = storage.read_recent_reactions_compatible(
            self.settings.paths.data_dir,
            self.settings.paths.legacy_data_dir,
            request.session,
        )
        parts: list[str] = []
        if recent:
            parts.append("[你最近說過]")
            parts.extend(f"- {reaction}" for reaction in recent)
            parts.append("[避免重複上面的話，可以接著講]")
        parts.append(request.source_packet)
        review_input = "\n\n".join(parts)

        started = time.perf_counter()
        result = self.dispatch(
            self.settings.provider,
            system_prompt,
            review_input,
            self.settings.model,
            schema_path=self.schema_path,
            timeout_sec=timeout_sec or self.settings.timeout_sec,
            log_error=self.log_error,
        )
        if not isinstance(result, dict):
            result = {"status": "error", "finding": "", "usage": {}}
        latency_ms = round((time.perf_counter() - started) * 1000)
        finding = sanitize_reaction(str(result.get("finding") or ""))
        status = str(result.get("status") or "error")
        if status not in {"finding", "no_finding", "error"}:
            status = "error"
        if status == "finding" and not finding:
            status = "error"
        if persist_reaction and status == "finding":
            storage.append_reaction(
                self.settings.paths.data_dir,
                request.session,
                provider=self.settings.provider,
                model=self.settings.model,
                reaction=finding,
                route_metadata=route_metadata(route),
                reason=request.reason,
            )

        try:
            telemetry_record = {
                "schema_version": request.schema_version,
                "host": request.session.host,
                "turn_id": request.session.turn_id,
                "session_id": request.session.session_id,
                "kind": request.kind,
                "reason": request.reason,
                "provider": self.settings.provider,
                "model": self.settings.model,
                "persona": route.effective_lens,
                **route_metadata(route),
                "status": status,
                "input_chars": len(system_prompt) + len(review_input),
                "latency_ms": latency_ms,
                "source_fingerprint": request.source_fingerprint,
                "shadow_candidates": list(request.shadow_candidates),
                "usage": result.get("usage") if isinstance(result, dict) else {},
            }
            review_telemetry.record_review(
                self.settings.paths.data_dir,
                telemetry_record,
                notice_log_path=storage.reaction_log_path(
                    self.settings.paths.data_dir, request.session
                ),
            )
        except Exception as exc:
            self.log_error(f"review telemetry failed: {exc}")

        return ReviewOutcome(
            status,  # type: ignore[arg-type]
            finding=finding if status == "finding" else "",
            effective_lens=route.effective_lens,
            provider=self.settings.provider,
            model=self.settings.model,
            latency_ms=latency_ms,
            usage=(result.get("usage") or {}) if isinstance(result, dict) else {},
        )
