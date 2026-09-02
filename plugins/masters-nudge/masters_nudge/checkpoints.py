"""Recognize observable results worth offering to one Nudge Lens."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import source_context

from .contracts import ToolCompleted


RESULT_MAX_CHARS = 5000
CHANGE_MAX_CHARS = source_context.WORKSPACE_SNAPSHOT_MAX_CHARS
VALIDATION_RE = re.compile(
    r"\b(?:pytest|unittest|vitest|jest|eslint|mocha|node\s+--test|"
    r"npx\s+(?:eslint|mocha|jest|vitest)|cargo\s+test|go\s+test|dotnet\s+test|"
    r"flutter\s+test|(?:npm|pnpm|yarn)\s+(?:run\s+)?(?:test|lint|build|verify))\b",
    re.IGNORECASE,
)
STANDALONE_VALIDATION_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:build|verify)(?=\s|$)", re.IGNORECASE
)
MEASUREMENT_RE = re.compile(r"\b(?:benchmark|bench|profile|trace)\b", re.IGNORECASE)
FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b|\btests? failed\b|"
    r"Traceback \(most recent call last\):|"
    r"\b(?:AssertionError|ImportError|TypeError|RuntimeError|SyntaxError):",
    re.IGNORECASE,
)
NAVIGATION_RE = re.compile(
    r"^(?:rg|grep|find|ls|dir|sed|head|tail|type|cat|get-content|get-childitem|"
    r"read|open|view|search)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class WorkspaceState:
    snapshot: str


def _compact(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except (TypeError, ValueError):
            text = str(value or "")
    return source_context.head_tail(text.strip(), RESULT_MAX_CHARS)


def _command(event: ToolCompleted) -> str:
    if isinstance(event.tool_input, dict):
        return str(
            event.tool_input.get("command")
            or event.tool_input.get("cmd")
            or event.tool_input.get("patch")
            or ""
        ).strip()
    return str(event.tool_input or "").strip()


def evidence_category(event: ToolCompleted) -> str:
    if not event.completed:
        return ""
    command = _command(event)
    semantic = f"{event.tool_name} {command}"
    output = _compact(event.tool_output)
    if is_navigation(event):
        return ""
    if event.failure_known and event.failed:
        return "failure"
    if MEASUREMENT_RE.search(semantic):
        return "failure" if FAILURE_RE.search(output) else "measurement"
    if _is_validation(event):
        return "failure" if FAILURE_RE.search(output) else "verification"
    if event.mutating or re.search(
        r"(?:apply_patch|file_change|write_file|edit_file|^edit$|^write$)",
        event.tool_name,
        re.IGNORECASE,
    ):
        return "change"
    return ""


def is_navigation(event: ToolCompleted) -> bool:
    if not event.completed:
        return False
    command = _command(event)
    return bool(NAVIGATION_RE.search(command)) and not _is_validation(event)


def _is_validation(event: ToolCompleted) -> bool:
    command = _command(event)
    semantic = f"{event.tool_name} {command}"
    return bool(
        VALIDATION_RE.search(semantic)
        or STANDALONE_VALIDATION_RE.search(command)
    )


def render_actor_source_record(event: ToolCompleted) -> str:
    """Preserve only navigation output that the host already returned."""
    if not is_navigation(event):
        return ""
    if isinstance(event.tool_output, str):
        result = event.tool_output.strip()
    else:
        try:
            result = json.dumps(
                event.tool_output,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ).strip()
        except (TypeError, ValueError):
            result = str(event.tool_output or "").strip()
    if not result:
        return ""
    command = _command(event)
    return (
        f"actual_command:\n{source_context.head_tail(command, 1800)}\n\n"
        f"result:\n{result}"
    )


def _untracked_files(cwd: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return []
    return [value for value in result.stdout.split("\0") if value] if result.returncode == 0 else []


def _untracked_state(session) -> list[str]:
    if not session.cwd:
        return []
    root = Path(session.cwd).resolve()
    paths = _untracked_files(session.cwd)
    paths.sort()
    rendered: list[str] = []
    for index, relative in enumerate(paths):
        display_path = relative.replace("\\", "/")
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
        except (OSError, ValueError):
            continue
        if index < 3:
            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            bounded = source_context.head_tail(content, 700)
            rendered.append(f"untracked_file: {display_path}\n{bounded}")
    return rendered


def _git_diff_units(raw_diff: str) -> list[str]:
    blocks = re.split(r"(?m)(?=^diff --git )", str(raw_diff or "").strip())
    units: list[str] = []
    for block in (value.strip() for value in blocks if value.strip()):
        lines = block.splitlines()
        if not lines or not lines[0].startswith("diff --git "):
            units.append(block)
            continue
        hunk_starts = [
            index for index, line in enumerate(lines) if line.startswith("@@ ")
        ]
        if not hunk_starts:
            units.append(block)
            continue
        prefix = lines[: hunk_starts[0]]
        for position, start in enumerate(hunk_starts):
            end = (
                hunk_starts[position + 1]
                if position + 1 < len(hunk_starts)
                else len(lines)
            )
            header = prefix if position == 0 else [lines[0]]
            units.append("\n".join([*header, *lines[start:end]]))
    return units


def _render_bounded_units(units: list[str], max_chars: int) -> str:
    units = [value.strip() for value in units if value.strip()]
    if not units or max_chars <= 0:
        return ""
    combined = "\n\n".join(units)
    if len(combined) <= max_chars:
        return combined
    separator_chars = 2 * (len(units) - 1)
    available = max_chars - separator_chars
    if available <= 0:
        return source_context.head_tail(combined, max_chars)

    budgets = [0] * len(units)
    active = set(range(len(units)))
    remaining = available
    while active:
        share = remaining // len(active)
        fitting = [index for index in active if len(units[index]) <= share]
        if not fitting:
            for offset, index in enumerate(sorted(active)):
                budgets[index] = share + (1 if offset < remaining % len(active) else 0)
            break
        for index in fitting:
            budgets[index] = len(units[index])
            remaining -= budgets[index]
            active.remove(index)

    return "\n\n".join(
        source_context.head_tail(unit, budgets[index])
        for index, unit in enumerate(units)
        if budgets[index] > 0
    )


def render_workspace_diff(raw_diff: str, max_chars: int) -> str:
    return _render_bounded_units(_git_diff_units(raw_diff), max_chars)


def workspace_state(session) -> WorkspaceState:
    if not session.cwd:
        return WorkspaceState("")
    try:
        result = subprocess.run(
            ["git", "diff", "--binary", "--unified=1", "HEAD", "--"],
            cwd=session.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return WorkspaceState("")
    if result.returncode != 0:
        return WorkspaceState("")
    untracked_units = _untracked_state(session)
    units = _git_diff_units(result.stdout)
    units.extend(untracked_units)
    return WorkspaceState(_render_bounded_units(units, CHANGE_MAX_CHARS))


def working_diff(session) -> str:
    return workspace_state(session).snapshot


def render_evidence_record(event: ToolCompleted) -> str:
    """Preserve the real command and result; do not infer semantic scope."""
    category = evidence_category(event)
    command = _command(event)
    result = _compact(event.tool_output)
    parts: list[str] = []
    if command:
        parts.append(f"actual_command:\n{source_context.head_tail(command, 1800)}")
    if result:
        parts.append(f"result:\n{result}")
    return "\n\n".join(parts)
