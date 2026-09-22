from __future__ import annotations

import json
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MARKER = ROOT / ".codex" / "hook-started.json"
TARGET = ROOT / "target.txt"
RESULT = ROOT / "result.json"
READ_TIMEOUT_SECONDS = 60
TERMINAL_EVENT_WINDOW_SECONDS = 5


def find_codex() -> str:
    executable = shutil.which("codex.cmd") or shutil.which("codex")
    if not executable:
        raise RuntimeError("codex CLI was not found on PATH")
    return executable


def reader(stream, output: queue.Queue[dict | None]) -> None:
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            output.put(json.loads(line))
        except json.JSONDecodeError:
            continue
    output.put(None)


def stderr_reader(stream, lines: list[str]) -> None:
    for line in stream:
        lines.append(line.rstrip())


def main() -> int:
    TARGET.write_text("before\n", encoding="utf-8")
    MARKER.unlink(missing_ok=True)
    RESULT.unlink(missing_ok=True)

    trust_override = f"projects={{'{ROOT}'={{trust_level='trusted'}}}}"
    process = subprocess.Popen(
        [
            find_codex(),
            "--dangerously-bypass-hook-trust",
            "-c",
            "features.plugins=false",
            "-c",
            "features.hooks=true",
            "-c",
            trust_override,
            "app-server",
            "--stdio",
        ],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    assert process.stdin and process.stdout and process.stderr

    messages: queue.Queue[dict | None] = queue.Queue()
    stderr_lines: list[str] = []
    threading.Thread(target=reader, args=(process.stdout, messages), daemon=True).start()
    threading.Thread(
        target=stderr_reader, args=(process.stderr, stderr_lines), daemon=True
    ).start()

    transcript: list[dict] = []
    next_id = 1

    def send(method: str, params: dict | None = None) -> int:
        nonlocal next_id
        request_id = next_id
        next_id += 1
        message: dict = {"id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        process.stdin.flush()
        return request_id

    def notify(method: str) -> None:
        process.stdin.write(json.dumps({"method": method}) + "\n")
        process.stdin.flush()

    def receive(deadline: float) -> dict:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("timed out waiting for app-server message")
        message = messages.get(timeout=remaining)
        if message is None:
            raise RuntimeError("app-server closed stdout")
        transcript.append(message)
        return message

    def wait_for_response(request_id: int, timeout: int = READ_TIMEOUT_SECONDS) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            message = receive(deadline)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"app-server request failed: {message['error']}")
                return message["result"]

    try:
        initialize_id = send(
            "initialize",
            {
                "clientInfo": {
                    "name": "post-tool-use-cancellation-repro",
                    "version": "1.0.0",
                },
                "capabilities": {"experimentalApi": True},
            },
        )
        wait_for_response(initialize_id)
        notify("initialized")

        thread_id_request = send(
            "thread/start",
            {
                "cwd": str(ROOT),
                "approvalPolicy": "never",
                "sandbox": "danger-full-access",
                "ephemeral": True,
                "config": {
                    "bypass_hook_trust": True,
                    "features.hooks": True,
                    "features.plugins": False,
                },
            },
        )
        thread_result = wait_for_response(thread_id_request)
        thread_id = thread_result["thread"]["id"]

        prompt = (
            "Call apply_patch exactly once with this exact patch and then stop: "
            "*** Begin Patch\n*** Update File: target.txt\n@@\n-before\n+after\n"
            "*** End Patch"
        )
        turn_request = send(
            "turn/start",
            {
                "threadId": thread_id,
                "input": [{"type": "text", "text": prompt}],
            },
        )
        turn_result = wait_for_response(turn_request)
        turn_id = turn_result["turn"]["id"]

        hook_started: dict | None = None
        deadline = time.monotonic() + READ_TIMEOUT_SECONDS
        while hook_started is None or not MARKER.exists():
            message = receive(deadline)
            if message.get("method") == "hook/started":
                params = message.get("params", {})
                if (
                    params.get("turnId") == turn_id
                    and params.get("run", {}).get("eventName") == "postToolUse"
                ):
                    hook_started = params

        interrupt_id = send(
            "turn/interrupt", {"threadId": thread_id, "turnId": turn_id}
        )
        wait_for_response(interrupt_id)

        hook_run_id = hook_started["run"]["id"]
        deadline = time.monotonic() + TERMINAL_EVENT_WINDOW_SECONDS
        while time.monotonic() < deadline:
            try:
                receive(deadline)
            except (TimeoutError, queue.Empty):
                break

        hook_completed = [
            message.get("params", {})
            for message in transcript
            if message.get("method") == "hook/completed"
            and message.get("params", {}).get("run", {}).get("id") == hook_run_id
        ]
        turn_completed = next(
            (
                message.get("params", {})
                for message in transcript
                if message.get("method") == "turn/completed"
                and message.get("params", {}).get("turn", {}).get("id") == turn_id
            ),
            None,
        )

        turn_status = (
            turn_completed.get("turn", {}).get("status") if turn_completed else None
        )
        reproduced = turn_status == "interrupted" and not hook_completed
        result = {
            "codex_version": subprocess.run(
                [find_codex(), "--version"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            ).stdout.strip(),
            "hook_started_run_id": hook_run_id,
            "hook_completed_count": len(hook_completed),
            "turn_completed": turn_completed is not None,
            "turn_status": turn_status,
            "observation_window_seconds": TERMINAL_EVENT_WINDOW_SECONDS,
            "reproduced": reproduced,
        }
        RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if reproduced else 1
    except Exception as error:
        diagnostic = {
            "error": f"{type(error).__name__}: {error}",
            "target": TARGET.read_text(encoding="utf-8").strip(),
            "marker_exists": MARKER.exists(),
            "messages": transcript,
            "stderr": stderr_lines[-20:],
        }
        RESULT.write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
