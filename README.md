# Masters’ Nudge

[繁體中文](README.zh-TW.md) | English

**Add a different voice to long-running Claude Code tasks.**

## Overview

The longer Claude Code works, the more its early choices shape everything that follows.

When the direction is right, this builds momentum. When it is wrong, Claude may keep patching and working around the same idea until the task looks finished but still carries a problem nobody stopped to question.

At a few key moments, Masters’ Nudge asks another model to look at a small piece of the latest work and leave the single most useful warning. If it finds no clear problem, it stays quiet.

Claude Code still does the work and makes the decisions. Masters’ Nudge simply adds a different voice beside it.

## Why only one line?

Each nudge is at most 52 characters and points to one concrete problem.

It may flag a wrong direction, growing scope, needless complexity, or a claim of completion that the evidence does not support.

The point is not to produce another full answer. It is to give the same work one brief look from another angle before Claude continues.

## Why another model?

When the same model reviews its own work, it can carry the same assumptions into the review.

By default, Anthropic's Claude Code does the work while an OpenAI model checks it. A different model creates another chance to notice a different problem.

The reviewer receives only a small packet of current evidence and must base its warning on that material. If the evidence does not support a clear finding, it says nothing.

## When does it join in?

```
Claude Code works normally
    │ tool failure / test failure / first large change
    ├─► check once → Claude only
    │
    │ turn ends
    └─► check once in the background
              ├─ give it to Claude on your next message
              └─ show it in the floating window
```

| Moment | Why look again? | Who sees it? |
|---|---|---|
| Tool failure | The fix may address only the surface symptom | Claude Code |
| Test failure | The repair may be taking a longer route around the problem | Claude Code |
| First change over ~80 lines | The task may be growing beyond its original scope | Claude Code |
| End of turn | Check whether the work is actually complete | Claude Code and the floating window |

Mid-turn checks call the model only for the first three cases and may pause Claude Code for up to about 15 seconds. End-of-turn checks run in the background and do not block the completed turn.

Claude receives an end-of-turn nudge when you send your next message. Claude Code does not display these system reminders in the terminal; the floating window is where you can read them directly.

Output is either one finding or silence. Findings are stripped of markdown and filler, with a hard limit of 52 characters.

## Who this is for

**Suitable** if you use Claude Code and accept that review content (your prompt, tool output, file snippets, errors, etc.) leaves the machine for an external model API (**OpenAI by default**; Anthropic optional).

