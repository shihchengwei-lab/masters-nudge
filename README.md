# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

> Dynamically add a new semantic anchor while an LLM agent is working.

Masters’ Nudge is a dynamic context steering plugin for Claude Code and Codex.

At selected checkpoints, it collects limited evidence left by the main agent and sends it to an independent Nudge provider. The provider focuses through a selected Lens, produces a short Nudge, and the Harness writes it into the main agent’s context.

The short question is the surface form of a Nudge. Underneath, the system places a new semantic anchor into context so the main agent continues generating under a new condition.

---

## The loop

```text
The user provides a task
        ↓
The main agent works and leaves observable results
        ↓
The Hook collects the current task and limited evidence
        ↓
The checkpoint policy decides whether to run a review
        ↓
The Nudge provider focuses through the selected Lens
        ↓
It produces one short question, or returns no_finding
        ↓
The Harness writes the Nudge into context as a new anchor
        ↓
The main agent continues under the new context
        ↺
```

Each Nudge is generated dynamically from the evidence available at that moment.

The same Lens can produce completely different anchors across tasks, stages, and outcomes.

---

## The underlying mechanism

An LLM uses its current context to calculate the conditional probability distribution of the next token.

After a Nudge enters context, its tokens also participate in subsequent generation. This can shift the next-token distribution and the generation path that follows.

Here, an “anchor” is a small sequence of tokens added to context. It introduces a new direction into the conditions available to subsequent generation.

```text
The original context
        +
A new semantic anchor
        ↓
A new token distribution
        ↓
A potentially different generation path
```

Masters’ Nudge currently compresses this anchor into one short question.

The question supplies a direction without expanding into a complete solution. The main agent combines that direction with the original task, evidence, and generation path, then decides what to produce next.

This control point lives in inference-time context. The model weights remain unchanged.

The anchor itself, its injection point, the main agent’s current state, and the surrounding context all shape the resulting shift.

---

## Why it is called Masters’ Nudge

`Masters` refers to a focusing filter placed in front of the Nudge provider.

A well-known name is the surface form of this filter. Underneath, the design relies on the dense associations between that name and related concepts in the model’s training material.

The design starts from a practical assumption:

Well-known people usually appear in a large amount of related text. Their names repeatedly co-occur with the questions they care about, the judgments they make, the trade-offs they emphasize, the cases associated with them, and the language used to describe their work.

A simplified way to understand this is that a person’s name and a particular set of concerns occupy nearby regions in the model’s semantic space.

When the name appears in the provider prompt, those associated patterns become easier to activate, helping the provider focus its generation on those concerns.

```text
Current evidence
    +
Master filter
    ↓
Nudge provider
    ↓
Focus on a nearby semantic region
    ↓
Produce one short Nudge
    ↓
Create a new anchor in the main agent’s context
```

The Master filter is supplied only to the Nudge provider.

The provider reads the current evidence through this filter, selects the direction most worth adding to the main agent’s context, and compresses it into a Nudge.

The main agent receives only the final question. It does not receive the person’s name, the role description, or the complete reviewer prompt.

The project name describes this path:

> **Masters focus the provider, the provider produces a Nudge, and the Nudge becomes a new anchor in the main agent’s context.**

The load-bearing part of the project is whether the Lens helps the provider select a useful direction from the evidence, and whether the resulting Nudge affects the main agent’s current generation path.

A name is one compressed representation of a Lens. The same position can instead hold explicit engineering principles, a moral philosophy, compliance requirements, scientific methods, or another evaluation framework.

---

## A Lens determines the direction of focus

A Lens defines what the Nudge provider should pay attention to.

It can focus on:

- software-engineering judgment;
- system boundaries and ownership;
- state, event order, and invariants;
- execution cost and performance;
- moral trade-offs;
- compliance evidence;
- scientific counterexamples and falsifiability conditions.

Different Lenses can select different semantic anchors from the same evidence.

The current implementation expresses each anchor as a question:

```text
Engineering Lens:
Which component actually owns this state?

Moral Lens:
Whose cost has this decision moved outside the system?

Compliance Lens:
What evidence supports this compliance claim?

Scientific Lens:
What result would distinguish these two explanations?
```

This repository currently implements the software-engineering version. Other Lenses can use the same Hook, checkpoint, and injection loop.

---

## The shape of a Nudge

The current output contract compresses a semantic anchor into one short question.

To the main agent, the Nudge is one short, evidence-grounded second opinion.

The Reviewer returns one of two outcomes.

### `finding`

A valid Nudge:

- uses only the evidence supplied for the current review;
- focuses on one assumption, constraint, counterexample, or alternative direction;
- asks one concrete question that can be checked now;
- contains only one idea;
- stays within 52 characters.

The main agent receives:

```text
Independent second opinion:
<one short question>
```

### `no_finding`

When the available evidence does not support a useful new direction, the Reviewer can return `no_finding`, and the main agent continues on its existing path.

In practice, `no_finding` is usually a low-probability result.

