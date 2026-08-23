"""Installation diagnostics and conservative legacy-hook migration."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from .contracts import safe_identifier
from .local_ollama import (
    DEFAULT_OLLAMA_URL,
    inspect_local_ollama,
    normalize_loopback_url,
    validate_model_name,
)
from .plugin_inventory import (
    INVENTORY_FILE,
    PLUGIN_RUNTIME_FILES,
    SOURCE_RUNTIME_FILES,
    load_plugin_inventory,
)
from .runtime import RuntimePaths, RuntimeSettings, reviewer_config_path


LEGACY_PERSONA_STAGES = {
    "general": "build",
    "jeff": "design",
    "beck": "build",
    "fowler": "evolve",
    "linus": "review",
}
SPECIALIST_PERSONAS = {"lamport", "carmack"}
STAGES = {"design", "build", "evolve", "review"}
LEGACY_ENVIRONMENT_MAPPINGS = {
    "BUDDY_ACTIVE": "MASTERS_NUDGE_ACTIVE",
    "BUDDY_CHECKPOINT_TIMEOUT": "MASTERS_NUDGE_CHECKPOINT_TIMEOUT",
    "BUDDY_CLAUDE_DIR": "MASTERS_NUDGE_DATA_DIR",
    "BUDDY_MODEL": "MASTERS_NUDGE_MODEL",
    "BUDDY_OLLAMA_URL": "MASTERS_NUDGE_OLLAMA_URL",
    "BUDDY_PROVIDER": "MASTERS_NUDGE_PROVIDER",
    "BUDDY_SHADOW_EVALUATION_DAYS": "MASTERS_NUDGE_SHADOW_EVALUATION_DAYS",
    "BUDDY_SHADOW_TARGET_CALLS": "MASTERS_NUDGE_SHADOW_TARGET_CALLS",
    "BUDDY_SPRITE_PATH": "MASTERS_NUDGE_SPRITE_PATH",
    "BUDDY_TIMEOUT": "MASTERS_NUDGE_TIMEOUT",
    "BUDDY_WORKSPACE": "MASTERS_NUDGE_WORKSPACE",
}

CLAUDE_LEGACY_COMMANDS = {
    "bash ~/.claude/scripts/buddy/checkpoint.sh",
    "bash ~/.claude/scripts/buddy/buddy.sh",
    "bash ~/.claude/scripts/buddy/inject.sh",
}

CODEX_LEGACY_COMMANDS = {
    "python3 ~/.masters-nudge/runtime/hook_entry.py --host codex_cli",
    "python3 ~/.masters-nudge/runtime/hook_entry.py --host codex_cli --detach-stop",
    'py -3 "%USERPROFILE%\\.masters-nudge\\runtime\\hook_entry.py" --host codex_cli',
    'py -3 "%USERPROFILE%\\.masters-nudge\\runtime\\hook_entry.py" --host codex_cli --detach-stop',
}


def _home(environment: Mapping[str, str]) -> Path:
    value = environment.get("USERPROFILE") or environment.get("HOME")
    return Path(value).expanduser() if value else Path.home()


def config_path_for(host: str, environment: Mapping[str, str]) -> Path:
    home = _home(environment)
    if host == "claude":
        return home / ".claude" / "settings.json"
    if host == "codex":
        return home / ".codex" / "hooks.json"
    raise ValueError(f"unsupported host: {host}")


def _selected_hosts(host: str, environment: Mapping[str, str]) -> list[str]:
    if host in {"claude", "codex"}:
        return [host]
    if host == "all":
        return ["claude", "codex"]
    if host != "auto":
        raise ValueError(f"unsupported host: {host}")
    path = environment.get("PATH")
    found = [
        name
        for name, executable in (("claude", "claude"), ("codex", "codex"))
        if shutil.which(executable, path=path)
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
    if provider == "anthropic":
        executable = "claude"
    elif provider in {"openai", "codex"}:
        executable = "codex"
    elif provider == "grok":
        executable = "grok"
    else:
        return None
    return shutil.which(executable, path=environment.get("PATH"))


def _python_version(executable: str | None) -> tuple[int, int, int] | None:
    if not executable:
        return None
    try:
        result = subprocess.run(
            [
                executable,
                "-c",
                "import sys; print('.'.join(map(str, sys.version_info[:3])))",
            ],
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


def _legacy_commands(host: str) -> set[str]:
    return CLAUDE_LEGACY_COMMANDS if host == "claude" else CODEX_LEGACY_COMMANDS


def _command_values(handler: dict) -> list[str]:
    return [
        str(handler[key]).strip()
        for key in ("command", "commandWindows", "command_windows")
        if isinstance(handler.get(key), str) and str(handler[key]).strip()
    ]


def _looks_like_legacy(command: str, host: str) -> bool:
    normalized = command.replace("\\", "/").lower()
    if host == "claude":
        return "/.claude/scripts/buddy/" in normalized
    return (
        "/.masters-nudge/runtime/hook_entry.py" in normalized
        or "masters-nudge\\runtime\\hook_entry.py" in command.lower()
    )


def _classify_handler(handler: object, host: str) -> str:
    if not isinstance(handler, dict) or handler.get("type") != "command":
        return "other"
    commands = _command_values(handler)
    if not commands:
        return "other"
    known = _legacy_commands(host)
    if all(command in known for command in commands):
        return "exact"
    if any(_looks_like_legacy(command, host) for command in commands):
        return "near"
    return "other"


def inspect_legacy_config(path: Path, host: str) -> dict:
    result = {
        "host": host,
        "path": str(path),
        "exists": path.exists(),
        "exact": 0,
        "near": [],
        "error": "",
    }
    if not path.exists():
        return result
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result["error"] = f"cannot read JSON: {exc}"
        return result
    hooks = document.get("hooks") if isinstance(document, dict) else None
    if not isinstance(hooks, dict):
        return result
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group_index, group in enumerate(groups):
            handlers = group.get("hooks") if isinstance(group, dict) else None
            if not isinstance(handlers, list):
                continue
            for handler_index, handler in enumerate(handlers):
                classification = _classify_handler(handler, host)
                if classification == "exact":
                    result["exact"] += 1
                elif classification == "near":
                    result["near"].append(
                        {
                            "event": event,
                            "group": group_index,
                            "handler": handler_index,
                            "commands": _command_values(handler),
                        }
                    )
    return result


def _remove_exact_handlers(document: dict, host: str) -> tuple[dict, int]:
    updated = copy.deepcopy(document)
    hooks = updated.get("hooks")
    if not isinstance(hooks, dict):
        return updated, 0
    removed = 0
    for event in list(hooks):
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                kept_groups.append(group)
                continue
            handlers = []
            for handler in group["hooks"]:
                if _classify_handler(handler, host) == "exact":
                    removed += 1
                else:
                    handlers.append(handler)
            if handlers:
                next_group = dict(group)
                next_group["hooks"] = handlers
                kept_groups.append(next_group)
        if kept_groups:
            hooks[event] = kept_groups
        else:
            hooks.pop(event, None)
    return updated, removed


def _backup_path(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = path.with_name(f"{path.name}.masters-nudge.{stamp}.bak")
    suffix = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.masters-nudge.{stamp}.{suffix}.bak")
        suffix += 1
    return candidate


def _atomic_json_write(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    original_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temp_path = Path(handle.name)
    try:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        os.chmod(temp_path, original_mode)
        os.replace(temp_path, path)
    finally:
        try:
            handle.close()
        except Exception:
            pass
        temp_path.unlink(missing_ok=True)


def _legacy_data_dir(environment: Mapping[str, str]) -> Path:
    claude_dir = Path(
        environment.get("BUDDY_CLAUDE_DIR") or _home(environment) / ".claude"
    ).expanduser()
    return claude_dir / "buddy"


def _neutral_data_dir(environment: Mapping[str, str]) -> Path:
    return RuntimePaths.resolve(environ=environment).data_dir


def _read_json_object(path: Path) -> tuple[dict, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, f"cannot read JSON: {exc}"
    if not isinstance(payload, dict):
        return {}, "JSON root must be an object"
    return payload, ""


def inspect_legacy_lifecycle(environment: Mapping[str, str]) -> dict:
    legacy_path = _legacy_data_dir(environment) / "config.json"
    destination = _neutral_data_dir(environment) / "config.json"
    source = legacy_path
    result = {
        "source": str(source),
        "destination": str(destination),
        "exists": False,
        "persona": "",
        "stage": "",
        "status": "not_found",
        "applied": False,
        "backup": "",
        "error": "",
    }

    if destination.exists():
        destination_payload, error = _read_json_object(destination)
        if error:
            result.update(
                exists=True, source=str(destination), status="invalid", error=error
            )
            return result
        if (
            set(destination_payload) == {"stage"}
            and str(destination_payload.get("stage") or "").strip().lower() in STAGES
        ):
            result.update(
                exists=True,
                source=str(destination),
                stage=str(destination_payload["stage"]).strip().lower(),
                status="already_migrated",
            )
            return result
        if set(destination_payload) == {"persona"}:
            source = destination
            result["source"] = str(source)
        else:
            result.update(
                exists=True,
                source=str(destination),
                status="conflict",
                error="destination config is not a canonical stage config",
            )
            return result

    if not source.exists():
        return result
    result["exists"] = True
    payload, error = _read_json_object(source)
    if error:
        result.update(status="invalid", error=error)
        return result
    if set(payload) == {"persona"}:
        persona = str(payload.get("persona") or "").strip().lower()
    elif (
        set(payload) == {"stage"}
        and str(payload.get("stage") or "").strip().lower() == "general"
    ):
        persona = "general"
    else:
        result.update(
            status="invalid",
            error="legacy lifecycle config must contain only persona",
        )
        return result
    result["persona"] = persona
    if persona in SPECIALIST_PERSONAS:
        result.update(
            status="manual_required",
            error=f"{persona} has no lossless lifecycle-stage mapping",
        )
        return result
    stage = LEGACY_PERSONA_STAGES.get(persona)
    if not stage:
        result.update(
            status="invalid", error=f"unsupported legacy persona: {persona!r}"
        )
        return result
    result.update(stage=stage, status="would_migrate")
    return result


def migrate_legacy_lifecycle(
    environment: Mapping[str, str], *, apply: bool = False
) -> dict:
    result = inspect_legacy_lifecycle(environment)
    if not apply or result["status"] != "would_migrate":
        return result
    source = Path(result["source"])
    destination = Path(result["destination"])
    backup: Path | None = None
    try:
        if source.resolve() == destination.resolve():
            backup = _backup_path(source)
            shutil.copy2(source, backup)
            result["backup"] = str(backup)
        _atomic_json_write(destination, {"stage": result["stage"]})
    except Exception as exc:
        if backup is not None and backup.exists():
            try:
                shutil.copy2(backup, destination)
            except OSError as restore_exc:
                result["error"] = (
                    f"migration failed: {exc}; restore failed: {restore_exc}"
                )
                result["status"] = "error"
                return result
        result.update(status="error", error=f"migration failed: {exc}")
        return result
    result.update(status="migrated", applied=True)
    return result


def _validate_jsonl(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return f"cannot read log: {exc}"
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except (TypeError, ValueError) as exc:
            return f"line {line_number} is not valid JSON: {exc}"
        if not isinstance(payload, dict):
            return f"line {line_number} must be a JSON object"
    return ""


def inspect_legacy_logs(environment: Mapping[str, str]) -> dict:
    source_dir = _legacy_data_dir(environment)
    destination_dir = _neutral_data_dir(environment)
    items = []
    for source in sorted(source_dir.glob("*.log")) if source_dir.exists() else []:
        safe_stem = safe_identifier(source.stem)
        destination = destination_dir / f"claude_code--{safe_stem}.log"
        error = ""
        if safe_stem != source.stem:
            error = "legacy log filename is not a safe session identifier"
        else:
            error = _validate_jsonl(source)
        if error:
            status = "invalid"
        elif destination.exists():
            try:
                status = (
                    "already_copied"
                    if destination.read_bytes() == source.read_bytes()
                    else "conflict"
                )
            except OSError as exc:
                status = "invalid"
                error = f"cannot compare destination: {exc}"
        else:
            status = "would_copy"
        items.append(
            {
                "source_name": source.name,
                "source": str(source),
                "destination": str(destination),
                "status": status,
                "applied": False,
                "error": error,
            }
        )
    return {
        "source": str(source_dir),
        "destination": str(destination_dir),
        "items": items,
    }


def migrate_legacy_logs(environment: Mapping[str, str], *, apply: bool = False) -> dict:
    result = inspect_legacy_logs(environment)
    if not apply:
        return result
    for item in result["items"]:
        if item["status"] != "would_copy":
            continue
        source = Path(item["source"])
        destination = Path(item["destination"])
        created = False
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as reader, destination.open("xb") as writer:
                created = True
                shutil.copyfileobj(reader, writer)
                writer.flush()
                os.fsync(writer.fileno())
        except Exception as exc:
            if created:
                try:
                    destination.unlink(missing_ok=True)
                except OSError:
                    pass
            item.update(status="error", error=f"migration failed: {exc}")
            continue
        item.update(status="copied", applied=True)
    return result


def inspect_legacy_environment(environment: Mapping[str, str]) -> list[dict[str, str]]:
    mappings = [
        {"legacy": legacy, "replacement": replacement}
        for legacy, replacement in sorted(LEGACY_ENVIRONMENT_MAPPINGS.items())
        if str(environment.get(legacy) or "").strip()
    ]
    for legacy in ("BUDDY_PERSONA", "MASTERS_NUDGE_PERSONA"):
        if str(environment.get(legacy) or "").strip():
            mappings.append(
                {
                    "legacy": legacy,
                    "replacement": "MASTERS_NUDGE_STAGE",
                    "note": "choose design|build|evolve|review; do not copy the persona value",
                }
            )
    return sorted(mappings, key=lambda item: item["legacy"])


def migrate_legacy_config(path: Path, host: str, *, apply: bool = False) -> dict:
    inspection = inspect_legacy_config(path, host)
    result = {**inspection, "applied": False, "removed": 0, "backup": ""}
    if inspection["error"] or inspection["near"] or not inspection["exact"]:
        return result
    if not apply:
        return result
    backup: Path | None = None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        updated, removed = _remove_exact_handlers(document, host)
        backup = _backup_path(path)
        shutil.copy2(path, backup)
        result["backup"] = str(backup)
        _atomic_json_write(path, updated)
    except Exception as exc:
        restore_error = ""
        if backup is not None and backup.exists():
            try:
                shutil.copy2(backup, path)
            except OSError as restore_exc:
                restore_error = f"; restore failed: {restore_exc}"
        result["error"] = f"migration failed: {exc}{restore_error}"
        return result
    result.update(applied=True, removed=removed)
    return result


def migrate_legacy(
    host: str = "all",
    *,
    apply: bool = False,
    environ: Mapping[str, str] | None = None,
) -> dict:
    environment = dict(os.environ if environ is None else environ)
    targets = [
        (name, config_path_for(name, environment))
        for name in _selected_hosts(host, environment)
    ]
    results = [migrate_legacy_config(path, name, apply=False) for name, path in targets]
    lifecycle = migrate_legacy_lifecycle(environment)
    logs = migrate_legacy_logs(environment)
    environment_aliases = inspect_legacy_environment(environment)
    unsafe = (
        any(item["error"] or item["near"] for item in results)
        or lifecycle["status"] in {"invalid", "conflict", "error"}
        or any(
            item["status"] in {"invalid", "conflict", "error"} for item in logs["items"]
        )
    )
    lifecycle_manual = lifecycle["status"] == "manual_required"
    if apply and not unsafe and not lifecycle_manual:
        lifecycle = migrate_legacy_lifecycle(environment, apply=True)
        logs = migrate_legacy_logs(environment, apply=True)
        unsafe = lifecycle["status"] == "error" or any(
            item["status"] == "error" for item in logs["items"]
        )
    if apply and not unsafe and not lifecycle_manual:
        results = [
            migrate_legacy_config(path, name, apply=True) for name, path in targets
        ]
        unsafe = any(item["error"] or item["near"] for item in results)
    return {
        "apply": apply,
        "unsafe": unsafe,
        "manual_required": lifecycle_manual or bool(environment_aliases),
        "results": results,
        "lifecycle": lifecycle,
        "logs": logs,
        "environment": environment_aliases,
    }


def configure_local(
    model: str,
    url: str = DEFAULT_OLLAMA_URL,
    *,
    environ: Mapping[str, str] | None = None,
    inspector: Callable[..., dict] = inspect_local_ollama,
) -> dict:
    environment = dict(os.environ if environ is None else environ)
    path = reviewer_config_path(RuntimePaths.resolve(environ=environment).data_dir)
    result = {
        "saved": False,
        "path": str(path),
        "provider": "ollama-local",
        "model": str(model or "").strip(),
        "ollama_url": str(url or "").strip(),
        "diagnostic": {},
        "error": "",
    }
    try:
        selected_model = validate_model_name(model)
        endpoint = normalize_loopback_url(url)
    except ValueError as exc:
        result["error"] = str(exc)
        return result
    try:
        diagnostic = inspector(endpoint, selected_model, timeout_sec=3)
    except Exception as exc:
        result["error"] = f"local Ollama inspection failed: {exc}"
        return result
    if not isinstance(diagnostic, dict):
        result["error"] = "local Ollama inspection returned an invalid result"
        return result
    result.update(model=selected_model, ollama_url=endpoint)
    result["diagnostic"] = diagnostic
    if not diagnostic.get("ready"):
        result["error"] = str(diagnostic.get("error") or "local Ollama is not ready")
        return result
    try:
        _atomic_json_write(
            path,
            {
                "provider": "ollama-local",
                "model": selected_model,
                "ollama_url": endpoint,
            },
        )
    except OSError as exc:
        result["error"] = f"cannot save reviewer config: {exc}"
        return result
    result["saved"] = True
    return result


def configure_grok(
    model: str = "",
    *,
    environ: Mapping[str, str] | None = None,
) -> dict:
    environment = dict(os.environ if environ is None else environ)
    path = reviewer_config_path(RuntimePaths.resolve(environ=environment).data_dir)
    executable = _provider_cli("grok", environment)
    result = {
        "saved": False,
        "path": str(path),
        "provider": "grok",
        "model": str(model or "").strip(),
        "provider_cli": executable or "",
        "error": "",
    }
    if not executable:
        result["error"] = "grok CLI not found in PATH"
        return result
    try:
        _atomic_json_write(
            path,
            {
                "provider": "grok",
                "model": result["model"],
                "ollama_url": "",
            },
        )
    except OSError as exc:
        result["error"] = f"cannot save reviewer config: {exc}"
        return result
    result["saved"] = True
    return result


def inspect_grok_cli(
    executable: str,
    *,
    environ: Mapping[str, str] | None = None,
    timeout_sec: int = 5,
) -> dict:
    """Check that Grok Build has an authenticated subscription session."""
    environment = dict(os.environ if environ is None else environ)
    environment.pop("XAI_API_KEY", None)
    environment["MASTERS_NUDGE_ACTIVE"] = "1"
    try:
        completed = subprocess.run(
            [executable, "models"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
            timeout=timeout_sec,
            **(
                {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
                if os.name == "nt"
                else {}
            ),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ready": False, "authenticated": False, "error": str(exc)}
    output = f"{completed.stdout}\n{completed.stderr}".strip()
    unauthenticated = "not authenticated" in output.lower()
    ready = completed.returncode == 0 and not unauthenticated
    error = (
        ""
        if ready
        else (
            "grok CLI is not authenticated"
            if unauthenticated
            else f"grok CLI exit {completed.returncode}"
        )
    )
    return {"ready": ready, "authenticated": ready, "error": error}


def reset_local(*, environ: Mapping[str, str] | None = None) -> dict:
    environment = dict(os.environ if environ is None else environ)
    path = reviewer_config_path(RuntimePaths.resolve(environ=environment).data_dir)
    try:
        existed = path.exists()
        path.unlink(missing_ok=True)
    except OSError as exc:
        return {
            "reset": False,
            "removed": False,
            "path": str(path),
            "error": f"cannot remove reviewer config: {exc}",
        }
    return {
        "reset": True,
        "removed": existed,
        "path": str(path),
        "error": "",
    }


def doctor(
    plugin_root: Path,
    host: str = "auto",
    *,
    environ: Mapping[str, str] | None = None,
    hook_python_command: str | None = None,
    local_inspector: Callable[..., dict] = inspect_local_ollama,
    grok_inspector: Callable[..., dict] = inspect_grok_cli,
) -> dict:
    environment = dict(os.environ if environ is None else environ)
    root = Path(plugin_root).resolve()
    python_ready = sys.version_info >= (3, 10)
    is_plugin = (root / ".claude-plugin" / "plugin.json").exists() or (
        root / ".codex-plugin" / "plugin.json"
    ).exists()
    required_runtime = SOURCE_RUNTIME_FILES
    inventory_error = ""
    if is_plugin:
        installed_files, inventory_error = load_plugin_inventory(root)
        if installed_files:
            required_runtime = installed_files
        else:
            required_runtime = tuple(
                dict.fromkeys((*SOURCE_RUNTIME_FILES, *PLUGIN_RUNTIME_FILES))
            )
    missing_runtime = [name for name in required_runtime if not (root / name).exists()]
    if inventory_error:
        missing_runtime.append(INVENTORY_FILE)
    host_results = []
    for name in _selected_hosts(host, environment):
        runtime_host = "claude_code" if name == "claude" else "codex_cli"
        settings = RuntimeSettings.from_env(
            root, environ=environment, host=runtime_host
        )
        executable = _provider_cli(settings.provider, environment)
        local = {}
        grok = {}
        if settings.provider == "ollama-local":
            try:
                local = local_inspector(
                    settings.ollama_url,
                    settings.model,
                    timeout_sec=3,
                )
            except Exception as exc:
                local = {
                    "ready": False,
                    "endpoint": settings.ollama_url,
                    "endpoint_loopback": False,
                    "server_ready": False,
                    "cloud_disabled": False,
                    "model_ready": False,
                    "model_local": False,
                    "error": f"local Ollama inspection failed: {exc}",
                }
            if not isinstance(local, dict):
                local = {
                    "ready": False,
                    "endpoint": settings.ollama_url,
                    "endpoint_loopback": False,
                    "server_ready": False,
                    "cloud_disabled": False,
                    "model_ready": False,
                    "model_local": False,
                    "error": "local Ollama inspection returned an invalid result",
                }
            provider_ready = bool(local.get("ready"))
        elif settings.provider == "grok":
            if executable:
                try:
                    grok = grok_inspector(
                        executable, environ=environment, timeout_sec=5
                    )
                except Exception as exc:
                    grok = {
                        "ready": False,
                        "authenticated": False,
                        "error": f"grok CLI inspection failed: {exc}",
                    }
            else:
                grok = {
                    "ready": False,
                    "authenticated": False,
                    "error": "grok CLI not found",
                }
            provider_ready = bool(grok.get("ready"))
        else:
            provider_ready = bool(executable)
        hook_command = (
            str(
                hook_python_command
                or environment.get("CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND")
                or "python"
            ).strip()
            if name == "claude"
            else "auto"
        )
        hook_python = (
            shutil.which(hook_command, path=environment.get("PATH"))
            if name == "claude" and hook_command
            else sys.executable
        )
        hook_version = _python_version(hook_python)
        host_results.append(
            {
                "host": name,
                "provider": settings.provider,
                "model": settings.model,
                "configuration_source": settings.configuration_source,
                "configuration_error": settings.configuration_error,
                "provider_cli": executable or "",
                "provider_ready": provider_ready,
                "local": local,
                "grok": grok,
                "hook_python_command": hook_command,
                "hook_python": hook_python or "",
                "hook_python_version": (
                    ".".join(map(str, hook_version)) if hook_version else ""
                ),
                "hook_python_ready": bool(hook_version and hook_version >= (3, 10, 0)),
                "legacy": inspect_legacy_config(
                    config_path_for(name, environment), name
                ),
                "trust": "review in /hooks" if name == "codex" else "not required",
            }
        )
    data_dir = RuntimeSettings.from_env(root, environ=environment).paths.data_dir
    data_ready = _data_path_ready(data_dir)
    pillow_ready = importlib.util.find_spec("PIL") is not None
    tkinter_ready = importlib.util.find_spec("tkinter") is not None
    core_ready = (
        python_ready
        and not missing_runtime
        and data_ready
        and bool(host_results)
        and all(
            item["provider_ready"] and item["hook_python_ready"]
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
        "ui": {
            "ready": pillow_ready and tkinter_ready,
            "pillow": pillow_ready,
            "tkinter": tkinter_ready,
        },
    }


def launch_window(plugin_root: Path, *, workspace: str | Path = "") -> dict:
    root = Path(plugin_root).resolve()
    try:
        workspace_path = Path(workspace or Path.cwd()).expanduser().resolve()
    except OSError as exc:
        return {
            "launched": False,
            "missing": [f"workspace directory: {exc}"],
            "workspace": str(workspace or ""),
        }
    if not workspace_path.is_dir():
        return {
            "launched": False,
            "missing": [f"workspace directory: {workspace_path}"],
            "workspace": str(workspace_path),
        }
    pillow_ready = importlib.util.find_spec("PIL") is not None
    tkinter_ready = importlib.util.find_spec("tkinter") is not None
    missing = []
    if not pillow_ready:
        missing.append("Pillow (python -m pip install --user Pillow)")
    if not tkinter_ready:
        missing.append("Tkinter (install the Tk package for this Python build)")
    script = root / "buddy_window.py"
    if not script.exists():
        missing.append(f"runtime file: {script}")
    if missing:
        return {
            "launched": False,
            "missing": missing,
            "workspace": str(workspace_path),
        }

    command = [sys.executable, str(script)]
    child_environment = {
        **os.environ,
        "MASTERS_NUDGE_WORKSPACE": str(workspace_path),
    }
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
        "cwd": str(workspace_path),
        "env": child_environment,
    }
    if os.name == "nt":
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if pythonw.exists():
            command[0] = str(pythonw)
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        kwargs["start_new_session"] = True
    try:
        process = subprocess.Popen(command, **kwargs)
    except OSError as exc:
        return {
            "launched": False,
            "missing": [f"could not launch window: {exc}"],
            "workspace": str(workspace_path),
        }
    return {
        "launched": True,
        "pid": process.pid,
        "missing": [],
        "workspace": str(workspace_path),
    }
