"""Runtime configuration and neutral/legacy path resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


DEFAULT_MODELS = {
    "anthropic": "sonnet",
    "openai": "gpt-5.6-sol",
    "codex": "gpt-5.6-sol",
}


def _value(
    environment: Mapping[str, str],
    primary: str,
    legacy: str,
    default: str = "",
) -> str:
    value = environment.get(primary)
    if value is None or str(value).strip() == "":
        value = environment.get(legacy)
    if value is None or str(value).strip() == "":
        return default
    return str(value)


def _positive_int(value: str, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


@dataclass(frozen=True)
class RuntimePaths:
    runtime_dir: Path
    data_dir: Path
    legacy_data_dir: Path
    error_log: Path

    @classmethod
    def resolve(
        cls,
        runtime_dir: Path | None = None,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "RuntimePaths":
        environment = os.environ if environ is None else environ
        user_home = Path(environment.get("USERPROFILE") or Path.home()).expanduser()
        legacy_claude_dir = Path(
            environment.get("BUDDY_CLAUDE_DIR") or user_home / ".claude"
        ).expanduser()
        legacy_data = legacy_claude_dir / "buddy"

        explicit_data = str(environment.get("MASTERS_NUDGE_DATA_DIR") or "").strip()
        legacy_override = "BUDDY_CLAUDE_DIR" in environment and not explicit_data
        data_dir = (
            Path(explicit_data).expanduser()
            if explicit_data
            else legacy_data
            if legacy_override
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
        error_log = (
            legacy_claude_dir / "buddy-error.log"
            if legacy_override
            else data_dir / "error.log"
        )
        return cls(resolved_runtime, data_dir, legacy_data, error_log)


@dataclass(frozen=True)
class RuntimeSettings:
    provider: str
    model: str
    timeout_sec: int
    checkpoint_timeout_sec: int
    paths: RuntimePaths

    @classmethod
    def from_env(
        cls,
        runtime_dir: Path | None = None,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "RuntimeSettings":
        environment = os.environ if environ is None else environ
        provider = _value(
            environment, "MASTERS_NUDGE_PROVIDER", "BUDDY_PROVIDER", "openai"
        ).lower()
        model = _value(
            environment,
            "MASTERS_NUDGE_MODEL",
            "BUDDY_MODEL",
            DEFAULT_MODELS.get(provider, "sonnet"),
        )
        timeout = _positive_int(
            _value(
                environment, "MASTERS_NUDGE_TIMEOUT", "BUDDY_TIMEOUT", "60"
            ),
            60,
        )
        checkpoint_timeout = _positive_int(
            _value(
                environment,
                "MASTERS_NUDGE_CHECKPOINT_TIMEOUT",
                "BUDDY_CHECKPOINT_TIMEOUT",
                "15",
            ),
            15,
        )
        return cls(
            provider,
            model,
            timeout,
            checkpoint_timeout,
            RuntimePaths.resolve(runtime_dir, environ=environment),
        )


def active_guard(environment: Mapping[str, str] | None = None) -> bool:
    environment = os.environ if environment is None else environment
    return (
        environment.get("MASTERS_NUDGE_ACTIVE") == "1"
        or environment.get("BUDDY_ACTIVE") == "1"
    )


def reviewer_environment() -> dict[str, str]:
    return {
        **os.environ,
        "MASTERS_NUDGE_ACTIVE": "1",
        "BUDDY_ACTIVE": "1",
    }
