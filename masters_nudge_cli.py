#!/usr/bin/env python3
"""JSON-only command interface used by Masters' Nudge skills."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from masters_nudge.local_ollama import DEFAULT_OLLAMA_URL
from masters_nudge.management import (
    configure_provider,
    doctor,
    get_provider,
    list_providers,
    recent_nudges,
    reset_provider_config,
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
