"""Claude hook session mapping and successful wire-return audit."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import storage
from .contracts import SessionRef, find_git_root
from .runtime import RuntimeSettings


RUNTIME = RuntimeSettings.from_env(Path(__file__).resolve().parent.parent, host="claude_code")


@dataclass(frozen=True)
class PreparedDelivery:
    output: dict[str, Any]
    session: SessionRef
    lens: str
    finding: str
    returned_via: str


def log_error(component: str, message: str) -> None:
    storage.append_error(runtime_settings().paths.error_log, component, message)


def runtime_settings() -> RuntimeSettings:
    return RUNTIME


def session_from_hook(hook: dict, *, default_cwd: str = "") -> SessionRef:
    cwd = str(hook.get("cwd") or default_cwd)
    return SessionRef(
        "claude_code",
        str(hook.get("session_id") or "unknown"),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )


def emit_json_delivery(prepared: PreparedDelivery, stream: Any = None) -> None:
    """Audit only after the Nudge has been flushed back to Claude Code."""
    target = stream if stream is not None else sys.stdout
    target.write(json.dumps(prepared.output, ensure_ascii=False) + "\n")
    target.flush()
    storage.append_host_returned_nudge(
        runtime_settings().paths.data_dir,
        prepared.session,
        lens=prepared.lens,
        finding=prepared.finding,
        returned_via=prepared.returned_via,
    )
