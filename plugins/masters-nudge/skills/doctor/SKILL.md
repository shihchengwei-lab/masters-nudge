---
name: doctor
description: Diagnose a Masters' Nudge installation only when the user explicitly asks to check setup, readiness, hooks, or missing dependencies.
---

# Masters' Nudge Doctor

Find the plugin root above this file containing masters_nudge_cli.py. With the current Python 3.10+ interpreter run:

```text
python masters_nudge_cli.py doctor --host codex
```

Explain the JSON in plain language. Report missing runtime files, Codex Provider login, and enabled plugin separately.
Do not call a Provider just to diagnose setup. This diagnostic does not prove PostToolBatch is supported or feedback was
delivered; those need a complete runtime test. The first version supports only Codex with OpenAI.
