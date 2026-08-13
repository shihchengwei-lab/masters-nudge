---
name: migrate
description: Migrate legacy Masters' Nudge hook entries only when the user explicitly asks to migrate or remove the old manual installation.
---

# Migrate legacy hooks

Resolve the plugin root as two directories above this `SKILL.md`. First run
`masters_nudge_cli.py migrate --json` with the current Python interpreter.

Explain the exact matches and any modified near-matches. Run again with
`--apply --json` only after the user explicitly confirms the migration. The
tool backs up each changed settings file and never removes local review data or
legacy runtime files.
