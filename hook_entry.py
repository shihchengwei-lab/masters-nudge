#!/usr/bin/env python3
"""Single Codex CLI hook entry point for Masters' Nudge."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from masters_nudge import storage
from masters_nudge.codex_adapter import CodexAdapter, DELIVERY_MARKER_KEY
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimeSettings, active_guard


MAX_STDIN_BYTES = 1024 * 1024
MAX_ERROR_LOG_BYTES = 256 * 1024


def _settings(host: str = "codex_cli") -> RuntimeSettings:
    return RuntimeSettings.from_env(
        Path(__file__).resolve().parent,
        host=host,
    )


def _log_error(settings: RuntimeSettings, message: str) -> None:
    path = settings.paths.error_log
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > MAX_ERROR_LOG_BYTES:
            tail = path.read_bytes()[-MAX_ERROR_LOG_BYTES // 2 :]
            path.write_bytes(tail)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now().isoformat()} {message}\n")
    except OSError:
        pass


def _read_payload(payload_file: str = "") -> dict:
    if payload_file:
        path = Path(payload_file)
        try:
            raw = path.read_bytes()
        finally:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
    else:
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
    delivery = public_output.pop(DELIVERY_MARKER_KEY, None)
    target = stream or sys.stdout
    try:
        target.write(json.dumps(public_output, ensure_ascii=True) + "\n")
        target.flush()
    except Exception:
        if isinstance(delivery, dict):
            storage.mark_delivery(
                settings.paths.data_dir,
                delivery["session"],
                delivery["timestamp"],
                status="failed",
                event_seq=int(delivery.get("event_seq") or 0),
                delivered_via=str(delivery.get("event_name") or "hook"),
            )
        raise
    if delivery:
        if isinstance(delivery, dict):
            storage.mark_delivered(
                settings.paths.data_dir,
                delivery["session"],
                delivery["timestamp"],
                event_seq=int(delivery.get("event_seq") or 0),
                delivered_via=str(delivery.get("event_name") or "hook"),
            )
        else:  # compatibility with pre-receipt tests and cached runtimes
            session, timestamp = delivery
            storage.mark_delivered(settings.paths.data_dir, session, timestamp)


def _schedule_strategy(settings: RuntimeSettings, payload: dict, log_error) -> bool:
    spool_dir = settings.paths.data_dir / "spool"
    spool_dir.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="codex-strategy-",
        dir=spool_dir, delete=False, encoding="utf-8",
    )
    spool_path = Path(handle.name)
    try:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        command = [
            sys.executable, str(Path(__file__).resolve()),
            "--host", "codex_cli", "--strategy-payload-file", str(spool_path),
        ]
        kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "close_fds": True,
            "env": dict(os.environ),
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                | getattr(subprocess, "DETACHED_PROCESS", 0)
                | getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(command, **kwargs)
        return True
    except Exception as exc:
        log_error(f"detached strategy launch failed: {exc}")
        try:
            handle.close()
        except Exception:
            pass
        try:
            spool_path.unlink(missing_ok=True)
        except OSError:
            pass
        return False


def _detach_stop(
    settings: RuntimeSettings, payload: dict, log_error
) -> None:
    """Spool one Stop payload and launch a detached worker.

    Codex CLI 0.147 parses but skips native async hooks, so the registered Stop
    hook stays synchronous only long enough to start this background process.
    """
    if payload.get("hook_event_name") != "Stop":
        return
    spool_dir = settings.paths.data_dir / "spool"
    spool_dir.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="codex-stop-",
        dir=spool_dir,
        delete=False,
        encoding="utf-8",
    )
    spool_path = Path(handle.name)
    try:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--host",
            "codex_cli",
            "--payload-file",
            str(spool_path),
        ]
        kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "close_fds": True,
            "env": dict(os.environ),
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                | getattr(subprocess, "DETACHED_PROCESS", 0)
                | getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(command, **kwargs)
    except Exception as exc:
        log_error(f"detached Stop launch failed: {exc}")
        try:
            handle.close()
        except Exception:
            pass
        try:
            spool_path.unlink(missing_ok=True)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default="codex_cli")
    parser.add_argument("--detach-stop", action="store_true")
    parser.add_argument("--payload-file", default="")
    parser.add_argument("--strategy-payload-file", default="")
    args, _unknown = parser.parse_known_args()
    settings = _settings(args.host)
    log_error = lambda message: _log_error(settings, message)
    if args.host != "codex_cli":
        log_error(f"unsupported hook host: {args.host}")
        return 0
    try:
        if args.strategy_payload_file:
            strategy_payload = _read_payload(args.strategy_payload_file)
            CodexAdapter(
                ReviewCore(settings, log_error=log_error)
            )._run_strategy_payload(strategy_payload)
            return 0
        payload = _read_payload(args.payload_file)
        if args.detach_stop:
            if active_guard():
                return 0
            _detach_stop(settings, payload, log_error)
            return 0
        core = ReviewCore(settings, log_error=log_error)
        adapter = CodexAdapter(
            core,
            schedule_strategy=lambda work: _schedule_strategy(
                settings, work, log_error
            ),
        )
        output = adapter.process(payload)
        if output is not None:
            _emit_output(output, settings)
    except Exception as exc:
        log_error(f"hook processing failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
