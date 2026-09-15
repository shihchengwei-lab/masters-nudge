#!/usr/bin/env python3
"""Task and workspace facts supplied to the read-only Provider."""

from __future__ import annotations

from pathlib import Path
import subprocess


TASK_ANCHOR_MAX_CHARS = 2000
WORKSPACE_STATE_MAX_CHARS = 12000
CHANGED_SOURCES_MAX_CHARS = 16000
DECISION_SNAPSHOT_MAX_CHARS = 32000
TRUNCATION_MARKER = "\n[…中段已截斷…]\n"


def head_tail(text: str, max_chars: int) -> str:
    text = str(text or "").strip()
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars <= len(TRUNCATION_MARKER):
        return text[:max_chars]
    available = max_chars - len(TRUNCATION_MARKER)
    head_chars = max(1, (available * 2) // 5)
    return text[:head_chars] + TRUNCATION_MARKER + text[-(available - head_chars) :]


def _git_text(workspace_root: str, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def capture_workspace_state(workspace_root: str) -> str:
    """Capture repository facts without interpreting their engineering meaning."""
    if not str(workspace_root or "").strip():
        return "workspace unavailable"
    status = _git_text(workspace_root, "status", "--short", "--untracked-files=all")
    unstaged = _git_text(
        workspace_root, "diff", "--no-ext-diff", "--unified=24", "--"
    )
    staged = _git_text(
        workspace_root, "diff", "--cached", "--no-ext-diff", "--unified=24", "--"
    )
    sections = [f"status:\n{status or '(clean)'}"]
    if staged:
        sections.append(f"staged diff:\n{staged}")
    if unstaged:
        sections.append(f"unstaged diff:\n{unstaged}")
    return head_tail("\n\n".join(sections), WORKSPACE_STATE_MAX_CHARS)


def _changed_source_contents(
    workspace_root: str, changed_paths: tuple[str, ...]
) -> str:
    try:
        root = Path(workspace_root).resolve()
    except (OSError, RuntimeError):
        return ""
    rendered: list[str] = []
    seen: set[str] = set()
    for value in changed_paths:
        if value in seen:
            continue
        seen.add(value)
        try:
            reference = Path(value)
            candidate = (
                reference.resolve()
                if reference.is_absolute()
                else (root / reference).resolve()
            )
            candidate.relative_to(root)
            if not candidate.is_file():
                continue
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except (OSError, RuntimeError, ValueError):
            continue
        if "\x00" not in content:
            rendered.append(f"source: {value}\n{content}")
    return head_tail("\n\n".join(rendered), CHANGED_SOURCES_MAX_CHARS)


def build_decision_snapshot(
    *,
    task_contract: str,
    task_start: str,
    workspace_root: str,
    changed_paths: tuple[str, ...] = (),
) -> str:
    """Describe the decision from task and workspace facts, never Actor narration."""
    current = capture_workspace_state(workspace_root)
    changed = _changed_source_contents(workspace_root, changed_paths)
    sections = [
        f"[task contract]\n{head_tail(task_contract, TASK_ANCHOR_MAX_CHARS) or 'unknown'}\n[end task contract]",
        f"[task-start workspace]\n{task_start or 'workspace unavailable'}\n[end task-start workspace]",
        f"[current workspace]\n{current}\n[end current workspace]",
    ]
    if changed:
        sections.append(
            f"[current changed sources]\n{changed}\n[end current changed sources]"
        )
    sections.append(
        "[provider access]\nThe Provider may inspect this workspace with read-only tools. "
        "The Actor's prose and intended remedy are not evidence.\n[end provider access]"
    )
    return head_tail("\n\n".join(sections), DECISION_SNAPSHOT_MAX_CHARS)
