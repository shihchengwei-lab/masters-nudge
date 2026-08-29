#!/usr/bin/env python3
"""JSON-only command interface used by Masters' Nudge skills."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from masters_nudge.local_ollama import DEFAULT_OLLAMA_URL
from masters_nudge.management import (
    configure_provider,
    doctor,
    get_lens,
    get_provider,
    list_lenses,
    list_providers,
    recent_nudges,
    reset_provider_config,
    set_lens,
)


PLUGIN_ROOT = Path(__file__).resolve().parent


def _write(result: dict) -> None:
    print(json.dumps(result, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(prog="masters-nudge")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor_parser = commands.add_parser("doctor")
    doctor_parser.add_argument(
        "--host", choices=("auto", "claude", "codex", "all"), default="auto"
    )
    doctor_parser.add_argument("--hook-python-command", default="")

    lens_parser = commands.add_parser("lens")
    lens_commands = lens_parser.add_subparsers(dest="lens_command", required=True)
    lens_commands.add_parser("list")
    lens_commands.add_parser("get")
    lens_set = lens_commands.add_parser("set")
    lens_set.add_argument(
        "lens", choices=("automatic", "simplicity", "reliability", "performance")
    )

    provider_parser = commands.add_parser("provider")
    provider_commands = provider_parser.add_subparsers(
        dest="provider_command", required=True
    )
    provider_commands.add_parser("list")
    provider_get = provider_commands.add_parser("get")
    provider_get.add_argument("--host", choices=("claude", "codex"), default="")
    provider_set = provider_commands.add_parser("set")
    provider_set.add_argument("provider", choices=("anthropic", "openai", "ollama"))
    provider_set.add_argument("--model", default="")
    provider_set.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    provider_commands.add_parser("reset")

    recent_parser = commands.add_parser("recent-nudges")
    recent_parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if args.command == "doctor":
        result = doctor(
            PLUGIN_ROOT,
            args.host,
            hook_python_command=args.hook_python_command or None,
        )
        _write(result)
        return 0 if result["core_ready"] else 1
    if args.command == "lens":
        if args.lens_command == "list":
            result = list_lenses()
        elif args.lens_command == "get":
            result = get_lens()
        else:
            result = set_lens(args.lens)
        _write(result)
        return 0 if not result.get("error") else 1
    if args.command == "provider":
        if args.provider_command == "list":
            result = list_providers()
        elif args.provider_command == "get":
            result = get_provider(host=args.host)
        elif args.provider_command == "set":
            result = configure_provider(
                args.provider,
                model=args.model,
                ollama_url=args.url,
            )
        else:
            result = reset_provider_config()
        _write(result)
        return 0 if not result.get("error") else 1
    result = recent_nudges(args.limit)
    _write(result)
    return 0 if not result["error"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
