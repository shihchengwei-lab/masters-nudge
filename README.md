# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **Passing tests provides evidence for exercised behavior; check the task contract before design taste.**

Masters’ Nudge gives a Claude Code or Codex agent one short, evidence-based
contract warning or engineering-taste nudge before its next decision. It does
not solve the task or stop the agent; the main model still owns the remedy and
verification.

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

Only a tool-result batch whose native top-level input contains an explicit
mutation shape is sent to the Provider: `patch`, `diff`, a path plus
`old_string` and `new_string`, or a path plus `content`. Read-only exploration,
status checks, and standalone verification, failure, or measurement results do
not call it. Each mutation batch is judged independently; Masters' Nudge does
not infer success from result text or pair a later result with an earlier
change. The main agent remains responsible for deciding whether and how to use
each Nudge.

Codex supplies its native `apply_patch` input as a top-level `command`. Masters'
Nudge accepts that Host-specific shape only when the tool name is exactly
`apply_patch` and `command` contains a complete patch envelope with an add,
update, or delete operation; another tool or arbitrary command text remains
ineligible.

Each selected batch is sent once. The Provider sees the task beginning and
bounded decision evidence in a clean context. A change record preserves the
concrete mutation input and observable result supplied by the Host; it does not
infer source relationships from matching identifier text. When the mutation
explicitly names a file inside the workspace, the same record also includes
bounded current source windows around its changed lines; it neither discovers
related files nor keeps source history. The Provider checks the visible task
contract first. Only when that stage yields no eligible warning does it inspect
the structural tradeoff most likely to change the next engineering decision.
Up to three returned texts
already returned in the same session are sent separately as exclusions so the
Provider does not repeat or continue them; they are not evidence or a record of
the main agent's decision path.

In one judgment, the Provider checks the task contract first and then evaluates
engineering taste with three structural principles:

- make invalid states unrepresentable in the data structure;
- preserve a unidirectional causal flow from events to state;
- keep effects and dependencies explicit enough for local reasoning.

The two stages and three principles form one judgment contract; they are not an
extra Provider call, three Lenses, or three separate outputs. When visible
evidence establishes a contract gap, the Provider returns `contract_warning`
and stops before taste. Only a pass with no eligible warning can produce
`taste_nudge`. A taste nudge states only a responsibility overlap directly
visible in the current packet: two concrete implementation elements carry the
same state, behavior, effect, or control-flow responsibility. The Actor owns
the remedy.

Each principle has a one-word label: `validity` for invalid states,
`causality` for unidirectional causal flow, and `predictability` for explicit,
locally understandable behavior. The Provider returns the visible
`evidence_seq` that grounds the finding, the principle, the smallest atomic
`anchor` needed to locate the observation, and one short `relationship` that
states the contract break or visible responsibility overlap. Missing context
does not become a contract warning or taste nudge. A relationship with only one
visible element, or one that depends on a distant caller, cross-file owner, or
lifecycle, remains silent. The Host renders
`contract_warning` as `causality warning:` and `taste_nudge` as
`causality nudge:`. A warning means the visible contract remains open; it does
not make the Hook block the main model.

A taste nudge neither asks a question nor directs a change, and it does not
package missing facts as conditions. The Actor still owns the remedy. Routine
verification status and task restatements are outside the role.

## How it works

```text
Task and observable tool results
              ↓
 Contract coverage (first stage)
     ├─ contract_warning
     └─ no eligible warning
                 ↓
 Engineering taste (second stage)
     ├─ taste_nudge
     └─ no_finding
                 ↓
      The agent's next context
```

Each output is generated for the current situation; it is not a random stock
sentence. A contract warning states a visible break. A taste nudge states a
visible responsibility overlap, not a review, score, complete solution, or
demand to run more tests. No contract warning means only
that the current packet yielded no eligible warning; it does not prove the whole
task contract complete.

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
- bounded contents of local task files explicitly referenced by that task;
- every ordered tool call and result in the current batch, with each record
  length-limited;
- up to three Nudge texts already returned in the same session, marked only as
  deduplication exclusions.

The Provider does not receive the complete conversation or hidden model
reasoning. It does not receive tool results from earlier batches. Masters'
Nudge does not scan the workspace or read files outside the workspace; a local
file is included only when its relative path is explicitly named by the task.

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
