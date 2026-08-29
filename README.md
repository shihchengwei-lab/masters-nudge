# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> **Passing tests settles behavior, not design.**

Masters’ Nudge adds one evidence-grounded engineering preference before a
Claude Code or Codex agent’s next decision.

---

## Actual run

![One actual run from passing tests through the main model's next decision](docs/assets/actual-nudge-run.png)

We started with code that already worked: 2 tests passed. But the same discount
calculation appeared in two places. Nothing was broken yet, so an agent could
easily stop there. If someone changed only one copy later, however, the two
places could charge different prices.

The Nudge pointed out the simpler choice: keep the calculation in one place.
The main model removed the duplicate copy and made checkout use the existing
pricing function. The same 2 tests passed again after the change.

The image combines the unedited Nudge, the main model's response, its actual
file change, and the test results from this run. Automatic selected Simplicity,
Anthropic `claude-opus-5` produced the Nudge, and OpenAI `gpt-5.6-sol` was the
main model. This is one observed reaction, not a promise that every Nudge will
be adopted.

---

## The three engineering Lenses

| Lens | The decision it focuses |
|---|---|
| Simplicity | Which complexity is necessary, and which component should own the responsibility |
| Reliability | What must remain true when events reorder, retry, or fail partway |
| Performance | Which measured work on the real execution path should disappear |

These recurring preferences about ownership, invariants, and measured work are
what this project calls engineering taste.

---

## Nudge contract

To the main agent, a Nudge is one short, evidence-grounded second opinion.
The provider returns exactly one JSON outcome:

- `finding`: one concrete engineering preference in one direct Traditional
  Chinese statement, within 52 characters;
- `no_finding`: silence when the supplied evidence does not support a useful
  preference.

A finding states what to favor, preserve, simplify, or remove. It is not a
question, review narration, complete solution, or generic request to add or run
tests.

Example:

```text
直接記錄輸入來源；別用值猜測，因為相同值不代表相同來源。
```

The main agent receives:

```text
Independent second opinion:
<one short direction>
```

Runtime validation is deliberately structural. It checks JSON shape, status
and field consistency, supported Lens, emptiness, one output object, and the
52-character limit. It does not use keywords or regular expressions to judge
engineering taste or rewrite a structurally valid result.

Prior Nudges are not shown to the provider. An exact duplicate of a previously
injected finding is suppressed only after generation.

---

## How it works

```text
Observable tool result
        ↓
Bounded task-and-evidence packet
        ↓
One qualified Lens, or none
        ↓
One short Nudge, or no_finding
        ↓
The agent’s later context
```

Each Nudge is generated from the evidence available at that control point. It
is not selected from a list of stock sentences. As new context, it can influence
later generation without changing model weights; the main agent may adopt,
reinterpret, or ignore it.

Automatic mode uses a compact Router to select one qualified Lens or `none`.
The Generator receives the original packet and only the selected Filter; Router
reasoning is not forwarded. Manual mode pins one Lens but does not waive its
evidence requirement or force a finding.

The names behind the Filters are private attention cues in provider prompts,
not claims that the provider imitates a person or gains that person’s ability.

Masters’ Nudge is not a reviewer, judge, solver, or Stop gate, and it does not
claim to improve general problem-solving accuracy.

---

## Host control points

The ideal intervention point is after all tool results from the current model
step are complete and before the next model request begins.

| Host | Control point | Precision | Known limitation |
|---|---|---|---|
| Claude Code | Native `PostToolBatch` | Exact for the native batch | A batch is marked failed only when its serialized result contains an explicit failure signal |
| Codex | Synchronous `PostToolUse` | Approximate | Parallel tools may be observed and considered separately because Codex does not expose a native batch boundary |

Claude Code creates at most one Nudge attempt for one completed tool batch.
Codex treats each `PostToolUse` as a one-item batch. Masters’ Nudge does not use
a timer, transcript guess, or delayed resend to imitate a missing Codex batch
boundary.

Eligible attempts run synchronously so a valid Nudge can enter later context in
the same turn. Provider work is capped at 90 seconds inside a 120-second Host
Hook budget. Automatic mode shares the provider budget between Router and
Generator; manual mode makes one Generator call. Errors and timeouts fail open:
the attempt ends and the main agent continues.

At `Stop`, the Hook only records whether the main agent responded after an
earlier Nudge. It does not call the Provider, emit another Nudge, block
completion, or extend the turn.

---

## What the provider sees

The provider receives only the bounded packet constructed for the current
control point. Depending on the event, it may contain:

- the current user task anchor;
- content from local sources explicitly named by the task;
- recent length-bounded substantive changes;
- objective failures, validations, tool results, and measurements.

It does not receive:

- the complete transcript;
- the main model’s undisclosed internal reasoning;
- the main agent’s running narration or response to a Nudge;
- prior Nudges;
- general navigation, search, or browsing output;
- source exploration not explicitly named by the task;
- tool names or complete commands.

The Base prompt defines only who the provider is, what it can see, and its
output contract. The selected Filter supplies the full engineering focus. The
Router and Generator both work from the original packet; the Generator never
receives a routing hypothesis.

---

## Supported providers

- Anthropic
- OpenAI
- xAI through an authenticated Grok CLI
- Local Ollama

Each Nudge attempt is an independent model call, even when the provider family
matches the main agent’s model family. No provider silently fails over to
another provider.

Without overrides, Claude Code uses Anthropic `sonnet`, and Codex uses OpenAI
`gpt-5.6-sol`.

---

## Installation

Requirements:

- a plugin-capable Claude Code or Codex CLI installation;
- Python 3.10+;
- an authenticated CLI for the selected cloud provider, or an already installed
  local Ollama model.

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

If `python` is not Python 3.10+, set `python_command` to `python3` or the
absolute path of the Python executable. The value must contain one executable
only, with no additional arguments.

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

Restart the Host after an update. Uninstalling preserves existing data under
`~/.masters-nudge/data/`.

---

## Usage and checks

Hooks run automatically; Masters’ Nudge does not need to be named in every
prompt. The plugin also includes Skills for these explicit tasks:

- **“Check whether Masters’ Nudge is ready.”** Checks Python, provider access,
  data-directory writes, Host Hooks, control-point precision, and optional UI
  dependencies without calling the Nudge provider.
- **“Open the Masters’ Nudge floating window.”** Opens the local history and
  settings window; it requires Pillow and Python with Tkinter.
- **“Configure Masters’ Nudge to use my local Ollama model
  `<full-model-name>`.”** Verifies an installed model on loopback Ollama and
  saves the provider configuration.
- **“Migrate legacy Masters’ Nudge hooks.”** Shows a dry run before changing
  clearly identifiable legacy Hooks after explicit approval.

Legacy Lens selections that no longer exist resolve to Automatic mode; they are
not mapped to a retained Lens.

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | Host-dependent | `anthropic`, `openai`, `grok`, or `ollama-local` |
| `MASTERS_NUDGE_MODEL` | Host-dependent | Full provider model name |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `90` | Provider timeout in seconds |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | Provider timeout at a tool control point |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | State, findings, receipts, telemetry, and provider configuration |
| `MASTERS_NUDGE_STAGE` | unset | `automatic`, `review`, `reliability`, or `performance` |
| `MASTERS_NUDGE_SPRITE_PATH` | bundled sprite | Optional floating-window spritesheet |

`MASTERS_NUDGE_STAGE` overrides the saved stage in `config.json`. `review`
selects Simplicity, `reliability` selects Reliability, and `performance`
selects Performance. When unset, Automatic mode uses the Router.

Provider environment variables override saved settings in `reviewer.json`.
Malformed provider configuration leaves a diagnostic and ends that attempt.

Local Ollama mode connects only to a loopback endpoint, disables client proxies
and redirects, uses an already installed model, and never downloads one. If the
local provider fails, the attempt ends without cloud fallback.

---

## Data, privacy, and evidence limits

Tasks, bounded evidence, findings, delivery receipts, provider settings, and
diagnostic telemetry are stored as plain text under:

```text
~/.masters-nudge/data/
```

Telemetry records content-free Host, Hook event, route, status, latency, and
provider-reported usage metadata.

Injected receipts and later response observations establish delivery order only.
They do not prove that a Nudge caused a later action. Likewise, Masters’ Nudge
does not claim to improve general problem-solving accuracy or test pass rates.
Whether a Filter produces recognizable engineering taste requires separate
blind evaluation of fixed evidence packets.

Cloud-provider retention and training policies are controlled by each provider.

---

## Development

Repository source is canonical. The checked-in plugin package is generated from
that source.

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- Architecture: [docs/architecture.md](docs/architecture.md)
- Active decisions: [ROADMAP.md](ROADMAP.md)
- License: [MIT](LICENSE)
