---
name: doctor
description: Diagnose a Masters' Nudge installation only when the user explicitly asks to check setup, readiness, hooks, or missing dependencies.
---

# Masters' Nudge Doctor

Resolve the plugin root as two directories above this `SKILL.md`. On Claude
Code, run `masters_nudge_cli.py doctor --host claude
--hook-python-command "${user_config.python_command}" --json` from that root
using the configured Python executable. On Codex, run
`masters_nudge_cli.py doctor --host codex --json` with the current Python
interpreter (`python3`, `python`, or `py -3`).

Report core readiness separately from the optional floating-window status.
Do not invoke either reviewer model as part of diagnosis. If Codex is the host,
remind the user that plugin hooks still need review in `/hooks`.
