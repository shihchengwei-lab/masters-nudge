# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **One independent observation after a change, before the agent thinks again.**

Masters’ Nudge gives a Claude Code or Codex agent one optional observation
about a change it just made. The Provider sees only the task and the completed
change. The main agent remains responsible for choosing, implementing, and
verifying the solution.

## Contract

Only a completed tool batch with an explicit mutation can trigger the Provider:
`patch`, `diff`, a path with `old_string` and `new_string`, or a path with
`content`. Codex's native `apply_patch` `command` is accepted only when it
contains a complete patch envelope.

The input is exactly:

```text
user task + completed change
```

The result is exactly one of:

```json
{"nudge":null}
```

```json
{"nudge":{"message":"<one concrete relationship>","evidence":["<material present in the task or change>"]}}
```

The Provider cannot inspect the Actor's workspace. It receives no task-start
snapshot, cumulative diff, current file contents, Actor explanation, or tool
for reading the repository. If the exact task and change exceed the input
limit, the attempt ends instead of sending partial evidence.

One returned Nudge is added to the Host context after the mutation batch and
before the Actor's next inference. It is not a patch, instruction, dialogue, or
final review. The Actor may reconsider the whole solution and retains all
implementation authority. Later mutation batches in the same task remain
silent after one Nudge is delivered.

## Timing

```text
Task → Actor mutation → optional Provider Nudge → Actor's next inference
```

Claude Code provides the intended `PostToolBatch` control point. Codex requires
a `PostToolBatch`-capable build; a stock build exposing only `PostToolUse` does
not run this hook. The local Codex implementation and upstream request are
documented in
[the proposed `PostToolBatch` issue](docs/codex-post-tool-batch-issue-draft.md).

Provider errors and the fixed timeout fail open: the main agent continues
without a Nudge.

## Privacy

Anthropic and OpenAI receive the task and completed change, so those contents
leave the computer and are subject to the Provider's data policy. Local Ollama
keeps them on the machine; Masters’ Nudge restricts Ollama to a loopback
address and never silently falls back to a cloud Provider.

Local task state and returned-Nudge audit records are stored under
`~/.masters-nudge/data/`. A record proves only that the Host returned the
Nudge, not that the Actor accepted or followed it.

## Providers

- Anthropic
- OpenAI
- local Ollama

Each attempt uses exactly one selected Provider.

## Installation

Requirements:

- a plugin-capable Claude Code or Codex CLI installation;
- Python 3.10+;
- an authenticated Anthropic or OpenAI CLI, or a running Ollama server with
  the selected model installed.

### Claude Code

```powershell
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

### Codex

```powershell
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Open a new task after installation. In Codex, open `/hooks`, inspect the plugin
commands, and approve them.

## Use it through your agent

Hooks run automatically. Manual skills can check readiness, change the
Provider, or show recent Nudge records. Users do not need to edit environment
variables or interpret raw JSON.

## Development

Repository source is canonical. The checked-in plugin package is generated
from that source.

```powershell
python -m unittest discover -s tests -v
python tools\build_plugin.py --check
```

License: [MIT](LICENSE)
