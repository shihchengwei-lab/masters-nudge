"""Validated file inventory shared by plugin builds and installation diagnostics."""

from __future__ import annotations

import json
from pathlib import Path


INVENTORY_SCHEMA_VERSION = 1
INVENTORY_FILE = ".masters-nudge-inventory.json"

# Source-tree fallback for development diagnostics. Installed plugins use the
# generated inventory, which covers every generated and static package file.
SOURCE_RUNTIME_FILES = (
    "buddy-prompt.txt",
    "claude_checkpoint.py",
    "claude_prompt.py",
    "claude_stop.py",
    "hook_entry.py",
    "lens_router.py",
    "masters_nudge_cli.py",
    "persona_config.py",
    "reaction-schema.json",
    "review_telemetry.py",
    "source_context.py",
    "personas/beck.txt",
    "personas/carmack.txt",
    "personas/fowler.txt",
    "personas/jeff.txt",
    "personas/lamport.txt",
    "personas/linus.txt",
    "masters_nudge/__init__.py",
    "masters_nudge/checkpoints.py",
    "masters_nudge/claude_adapter.py",
    "masters_nudge/codex_adapter.py",
    "masters_nudge/contracts.py",
    "masters_nudge/core.py",
    "masters_nudge/evidence.py",
    "masters_nudge/local_ollama.py",
    "masters_nudge/management.py",
    "masters_nudge/plugin_inventory.py",
    "masters_nudge/prompting.py",
    "masters_nudge/providers.py",
    "masters_nudge/runtime.py",
    "masters_nudge/storage.py",
)

PLUGIN_RUNTIME_FILES = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "hooks/claude.json",
    "hooks/hooks.json",
    "hooks/run_python.cmd",
    "hooks/run_python.sh",
)


def load_plugin_inventory(plugin_root: Path) -> tuple[tuple[str, ...], str]:
    """Return a validated installed-plugin inventory and an error message."""
    path = Path(plugin_root) / INVENTORY_FILE
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return (), f"missing inventory: {INVENTORY_FILE}"
    except (OSError, ValueError) as exc:
        return (), f"cannot read inventory: {exc}"
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != INVENTORY_SCHEMA_VERSION
    ):
        return (), "inventory has an invalid schema"
    files = payload.get("files")
    runtime_files = payload.get("runtime_files")
    if not isinstance(files, list) or not files:
        return (), "inventory files must be a non-empty list"
    if not isinstance(runtime_files, list) or not runtime_files:
        return (), "inventory runtime_files must be a non-empty list"

    def normalize(values: list, field: str) -> tuple[list[str], str]:
        normalized: list[str] = []
        for value in values:
            if not isinstance(value, str):
                return [], f"inventory {field} entries must be strings"
            relative = Path(value)
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or "\\" in value
                or value != relative.as_posix()
            ):
                return [], f"inventory contains an unsafe path: {value!r}"
            normalized.append(value)
        if len(set(normalized)) != len(normalized):
            return [], f"inventory {field} contains duplicate paths"
        return normalized, ""

    normalized, error = normalize(files, "files")
    if error:
        return (), error
    runtime, error = normalize(runtime_files, "runtime_files")
    if error:
        return (), error
    if not set(runtime).issubset(normalized):
        return (), "inventory runtime_files are not a subset of files"
    if INVENTORY_FILE not in normalized:
        return (), "inventory does not include itself"
    return tuple(runtime), ""
