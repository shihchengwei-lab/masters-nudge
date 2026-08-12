# Roadmap

Items kept after first-pass scope cuts. Each entry has a "why kept" line (the
reason the trade-off wasn't a flat "no") and a "trigger to actually do it" line
(the signal that turns this from someday-maybe into a real ticket).

The point of this file is to keep ideas warm without bloating v1. If you're
reading this much later and an item still has no trigger reached, that's
evidence to delete it, not to do it.

## Current product directions

### 1. Reaction quality and impact evaluation（短評品質與後續影響） — NEXT, IN TWO PHASES

**Goal:** First establish that a finding is reliable, then test whether injecting
it changes the main agent's work for the better. A good-sounding reaction is not
the product outcome; the intended outcome is a better decision by the combined
user-and-agent workflow.

**Why now:** Lifecycle lens routing changed what the reviewer looks for, so the
trigger in item 5 has been reached. Cost telemetry only counts call outcomes; it
cannot tell whether a finding was correct or whether a lens improved the review.

**Phase A — reaction quality:** Build labeled evidence packets covering the
internal no-overlay baseline, the four lifecycle stages, both specialist
takeovers, and cases that should stay silent. Prefer packets with an objective
oracle: a seeded defect, a known unsupported claim, an explicit scope conflict,
or a verified no-finding case. Check schema compliance, evidence grounding,
issue identification, and correct silence automatically. Use blind rubric-based
human adjudication only when more than one finding could legitimately be useful;
record disagreement instead of hiding it in one average score. Compare the
internal baseline with the intended lens under the same model and prompt budget.
The baseline is not a user-selectable mode.

**Phase B — reaction impact:** Start only after Phase A reaches a declared
quality floor. Run matched tasks from the same repository state with Nudge
injected in one condition and withheld in the other, keeping the main model,
task, tool budget, and acceptance criteria fixed. Repeat runs rather than
treating one stochastic trajectory as proof. Primary outcomes should be
checkable: hidden tests, removal of a seeded defect, satisfaction of explicit
requirements, absence of regressions, and evidence supporting the final claim.
Turns, latency, and diff size are secondary diagnostics, not standalone quality
scores. Blind human review is reserved for design decisions that have no honest
executable oracle.

Do not count the agent acknowledging a Nudge, an evaluator model preferring its
wording, or production telemetry correlations as proof of impact. Until Phase B
shows a repeatable difference, describe Masters' Nudge as increasing the chance
of noticing a different problem, not as proven to improve task outcomes.

### 2. Generalization（通用化） — PLANNED AFTER THE EVALUATION BASELINE

**Goal:** Keep the review engine, evidence policy, lenses, output schema,
telemetry, and floating UI reusable while host-specific code becomes a thin
adapter. A normalized review event should carry the task anchor, checkpoint
reason, bounded evidence, session identity, and repository context without
requiring the core to understand one host's hook JSON.

**Current boundary:** Claude Code is the only supported host. Its
`UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, and `Stop` payloads are
still interpreted directly by the current scripts. Do not advertise another
host until its adapter, installer, smoke test, and data-disclosure docs exist.

**Sequence:** First preserve today's behavior with the Phase A quality baseline
and run a small Phase B impact study. Then treat the current integration as the
Claude Code adapter and separate it from a shared reviewer core. Validate that
boundary with one real second agent instead of designing a universal event
format from imagined integrations.

### 3. Local reviewer evaluation（本地審查模型評估） — AFTER SHARED CORE

**Goal:** Evaluate whether a local model can produce useful, evidence-backed
findings with reliable silence and schema compliance at acceptable latency.

**Dependency:** Do this only after the shared reviewer core exposes a clean
provider boundary. Reuse the reaction quality fixtures to compare local and
cloud reviewers under the same evidence packets and scoring rules.

**Current boundary:** No local provider is promised. Model size, speed, and
quality are measurements to collect, not assumptions; selecting a lifecycle
lens is already handled by deterministic local rules and is not the model's job.

### 4. Cost control（成本控制） — SHADOW EVALUATION

**Goal:** Reduce review spend without lowering the finding quality floor.
Item 10 already records call outcomes, token/cache metadata, and candidate skip
conditions for a fixed seven-day window with a 300-call target.

**Decision rule:** Any candidate call that produces a finding is a
`shadow_fail`. Errors and insufficient samples cannot justify activation.
After the report exists, consider only narrow, reversible gating backed by that
evidence. Prompt/context reduction or a cheaper model also requires the reaction
quality eval in item 5; lower token count alone is not proof of preserved quality.

**Current boundary:** Live gating remains off. The shadow window never extends
or enables skipping automatically, and no model downgrade is scheduled.

Concrete unshipped items below are **2. Plugin format packaging**, **5. Reaction
quality and impact eval**, and **11. Local reviewer evaluation**. Item 5 Phase A
is next, followed by its small Phase B study; item 2 waits for a real sharing
need, and item 11 waits for the shared reviewer core. Everything else below is
either shipped or explicitly cut from scope.

## 1. Floating window UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` + `start_buddy_window.bat`. Single-file Tk app, watches
`~/.claude/buddy/` and tails the most-recently-modified per-session log file.
Pinned to bottom-right, always on top. Switches automatically when a different
session's log gets newer activity.

Hook delivery works via `UserPromptSubmit hook success:` system-reminder
messages — main Claude sees the injected reaction in its context, but
system-reminders don't render in the user's terminal. The floating window
is the user's only direct visibility channel. Runtime lens selection and
beginner-friendly focus labels were added later under item 9.

## 2. Plugin format packaging (`plugin.json`) — installation improvement

**Why kept:** Currently installed via shell script + manual `settings.json` edit.
Fine for personal use, awkward to share. Wrapping in Claude Code's plugin
manifest format would make `bash install.sh` → "click install in Claude Code"
possible.

**Trigger to do:** When sharing with at least one other person.

This improves Claude Code installation only. It does not extract the shared
reviewer core, add another host, or add another model provider.

## 3. Mid-work checkpoint gating — ✅ SHIPPED 2026-08-11

`checkpoint.py` + `checkpoint.sh` add synchronous, non-blocking Masters’ Nudge reviews inside a
long agentic turn. The local classifier calls the reviewer only for tool errors, test
failures, or the first working-tree total above 80 changed lines. Exact repeats
are deduplicated per session. There is deliberately no time cooldown.

Checkpoint reactions return directly to the main agent through
`additionalContext`; they are not written to the user-facing floating-window
log. The existing asynchronous Stop path remains as supplementary review.

## 4. Multi-model switching — ✅ SHIPPED (cross-vendor)

`BUDDY_PROVIDER` env var routes between Anthropic (`claude -p`) and OpenAI
(`codex exec`). Default is `openai` with `gpt-5.6-sol` so the side-review view is
independent from the main agent's Anthropic Sonnet — different blind spots.

Smart routing (different models per turn type) remains cut: checkpoint reasons
select when to review, not which model to use. The configured provider remains
stable while the lifecycle router selects the engineering lens.

## 5. Reaction quality and impact eval — NEXT, IN TWO PHASES

**Why kept:** Currently no measurement of whether Masters’ Nudge reactions are
reliable or whether the main agent makes a better decision after receiving one.
Could borrow `cold-eyes-reviewer`'s case-fixture structure, but subjective score
cards must not be the primary evidence. The cost shadow telemetry in item 10
measures call outcomes and possible skip conditions; it establishes neither
reaction correctness nor downstream impact.

**Trigger reached:** Lifecycle lens routing changed the engineering lenses on
2026-08-12. Build the baseline before refactoring the core or evaluating a
different reviewer model.

**Phase A — quality:** Use fixed, labeled evidence packets with known issues or
verified no-finding cases. Automatically check schema compliance, grounding,
issue match, and correct silence. Compare the internal no-overlay baseline with
the intended lens while keeping the reviewer model, prompt budget, and output
contract fixed. Blind human adjudication handles only cases with multiple
defensible findings and reports inter-rater disagreement. The baseline is not
exposed as a product mode.

**Phase B — impact:** For reactions that pass the quality floor, run paired
agent tasks from identical starting states with injection enabled or withheld.
Use hidden tests, seeded issues, explicit acceptance checks, regression checks,
and support for the final completion claim as primary outcomes. Hold the main
model and task budget constant, randomize or alternate condition order, and run
enough repeats to report a distribution rather than a showcase. Use blind human
review only where no executable oracle can represent the design trade-off.

**Claim boundary:** Agent acknowledgement, evaluator-model preference, fewer
turns, smaller diffs, or observational production telemetry cannot by themselves
show that Nudge improved the result. Product claims remain conservative until a
repeatable controlled difference is observed.

## 6. Background mode — ✅ SHIPPED 2026-05-09

Uses Claude Code's native `async: true` hook setting. `buddy.sh` runs
synchronously; background execution is managed by the framework. Timeout and
lifecycle are handled by Claude Code, not shell-level forking.

## 7. Event-centered source evidence packets — ✅ SHIPPED 2026-08-11

`source_context.py` gives Stop and checkpoint reviews the same lens-neutral
source-selection layer. `UserPromptSubmit` stores a bounded task anchor and the
prompt-time transcript byte offset. Checkpoints receive the anchor, triggering
event, and small recent-agent context; Stop receives the anchor, direct final
claim, current-turn tool evidence, and named agentcam evidence sections.

Long fields keep their head and tail with an explicit middle-cut marker. The old
6000-character rolling transcript remains only as a Stop fallback when no
final-claim, tool, or agentcam evidence is available.

## 8. Pet-style UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` now includes Rook, an animated raven companion, alongside the
speech bubble. The 2x6 transparent spritesheet provides idle and review rows,
is draggable, always on top, runs at 4fps, and follows the active session.
The outer-window background follows the effective lens while Rook remains
graphite black. Legacy `BUDDY_SPRITE_PATH` overrides remain compatible.

## 9. Lifecycle lens routing — ✅ SHIPPED 2026-08-12

The floating window offers Design, Build, Evolve, and Review stages. These map
to Jeff Dean, Kent Beck, Martin Fowler, and Linus Torvalds. Build is the default;
General remains the shared evidence and high-risk review base rather than a
selectable stage. Stop and checkpoint reviews use the same local, deterministic
router without an extra model call.

High-confidence state/ordering evidence temporarily selects Leslie Lamport;
measured execution-cost evidence temporarily selects John Carmack. A temporary
specialist does not change the saved stage, and Lamport wins a simultaneous
match. Reaction logs and telemetry record the primary and effective lens,
trigger, stage, and route source. `BUDDY_PERSONA`, existing persona configs, and
old log entries remain compatible.

## 10. Bounded cost shadow evaluation — ✅ SHIPPED 2026-08-11 (enforcement off)

`review_telemetry.py` records content-free metadata for Stop and checkpoint
model calls, including outcome status, latency, source fingerprint, and token /
cache usage when the CLI exposes it. It does not store prompts, transcripts,
tool results, or finding text.

The first review starts a fixed seven-day shadow window with a 300-call target.
Potential `no_new_evidence` and `checkpoint_stop_overlap` skips are observed
only; every review still runs. Any candidate call that produces a finding is a
`shadow_fail`. At the deadline, the next review writes
`shadow-evaluation.md` and emits one notice, even when the sample is
insufficient. The evaluation never silently extends and never enables skipping automatically.

**Next decision:** Review the generated report manually. Live cost gating needs
explicit approval after the evidence window; it is not a current implementation
task merely because telemetry is present.

## 11. Local reviewer evaluation — AFTER SHARED CORE

**Why kept:** A local reviewer could avoid a second cloud egress and may reduce
per-call cost and latency. Those benefits matter only if review quality remains
useful.

**Prerequisite:** Extract the shared reviewer core and provider boundary, then
reuse item 5's fixtures and score card. Do not add an Ollama-compatible or other
local provider directly to the current Claude-specific path first.

**Promotion gate:** A candidate must meet an explicit quality floor for correct
findings, correct silence, schema compliance, and latency. Do not promise that a
particular parameter count or hardware setup will pass before measuring it.

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Cross-session memory** — Masters’ Nudge doesn't need to remember things across days;
  one-turn reactions are enough.
- **Lens-selection CLI** — the floating-window selector covers normal use; a
  separate CLI layer adds surface area for no real benefit.
- **buddy.log dashboard** — JSONL 可以直接看，trigger 沒到過，log 量不大。
- **Smart model routing** — reason-based 路由被明確拒絕，trigger 是場景上下文不是路由信號。
- **Live Claude Code integration tests** — unit tests cover checkpoint payload
  classification, settings registration, deduplication, and output shape. A real
  Claude Code session, provider latency, shell-wrapper startup, and Tk startup
  remain manual checks rather than CI requirements.
- **Built-in custom lens/rule management** — this is an open-source prompt-based
  tool. Users who need different rules can edit or fork `buddy-prompt.txt` and
  `personas/*.txt`; a loader, marketplace, merge policy, and management UI would
  add product surface without improving the core review loop.
