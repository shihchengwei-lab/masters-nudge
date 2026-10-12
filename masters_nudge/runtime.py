"""Resolve paths/settings once, separately from Provider judgment."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from .settings import load_user_settings

DEFAULT_MODEL = "gpt-5.6-sol"
PROVIDER_REASONING_EFFORT = "medium"
PROVIDER_TIMEOUT_SEC = 1200
HOOK_TIMEOUT_SEC = 1320
PROFILES = ("software-engineering", "performance")


@dataclass(frozen=True)
class RuntimePaths:
    runtime_dir: Path
    data_dir: Path
    settings_dir: Path
    error_log: Path

    @classmethod
    def resolve(cls, runtime_dir=None, *, environ=None):
        env = os.environ if environ is None else environ
        user_dir = Path(env.get("USERPROFILE") or env.get("HOME") or Path.home())
        settings = Path(env["MASTERS_NUDGE_DATA_DIR"]) if env.get("MASTERS_NUDGE_DATA_DIR") else user_dir / ".masters-nudge"
        data = settings if env.get("MASTERS_NUDGE_DATA_DIR") else settings / "data"
        if env.get("MASTERS_NUDGE_PROFILE") == "performance":
            data = data / "performance"
        runtime = Path(env.get("MASTERS_NUDGE_RUNTIME_DIR") or runtime_dir or user_dir / ".masters-nudge" / "runtime")
        return cls(runtime.resolve(), data, settings, data / "error.log")


@dataclass(frozen=True)
class RuntimeSettings:
    provider: str
    model: str
    paths: RuntimePaths
    configuration_source: str = "default"
    configuration_error: str = ""
    strict: bool = False
    profile: str = "software-engineering"

    @property
    def prompt_file(self) -> Path:
        name = "performance-prompt.txt" if self.profile == "performance" else "buddy-prompt.txt"
        return self.paths.runtime_dir / name

    @classmethod
    def from_env(cls, runtime_dir=None, *, environ=None, host=None):
        env = os.environ if environ is None else environ
        paths = RuntimePaths.resolve(runtime_dir, environ=env)
        config = load_user_settings(paths.settings_dir)
        error = config.error
        profile = env.get("MASTERS_NUDGE_PROFILE", "software-engineering")
        if profile not in PROFILES:
            error = f"不支援 profile：{profile}"
        if host not in (None, "codex", "codex_cli"):
            error = f"不支援執行環境：{host}"
        return cls(config.provider or "openai", config.model or DEFAULT_MODEL, paths,
                   "config" if config.provider else "default", error,
                   env.get("MASTERS_NUDGE_TEST_MODE") == "1", profile)


def active_guard(environment: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environment is None else environment
    return env.get("MASTERS_NUDGE_ACTIVE") == "1"


def provider_environment() -> dict[str, str]:
    return {**os.environ, "MASTERS_NUDGE_ACTIVE": "1"}