After an LLM receives a review task, it tends to produce a deliverable opinion rather than say it has no opinion. Even when the evidence is weak, it may force a question.

`no_finding` therefore provides an explicit path to silence. It should not be expected to appear as often as `finding`.

The structural validator checks the output format, item count, and length. Only a Nudge that satisfies the contract enters the main agent’s context.

---

## How it differs from other controls

| Control | How it intervenes |
|---|---|
| Fixed System Prompt | Applies a persistent behavioral bias before the task begins |
| Temperature | Changes the global dispersion of token sampling |
| Full Reviewer | Produces another analysis, recommendation, or solution |
| Masters’ Nudge | Adds one short, local semantic anchor based on the current state |

A fixed System Prompt is suitable for persistent rules.

Temperature is suitable for adjusting the overall sampling process.

A full Reviewer is suitable for delivering a separate analysis.

Masters’ Nudge intervenes during the work. It first reads how far the main agent has progressed, then chooses which direction to place into context at that moment.

The current implementation carries that direction in a short question.

---

## The Harness turns one Prompt into a loop

A single Prompt can ask another model to produce a new direction.

The Harness makes that direction operate repeatedly inside a fixed workflow:

1. preserve the user’s task;
2. collect observable evidence;
3. evaluate the checkpoint;
4. select a Lens;
5. invoke the Nudge provider;
6. validate the Nudge format;
7. write the Nudge into the main agent’s context as a new anchor;
8. record the review, delivery, and subsequent response.

This engineering layer turns a one-off Prompt technique into a repeatable, replaceable, and observable intervention loop.

---

## A pluggable superego

A simplified analogy can describe the architecture:

- **The main LLM is the id:** it supplies the drive to keep generating, solving, and acting.
- **The Harness is the ego:** it manages tools, evidence, timing, and workflow.
- **The Nudge is the superego:** it introduces an additional semantic anchor at a selected moment.

Changing the Lens changes what this superego pays attention to.

It can add an anchor for engineering judgment, morality, compliance, safety, or scientific evidence. The main model and Harness stay the same while the direction of intervention changes dynamically.

This analogy describes architectural roles. It does not claim that models have human psychological states.

---

## Tension and convergence

After working for some time, the main agent begins to form a generation path that is moving toward convergence.

A Nudge places another semantic anchor into the same context, requiring the main agent to account for both its existing path and the new direction.

When the Nudge reaches a blind spot, this tension can:

- expose an untested assumption;
- prevent a premature completion claim;
- recover a direction that was dropped too early;
- prompt one discriminating check;
- move generation toward a lower-probability but more valuable path.

When the Nudge conflicts with sufficient evidence or reopens a question at the wrong time, the same tension can appear as:

- a resolved issue being opened again;
- loss of focus on the main objective;
- oscillation between directions;
- continued divergence without convergence.

The mechanism derives its effect from tension and is also limited by that tension.

The Harness bounds each intervention through sparse checkpoints, limited evidence, one question, a 52-character limit, and the `no_finding` path.

---

## The current software-engineering implementation

The repository currently provides six engineering Lenses:

| Lens | Direction of focus |
|---|---|
| Design | Upstream constraints, ownership, and downstream cost |
| Build | Shortest feedback path, observable behavior, and stopping conditions |
| Evolve | Duplicated knowledge, change propagation, and correct ownership |
| Review | Control flow, necessary complexity, and ownership |
| Reliability | State, event order, invariants, and partial failure |
| Performance | Actual execution cost and unnecessary work |

Automatic mode selects a Lens from the main agent’s reported work focus. This focus report only selects the reviewer prompt; the Hook and checkpoint policy still decide whether a review runs.

Manual configuration can pin the Design, Build, Evolve, or Review Lens.

---

## Supported environments

### Host

- Claude Code
- Codex CLI

The two Hosts use different event adapters, then construct the same bounded `ReviewRequest` for the shared review core.

### Nudge provider

- Anthropic
- OpenAI
- xAI through an authenticated Grok CLI
- Local Ollama

Every review is an independent model call, even when it uses the same provider as the main agent.

---

## Review checkpoints

The current Hooks may produce a Nudge at these points:

- the second failure on the same observable surface;
- an explicit transition of a long-running goal to `complete` or `blocked`;
- the end of a work turn.

Ordinary code changes, large diffs, successful validation, and the first failure accumulate as evidence. The Nudge provider reads the bounded evidence packet only after a checkpoint becomes eligible.

Eligible reviews run synchronously so the Nudge can enter the main agent’s later context in the same turn.

Provider work is capped at 90 seconds, inside a 120-second Host Hook budget. If a review errors or times out, that intervention ends and the main agent continues.

---

## Installation

Requirements:

- a plugin-capable Claude Code or Codex CLI installation;
- Python 3.10+;
- an authenticated CLI for the selected cloud Nudge provider; local Ollama does not require cloud authentication.

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

If `python` is not Python 3.10+, set `python_command` to `python3` or to the absolute path of the Python executable.

The setting must contain one executable only, without additional arguments.

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Open a new task after installation.

