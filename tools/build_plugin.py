#!/usr/bin/env python3
"""Mechanically copy the declared runtime; never maintain a second implementation."""
import argparse
import filecmp
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.plugin_inventory import package_files, RETIRED_FILES

PLUGIN_ROOT = ROOT / "plugins" / "masters-nudge"

def check_plugin():
    expected = set(package_files())
    actual = {path.relative_to(PLUGIN_ROOT).as_posix() for path in PLUGIN_ROOT.rglob("*")
              if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"}
    errors = [f"missing: {name}" for name in sorted(expected - actual)]
    errors += [f"unexpected: {name}" for name in sorted(actual - expected)]
    for name in package_files(source="generated"):
        if (PLUGIN_ROOT / name).exists() and not filecmp.cmp(ROOT / name, PLUGIN_ROOT / name, shallow=False):
            errors.append(f"stale: {name}")
    return errors

def write_plugin():
    root = PLUGIN_ROOT.resolve()
    for name in RETIRED_FILES:
        target = (root / name).resolve()
        target.relative_to(root)
        target.unlink(missing_ok=True)
    for name in package_files(source="generated"):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)

def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--write", action="store_true")
    choice.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_plugin()
    errors = check_plugin()
    print("\n".join(errors) if errors else "plugin runtime is synchronized")
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
