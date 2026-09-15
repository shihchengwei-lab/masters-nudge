# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **Catch a patch-like structural direction while it is still cheap to change.**

Masters’ Nudge gives a Claude Code or Codex agent one independent, read-only
structural intervention before its next decision. The Provider may identify a
better responsibility boundary or existing seam, but the main model still owns
implementation and verification.

## See an actual run

![One actual run from passing tests through the main model's next decision](docs/assets/actual-nudge-run.png)

This is not a UI mockup. It records one real CLI run. The code already worked
and both tests passed, but `web_total` and `invoice_total` each owned the same
discount formula.

The Hook gave the code and test result to the Provider. The Provider returned
a Nudge favoring one owner for the formula. The main model judged that advice
reasonable, extracted `discounted_total`, and ran the same tests again.

The screenshot omits only startup warnings, timestamps, and repeated output.
The Nudge, main-model decision, diff, and test results come from the same run.
It is one observed reaction, not a promise that every main model will follow a
Nudge.

## One early judgment

Only a tool-result batch whose native top-level input contains an explicit
mutation shape is sent to the Provider: `patch`, `diff`, a path plus
`old_string` and `new_string`, or a path plus `content`. Read-only exploration,
status checks, and standalone verification, failure, or measurement results do
not call it. Mutation batches may trigger a fresh workspace judgment until one
intervention is delivered for the task. The main agent remains responsible for
deciding whether and how to use that intervention.

Codex supplies its native `apply_patch` input as a top-level `command`. Masters'
Nudge accepts that Host-specific shape only when the tool name is exactly
`apply_patch` and `command` contains a complete patch envelope with an add,
update, or delete operation; another tool or arbitrary command text remains
ineligible.

At task start, Masters' Nudge records the bounded Git workspace state. After an
explicit mutation, it sends the task contract, task-start workspace, current
cumulative workspace, and bounded contents of explicitly changed files. It
does not send the Actor's explanation of its approach as evidence.

The OpenAI Provider runs with read-only filesystem access in the Actor's
workspace, so it can verify an existing abstraction, owner, caller, data path,
or control-flow path instead of relying on Host-selected source windows. Other
Providers receive the same bounded snapshot. The Host recognizes only changed
paths; it does not assign ownership, lifecycle, or data-flow meaning.

The Provider returns either `pass` or `intervene`. An intervention names the
current choice, its structural cost, a direction the Actor can evaluate, and
concrete repository evidence. The direction may be opinionated, but it cannot
contain a patch, replacement code, or step-by-step edit. Once one intervention
has been delivered for a task, later mutation batches remain silent. A new task
resets that boundary.

## How it works

```text
Task contract + task-start workspace
                 ↓
          Actor mutation
                 ↓
 Current cumulative workspace + changed files
                 ↓
 Read-only Provider ── pass (silent)
                 └──── intervene (advisory direction)
                              ↓
                 Actor owns implementation
```

`pass` means only that the current snapshot yielded no important, grounded
intervention. It does not prove the task complete or the design optimal.

Claude Code provides the intended `PostToolBatch` control point: all tool
results from one model step are available before the next step. The Codex
integration requires a `PostToolBatch`-capable Codex build; a stock build that
only exposes `PostToolUse` will not run this hook. The local Codex implementation
and upstream request are documented in
[the proposed `PostToolBatch` issue](docs/codex-post-tool-batch-issue-draft.md).

Provider errors and the fixed 90-second timeout fail open: the Nudge attempt
ends and the main agent continues.

## Privacy

### What leaves your computer

The selected Provider receives a bounded snapshot that may include:

- the current task or recovered long-running Goal;
- the bounded Git status and diff at task start;
- the current bounded Git status and cumulative diff;
- bounded current contents of files explicitly changed by the mutation.

The Provider does not receive the complete conversation, hidden model
reasoning, or Actor-authored explanation as evidence. The OpenAI Provider can
inspect files inside the workspace with read-only tools; it cannot modify them.

Anthropic and OpenAI are cloud Providers, so the packet leaves your computer
and is also subject to that Provider's data policy. Choose local Ollama when
the packet must stay on your machine. Ollama is restricted to a loopback
address, uses an already installed model, and never falls back to a cloud
Provider.

## Local records

Masters’ Nudge stores the current task state and a small audit record under
`~/.masters-nudge/data/`. An audit entry records when a Nudge was returned to
the Host and what it said.

This proves only that the Hook returned the Nudge to Claude Code or Codex. It
does not prove that the main model read, accepted, or acted because of it.

When a new task starts, session data not updated for more than 30 days is
deleted. The Provider preference lives separately in
`~/.masters-nudge/config.json` and remains until changed. A legacy `lens` field
is ignored and removed the next time Provider settings are saved.

## Providers

- Anthropic
- OpenAI
- local Ollama

Each Nudge uses exactly one selected Provider. There is no silent fallback.

## Installation

Requirements:

- a plugin-capable Claude Code or Codex CLI installation;
- Python 3.10+;
- an authenticated CLI for Anthropic or OpenAI, or a running Ollama server
  with the selected model already installed.

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

If `python` is not Python 3.10+, set `python_command` to `python3` or the
absolute path of a suitable Python executable. Do not add command arguments.

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Open a new task after installation. In Codex, open `/hooks`, inspect the plugin
commands, and approve them.

### Update or remove

```bash
# Claude Code
claude plugin marketplace update masters-nudge
claude plugin update masters-nudge@masters-nudge
claude plugin uninstall masters-nudge@masters-nudge

# Codex
codex plugin marketplace upgrade masters-nudge
codex plugin add masters-nudge@masters-nudge
codex plugin remove masters-nudge@masters-nudge
```

Restart the Host after an update. Uninstalling does not delete existing local
data.

## Use it through your agent

Hooks run automatically. For manual actions, ask the agent in ordinary
language:

- **“Check whether Masters’ Nudge is ready.”** Checks Python, Provider access,
  data storage, and Host Hooks without generating a Nudge.
- **“Switch the Masters’ Nudge Provider.”** Shows Anthropic, OpenAI, and local
  Ollama. Ollama setup verifies the selected installed model and loopback
  server.
- **“Show recent Masters’ Nudge records.”** Explains recent audit entries in
  plain language.

The Skills call an internal JSON command-line interface and translate the
result. Users do not need to edit environment variables, remember exact names,
or interpret raw JSON.

## Development

Repository source is canonical. The checked-in plugin package is generated
from that source.

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

License: [MIT](LICENSE)
