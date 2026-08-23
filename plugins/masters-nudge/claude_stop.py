#!/usr/bin/env python3
"""Masters' Nudge — Claude Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, dispatches to the configured provider's CLI (Anthropic by default for
this Claude host; explicitly overridable), and appends the reaction to the
host-namespaced local data log.

Never raises out of main() — hook must not block on our errors.
"""

import hashlib
import json
import os
import sys

from masters_nudge import claude_adapter, evidence as shared_evidence, storage
from masters_nudge.contracts import ReviewRequest
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import active_guard


def log_error(msg: str) -> None:
    claude_adapter.log_error("claude-stop", msg)


def read_hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        log_error(f"hook input parse failed: {e}")
        return {}


def main() -> None:
    if active_guard():
        return
    hook = read_hook_input()
    settings = claude_adapter.runtime_settings()
    cwd = hook.get("cwd") or os.getcwd()
    session = claude_adapter.session_from_hook(hook, default_cwd=str(cwd))

    report = shared_evidence.read_latest_agentcam_report(
        str(cwd), log_error=log_error
    )
    report_content = ""
    if report and float(report["mtime"]) > storage.load_agentcam_mtime(
        settings.paths.data_dir, session
    ):
        report_content = report["content"]
        storage.save_agentcam_mtime(
            settings.paths.data_dir, session, float(report["mtime"])
        )

    source = claude_adapter.build_stop_source_context(
        hook, report_content, session=session
    )
    source_packet = str(source["packet"])
    if not source_packet:
        log_error("empty source packet, skipping")
        return

    request = ReviewRequest(
        schema_version=1,
        kind="stop",
        reason="stop",
        session=session,
        source_packet=source_packet,
        source_fingerprint=hashlib.sha256(
            source_packet.encode("utf-8", errors="replace")
        ).hexdigest()[:24],
    )

    ReviewCore(settings, log_error=log_error).review(request, persist_reaction=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
