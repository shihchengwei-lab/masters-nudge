"""Host-neutral checkpoint classification and bounded event rendering."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from typing import Any

import source_context

from .contracts import ToolCompleted


MAX_EVENT_CONTEXT_CHARS = 5000
SEMANTIC_CHANGE_MAX_CHARS = 1800
MIDTURN_REVIEW_LIMIT = 3
TEST_FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b"
    r"|\btests?\s+failed\b"
    r"|^FAIL(?:ED)?\b"
    r"|\s[✗✘]\s",
    re.IGNORECASE | re.MULTILINE,
)
RUNTIME_FAILURE_RE = re.compile(
    r"\bTraceback \(most recent call last\):"
    r"|\b(?:AssertionError|ModuleNotFoundError|ImportError|"
    r"TypeError|ValueError|RuntimeError|SyntaxError)(?::|\s*$)",
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
    raw = json.dumps(
        {"reason": reason, "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return f"{reason}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"


def tool_event_fingerprint(event: ToolCompleted) -> str:
    """Identify an exact consecutive native event replay."""
    return stable_fingerprint(
        "tool-event",
        {
            "tool_name": event.tool_name,
            "tool_input": event.tool_input,
            "tool_output": event.tool_output,
            "failed": event.failed,
            "failure_known": event.failure_known,
            "mutating": event.mutating,
        },
    )


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
    test_command = bool(TEST_COMMAND_RE.search(command))
    validation_like = bool(test_command or SEMANTIC_VALIDATION_RE.search(semantic_text))
    if event.failure_known and event.failed:
        return "failure"
    if READ_NAVIGATION_RE.search(semantic_text) and not test_command:
        return ""
    if validation_like and (
        TEST_FAILURE_RE.search(output) or RUNTIME_FAILURE_RE.search(output)
    ):
        return "failure"
    if SEMANTIC_MUTATION_RE.search(semantic_text):
        return "change"
    if validation_like:
        return "verification"
    return ""


def evidence_scope(event: ToolCompleted) -> str:
    """Identify the validated surface without putting commands in the packet."""
    category = evidence_category(event)
    if category not in {"verification", "failure"}:
        return ""
    command = _command(event).strip()
    command = re.sub(
        r"^(?:[A-Za-z_][A-Za-z0-9_]*=[^\s]+\s+)+", "", command
    )
    if not command:
        return ""
    tokens = re.findall(r"[^\s'\"]+", command)
    targets: list[str] = []
    for token in tokens:
        value = token.strip(" ,;()[]{}")
        if not value or value.startswith("-"):
            continue
        normalized = value.replace("\\", "/").lower()
        if (
            "::" in normalized
            or "/test" in normalized
            or normalized.startswith(("test", "tests/", "testing/"))
            or re.search(r"\.(?:py|js|jsx|ts|tsx|go|rs|java|rb)(?:::\S+)?$", normalized)
        ):
            if normalized not in targets:
                targets.append(normalized)
    if targets:
        semantic = "|".join(targets[:4])
        return source_context.head_tail(f"validation:{semantic}", 160)
    family = command_family(event)
    if not family:
        return ""
    runner = re.search(
        r"\b(pytest|py\.test|unittest|vitest|jest|mocha|rspec|cargo\s+test|"
        r"go\s+test|dotnet\s+test|flutter\s+test)\b",
        command,
        re.IGNORECASE,
    )
    return f"validation-suite:{runner.group(1).lower()}" if runner else f"validation-family:{family}"


def failure_family(event: ToolCompleted) -> str:
    """Group retries by the observable surface, not by incidental CLI flags."""
    return evidence_scope(event) if evidence_category(event) == "failure" else ""


def _semantic_change_excerpt(event: ToolCompleted) -> str:
    raw = _command(event).strip()
    if "apply_patch" in event.tool_name.lower() and raw:
        lines = []
        for line in raw.splitlines():
            if line.startswith(("*** Begin Patch", "*** End Patch", "*** Add File:",
                                "*** Update File:", "*** Delete File:", "*** Move to:")):
                continue
            if line.startswith(("@@", "+", "-")):
                lines.append(line)
        return source_context.head_tail("\n".join(lines), SEMANTIC_CHANGE_MAX_CHARS)
    if event.session.cwd:
        diff = _git_output(["diff", "--unified=1", "HEAD", "--"], event.session.cwd)
        if diff:
            return source_context.head_tail(diff, SEMANTIC_CHANGE_MAX_CHARS)
    return ""


def render_evidence_record(event: ToolCompleted) -> str:
    """Render semantic evidence without exposing tool identity or commands."""
    category = evidence_category(event)
    output = compact_json(event.tool_output)
    if category == "change":
        changed_paths: list[str] = []
        if "apply_patch" in event.tool_name.lower():
            raw = _command(event).strip() or compact_json(event.tool_input)
            for path in re.findall(
                r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$|"
                r"^\*\*\* Move to:\s*(.+?)\s*$",
                raw,
                re.MULTILINE,
            ):
                value = next((item.strip() for item in path if item.strip()), "")
                if value and value not in changed_paths:
                    changed_paths.append(value)
        parts = []
        if changed_paths:
            parts.append("changed_paths:\n" + "\n".join(f"- {path}" for path in changed_paths))
        semantic_change = _semantic_change_excerpt(event)
        if semantic_change:
            parts.append(f"semantic_change:\n{semantic_change}")
        if output:
            parts.append(f"result:\n{output}")
        return "\n".join(parts)
    label = "failure" if category == "failure" else "verification"
    return f"{label}:\n{output}" if output else ""


def classify_strategy(
    progress: dict[str, Any],
) -> dict[str, str] | None:
    recent = progress.get("recent") if isinstance(progress.get("recent"), list) else []
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
        midturn_attempts = int(progress.get("midturn_review_attempts") or 0)
        if midturn_attempts >= MIDTURN_REVIEW_LIMIT:
            return None
        failures = [item for item in since if item.get("failed")]
        failure_counts: dict[str, int] = {}
        for item in failures:
            family = str(item.get("failure_family") or "")
            if family:
                failure_counts[family] = failure_counts.get(family, 0) + 1
        repeated_failure = any(count >= 2 for count in failure_counts.values())
        if repeated_failure:
            reason, trigger = "strategy-review", "repeated-failure-family"
        elif completed_semantic_cycles_after(progress, last_seq) >= (
            1 if midturn_attempts == 0 else 2
        ):
            reason, trigger = "strategy-review", "validated-progress"
        else:
            return None
    lines = [
        f"reason: {reason}",
        f"trigger: {trigger}",
    ]
    return {
        "reason": reason,
        "trigger": trigger,
        "routing_concern": routing_concern_for_trigger(trigger),
        "context": "\n".join(lines),
        "fingerprint": f"{reason}-{trigger}",
    }


def completed_semantic_cycles_after(
    progress: dict[str, Any], event_seq: int
) -> int:
    """Count change-to-validation boundaries after ``event_seq``."""
    recent = progress.get("recent") if isinstance(progress.get("recent"), list) else []
    categories = [
        str(item.get("evidence_category") or "")
        for item in recent
        if int(item.get("event_seq") or 0) > int(event_seq or 0)
    ]
    cycles = 0
    changed = False
    for category in categories:
        if category == "change":
            changed = True
        elif changed and category in {"verification", "failure"}:
            cycles += 1
            changed = False
    return cycles


def semantic_cycle_after(progress: dict[str, Any], event_seq: int) -> bool:
    """Wait for one post-Nudge change and one resulting validation boundary."""
    return completed_semantic_cycles_after(progress, event_seq) > 0
