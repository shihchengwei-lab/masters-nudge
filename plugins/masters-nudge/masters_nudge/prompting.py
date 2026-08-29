"""Host-neutral prompt assembly and delivery formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import lens_router
import persona_config


MAX_REACTION_CHARS = 52
INDEPENDENT_OPINION_LABEL = "獨立第二意見："

AUTOMATIC_ROUTING_PROMPT = """# AUTOMATIC LENS ROUTER

Use only the supplied task anchor and observable evidence. Select exactly one
Lens only when its minimum evidence is present:

- linus: a current-task mechanism or ownership path contains a wrapper,
  adapter, fallback, compatibility path, workaround, duplicate owner, or
  accumulating patch whose necessity can be judged from the packet.
- lamport: the packet states an invariant, at least two reorderable events,
  and a concrete retry, interruption, redelivery, or partial-success path.
- carmack: profiler, benchmark, or trace numbers locate actual cost on a
  concrete execution path.

An abstraction alone does not qualify linus. Async or network vocabulary alone
does not qualify lamport. A performance task without measurements does not
qualify carmack. Route by evidence, not lifecycle stage, task topic, tool name,
test presence, failure presence, persona rotation, or novelty.

Return only the selected Lens or silence. Do not give advice, explain the
route, identify a blind spot, or produce a Nudge.

{"status":"finding","effective_lens":"linus"}

or

{"status":"no_finding","effective_lens":"none"}
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
    log_error: Callable[[str], None] | None = None,
) -> str:
    """Compose the base contract with exactly one selected Lens."""
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""

    selected_lens = str(route.lens or "").strip().lower()
    if selected_lens not in persona_config.LENS_PERSONAS:
        logger("generator requires one selected lens")
        return ""
    persona_file = persona_dir / f"{selected_lens}.txt"
    try:
        overlay = persona_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"persona prompt read failed ({selected_lens}): {exc}")
        return ""

    return (
        f"{base_prompt}\n\n"
        f"# LENS CONTEXT: {selected_lens}\n\n{overlay}\n\n"
        f"# SELECTED LENS\n\nUse only `{selected_lens}` and return it as "
        "`effective_lens` when there is a finding.\n"
    )


def build_review_input(source_packet: str) -> str:
    """Pass the bounded packet through without hidden context or exclusions."""
    return str(source_packet or "")
