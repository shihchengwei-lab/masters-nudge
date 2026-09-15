"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable


def delivery_text(
    current_choice: str,
    structural_cost: str,
    direction: str,
    evidence: tuple[str, ...] | list[str],
) -> str:
    evidence_text = ", ".join(str(item).strip() for item in evidence if str(item).strip())
    return (
        "Provider 結構提醒（供參考）："
        f"目前選擇：{str(current_choice).strip()}；"
        f"結構成本：{str(structural_cost).strip()}；"
        f"方向：{str(direction).strip()}；"
        f"證據：{evidence_text}。Actor 負責驗證與實作。"
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
