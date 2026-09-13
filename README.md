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

## One judgment

Normally, only a tool-result batch containing a successful code change is sent
to the Provider. Read-only exploration, status checks, and standalone
verification, failure, or measurement results do not call it. After a Nudge is
returned, later change batches are held and only the latest change is retained
until the main agent produces a verification, failure, or measurement result.
That first result is combined with the retained change and sent as one Provider
judgment, then the hold is cleared. A result without a post-Nudge change does
not call the Provider or clear the hold. This keeps the implementation decision
and its observed result together without turning intermediate edits into
separate problems. The main agent remains responsible for deciding whether and
how to use each Nudge.

Each selected batch is sent once. The Provider sees the task beginning and
bounded decision evidence in a clean context. Each change record can include up
to 16 source-link records (4,000 characters total) for direct calls and
multi-hop owners in the concrete mutation. Each link independently resolves to
a definition or occurrence in the changed text files, or is marked unresolved;
an omitted count makes the fixed reference limit explicit. This does not depend
on which source command ran most recently. The Provider forms its own causal
judgment, then selects the strongest non-obvious observation that could change
the next engineering decision. Up to three Nudge texts already returned in the
same session are sent separately as exclusions so the Provider does not repeat
or continue them; they are not evidence or a record of the main agent's decision
path.

The Provider evaluates three structural principles in one pass without routing
the problem through a category first:

- make invalid states unrepresentable in the data structure;
- preserve a unidirectional causal flow from events to state;
- keep effects and dependencies explicit enough for local reasoning.

The three principles form one judgment contract; they are not three Lenses,
three model calls, or three separate Nudges.

Each principle has a one-word label: `validity` for invalid states,
`causality` for unidirectional causal flow, and `predictability` for explicit,
locally understandable behavior. The Provider returns the principle, the
smallest atomic `anchor` needed to locate the observation, and one short
`relationship` that states a single engineering edge. The Host then renders the
fixed `warning` attention marker, for example `causality warning:`. The marker
carries no classification or severity meaning.

A Nudge may reveal the abstraction or responsibility the implementation is
choosing, predict behavior beyond the immediate example, or show a simpler data
or control-flow shape. Routine verification status and task restatements are
outside the role.

## How it works

```text
Task and observable tool results
              ↓
      One Provider judgment
              ↓
   One short Nudge, or silence
              ↓
    The agent's next context
```

Each Nudge is generated for the current situation; it is not a random stock
sentence. It is an independent second opinion, not a review, score, question,
complete solution, or demand to run more tests.

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

The selected Provider receives a bounded packet that may include:

- the current task or recovered long-running Goal;
- content from local files explicitly named by the task, read once when the
  task begins;
- up to 16 source-link records (4,000 characters total) that resolve direct
  calls and multi-hop owners to definitions or occurrences in the changed text
  files, with unresolved references and the omitted count shown explicitly;
- every ordered tool call and result in the current batch, with each record
  length-limited;
- the final bounded working diff when the batch changed files;
- up to three Nudge texts already returned in the same session, marked only as
  deduplication exclusions.

The Provider does not receive the complete conversation or hidden model
reasoning. It does not receive tool results from earlier batches. Resolved
related-source links can include parts of a changed file that the main agent did
not explicitly read in a tool call.

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
