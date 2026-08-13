"""Host-neutral evidence helpers that do not depend on transcript formats."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import source_context

from .contracts import find_git_root


AGENTCAM_REPORT_READ_CHARS = 65536


def read_latest_agentcam_report(
    cwd: str, *, log_error: Callable[[str], None] | None = None
) -> dict[str, object] | None:
    root = find_git_root(cwd)
    if not root:
        return None
    runs_dir = Path(root) / ".git" / "agentcam" / "runs"
    if not runs_dir.is_dir():
        return None
    try:
        candidates = list(runs_dir.glob("*/AGENT_RUN_REPORT.md"))
        newest = max(candidates, key=lambda path: path.stat().st_mtime)
        content = newest.read_text(encoding="utf-8", errors="replace")
        mtime = newest.stat().st_mtime
    except (OSError, ValueError) as exc:
        if log_error:
            log_error(f"agentcam report read failed: {exc}")
        return None
    return {
        "path": str(newest),
        "content": source_context.head_tail(content, AGENTCAM_REPORT_READ_CHARS),
        "mtime": mtime,
    }
