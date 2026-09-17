"""Settings, recent attempts, and read-only dependency diagnostics."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from .plugin_inventory import runtime_files
from .runtime import RuntimePaths, RuntimeSettings
from .settings import PROVIDERS, config_path, reset_provider, save_provider
from .storage import recent_nudges as read_recent
from .providers import resolve_codex_bin, _provider_process_kwargs


def list_providers() -> dict:
    return {"providers": list(PROVIDERS.values())}


def get_provider(*, host="codex", environ=None) -> dict:
    settings = RuntimeSettings.from_env(environ=environ, host=host or "codex")
    return {"provider": settings.provider, "model": settings.model,
            "source": settings.configuration_source, "error": settings.configuration_error,
            "path": str(config_path(settings.paths.settings_dir))}


def configure_provider(provider: str, *, model: str = "", environ=None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    try:
        path = save_provider(paths.settings_dir, provider, model=model)
        return {"saved": True, "path": str(path), "error": ""}
    except (OSError, ValueError) as exc:
        return {"saved": False, "error": str(exc)}


def reset_provider_config(*, environ=None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    try:
        reset_provider(paths.settings_dir)
        return {"reset": True, "error": ""}
    except OSError as exc:
        return {"reset": False, "error": str(exc)}


def recent_nudges(limit=20, *, environ=None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    try:
        return {"nudges": read_recent(paths.data_dir, limit=limit), "limit": limit, "error": ""}
    except (OSError, ValueError) as exc:
        return {"nudges": [], "limit": limit, "error": str(exc)}


def _run_cli(command: list[str], environment):
    shell = command[0].lower().endswith((".cmd", ".bat"))
    return subprocess.run(subprocess.list2cmdline(command) if shell else command,
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=10, shell=shell, env=dict(environment), **_provider_process_kwargs())


def doctor(root: Path, host="codex", *, environ=None, **_unused) -> dict:
    env = os.environ if environ is None else environ
    settings = RuntimeSettings.from_env(root, environ=env, host=host)
    binary = shutil.which("codex", path=env.get("PATH"))
    missing = [name for name in runtime_files() if not (root / name).is_file()]
    authenticated = False
    installed = False
    error = settings.configuration_error
    if binary:
        try:
            auth = _run_cli([binary, "login", "status"], env)
            authenticated = auth.returncode == 0 and "logged in" in (auth.stdout + auth.stderr).lower()
            listing = _run_cli([binary, "plugin", "list", "--json"], env)
            if listing.returncode == 0:
                value = json.loads(listing.stdout)
                entries = value.get("installed", []) if isinstance(value, dict) else value
                installed = any(isinstance(entry, dict) and entry.get("enabled") is True and
                                (entry.get("name") == "masters-nudge" or
                                 str(entry.get("pluginId", entry.get("id", ""))).startswith("masters-nudge@"))
                                for entry in entries)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            error = error or str(exc)
    return {"core_ready": not error and not missing and bool(binary) and authenticated and installed,
            "provider": settings.provider, "model": settings.model,
            "codex_cli": binary or "", "provider_authenticated": authenticated,
            "plugin_enabled": installed, "missing_files": missing, "error": error,
            "unverified": ["PostToolBatch 事件支援與完整反饋交付，須實測確認"] }
