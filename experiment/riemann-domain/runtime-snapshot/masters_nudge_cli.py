#!/usr/bin/env python3
"""Manage a plugin-based Masters' Nudge installation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from masters_nudge.contracts import SessionRef
from masters_nudge.local_ollama import DEFAULT_OLLAMA_URL
from masters_nudge.management import (
    configure_local,
    configure_grok,
    doctor,
    launch_window,
    migrate_legacy,
    reset_local,
)
from masters_nudge.profiles import (
    RIEMANN_STAGES,
    configure_workspace_profile,
    load_workspace_profile,
    normalize_workspace,
    reset_workspace_profile,
    workspace_profile_path,
)
from masters_nudge.runtime import RuntimePaths


PLUGIN_ROOT = Path(__file__).resolve().parent


def _print_doctor(result: dict) -> None:
    print(f"Core ready: {'yes' if result['core_ready'] else 'no'}")
    print(f"Python: {result['python']['version']} ({result['python']['executable']})")
    if result["runtime"]["missing"]:
        print("Missing runtime: " + ", ".join(result["runtime"]["missing"]))
    for item in result["hosts"]:
        status = "ready" if item["provider_ready"] else "not ready"
        print(
            f"{item['host']}: {item['provider']} / {item['model']} ({status})"
        )
        if item["configuration_error"]:
            print("  reviewer config: " + item["configuration_error"])
        local = item.get("local") or {}
        if local:
            print(f"  local endpoint: {local['endpoint']}")
            print(
                "  privacy: "
                + (
                    "cloud disabled; model is local"
                    if local["ready"]
                    else local["error"]
                )
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


def _print_local_configure(result: dict) -> None:
    if result["saved"]:
        print(
            f"Local reviewer configured for both hosts: {result['model']} "
            f"at {result['ollama_url']}"
        )
        print(f"Config: {result['path']}")
    else:
        print("Local reviewer not configured: " + result["error"])


def _print_local_reset(result: dict) -> None:
    if not result["reset"]:
        print("Local reviewer config not reset: " + result["error"])
    elif result["removed"]:
        print(
            "Local reviewer config removed; environment overrides now win, "
            "otherwise host cloud defaults are active again."
        )
    else:
        print("No persistent local reviewer config was present.")


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

    local_parser = subparsers.add_parser("local")
    local_subparsers = local_parser.add_subparsers(
        dest="local_command", required=True
    )
    local_configure_parser = local_subparsers.add_parser("configure")
    local_configure_parser.add_argument("--model", required=True)
    local_configure_parser.add_argument("--url", default=DEFAULT_OLLAMA_URL)
    local_configure_parser.add_argument("--json", action="store_true")
    local_reset_parser = local_subparsers.add_parser("reset")
    local_reset_parser.add_argument("--json", action="store_true")

    grok_parser = subparsers.add_parser("grok")
    grok_subparsers = grok_parser.add_subparsers(
        dest="grok_command", required=True
    )
    grok_configure_parser = grok_subparsers.add_parser("configure")
    grok_configure_parser.add_argument("--model", default="")
    grok_configure_parser.add_argument("--json", action="store_true")
    grok_reset_parser = grok_subparsers.add_parser("reset")
    grok_reset_parser.add_argument("--json", action="store_true")

    profile_parser = subparsers.add_parser("profile")
    profile_subparsers = profile_parser.add_subparsers(
        dest="profile_command", required=True
    )
    profile_configure = profile_subparsers.add_parser("configure")
    profile_configure.add_argument("--workspace", default=".")
    profile_configure.add_argument("--domain", choices=("riemann",), default="riemann")
    profile_configure.add_argument("--stage", choices=RIEMANN_STAGES, default="explore")
    profile_configure.add_argument("--provider", choices=("anthropic",), default="anthropic")
    profile_configure.add_argument("--model", default="claude-opus-4-6")
    profile_configure.add_argument(
        "--review-mode", choices=("all", "stop_only"), default="stop_only"
    )
    profile_configure.add_argument("--json", action="store_true")
    for command in ("show", "reset"):
        child = profile_subparsers.add_parser(command)
        child.add_argument("--workspace", default=".")
        child.add_argument("--json", action="store_true")

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
    if args.command == "local":
        if args.local_command == "configure":
            result = configure_local(args.model, args.url)
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                _print_local_configure(result)
            return 0 if result["saved"] else 1
        result = reset_local()
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            _print_local_reset(result)
        return 0 if result["reset"] else 1
    if args.command == "grok":
        if args.grok_command == "configure":
            result = configure_grok(args.model)
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            elif result["saved"]:
                selected = result["model"] or "Grok CLI default model"
                print(f"Grok reviewer configured for both hosts: {selected}")
                print(f"Config: {result['path']}")
            else:
                print("Grok reviewer not configured: " + result["error"])
            return 0 if result["saved"] else 1
        result = reset_local()
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        elif result["removed"]:
            print("Persistent reviewer config removed; host defaults are active again.")
        else:
            print("No persistent reviewer config was present.")
        return 0 if result["reset"] else 1
    if args.command == "profile":
        data_dir = RuntimePaths.resolve(PLUGIN_ROOT).data_dir
        workspace = normalize_workspace(args.workspace)
        if args.profile_command == "configure":
            result = configure_workspace_profile(
                data_dir,
                workspace,
                domain=args.domain,
                stage=args.stage,
                provider=args.provider,
                model=args.model,
                review_mode=args.review_mode,
            )
        elif args.profile_command == "reset":
            result = reset_workspace_profile(data_dir, workspace)
        else:
            profile, error = load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "profile", cwd=workspace, repo_root=workspace),
            )
            result = {
                **profile.__dict__,
                "path": str(workspace_profile_path(data_dir, workspace)),
                "error": error,
            }
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        elif args.profile_command == "configure":
            if result["saved"]:
                print(
                    f"Workspace uses {result['domain']} / {result['stage']} with "
                    f"{result['provider']} / {result['model']} ({result['review_mode']})."
                )
                print(f"Profile: {result['path']}")
            else:
                print("Workspace profile not configured: " + result["error"])
        elif args.profile_command == "reset":
            print(
                "Workspace profile removed."
                if result["removed"]
                else "No workspace profile was present."
            )
        elif result["error"]:
            print("Workspace profile error: " + result["error"])
        elif result["source"] == "default":
            print("Workspace uses the default software profile.")
        else:
            print(
                f"Workspace uses {result['domain']} / {result['stage']} with "
                f"{result['provider']} / {result['model']} ({result['review_mode']})."
            )
        return 1 if result.get("error") else 0

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
