"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, Iterable

PRINCIPLE_LABELS = ("validity", "causality", "predictability")
NUDGE_PREFIXES = tuple(f"{principle} warning: " for principle in PRINCIPLE_LABELS)
CODE_TASTE_HINTS = (
    "資料結構能排除不可能的狀態，就不必讓每條路徑重複防守。",
    "旗標組合越多，資料模型容許的矛盾狀態通常也越多。",
    "事件是已發生的事實；狀態應沿單一方向由事件推導。",
    "許多時序問題源自缺少唯一的因果順序，而非缺少重試。",
    "好的抽象讓人能局部推理，不必在腦中執行整個系統。",
    "依賴與副作用越隱晦，所謂彈性越容易變成不可預測。",
)


def is_principle(value: str) -> bool:
    return str(value or "") in PRINCIPLE_LABELS


def has_nudge_prefix(relationship: str) -> bool:
    return str(relationship or "").startswith(NUDGE_PREFIXES)


def delivery_text(principle: str, anchor: str, relationship: str) -> str:
    return (
        f"{principle} warning: {str(anchor or '').strip()} — "
        f"{str(relationship or '').strip()}"
    )


def no_finding_hint(seed: str) -> str:
    """Choose one stable local hint without turning it into a Nudge finding."""
    digest = hashlib.sha256(str(seed or "").encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(CODE_TASTE_HINTS)
    return f"hint: {CODE_TASTE_HINTS[index]}"


def build_review_input(source_packet: str, recent_nudges: Iterable[str]) -> str:
    """Prepend up to three prior Nudge texts as exclusions, never as evidence."""
    exclusions = [str(value or "").strip() for value in recent_nudges]
    exclusions = [value for value in exclusions if value][-3:]
    packet = str(source_packet or "")
    if not exclusions:
        return packet
    section = "\n".join(
        (
            "[recent returned nudges — exclusions, not evidence]",
            *(f"- {value}" for value in exclusions),
            "[end recent returned nudges — exclusions]",
        )
    )
    return f"{section}\n\n{packet}"


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
