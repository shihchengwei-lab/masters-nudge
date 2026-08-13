# Phase C: shared reviewer architecture

Phase C separates *where an event came from* from *how Masters’ Nudge reviews
it*. Codex CLI normalizes native hook payloads into stable events. The Claude
compatibility path maps checkpoint payloads to `ToolCompleted`; its prompt and
Stop entry points update turn state or construct `ReviewRequest` directly. Both
hosts enter the same `ReviewCore` for an actual review.

## Boundary

| Layer | Owns | Must not own |
|---|---|---|
| Host adapter | Native JSON parsing, session/turn identity, evidence capture, turn journal, checkpoint deduplication, delivery state | Persona prompt logic or provider-specific review policy |
| Shared contracts and evidence | Normalized event/request types, bounded packet construction, evidence limits | Native delivery timing or provider invocation |
| Shared core | Lens routing, prompt composition, provider dispatch, sanitization, recent-reaction context, reaction persistence, telemetry | Claude/Codex transcript wire formats or host delivery state |
| Provider adapter | CLI invocation, schema parsing, usage extraction, recursion guard | Host hook semantics |

The host-neutral event contracts are `PromptSubmitted`, `ToolCompleted`, and
`TurnStopped`; the Codex adapter uses all three, while the Claude compatibility
path currently uses `ToolCompleted` for checkpoint classification. A
`ReviewRequest` carries host/session/turn identity, bounded evidence, review
reason, fingerprint, and shadow labels. Both hosts use the same `ReviewCore`,
prompt/lenses, 42-character completion target, 52-character hard cap, and
`reaction-schema.json` contract.

Legacy callers may still import prompt and output helpers from `buddy.py`, but
those names are compatibility delegates to `masters_nudge.prompting` and
`masters_nudge.providers`. Evaluation scripts using the old API therefore
exercise the same prompt composition, sanitization, length cap, and structured
output parser and provider clients as the production core; `buddy.py` does not
keep a second copy of those rules.

The live Claude Stop and checkpoint paths instantiate `ReviewCore` directly.
Compatibility helper names remain available to older evaluation scripts, but
they are not inserted as pass-through callbacks in the production control flow.

## Host mapping

| Review lifecycle | Claude Code | Codex CLI 0.147+ |
|---|---|---|
| Start turn | `UserPromptSubmit` stores task anchor and transcript offset | `UserPromptSubmit` stores task anchor; transcript content is never parsed |
| Collect evidence | Claude transcript slice, direct hook event, optional agentcam | Every delivered `PostToolUse` appends a bounded journal record |
| Checkpoint | `PostToolUseFailure`; selected successful mutating tools | `PostToolUse`; structured failures when delivered, test output, first >80-line diff |
| End of turn | Native async `Stop` worker | Fast `Stop --detach-stop` shim launches the background worker |
| Deliver Stop finding | Plain additional context on the next prompt | JSON `hookSpecificOutput.additionalContext` on the next prompt |

Codex's documented transcript path is retained only as metadata because its
format is not a stable hooks interface. The Codex journal is capped at 8,000
characters per turn; individual tool records are capped at 3,000 characters.

## Storage and compatibility

New writes default to `~/.masters-nudge/data/` and are host-namespaced:

```text
claude_code--<session>.log
codex_cli--<session>.log
<host>--<session>.turn.json
<host>--<session>.delivery.json
<host>--<session>.checkpoints/
```

The floating window and Claude injection path can read pre-Phase-C
`~/.claude/buddy/` logs/config. They do not move, rewrite, or delete them.
`BUDDY_*` variables remain aliases; `MASTERS_NUDGE_*` is preferred.

## Failure behavior

Hooks fail open: malformed input, missing provider CLIs, timeouts, and reviewer
schema errors are locally logged and never block the main coding agent.
Checkpoint claims are released after reviewer errors/no-finding so a later
equivalent event can retry; delivered findings keep their dedup marker.

The installed Windows Codex CLI 0.147.0 used for the live smoke had two runtime
differences from current documentation: it skipped native `async: true` hooks,
and a non-zero Bash result did not emit `PostToolUse`. The detached Stop shim
handles the former. The latter makes immediate failure checkpoints best-effort
on that build; Stop still reviews the task anchor and final claim. See the
[smoke result](../evaluation/results/phase-c-codex-smoke-20260813/SMOKE_RESULT.md).

Codex hook field and trust behavior follow the
[official hooks documentation](https://learn.chatgpt.com/docs/hooks).
