# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

**Before a coding agent decides what to do next, add one brief reminder from a different angle.**

At a few key moments, Masters’ Nudge asks another model to generate one brief reminder from the current progress, then adds it to the main agent's context. It does not take over the task or inspect code line by line; the reminder simply makes the model more likely to notice a direction it may have overlooked.

In LLM terms, it uses a dynamic frame to guide the reviewer in generating a Nudge, then injects that Nudge into the main agent's context, indirectly shifting the conditional probability distribution of the tokens that follow.

## Start with an example

**Original next move**

The feature and automated tests are done, so the main agent is ready to call the installation experience complete.

**Nudge**

> The clean install is still unverified.

**Reconsidered next move**

The main agent first follows the README from a clean environment, then decides whether the work is ready to call complete.

The Nudge did not identify a bad line or issue an instruction. It brought an implicit way of working back onto the decision table, giving the main agent one chance to reconsider before more cost accumulates.

## What problem it solves

The problem is not that coding agents cannot write code. In a long task, the same agent plans, executes, and judges its own work, so early assumptions can survive all the way to completion. When the direction is sound, that momentum helps. When it is not, the agent can keep patching and elaborating without stopping to reconsider.

At a few key moments, Masters’ Nudge captures a small evidence packet and asks a separate model to look only at how the work is framed, advanced, and verified. It either leaves one short Nudge or stays silent; the main agent still makes every decision and performs every change.

Claude Code and Codex CLI 0.147+ are supported.

## An observable long-task experiment

The software-engineering version is difficult to benchmark directly: workflow
effects are mixed with the coding agent's own reasoning, and a short task may
finish before a Nudge has a visible consequence. To obtain a longer,
inspectable trace, we made a local mathematical specialization and ran it on an
extended Riemann-hypothesis research task.

That math profile is an archived experiment, not a shipped feature and not a
claim of mathematical progress. Across three sessions it produced 102 Nudge
findings. Delivery receipts were available only in the final segment: 19
findings were generated there, 17 were confirmed in the main model's context,
and 13 of those 17 had a direct, reframed, or delayed visible response. With no
control arm, these are observational interactions rather than a causal effect
estimate.

Start with the **[benchmark result and limitations](experiment/riemann-domain/benchmark/README.md)**,
then read the **[complete 17 traceable interactions](experiment/riemann-domain/benchmark/interactions.md)**
and, if useful, the **[four reproducible route-closure packages](experiment/riemann-domain/benchmark/closures/README.md)**.

## Why only one line?

Each nudge is at most 52 characters and points to one concrete workflow tension or question.

It may surface an assumption that was never revisited, feedback that stops too early, growing scope, a fragile event order, or a completion claim that has moved ahead of its evidence.

The point is not to produce another answer or another code review. It is to give the same workflow one brief look from another angle before the agent continues.

## Why another model?

When the same model continues its own work, it can carry the same assumptions into the next decision.

The zero-config reviewer follows the host you already authenticated: Claude Code uses Anthropic `sonnet`; Codex uses OpenAI `gpt-5.6-sol`. You can explicitly choose the other provider or bring a user-selected, locally installed Ollama model. The second opinion always has a separate context and role, but is not cross-vendor unless you configure it that way.

The second model receives only a small packet of current evidence and must ground its nudge in that material. Code, tests, and tool output may anchor the observation, but the target is how the work is being framed, sequenced, scoped, tested, or declared complete. If the evidence does not support a useful nudge, it says nothing.

## When does it join in?

```
Coding agent works normally
    │ tool failure / test failure / first large change
    ├─► check once → main agent only
    │
    │ turn ends
    └─► check once in the background
              ├─ give it to the agent on your next message
              └─ show it in the floating window
```

