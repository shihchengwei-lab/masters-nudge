"""JSON-ready settings operations and installation diagnostics."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Mapping

from .contracts import POST_TOOL_BATCH_EVENT
from .local_ollama import DEFAULT_OLLAMA_URL, inspect_local_ollama
from .plugin_inventory import runtime_files
from .runtime import RuntimePaths, RuntimeSettings
from .storage import recent_nudges as read_recent_nudges
from .settings import (
    LENSES,
    PROVIDERS,
    config_path,
    load_user_settings,
    reset_provider,
    resolve_lens,
    save_lens,
    save_provider,
)


def _selected_hosts(host: str, environment: Mapping[str, str]) -> list[str]:
    if host in {"claude", "codex"}:
        return [host]
    if host == "all":
        return ["claude", "codex"]
    if host != "auto":
        raise ValueError(f"unsupported host: {host}")
    found = [
        name
        for name, executable in (("claude", "claude"), ("codex", "codex"))
        if shutil.which(executable, path=environment.get("PATH"))
    ]
    return found or ["claude", "codex"]


def _nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current.parent != current:
        current = current.parent
    return current


def _data_path_ready(path: Path) -> bool:
    target = path if path.exists() else _nearest_existing_parent(path)
    return target.exists() and os.access(target, os.W_OK)


def _provider_cli(provider: str, environment: Mapping[str, str]) -> str | None:
    executable = {"anthropic": "claude", "openai": "codex"}.get(provider)
    return shutil.which(executable, path=environment.get("PATH")) if executable else None


def _python_version(executable: str | None) -> tuple[int, int, int] | None:
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=3,
            check=False,
        )
        parts = tuple(int(part) for part in result.stdout.strip().split("."))
    except (OSError, subprocess.SubprocessError, TypeError, ValueError):
        return None
    return parts if result.returncode == 0 and len(parts) == 3 else None


def _run_cli(command: list[str], environment: Mapping[str, str]) -> subprocess.CompletedProcess:
    executable = command[0]
    is_windows_script = os.name == "nt" and Path(executable).suffix.lower() in {
        ".bat",
        ".cmd",
    }
    value: list[str] | str = (
        subprocess.list2cmdline(command) if is_windows_script else command
    )
    return subprocess.run(
        value,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=5,
        check=False,
        shell=is_windows_script,
        env=dict(environment),
    )


def _provider_authenticated(
    provider: str,
    executable: str | None,
    environment: Mapping[str, str],
) -> bool:
    if not executable:
        return False
    command = (
        [executable, "auth", "status", "--json"]
        if provider == "anthropic"
        else [executable, "login", "status"]
    )
    try:
        result = _run_cli(command, environment)
        if result.returncode != 0:
            return False
        if provider == "anthropic":
            payload = json.loads(result.stdout)
            return isinstance(payload, dict) and payload.get("loggedIn") is True
        return "logged in" in f"{result.stdout}\n{result.stderr}".lower()
    except (OSError, subprocess.SubprocessError, ValueError):
        return False


def _plugin_version(root: Path, host: str) -> str:
    manifest_name = ".claude-plugin" if host == "claude" else ".codex-plugin"
    candidates = (
        root / manifest_name / "plugin.json",
        root / "plugins" / "masters-nudge" / manifest_name / "plugin.json",
    )
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict) and payload.get("version"):
            return str(payload["version"])
    return ""


def _hook_status(
    host: str,
    environment: Mapping[str, str],
    expected_version: str,
) -> dict[str, object]:
    executable = shutil.which(host, path=environment.get("PATH"))
    if not executable:
        return {"ready": False, "version": "", "error": "host CLI not found"}
    command = [executable, "plugin", "list", "--json"]
    try:
        result = _run_cli(command, environment)
        if result.returncode != 0:
            return {"ready": False, "version": "", "error": "plugin list failed"}
        payload = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"ready": False, "version": "", "error": "plugin list unreadable"}
    entries = payload.get("installed", []) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return {"ready": False, "version": "", "error": "plugin list unreadable"}
    for item in entries:
        if not isinstance(item, dict) or not (
            item.get("name") == "masters-nudge"
            or str(item.get("id") or item.get("pluginId") or "").startswith(
                "masters-nudge@"
            )
        ):
            continue
        version = str(item.get("version") or "")
        enabled = item.get("enabled") is True
        version_matches = not expected_version or version == expected_version
        error = "" if enabled and version_matches else (
            "installed version differs" if enabled else "plugin is disabled"
        )
        return {"ready": enabled and version_matches, "version": version, "error": error}
    return {"ready": False, "version": "", "error": "plugin is not installed"}


def _control_point_status(host: str) -> dict[str, object]:
    if host == "claude":
        return {
            "event": POST_TOOL_BATCH_EVENT,
            "precision": "exact",
            "verified": True,
            "limitation": "",
        }
    return {
        "event": POST_TOOL_BATCH_EVENT,
        "precision": "unverified",
        "verified": False,
        "limitation": (
            "plugin installation does not prove that this Codex build emits "
            "PostToolBatch; verify the control point with an isolated smoke run"
        ),
    }


def list_lenses() -> dict:
    return {
        "lenses": [
            {"id": spec.id, "name": spec.name, "focus": spec.focus}
            for spec in LENSES.values()
        ]
    }


def get_lens(*, environ: Mapping[str, str] | None = None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    selected = resolve_lens(paths.settings_dir)
    settings = load_user_settings(paths.settings_dir)
    return {
        "lens": selected.lens,
        "source": selected.source,
        "path": str(config_path(paths.settings_dir)),
        "error": settings.error,
    }


def set_lens(lens: str, *, environ: Mapping[str, str] | None = None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    result = {
        "saved": False,
        "lens": str(lens or "").strip().lower(),
        "path": str(config_path(paths.settings_dir)),
        "error": "",
    }
    try:
        save_lens(paths.settings_dir, lens)
        result["saved"] = True
    except (OSError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def list_providers() -> dict:
    return {"providers": list(PROVIDERS.values())}


def get_provider(
    *, host: str = "", environ: Mapping[str, str] | None = None
) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    settings = load_user_settings(paths.settings_dir)
    selected_host = str(host or "").strip().lower()
    if selected_host not in {"", "claude", "codex"}:
        raise ValueError(f"unsupported host: {host}")
    resolved = None
    if not settings.error and not settings.provider and selected_host:
        runtime_host = "claude_code" if selected_host == "claude" else "codex_cli"
        resolved = RuntimeSettings.from_env(environ=environ, host=runtime_host)
    return {
        "provider": resolved.provider if resolved else settings.provider,
        "model": resolved.model if resolved else settings.model,
        "ollama_url": settings.ollama_url,
        "source": "invalid_config" if settings.error else "config" if settings.provider else "host_default",
        "path": str(config_path(paths.settings_dir)),
        "error": settings.error,
    }


def configure_provider(
    provider: str,
    *,
    model: str = "",
    ollama_url: str = DEFAULT_OLLAMA_URL,
    environ: Mapping[str, str] | None = None,
    local_inspector: Callable[..., dict] = inspect_local_ollama,
) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    selected = str(provider or "").strip().lower()
    result = {
        "saved": False,
        "provider": selected,
        "model": str(model or "").strip(),
        "ollama_url": str(ollama_url or DEFAULT_OLLAMA_URL).strip(),
        "diagnostic": {},
        "path": str(config_path(paths.settings_dir)),
        "error": "",
    }
    try:
        if selected == "ollama":
            # save_provider performs model and loopback validation first.
            from .local_ollama import normalize_loopback_url, validate_model_name

            selected_model = validate_model_name(model)
            endpoint = normalize_loopback_url(ollama_url)
            diagnostic = local_inspector(endpoint, selected_model, timeout_sec=3)
            if not isinstance(diagnostic, dict):
                raise ValueError("local Ollama inspection returned an invalid result")
            result.update(model=selected_model, ollama_url=endpoint, diagnostic=diagnostic)
            if not diagnostic.get("ready"):
                raise ValueError(str(diagnostic.get("error") or "local Ollama is not ready"))
        save_provider(
            paths.settings_dir,
            selected,
            model=result["model"],
            ollama_url=result["ollama_url"],
        )
        result["saved"] = True
    except (OSError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def reset_provider_config(*, environ: Mapping[str, str] | None = None) -> dict:
    paths = RuntimePaths.resolve(environ=environ)
    result = {
        "reset": False,
        "provider": "",
        "model": "",
        "ollama_url": DEFAULT_OLLAMA_URL,
        "path": str(config_path(paths.settings_dir)),
        "error": "",
    }
    try:
        reset_provider(paths.settings_dir)
        result["reset"] = True
    except OSError as exc:
        result["error"] = str(exc)
    return result


def recent_nudges(
    limit: int = 20, *, environ: Mapping[str, str] | None = None
) -> dict:
    """Return the bounded host-return audit through a stable JSON interface."""
    bounded_limit = max(1, min(int(limit), 100))
    data_dir = RuntimePaths.resolve(environ=environ).data_dir
    try:
        entries = read_recent_nudges(data_dir, limit=bounded_limit)
    except OSError as exc:
        return {"nudges": [], "limit": bounded_limit, "error": str(exc)}
    return {"nudges": entries, "limit": bounded_limit, "error": ""}


def doctor(
    plugin_root: Path,
    host: str = "auto",
    *,
    environ: Mapping[str, str] | None = None,
    hook_python_command: str | None = None,
    local_inspector: Callable[..., dict] = inspect_local_ollama,
) -> dict:
    environment = dict(os.environ if environ is None else environ)
    root = Path(plugin_root).resolve()
    python_ready = sys.version_info >= (3, 10)
    missing_runtime = [
        name for name in runtime_files() if not (root / name).exists()
    ]
    host_results = []
    for name in _selected_hosts(host, environment):
        runtime_host = "claude_code" if name == "claude" else "codex_cli"
        settings = RuntimeSettings.from_env(root, environ=environment, host=runtime_host)
        executable = _provider_cli(settings.provider, environment)
        local = {}
        if settings.provider == "ollama":
            try:
                local = local_inspector(settings.ollama_url, settings.model, timeout_sec=3)
            except Exception as exc:
                local = {"ready": False, "error": f"local Ollama inspection failed: {exc}"}
            if not isinstance(local, dict):
                local = {"ready": False, "error": "local Ollama inspection returned an invalid result"}
            provider_ready = bool(local.get("ready"))
            provider_authenticated = provider_ready
        else:
            provider_authenticated = _provider_authenticated(
                settings.provider, executable, environment
            )
            provider_ready = bool(executable) and provider_authenticated
        expected_plugin_version = _plugin_version(root, name)
        hook = _hook_status(name, environment, expected_plugin_version)
        hook_ready = bool(hook["ready"])
        hook_command = (
            str(hook_python_command or environment.get("CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND") or "python").strip()
            if name == "claude"
            else "auto"
        )
        hook_python = (
            shutil.which(hook_command, path=environment.get("PATH"))
            if name == "claude" and hook_command
            else sys.executable
        )
        hook_version = _python_version(hook_python)
        control_point = _control_point_status(name)
        host_results.append(
            {
                "host": name,
                "provider": settings.provider,
                "model": settings.model,
                "configuration_source": settings.configuration_source,
                "configuration_error": settings.configuration_error,
                "provider_cli": executable or "",
                "provider_ready": provider_ready,
                "provider_authenticated": provider_authenticated,
                "local": local,
                "hook_python_command": hook_command,
                "hook_python": hook_python or "",
                "hook_python_version": ".".join(map(str, hook_version)) if hook_version else "",
                "hook_python_ready": bool(hook_version and hook_version >= (3, 10, 0)),
                "hook_ready": hook_ready,
                "hook_version": hook["version"],
                "expected_hook_version": expected_plugin_version,
                "hook_error": hook["error"],
                "trust": "inspect in /hooks" if name == "codex" else "not required",
                "control_point": control_point,
            }
        )
    data_dir = RuntimePaths.resolve(root, environ=environment).data_dir
    data_ready = _data_path_ready(data_dir)
    core_ready = (
        python_ready
        and not missing_runtime
        and data_ready
        and bool(host_results)
        and all(
            item["provider_ready"]
            and item["hook_python_ready"]
            and item["hook_ready"]
            and item["control_point"]["verified"]
            for item in host_results
        )
    )
    return {
        "core_ready": core_ready,
        "python": {
            "ready": python_ready,
            "version": ".".join(map(str, sys.version_info[:3])),
            "executable": sys.executable,
        },
        "runtime": {"root": str(root), "missing": missing_runtime},
        "data": {"path": str(data_dir), "writable": data_ready},
        "hosts": host_results,
    }
