"""The single persistent user-settings contract for Masters' Nudge."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from .lenses import LENSES
from .local_ollama import DEFAULT_OLLAMA_URL, normalize_loopback_url, validate_model_name


CONFIG_FILE = "config.json"
PROVIDER_IDS = ("anthropic", "openai", "ollama")

PROVIDERS = {
    "anthropic": {"id": "anthropic", "name": "Anthropic", "local": False},
    "openai": {"id": "openai", "name": "OpenAI", "local": False},
    "ollama": {"id": "ollama", "name": "Ollama", "local": True},
}


@dataclass(frozen=True)
class UserSettings:
    lens: str = "simplicity"
    provider: str = ""
    model: str = ""
    ollama_url: str = DEFAULT_OLLAMA_URL
    error: str = ""


@dataclass(frozen=True)
class LensSelection:
    lens: str
    persona: str
    source: str


def config_path(data_dir: Path) -> Path:
    return Path(data_dir) / CONFIG_FILE


def _payload(settings: UserSettings) -> dict[str, str]:
    value = asdict(settings)
    value.pop("error", None)
    return value


def load_user_settings(data_dir: Path) -> UserSettings:
    path = config_path(data_dir)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return UserSettings()
    except (OSError, UnicodeError, ValueError) as exc:
        return UserSettings(error=f"cannot read config: {exc}")
    if not isinstance(value, dict) or set(value) != {
        "lens",
        "provider",
        "model",
        "ollama_url",
    }:
        return UserSettings(error="config has an invalid shape")
    if not all(isinstance(value.get(key), str) for key in value):
        return UserSettings(error="config values must be strings")
    lens = value["lens"].strip().lower()
    provider = value["provider"].strip().lower()
    model = value["model"].strip()
    url = value["ollama_url"].strip()
    if lens not in LENSES:
        return UserSettings(error="config contains an unsupported lens")
    if provider not in {"", *PROVIDERS}:
        return UserSettings(error="config contains an unsupported provider")
    if provider == "ollama":
        try:
            model = validate_model_name(model)
            url = normalize_loopback_url(url)
        except ValueError as exc:
            return UserSettings(error=f"config contains invalid Ollama settings: {exc}")
    elif not url:
        url = DEFAULT_OLLAMA_URL
    return UserSettings(lens, provider, model, url)


def save_user_settings(data_dir: Path, settings: UserSettings) -> Path:
    if settings.error:
        settings = replace(settings, error="")
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".tmp",
        prefix="settings-",
        dir=data_dir,
        delete=False,
    )
    temp_path = Path(handle.name)
    try:
        json.dump(_payload(settings), handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            pass
        os.replace(temp_path, config_path(data_dir))
    finally:
        try:
            handle.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return config_path(data_dir)


def resolve_lens(data_dir: Path) -> LensSelection:
    settings = load_user_settings(data_dir)
    lens = settings.lens if not settings.error else "simplicity"
    source = "config" if config_path(data_dir).exists() and not settings.error else "default"
    if settings.error:
        source = "invalid_config"
    return LensSelection(lens, LENSES[lens].persona, source)


def save_lens(data_dir: Path, lens: str) -> Path:
    selected = str(lens or "").strip().lower()
    if selected not in LENSES:
        raise ValueError(f"unsupported lens: {lens!r}")
    current = load_user_settings(data_dir)
    if current.error:
        current = UserSettings()
    return save_user_settings(data_dir, replace(current, lens=selected))


def save_provider(
    data_dir: Path,
    provider: str,
    *,
    model: str = "",
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> Path:
    selected = str(provider or "").strip().lower()
    if selected not in PROVIDERS:
        raise ValueError(f"unsupported provider: {provider!r}")
    selected_model = str(model or "").strip()
    endpoint = str(ollama_url or DEFAULT_OLLAMA_URL).strip()
    if selected == "ollama":
        selected_model = validate_model_name(selected_model)
        endpoint = normalize_loopback_url(endpoint)
    current = load_user_settings(data_dir)
    if current.error:
        current = UserSettings()
    return save_user_settings(
        data_dir,
        replace(
            current,
            provider=selected,
            model=selected_model,
            ollama_url=endpoint,
        ),
    )


def reset_provider(data_dir: Path) -> Path:
    current = load_user_settings(data_dir)
    if current.error:
        current = UserSettings()
    return save_user_settings(
        data_dir,
        replace(
            current,
            provider="",
            model="",
            ollama_url=DEFAULT_OLLAMA_URL,
        ),
    )
