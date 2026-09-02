---
name: select-lens
description: Show or change the Masters' Nudge Lens only when the user explicitly asks to view, choose, switch, or reset the Lens.
---

# Select a Masters' Nudge Lens

Starting from this `SKILL.md`, walk upward to the plugin root containing
`masters_nudge_cli.py`. Use the configured Python executable on Claude Code or the current Python 3.10+
interpreter on Codex. Run these internal JSON commands from the plugin root:

```text
masters_nudge_cli.py lens get
masters_nudge_cli.py lens list
```

Do not show raw JSON. Tell the user which Lens is active, then present the
returned choices in plain language. The expected choices are:

- Simplicity: notice unnecessary complexity and misplaced responsibility;
- Reliability: notice reordering, retries, and partial failure;
- Performance: notice measured work on the real execution path.

The user may choose by name, number, or description; do not require exact
spelling. Do not change the saved setting until the user has selected one. Run:

```text
masters_nudge_cli.py lens set <simplicity|reliability|performance>
```

After a successful write, run `masters_nudge_cli.py lens get` again. Confirm
the value read back in plain language. If saving or read-back fails, say the
setting was not confirmed and explain the returned diagnostic without dumping
the JSON.
