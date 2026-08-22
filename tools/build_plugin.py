#!/usr/bin/env python3
"""Build or verify the generated Masters' Nudge plugin runtime."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from masters_nudge.plugin_inventory import (  # noqa: E402
    INVENTORY_FILE,
    INVENTORY_SCHEMA_VERSION,
    PLUGIN_RUNTIME_FILES,
    SOURCE_RUNTIME_FILES,
)


PLUGIN_ROOT = ROOT / "plugins" / "masters-nudge"

FILES = (
    "CHANGELOG.md",
    "LICENSE",
    "buddy-prompt.txt",
    "buddy_window.py",
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
    "shader_progress.py",
    "shader_router.py",
    "spritesheet.webp",
)

DIRECTORIES = ("domains", "masters_nudge", "personas")
ASSETS = {
    "docs/images/masters-nudge-six-lenses-hero.png": (
        "assets/masters-nudge-six-lenses-hero.png"
    ),
}

STATIC_FILES = (
    *PLUGIN_RUNTIME_FILES,
    "skills/doctor/SKILL.md",
    "skills/migrate/SKILL.md",
    "skills/setup-local/SKILL.md",
    "skills/window/SKILL.md",
)
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_VERSION_RE = re.compile(r"^(?P<base>[^+]+)\+codex\.(?P<token>[^+]+)$")


def _source_files(directory: str) -> list[Path]:
    root = ROOT / directory
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


def _generated_targets() -> set[Path]:
    targets = {Path(relative) for relative in FILES}
    for directory in DIRECTORIES:
        targets.update(
            Path(directory) / path.relative_to(ROOT / directory)
            for path in _source_files(directory)
        )
    targets.update(Path(destination) for destination in ASSETS.values())
    return targets


def expected_plugin_files() -> set[Path]:
    return _generated_targets() | {
        *(Path(relative) for relative in STATIC_FILES),
        Path(INVENTORY_FILE),
    }


def _actual_plugin_files() -> set[Path]:
    if not PLUGIN_ROOT.exists():
        return set()
    return {
        path.relative_to(PLUGIN_ROOT)
        for path in PLUGIN_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def _label(relative: Path) -> str:
    return (Path("plugins") / "masters-nudge" / relative).as_posix()


def _read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _base_version() -> str:
    return str(
        _read_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json").get("version", "")
    ).strip()


def _sync_versions() -> None:
    base_version = _base_version()
    if not base_version or "+" in base_version:
        raise ValueError(
            "Claude plugin version must be the base version without metadata"
        )

    codex_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    codex = _read_json(codex_path)
    match = CODEX_VERSION_RE.fullmatch(str(codex.get("version") or ""))
    token = match.group("token") if match else "local"
    codex["version"] = f"{base_version}+codex.{token}"
    _write_json(codex_path, codex)

    if CLAUDE_MARKETPLACE.exists():
        marketplace = _read_json(CLAUDE_MARKETPLACE)
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            raise ValueError("Claude marketplace plugins must be a list")
        matches = [
            item
            for item in plugins
            if isinstance(item, dict) and item.get("name") == "masters-nudge"
        ]
        if len(matches) != 1:
            raise ValueError("Claude marketplace must contain one masters-nudge entry")
        matches[0]["version"] = base_version
        _write_json(CLAUDE_MARKETPLACE, marketplace)


def _inventory_payload() -> dict:
    runtime_files = {
        *(Path(relative) for relative in SOURCE_RUNTIME_FILES),
        *(Path(relative) for relative in PLUGIN_RUNTIME_FILES),
        Path(INVENTORY_FILE),
    }
    unexpected_runtime = runtime_files - expected_plugin_files()
    if unexpected_runtime:
        labels = ", ".join(sorted(path.as_posix() for path in unexpected_runtime))
        raise ValueError(f"runtime inventory is not packaged: {labels}")
    return {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "base_version": _base_version(),
        "files": sorted(path.as_posix() for path in expected_plugin_files()),
        "runtime_files": sorted(path.as_posix() for path in runtime_files),
    }


def _write_inventory() -> None:
    _write_json(PLUGIN_ROOT / INVENTORY_FILE, _inventory_payload())


def write_plugin() -> None:
    PLUGIN_ROOT.mkdir(parents=True, exist_ok=True)
    for cache_dir in PLUGIN_ROOT.rglob("__pycache__"):
        shutil.rmtree(cache_dir)
    for bytecode in PLUGIN_ROOT.rglob("*.pyc"):
        bytecode.unlink()
    for relative in FILES:
        destination = PLUGIN_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    for directory in DIRECTORIES:
        destination = PLUGIN_ROOT / directory
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(
            ROOT / directory,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for source, destination in ASSETS.items():
        target = PLUGIN_ROOT / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / source, target)
    _sync_versions()
    _write_inventory()
    expected = expected_plugin_files()
    for relative in sorted(_actual_plugin_files() - expected, reverse=True):
        (PLUGIN_ROOT / relative).unlink()
    for directory in sorted(
        (path for path in PLUGIN_ROOT.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        try:
            directory.rmdir()
        except OSError:
            pass


def check_plugin() -> list[str]:
    errors: list[str] = []
    expected = expected_plugin_files()
    actual = _actual_plugin_files()
    for relative in sorted(expected - actual):
        errors.append(f"missing: {_label(relative)}")
    for relative in sorted(actual - expected):
        errors.append(f"unexpected: {_label(relative)}")
    for relative in FILES:
        source = ROOT / relative
        destination = PLUGIN_ROOT / relative
        if not destination.exists():
            continue
        elif not filecmp.cmp(source, destination, shallow=False):
            errors.append(f"stale: {_label(Path(relative))}")
    for directory in DIRECTORIES:
        expected = {
            path.relative_to(ROOT / directory) for path in _source_files(directory)
        }
        destination_root = PLUGIN_ROOT / directory
        actual = (
            {
                path.relative_to(destination_root)
                for path in destination_root.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            }
            if destination_root.exists()
            else set()
        )
        for relative in sorted(expected & actual):
            if not filecmp.cmp(
                ROOT / directory / relative,
                destination_root / relative,
                shallow=False,
            ):
                errors.append(f"stale: {_label(Path(directory) / relative)}")
    for source, destination in ASSETS.items():
        target = PLUGIN_ROOT / destination
        if not target.exists():
            continue
        elif not filecmp.cmp(ROOT / source, target, shallow=False):
            errors.append(f"stale: {_label(Path(destination))}")
    try:
        base_version = _base_version()
        codex = _read_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
        match = CODEX_VERSION_RE.fullmatch(str(codex.get("version") or ""))
        if not match or match.group("base") != base_version:
            errors.append(
                "version: Codex manifest does not derive from Claude manifest"
            )
        marketplace = _read_json(CLAUDE_MARKETPLACE)
        marketplace_versions = [
            str(item.get("version") or "")
            for item in marketplace.get("plugins", [])
            if isinstance(item, dict) and item.get("name") == "masters-nudge"
        ]
        if marketplace_versions != [base_version]:
            errors.append("version: Claude marketplace does not match Claude manifest")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"version: {exc}")
    inventory_path = PLUGIN_ROOT / INVENTORY_FILE
    if inventory_path.exists():
        try:
            if _read_json(inventory_path) != _inventory_payload():
                errors.append(f"stale: {_label(Path(INVENTORY_FILE))}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"inventory: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_plugin()
    errors = check_plugin()
    if errors:
        print("\n".join(errors))
        return 1
    print("plugin runtime is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
