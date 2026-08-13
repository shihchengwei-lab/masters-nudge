#!/usr/bin/env python3
"""Render selected real reviewer outputs in six actual BuddyWindow instances."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tkinter as tk  # noqa: E402
from PIL import ImageGrab  # noqa: E402

import buddy_window  # noqa: E402


ORDER = ("jeff", "beck", "fowler", "linus", "lamport", "carmack")
BACKDROP = "#0D1020"
HERO_WIDTH = 1580
HERO_HEIGHT = 650
HERO_X = 170
HERO_Y = 45


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--hero", type=Path, required=True)
    parser.add_argument("--screenshots-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.selection.read_text(encoding="utf-8"))
    selected = {row["lens"]: row for row in payload["selections"]}
    if set(selected) != set(ORDER) or any(not selected[lens]["finding"] for lens in ORDER):
        raise SystemExit("selection must contain one non-empty finding for each lens")
    args.hero.parent.mkdir(parents=True, exist_ok=True)
    args.screenshots_dir.mkdir(parents=True, exist_ok=True)

    previous_persona = os.environ.get("BUDDY_PERSONA")
    with tempfile.TemporaryDirectory(prefix="masters-nudge-tk-capture-") as raw_temp:
        log_dir = Path(raw_temp) / "buddy"
        log_dir.mkdir()
        buddy_window.BUDDY_DIR = log_dir
        buddy_window.POLL_MS = 600_000

        backdrop = tk.Tk()
        backdrop.title("Masters’ Nudge — six-lens capture")
        backdrop.overrideredirect(True)
        backdrop.configure(bg=BACKDROP)
        backdrop.geometry(f"{HERO_WIDTH}x{HERO_HEIGHT}+{HERO_X}+{HERO_Y}")
        backdrop.attributes("-topmost", True)
        heading = tk.Label(
            backdrop,
            text="Masters’ Nudge",
            bg=BACKDROP,
            fg="#F2F4FF",
            font=("Segoe UI", 25, "bold"),
        )
        heading.place(x=34, y=22)
        subheading = tk.Label(
            backdrop,
            text="同一個 checkpoint，六種工作流視角  ·  Same evidence, same model, only the lens changes",
            bg=BACKDROP,
            fg="#AEB6D9",
            font=("Microsoft JhengHei", 12),
        )
        subheading.place(x=36, y=70)

        windows: list[tuple[str, tk.Toplevel, buddy_window.BuddyWindow]] = []
        for index, lens in enumerate(ORDER):
            os.environ["BUDDY_PERSONA"] = lens
            top = tk.Toplevel(backdrop)
            view = buddy_window.BuddyWindow(top)
            top.attributes("-topmost", True)
            entry = {
                "ts": datetime(2026, 8, 13, 21, 0, index).isoformat(),
                "session_id": "six-lens-hero",
                "kind": "review",
                "provider": "openai",
                "model": "gpt-5.6-sol",
                "persona": lens,
                "reaction": selected[lens]["finding"],
            }
            log_path = log_dir / f"{index:02d}-{lens}.log"
            log_path.write_text(json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8")
            view.current_log = log_path
            view.last_offset = 0
            view._read_new()
            top.update_idletasks()
            col = index % 3
            row = index // 3
            x = HERO_X + 35 + col * 510
            y = HERO_Y + 115 + row * 255
            top.geometry(f"{buddy_window.WINDOW_WIDTH}x{view.window_height}+{x}+{y}")
            windows.append((lens, top, view))

        if previous_persona is None:
            os.environ.pop("BUDDY_PERSONA", None)
        else:
            os.environ["BUDDY_PERSONA"] = previous_persona

        def capture() -> None:
            backdrop.update_idletasks()
            for _, top, _ in windows:
                top.lift()
                top.update_idletasks()
            for lens, top, _ in windows:
                x = top.winfo_rootx()
                y = top.winfo_rooty()
                image = ImageGrab.grab(
                    bbox=(x, y, x + top.winfo_width(), y + top.winfo_height()),
                    all_screens=True,
                )
                image.save(args.screenshots_dir / f"{lens}.png")
            hero = ImageGrab.grab(
                bbox=(HERO_X, HERO_Y, HERO_X + HERO_WIDTH, HERO_Y + HERO_HEIGHT),
                all_screens=True,
            )
            hero.save(args.hero)
            backdrop.after(250, backdrop.destroy)

        backdrop.after(1500, capture)
        backdrop.mainloop()

    print(args.hero)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
