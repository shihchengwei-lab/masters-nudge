# Roadmap

Items kept after first-pass scope cuts. Each entry has a "why kept" line (the
reason the trade-off wasn't a flat "no") and a "trigger to actually do it" line
(the signal that turns this from someday-maybe into a real ticket).

The point of this file is to keep ideas warm without bloating v1. If you're
reading this much later and an item still has no trigger reached, that's
evidence to delete it, not to do it.

## 1. Floating window UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` + `start_buddy_window.bat`. Single-file Tk app, watches
`~/.claude/buddy/` and tails the most-recently-modified per-session log file.
Pinned to bottom-right, always on top. Switches automatically when a different
session's log gets newer activity.

Hook delivery works via `UserPromptSubmit hook success:` system-reminder
messages — main Claude sees the injected reaction in its context, but
system-reminders don't render in the user's terminal. The floating window
is the user's only direct visibility channel.

## 2. Plugin format packaging (`plugin.json`)

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

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Runtime lens UI/automatic switching** — six optional environment-selected
  engineering lenses are shipped, but no menu or automatic per-event switching
  is planned.
- **Cross-session memory** — Masters’ Nudge doesn't need to remember things across days;
  one-turn reactions are enough.
- **Lens-selection CLI** — editing `buddy-prompt.txt` directly is fine; a CLI
  layer adds surface area for no real benefit.
- **buddy.log dashboard** — JSONL 可以直接看，trigger 沒到過，log 量不大。
- **Smart model routing** — reason-based 路由被明確拒絕，trigger 是場景上下文不是路由信號。
- **Live Claude Code integration tests** — unit tests cover checkpoint payload
  classification, settings registration, deduplication, and output shape. A real
  Claude Code session, provider latency, shell-wrapper startup, and Tk startup
  remain manual checks rather than CI requirements.
