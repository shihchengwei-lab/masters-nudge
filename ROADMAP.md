# Roadmap

Items kept after first-pass scope cuts. Each entry has a "why kept" line (the
reason the trade-off wasn't a flat "no") and a "trigger to actually do it" line
(the signal that turns this from someday-maybe into a real ticket).

The point of this file is to keep ideas warm without bloating v1. If you're
reading this much later and an item still has no trigger reached, that's
evidence to delete it, not to do it.

## 1. Floating window UI (closest to original Buddy feel) — ✅ SHIPPED 2026-05-09

`buddy_window.py` + `start_buddy_window.bat`. Single-file Tk app, watches
`~/.claude/buddy/` and tails the most-recently-modified per-session log file.
Pinned to bottom-right, always on top. Switches automatically when a different
session's log gets newer activity.

Hook delivery to user UI works via `UserPromptSubmit hook success:`
system-reminder messages — both user and main Claude can see Buddy's reactions
in the transcript. The floating window is an additional, unmediated visibility
channel.

## 2. Plugin format packaging (`plugin.json`)

**Why kept:** Currently installed via shell script + manual `settings.json` edit.
Fine for personal use, awkward to share. Wrapping in Claude Code's plugin
manifest format would make `bash install.sh` → "click install in Claude Code"
possible.

**Trigger to do:** When sharing with at least one other person.

## 3. Trigger throttling / smart gating

**Why kept:** Every Stop fires a GPT-5.5 call via Codex CLI（or Claude CLI if
`BUDDY_PROVIDER=anthropic`）. Both sides are subscription-based, so direct
token cost is zero under current plans. The only real cost is noise — if
Buddy's reactions on trivial turns start getting skipped over, throttling
would help. Future options: rate limit (one reaction per N minutes), or only
trigger on certain shapes (errors, long turns, tool calls that failed).

**Trigger to do:** When you start skipping over Buddy's injected blocks
because they're too frequent or too generic.

## 4. Multi-model switching — ✅ SHIPPED (cross-vendor)

`BUDDY_PROVIDER` env var routes between Anthropic (`claude -p`) and OpenAI
(`codex exec`). Default is `openai` with `gpt-5.5` so the buddy view is
independent from the main agent's Anthropic Sonnet — different blind spots.

Smart routing (different models per turn type) was evaluated and cut —
reason-based model routing adds complexity without clear benefit. The trigger
signal (turn/error/test-fail) is scene context for the model, not a routing
decision.

## 5. Reaction quality eval

**Why kept:** Currently no measurement of whether Buddy's reactions are good.
Could borrow `cold-eyes-reviewer`'s eval framework — case fixtures + score cards.

**Trigger to do:** When you suspect the Buddy prompt has drifted, or you've
changed the personality and want to compare versions A vs B.

## 6. Background mode — ✅ SHIPPED 2026-05-09

Uses Claude Code's native `async: true` hook setting. `buddy.sh` runs
synchronously; background execution is managed by the framework. Timeout and
lifecycle are handled by Claude Code, not shell-level forking.

## 8. Pet-style UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` now includes animated Cinder sprite (auto-detected from
`~/.codex/pets/cinder/spritesheet.webp`) alongside the speech bubble.
Draggable, always-on-top, 4fps animation, auto-follows active session.

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Multi-personality switching** — only Buddy is wanted; switching dilutes the
  project's identity.
- **Cross-session memory** — buddy doesn't need to remember things across days;
  one-turn reactions are enough.
- **Personality CLI** — editing `buddy-prompt.txt` directly is fine; a CLI
  layer adds surface area for no real benefit.
- **buddy.log dashboard** — JSONL 可以直接看，trigger 沒到過，log 量不大。
- **Smart model routing** — reason-based 路由被明確拒絕，trigger 是場景上下文不是路由信號。
