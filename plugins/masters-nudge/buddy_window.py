#!/usr/bin/env python3
"""Masters' Nudge — floating Rook companion window with speech bubble.

Displays an animated raven companion beside the latest nudge.
Tails the active host-namespaced log.

Requires: Pillow (pip install Pillow)

Run:
    python buddy_window.py
    pythonw buddy_window.py     # Windows, no console
Env:
    MASTERS_NUDGE_DATA_DIR    override local data directory
    MASTERS_NUDGE_SPRITE_PATH override spritesheet path (default: spritesheet.webp
                        next to this script). Point at any spritesheet you
                        prefer — the auto-frame detector handles arbitrary
                        transparent-background sheets.
"""

import json
import math
import os
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

import persona_config
from masters_nudge import storage
from masters_nudge.contracts import find_git_root
from masters_nudge.runtime import RuntimeSettings

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow required: pip install Pillow", file=sys.stderr)
    sys.exit(1)

_RUNTIME = RuntimeSettings.from_env(Path(__file__).resolve().parent)
DATA_DIR = _RUNTIME.paths.data_dir
CUSTOM_SPRITE_PATH = os.environ.get("MASTERS_NUDGE_SPRITE_PATH")
SPRITESHEET_PATH = Path(
    CUSTOM_SPRITE_PATH
    or Path(__file__).resolve().parent / "spritesheet.webp"
)

POLL_MS = 1000
ANIM_MS = 250           # 4 fps sprite animation
SPRITE_HEIGHT = 90      # display height in pixels
WINDOW_WIDTH = 460
WINDOW_MIN_HEIGHT = 180
WINDOW_MAX_HEIGHT = 290
BUBBLE_WRAP_LENGTH = 300
APPROX_CHARS_PER_LINE = 16
TEXT_LINE_HEIGHT = 22
WINDOW_NON_TEXT_HEIGHT = 136

# Colors
BG = "#1a1a2e"
BUBBLE_BG = "#252545"
BUBBLE_FG = "#e0e0e0"
BUBBLE_BORDER = "#4a4a6a"
TS_FG = "#6a6a8a"

LENS_BADGES = {
    "jeff": (persona_config.persona_label("jeff"), "#56CFE1"),
    "linus": (persona_config.persona_label("linus"), "#FF6B6B"),
    "fowler": (persona_config.persona_label("fowler"), "#C77DFF"),
    "beck": (persona_config.persona_label("beck"), "#80ED99"),
    "lamport": (persona_config.persona_label("lamport"), "#72A1FF"),
    "carmack": (persona_config.persona_label("carmack"), "#FFB86C"),
    "evaluation": ("Shadow evaluation", "#FFD166"),
}
UNKNOWN_LENS_BADGE = ("未記錄", "#A0A0B8")

LENS_BACKGROUNDS = {
    "jeff": "#17343B",
    "linus": "#3A2228",
    "fowler": "#30233D",
    "beck": "#1D3528",
    "lamport": "#222B4A",
    "carmack": "#3A2E1D",
    "evaluation": "#3A321D",
}


def lens_badge(persona: str | None) -> tuple[str, str]:
    """Return a color-plus-work badge, falling back for old or unknown logs."""
    key = persona.strip().lower() if isinstance(persona, str) else ""
    name, color = LENS_BADGES.get(key, UNKNOWN_LENS_BADGE)
    return f"● {name}", color


def selector_options() -> list[str]:
    return [
        persona_config.AUTOMATIC_LABEL,
        *(spec.label for spec in persona_config.STAGE_SPECS.values()),
    ]


SELECTOR_STAGES = {
    persona_config.AUTOMATIC_LABEL: persona_config.AUTOMATIC_STAGE,
    **{
        spec.label: key
        for key, spec in persona_config.STAGE_SPECS.items()
    },
}


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
        components = []
        in_f = False
        xs = 0
        for x in range(w):
            if col_has[x] and not in_f:
                xs = x
                in_f = True
            elif not col_has[x] and in_f:
                components.append((xs, x))
                in_f = False
        if in_f:
            components.append((xs, w))

        # A pet can have detached feet or a gap between beak and body. Merge
        # small internal gaps while preserving the larger gap between cells.
        merged = []
        for start, end in components:
            previous_width = merged[-1][1] - merged[-1][0] if merged else 0
            current_width = end - start
            joins_pet_part = min(previous_width, current_width) < 40
            if merged and joins_pet_part and start - merged[-1][1] <= 40:
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        frames = [(start, ys, end, ye) for start, end in merged]
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


def lens_background(persona: str | None) -> str:
    """Return a restrained outer-window color for the effective lens."""
    key = persona.strip().lower() if isinstance(persona, str) else ""
    return LENS_BACKGROUNDS.get(key, BG)


