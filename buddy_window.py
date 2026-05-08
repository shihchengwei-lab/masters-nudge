#!/usr/bin/env python3
"""Buddy_similar — floating window that tails the active session's buddy log.

Single-file Tk app, stdlib only. Polls ~/.claude/buddy/ every second, tracks
the most-recently-modified <session_id>.log file, and shows new JSONL entries
as they appear. Pinned to bottom-right corner, always on top. When a different
session becomes active (its log gets newer mtime), the window resets and
follows that one — old session's entries don't leak into the view.

Run:
    python buddy_window.py
    pythonw buddy_window.py     # Windows, no console
    bash start_buddy_window.bat # Windows convenience launcher

Env:
    BUDDY_CLAUDE_DIR   override location of .claude (default ~/.claude)
"""

import json
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
BUDDY_DIR = CLAUDE_DIR / "buddy"

POLL_INTERVAL_MS = 1000
MAX_ENTRIES = 40
WINDOW_WIDTH = 460
WINDOW_HEIGHT = 480

BG = "#1e1e1e"
HEADER_BG = "#252525"
TS_FG = "#7a7a7a"
BODY_FG = "#e0e0e0"
NEW_FG = "#9be09b"
SEP_FG = "#3a3a3a"


class BuddyWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Buddy")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - WINDOW_WIDTH - 20
        y = sh - WINDOW_HEIGHT - 80
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.root.minsize(320, 240)

        # State
        self.current_log: Path | None = None
        self.last_offset = 0
        self.entries_shown = 0
        self._initial_load_done = False

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Frame(self.root, bg=HEADER_BG, height=32)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header, text="Buddy", bg=HEADER_BG, fg=BODY_FG,
            font=("Microsoft JhengHei", 11, "bold"),
        )
        title.pack(side="left", padx=12, pady=6)

        self.session_label = tk.Label(
            header, text="—", bg=HEADER_BG, fg=TS_FG,
            font=("Microsoft JhengHei", 8),
        )
        self.session_label.pack(side="left", padx=4, pady=6)

        self.status_label = tk.Label(
            header, text="—", bg=HEADER_BG, fg=TS_FG,
            font=("Microsoft JhengHei", 8),
        )
        self.status_label.pack(side="right", padx=12, pady=6)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        self.text = tk.Text(
            body, bg=BG, fg=BODY_FG,
            font=("Microsoft JhengHei", 11),
            wrap="word", borderwidth=0, padx=14, pady=10,
            state="disabled", spacing1=2, spacing3=4,
        )
        scrollbar = ttk.Scrollbar(body, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.tag_configure("ts", foreground=TS_FG, font=("Microsoft JhengHei", 8))
        self.text.tag_configure("body", foreground=BODY_FG,
                                font=("Microsoft JhengHei", 11), spacing3=8)
        self.text.tag_configure("new", foreground=NEW_FG,
                                font=("Microsoft JhengHei", 11), spacing3=8)
        self.text.tag_configure("sep", foreground=SEP_FG, font=("Microsoft JhengHei", 8))

    def refresh(self):
        try:
            self._poll()
        except Exception as e:
            self._set_status(f"err: {type(e).__name__}")
        self.root.after(POLL_INTERVAL_MS, self.refresh)

    def _set_status(self, txt):
        self.status_label.config(text=txt)

    def _set_session(self, session_id: str):
        if session_id:
            self.session_label.config(text=session_id[:8])
        else:
            self.session_label.config(text="—")

    def _find_active_log(self) -> Path | None:
        """Return the most-recently-modified *.log under BUDDY_DIR, or None."""
        if not BUDDY_DIR.exists():
            return None
        candidates = list(BUDDY_DIR.glob("*.log"))
        if not candidates:
            return None
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    def _reset_display(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")
        self.last_offset = 0
        self.entries_shown = 0
        self._initial_load_done = False

    def _poll(self):
        active = self._find_active_log()
        if active is None:
            self._set_status("waiting for log")
            self._set_session("")
            return

        # Switch target if the active session log changed
        if self.current_log != active:
            self.current_log = active
            self._reset_display()
            session_id = active.stem
            self._set_session(session_id)

        try:
            with active.open("rb") as f:
                f.seek(self.last_offset)
                chunk = f.read()
                self.last_offset = f.tell()
        except Exception as e:
            self._set_status(f"read err: {type(e).__name__}")
            return

        if not chunk:
            self._set_status(
                f"{datetime.now().strftime('%H:%M:%S')} • {self.entries_shown} entries"
            )
            return

        text_data = chunk.decode("utf-8", errors="replace")
        new_entries = []
        for line in text_data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                new_entries.append(json.loads(line))
            except Exception:
                continue

        if not new_entries:
            return

        self.text.config(state="normal")
        for obj in new_entries:
            ts = obj.get("ts", "")
            reaction = (obj.get("reaction") or "").strip()
            model = obj.get("model", "")

            header_line = f"{ts}  ·  {model}\n"
            body_tag = "body" if not self._initial_load_done else "new"

            self.text.insert("end", header_line, "ts")
            self.text.insert("end", reaction + "\n", body_tag)
            self.text.insert("end", "─" * 50 + "\n", "sep")
            self.entries_shown += 1

        if self.entries_shown > MAX_ENTRIES:
            excess = self.entries_shown - MAX_ENTRIES
            self.text.delete("1.0", f"{excess * 3 + 1}.0")
            self.entries_shown = MAX_ENTRIES

        self.text.see("end")
        self.text.config(state="disabled")
        self._initial_load_done = True
        self._set_status(
            f"{datetime.now().strftime('%H:%M:%S')} • {self.entries_shown} entries"
        )


def main():
    if not CLAUDE_DIR.exists():
        sys.stderr.write(f"claude dir not found: {CLAUDE_DIR}\n")
        sys.exit(1)

    root = tk.Tk()
    BuddyWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
