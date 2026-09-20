#!/usr/bin/env python3
"""Replay the failed hook input without the Codex hook host."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid


ROOT = Path.home() / "AppData" / "Local" / "Temp" / "mn-ab-preserved-result-expanded-20260920-v2"
FAILED = ROOT / "runs" / "django__django-12273" / "repeat-1" / "B"
RUNTIME = ROOT / "runtime-preserved-result"
WORKSPACE = ROOT / "workspaces" / "django__django-12273" / "repeat-1" / "B"
OUT = ROOT / "fault-replay"


def invoke(payload: dict, env: dict[str, str]) -> dict:
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(RUNTIME / "hook_entry.py"), "--host", "codex_cli"],
        input=json.dumps(payload), text=True, encoding="utf-8", errors="replace",
        capture_output=True, env=env, cwd=WORKSPACE, timeout=210,
    )
    return {
        "elapsed_seconds": time.monotonic() - started,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> None:
    OUT.mkdir(exist_ok=False)
    with sqlite3.connect(FAILED / "masters-nudge-data" / "feedback.sqlite3") as db:
        db.row_factory = sqlite3.Row
        round_row = db.execute("SELECT * FROM rounds").fetchone()
        batch = db.execute("SELECT * FROM batches").fetchone()
    session = uuid.uuid4().hex
    turn = uuid.uuid4().hex
    common = {
        "session_id": session, "turn_id": turn, "cwd": str(WORKSPACE),
        "transcript_path": "",
    }
    environment = {
        **os.environ,
        "MASTERS_NUDGE_ACTIVE": "0",
        "MASTERS_NUDGE_TEST_MODE": "1",
        "PLUGIN_ROOT": str(RUNTIME),
        "MASTERS_NUDGE_DATA_DIR": str(OUT / "data"),
        "MASTERS_NUDGE_RUNTIME_DIR": str(RUNTIME),
    }
    start = invoke({
        **common, "hook_event_name": "UserPromptSubmit",
        "prompt": round_row["request"], "goal": {"objective": round_row["goal"]},
    }, environment)
    original = json.loads(batch["payload"])[0]
    completed = invoke({
        **common, "hook_event_name": "PostToolUse",
        "tool_name": original["tool_name"], "tool_use_id": original["tool_use_id"] + "-replay",
        "tool_input": original["tool_input"], "tool_response": original["tool_response"],
    }, environment)
    record = {"start": start, "completed": completed}
    (OUT / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
