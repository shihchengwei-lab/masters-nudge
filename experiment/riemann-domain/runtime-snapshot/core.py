"""Shared reviewer orchestration used by every coding-agent host."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

import lens_router
import persona_config
import riemann_router
import review_telemetry

from . import profiles, providers, storage
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

STRATEGY_PROMPT = """

# 長流程策略 checkpoint

檢視近期 workflow 是否實際縮短任務驗收條件，而非只讓局部 proxy 更漂亮。
若有漂移，只指出一個最值得改變後續工作方向的觀察；證據不足時不反應。
"""

GOAL_TRANSITION_PROMPT = """

# Goal 轉場 checkpoint

檢查 Goal 的狀態變更究竟代表：原始 objective 已達成、僅完成子成果、
路徑已耗盡，或完成依據不清。只在狀態與證據不一致時給一句 nudge。
"""

RIEMANN_OPUS_CHECKPOINT_TIMEOUT_SEC = 60
RIEMANN_OPUS_STOP_TIMEOUT_SEC = 180


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

    def _profile(self, request: ReviewRequest) -> profiles.WorkspaceProfile:
        profile, error = profiles.load_workspace_profile(
            self.settings.paths.data_dir, request.session
        )
        if error:
            self.log_error(error)
        return profile

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
        mark_delivered: bool = False,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        profile = self._profile(request)
        domain = profile.domain
        provider, model, configuration_source = profiles.resolve_reviewer(
            self.settings, profile
        )
        if request.kind != "stop" and profile.review_mode == "stop_only":
            return ReviewOutcome(
                "no_finding",
                effective_lens=(
                    riemann_router.STAGE_LENSES.get(profile.stage, "ramanujan")
                    if domain == "riemann"
                    else "general"
                ),
                provider=provider,
                model=model,
            )
        if domain == "riemann":
            pinned_lens = str(
                os.environ.get("MASTERS_NUDGE_PERSONA")
                or os.environ.get("BUDDY_PERSONA")
                or ""
            ).strip().lower()
            if pinned_lens not in riemann_router.MATH_LENSES:
                pinned_lens = ""
            if request.kind == "stop":
                routing_evidence = request.evidence.assistant_claim
            elif request.kind == "checkpoint":
                routing_evidence = request.evidence.checkpoint_event
            else:
                routing_evidence = request.evidence.tool_evidence
            route = riemann_router.resolve_riemann_route(
                profile.stage,
                routing_evidence or request.source_packet,
                pinned_lens=pinned_lens,
            )
            cooldown = storage.consume_riemann_specialist_slot(
                self.settings.paths.data_dir,
                request.session,
                specialist_requested=bool(route.override_lens),
            )
            if cooldown and route.source != "environment":
                route = lens_router.ReviewRoute(
                    route.stage,
                    route.primary_lens,
                    route.primary_lens,
                    "",
                    "specialist-cooldown",
                    route.source,
                )
            prompt_file = (
                self.settings.paths.runtime_dir / "domains" / "riemann" / "base-prompt.txt"
            )
            persona_dir = (
                self.settings.paths.runtime_dir / "domains" / "riemann" / "personas"
            )
        else:
            route = lens_router.resolve_review_route(
                self._route_dir(), request.source_packet
            )
            prompt_file = self.prompt_file
            persona_dir = self.persona_dir
        system_prompt = build_system_prompt(
            prompt_file=prompt_file,
            persona_dir=persona_dir,
            data_dir=self._route_dir(),
            route=route,
            domain=domain,
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

        effective_timeout = timeout_sec or self.settings.timeout_sec
        if (
            request.kind in {"checkpoint", "strategy", "goal_transition"}
            and domain == "riemann"
            and provider == "anthropic"
            and model == "claude-opus-4-6"
        ):
            effective_timeout = max(
                effective_timeout, RIEMANN_OPUS_CHECKPOINT_TIMEOUT_SEC
            )
        if (
            request.kind == "stop"
            and domain == "riemann"
            and provider == "anthropic"
            and model == "claude-opus-4-6"
        ):
            effective_timeout = max(
                effective_timeout, RIEMANN_OPUS_STOP_TIMEOUT_SEC
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
        finding = sanitize_reaction(
            str(result.get("finding") or ""), domain=domain
        )
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
                    **route_metadata(route, domain=domain),
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
            )
            reaction_ts = str((entry or {}).get("ts") or "")
            if mark_delivered and entry:
                storage.mark_delivered(
                    self.settings.paths.data_dir,
                    request.session,
                    str(entry.get("ts") or ""),
                )
        elif persist_reaction and status == "error":
            error_kind = str(result.get("error_kind") or "error")
            status_text = (
                f"Reviewer 逾時（{effective_timeout} 秒）；本輪沒有 Nudge。"
                if error_kind == "timeout"
                else "Reviewer 呼叫失敗；本輪沒有 Nudge。"
            )
            storage.append_reaction(
                self.settings.paths.data_dir,
                request.session,
                provider=provider,
                model=model,
                reaction=status_text,
                route_metadata={
                    **route_metadata(route, domain=domain),
                    "review_trigger": request.trigger or request.reason,
                },
                kind="review_status",
                reason=request.reason,
                source_event_seq=request.source_event_seq,
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
                "persona": route.effective_lens,
                **route_metadata(route, domain=domain),
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
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            usage=(result.get("usage") or {}) if isinstance(result, dict) else {},
            reaction_ts=reaction_ts,
        )
