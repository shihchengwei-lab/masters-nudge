#!/usr/bin/env python3
"""Rebuild the shipped Rook sheet from hatch-pet component-extracted frames."""

import argparse
from pathlib import Path

from PIL import Image


FRAME_SIZE = (192, 208)
FRAME_COUNT = 6
STATES = ("idle", "review")


def build(frames_root: Path, output: Path) -> None:
    sheet = Image.new(
        "RGBA", (FRAME_SIZE[0] * FRAME_COUNT, FRAME_SIZE[1] * len(STATES))
    )
    for row, state in enumerate(STATES):
        for column in range(FRAME_COUNT):
            frame = Image.open(frames_root / state / f"{column:02d}.png").convert(
                "RGBA"
            )
            if frame.size != FRAME_SIZE:
                raise ValueError(f"unexpected {state} frame size: {frame.size}")
            sheet.alpha_composite(frame, (column * FRAME_SIZE[0], row * FRAME_SIZE[1]))
    sheet.save(output, "WEBP", lossless=True, method=6)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "spritesheet.webp",
    )
    args = parser.parse_args()
    build(args.frames_root, args.output)


if __name__ == "__main__":
    main()
