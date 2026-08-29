# Masters' Nudge architecture

Masters' Nudge injects one independent engineering preference after observable
tool results and before the next model decision. It is not a reviewer, judge,
complete solver, or Stop gate.

## Ownership

| Layer | Owns | Does not own |
|---|---|---|
| Host adapter | Native payload parsing, session identity, event or batch normalization, delivery | Lens selection or engineering interpretation |
| Checkpoints and evidence | Bounded evidence, order, fingerprints, and exact replay suppression | Lens qualification |
| Router | Select one qualified Lens or `none` from the original packet | Advice or a routing explanation for the Generator |
| Generator | Base prompt, one selected Filter, and the original packet | Other Filters, main-model reasoning, or prior Nudges |
| Provider contract | JSON shape, field consistency, supported Lens, emptiness, and 52-character limit | Semantic quality |
| Delivery | Inject one structurally valid, non-identical Nudge and record wire state | Rewriting or semantic filtering |

`persona_config.STAGE_SPECS` is the single source for the three manual choices:
`review` (Simplicity), `reliability`, and `performance`. `automatic` runs the
Router. Retired values resolve to `automatic`; they are not mapped to a retained
Lens. Person names are private attention cues inside Filter prompts, not public
capability claims.

`MASTERS_NUDGE_STAGE` accepts only `automatic`, `review`, `reliability`, or
`performance`.

The Base prompt defines only identity, visible input, and output shape. The
Router receives the bounded task-and-evidence packet plus three minimum evidence
thresholds. The Generator receives the same original packet and exactly one
Filter prompt. Router reasoning is never forwarded.

## Host control points

The ideal control point is after all tools chosen by the current model step have
finished and before the next model request starts.

| Host | Native event | Precision | Known limitation |
|---|---|---|---|
| Claude Code | `PostToolBatch` | Exact for the native batch | Failure is marked only when the serialized result exposes an explicit signal |
| Codex | synchronous `PostToolUse` | Approximate | Parallel tools may be observed and reviewed separately |

Claude `UserPromptSubmit` stores the task anchor. `PostToolBatch` preserves tool
call order, records the complete batch as one progress event, and opens at most
one review attempt. Claude `Stop` only observes a later response.

Codex `UserPromptSubmit` stores the task anchor. Each synchronous `PostToolUse`
is treated as a one-item batch. Masters' Nudge does not use a timer, transcript
guess, or delayed resend to imitate a missing batch boundary. Codex `Stop` only
observes a later response.

Both Hosts deliver a finding through `hookSpecificOutput.additionalContext`,
prefixed `獨立第二意見：`. Stop never calls the Provider, emits a Nudge, blocks
completion, or extends the turn.

## Packet, routing, and output

The Provider packet contains only the current task anchor, explicitly referenced
task sources, and bounded objective evidence such as changes, failures,
verifications, and measurements. It excludes full transcripts, main-model
reasoning, running narration, generic navigation, tool names, complete commands,
and prior Nudges.

Automatic mode first asks the Router for one of `linus`, `lamport`, `carmack`,
or `none`. Manual mode skips the Router but does not lower the selected Filter's
evidence threshold. The Generator returns one direct Traditional Chinese
preference or `no_finding`, within 52 characters.

Runtime validation is structural only. An exact previously injected finding is
suppressed after generation without exposing prior Nudge text to the Provider.

## State and delivery

Runtime state is stored under `~/.masters-nudge/data/` by default. Turn state
owns the task anchor, named sources, and bounded evidence. Progress state keeps
only the event sequence and last event fingerprint. Reaction logs keep Provider
outputs and delivery metadata; telemetry keeps content-free host, hook event,
route, status, latency, and reported usage.

A generated finding is `queued`, becomes `emitted` only after hook output is
flushed, and becomes `injected` only when a later host event exposes a model
response. These receipts establish order, not causation. Failed output is
terminal for that attempt; older queued findings are not picked up by later
events.

Hooks fail open on malformed input, unavailable Provider CLIs, timeouts, schema
errors, or local write failures. Provider selection never fails over silently.

## Package and verification

Repository source is canonical. `masters_nudge/plugin_inventory.py` owns package
membership; `tools/build_plugin.py` generates the checked-in
`plugins/masters-nudge/` runtime and detects stale or unexpected files. Doctor
reports the actual Host event and whether its control point is exact or
approximate; it does not invent a capability enum.
