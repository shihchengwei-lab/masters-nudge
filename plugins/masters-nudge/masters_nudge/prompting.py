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

AUTOMATIC_ROUTING_PROMPT = """# AUTOMATIC LENS ROUTER

Find one unresolved engineering choice in the supplied evidence, then choose
the one Lens whose taste is most relevant to that choice:

- jeff: system shape, data movement, ownership, scale, and downstream cost.
- linus: data shape, interfaces, special cases, and unnecessary complexity.
- fowler: duplicated knowledge, change spread, naming, and responsibility.
- beck: uncertainty that a smaller feedback step can resolve before expansion.
- lamport: state, event order, invariants, retries, and partial failure.
- carmack: measured runtime cost, hot paths, and work the machine need not do.

Route by decision pressure, not lifecycle stage, project topic, test presence,
or failure presence. Do not give advice and do not produce a Nudge. The full
persona contexts are intentionally absent.

Return exactly one JSON object. Use `finding` only as the unresolved decision:

{"status":"finding","effective_lens":"linus","finding":"如何記錄輸入值的來源"}

or, when no unresolved choice is supported by the evidence:

{"status":"no_finding","effective_lens":"none","finding":""}
"""


def build_router_prompt() -> str:
    return AUTOMATIC_ROUTING_PROMPT.strip() + "\n"

def delivery_text(finding: str) -> str:
    """Identify reviewer provenance without changing the stored finding."""
    return f"{INDEPENDENT_OPINION_LABEL}\n{str(finding or '').strip()}"


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    route: lens_router.ReviewRoute,
    route_decision: str = "",
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
    selected_lens = route.lens
    selected = (selected_lens,) if selected_lens else ()
    if not selected:
        logger("generator requires one selected lens")
        return ""
    overlays = []
    for persona in selected:
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
        overlays.append(f"# LENS CONTEXT: {persona}\n\n{overlay}")

    contract_marker = "\n# NUDGE\n"
    foundation, marker, contract = base_prompt.partition(contract_marker)
    if not marker:
        logger("prompt file is missing the # NUDGE contract")
        return ""
    sections = (
        foundation.strip(),
        "\n\n".join(overlays),
        str(timing_prompt or "").strip(),
        (
            "# ROUTING HYPOTHESIS — NOT EVIDENCE\n\n"
            f"The router identified this unresolved choice: {route_decision.strip()}\n"
            "Verify it against the supplied evidence. If unsupported or already "
            "decided, return `no_finding`."
            if route_decision.strip()
            else ""
        ),
        (
            f"# SELECTED LENS\n\nUse only `{selected_lens}` and return it as "
            "`effective_lens` when there is a finding."
        ),
        lens_focus_prompt(selected_lens).strip(),
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
