"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

PRINCIPLE_LABELS = ("validity", "causality", "predictability")
DELIVERY_MARKERS = {
    "contract_warning": "warning",
    "taste_nudge": "nudge",
}
NUDGE_PREFIXES = tuple(
    f"{principle} {marker}: "
    for principle in PRINCIPLE_LABELS
    for marker in DELIVERY_MARKERS.values()
)


def is_principle(value: str) -> bool:
    return str(value or "") in PRINCIPLE_LABELS


def is_delivery_status(value: str) -> bool:
    return str(value or "") in DELIVERY_MARKERS


def has_nudge_prefix(relationship: str) -> bool:
    return str(relationship or "").startswith(NUDGE_PREFIXES)


def delivery_text(
    status: str, principle: str, anchor: str, relationship: str
) -> str:
    marker = DELIVERY_MARKERS[str(status)]
    return (
        f"{principle} {marker}: {str(anchor or '').strip()} — "
        f"{str(relationship or '').strip()}"
    )


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