def reaction_log_workspace(path: Path) -> str:
    """Return the workspace declared by a reaction log's newest valid entry."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except (TypeError, ValueError):
            continue
        if isinstance(entry, dict):
            workspace = normalize_workspace(str(entry.get("workspace") or ""))
            if workspace:
                return workspace
    return ""


def normalize_workspace(workspace: str | Path) -> str:
    raw = str(workspace or "").strip()
    if not raw:
        return ""
    try:
        resolved = str(Path(raw).expanduser().resolve())
    except OSError:
        resolved = str(Path(raw).expanduser().absolute())
    return os.path.normcase(resolved)


def resolve_window_workspace(
    *,
    environ: dict[str, str] | None = None,
    cwd: str | Path | None = None,
) -> str:
    """Resolve the caller's explicit workspace before falling back to process cwd."""
    environment = os.environ if environ is None else environ
    raw = str(
        environment.get("MASTERS_NUDGE_WORKSPACE")
        or cwd
        or Path.cwd()
    )
    normalized = normalize_workspace(raw)
    return normalize_workspace(find_git_root(normalized) or normalized)


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
        self.last_reaction_ts = ""
        self._reported_error_kinds: set[tuple[str, str]] = set()
        self.workspace = resolve_window_workspace()
        self.stage_selection = persona_config.resolve_stage(DATA_DIR)

        # Load sprite
        self.idle_frames: list[ImageTk.PhotoImage] = []
        self.review_frames: list[ImageTk.PhotoImage] = []
        self.review_frames_remaining = 0
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
        except Exception as exc:
            self._report_error("window-sprite", exc)
            return

        rows = detect_frames(img)
        if not rows:
            return

        candidates = []
        scored = []
        for i, row in enumerate(rows):
            if len(row) < 3:
                continue
            widths = [b[2] - b[0] for b in row]
            consistency = 1.0 - (max(widths) - min(widths)) / max(max(widths), 1)
            if consistency >= 0.65:
                candidates.append(i)
            scored.append((consistency, len(row), i))

        if CUSTOM_SPRITE_PATH is None and len(candidates) >= 2:
            idle_row_idx, review_row_idx = candidates[:2]
        elif CUSTOM_SPRITE_PATH is None and len(candidates) == 1:
            idle_row_idx = review_row_idx = candidates[0]
        elif scored:
            scored.sort(reverse=True)
            idle_row_idx = scored[0][2]
            review_row_idx = scored[1][2] if len(scored) >= 2 else idle_row_idx
        else:
            return

        idle_pil = cut_and_scale(img, rows[idle_row_idx], SPRITE_HEIGHT)
        review_pil = cut_and_scale(img, rows[review_row_idx], SPRITE_HEIGHT)

        self.idle_frames = [ImageTk.PhotoImage(frame) for frame in idle_pil]
        self.review_frames = [ImageTk.PhotoImage(frame) for frame in review_pil]

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
        self.right_panel = tk.Frame(self.root, bg=BG)
        self.right_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        bubble = tk.Frame(
            self.right_panel, bg=BUBBLE_BG,
            highlightbackground=BUBBLE_BORDER, highlightthickness=1,
        )
        bubble.pack(fill="both", expand=True)

        active_persona = self.stage_selection.persona
        if active_persona not in LENS_BADGES:
            active_persona = ""
        badge_text, badge_color = lens_badge(active_persona)
        self.lens_label = tk.Label(
            bubble, text=badge_text, bg=BUBBLE_BG, fg=badge_color,
            font=("Microsoft JhengHei", 9, "bold"),
            anchor="w", padx=10, pady=2,
        )
        self.lens_label.pack(fill="x", pady=(4, 0))

        selected_label = persona_config.stage_label(self.stage_selection.stage)
        self.stage_var = tk.StringVar(value=selected_label)
        selector_state = (
            "disabled"
            if self.stage_selection.source == "environment"
            else "readonly"
        )
        self.stage_selector = ttk.Combobox(
            bubble,
            textvariable=self.stage_var,
            values=selector_options(),
            state=selector_state,
            width=34,
            font=("Microsoft JhengHei", 9),
        )
        self.stage_selector.pack(fill="x", padx=10, pady=(2, 2))
        self.stage_selector.bind("<<ComboboxSelected>>", self._on_stage_selected)

        initial_text = "( . . . )"
        if self.stage_selection.source == "environment":
            initial_text = (
                f"MASTERS_NUDGE_STAGE 正在接管：{selected_label}。"
            )

        self.bubble_label = tk.Label(
            bubble, text=initial_text, bg=BUBBLE_BG, fg=BUBBLE_FG,
            font=("Microsoft JhengHei", 11),
            wraplength=BUBBLE_WRAP_LENGTH, justify="left",
            anchor="nw", padx=10, pady=6,
        )
        self.bubble_label.pack(fill="both", expand=True)

        self.ts_label = tk.Label(
            self.right_panel, text="", bg=BG, fg=TS_FG,
            font=("Microsoft JhengHei", 8), anchor="e",
        )
        self.ts_label.pack(fill="x")
        self._set_lens_background(active_persona)

    def _set_lens_background(self, persona: str | None):
        color = lens_background(persona)
        self.root.configure(bg=color)
        self.sprite_canvas.configure(bg=color)
        self.right_panel.configure(bg=color)
        self.ts_label.configure(bg=color)

    def _set_lens_badge(self, persona: str | None):
        text, color = lens_badge(persona)
        self.lens_label.config(text=text, fg=color)
        self._set_lens_background(persona)

    def _on_stage_selected(self, _event=None):
        label = self.stage_var.get()
        stage = SELECTOR_STAGES.get(label)
        if stage is None:
            return
        try:
            persona_config.save_stage(DATA_DIR, stage)
        except (OSError, ValueError):
            self.bubble_label.config(text="階段設定無法儲存，仍使用原設定。")
            return
        persona = (
            persona_config.STAGE_SPECS[stage].persona
            if stage in persona_config.STAGE_SPECS
            else ""
        )
        self._set_lens_badge(persona)
        if stage == persona_config.AUTOMATIC_STAGE:
            message = (
                "下一次 review 起，由 reviewer 依目前決策壓力選一種 Lens；"
                "Hook 仍決定何時呼叫 Provider。"
            )
        else:
            message = f"下一次 review 起固定使用 {label}。"
        message += "若設有 MASTERS_NUDGE_STAGE，仍以環境變數為準。"
        self.bubble_label.config(text=message)
        self._resize_for_reaction(message)

    # ── Animation ─────────────────────────────────────────

    def _animate(self):
        reviewing = self.review_frames_remaining > 0 and self.review_frames
        frames = self.review_frames if reviewing else self.idle_frames
        if frames:
            self.frame_idx = (self.frame_idx + 1) % len(frames)
            tk_img = frames[self.frame_idx]
            self.sprite_canvas.delete("all")
            self.sprite_canvas.create_image(50, SPRITE_HEIGHT // 2 + 5, image=tk_img)
            if reviewing:
                self.review_frames_remaining -= 1
        self.root.after(ANIM_MS, self._animate)

    # ── Log polling ───────────────────────────────────────

    def _report_error(self, component: str, exc: Exception) -> None:
        """Record each failure class once while keeping the UI loop alive."""
        key = (component, type(exc).__name__)
        reported = getattr(self, "_reported_error_kinds", set())
        if key in reported:
            return
        reported.add(key)
        self._reported_error_kinds = reported
        storage.append_error(
            _RUNTIME.paths.error_log,
            component,
            f"{type(exc).__name__}: {exc}",
        )

    def _poll(self):
        try:
            active = self._find_active_log()
            if active and active != self.current_log:
                self.current_log = active
                # A new session log is often created with its first reaction
                # already written. Read it from the start instead of skipping
                # the very finding that caused this log to become active.
                self.last_offset = 0

            if self.current_log:
                self._read_new()
        except Exception as exc:
            self._report_error("window-poll", exc)
        self.root.after(POLL_MS, self._poll)

    def _find_active_log(self) -> Path | None:
        logs = (
            [
                path
                for path in DATA_DIR.glob("*.log")
                if path.name != "error.log"
                and reaction_log_workspace(path) == self.workspace
            ]
            if DATA_DIR.exists()
            else []
        )
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
        except Exception as exc:
            self._report_error("window-read", exc)
            return

        if not chunk:
            return

        for line in chunk.decode("utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("kind") == "delivery_receipt":
                    if str(entry.get("reaction_ts") or "") == self.last_reaction_ts:
                        status = str(entry.get("delivery_status") or "")
                        labels = {
                            "emitted": "已送出，待確認",
                            "injected": "已注入",
                            "expired": "已過期（未注入）",
                            "superseded": "已被新狀態取代",
                            "failed": "送出失敗",
                        }
                        ts = str(entry.get("delivered_at") or entry.get("ts") or "")
                        short_ts = ts[11:19] if len(ts) > 19 else ts
                        self.ts_label.config(
                            text=f"{short_ts} · {labels.get(status, status)}"
                        )
                    continue
                reaction = (entry.get("reaction") or "").strip()
                ts = entry.get("ts", "")
                persona = entry.get("effective_lens") or entry.get("persona", "")
                if reaction:
                    self.last_reaction_ts = str(ts or "")
                    self._set_lens_badge(persona)
                    self.frame_idx = -1
                    self.review_frames_remaining = len(self.review_frames)
                    self.bubble_label.config(text=reaction)
                    self._resize_for_reaction(reaction)
                    if ts:
                        short_ts = ts[11:19] if len(ts) > 19 else ts
                        delivery = str(entry.get("delivery_status") or "")
                        suffix = (
                            " · 待送出"
                            if delivery == "queued"
                            and entry.get("kind", "review") != "review_status"
                            else ""
                        )
                        self.ts_label.config(text=f"{short_ts}{suffix}")
            except Exception as exc:
                self._report_error("window-entry", exc)
                continue


def main():
    root = tk.Tk()
    BuddyWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
