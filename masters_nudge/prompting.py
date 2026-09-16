"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable


def delivery_text(
    message: str,
    evidence: tuple[str, ...] | list[str],
) -> str:
    evidence_text = ", ".join(str(item).strip() for item in evidence if str(item).strip())
    return (
        f"Nudge：{str(message).strip()}\n"
        f"證據：{evidence_text}\n"
        "請重新比較可行解法；Actor 自行決定、實作與驗證。"
    )


def load_system_prompt(
    *,
    prompt_file: Path,
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""
    return base_prompt + "\n"
