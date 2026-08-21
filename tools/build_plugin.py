#!/usr/bin/env python3
"""Build or verify the generated Masters' Nudge plugin runtime."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "masters-nudge"

FILES = (
    "CHANGELOG.md",
    "LICENSE",
    "buddy-prompt.txt",
    "buddy.py",
    "buddy.sh",
    "buddy_window.py",
    "checkpoint.py",
    "checkpoint.sh",
    "hook_entry.py",
    "inject.py",
    "inject.sh",
    "lens_router.py",
    "masters_nudge_cli.py",
    "persona_config.py",
    "reaction-schema.json",
    "review_telemetry.py",
    "source_context.py",
    "shader_progress.py",
    "shader_router.py",
    "spritesheet.webp",
    "start_buddy_window.bat",
)

DIRECTORIES = ("domains", "masters_nudge", "personas")
ASSETS = {
    "docs/images/masters-nudge-six-lenses-hero.png": (
        "assets/masters-nudge-six-lenses-hero.png"
    ),
}


def _source_files(directory: str) -> list[Path]:
    root = ROOT / directory
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


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


def check_plugin() -> list[str]:
    errors: list[str] = []
    for relative in FILES:
        source = ROOT / relative
        destination = PLUGIN_ROOT / relative
        if not destination.exists():
            errors.append(f"missing: {destination.relative_to(ROOT)}")
        elif not filecmp.cmp(source, destination, shallow=False):
            errors.append(f"stale: {destination.relative_to(ROOT)}")
    for directory in DIRECTORIES:
        expected = {
            path.relative_to(ROOT / directory)
            for path in _source_files(directory)
        }
        destination_root = PLUGIN_ROOT / directory
        actual = {
            path.relative_to(destination_root)
            for path in destination_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        } if destination_root.exists() else set()
        for relative in sorted(expected - actual):
            errors.append(f"missing: {destination_root.relative_to(ROOT) / relative}")
        for relative in sorted(actual - expected):
            errors.append(f"unexpected: {destination_root.relative_to(ROOT) / relative}")
        for relative in sorted(expected & actual):
            if not filecmp.cmp(
                ROOT / directory / relative,
                destination_root / relative,
                shallow=False,
            ):
                errors.append(
                    f"stale: {destination_root.relative_to(ROOT) / relative}"
                )
    for source, destination in ASSETS.items():
        target = PLUGIN_ROOT / destination
        if not target.exists():
            errors.append(f"missing: {target.relative_to(ROOT)}")
        elif not filecmp.cmp(ROOT / source, target, shallow=False):
            errors.append(f"stale: {target.relative_to(ROOT)}")
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
