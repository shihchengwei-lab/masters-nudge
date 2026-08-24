"""Runtime configuration and neutral data-path resolution."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .local_ollama import DEFAULT_OLLAMA_URL


DEFAULT_MODELS = {
    "anthropic": "sonnet",
    "openai": "gpt-5.6-sol",
    "codex": "gpt-5.6-sol",
    "grok": "",
    "ollama-local": "",
}

REVIEWER_CONFIG_FILE = "reviewer.json"
REVIEWER_CONFIG_KEYS = {"provider", "model", "ollama_url"}
INVALID_CONFIG_PROVIDER = "configuration-error"
REVIEW_TIMEOUT_SEC = 90
HOOK_TIMEOUT_SEC = 120

HOST_DEFAULT_PROVIDERS = {
    "claude": "anthropic",
    "claude_code": "anthropic",
    "codex": "openai",
    "codex_cli": "openai",
}


def _value(
    environment: Mapping[str, str],
    primary: str,
    default: str = "",
) -> str:
    value = environment.get(primary)
    if value is None or str(value).strip() == "":
        return default
    return str(value)


def _positive_int(value: str, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _explicit_value(environment: Mapping[str, str], name: str) -> str | None:
    value = environment.get(name)
    if value is not None and str(value).strip():
        return str(value).strip()
    return None


def reviewer_config_path(data_dir: Path) -> Path:
    return Path(data_dir) / REVIEWER_CONFIG_FILE


def _load_reviewer_config(path: Path) -> tuple[dict[str, str], str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, ""
    except (OSError, ValueError) as exc:
        return {}, f"cannot read reviewer config: {exc}"
    if not isinstance(payload, dict) or set(payload) != REVIEWER_CONFIG_KEYS:
        return {}, "reviewer config has an invalid shape"
    provider = str(payload.get("provider") or "").strip().lower()
    if provider not in {"ollama-local", "grok"}:
        return {}, "reviewer config contains an unsupported provider"
    for key in ("model", "ollama_url"):
        if not isinstance(payload.get(key), str):
            return {}, f"reviewer config has an invalid {key}"
    if provider == "ollama-local" and (
        not payload["model"].strip() or not payload["ollama_url"].strip()
    ):
        return {}, "reviewer config has an invalid local model or ollama_url"
    return {key: str(payload[key]).strip() for key in REVIEWER_CONFIG_KEYS}, ""


@dataclass(frozen=True)
class RuntimePaths:
    runtime_dir: Path
    data_dir: Path
    error_log: Path

    @classmethod
    def resolve(
        cls,
        runtime_dir: Path | None = None,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "RuntimePaths":
        environment = os.environ if environ is None else environ
        user_home = Path(
            environment.get("USERPROFILE") or environment.get("HOME") or Path.home()
        ).expanduser()
        explicit_data = str(environment.get("MASTERS_NUDGE_DATA_DIR") or "").strip()
        data_dir = (
            Path(explicit_data).expanduser()
            if explicit_data
            else user_home / ".masters-nudge" / "data"
        )
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
        error_log = data_dir / "error.log"
        return cls(resolved_runtime, data_dir, error_log)


@dataclass(frozen=True)
class RuntimeSettings:
    provider: str
    model: str
    timeout_sec: int
    checkpoint_timeout_sec: int
    paths: RuntimePaths
    ollama_url: str = DEFAULT_OLLAMA_URL
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
        environment = os.environ if environ is None else environ
        paths = RuntimePaths.resolve(runtime_dir, environ=environment)
        default_provider = HOST_DEFAULT_PROVIDERS.get(
            str(host or "").strip().lower(), "openai"
        )
        configured, config_error = _load_reviewer_config(
            reviewer_config_path(paths.data_dir)
        )
        explicit_provider = _explicit_value(environment, "MASTERS_NUDGE_PROVIDER")
        explicit_model = _explicit_value(environment, "MASTERS_NUDGE_MODEL")
        explicit_url = _explicit_value(environment, "MASTERS_NUDGE_OLLAMA_URL")
        if explicit_provider:
            provider = explicit_provider.lower()
            source = "environment"
            config_error = ""
        elif config_error:
            provider = INVALID_CONFIG_PROVIDER
            source = "invalid_config"
        elif configured:
            provider = configured["provider"]
            source = "config"
        else:
            provider = default_provider
            source = "host_default"
        if explicit_model:
            model = explicit_model
        elif source == "config":
            model = configured["model"]
        else:
            model = DEFAULT_MODELS.get(provider, "")
        ollama_url = (
            explicit_url
            or (configured.get("ollama_url") if source == "config" else "")
            or DEFAULT_OLLAMA_URL
        )
        timeout = min(
            _positive_int(
                _value(environment, "MASTERS_NUDGE_TIMEOUT", str(REVIEW_TIMEOUT_SEC)),
                REVIEW_TIMEOUT_SEC,
            ),
            REVIEW_TIMEOUT_SEC,
        )
        checkpoint_timeout = min(
            _positive_int(
                _value(
                    environment,
                    "MASTERS_NUDGE_CHECKPOINT_TIMEOUT",
                    str(REVIEW_TIMEOUT_SEC),
                ),
                REVIEW_TIMEOUT_SEC,
            ),
            REVIEW_TIMEOUT_SEC,
        )
        return cls(
            provider,
            model,
            timeout,
            checkpoint_timeout,
            paths,
            ollama_url,
            source,
            config_error,
        )


def active_guard(environment: Mapping[str, str] | None = None) -> bool:
    environment = os.environ if environment is None else environment
    return environment.get("MASTERS_NUDGE_ACTIVE") == "1"


def reviewer_environment() -> dict[str, str]:
    return {
        **os.environ,
        "MASTERS_NUDGE_ACTIVE": "1",
    }
