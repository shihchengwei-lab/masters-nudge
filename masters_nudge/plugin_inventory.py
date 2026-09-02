"""Files copied into the checked-in plugin package."""

GENERATED_FILES = (
    "LICENSE",
    "buddy-prompt.txt",
    "claude_checkpoint.py",
    "claude_prompt.py",
    "hook_entry.py",
    "masters_nudge_cli.py",
    "nudge-schema.json",
    "source_context.py",
    "masters_nudge/__init__.py",
    "masters_nudge/checkpoints.py",
    "masters_nudge/claude_adapter.py",
    "masters_nudge/codex_adapter.py",
    "masters_nudge/contracts.py",
    "masters_nudge/core.py",
    "masters_nudge/evidence.py",
    "masters_nudge/local_ollama.py",
    "masters_nudge/lenses.py",
    "masters_nudge/management.py",
    "masters_nudge/plugin_inventory.py",
    "masters_nudge/provider_contract.py",
    "masters_nudge/prompting.py",
    "masters_nudge/providers.py",
    "masters_nudge/runtime.py",
    "masters_nudge/settings.py",
    "masters_nudge/storage.py",
    "personas/carmack.txt",
    "personas/lamport.txt",
    "personas/linus.txt",
)

STATIC_FILES = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "hooks/claude.json",
    "hooks/hooks.json",
    "hooks/run_python.cmd",
    "hooks/run_python.sh",
    "skills/doctor/SKILL.md",
    "skills/select-lens/SKILL.md",
    "skills/select-provider/SKILL.md",
    "skills/recent-nudges/SKILL.md",
)


def package_files(*, source: str | None = None) -> tuple[str, ...]:
    if source == "generated":
        return GENERATED_FILES
    if source == "static":
        return STATIC_FILES
    return GENERATED_FILES + STATIC_FILES


def runtime_files() -> tuple[str, ...]:
    return tuple(path for path in GENERATED_FILES if path != "LICENSE")
