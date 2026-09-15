"""Ask one Provider for one judgment on a bounded evidence packet."""

from __future__ import annotations

from typing import Callable

from . import providers
from .contracts import NudgeOutcome
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
        source_packet: str,
        timeout_sec: int | None = None,
        *,
        workspace_root: str = "",
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
            workspace_root=workspace_root,
            log_error=self.log_error,
        )
        if not isinstance(result, dict):
            return NudgeOutcome("error")
        decision = str(result.get("decision") or "error")
        current_choice = str(result.get("current_choice") or "").strip()
        structural_cost = str(result.get("structural_cost") or "").strip()
        direction = str(result.get("direction") or "").strip()
        raw_evidence = result.get("evidence")
        evidence = (
            tuple(item.strip() for item in raw_evidence if isinstance(item, str) and item.strip())
            if isinstance(raw_evidence, list)
            else ()
        )
        if decision == "pass":
            return (
                NudgeOutcome("pass")
                if not current_choice
                and not structural_cost
                and not direction
                and not evidence
                else NudgeOutcome("error")
            )
        if (
            decision != "intervene"
            or not current_choice
            or not structural_cost
            or not direction
            or not evidence
        ):
            return NudgeOutcome("error")
        return NudgeOutcome(
            "intervene",
            current_choice,
            structural_cost,
            direction,
            evidence,
        )
