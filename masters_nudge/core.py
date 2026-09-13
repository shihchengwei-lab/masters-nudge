"""Ask one Provider for one judgment on a bounded evidence packet."""

from __future__ import annotations

from typing import Callable

from . import providers
from .contracts import NudgeOutcome
from .prompting import (
    has_nudge_prefix,
    is_principle,
    load_system_prompt,
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
        self.schema_path = runtime / "nudge-schema.json"

    def nudge_once(
        self,
        source_packet: str,
        timeout_sec: int | None = None,
    ) -> NudgeOutcome:
        timeout = max(
            1,
            min(timeout_sec or PROVIDER_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC),
        )
        system_prompt = load_system_prompt(
            prompt_file=self.prompt_file,
            log_error=self.log_error,
        )
        if not system_prompt:
            return NudgeOutcome("error")
        result = self.dispatch(
            self.settings.provider,
            system_prompt,
            str(source_packet or ""),
            self.settings.model,
            schema_path=self.schema_path,
            timeout_sec=timeout,
            ollama_url=self.settings.ollama_url,
            log_error=self.log_error,
        )
        if not isinstance(result, dict):
            return NudgeOutcome("error")
        status = str(result.get("status") or "error")
        principle = str(result.get("principle") or "none")
        anchor = str(result.get("anchor") or "").strip()
        relationship = str(result.get("relationship") or "").strip()
        if status == "no_finding":
            return (
                NudgeOutcome("no_finding")
                if principle == "none" and not anchor and not relationship
                else NudgeOutcome("error")
            )
        if (
            status != "finding"
            or not is_principle(principle)
            or not anchor
            or not relationship
            or has_nudge_prefix(relationship)
        ):
            return NudgeOutcome("error")
        return NudgeOutcome("finding", principle, anchor, relationship)
