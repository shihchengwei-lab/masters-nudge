"""Shared reviewer orchestration used by every coding-agent host."""

from __future__ import annotations

import time
from typing import Callable

import lens_router
import review_telemetry

from . import providers, storage
from .contracts import ReviewOutcome, ReviewRequest
from .prompting import build_system_prompt, route_metadata, sanitize_reaction
from .runtime import RuntimeSettings


CHECKPOINT_PROMPT = """

# 工作途中 checkpoint

輸入末尾是截至目前的有限研究狀態，不只是一個工具事件。
workflow 是行為證據，不等於主 Agent 已明說的理由。
finding 落在目前瓶頸解釋仍未消解、且跨數分鐘仍成立的一個關係；
證據不足時可以不反應。
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
        mark_delivered: bool = False,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        provider = self.settings.provider
        model = self.settings.model
        configuration_source = self.settings.configuration_source
        checkpoint_routing = request.kind != "stop"
        routing_evidence = request.routing_evidence if checkpoint_routing else ""
        route = lens_router.resolve_review_route(
            self.settings.paths.data_dir,
            routing_evidence,
            checkpoint=checkpoint_routing,
            routing_concern=(request.routing_concern if checkpoint_routing else ""),
            injected_personas=storage.read_recent_injected_personas(
                self.settings.paths.data_dir,
                request.session,
                limit=2,
            ),
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

        review_input = request.source_packet

        effective_timeout = timeout_sec or self.settings.timeout_sec
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
        finding = sanitize_reaction(str(result.get("finding") or ""))
        status = str(result.get("status") or "error")
        if status not in {"finding", "no_finding", "error"}:
            status = "error"
        if status == "finding" and not finding:
            status = "error"
        reaction_ts = ""
        if persist_reaction and status == "finding":
            finding_scope = _finding_scope(request)
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
                finding_scope=finding_scope,
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
                "persona": route.effective_lens,
                **route_fields,
                "review_trigger": request.trigger or request.reason,
                "status": status,
                "input_chars": len(system_prompt) + len(review_input),
                "latency_ms": latency_ms,
                "source_fingerprint": request.source_fingerprint,
                "finding_scope": _finding_scope(request),
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


def _finding_scope(request: ReviewRequest) -> str:
    return "local" if request.kind == "checkpoint" else "trajectory"
