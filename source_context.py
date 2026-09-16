"""Build the complete input for one post-mutation Nudge decision."""

from __future__ import annotations

from collections.abc import Sequence

from masters_nudge.contracts import ToolCompleted


OBSERVATION_MAX_CHARS = 32_000


class ObservationTooLargeError(ValueError):
    """The exact task and change cannot fit without hiding evidence."""


def build_observation(task: str, events: Sequence[ToolCompleted]) -> str:
    """Return exactly the task and completed mutations, without reconstruction."""
    clean_task = str(task or "").strip()
    changes = [
        event.mutation.change.strip()
        for event in events
        if event.mutation is not None and event.mutation.change.strip()
    ]
    if not clean_task or not changes:
        raise ValueError("task and completed change are required")
    change = "\n\n".join(changes)
    observation = (
        f"[task]\n{clean_task}\n[end task]\n\n"
        f"[change]\n{change}\n[end change]"
    )
    if len(observation) > OBSERVATION_MAX_CHARS:
        raise ObservationTooLargeError(
            f"task plus completed change exceeds {OBSERVATION_MAX_CHARS} characters"
        )
    return observation