**Not suitable** where conversation or code must not leave the machine. Details: [Privacy](#privacy). Do not install if that is a hard constraint.

Cost: by default **every completed turn** calls the review model once; mid-turn calls only on error / test failure / first large change. Busy days accumulate tokens.

## Install

### Prerequisites

- Working Claude Code
- Default path: [Codex CLI](https://github.com/openai/codex) installed and able to authenticate/run  
  (or `BUDDY_PROVIDER=anthropic` and `claude -p`)
- `bash` (native on macOS/Linux; on Windows use Git Bash or WSL for the install script)

### Steps

1. Copy scripts (does not touch settings):

```bash
bash install.sh
```

Target: `~/.claude/scripts/buddy/`.

2. Open `~/.claude/settings.json` and **merge** the `hooks` from [`settings-snippet.json`](settings-snippet.json): keep your existing hooks; add the snippet’s `PostToolUse`, `PostToolUseFailure`, `Stop`, and `UserPromptSubmit` entries alongside them. Do not replace the whole file. The snippet’s `_comment` field says the same.

3. (Optional) Floating window — otherwise you almost never see end-of-turn lines in the UI:

```bash
pip install Pillow
```

- **Windows:** double-click `~/.claude/scripts/buddy/start_buddy_window.bat`
- **macOS / Linux:** `python3 ~/.claude/scripts/buddy/buddy_window.py &`

Closing the window does not disable hooks.

### Verify

- Force a failing test in Claude Code, or accumulate more than ~80 changed lines and finish a turn: a mid-turn hit may add a few seconds of wait; after a turn ends you should see `~/.claude/buddy/<session_id>.log`.
- Script errors: `~/.claude/buddy-error.log`.
- No log at all: hooks usually not merged, or the Codex / `BUDDY_PROVIDER` call is failing.

## Filters: different stages, different questions

Different parts of a project make different problems easy to miss.

During design, data, state, and ownership matter most. During implementation, scope can quietly grow. As the code evolves, today's structure can make tomorrow's change harder. Before delivery, it is worth asking which layers never needed to exist.

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

Each name stands for a set of engineering concerns. The nudge does not imitate that person's voice; it stays direct and specific.

Whatever the stage, clear errors, unsupported claims, work that has drifted from the request, and delivery gaps always come first.

The floating-window dropdown stores the stage in `~/.claude/buddy/config.json`. Your choice applies from the next review; Build is the default. The dropdown shows your chosen stage; the colored badge shows the viewpoint used for the latest nudge. A temporary Lamport or Carmack review changes the badge, not the dropdown.

New configuration files use `{"stage":"build"}`. Valid stages are `design`, `build`, `evolve`, and `review`. General evidence and high-risk checks are the shared base for every stage, not a selectable filter.

`BUDDY_PERSONA` set before Claude Code starts remains a force override and disables specialist switching. Old persona-based config files remain readable: the four lifecycle lenses map to their stages, old General settings fall back to the default Build stage, and old Lamport/Carmack choices stay locked until a stage is selected in the window.

A lens changes which kind of problem gets checked first. It does not change the evidence rules, model-call count, single-finding limit, or length cap. Files under `personas/` append to `buddy-prompt.txt`. All six viewpoints share one review; they are not six agents speaking at once.

<details>
<summary>Filter notes</summary>

##### Jeff Dean — systems causality and cost

> “As systems scale up, simply stamping out all sources of variability does not work.” — [Jeff Dean](https://research.google/pubs/achieving-rapid-response-times-in-large-online-services/)

Which real constraint caused each mechanism; cost through data flow, latency, state, failure handling, operations — without assuming Google scale.

##### Linus Torvalds — direct code and ownership

> “Talk is cheap. Show me the code.” — [Linus Torvalds](https://groups.google.com/g/mlist.linux.kernel/c/pdl_7y9bPgk)

Wrappers and indirection that hide behavior or ownership. Inspection focus, not tone.

##### Martin Fowler — safer evolution of design

> “…to make it easier to understand and cheaper to modify without changing its observable behavior.” — [Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)

Structures that make the next change too expensive; small, behavior-preserving fixes over needless rewrites.

##### Kent Beck — small, testable steps

> “You don’t always have to take tiny steps, but they are always an option.” — [Kent Beck](https://newsletter.kentbeck.com/p/first-one-then-many)

Current requirement and useful feedback; whether implementation keeps growing after the need is met.

##### Leslie Lamport — state, order, failure

> “A distributed system is one in which the failure of a computer you didn’t even know existed can render your own computer unusable.” — [Leslie Lamport](https://www.microsoft.com/en-us/research/publication/distribution/)

Hidden state and event order; retries, duplication, delay, partial failure.

##### John Carmack — path that actually runs

> “Sometimes, the elegant implementation is just a function. Not a method. Not a class. Not a framework. Just a function.” — [John Carmack](https://twitter.com/ID_AA_Carmack/status/53512300451201024)

Control flow and data movement; measurement before optimization claims; work that does not change results.

</details>

Default OpenAI is intentional: different vendor family from the Anthropic main agent. Design choice, not an accuracy claim.

## Configure

| Env var | Default | Effect |
|---|---|---|
| `BUDDY_PROVIDER` | `openai` | `openai` (`codex exec`) or `anthropic` (`claude -p`) |
| `BUDDY_MODEL` | `gpt-5.6-sol` / `sonnet` | Model name for the chosen CLI |
| `BUDDY_TIMEOUT` | `60` | End-of-turn model-call timeout (seconds) |
| `BUDDY_CHECKPOINT_TIMEOUT` | `15` | Max wait for a mid-turn review (seconds) |
| `BUDDY_CLAUDE_DIR` | `~/.claude` | Logs and state |
| `BUDDY_PERSONA` | unset | Force `jeff`, `beck`, `fowler`, `linus`, `lamport`, or `carmack`; wins over the window and specialist routing |
| `BUDDY_SPRITE_PATH` | shipped spritesheet | Custom transparent spritesheet |
| `BUDDY_SHADOW_EVALUATION_DAYS` | `7` | Shadow cost-policy evaluation length |
| `BUDDY_SHADOW_TARGET_CALLS` | `300` | Sample-size target for that evaluation |

Review copy: `~/.claude/scripts/buddy/buddy-prompt.txt`.

### Cost telemetry and shadow evaluation

First review after install opens a fixed 7-day shadow window: candidate skips are labeled only; every review still runs. First review on or after day seven writes `~/.claude/buddy/shadow-evaluation.md` and shows one notice. Below 300 calls → `insufficient_samples`. No silent extension; no automatic skip enablement.

Each review appends content-free metadata to `~/.claude/buddy/review-telemetry.jsonl`, including stage, primary lens, effective lens, specialist trigger, and route source. Reaction log entries keep `persona` as the effective lens and carry the same route metadata. Delete `shadow-evaluation.json`, `shadow-evaluation.md`, and `review-telemetry.jsonl` to start a fresh evaluation window.

## Privacy

**Conversation and tool-event data go to an external model provider.** Each end-of-turn review and each matching mid-turn review is a separate egress. A payload may include:

1. Latest user prompt (≤2000 chars; long text keeps head and tail with an explicit middle cut)
2. Mid-turn: triggering tool event (≤3000) and recent agent context (≤1200)
3. End of turn: last claim (≤2500) and current-turn tool results (≤2000; may include Read contents, command output, errors, diffs). Fallback: longer transcript slice when better evidence is missing
4. Optional agentcam excerpts (combined ≤2000)
5. Up to 3 prior short reactions in the session (reduces repetition)
6. Review system prompt and optional persona file (instructions, not your project source as such)

Default `BUDDY_PROVIDER=openai` forwards content related to an Anthropic main agent to OpenAI. Switching provider mid-session can resend earlier reactions to the new vendor as recent context. Reactions and task anchors are also stored in plain text under `~/.claude/buddy/`.

If even same-vendor egress is unacceptable, do not enable. Provider retention/training terms change; check current API policy.

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

Shipped prompt language is Traditional Chinese. For another language, update `buddy-prompt.txt`, the hard-coded wrapper in `inject.py` (search for `第三方第二意見`), and optionally Chinese fixtures in `test_buddy.py`. Plumbing is language-neutral.

## Implementation notes

Hooks build a small labeled evidence packet rather than resending a full transcript. Submitting a prompt stores a task anchor and transcript offset; mid-turn adds the event; end of turn adds final claim and current-turn tool results. Contract: `reaction-schema.json`.

Script paths still use `buddy.py`, `BUDDY_*`, and `~/.claude/buddy/` for install compatibility. Product name is Masters’ Nudge.

| Component | Path |
|---|---|
| Install | `install.sh` → `~/.claude/scripts/buddy/` |
| Hook snippet | `settings-snippet.json` |
| Mid-turn | `checkpoint.sh` / `checkpoint.py` |
| End of turn | `buddy.sh` / `buddy.py` |
| Inject | `inject.sh` / `inject.py` |
| Evidence packets | `source_context.py` |
| Prompts / routing | `buddy-prompt.txt`, `personas/*.txt`, `lens_router.py` |
| Output contract | `reaction-schema.json` |
| Floating UI | `buddy_window.py`, `start_buddy_window.bat` |
| Tests | `python -m unittest test_buddy -v` |
| Roadmap | `ROADMAP.md` |
| Historical notes | `BUDDY_FORENSICS_REPORT.md` |

Runtime:

| Path | Purpose |
|---|---|
| `~/.claude/buddy/<session_id>.log` | Reaction JSONL |
| `~/.claude/buddy/<session_id>.state.json` | Inject read pointer |
| `~/.claude/buddy/<session_id>.source.json` | Task anchor and transcript offset |
| `~/.claude/buddy/config.json` | Lifecycle stage saved by the window |
| `~/.claude/buddy/<session_id>.checkpoints/` | Mid-turn dedup |
| `~/.claude/buddy-error.log` | Error log |

## Known limitations

- Matching mid-turn review may pause the agent up to `BUDDY_CHECKPOINT_TIMEOUT` (default 15s).
- Test-failure heuristics can miss unusual runners; large-diff uses Git plus untracked text files, binaries excluded, once per session after ~80 lines.
- A terse follow-up such as “continue” replaces an earlier detailed prompt as the task anchor.
- Current-turn tool evidence depends on transcript write timing; delayed writes can leave gaps.
- If the next prompt is submitted before end-of-turn review finishes, that reaction injects one turn later.
- No time cooldown; every end of turn calls a model. Cost-skip policy is shadow-only.
- Other hooks without a `BUDDY_ACTIVE`-style guard can still loop with `claude` / `codex`.

## Origin

Hook and CLI patterns from [`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer); rewritten from prior Buddy/Cinder companion usage. Historical screenshots: `buddy_screenshot.png`, `cinder_screenshot.png`. Current companion: Rook, a raven shown against the effective review lens color.

## License

MIT
