#!/usr/bin/env python3
"""Run a disposable real-Codex hook transport smoke test.

The temporary data directory is deleted on exit. The script briefly creates a
repo-local `.codex/hooks.json`, refuses to overwrite an existing one, and
removes its file in `finally`. It never edits `~/.codex/hooks.json`. Use
--provider anthropic/openai to include a real reviewer call; the default
deliberately exercises only the host transport. The checkout must be trusted.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def hook_commands() -> tuple[str, str]:
    script = ROOT / "hook_entry.py"
    return (
        f'python3 "{script.as_posix()}" --host codex_cli',
        f'py -3 "{script}" --host codex_cli',
    )


def hooks_payload() -> dict:
    command, command_windows = hook_commands()
    handler = {
        "type": "command",
        "command": command,
        "commandWindows": command_windows,
    }
    return {
        "description": "Temporary Phase C live smoke hooks.",
        "hooks": {
            "UserPromptSubmit": [
                {"hooks": [{**handler, "timeout": 5, "additionalContextLimit": 256}]}
            ],
            "PostToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {**handler, "timeout": 20, "additionalContextLimit": 256}
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            **handler,
                            "command": command + " --detach-stop",
                            "commandWindows": command_windows + " --detach-stop",
                            "timeout": 5,
                        }
                    ]
                }
            ],
        },
    }


def wait_for_stop(data_dir: Path, timeout: float) -> dict:
    telemetry = data_dir / "review-telemetry.jsonl"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            records = [json.loads(line) for line in telemetry.read_text(encoding="utf-8").splitlines()]
        except (OSError, ValueError):
            records = []
        matches = [
            record
            for record in records
            if record.get("host") == "codex_cli" and record.get("kind") == "stop"
        ]
        if matches:
            return matches[-1]
        time.sleep(0.5)
    raise RuntimeError("timed out waiting for the asynchronous Stop hook")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider", choices=("transport", "anthropic", "openai"), default="transport"
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("codex CLI not found")

    hooks_path = ROOT / ".codex" / "hooks.json"
    if hooks_path.exists():
        raise SystemExit(f"refusing to overwrite existing {hooks_path}")
    hooks_path.parent.mkdir(parents=True, exist_ok=True)
    hooks_path.write_text(
        json.dumps(hooks_payload(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
      with tempfile.TemporaryDirectory(prefix="masters-nudge-codex-smoke-") as tmpdir:
        root = Path(tmpdir)
        project = ROOT / "evaluation" / "phase_c" / "smoke_workspace"
        data_dir = root / "data"
        environment = {
            **os.environ,
            "MASTERS_NUDGE_DATA_DIR": str(data_dir),
            "MASTERS_NUDGE_PROVIDER": (
                "unsupported-smoke-provider"
                if args.provider == "transport"
                else args.provider
            ),
            "MASTERS_NUDGE_MODEL": "sonnet" if args.provider == "anthropic" else "gpt-5.6-sol",
            "MASTERS_NUDGE_TIMEOUT": "60",
            "MASTERS_NUDGE_ACTIVE": "0",
        }
        command = [
            codex,
            "--dangerously-bypass-hook-trust",
            "-a",
            "never",
            "-s",
            "read-only",
            "-C",
            str(project),
            "exec",
            "--skip-git-repo-check",
            "--json",
            (
                "Run exactly one shell command that prints phase-c-smoke, "
                "inspect its output, then reply with exactly done."
            ),
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=args.timeout,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"codex smoke exited {completed.returncode}: {completed.stderr[-1000:]}"
            )
        turn_files = list(data_dir.glob("codex_cli--*.turn.json"))
        if len(turn_files) != 1:
            raise RuntimeError(
                f"expected one namespaced turn journal, got {len(turn_files)}; "
                f"stdout={completed.stdout[-1500:]!r}; stderr={completed.stderr[-1500:]!r}"
            )
        turn = json.loads(turn_files[0].read_text(encoding="utf-8"))
        if "phase-c-smoke" not in str(turn.get("tool_evidence") or ""):
            raise RuntimeError("PostToolUse did not journal the shell output")
        stop_record = wait_for_stop(data_dir, args.timeout)
        print(
            json.dumps(
                {
                    "codex_version": subprocess.run(
                        [codex, "--version"], capture_output=True, text=True, encoding="utf-8"
                    ).stdout.strip(),
                    "provider_mode": args.provider,
                    "prompt_captured": turn.get("task_anchor", "").startswith("Run exactly"),
                    "tool_journaled": True,
                    "stop_review_status": stop_record.get("status"),
                    "host": stop_record.get("host"),
                    "turn_id_present": bool(stop_record.get("turn_id")),
                },
                ensure_ascii=False,
            )
        )
    finally:
        try:
            hooks_path.unlink(missing_ok=True)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
