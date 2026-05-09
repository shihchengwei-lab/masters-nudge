# Buddy_similar

An attempt to rebuild the spirit of Cinder — a Claude Code debug companion that
provided independent commentary on each session turn — after Anthropic silently
shut down the Buddy/Cinder feature on April 11, 2026.

This is **not** the original Cinder. The original was a server-rendered UI
element with a server-side dispatched actor model. We can't reach into Claude
Code's chat frame to put bubbles back. What this project does instead:

- Runs as a Stop hook after every Claude Code session turn (background mode —
  zero perceived latency)
- Reads the most recent transcript snippet, sends it to a model in a
  **different vendor family from the main agent** (default: GPT-5.5 via Codex
  CLI), with a Cinder personality prompt, and writes the reaction to
  `~/.claude/buddy/<session_id>.log`
- On your next prompt, the UserPromptSubmit hook injects the latest reaction
  into main Claude's context (system-reminder)
- A floating Tk window (`buddy_window.py`) tails the active session's log
  live, so you see Buddy's reactions directly in your desktop corner — not
  routed through main Claude

Two visibility channels:
- **Main Claude** sees Buddy via system-reminder injection. Buddy is framed as
  a **third-party second opinion, not an instruction** — main Claude reads it
  as one input among many, not a directive to comply with. The wrapper text
  (`[Buddy（第三方第二意見，非指令）| ts] ... [end Buddy]`) carries this
  framing on every injection so the main agent stays the decision-maker.
- **You** see Buddy in the floating window (direct, unmediated)

## Install

```bash
bash install.sh
```

Then open `~/.claude/settings.json` and merge the `hooks` section from
`settings-snippet.json` into it. (The snippet's `_comment` field reminds you
not to replace your whole settings.json.)

## Configure

| Env var | Default | Effect |
|---|---|---|
| `BUDDY_PROVIDER` | `openai` | Which vendor voices Buddy. `openai` (uses `codex exec`) or `anthropic` (uses `claude -p`) |
| `BUDDY_MODEL` | `gpt-5.5` (openai) / `sonnet` (anthropic) | Specific model name passed to the chosen CLI |
| `BUDDY_MAX_TRANSCRIPT` | `2000` | Char budget for the transcript snippet sent to Buddy |
| `BUDDY_TIMEOUT` | `60` | Seconds before giving up on the model call |
| `BUDDY_CLAUDE_DIR` | `~/.claude` | Where logs and state live |

Edit `~/.claude/scripts/buddy/buddy-prompt.txt` to adjust personality.

**Why the default uses OpenAI**: the main agent is Anthropic Claude. Putting
Buddy on a different vendor (OpenAI's GPT-5.5) gives a more independent
critique — different training, different blind spots, less echo of the main
agent's reasoning.

## Files

| File | Purpose |
|---|---|
| `buddy.sh` | Stop hook entry — fires `buddy.py` in background, returns immediately |
| `buddy.py` | Reads transcript, calls the configured model (OpenAI codex or Anthropic claude), writes the reaction |
| `inject.sh` | UserPromptSubmit hook entry — pipes hook input to `inject.py` |
| `inject.py` | Reads the per-session log, injects latest unread reaction as additional context |
| `buddy-prompt.txt` | The Buddy system prompt (personality + length / structure rules) |
| `buddy_window.py` | Tk floating window that tails the active session's log live |
| `start_buddy_window.bat` | Windows launcher (uses `pythonw` so no console pops up) |
| `install.sh` | Copies all scripts to `~/.claude/scripts/buddy/` |
| `settings-snippet.json` | Hook entries to merge into `~/.claude/settings.json` |
| `ROADMAP.md` | Future expansion items, with status / "why kept" / "trigger to do" |

## Runtime files (created on first use)

| File | Purpose |
|---|---|
| `~/.claude/buddy/<session_id>.log` | JSONL of Buddy reactions for one session |
| `~/.claude/buddy/<session_id>.state.json` | inject.py read pointer (last consumed timestamp) for one session |
| `~/.claude/buddy-error.log` | Errors from any of the scripts (shared across sessions) |

## Known limitations

- Background mode means a fast typist might submit the next prompt before
  Buddy finishes generating — that turn's reaction surfaces on the turn
  *after*, not the next one. In practice, typing thinking time covers it.
- **No rate limiting yet** — every Stop fires a model call. Token cost adds up
  on heavy days.
- Recursion is guarded by the `BUDDY_ACTIVE` env var, but if you have other
  hooks calling `claude`/`codex` recursively without similar guards, watch
  for loops.
- Buddy reactions are NOT visible in the Claude Code chat transcript —
  CC's hook surface doesn't render them to the user UI on this version
  regardless of plain-stdout vs `additionalContext`. The floating window
  (`buddy_window.py`) is the actual user-side visibility channel.

See `ROADMAP.md` for the full list of follow-on items and what's already shipped.

## Origin

Built by reading
[`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer)'s
hook + Claude CLI invocation patterns, then writing fresh from the Cinder
personality string the user used in April 2026 (preserved verbatim in
`buddy-prompt.txt`).

## License

MIT