Codex users must open `/hooks`, inspect the commands, and approve the plugin Hooks.

Plugin packaging and Hook approval follow the current [OpenAI plugin documentation](https://developers.openai.com/plugins/build/plugins) and [Codex Hooks documentation](https://learn.chatgpt.com/docs/hooks).

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

Restart the Host after an update.

Uninstalling the plugin preserves existing data under `~/.masters-nudge/data/`.

---

## Usage and checks

Hooks run automatically. Masters’ Nudge does not need to be invoked manually in every Prompt.

The following requests activate built-in plugin Skills:

- **“Check whether Masters’ Nudge is ready.”**  
  Checks the runtime, provider, data-directory write access, Hooks, and optional UI dependencies without invoking the Reviewer.

- **“Open the Masters’ Nudge floating window.”**  
  Opens the local history window. It requires Pillow and a Python installation with Tkinter.

- **“Configure Masters’ Nudge to use my local Ollama model `<full-model-name>`.”**  
  Validates that the model is installed on loopback Ollama and saves the configuration.

- **“Migrate legacy Masters’ Nudge hooks.”**  
  Shows a dry run first, then handles clearly identifiable legacy Hooks after explicit approval.

Before migration, the plugin creates a timestamped backup beside the Host configuration. Ambiguous legacy settings remain in diagnostics, and existing review data is preserved.

---

## Configuration

Without overrides:

- Claude Code uses Anthropic `sonnet`;
- Codex uses OpenAI `gpt-5.6-sol`.

Common environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | Host-dependent | `anthropic`, `openai`, `grok`, or `ollama-local` |
| `MASTERS_NUDGE_MODEL` | Host-dependent | Full Reviewer model name |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `90` | Reviewer timeout at the end of a turn, in seconds |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | Reviewer timeout during the work, in seconds |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | Logs, state, receipts, telemetry, and Reviewer configuration |
| `MASTERS_NUDGE_STAGE` | unset | Select `automatic`, `design`, `build`, `evolve`, or `review` |
| `MASTERS_NUDGE_SPRITE_PATH` | bundled sprite | Optional floating-window spritesheet |

Provider environment variables take precedence over saved settings in `reviewer.json`.

`MASTERS_NUDGE_STAGE` takes precedence over the engineering stage in `config.json`. When unset, the plugin uses Automatic mode. When set, the Reviewer uses the selected Lens.

A malformed or unreadable Reviewer configuration leaves a diagnostic and ends that review.

### Local Ollama

Local mode connects only to a loopback HTTP endpoint and disables client proxies and redirects.

The setup flow confirms that Ollama cloud features are disabled and checks the model metadata. Masters’ Nudge uses an already installed model and does not download one automatically.

If the local provider fails, that review ends without being forwarded to a cloud provider.

---

## Data and privacy

The Reviewer receives only the bounded evidence packet constructed by the Hook.

Depending on the event, the packet may contain:

- the latest user task request;
- content read from local sources explicitly named by the task;
- the latest length-bounded substantive changes;
- semantic validation and failure results;
- the current final claim at a Stop boundary.

Up to three previously injected Nudges are sent as an exclusion set to reduce repetition.

The Reviewer prompt and selected Lens are generation instructions, not evidence.

The following content does not enter the Reviewer packet:

- the complete transcript;
- the main model’s undisclosed internal reasoning;
- general search and browsing output;
- general source-code exploration not explicitly named by the task;
- external reports;
- tool names and complete commands;
- the main agent’s in-progress narration or response to a Nudge.

Tasks, evidence, Nudges, delivery receipts, provider settings, and diagnostic telemetry are stored as plain text under:

```text
~/.masters-nudge/data/
```

Telemetry records routing, status, latency, and usage metadata reported by the provider.

Review scheduling and receipt states are documented in [the architecture document](docs/architecture.md).

Cloud-provider retention and training policies are controlled by each provider.

---

## Historical evaluation material

The repository preserves one prerelease A/B snapshot:

- four previously unused SWE-bench Verified tasks;
- Arm A ran with plugin Hooks disabled and passed 2/4;
- Arm B ran with the historical plugin snapshot enabled and passed 3/4;
- Arm B produced and injected six Reviewer findings;
- one task produced a different result between the two arms.

The snapshot comes from commit `ac090a9f34ff76b826ceedb10361f7d7a3bd4ed3`. It records that historical version, not validation of the current source tree.

Four fixed-order tasks provide descriptive behavioral material. They are insufficient to establish a stable effect, demonstrate generalization, or attribute the changed task result to the Nudge.

Injected receipts and later response observations establish delivery order only. They cannot prove that a Nudge caused the later action.

For the full protocol, results, exclusions, and claim boundaries, see:

- [Historical prerelease benchmark](evaluation/README.md)

---

## Development

The plugin package in this repository is generated from source.

Before submitting changes, run:

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- Architecture: [docs/architecture.md](docs/architecture.md)
- Active decisions: [ROADMAP.md](ROADMAP.md)
- License: [MIT](LICENSE)
