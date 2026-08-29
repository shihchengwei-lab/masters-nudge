---
name: select-provider
description: Show or change the Masters' Nudge Provider only when the user explicitly asks to view, choose, switch, reset, or configure a Provider or local Ollama model.
---

# Select a Masters' Nudge Provider

Starting from this `SKILL.md`, walk upward to the plugin root containing
`masters_nudge_cli.py`. Use the configured Python executable on Claude Code or the current Python 3.10+
interpreter on Codex. Run these internal JSON commands from the plugin root:

```text
masters_nudge_cli.py provider get --host <claude|codex>
masters_nudge_cli.py provider list
```

Do not show raw JSON. Tell the user which Provider and model are active, then
show the returned choices in plain language:

- Anthropic: sends the bounded Nudge packet to the Anthropic CLI;
- OpenAI: sends the bounded Nudge packet to the OpenAI CLI;
- local Ollama: keeps the packet on this computer through a loopback server.

The user may choose by name, number, or description; do not require exact
spelling. Explain that cloud Providers receive the task packet, including
length-limited commands and results. Do not change anything until the user has
selected a Provider.

For Anthropic or OpenAI, run the matching command. Add `--model <model>` only
when the user supplied a model name:

```text
masters_nudge_cli.py provider set <anthropic|openai> [--model <model>]
```

For Ollama, obtain the exact already-installed model name. Do not install
Ollama, pull a model, or choose a model for the user. Use the default loopback
address unless the user supplied another loopback address, then run:

```text
masters_nudge_cli.py provider set ollama --model <exact-model> [--url <loopback-url>]
```

Never pass a non-loopback Ollama URL. The command must validate the local
server and model before replacing the previous setting. Do not silently fall
back to a cloud Provider.

After a successful write, run `masters_nudge_cli.py provider get --host <claude|codex>` again.
Confirm the Provider, model, and local endpoint when applicable in plain
language. If saving or read-back fails, say the setting was not confirmed and
explain the diagnostic without dumping JSON.

Only run `masters_nudge_cli.py provider reset` when the user explicitly asks
to restore the current Host's default. Read back and confirm the resulting
selection.