| Moment | Why look again? | Who sees it? |
|---|---|---|
| Tool failure | The fix may address only the surface symptom | Main agent |
| Test failure | The repair may be taking a longer route around the problem | Main agent |
| First change over ~80 lines | The task may be growing beyond its original scope | Main agent |
| Repeated command/failure family, 8 meaningful events, or another ~80 changed lines | Local progress may not shorten the original acceptance criteria | Main agent and floating window |
| Goal declares `complete` or `blocked` | Distinguish objective completion, a sub-result, and path exhaustion | Main agent and floating window |
| End of turn | Check whether the work is actually complete | Main agent and the floating window |

Tool/test failures and the first large diff remain immediate checks and may pause the main agent for up to about 15 seconds. Codex long-goal strategy checks run in the background and inject on the next hook event; `complete`/`blocked` Goal transitions are checked immediately. Each reaction records its source event sequence and a `queued`, `injected`, `expired`, or `failed` delivery state, so the floating window does not confuse reviewer output with context the main model actually received. End-of-turn checks also run in the background. Claude Code reports failures through `PostToolUseFailure`; the Codex adapter can infer structured non-zero exits and failure status when Codex delivers them in `PostToolUse`. The tested Windows 0.147.0 build did not emit that event for a non-zero Bash result, so immediate failure checks are best-effort there and Stop remains the fallback.

The main agent receives an end-of-turn nudge when you send your next message. The floating window reads both hosts' namespaced logs and is the direct user-visible channel.

Output is either one finding or silence. Findings are stripped of markdown and filler, with a hard limit of 52 characters. The hook envelope identifies the effective lens and review reason outside that limit; the finding itself never spends its 52 characters naming a person or lens.

## Who this is for

**Suitable** if you use Claude Code or Codex CLI and either accept the host's external reviewer API or configure the experimental loopback-only Ollama provider.

