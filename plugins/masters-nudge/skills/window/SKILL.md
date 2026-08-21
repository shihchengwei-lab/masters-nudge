---
name: window
description: Open or troubleshoot the optional Masters' Nudge floating window only when the user explicitly asks for the window or UI.
---

# Masters' Nudge window

Resolve the plugin root as two directories above this `SKILL.md`. Do not change
the working directory. Capture the active workspace, then run the absolute
`masters_nudge_cli.py` path with the current Python interpreter as
`masters_nudge_cli.py window --workspace "<active-workspace>" --json`.
Report missing Pillow or Tkinter dependencies exactly as returned. Do not
install packages without the user's request.
