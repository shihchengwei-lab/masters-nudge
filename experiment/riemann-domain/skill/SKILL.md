---
name: riemann
description: Configure, inspect, change, or reset the experimental Riemann-research profile for the current Codex workspace.
---

# Riemann Research Profile

Resolve the plugin root as two directories above this `SKILL.md`. Use the current
workspace root, never a different repository inferred from conversation text.

When the user asks to enable the Riemann research profile, run:

```text
python "${PLUGIN_ROOT}/masters_nudge_cli.py" profile configure --workspace "<workspace-root>" --domain riemann --stage explore --provider anthropic --model claude-opus-4-6 --review-mode stop_only --json
```

Use the current Python interpreter (`python3`, `python`, or `py -3`). Do not edit
global environment variables. Explain that the setting is scoped to this
workspace, uses Claude Opus 4.6 as an external reviewer, runs only at Stop by
default, and takes effect in the next Codex task.

If the user names a lifecycle stage, pass exactly one of `frame`, `explore`,
`attack`, or `prove`. Use `profile show --workspace "<workspace-root>" --json`
to inspect it and `profile reset --workspace "<workspace-root>" --json` only
when explicitly asked to return this workspace to the software profile.

This is an experimental research-operation lens, not a claim that the model can
prove the Riemann hypothesis and not a reproduction of Anthropic's unpublished
research setup. Never weaken proof standards or describe numerical evidence as
a proof.
