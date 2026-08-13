"""Host-neutral checkpoint classification and bounded event rendering."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import source_context

from .contracts import ToolCompleted


LARGE_DIFF_THRESHOLD = 80
MAX_EVENT_CONTEXT_CHARS = 5000
SHELL_TOOLS = {"Bash", "PowerShell", "shell_command", "exec_command"}

TEST_FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b"
    r"|\btests?\s+failed\b"
    r"|^FAIL(?:ED)?\b"
    r"|\s[✗✘]\s",
    re.IGNORECASE | re.MULTILINE,
)
TEST_COMMAND_RE = re.compile(
    r"(?:^|[;&|\s])(?:"
    r"pytest|py\.test|unittest|vitest|jest|mocha|rspec|"
    r"npm\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|"
    r"yarn\s+(?:run\s+)?test|bun\s+test|cargo\s+test|"
    r"go\s+test|dotnet\s+test|mvn(?:w)?(?:\.cmd)?\s+test|"
    r"gradle(?:w)?(?:\.bat)?\s+test|flutter\s+test|dart\s+test"
    r")(?:\s|$)",
    re.IGNORECASE,
)


def compact_json(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            text = str(value)
    return source_context.head_tail(text.strip(), MAX_EVENT_CONTEXT_CHARS)


def stable_fingerprint(reason: str, payload: dict[str, Any]) -> str:
    if reason == "large-diff":
        return f"large-diff-over-{LARGE_DIFF_THRESHOLD}"
    raw = json.dumps(
        {"reason": reason, "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return f"{reason}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"


def _git_output(args: list[str], cwd: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def _parse_numstat(text: str) -> int:
    total = 0
    for line in text.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2 or parts[0] == "-" or parts[1] == "-":
            continue
        try:
            total += int(parts[0]) + int(parts[1])
        except ValueError:
            continue
    return total


def _count_text_lines(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            data = handle.read(1024 * 1024)
    except OSError:
        return 0
    if b"\x00" in data:
        return 0
    count = data.count(b"\n") + int(bool(data and not data.endswith(b"\n")))
    return min(count, LARGE_DIFF_THRESHOLD + 1)


def get_changed_line_count(cwd: str) -> int | None:
    tracked = _git_output(["diff", "--numstat", "HEAD", "--"], cwd)
    if tracked is None:
        tracked = _git_output(["diff", "--numstat", "--cached", "--"], cwd)
    untracked = _git_output(["ls-files", "--others", "--exclude-standard", "-z"], cwd)
    if tracked is None or untracked is None:
        return None
    total = _parse_numstat(tracked)
    root = Path(cwd).resolve()
    for relative in untracked.split("\0"):
        if not relative:
            continue
        try:
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                continue
        except (OSError, ValueError):
            continue
        total += _count_text_lines(candidate)
    return total


def _command(event: ToolCompleted) -> str:
    value = event.tool_input
    if isinstance(value, dict):
        return str(value.get("command") or value.get("cmd") or "")
    return str(value or "")


def classify_tool(
    event: ToolCompleted,
    changed_line_count: int | None = None,
) -> dict[str, str] | None:
    if event.interrupted:
        return None
    output = compact_json(event.tool_output)
    command = _command(event)
    is_shell = event.tool_name in SHELL_TOOLS

    if event.failure_known and event.failed:
        reason = (
            "test-fail"
            if (is_shell and TEST_COMMAND_RE.search(command))
            or TEST_FAILURE_RE.search(output)
            else "error"
        )
        payload = {
            "tool_name": event.tool_name,
            "tool_input": event.tool_input,
            "tool_output": output,
        }
        return {
            "reason": reason,
            "context": (
                f"reason: {reason}\n"
                f"tool: {event.tool_name}\n"
                f"input: {compact_json(event.tool_input)}\n"
                f"failure: {output}"
            ),
            "fingerprint": stable_fingerprint(reason, payload),
        }

    if is_shell and TEST_FAILURE_RE.search(output):
        reason = "test-fail"
        payload = {
            "tool_name": event.tool_name,
            "tool_input": event.tool_input,
            "tool_output": output,
        }
        return {
            "reason": reason,
            "context": (
                f"reason: {reason}\n"
                f"tool: {event.tool_name}\n"
                f"input: {compact_json(event.tool_input)}\n"
                f"result: {output}"
            ),
            "fingerprint": stable_fingerprint(reason, payload),
        }

    if not event.mutating:
        return None
    if changed_line_count is None:
        changed_line_count = get_changed_line_count(event.session.cwd or os.getcwd())
    if changed_line_count is None or changed_line_count <= LARGE_DIFF_THRESHOLD:
        return None
    reason = "large-diff"
    return {
        "reason": reason,
        "context": (
            f"reason: {reason}\n"
            f"tool: {event.tool_name}\n"
            f"input: {compact_json(event.tool_input)}\n"
            f"working tree: 偵測到至少 {changed_line_count} 行變動"
        ),
        "fingerprint": stable_fingerprint(reason, {}),
    }
