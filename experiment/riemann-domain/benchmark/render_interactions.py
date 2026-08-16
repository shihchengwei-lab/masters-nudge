#!/usr/bin/env python3
"""Render the manually coded interaction JSON as a human-readable Markdown page."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LABELS = {
    "direction_aligned": "Direction aligned",
    "engaged_reframed": "Engaged and reframed",
    "delayed": "Delayed adoption",
    "ambiguous_in_flight": "Ambiguous: related work already in flight",
    "not_adopted_or_late": "Not adopted or too late",
}


def render() -> str:
    payload = json.loads(
        (ROOT / "interaction_annotations.json").read_text(encoding="utf-8")
    )
    lines = [
        "# Complete traceable Nudge interactions",
        "",
        "> **Scope:** These are the 17 interactions with both a confirmed injection",
        "> receipt and a matching transcript message. They are the traceable subset",
        "> of 19 findings generated after receipt tracking began, and of 102 findings",
        "> across the full experiment. Temporal alignment does not establish exclusive",
        "> causation or mathematical correctness.",
        "",
        "Return to the [benchmark report](README.md). The machine-readable source is",
        "[`interaction_annotations.json`](interaction_annotations.json).",
        "",
        "## Coding rubric",
        "",
    ]
    for key, description in payload["rubric"].items():
        lines.append(f"- **{LABELS[key]}:** {description}")

    lines.extend(["", "## Chronological observations", ""])
    for item in payload["annotations"]:
        label = LABELS[item["classification"]]
        lines.extend(
            [
                f"### {item['id']}. {label}",
                "",
                f"- **Time:** `{item['ts']}`",
                f"- **Lens:** `{item['lens']}`",
                f"- **Nudge:** {item['nudge']}",
                f"- **Next visible response:** {item['next_response']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    output = ROOT / "interactions.md"
    output.write_text(render(), encoding="utf-8")
    print(f"rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
