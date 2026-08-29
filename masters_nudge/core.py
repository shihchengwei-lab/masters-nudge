"""Route one bounded evidence packet through one Nudge Lens."""

from __future__ import annotations

import math
import time
from typing import Callable

import lens_router

from . import providers
from .contracts import NudgeOutcome
from .prompting import (
    MAX_NUDGE_CHARS,
    build_nudge_input,
    build_router_prompt,
    build_system_prompt,
)
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
        self.route_schema_path = runtime / "route-schema.json"

    def _call(
        self,
        system_prompt: str,
        source_packet: str,
        schema_path,
        timeout_sec: int,
    ) -> dict:
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
        return result if isinstance(result, dict) else {"status": "error"}

    def nudge_once(
        self,
        source_packet: str,
        timeout_sec: int | None = None,
    ) -> NudgeOutcome:
        timeout = min(timeout_sec or PROVIDER_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC)
        deadline = time.perf_counter() + timeout
        route = lens_router.resolve_nudge_route(self.settings.lens)

        if not route.lens:
            routed = self._call(
                build_router_prompt(),
                source_packet,
                self.route_schema_path,
                max(1, math.ceil(deadline - time.perf_counter())),
            )
            status = str(routed.get("status") or "error")
            if status == "no_finding":
                return NudgeOutcome("no_finding")
            routed_lens = str(routed.get("lens") or "").lower()
            route = lens_router.resolve_nudge_route(routed_lens)
            if status != "finding" or not route.lens:
                return NudgeOutcome("error")

        system_prompt = build_system_prompt(
            prompt_file=self.prompt_file,
            persona_dir=self.persona_dir,
            route=route,
            log_error=self.log_error,
        )
        remaining = deadline - time.perf_counter()
        if not system_prompt or remaining <= 0:
            return NudgeOutcome("error")
        result = self._call(
            system_prompt,
            build_nudge_input(source_packet),
            self.schema_path,
            max(1, math.ceil(remaining)),
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
            or returned_lens != route.lens
        ):
            return NudgeOutcome("error")
        return NudgeOutcome("finding", finding, route.lens)
