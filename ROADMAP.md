# Roadmap

Items kept after first-pass scope cuts. Each entry has a "why kept" line (the
reason the trade-off wasn't a flat "no") and a "trigger to actually do it" line
(the signal that turns this from someday-maybe into a real ticket).

The point of this file is to keep ideas warm without bloating v1. If you're
reading this much later and an item still has no trigger reached, that's
evidence to delete it, not to do it.

## Current product directions

### 1. Generalization（通用化） — PLANNED

**Goal:** Keep the review engine, evidence policy, lenses, output schema,
telemetry, and floating UI reusable while host-specific code becomes a thin
adapter. A normalized review event should carry the task anchor, checkpoint
reason, bounded evidence, session identity, and repository context without
requiring the core to understand one host's hook JSON.

**Current boundary:** Claude Code is the only supported host. Its
`UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, and `Stop` payloads are
still interpreted directly by the current scripts. Do not advertise another
host until its adapter, installer, smoke test, and data-disclosure docs exist.

**Next slice:** Treat the current integration as the Claude Code adapter, then
extract the normalized event boundary only when a real second host or user
requires it. Plugin format packaging in item 2 is the first generalization
deliverable because installation friction is already concrete; speculative
multi-host abstractions are not.

### 2. Cost control（成本控制） — SHADOW EVALUATION

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

Concrete unshipped supporting items kept for a real trigger are **2. Plugin
format packaging** and **5. Reaction quality eval**. Everything else below is
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

## 2. Plugin format packaging (`plugin.json`) — first generalization deliverable

**Why kept:** Currently installed via shell script + manual `settings.json` edit.
Fine for personal use, awkward to share. Wrapping in Claude Code's plugin
manifest format would make `bash install.sh` → "click install in Claude Code"
possible.

**Trigger to do:** When sharing with at least one other person.

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
select when to review, not which model to use. The same configured provider and
engineering lens handle every checkpoint.

## 5. Reaction quality eval

**Why kept:** Currently no measurement of whether Masters’ Nudge reactions are good.
Could borrow `cold-eyes-reviewer`'s eval framework — case fixtures + score cards.
The cost shadow telemetry in item 10 measures call outcomes and possible skip
conditions; it does not establish that a finding is correct or useful.

**Trigger to do:** When you suspect the Masters’ Nudge prompt has drifted, or you've
changed an engineering lens and want to compare versions A vs B.

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

`buddy_window.py` now includes the animated Masters’ Nudge engineering
checkpoint bell alongside the speech bubble. The 2x6 transparent spritesheet is
auto-detected, draggable, always on top, runs at 4fps, and follows the active
session. Legacy `BUDDY_SPRITE_PATH` overrides remain compatible.

## 9. Runtime lens selector — ✅ SHIPPED 2026-08-11

The floating window now offers General plus all six master lenses without
requiring CLI use. It writes the selected persona key to
`~/.claude/buddy/config.json`; Stop and checkpoint reviews resolve that file on
every call, so the next review uses the new lens without restarting Claude
Code. `BUDDY_PERSONA` remains an advanced environment-variable override.

Dropdown choices and reaction badges append a short Traditional Chinese focus
description after each master name, such as
`Linus Torvalds lens（簡化與責任歸屬）`. Existing persona keys and old log entries
remain compatible.

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

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Automatic per-event lens switching** — manual runtime selection is shipped,
  but tool events and checkpoint reasons do not change the lens automatically.
  A user's chosen engineering viewpoint remains stable until the user changes it.
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
