# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **Passing tests settles behavior, not design.**

Masters’ Nudge gives a Claude Code or Codex agent one short, evidence-grounded
engineering perspective before its next decision. It does not solve the task or
stop the agent. It surfaces a relationship the main model may be underweighting.

## See the Lenses separate

![One same-packet smoke through no Lens context and all three Lenses](docs/assets/lens-discrimination-smoke.svg)

This is not a UI mockup. It records four live Provider calls using the same
bounded packet and model. The packet exposed an uncertain retry, a required
return shape, and a measured serialization cost. Only the Lens context changed;
the ablation control omitted it.

The control noticed split ownership. Simplicity separated replay identity from
the response cache, Reliability asked who owns completion state, and Performance
challenged whether the single-call measurement covered the main batch cost.

The text shown is the complete Nudge from one call per condition. This smoke
checks whether the prompts can separate attention; it does not establish
accuracy, repeatability, or an effect on the main model.

## Three Lenses

| Lens | What it notices |
|---|---|
| Simplicity | Unnecessary complexity and the wrong owner for a responsibility |
| Reliability | What must remain true through reordering, retries, and partial failure |
| Performance | Measured work on the real execution path that can be removed |

Choose one Lens and keep it until you change it. Simplicity is the default;
there is no automatic Router. The selected Lens makes one Provider call when a
checkpoint is admitted, and the Provider returns `no_finding` when the packet
does not support a useful Nudge.

The expert names inside the Lens prompts are attention cues. They do not give a
provider another person's ability or make the Nudge more accurate by itself.

## How it works

```text
Task and current workspace
Nearby source seen by the agent
Current triggering checkpoint
              ↓
       One selected Lens
              ↓
   One short Nudge, or silence
              ↓
    The agent's next context
```

Each Nudge is one concise Traditional Chinese perspective within 52 characters.
It names an engineering point and its consequence under the selected direction
of taste, while leaving the tradeoff and implementation to the agent. It is
generated for the current situation, not selected from stock text. It is not a
review, score, question, or complete solution.

Claude Code and the supported Codex build provide the intended `PostToolBatch`
control point: all tool results from one model step are available before the
next step. Codex builds without this event are not supported by this version.
Codex does not currently expose a read-only Hook capability query, so plugin
installation alone cannot verify this event. The Doctor therefore reports Codex
precision as unverified; establish exactness separately with an isolated smoke
run.

Changes are recorded for the next check. After a change has been observed in
the turn, a `PostToolBatch` containing a validation, failure, or measurement may
synchronously start one Nudge flow. Each turn has at most one candidate
opportunity for a non-failing check and one failure opportunity, in either
order. Each admitted checkpoint consumes its opportunity and makes one Provider
call with a 90-second limit, including when the result is `no_finding`. A slower
Provider directly adds to the agent's wait; on an error or timeout, the Nudge
attempt ends and the main agent continues.

The Provider packet uses the current workspace as current state and includes
only the triggering batch as checkpoint evidence. Older tool results remain in
local audit state instead of being replayed to the Provider. Source excerpts
previously shown to the agent are additional, non-authoritative context. They
are selected from bounded, flattened Hook output and may omit a decisive
caller or contract; Masters' Nudge does not claim to reconstruct a complete
repository review.

## Privacy

### What leaves your computer

The selected Provider receives a bounded packet that may include:

- the current task or recovered long-running Goal;
- content from local files explicitly named by the task, read once when the
  task begins;
- excerpts from current uncommitted changes to Git-tracked files, which may
  include files outside the current task;
- partial content from up to three untracked files that Git does not ignore;
- selected excerpts from source-navigation results already shown to the agent;
- validations, failures, and measurements from the batch that triggered the
  current call;
- the current batch's change only when no authoritative Git workspace snapshot
  is available;
- previous Nudges used to avoid repeating the same tradeoff;
- length-limited commands and results attached to those selected excerpts and
  the current checkpoint.

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
- **“Switch the Masters’ Nudge Lens.”** Shows Simplicity, Reliability, and
  Performance in plain language, then confirms the saved choice.
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
