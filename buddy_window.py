#!/usr/bin/env python3
"""Masters' Nudge — floating checkpoint-bell window with speech bubble.

Displays an animated engineering checkpoint bell beside the latest nudge.
Tails the active session's legacy-compatible buddy log.

Requires: Pillow (pip install Pillow)

Run:
    python buddy_window.py
    pythonw buddy_window.py     # Windows, no console
    start_buddy_window.bat      # Windows convenience launcher

Env:
    BUDDY_CLAUDE_DIR    override location of .claude (default ~/.claude)
    BUDDY_SPRITE_PATH   override spritesheet path (default: spritesheet.webp
                        next to this script). Point at any spritesheet you
                        prefer — the auto-frame detector handles arbitrary
                        transparent-background sheets.
"""

import json
import math
import os
import sys
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow required: pip install Pillow", file=sys.stderr)
    sys.exit(1)

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
BUDDY_DIR = CLAUDE_DIR / "buddy"
SPRITESHEET_PATH = Path(os.environ.get(
    "BUDDY_SPRITE_PATH",
    Path(__file__).resolve().parent / "spritesheet.webp",
))

POLL_MS = 1000
ANIM_MS = 250           # 4 fps sprite animation
SPRITE_HEIGHT = 90      # display height in pixels
WINDOW_WIDTH = 460
WINDOW_MIN_HEIGHT = 150
WINDOW_MAX_HEIGHT = 220
BUBBLE_WRAP_LENGTH = 300
APPROX_CHARS_PER_LINE = 16
TEXT_LINE_HEIGHT = 22
WINDOW_NON_TEXT_HEIGHT = 84

# Colors
BG = "#1a1a2e"
BUBBLE_BG = "#252545"
BUBBLE_FG = "#e0e0e0"
BUBBLE_BORDER = "#4a4a6a"
TS_FG = "#6a6a8a"


def window_height_for_reaction(reaction: str) -> int:
    """Estimate enough window height for a bounded nudge without clipping."""
    lines = reaction.splitlines() or [""]
    wrapped_lines = sum(
        max(1, math.ceil(len(line) / APPROX_CHARS_PER_LINE)) for line in lines
    )
    estimated = WINDOW_NON_TEXT_HEIGHT + wrapped_lines * TEXT_LINE_HEIGHT
    return min(WINDOW_MAX_HEIGHT, max(WINDOW_MIN_HEIGHT, estimated))


def detect_frames(img: Image.Image) -> list[list[tuple[int, int, int, int]]]:
    """Auto-detect sprite frames from a transparent-background spritesheet.

    Returns a list of rows, each row a list of (x0, y0, x1, y1) bounding boxes.
    """
    w, h = img.size
    alpha = img.split()[3]
    px = alpha.load()

    # Find row bands (contiguous horizontal strips with content)
    row_has = [any(px[x, y] > 10 for x in range(0, w, 3)) for y in range(h)]
    bands = []
    in_band = False
    start = 0
    for y in range(h):
        if row_has[y] and not in_band:
            start = y
            in_band = True
        elif not row_has[y] and in_band:
            bands.append((start, y))
            in_band = False
    if in_band:
        bands.append((start, h))

    # For each band, find individual frame columns
    rows = []
    for ys, ye in bands:
        col_has = [any(px[x, y] > 10 for y in range(ys, ye, 2)) for x in range(w)]
        frames = []
        in_f = False
        xs = 0
        for x in range(w):
            if col_has[x] and not in_f:
                xs = x
                in_f = True
            elif not col_has[x] and in_f:
                frames.append((xs, ys, x, ye))
                in_f = False
        if in_f:
            frames.append((xs, ys, w, ye))
        if frames:
            rows.append(frames)
    return rows


def cut_and_scale(img: Image.Image, bboxes: list[tuple], target_h: int) -> list[Image.Image]:
    """Crop frames from spritesheet and scale to target height."""
    result = []
    for bbox in bboxes:
        frame = img.crop(bbox)
        fw, fh = frame.size
        scale = target_h / fh
        new_w = max(1, int(fw * scale))
        frame = frame.resize((new_w, target_h), Image.NEAREST)
        result.append(frame)
    return result


class BuddyWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Masters’ Nudge")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Position: bottom-right
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        win_w, win_h = WINDOW_WIDTH, WINDOW_MIN_HEIGHT
        self.window_height = win_h
        x = sw - win_w - 24
        y = sh - win_h - 80
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # Drag support
        self._drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)

        # State
        self.current_log: Path | None = None
        self.last_offset = 0
        self.last_reaction = ""

        # Load sprite
        self.idle_frames: list[ImageTk.PhotoImage] = []
        self.walk_frames: list[ImageTk.PhotoImage] = []
        self.frame_idx = 0
        self._load_sprites()

        self._build_ui()
        self._animate()
        self._poll()

    # ── Drag ──────────────────────────────────────────────

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _resize_for_reaction(self, reaction: str):
        """Grow upward so a longer nudge keeps the window's bottom position."""
        new_height = window_height_for_reaction(reaction)
        if new_height == self.window_height:
            return
        self.root.update_idletasks()
        x = self.root.winfo_x()
        bottom = self.root.winfo_y() + self.root.winfo_height()
        y = max(0, bottom - new_height)
        self.root.geometry(f"{WINDOW_WIDTH}x{new_height}+{x}+{y}")
        self.window_height = new_height

    # ── Sprites ───────────────────────────────────────────

    def _load_sprites(self):
        if not SPRITESHEET_PATH.exists():
            return
        try:
            img = Image.open(SPRITESHEET_PATH).convert("RGBA")
        except Exception:
            return

        rows = detect_frames(img)
        if not rows:
            return

        # Pick animation rows:
        # - Idle: row with ~6 consistent-width frames (prefer middle rows)
        # - Walk: another row with ~6 frames
        scored = []
        for i, row in enumerate(rows):
            if len(row) < 3:
                continue
            widths = [b[2] - b[0] for b in row]
            consistency = 1.0 - (max(widths) - min(widths)) / max(max(widths), 1)
            scored.append((consistency, len(row), i))
        scored.sort(reverse=True)

        if len(scored) >= 2:
            idle_row_idx = scored[0][2]
            walk_row_idx = scored[1][2]
        elif len(scored) == 1:
            idle_row_idx = walk_row_idx = scored[0][2]
        else:
            return

        idle_pil = cut_and_scale(img, rows[idle_row_idx], SPRITE_HEIGHT)
        walk_pil = cut_and_scale(img, rows[walk_row_idx], SPRITE_HEIGHT)

        self.idle_frames = [ImageTk.PhotoImage(f) for f in idle_pil]
        self.walk_frames = [ImageTk.PhotoImage(f) for f in walk_pil]

    # ── UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Sprite (left)
        sprite_w = 100
        self.sprite_canvas = tk.Canvas(
            self.root, width=sprite_w, height=SPRITE_HEIGHT + 10,
            bg=BG, highlightthickness=0,
        )
        self.sprite_canvas.pack(side="left", padx=(10, 0), pady=10)

        # Bubble (right)
        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        bubble = tk.Frame(
            right, bg=BUBBLE_BG,
            highlightbackground=BUBBLE_BORDER, highlightthickness=1,
        )
        bubble.pack(fill="both", expand=True)

        self.bubble_label = tk.Label(
            bubble, text="( . . . )", bg=BUBBLE_BG, fg=BUBBLE_FG,
            font=("Microsoft JhengHei", 11),
            wraplength=BUBBLE_WRAP_LENGTH, justify="left",
            anchor="nw", padx=10, pady=8,
        )
        self.bubble_label.pack(fill="both", expand=True)

        self.ts_label = tk.Label(
            right, text="", bg=BG, fg=TS_FG,
            font=("Microsoft JhengHei", 8), anchor="e",
        )
        self.ts_label.pack(fill="x")

    # ── Animation ─────────────────────────────────────────

    def _animate(self):
        frames = self.idle_frames or self.walk_frames
        if frames:
            self.frame_idx = (self.frame_idx + 1) % len(frames)
            tk_img = frames[self.frame_idx]
            self.sprite_canvas.delete("all")
            self.sprite_canvas.create_image(50, SPRITE_HEIGHT // 2 + 5, image=tk_img)
        self.root.after(ANIM_MS, self._animate)

    # ── Log polling ───────────────────────────────────────

    def _poll(self):
        try:
            active = self._find_active_log()
            if active and active != self.current_log:
                self.current_log = active
                # Jump to end so we only show NEW reactions
                try:
                    self.last_offset = active.stat().st_size
                except Exception:
                    self.last_offset = 0

            if self.current_log:
                self._read_new()
        except Exception:
            pass
        self.root.after(POLL_MS, self._poll)

    def _find_active_log(self) -> Path | None:
        if not BUDDY_DIR.exists():
            return None
        logs = list(BUDDY_DIR.glob("*.log"))
        if not logs:
            return None
        logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return logs[0]

    def _read_new(self):
        try:
            with self.current_log.open("rb") as f:
                f.seek(self.last_offset)
                chunk = f.read()
                self.last_offset = f.tell()
        except Exception:
            return

        if not chunk:
            return

        for line in chunk.decode("utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                reaction = (entry.get("reaction") or "").strip()
                ts = entry.get("ts", "")
                if reaction:
                    self.last_reaction = reaction
                    self.bubble_label.config(text=reaction)
                    self._resize_for_reaction(reaction)
                    if ts:
                        short_ts = ts[11:19] if len(ts) > 19 else ts
                        self.ts_label.config(text=short_ts)
            except Exception:
                continue


def main():
    root = tk.Tk()
    BuddyWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
