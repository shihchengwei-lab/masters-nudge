---
name: doctor
description: Diagnose a Masters' Nudge installation only when the user explicitly asks to check setup, readiness, hooks, or missing dependencies.
---

# Masters' Nudge Doctor

Starting from this `SKILL.md`, walk upward to the plugin root containing
`masters_nudge_cli.py`. Run the internal CLI from that root. On Claude Code, use the configured Python
executable and run:

```text
masters_nudge_cli.py doctor --host claude --hook-python-command <configured-python>
```

On Codex, use the current Python 3.10+ interpreter and run:

```text
masters_nudge_cli.py doctor --host codex
```

The command returns JSON for the Agent, not user-facing prose. Explain the
result in plain language and do not paste raw JSON unless the user explicitly
asks for it. Separate these checks:

- Python and packaged runtime files;
- ability to write local data;
- selected Provider and its availability;
- Host Hook registration and control-point precision.

Do not call a Nudge Provider merely to diagnose readiness. For local Ollama,
report the loopback endpoint, server availability, selected installed model,
and any diagnostic separately. Availability does not prove model quality. For
Codex, report plugin registration separately from control-point verification.
The CLI does not expose a read-only Hook capability query, so Doctor reports
`PostToolBatch` precision as unverified. Establish exactness separately with an
isolated smoke run. Remind the user to inspect and approve plugin commands in
`/hooks` when needed.
