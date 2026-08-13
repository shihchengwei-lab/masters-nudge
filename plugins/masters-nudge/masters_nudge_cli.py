#!/usr/bin/env python3
"""Manage a plugin-based Masters' Nudge installation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from masters_nudge.management import doctor, launch_window, migrate_legacy


PLUGIN_ROOT = Path(__file__).resolve().parent


def _print_doctor(result: dict) -> None:
    print(f"Core ready: {'yes' if result['core_ready'] else 'no'}")
    print(f"Python: {result['python']['version']} ({result['python']['executable']})")
    if result["runtime"]["missing"]:
        print("Missing runtime: " + ", ".join(result["runtime"]["missing"]))
    for item in result["hosts"]:
        status = "ready" if item["provider_ready"] else "missing CLI"
        print(
            f"{item['host']}: {item['provider']} / {item['model']} ({status})"
        )
        if not item["hook_python_ready"]:
            detail = (
                f"version {item['hook_python_version']} is below 3.10"
                if item["hook_python_version"]
                else f"executable not found: {item['hook_python_command']}"
            )
            print("  hook Python: " + detail)
        legacy = item["legacy"]
        if legacy["exact"]:
            print(
                f"  legacy hooks: {legacy['exact']} exact match(es); "
                "run migrate --apply after installing the plugin"
            )
        if legacy["near"]:
            print("  legacy hooks: modified entries need manual review")
        if legacy["error"]:
            print(f"  legacy hooks: {legacy['error']}")
        if item["host"] == "codex":
            print("  trust: review this plugin in /hooks")
    ui = result["ui"]
    print(
        "Optional window: "
        + ("ready" if ui["ready"] else "missing Pillow or Tkinter")
    )


def _print_migration(result: dict) -> None:
    for item in result["results"]:
        if item["error"]:
            backup = f"; backup: {item['backup']}" if item["backup"] else ""
            print(f"{item['host']}: {item['error']}{backup}")
        elif item["near"]:
            print(f"{item['host']}: modified legacy hooks require manual review")
        elif item["applied"]:
            print(
                f"{item['host']}: removed {item['removed']} legacy hook(s); "
                f"backup: {item['backup']}"
            )
        elif item["exact"]:
            print(
                f"{item['host']}: would remove {item['exact']} legacy hook(s); "
                "rerun with --apply"
            )
        else:
            print(f"{item['host']}: no known legacy hooks found")


def main() -> int:
    parser = argparse.ArgumentParser(prog="masters-nudge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument(
        "--host", choices=("auto", "claude", "codex", "all"), default="auto"
    )
    doctor_parser.add_argument("--hook-python-command", default="")
    doctor_parser.add_argument("--json", action="store_true")

    migrate_parser = subparsers.add_parser("migrate")
    migrate_parser.add_argument(
        "--host", choices=("claude", "codex", "all"), default="all"
    )
    migrate_parser.add_argument("--apply", action="store_true")
    migrate_parser.add_argument("--json", action="store_true")

    window_parser = subparsers.add_parser("window")
    window_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "doctor":
        result = doctor(
            PLUGIN_ROOT,
            args.host,
            hook_python_command=args.hook_python_command or None,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            _print_doctor(result)
        return 0 if result["core_ready"] else 1
    if args.command == "migrate":
        result = migrate_legacy(args.host, apply=args.apply)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            _print_migration(result)
        return 2 if result["unsafe"] else 0

    result = launch_window(PLUGIN_ROOT)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["launched"]:
        print(f"Masters’ Nudge window launched (pid {result['pid']}).")
    else:
        print("Window not launched: " + "; ".join(result["missing"]))
    return 0 if result["launched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
