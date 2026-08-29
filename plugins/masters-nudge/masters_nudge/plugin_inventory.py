"""Validated file inventory shared by plugin builds and installation diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


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
    PackageFile("route-schema.json"),
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
    PackageFile("masters_nudge/provider_contract.py"),
    PackageFile("masters_nudge/prompting.py"),
    PackageFile("masters_nudge/providers.py"),
    PackageFile("masters_nudge/runtime.py"),
    PackageFile("masters_nudge/storage.py"),
    PackageFile("personas/carmack.txt"),
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
    return paths
