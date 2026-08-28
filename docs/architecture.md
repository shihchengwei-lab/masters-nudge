# Shared reviewer architecture

Native host events are separate from review policy. Claude Code and Codex keep different adapters because their event payloads, Stop timing, and delivery channels differ; both adapters construct the same bounded `ReviewRequest` and call the same `ReviewCore`.

## Ownership boundary

| Layer | Owns | Does not own |
|---|---|---|
| Host entry and adapter | Native JSON parsing, session/turn identity, evidence capture, delivery channel | Review timing, lens prompts, provider policy, output validation |
| Shared checkpoints and evidence | Event classification, stable fingerprints, bounded packet construction | Host JSON or provider invocation |
| `ReviewCore` | Routing, prompt composition, single-attempt provider dispatch, sanitation, persistence, telemetry | Native transcript formats or hook stdout |
| Provider adapter | CLI/HTTP invocation, schema parsing, usage extraction, recursion guard, transport checks | Hook semantics or delivery receipts |
| Storage | Host-namespaced turn state, reactions, receipts, and canonical review attempts | Routing, provider choice, or telemetry policy |
| Diagnostic telemetry | Content-free route, status, latency, and provider-reported usage metadata | Review text, task content, cost policy, or automatic gates |

The core contracts are `PromptSubmitted`, `ToolCompleted`, `TurnStopped`, `ReviewRequest`, and `ReviewOutcome`.

## Lifecycle selection and private attention cues

`persona_config.STAGE_SPECS` owns each manual lifecycle stage's public name, practical focus, and private persona slug; window choices read that registry directly. `persona_config.resolve_stage()` owns manual selection and defaults to `automatic`. `MASTERS_NUDGE_STAGE` accepts `automatic`, `design`, `build`, `evolve`, `review`, `reliability`, or `performance`; an invalid value falls back visibly to Automatic through the `invalid_environment` source. The former persona environment override is not accepted.

Public UI labels describe the engineering stage and practical focus. Internal persona slugs remain available for routing and telemetry, while the corresponding person name appears only in the provider prompt as a private attention cue. At turn start, the Host asks the coding agent to append one hidden focus marker to progress and final messages. The marker can report Design, Build, Evolve, Review, Reliability, or Performance and selects exactly one private prompt only after the shared checkpoint policy has already made a review due. It cannot request or suppress a Provider call. An explicit manual stage wins; a missing marker uses Build during work and Review at Stop. No tool output or free-form evidence text is reparsed to choose a lens.

## Host paths

Claude Code uses three small native entry points:

- `claude_prompt.py` for `UserPromptSubmit`;
- `claude_checkpoint.py` for successful mutating tools and `PostToolUseFailure`;
- `claude_stop.py` for the synchronous `Stop` review and same-turn continuation.

`masters_nudge/claude_adapter.py` is the sole owner of mapping a Claude hook payload to `SessionRef`; each entry point reuses that identity throughout one event.

Codex uses `hook_entry.py --host codex_cli` for prompt, tool, and Stop events. `masters_nudge/codex_adapter.py` owns Codex payload normalization and its per-turn evidence capture.

Both paths use the classifier in `masters_nudge/checkpoints.py`. Host entry files convert payloads and delivery behavior; they do not keep a second classifier or prompt/provider implementation.

| Lifecycle | Claude Code | Codex |
|---|---|---|
| Start turn | Save the task request and final-claim fallback offset; add the hidden focus-report contract | Save the task request and transcript offset; add the hidden focus-report contract |
| Collect evidence | Capture explicitly referenced task sources plus semantic results | Capture explicitly referenced task sources plus semantic results |
| Tool boundary | Record bounded semantic evidence; review on the second same-surface failure or an explicit long-goal `complete`／`blocked` transition | Record bounded semantic evidence; review on the second same-surface failure or an explicit long-goal `complete`／`blocked` transition |
| End turn | Synchronous native `Stop`; a finding adds context and continues | Synchronous native `Stop`; a finding returns `decision: block` and continues |
| Deliver finding | `hookSpecificOutput.additionalContext` on the eligible event, prefixed `獨立第二意見：` | `hookSpecificOutput.additionalContext`, or Stop `reason`, on the eligible event, prefixed `獨立第二意見：` |

## Output and delivery

The provider is prompted to return one evidence-grounded, contract-bound, immediately testable second opinion or silence. The opinion may be a statement or question that identifies one missed constraint, counterexample, alternative hypothesis, or direction plus the smallest discriminating check. Unknown information must not become a new acceptance criterion. The structured output contract rejects malformed or over-length findings; runtime code does not rewrite reviewer text.

The host hook output contains the finding text. Effective lens, route source, trigger, and review reason belong to local reaction and telemetry records; callers must not assume those fields are present in the host wire output.

A generated reaction starts as `queued`. The eligible hook either writes it in the same event, after which it becomes `emitted`, or records `failed` if wire output fails. Only a later host event exposing the main model's response confirms `injected`; later prompt or tool events never pick up an older queued reaction.

`ReviewCore.review_once()` claims a canonical identity composed of host session, turn, review kind, and source fingerprint before invoking the Provider. The attempt ends as `finding`, `no_finding`, or `error`; the same identity is never retried automatically. Checkpoint, strategy, goal-transition, and Stop reviews use this one mechanism, so no detached single-flight coordinator or Stop/strategy race exists. Provider work is capped at 90 seconds inside the host hook's 120-second timeout. If a Provider process times out after already emitting one complete schema result, the Provider adapter may recover that result before cleaning up the process tree; there is no fallback to another Provider.

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

Hooks fail open on errors: malformed native input, unavailable Provider CLIs, timeouts, schema errors, and local write failures produce no Nudge and are logged locally. A valid Stop finding intentionally continues the same turn; it is not an error path.

Provider selection does not fail over silently. The Ollama path additionally fails closed for network privacy: only loopback HTTP is accepted, proxies and redirects are disabled, cloud-disabled status is checked, and remote model metadata is rejected.

The packet keeps the task contract, explicitly referenced source content, and the latest bounded semantic results in chronological order. Routine navigation output, generic source inspection, external reports, tool identity, commands, and the main model's running explanation or reaction are excluded. The Host may read the latest current-turn assistant text only to extract the hidden focus marker; the marker is stripped from final claims and never copied into reviewer evidence. Normal changes, large diffs, and a single failure are evidence, not intervention triggers. After an injected Nudge, another tool-time review waits until a new semantic change reaches a later verification or failure boundary. `ReviewCore` places at most the latest three injected Nudge texts before the packet as an exclusion set, not as evidence, suggestions, or examples. Current final claims are bounded before entering `ReviewCore`; full transcripts are not copied into reviewer packets or telemetry.

## Package and verification

The checked-in `plugins/masters-nudge/` directory is the self-contained install package. `masters_nudge/plugin_inventory.py` owns one code-defined package manifest for generated files, static files, core runtime dependencies, and optional UI assets. `tools/build_plugin.py` and `doctor` derive their inventories from that manifest; the installed package does not self-report a second inventory. Marketplace metadata points to the generated package rather than to the repository root.

The repository's historical prerelease benchmark is indexed in [evaluation](../evaluation/README.md). Retired specialization and host-smoke artifacts are preserved separately in [`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22). Neither archive guarantees behavior on later source or host versions; native event availability and hook trust must be rechecked during fresh-install acceptance.

See the [OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins) and [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) for the current host contracts.
