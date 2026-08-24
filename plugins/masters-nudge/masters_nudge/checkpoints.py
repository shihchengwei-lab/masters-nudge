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
GOAL_TOOLS = {"create_goal", "update_goal"}
MEANINGFUL_TOOL_RE = re.compile(
    r"(?:apply_patch|write|edit|test|verify|benchmark|build|plan|goal)", re.IGNORECASE
)
SEMANTIC_MUTATION_RE = re.compile(
    r"(?:\bapply_patch\b|\bwrite\b|\bedit\b)", re.IGNORECASE
)
SEMANTIC_VALIDATION_RE = re.compile(
    r"\b(?:test|verify|benchmark|build|pytest|unittest|vitest|jest|cargo|dotnet)\b"
    r"|(?<!\w)(?:test|verify|benchmark|build)(?=[_.-])",
    re.IGNORECASE,
)
READ_NAVIGATION_RE = re.compile(
    r"(?:^|\b)(?:rg|grep|find|ls|dir|sed|head|tail|type|cat|get-content|"
    r"read|open|view|search)(?:\b|$)",
    re.IGNORECASE,
)

TRIGGER_ROUTING_CONCERNS = {
    "repeated-command-family": "feedback-loop",
    "repeated-failure-family": "feedback-loop",
    "diff-growth": "knowledge-boundary",
    "goal-complete": "completion-boundary",
    "goal-blocked": "completion-boundary",
}


def routing_concern_for_trigger(trigger: str) -> str:
    """Map classifier-owned triggers to router-owned structured concerns."""
    return TRIGGER_ROUTING_CONCERNS.get(str(trigger or ""), "")


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


def command_family(event: ToolCompleted) -> str:
    """Return a stable, low-cardinality family for repetition detection."""
    command = _command(event).strip()
    if not command:
        return event.tool_name.lower() if MEANINGFUL_TOOL_RE.search(event.tool_name) else ""
    words = re.findall(r"[A-Za-z0-9_.-]+", command.lower())
    if not words:
        return event.tool_name.lower()
    launchers = {"python", "python3", "py", "node", "npx", "npm", "pnpm", "yarn"}
    width = 3 if words[0] in launchers else 2
    return " ".join(words[:width])


def goal_transition(event: ToolCompleted) -> tuple[str, str]:
    tool = event.tool_name.lower().split("__")[-1]
    if tool not in GOAL_TOOLS or not isinstance(event.tool_input, dict):
        return "", ""
    if tool == "create_goal":
        return "created", str(event.tool_input.get("objective") or "")
    status = str(event.tool_input.get("status") or "").lower()
    return (status if status in {"complete", "blocked"} else ""), ""


def evidence_category(event: ToolCompleted) -> str:
    """Classify durable evidence; routine navigation intentionally stays out."""
    output = compact_json(event.tool_output)
    command = _command(event)
    semantic_text = f"{event.tool_name} {command}"
    if (event.failure_known and event.failed) or TEST_FAILURE_RE.search(output):
        return "failure"
    if READ_NAVIGATION_RE.search(semantic_text):
        return ""
    if SEMANTIC_MUTATION_RE.search(semantic_text):
        return "change"
    if TEST_COMMAND_RE.search(command) or SEMANTIC_VALIDATION_RE.search(
        semantic_text
    ):
        return "verification"
    return ""


def render_evidence_record(event: ToolCompleted) -> str:
    """Render semantic evidence without exposing tool identity or commands."""
    category = evidence_category(event)
    output = compact_json(event.tool_output)
    if category == "change":
        change = ""
        if "apply_patch" in event.tool_name.lower():
            raw = _command(event).strip() or compact_json(event.tool_input)
            marker = raw.find("*** Begin Patch")
            if marker >= 0:
                change = raw[marker:]
        parts = [f"change:\n{change}"] if change else []
        if output:
            parts.append(f"result:\n{output}")
        return "\n".join(parts)
    label = "failure" if category == "failure" else "verification"
    return f"{label}:\n{output}" if output else ""


def classify_strategy(
    progress: dict[str, Any],
    *,
    changed_line_count: int | None,
) -> dict[str, str] | None:
    recent = progress.get("recent") if isinstance(progress.get("recent"), list) else []
    event_seq = int(progress.get("event_seq") or 0)
    last_seq = int(progress.get("last_strategy_event_seq") or 0)
    since = [
        item
        for item in recent
        if int(item.get("event_seq") or 0) > last_seq and item.get("meaningful")
    ]
    if not since:
        return None
    latest_transition = str(since[-1].get("goal_transition") or "")
    if latest_transition in {"complete", "blocked"}:
        reason = "goal-transition"
        trigger = f"goal-{latest_transition}"
    else:
        families = [str(item.get("command_family") or "") for item in since]
        repeated = next(
            (family for family in reversed(families) if family and families.count(family) >= 3),
            "",
        )
        failures = [item for item in since if item.get("failed")]
        baseline = int(progress.get("changed_lines_at_strategy") or 0)
        diff_growth = (
            changed_line_count is not None
            and changed_line_count - baseline >= LARGE_DIFF_THRESHOLD
        )
        if repeated:
            reason, trigger = "strategy-review", "repeated-command-family"
        elif len(failures) >= 2:
            reason, trigger = "strategy-review", "repeated-failure-family"
        elif diff_growth:
            reason, trigger = "strategy-review", "diff-growth"
        else:
            return None
    lines = [
        f"reason: {reason}",
        f"trigger: {trigger}",
        f"event_seq: {event_seq}",
    ]
    return {
        "reason": reason,
        "trigger": trigger,
        "routing_concern": routing_concern_for_trigger(trigger),
        "context": "\n".join(lines),
        "fingerprint": f"{reason}-{trigger}-{event_seq}",
    }


def _failure_checkpoint(
    event: ToolCompleted, *, reason: str, output: str, evidence_label: str
) -> dict[str, str]:
    payload = {
        "tool_name": event.tool_name,
        "tool_input": event.tool_input,
        "tool_output": output,
    }
    return {
        "reason": reason,
        "context": (
            f"reason: {reason}\n"
            f"{evidence_label}: {output}"
        ),
        "fingerprint": stable_fingerprint(reason, payload),
    }


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
        return _failure_checkpoint(
            event, reason=reason, output=output, evidence_label="failure"
        )

    if is_shell and TEST_FAILURE_RE.search(output):
        return _failure_checkpoint(
            event, reason="test-fail", output=output, evidence_label="result"
        )

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
            f"working tree: 偵測到至少 {changed_line_count} 行變動"
        ),
        "fingerprint": stable_fingerprint(reason, {}),
    }
