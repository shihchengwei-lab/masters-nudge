#!/usr/bin/env python3
"""Explicit performance checkpoint. Reads one bounded JSON object from stdin."""
import json
import sys
from pathlib import Path

from masters_nudge import storage
from masters_nudge.contracts import ToolFault
from masters_nudge.core import NudgeCore
from masters_nudge.diagnostics import MAX_INPUT_BYTES
from masters_nudge.prompting import delivery_text
from masters_nudge.runtime import RuntimeSettings, active_guard


def main():
    if active_guard():
        return 0
    settings = RuntimeSettings.from_env(Path(__file__).resolve().parent, host="codex_cli")
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ToolFault("input_size", "diagnostic checkpoint 超過 64 KiB")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise ToolFault("input", "diagnostic checkpoint 必須是 UTF-8 JSON") from exc
        core = NudgeCore(settings)
        result = core.process_diagnostic(payload)
        if result is None:
            output = {"status": "no_feedback", "note": "See journal: silence, duplicate, quota or superseded round; this status alone is not Provider silence."}
        else:
            attempt, feedback = result
            output = {"status": "feedback", "additionalContext": delivery_text(feedback, profile="performance")}
        print(json.dumps(output, ensure_ascii=True), flush=True)
        if result:
            core.journal.delivered(attempt)
        return 0
    except Exception as exc:
        kind = exc.kind if isinstance(exc, ToolFault) else "internal"
        try:
            storage.append_error(settings.paths.error_log, "diagnostic-checkpoint", str(exc))
        except OSError:
            pass
        # A fault is always observable to the command caller; no silent success exit.
        print(json.dumps({"status": "fault", "kind": kind, "message": str(exc)}, ensure_ascii=True), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
