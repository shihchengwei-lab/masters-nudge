# Shared reviewer architecture

Native host events are separate from review policy. Claude Code and Codex keep different adapters because their event payloads, Stop timing, and delivery channels differ; both adapters construct the same bounded `ReviewRequest` and call the same `ReviewCore`.

## Ownership boundary

| Layer | Owns | Does not own |
|---|---|---|
| Host entry and adapter | Native JSON parsing, session/turn identity, evidence capture, delivery channel | Review timing, lens prompts, provider policy, output validation |
| Shared checkpoints and evidence | Event classification, stable fingerprints, bounded packet construction | Host JSON or provider invocation |
| `ReviewCore` | Routing, prompt composition, canonical review attempts, sanitation, persistence, telemetry | Native transcript formats or hook stdout |
| Provider adapter | CLI/HTTP invocation, schema parsing, usage extraction, recursion guard, transport checks | Hook semantics or delivery receipts |
| Storage | Host-namespaced turn state, reactions, receipts, and canonical review attempts | Routing, provider choice, or telemetry policy |
| Diagnostic telemetry | Content-free route, status, latency, and provider-reported usage metadata | Review text, task content, cost policy, or automatic gates |

The core contracts are `PromptSubmitted`, `ToolCompleted`, `TurnStopped`, `ReviewRequest`, and `ReviewOutcome`.

## Lens selection and private attention cues

`persona_config.STAGE_SPECS` owns each manual Lens's public name, practical focus, and private persona slug; window choices read that registry directly. `persona_config.resolve_stage()` owns manual selection and defaults to `automatic`. `MASTERS_NUDGE_STAGE` accepts `automatic`, `design`, `build`, `evolve`, `review`, `reliability`, or `performance`; an invalid value falls back visibly to Automatic through the `invalid_environment` source. The former persona environment override is not accepted.

Public UI labels describe the engineering focus. Internal persona slugs remain available for routing and telemetry, while the corresponding person name appears only in the Generator prompt as a private attention cue. Automatic mode is explicitly two-stage: a compact Router receives the bounded source packet and six short Lens definitions, then returns one Lens and a routing hypothesis. The Generator receives the shared output contract, only the selected persona overlay, and the routing hypothesis marked as non-evidence. Manual selection skips the Router. No hidden marker or main-agent self-report chooses the Lens.

## Host paths

Claude Code uses three small native entry points:

- `claude_prompt.py` for `UserPromptSubmit`;
- `claude_checkpoint.py` for completed tool evidence and `PostToolUseFailure`;
- `claude_stop.py` for observing the main agent's response at `Stop`, without a Provider call or output.

`masters_nudge/claude_adapter.py` is the sole owner of mapping a Claude hook payload to `SessionRef`; each entry point reuses that identity throughout one event.

Codex uses `hook_entry.py --host codex_cli` for prompt, tool, and Stop events. `masters_nudge/codex_adapter.py` owns Codex payload normalization and its per-turn evidence capture.

Both paths use the classifier in `masters_nudge/checkpoints.py`. Host entry files convert payloads and delivery behavior; they do not keep a second classifier or prompt/provider implementation.

| Lifecycle | Claude Code | Codex |
|---|---|---|
| Start turn | Save the task request and final-claim fallback offset | Save the task request and transcript offset |
| Collect evidence | Capture explicitly referenced task sources plus semantic results | Capture explicitly referenced task sources plus semantic results |
| After tool use | Record bounded semantic evidence; review the first semantic change or repeated same-surface failures | Record bounded semantic evidence; review the first semantic change or repeated same-surface failures |
| End turn | Native `Stop` records whether an earlier Nudge received a response; no Provider call or output | Native `Stop` records whether an earlier Nudge received a response; no Provider call or output |
| Deliver finding | `hookSpecificOutput.additionalContext` on the eligible tool event, prefixed `獨立第二意見：` | `hookSpecificOutput.additionalContext` on the eligible tool event, prefixed `獨立第二意見：` |

## Output and delivery

