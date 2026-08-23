# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

Masters’ Nudge gives Claude Code or Codex one brief, evidence-grounded second opinion at selected checkpoints and at the end of a turn. The reviewer prompt asks for one short open question or permits silence; the coding agent remains responsible for every decision and change.

## What it does

Masters’ Nudge packages hooks, skills, reviewer prompts, six software-engineering lenses, and an optional floating window as one plugin. It looks for workflow tensions such as an untested assumption, expanding scope, weak feedback, fragile event order, or a completion claim that has moved ahead of its evidence.

A Nudge is not a code review, an instruction, or proof that another model is more accurate. Findings are sanitized and capped at 52 characters. Selected tool failures, test failures, large changes, long-goal transitions, and end-of-turn events may each invoke a reviewer.

## Install

Requirements:

- A plugin-capable Claude Code or Codex CLI installation
- Python 3.10+
- The CLI for the selected cloud reviewer provider is signed in, unless local-only Ollama is configured

Claude Code:

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

Use `python3` or an absolute executable path as `python_command` when `python` is not Python 3.10+. The value must be one executable without arguments.

Codex:

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Start a new task after installation. In Codex, open `/hooks`, inspect the commands, and approve the plugin hooks. Plugin packaging and hook approval follow the current [OpenAI plugin documentation](https://developers.openai.com/plugins/build/plugins) and [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).

Update or remove:

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

Restart the host after an update. Uninstalling the plugin does not delete `~/.masters-nudge/data/`.

## Use and diagnose

The hooks run automatically. These requests activate bundled skills:

- “Check whether Masters’ Nudge is ready.” — checks the runtime, provider, writable data directory, hooks, and optional UI dependencies without making a reviewer call.
- “Open the Masters’ Nudge window.” — opens the optional local history window; Pillow and a Python build with Tkinter are required.
- “Configure Masters’ Nudge for my local Ollama model `<exact-model>`.” — validates an already-installed model on a loopback Ollama server and persists the setting.
- “Migrate my legacy Masters’ Nudge hooks.” — shows a dry run first, then changes only exact known legacy hooks after explicit approval.

Migration writes an adjacent timestamped backup before changing a host config. Modified or ambiguous hooks, malformed data, conflicting destinations, and legacy specialist personas that cannot be mapped safely are reported for manual handling. Existing review data is not deleted.

## Configuration

Without an override, Claude Code uses Anthropic `sonnet`; Codex uses OpenAI `gpt-5.6-sol`. A reviewer is a separate model invocation, even when it uses the same provider as the host.

Common environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | Host-aware | `anthropic`, `openai`, `grok`, or `ollama-local` |
| `MASTERS_NUDGE_MODEL` | Host-aware | Exact reviewer model |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `120` | End-of-turn reviewer timeout in seconds |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | Mid-turn reviewer timeout in seconds |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | Logs, state, receipts, telemetry, and reviewer config |
| `MASTERS_NUDGE_STAGE` | Unset | Select `design`, `build`, `evolve`, or `review` |
| `MASTERS_NUDGE_SPRITE_PATH` | Bundled sprite | Optional floating-window spritesheet |

Provider environment variables override the persistent `reviewer.json` setting; `MASTERS_NUDGE_STAGE` overrides the lifecycle stage in `config.json`. A malformed reviewer config stops the review and writes a diagnostic; it does not silently switch providers.

The floating window and public configuration describe engineering stages and practical focus, not the people used as private reviewer attention cues. Reliability and Performance may take over automatically when the packet contains direct specialist evidence; they are not manual stage settings.

Local-only mode accepts only loopback HTTP, disables client proxy use and redirects, requires Ollama to report cloud features disabled, and rejects remote model metadata. It never installs or pulls a model and never falls back to a cloud provider. Grok remains a cloud provider through the signed-in Grok CLI.

## Privacy

Default reviews send a bounded current-state packet to an external provider: Anthropic for Claude Code and OpenAI for Codex. Explicit `grok` configuration sends it to xAI. Local-only mode sends it to the validated loopback Ollama server.

Depending on the event, the packet can contain:

- the latest user task anchor;
- the triggering tool input/output, errors, test output, or diff summary;
- a bounded current-turn journal or Claude transcript slice;
- the current final claim and verification evidence;
- optional agentcam evidence;
- the reviewer prompt and selected lens.

Reactions, task anchors, bounded journals, delivery receipts, local-model selection, and content-free diagnostic telemetry are stored as plain text under `~/.masters-nudge/data/`. The telemetry records routing, status, latency, and provider-reported usage metadata; there is no active cost experiment or automatic cost gate. On Codex, a receipt may also record the first observable host action after an injection. That following action records sequence only; it does not prove that the Nudge caused the action. Provider retention and training policies are outside this repository and may change.

## Evidence and limits

The retained evidence index is [evaluation/README.md](evaluation/README.md).

Current evidence supports only bounded claims:

- Fixed synthetic packets showed lens separation and schema compliance; they do not prove general reliability.
- Phase B synthetic tasks produced no positive treatment effect and were stopped.
- Provider-reported tokens, latency, and estimated cost are not normalized across providers and are not billing guarantees.
- Hook delivery is best-effort when a host does not emit an expected native event.

## Development

The checked-in plugin package is generated from the repository source. Before submitting a change:

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- Architecture: [docs/architecture.md](docs/architecture.md)
- Active decisions: [ROADMAP.md](ROADMAP.md)
- License: [MIT](LICENSE)
