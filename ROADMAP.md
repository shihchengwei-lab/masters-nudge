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

Hook delivery to user UI was confirmed broken (CC docs mismatch — both plain
stdout and JSON `additionalContext` fail to render in the user-visible
transcript on this CC version). The floating window is the actual user-side
visibility channel.

## 2. Plugin format packaging (`plugin.json`)

**Why kept:** Currently installed via shell script + manual `settings.json` edit.
Fine for personal use, awkward to share. Wrapping in Claude Code's plugin
manifest format would make `bash install.sh` → "click install in Claude Code"
possible.

**Trigger to do:** When sharing with at least one other person.

## 3. Trigger throttling / smart gating

**Why kept:** Right now every Stop fires a Sonnet 4.6 call. Token cost adds up;
reactions on trivial turns are noise. Future: rate limit (one reaction per N
minutes), or only trigger on certain shapes (errors, long turns, user expressed
confusion, tool calls that failed).

**Trigger to do:** When token cost or noise rate becomes annoying enough to
measure. The first symptom is usually skipping over Buddy's injected blocks
because they're too frequent or too generic.

## 4. Multi-model switching — ✅ PARTIAL (cross-vendor, not cross-tier)

`BUDDY_PROVIDER` env var routes between Anthropic (`claude -p`) and OpenAI
(`codex exec`). Default is `openai` with `gpt-5.5` so the buddy view is
independent from the main agent's Anthropic Sonnet — different blind spots.

Still pending if it ever matters: smart routing (Haiku for routine turns, Opus
for hard turns), or fallback chain when one provider is rate-limited.

**Trigger to do remaining work:** When you actually want differentiated
quality/cost per turn type, not just per-vendor independence.

## 5. Reaction quality eval

**Why kept:** Currently no measurement of whether Buddy's reactions are good.
Could borrow `cold-eyes-reviewer`'s eval framework — case fixtures + score cards.

**Trigger to do:** When you suspect the Buddy prompt has drifted, or you've
changed the personality and want to compare versions A vs B.

## 6. Background mode — ✅ SHIPPED 2026-05-09

`buddy.sh` now fires `buddy.py` in a detached subshell and exits immediately.
Zero perceived Stop-hook latency. Race tradeoff (described above) is real but
rare in practice — typing thinking time is usually longer than buddy's
generation time.

## 7. Shared buddy.log dashboard

**Why kept:** `buddy.log` is JSONL — easy to parse but you have to open it
manually. A small tool that summarizes hit rate, common reaction types,
sessions where Buddy said something useful vs. filler.

**Trigger to do:** When you want to know "is this thing actually adding value
over the past month".

## 8. Pet-style UI (level-up from the text-tail window)

**Why kept:** The current `buddy_window.py` is the minimum viable visibility
channel — it's a Tk text window that tails the JSONL. Codex CLI ships with a
pet system (pixel-art character + timestamped reaction list, customizable
appearance) and that style of UI is a meaningful upgrade over plain text —
adds presence, makes Buddy feel like a thing that exists alongside the work,
not a log.

**Trigger to do:** When the text window starts feeling like a logging sidebar
instead of a companion. Or when you want to share Buddy with someone and the
text window feels too engineer-flavored.

**Implementation:** Codex's pet system is likely closed to external
redirection — user's experience: asking Codex to modify the bubble layer
broke it. So the path is "build it ourselves", not "redirect Codex pet".

The reaction display format `timestamp · model · text` is already what
`buddy_window.py` does. The work is **adding a sprite/character render to
the existing window**, not building a UI from scratch:

- Tk Canvas widget on the left for sprite (animated GIF or frame sequence)
- Existing text widget on the right
- Optional: sprite reacts to new entries (jiggle, eye blink, color flash)
- Optional: clickable sprite triggers a "plain language follow-up" turn

Time-to-build is not estimated here — depends on whether `buddy_window.py`'s
layout refactors cleanly. Open the file and see before estimating.

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Multi-personality switching** — only Buddy is wanted; switching dilutes the
  project's identity.
- **Cross-session memory** — buddy doesn't need to remember things across days;
  one-turn reactions are enough.
- **Personality CLI** — editing `buddy-prompt.txt` directly is fine; a CLI
  layer adds surface area for no real benefit.
