---
name: recent-nudges
description: Read recent Masters' Nudge audit records only when the user explicitly asks what Nudges were returned or wants recent Nudge history for auditing.
---

# Show recent Masters' Nudge records

Starting from this `SKILL.md`, walk upward to the plugin root containing
`masters_nudge_cli.py`. Use the configured Python executable on Claude Code or the current Python 3.10+
interpreter on Codex. Run the internal JSON command from the plugin root:

```text
masters_nudge_cli.py recent-nudges --limit <count>
```

Use 10 when the user does not provide a count. Do not paste raw JSON. Present
each returned record in plain language with its time and returned text. Render
an `intervene` record as: current choice, structural cost, direction, and
evidence. For a legacy record containing `relationship` or `finding`, present
that stored text without inventing missing fields. If there are no records, say
so directly. Explain diagnostics without dumping the JSON.

Call these audit records "returned to the Host," not "read," "adopted," or
"injected." A record proves that the Hook returned a Nudge to Claude Code or
Codex. It cannot prove that the main model read it, accepted it, or changed its
decision because of it. Session data older than 30 days is removed when a new
task starts.
