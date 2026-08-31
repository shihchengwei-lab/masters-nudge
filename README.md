# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **Passing tests settles behavior, not design.**

Masters’ Nudge gives a Claude Code or Codex agent one short, evidence-based
engineering preference before its next decision. It does not solve the task or
stop the agent. It points at a tradeoff the main model may otherwise overlook.

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

## Three Lenses

| Lens | What it notices |
|---|---|
| Simplicity | Unnecessary complexity and the wrong owner for a responsibility |
| Reliability | What must remain true through reordering, retries, and partial failure |
| Performance | Measured work on the real execution path that can be removed |

Automatic mode asks the Provider to choose a Lens from the available evidence.
You can also ask the agent to show the Lens choices and pin one. In either mode,
the Provider is instructed to return `no_finding` when the evidence does not
support a useful Nudge.

The expert names inside the Lens prompts are attention cues. They do not give a
provider another person's ability or make the Nudge more accurate by itself.

## How it works

```text
Task and observable tool results
              ↓
       One qualified Lens
              ↓
   One short Nudge, or silence
              ↓
    The agent's next context
```

Each Nudge is one direct Traditional Chinese engineering preference within 52
characters, placed in the agent's next context. It is generated for the current
situation, not selected from stock text. It is not a review, score, question,
or complete solution, and the Provider does not take over the task.

Claude Code and the supported Codex build provide the intended `PostToolBatch`
control point: all tool results from one model step are available before the
next step. Codex builds without this event are not supported by this version.

One `PostToolBatch` checkpoint containing an eligible change, validation,
failure, or measurement synchronously starts one Nudge flow. A pinned Lens
makes at most one Provider call. Automatic mode makes at most two calls that
share 90 seconds. A slower Provider directly adds to the agent's wait; on an
error or timeout, the Nudge attempt ends and the main agent continues.

## Privacy

### What leaves your computer

The selected Provider receives a bounded packet that may include:

- the current task or recovered long-running Goal;
- content from local files explicitly named by the task, read once when the
  task begins;
- excerpts from current uncommitted changes to Git-tracked files, which may
  include files outside the current task;
- partial content from up to three untracked files that Git does not ignore;
- recent failures, validations, and measurements;
- the length-limited command that was run and its result.

The Provider does not receive the complete conversation or hidden model
reasoning, and the system does not automatically send a complete copy of the
repository.

Anthropic and OpenAI are cloud Providers, so the packet leaves your computer
and is also subject to that Provider's data policy. Choose local Ollama when
the packet must stay on your machine. Ollama is restricted to a loopback
address, uses an already installed model, and never falls back to a cloud
Provider.

## Local records

Masters’ Nudge stores the current task state and a small audit record under
`~/.masters-nudge/data/`. An audit entry records when a Nudge was returned to
the Host, which Lens produced it, and what it said.

This proves only that the Hook returned the Nudge to Claude Code or Codex. It
does not prove that the main model read, accepted, or acted because of it.

When a new task starts, session data not updated for more than 30 days is
deleted. Provider and Lens preferences live separately in
`~/.masters-nudge/config.json` and are kept until you change them.

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
- **“Switch the Masters’ Nudge Lens.”** Shows Automatic, Simplicity,
  Reliability, and Performance in plain language, then confirms the saved
  choice.
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
