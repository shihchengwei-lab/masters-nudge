"""Prompt assembly and agent-visible Nudge formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import lens_router


MAX_NUDGE_CHARS = 52
NUDGE_LABEL = "獨立第二意見："

AUTOMATIC_ROUTING_PROMPT = """# AUTOMATIC LENS ROUTER

Use only the supplied task anchor and observable evidence. Select exactly one
Lens only when its minimum evidence is present:

- simplicity: a current mechanism or ownership path contains a wrapper,
  fallback, compatibility path, workaround, duplicate owner, or accumulating
  patch whose necessity can be judged from the packet.
- reliability: the packet states an invariant, at least two reorderable events,
  and a concrete retry, interruption, redelivery, or partial-success path.
- performance: profiler, benchmark, or trace numbers locate actual cost on a
  concrete execution path.

An abstraction alone does not qualify simplicity. Async or network vocabulary
alone does not qualify reliability. A performance task without measurements
does not qualify performance. Route by evidence, not task topic, tool name,
test presence, failure presence, rotation, or novelty.

Return only the selected Lens or silence. Do not give advice or explain the
route.

{"status":"finding","lens":"simplicity"}

or

{"status":"no_finding","lens":"none"}
"""


def build_router_prompt() -> str:
    return AUTOMATIC_ROUTING_PROMPT.strip() + "\n"


def delivery_text(finding: str) -> str:
    return f"{NUDGE_LABEL}\n{str(finding or '').strip()}"


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    route: lens_router.NudgeRoute,
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""
    if route.lens not in lens_router.LENS_PERSONAS or not route.persona:
        logger("generator requires one selected lens")
        return ""
    try:
        overlay = (persona_dir / f"{route.persona}.txt").read_text(
            encoding="utf-8"
        ).strip()
    except Exception as exc:
        logger(f"lens prompt read failed ({route.lens}): {exc}")
        return ""
    return (
        f"{base_prompt}\n\n"
        f"# LENS CONTEXT: {route.lens}\n\n{overlay}\n\n"
        f"# SELECTED LENS\n\nUse only `{route.lens}` and return it as `lens` "
        "when there is a finding.\n"
    )


def build_nudge_input(source_packet: str) -> str:
    return str(source_packet or "")