If conversation or code must not leave the machine, configure local-only mode before relying on the hooks. Details: [Local-only Ollama reviewer](#local-only-ollama-reviewer-experimental) and [Privacy](#privacy).

Cost: by default **every completed turn** calls the review model once; mid-turn calls only on error / test failure / first large change. Busy days accumulate tokens.

## Install

The repository marketplace currently serves the unreleased `0.1.0-dev.2` prerelease; no release tag has been created.

### Prerequisites

- Claude Code with plugin support (tested on 2.1.215), Codex CLI 0.147+, or both
- The chosen host CLI signed in and callable from the terminal
- Python 3.10+

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

Start a new Claude Code session. No clone, manual hook merge, or UI package is required for the core Nudge.

If Python 3.10+ has another executable name or path, replace the configuration value (it must not contain arguments):

```bash
claude plugin install masters-nudge@masters-nudge --config python_command=python3
```

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Start a new task, open `/hooks`, review the commands, and trust the plugin hooks. Codex intentionally asks for approval when a new hook command or command hash appears; see the [official hooks documentation](https://learn.chatgpt.com/docs/hooks).

### Check, migrate, or open the window

Ask the host to **“Check whether Masters' Nudge is ready.”** The bundled `doctor` skill checks Python, provider readiness, writable data paths, hooks, and optional UI dependencies without generating a reviewer response. For local mode it reads only Ollama status and model metadata.

If you previously used the manual install, first install the plugin and then ask it to **“Migrate my legacy Masters' Nudge hooks.”** Migration shows a dry run, changes only exact known hook entries after confirmation, writes an adjacent timestamped backup, and leaves runtime and review data untouched. Modified entries are refused for manual review.

The floating window is optional. Install Pillow, then ask the host to **“Open the Masters' Nudge window.”** Tkinter must also be present in the Python build.

```bash
python -m pip install --user Pillow
```

Closing the window does not disable hooks.

### Local-only Ollama reviewer (experimental)

Ask the host to **“Configure Masters' Nudge for my local Ollama model `<exact-model-name>`.”** The bundled `setup-local` skill uses your model choice; it never installs Ollama, pulls a model, signs in, or recommends a model size.

[Ollama must already be running with cloud features disabled](https://docs.ollama.com/faq) using `OLLAMA_NO_CLOUD=1` or `disable_ollama_cloud`, and the selected model must already exist locally. The setup refuses remote endpoints, redirects, cloud-enabled servers, explicit cloud model names, and models whose metadata names a remote host. Older Ollama builds without the cloud-status endpoint are rejected. It writes the shared setting to `~/.masters-nudge/data/reviewer.json`, so both Claude Code and Codex use it. Calls use Ollama's native [structured-output schema](https://docs.ollama.com/capabilities/structured-outputs).

### Grok subscription reviewer

If Grok CLI is installed and signed in, run `python masters_nudge_cli.py grok configure` to use its default model for both Claude Code and Codex, or add `--model <model-id>`. Every review is a single structured-output turn with web search, tools, memory, and subagents disabled. Bounded evidence still goes to xAI cloud; this is not local-only mode. Run `python masters_nudge_cli.py grok reset` to restore host defaults.

Providers, models, and CLI harnesses have different token overhead, subscription limits, pricing, and rate limits. Masters’ Nudge does not decide which option is economical and does not assume a subscription means zero marginal cost. In one very short smoke on 2026-08-14, Grok CLI 1.0.3 using `grok-4.6-build` reported 12,717 input tokens, 774 output tokens, and `total_cost_usd: 0.030142`; most of that input was clearly not the tiny evidence packet and may belong to the Grok Build harness. This is one CLI-reported observation—not an invoice, fixed price, or future promise. Users should judge from their provider plan, trigger frequency, and observed usage.

Source-install users can run the same setup directly:

```bash
python masters_nudge_cli.py local configure --model <exact-model-name>
```

Use `--url http://localhost:<port>` only for another loopback port. To remove the persistent local setting, explicitly ask the host to reset it or run `python masters_nudge_cli.py local reset`; reset restores the normal cloud default unless environment variables override it.

This is a BYOM compatibility interface, not a quality or licensing claim. Model size, license, latency, and usefulness are the user's decision.

### Update or uninstall

```bash
# Claude Code
claude plugin marketplace update masters-nudge
claude plugin update masters-nudge@masters-nudge

# Codex
codex plugin marketplace upgrade masters-nudge
codex plugin add masters-nudge@masters-nudge
```

Restart the host after an update; review Codex hooks again if their command hash changed.

```bash
claude plugin uninstall masters-nudge@masters-nudge
codex plugin remove masters-nudge@masters-nudge
```

Uninstalling does not remove `~/.masters-nudge/data/`.

<details>
<summary>Source / legacy installation</summary>

Clone the repository, run `bash install.sh --all` or `.\install.ps1 -HostName all`, then merge the appropriate [`settings-snippet.json`](settings-snippet.json) or [`codex-hooks-snippet.json`](codex-hooks-snippet.json) without replacing the whole settings file. Use `--claude` / `--codex` (or `-HostName claude` / `codex`) for one host. This path is retained for compatibility and development; new users should prefer the plugin.

</details>

### Verify

- Force a failing test, or finish a turn: a checkpoint hit may add a few seconds of wait; the next prompt should receive any end-of-turn finding.
- New logs: `~/.masters-nudge/data/<host>--<session_id>.log`; errors: `~/.masters-nudge/data/error.log`.
- No log at all: run the bundled doctor; hooks are usually not loaded/trusted, or the selected provider is not ready.

## Filters: different stages, different workflow questions

Different parts of a project make different problems easy to miss.

During design, data, state, and ownership matter most. During implementation, scope can quietly grow. As the code evolves, today's structure can make tomorrow's change harder. Before delivery, it is worth asking which layers never needed to exist.

Each lens gives the reviewer a private observation scene: a distinct operation for arranging visible evidence, such as tracing causality, shortening a feedback loop, following change propagation, removing transfer layers, reordering events, or counting an execution path. These scenes guide attention; they are not biographical claims, output styles, or evidence.

![Six Masters' Nudge lenses showing different workflow observations from the same checkpoint](docs/images/masters-nudge-six-lenses-hero.png)

*Same evidence and model; only the lens changes. These are actual delivered
findings rendered by six real Tk windows. In the fresh 18-call run, all six
lenses aligned in 3/3 repeats and all 18 delivered findings were complete and
punctuated. Three capped raw outputs were closed locally without rejection or
retry. [See the evaluation and selection details.](evaluation/results/lens-observation-scenes-20260813/ROUND_4_RESULT.md)*

| Stage | Viewpoint | First question |
|---|---|---|
| Design | Jeff Dean (`jeff`) | Are data, state, or ownership in the wrong place? |
| Build | Kent Beck (`beck`) | Has the work grown beyond what is needed now? |
| Evolve | Martin Fowler (`fowler`) | Will this structure make the next change harder? |
| Review | Linus Torvalds (`linus`) | Which extra layers do not need to exist? |

Two more viewpoints join for one review when there is a clear signal:

- Retry, idempotency, races, duplicate handling, event order, or partial failure bring in Leslie Lamport (`lamport`).
- A profiler, benchmark, or measured latency, throughput, allocation, copying, I/O, or hot-path cost brings in John Carmack (`carmack`).

If both match, Lamport goes first because correctness comes before speed. A lone word such as `async`, `cache`, `performance`, or `latency` is not enough to switch viewpoints.

Each name stands for a conceptual lens and a set of attention areas. The nudge does not imitate that person's voice and does not add another code review; it uses visible technical facts only as anchors for reconsidering the workflow.

Whatever the stage, explicit destructive action, security or authorization risk, drift from the user's request, and completion claims contradicted by visible evidence still stop the line first.

The floating-window dropdown stores the stage in `~/.masters-nudge/data/config.json`. Your choice applies from the next review; Build is the default. The dropdown shows your chosen stage; the colored badge shows the viewpoint used for the latest nudge. A temporary Lamport or Carmack review changes the badge, not the dropdown. A pre-existing `~/.claude/buddy/config.json` remains readable until a new neutral config is saved.

New configuration files use `{"stage":"build"}`. Valid stages are `design`, `build`, `evolve`, and `review`. General workflow evidence and stop-the-line checks are the shared base for every stage, not a selectable filter.

`MASTERS_NUDGE_PERSONA` (or legacy `BUDDY_PERSONA`) set before the host starts remains a force override and disables specialist switching. Old persona-based config files remain readable: the four lifecycle lenses map to their stages, old General settings fall back to the default Build stage, and old Lamport/Carmack choices stay locked until a stage is selected in the window.

A lens changes which part of the workflow gets reconsidered first. It does not change the evidence rules, model-call count, single-Nudge limit, or length cap. Files under `personas/` append to `buddy-prompt.txt`. All six viewpoints share one model call; they are not six agents speaking at once.

<details>
<summary>Filter notes</summary>

##### Jeff Dean — systems causality and cost

> “As systems scale up, simply stamping out all sources of variability does not work.” — [Jeff Dean](https://research.google/pubs/achieving-rapid-response-times-in-large-online-services/)

Which real constraint caused each mechanism; cost through data flow, latency, state, failure handling, operations — without assuming Google scale.

##### Linus Torvalds — directness and ownership

> “Talk is cheap. Show me the code.” — [Linus Torvalds](https://groups.google.com/g/mlist.linux.kernel/c/pdl_7y9bPgk)

Decisions deferred through wrappers and indirection; whether the workflow still has one clear path and owner. Conceptual focus, not tone.

##### Martin Fowler — knowledge boundaries and safer change

> “…to make it easier to understand and cheaper to modify without changing its observable behavior.” — [Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)

What the current change reveals about where knowledge belongs and how expensive the next change will be; small, behavior-preserving steps over open-ended rewrites.

##### Kent Beck — feedback loops and small steps

> “You don’t always have to take tiny steps, but they are always an option.” — [Kent Beck](https://newsletter.kentbeck.com/p/first-one-then-many)

The shortest path from the current assumption to useful feedback; whether the work keeps growing after its stopping condition has been met.

##### Leslie Lamport — state, order, failure

> “A distributed system is one in which the failure of a computer you didn’t even know existed can render your own computer unusable.” — [Leslie Lamport](https://www.microsoft.com/en-us/research/publication/distribution/)

Assumptions about state and event order; whether retries, duplication, delay, or partial failure break the promised invariant.

##### John Carmack — path that actually runs

> “Sometimes, the elegant implementation is just a function. Not a method. Not a class. Not a framework. Just a function.” — [John Carmack](https://twitter.com/ID_AA_Carmack/status/53512300451201024)

What actually runs and what was actually measured; whether the chosen path removes work or merely rearranges it.

</details>

Host-aware defaults remove the need for a second login: Claude Code uses Anthropic and Codex uses OpenAI. Set `MASTERS_NUDGE_PROVIDER` when cross-vendor or local-only review is worth the extra setup. Either way, this is a separate reviewer invocation, not an accuracy claim.

## Configure

`MASTERS_NUDGE_*` is the preferred namespace. Every listed `BUDDY_*` name remains a compatibility alias for existing installations.

| Env var | Default | Effect |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` / `BUDDY_PROVIDER` | Claude: `anthropic`; Codex: `openai` | `openai` (`codex exec`), `anthropic` (`claude -p`), `grok`, or `ollama-local` |
| `MASTERS_NUDGE_MODEL` / `BUDDY_MODEL` | Claude: `sonnet`; Codex: `gpt-5.6-sol`; Grok: CLI default; local: required | Model name for the chosen provider |
| `MASTERS_NUDGE_OLLAMA_URL` / `BUDDY_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback-only Ollama base URL; used only by `ollama-local` |
| `MASTERS_NUDGE_TIMEOUT` / `BUDDY_TIMEOUT` | `60` | End-of-turn model-call timeout (seconds) |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` / `BUDDY_CHECKPOINT_TIMEOUT` | `15` | Max wait for a mid-turn review (seconds) |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | New logs, state, config, and content-free telemetry |
| `MASTERS_NUDGE_RUNTIME_DIR` | Plugin root; legacy: `~/.masters-nudge/runtime` | Override the prompt/schema/persona runtime directory |
| `MASTERS_NUDGE_PERSONA` / `BUDDY_PERSONA` | unset | Force `jeff`, `beck`, `fowler`, `linus`, `lamport`, or `carmack`; wins over the window and specialist routing |
| `MASTERS_NUDGE_SPRITE_PATH` / `BUDDY_SPRITE_PATH` | shipped spritesheet | Custom transparent spritesheet |
| `MASTERS_NUDGE_SHADOW_EVALUATION_DAYS` / `BUDDY_SHADOW_EVALUATION_DAYS` | `7` | Shadow cost-policy evaluation length |
| `MASTERS_NUDGE_SHADOW_TARGET_CALLS` / `BUDDY_SHADOW_TARGET_CALLS` | `300` | Sample-size target for that evaluation |
| `BUDDY_CLAUDE_DIR` | unset | Legacy compatibility override; when explicitly set, preserves old Claude data paths |

Review copy lives in the managed plugin runtime. Source installs use `~/.masters-nudge/runtime/buddy-prompt.txt`; the Claude compatibility copy remains under `~/.claude/scripts/buddy/`.

Environment variables override `~/.masters-nudge/data/reviewer.json`, which overrides the host-aware defaults. If the persistent reviewer file is malformed, reviews stop with a diagnostic rather than silently reverting to a cloud provider.

### Cost telemetry and shadow evaluation

First review after install opens a fixed 7-day shadow window: candidate skips are labeled only; every review still runs. First review on or after day seven writes `~/.masters-nudge/data/shadow-evaluation.md` and shows one notice. Below 300 calls → `insufficient_samples`. No silent extension; no automatic skip enablement.

Telemetry stores only usage fields the selected provider actually reports and Masters’ Nudge can parse. CLIs may define cache, reasoning tokens, and estimated cost differently, so these records are not a normalized cross-provider price comparison.

Each review appends content-free metadata to `~/.masters-nudge/data/review-telemetry.jsonl`, including host, turn, stage, primary lens, effective lens, specialist trigger, and route source. Reaction log entries keep `persona` as the effective lens and carry the same route metadata. Delete `shadow-evaluation.json`, `shadow-evaluation.md`, and `review-telemetry.jsonl` to start a fresh evaluation window.

## Privacy

With the default cloud providers, **conversation and tool-event data go to an external model provider.** With `ollama-local`, the same payload is sent only to the validated loopback Ollama server. Each end-of-turn review and each matching mid-turn review is a separate model call. A payload may include:

1. Latest user prompt (≤2000 chars; long text keeps head and tail with an explicit middle cut)
2. Mid-turn: triggering tool event (≤3000) and recent agent context (≤1200)
3. End of turn: last claim (≤2500) and current-turn tool results (≤2000; may include Read contents, command output, errors, diffs). Claude can fall back to a bounded transcript slice; Codex never parses its transcript and instead uses the bounded PostToolUse journal
4. Optional agentcam excerpts (combined ≤2000)
5. Up to 3 prior short reactions in the session (reduces repetition)
6. Review system prompt and optional persona file (instructions, not your project source as such)

Without an override, Claude Code forwards the evidence packet to Anthropic and Codex forwards it to OpenAI. Setting `MASTERS_NUDGE_PROVIDER` can switch either host; `grok` uses the signed-in Grok CLI with web search and agent tools explicitly disabled, but still sends the payload to xAI. Switching provider mid-session can resend earlier reactions to the new provider as recent context. `ollama-local` accepts only loopback HTTP, disables client proxies and redirects, requires Ollama to report cloud disabled before every generation, and rejects remote model metadata. Any failure produces no nudge and never falls back to another provider.

Reactions, task anchors, bounded tool journals, and the selected local model name are stored in plain text under `~/.masters-nudge/data/`. Existing `~/.claude/buddy/` logs and config remain readable but are not automatically moved or deleted. Local-only mode cannot audit the operating system or a malicious process impersonating Ollama; the user remains responsible for the local runtime and model license. Provider retention/training terms change, so check current policy when using cloud mode.

## Optional integrations

### agentcam

With [agentcam](https://github.com/shihchengwei-lab/agentcam), selected report sections (risk, changed files, exit codes, tests, verification) attach when present. Without it, review still runs on task anchor, claim, and tool evidence.

### Custom sprite

```bash
export BUDDY_SPRITE_PATH=/path/to/spritesheet.png
```

Missing file: window opens without animation.

The shipped Rook sheet uses two six-frame rows: quiet idle, then a short review
reaction. The quiet outer-window background follows the effective lens shown
by the badge; specialist takeovers change it for that review without changing
the saved lifecycle stage. Rook itself remains graphite black.

### Localization

Shipped prompt language is Traditional Chinese. For another language, update `buddy-prompt.txt`, the hook wrappers in `checkpoint.py`, `inject.py`, and `masters_nudge/codex_adapter.py` (search for `第三方觀察`), and optionally Chinese fixtures in `test_buddy.py`. Plumbing is language-neutral.

## Implementation notes

Codex normalizes hook payloads into prompt-submitted, tool-completed, and
turn-stopped events. The Claude compatibility hooks translate checkpoint tool
events and otherwise update turn state or construct the same `ReviewRequest`
contract directly. Both review paths enter `ReviewCore` without host-specific
pass-through callbacks.

The shared core owns lens routing, prompt composition, provider dispatch, the
36–42-character completion target / 52-character hard cap, structured-output
handling, recent-reaction context, reaction persistence, and telemetry. Host
adapters own native event parsing, evidence capture, turn journals, checkpoint
deduplication, and delivery state. Shared evidence helpers build a small labeled
packet rather than resending a full transcript. Output contract:
`reaction-schema.json`.

If a finding reaches the hard cap without terminal punctuation, the shared
sanitizer closes it at the preceding complete clause. The paid result is still
delivered; this fallback neither rejects it nor makes another reviewer call.

New runtime and data paths are host-neutral. Script paths still use `buddy.py`, `BUDDY_*`, and `~/.claude/buddy/` as a compatibility layer for existing installations; old data is read in place and never migrated or removed automatically. Product name is Masters’ Nudge.

| Component | Path |
|---|---|
| Install | Native plugin marketplaces; source installers remain for compatibility |
| Plugin package | `plugins/masters-nudge/`; generated runtime checked by `tools/build_plugin.py` |
| Legacy hook snippets | Claude `settings-snippet.json`; Codex `codex-hooks-snippet.json` |
| Shared core | `masters_nudge/core.py`, `contracts.py`, `providers.py` |
| Architecture | `docs/phase-c-architecture.md` |
| Codex adapter | `hook_entry.py`, `masters_nudge/codex_adapter.py` |
| Claude compatibility adapter | `checkpoint.py`, `buddy.py`, `inject.py` and shell wrappers |
| Evidence packets | `source_context.py` |
| Prompts / routing | `buddy-prompt.txt`, `personas/*.txt`, `lens_router.py` |
| Output contract | `reaction-schema.json` |
| Floating UI | `buddy_window.py`, `start_buddy_window.bat` |
| Tests | `python -m unittest discover -v` |
| Roadmap | `ROADMAP.md` |
| Historical notes | `BUDDY_FORENSICS_REPORT.md` |

Runtime:

| Path | Purpose |
|---|---|
| `~/.masters-nudge/data/<host>--<session_id>.log` | Reaction JSONL |
| `~/.masters-nudge/data/<host>--<session_id>.turn.json` | Task anchor and bounded tool journal |
| `~/.masters-nudge/data/<host>--<session_id>.delivery.json` | Inject read pointer |
| `~/.masters-nudge/data/config.json` | Lifecycle stage saved by the window |
| `~/.masters-nudge/data/<host>--<session_id>.checkpoints/` | Mid-turn dedup |
| `~/.masters-nudge/data/error.log` | Error log |
| `~/.claude/buddy/*` | Read-only legacy compatibility (unless `BUDDY_CLAUDE_DIR` explicitly selects legacy mode) |

## Known limitations

- Matching mid-turn review may pause the agent up to `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` / `BUDDY_CHECKPOINT_TIMEOUT` (default 15s).
- Test-failure heuristics can miss unusual runners; large-diff uses Git plus untracked text files, binaries excluded, once per session after ~80 lines.
- A terse follow-up such as “continue” replaces an earlier detailed prompt as the task anchor.
- Claude current-turn evidence can still depend on transcript write timing. Codex avoids that dependency by journaling each PostToolUse payload, bounded to 8,000 characters per turn.
- On the tested Windows Codex CLI 0.147.0 build, non-zero Bash results did not emit `PostToolUse`, despite current docs; those failures are absent from the journal and receive only Stop review. See the [live smoke result](evaluation/results/phase-c-codex-smoke-20260813/SMOKE_RESULT.md).
- That 0.147.0 build also skipped native `async: true` hooks, so the Codex Stop command uses a fast detached-worker shim. This can be retired after the minimum supported CLI demonstrably runs native async hooks.
- If the next prompt is submitted before end-of-turn review finishes, that reaction injects one turn later.
- No time cooldown; every end of turn calls a model. Cost-skip policy is shadow-only.
- Other hooks without a `MASTERS_NUDGE_ACTIVE` / `BUDDY_ACTIVE`-style guard can still loop with `claude` / `codex`.

## Origin

Hook and CLI patterns from [`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer); rewritten from prior Buddy/Cinder companion usage. Historical screenshots: `buddy_screenshot.png`, `cinder_screenshot.png`. Current companion: Rook, a raven shown against the effective review lens color.

## License

MIT
