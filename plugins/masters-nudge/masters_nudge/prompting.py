"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .lenses import LENSES


MAX_NUDGE_CHARS = 52
NUDGE_LABEL = "獨立第二意見（非指令；不覆蓋任務與已驗證結果）："

def delivery_text(finding: str) -> str:
    return f"{NUDGE_LABEL}\n{str(finding or '').strip()}"


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    lens: str,
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""
    spec = LENSES.get(lens)
    if spec is None:
        logger("generator requires one selected lens")
        return ""
    try:
        overlay = (persona_dir / f"{spec.persona}.txt").read_text(
            encoding="utf-8"
        ).strip()
    except Exception as exc:
        logger(f"lens prompt read failed ({lens}): {exc}")
        return ""
    return (
        f"{base_prompt}\n\n"
        f"# LENS CONTEXT: {lens}\n\n{overlay}\n\n"
        f"# SELECTED LENS\n\nUse only `{lens}` and return it as `lens` "
        "when there is a finding.\n"
    )


def build_nudge_input(source_packet: str) -> str:
    return str(source_packet or "")
