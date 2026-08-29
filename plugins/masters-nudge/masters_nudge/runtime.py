"""Runtime paths and settings resolved from one persistent config file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .local_ollama import DEFAULT_OLLAMA_URL
from .settings import load_user_settings


DEFAULT_MODELS = {
    "anthropic": "sonnet",
    "openai": "gpt-5.6-sol",
    "ollama": "",
}
INVALID_CONFIG_PROVIDER = "configuration-error"
PROVIDER_TIMEOUT_SEC = 90
HOOK_TIMEOUT_SEC = 120

HOST_DEFAULT_PROVIDERS = {
    "claude": "anthropic",
    "claude_code": "anthropic",
    "codex": "openai",
    "codex_cli": "openai",
}


@dataclass(frozen=True)
class RuntimePaths:
    runtime_dir: Path
    data_dir: Path
    settings_dir: Path
    error_log: Path

    @classmethod
    def resolve(
        cls,
        runtime_dir: Path | None = None,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "RuntimePaths":
        environment = os.environ if environ is None else environ
        home_value = environment.get("USERPROFILE") or environment.get("HOME")
        try:
            user_home = Path(home_value).expanduser() if home_value else Path.home()
        except RuntimeError:
            user_home = Path.cwd()
        explicit_data = str(environment.get("MASTERS_NUDGE_DATA_DIR") or "").strip()
        if explicit_data:
            data_dir = Path(explicit_data).expanduser()
            settings_dir = data_dir
        else:
            settings_dir = user_home / ".masters-nudge"
            data_dir = settings_dir / "data"
        explicit_runtime = str(
            environment.get("MASTERS_NUDGE_RUNTIME_DIR") or ""
        ).strip()
        resolved_runtime = (
            Path(explicit_runtime).expanduser()
            if explicit_runtime
            else Path(runtime_dir).resolve()
            if runtime_dir is not None
            else user_home / ".masters-nudge" / "runtime"
        )
        return cls(resolved_runtime, data_dir, settings_dir, data_dir / "error.log")


@dataclass(frozen=True)
class RuntimeSettings:
    provider: str
    model: str
    paths: RuntimePaths
    ollama_url: str = DEFAULT_OLLAMA_URL
    lens: str = "automatic"
    configuration_source: str = "host_default"
    configuration_error: str = ""

    @classmethod
    def from_env(
        cls,
        runtime_dir: Path | None = None,
        *,
        environ: Mapping[str, str] | None = None,
        host: str | None = None,
    ) -> "RuntimeSettings":
        """Resolve paths from the environment and manual choices from config.json."""
        environment = os.environ if environ is None else environ
        paths = RuntimePaths.resolve(runtime_dir, environ=environment)
        default_provider = HOST_DEFAULT_PROVIDERS.get(
            str(host or "").strip().lower(), "openai"
        )
        configured = load_user_settings(paths.settings_dir)
        if configured.error:
            provider = INVALID_CONFIG_PROVIDER
            model = ""
            source = "invalid_config"
        elif configured.provider:
            provider = configured.provider
            model = configured.model or DEFAULT_MODELS.get(provider, "")
            source = "config"
        else:
            provider = default_provider
            model = DEFAULT_MODELS[provider]
            source = "host_default"
        return cls(
            provider=provider,
            model=model,
            paths=paths,
            ollama_url=configured.ollama_url or DEFAULT_OLLAMA_URL,
            lens=configured.lens if not configured.error else "automatic",
            configuration_source=source,
            configuration_error=configured.error,
        )


def active_guard(environment: Mapping[str, str] | None = None) -> bool:
    environment = os.environ if environment is None else environment
    return environment.get("MASTERS_NUDGE_ACTIVE") == "1"


def provider_environment() -> dict[str, str]:
    return {**os.environ, "MASTERS_NUDGE_ACTIVE": "1"}