The provider is prompted to return one evidence-grounded, contract-bound preference or silence. A finding must use `<favor>；別<alternative>，因為<reason>。`, stay within 52 characters, and state an engineering preference rather than a question, review procedure, or test-only instruction. A test request is valid only when it changes an implementation, interface, ownership, behavior boundary, or reversible decision. The schema, provider parser, and shared core all reject malformed findings; runtime code does not rewrite reviewer text.

The host hook output contains the finding text. Effective lens, route source, trigger, and review reason belong to local reaction and telemetry records; callers must not assume those fields are present in the host wire output.

A generated reaction starts as `queued`. The eligible hook either writes it in the same event, after which it becomes `emitted`, or records `failed` if wire output fails. Only a later host event exposing the main model's response confirms `injected`; later prompt or tool events never pick up an older queued reaction.

`ReviewCore.review_once()` claims a canonical identity composed of host session, turn, review kind, and source fingerprint before invoking the Provider. The attempt ends as `finding`, `no_finding`, or `error`; the same identity is never retried automatically. Automatic attempts use a Router followed by one selected Generator and merge both calls' usage; manual attempts use one Generator. Stop and goal-transition events do not create review attempts. Provider work is capped at 90 seconds total inside the host hook's 120-second timeout. If a Provider process times out after already emitting one complete schema result, the Provider adapter may recover that result before cleaning up the process tree; there is no fallback to another Provider.

## State

New state is written under `~/.masters-nudge/data/` by default:

```text
claude_code--<session>.log
codex_cli--<session>.log
<host>--<session>.turn.json
<host>--<session>.progress.json
<host>--<session>.delivery.json
<host>--<session>.review-attempts/
reviewer.json
review-telemetry.jsonl
```

One `.turn.json` record owns the task request, explicitly referenced sources, bounded semantic results, and any final-claim fallback offset. The matching `.progress.json` keeps only scheduler state needed to decide when another review is eligible; it does not duplicate the task, tool identity, commands, or evidence text. Reviewer configuration is host-neutral.

The `migrate` command is a one-shot boundary for older installations. It defaults to dry-run, requires `--apply` to write, backs up an exact known host configuration before editing, refuses near matches or conflicting destinations, refuses if the source changes after preflight, and does not delete original review data.

## Failure and privacy behavior

Hooks fail open on errors: malformed native input, unavailable Provider CLIs, timeouts, schema errors, and local write failures produce no Nudge and are logged locally. Stop observation never emits a finding or continues the turn.

Provider selection does not fail over silently. The Ollama path additionally fails closed for network privacy: only loopback HTTP is accepted, proxies and redirects are disabled, cloud-disabled status is checked, and remote model metadata is rejected.

The packet keeps the task contract, explicitly referenced source content, and the latest bounded semantic results in chronological order. Routine navigation output, generic source inspection, external reports, tool identity, unrelated commands, and the main model's running explanation are excluded. Stop reads the latest current-turn assistant text only to record a response observation; it sends no final claim to the Provider. The first completed semantic change opens one taste window. A single failure does not; the same failure family must repeat. `PreToolUse.additionalContext` is deliberately not used for this window: both supported Hosts deliver that context on the next model request, after the pending tool call has already been chosen; changing the pending call would require blocking or rewriting it. `ReviewCore` places at most the latest three injected Nudge texts before the packet as an exclusion set, not as evidence, suggestions, or examples. Full transcripts are not copied into reviewer packets or telemetry.

## Package and verification

The checked-in `plugins/masters-nudge/` directory is the self-contained install package. `masters_nudge/plugin_inventory.py` owns one code-defined package manifest for generated files, static files, core runtime dependencies, and optional UI assets. `tools/build_plugin.py` and `doctor` derive their inventories from that manifest; the installed package does not self-report a second inventory. Marketplace metadata points to the generated package rather than to the repository root.

The repository's historical prerelease benchmark is indexed in [evaluation](../evaluation/README.md). Retired specialization and host-smoke artifacts are preserved separately in [`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22). Neither archive guarantees behavior on later source or host versions; native event availability and hook trust must be rechecked during fresh-install acceptance.

See the [OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins) and [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) for the current host contracts.
