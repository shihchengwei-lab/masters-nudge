#!/usr/bin/env python3
"""Resolve an automatic route or one explicit user-selected lens."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import persona_config


@dataclass(frozen=True)
class ReviewRoute:
    stage: str
    lens: str
    source: str


def resolve_review_route(
    base_dir: Path,
    *,
    environ: Mapping[str, str] | None = None,
) -> ReviewRoute:
    """Honor an explicit override; automatic mode leaves lens choice open."""
    selection = persona_config.resolve_stage(base_dir, environ=environ)
    if (
        selection.source in {"environment", "config"}
        and selection.persona in persona_config.PERSONA_NAMES
    ):
        return ReviewRoute(selection.stage, selection.persona, selection.source)
    return ReviewRoute(
        persona_config.AUTOMATIC_STAGE,
        "",
        selection.source,
    )
