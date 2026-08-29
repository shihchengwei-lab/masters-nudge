#!/usr/bin/env python3
"""Map one public Lens to its private attention cue."""

from __future__ import annotations

from dataclasses import dataclass

from masters_nudge.lenses import LENSES


AUTOMATIC_LENS = "automatic"
LENS_PERSONAS = {
    lens: spec.persona for lens, spec in LENSES.items() if spec.persona
}


@dataclass(frozen=True)
class NudgeRoute:
    lens: str = ""
    persona: str = ""


def resolve_nudge_route(selected_lens: str) -> NudgeRoute:
    """Automatic mode leaves selection to the Provider router."""
    lens = str(selected_lens or AUTOMATIC_LENS).strip().lower()
    persona = LENS_PERSONAS.get(lens, "")
    return NudgeRoute(lens if persona else "", persona)
