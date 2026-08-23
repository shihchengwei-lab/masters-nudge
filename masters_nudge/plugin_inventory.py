"""Validated file inventory shared by plugin builds and installation diagnostics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


INVENTORY_SCHEMA_VERSION = 1
INVENTORY_FILE = ".masters-nudge-inventory.json"

@dataclass(frozen=True)
class PackageFile:
    """One packaged file and its installation responsibility."""

    path: str
    source: str = "generated"
    runtime_required: bool = True


# This is the single owner of package membership and runtime responsibility.
# Generated files are copied from the source tree; static files are maintained
# directly in the checked-in plugin package. UI assets remain packaged without
# making the optional window a core readiness dependency.
PACKAGE_MANIFEST = (
    PackageFile("LICENSE", runtime_required=False),
    PackageFile("buddy-prompt.txt"),
    PackageFile("buddy_window.py", runtime_required=False),
    PackageFile("claude_checkpoint.py"),
    PackageFile("claude_prompt.py"),
    PackageFile("claude_stop.py"),
    PackageFile("hook_entry.py"),
    PackageFile("lens_router.py"),
    PackageFile("masters_nudge_cli.py"),
    PackageFile("persona_config.py"),
    PackageFile("reaction-schema.json"),
    PackageFile("review_telemetry.py"),
    PackageFile("source_context.py"),
    PackageFile("spritesheet.webp", runtime_required=False),
    PackageFile("masters_nudge/__init__.py"),
    PackageFile("masters_nudge/checkpoints.py"),
    PackageFile("masters_nudge/claude_adapter.py"),
    PackageFile("masters_nudge/codex_adapter.py"),
    PackageFile("masters_nudge/contracts.py"),
    PackageFile("masters_nudge/core.py"),
    PackageFile("masters_nudge/evidence.py"),
    PackageFile("masters_nudge/local_ollama.py"),
    PackageFile("masters_nudge/management.py"),
    PackageFile("masters_nudge/plugin_inventory.py"),
    PackageFile("masters_nudge/prompting.py"),
    PackageFile("masters_nudge/providers.py"),
    PackageFile("masters_nudge/runtime.py"),
    PackageFile("masters_nudge/storage.py"),
    PackageFile("personas/beck.txt"),
    PackageFile("personas/carmack.txt"),
    PackageFile("personas/fowler.txt"),
    PackageFile("personas/jeff.txt"),
    PackageFile("personas/lamport.txt"),
    PackageFile("personas/linus.txt"),
    PackageFile(".claude-plugin/plugin.json", source="static"),
    PackageFile(".codex-plugin/plugin.json", source="static"),
    PackageFile("hooks/claude.json", source="static"),
    PackageFile("hooks/hooks.json", source="static"),
    PackageFile("hooks/run_python.cmd", source="static"),
    PackageFile("hooks/run_python.sh", source="static"),
    PackageFile(
        "skills/doctor/SKILL.md", source="static", runtime_required=False
    ),
    PackageFile(
        "skills/migrate/SKILL.md", source="static", runtime_required=False
    ),
    PackageFile(
        "skills/setup-local/SKILL.md", source="static", runtime_required=False
    ),
    PackageFile(
        "skills/window/SKILL.md", source="static", runtime_required=False
    ),
)


def package_files(*, source: str | None = None) -> tuple[str, ...]:
    """Return package paths, optionally filtered by their source owner."""
    return tuple(
        entry.path
        for entry in PACKAGE_MANIFEST
        if source is None or entry.source == source
    )


def runtime_files(*, installed: bool) -> tuple[str, ...]:
    """Return core dependencies for a source tree or installed plugin."""
    paths = tuple(
        entry.path
        for entry in PACKAGE_MANIFEST
        if entry.runtime_required and (installed or entry.source == "generated")
    )
    return (*paths, INVENTORY_FILE) if installed else paths


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
