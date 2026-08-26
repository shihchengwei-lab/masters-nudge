#!/usr/bin/env python3
"""Select one private review lens from explicit work-focus state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import persona_config


@dataclass(frozen=True)
class ReviewRoute:
    stage: str
    effective_lens: str
    source: str


def resolve_review_route(
    base_dir: Path,
    *,
    environ: Mapping[str, str] | None = None,
    reported_focus: str = "",
    stopping: bool = False,
) -> ReviewRoute:
    """Honor an explicit user override, then the main model's progress report."""
    selection = persona_config.resolve_stage(base_dir, environ=environ)
    if (
        selection.source in {"environment", "config"}
        and selection.persona in persona_config.PERSONA_NAMES
    ):
        return ReviewRoute(selection.stage, selection.persona, selection.source)

    focus = str(reported_focus or "").strip().lower()
    lens = persona_config.FOCUS_LENSES.get(focus, "")
    if lens:
        return ReviewRoute(focus, lens, "main_model_report")

    if stopping:
        return ReviewRoute("review", "linus", "stop_fallback")
    return ReviewRoute("build", "beck", "default_fallback")
