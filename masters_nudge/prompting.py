"""Host-neutral prompt assembly and reaction sanitation."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import lens_router
import persona_config


MAX_REACTION_CHARS = 52
INDEPENDENT_OPINION_LABEL = "獨立第二意見："
RECENT_NUDGES_MAX = 3

LENS_FOCUS = {
    "jeff": "Trace upstream constraints, ownership, and downstream cost.",
    "linus": "Trace the direct control flow, ownership, and necessary complexity.",
    "fowler": "Trace duplicated knowledge, change spread, and its proper home.",
    "beck": "Trace the shortest feedback path, observable behavior, and stop condition.",
    "lamport": "Trace state, event order, invariants, and partial failure.",
    "carmack": "Trace measured execution cost and work the machine need not do.",
}

def delivery_text(finding: str) -> str:
    """Identify reviewer provenance without changing the stored finding."""
    return f"{INDEPENDENT_OPINION_LABEL}\n{str(finding or '').strip()}"


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    route: lens_router.ReviewRoute,
    timing_prompt: str = "",
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8")
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""

    personas = persona_config.LENS_PERSONAS
    persona = route.effective_lens
    if persona not in personas:
        supported = ", ".join(personas)
        logger(f"unknown persona: {persona!r}; supported: {supported}")
        return ""

    persona_file = persona_dir / f"{persona}.txt"
    try:
        overlay = persona_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"persona prompt read failed ({persona}): {exc}")
        return ""

    contract_marker = "\n# NUDGE\n"
    foundation, marker, contract = base_prompt.partition(contract_marker)
    if not marker:
        logger("prompt file is missing the # NUDGE contract")
        return ""
    sections = (
        foundation.strip(),
        overlay,
        str(timing_prompt or "").strip(),
        lens_focus_prompt(route.effective_lens).strip(),
        f"# NUDGE\n{contract.strip()}",
    )
    return "\n\n".join(section for section in sections if section).rstrip() + "\n"


def lens_focus_prompt(effective_lens: str) -> str:
    focus = LENS_FOCUS.get(str(effective_lens or "").strip().lower(), "")
    if not focus:
        return ""
    return f"\n\n# LENS FOCUS\n\n{focus}\n"


def build_review_input(
    source_packet: str,
    recent_nudges: tuple[str, ...],
) -> str:
    """Add delivered findings only as a bounded duplicate-avoidance aid."""
    findings = tuple(
        str(finding or "").strip()
        for finding in recent_nudges[-RECENT_NUDGES_MAX:]
        if str(finding or "").strip()
    )
    if not findings:
        return source_packet
    block = "\n".join(
        (
            "[recent injected nudges — exclusions, not evidence]",
            "以下內容不是證據、建議或範例，也不表示主模型是否採納；不得引用、延續或模仿：",
            *(f"- {finding}" for finding in findings),
            "[end recent injected nudges — exclusions]",
        )
    )
    return f"{block}\n\n{source_packet.rstrip()}" if source_packet.strip() else block
