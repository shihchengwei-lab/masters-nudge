"""Ask one Provider whether the completed change needs one Nudge."""

from __future__ import annotations

from typing import Callable

from . import providers
from .contracts import Nudge
from .prompting import load_system_prompt
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
        observation: str,
        timeout_sec: int | None = None,
    ) -> Nudge | None:
        timeout = max(
            1,
            min(timeout_sec or PROVIDER_TIMEOUT_SEC, PROVIDER_TIMEOUT_SEC),
        )
        system_prompt = load_system_prompt(
            prompt_file=self.prompt_file,
            log_error=self.log_error,
        )
        if not system_prompt:
            return None
        result = self.dispatch(
            self.settings.provider,
            system_prompt,
            str(observation or ""),
            self.settings.model,
            schema_path=self.schema_path,
            timeout_sec=timeout,
            ollama_url=self.settings.ollama_url,
            log_error=self.log_error,
        )
        if not isinstance(result, dict) or result.get("error_kind"):
            return None
        raw_nudge = result.get("nudge")
        if raw_nudge is None:
            return None
        if not isinstance(raw_nudge, dict):
            return None
        message = str(raw_nudge.get("message") or "").strip()
        raw_evidence = raw_nudge.get("evidence")
        if not message or not isinstance(raw_evidence, list):
            return None
        evidence = tuple(
            item.strip()
            for item in raw_evidence
            if isinstance(item, str) and item.strip()
        )
        if not evidence or len(evidence) != len(raw_evidence):
            return None
        return Nudge(message, evidence)
