#!/usr/bin/env python3
"""Single Codex CLI hook entry point for Masters' Nudge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from masters_nudge import storage
from masters_nudge.codex_adapter import AUDIT_MARKER_KEY, CodexAdapter
from masters_nudge.contracts import POST_TOOL_BATCH_EVENT
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import RuntimeSettings, active_guard


MAX_STDIN_BYTES = 1024 * 1024


def _settings(host: str = "codex_cli") -> RuntimeSettings:
    return RuntimeSettings.from_env(
        Path(__file__).resolve().parent,
        host=host,
    )


def _log_error(settings: RuntimeSettings, message: str) -> None:
    storage.append_error(settings.paths.error_log, "codex-hook", message)


def _read_payload() -> dict:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(raw) > MAX_STDIN_BYTES:
        raise ValueError("hook input exceeds 1 MiB")
    value = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    if not isinstance(value, dict):
        raise ValueError("hook input must be a JSON object")
    return value


def _emit_output(output: dict, settings: RuntimeSettings, stream=None) -> None:
    """Write one code-page-safe hook response, then commit delivery state."""
    public_output = dict(output)
    audit = public_output.pop(AUDIT_MARKER_KEY, None)
    target = stream or sys.stdout
    target.write(json.dumps(public_output, ensure_ascii=True) + "\n")
    target.flush()
    if isinstance(audit, dict):
        storage.append_host_returned_nudge(
            settings.paths.data_dir,
            audit["session"],
            lens=str(audit.get("lens") or ""),
            finding=str(audit.get("finding") or ""),
            returned_via=str(audit.get("returned_via") or POST_TOOL_BATCH_EVENT),
        )


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default="codex_cli")
    args, _unknown = parser.parse_known_args()
    settings = _settings(args.host)

    def log_error(message: str) -> None:
        _log_error(settings, message)

    if args.host != "codex_cli":
        log_error(f"unsupported hook host: {args.host}")
        return 0
    if active_guard():
        return 0
    try:
        payload = _read_payload()
        core = NudgeCore(settings, log_error=log_error)
        adapter = CodexAdapter(core)
        output = adapter.process(payload)
        if output is not None:
            _emit_output(output, settings)
    except Exception as exc:
        log_error(f"hook processing failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
