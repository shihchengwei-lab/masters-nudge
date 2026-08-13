---
name: setup-local
description: Configure Masters' Nudge to use a user-selected local Ollama model only when the user explicitly asks for local or private model setup.
---

# Set up the local reviewer

Resolve the plugin root as two directories above this `SKILL.md`. Obtain the
exact Ollama model name from the user; do not choose or recommend a model.
Do not install Ollama, pull a model, sign in, or enable network access.

Explain that Ollama must already be running with cloud features disabled via
`OLLAMA_NO_CLOUD=1` or `disable_ollama_cloud`, and that the selected model must
already be available locally. Then run:

`masters_nudge_cli.py local configure --model <exact-model> --json`

Use the configured Python executable on Claude Code and the current Python
3.10+ interpreter on Codex. Add `--url <url>` only when the user supplied a
different loopback endpoint. Never substitute a non-loopback URL.

If configuration succeeds, run `masters_nudge_cli.py doctor --host <host>
--json`. Report interface readiness without claiming that the selected model
has adequate quality. If setup fails, preserve the previous reviewer setting
and explain the diagnostic; never fall back to or configure a cloud provider.

Only run `masters_nudge_cli.py local reset --json` when the user explicitly
asks to stop using the persistent local reviewer. Warn that reset restores the
host's normal cloud reviewer default unless environment variables override it.
