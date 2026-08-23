# Shared reviewer architecture

Native host events are separate from review policy. Claude Code and Codex keep different adapters because their event payloads, journals, Stop timing, and delivery channels differ; both adapters construct the same bounded `ReviewRequest` and call the same `ReviewCore`.

## Ownership boundary

| Layer | Owns | Does not own |
|---|---|---|
| Host entry and adapter | Native JSON parsing, session/turn identity, evidence capture, checkpoint timing, delivery channel | Lens prompts, provider policy, output sanitation |
| Shared checkpoints and evidence | Event classification, stable fingerprints, bounded packet construction | Host JSON or provider invocation |
| `ReviewCore` | Routing, prompt composition, provider dispatch, sanitation, persistence, telemetry | Native transcript formats or hook stdout |
| Provider adapter | CLI/HTTP invocation, schema parsing, usage extraction, recursion guard, transport checks | Hook semantics or delivery receipts |
| Storage | Host-namespaced turn state, reactions, receipts, checkpoint claims | Routing, provider choice, or telemetry policy |
| Diagnostic telemetry | Content-free route, status, latency, and provider-reported usage metadata | Review text, task content, cost policy, or automatic gates |

The core contracts are `PromptSubmitted`, `ToolCompleted`, `TurnStopped`, `ReviewRequest`, and `ReviewOutcome`.

## Lifecycle selection and private attention cues

`persona_config.STAGE_SPECS` owns each lifecycle stage's public name, practical focus, and private persona slug; window choices read that registry directly. `persona_config.resolve_stage()` owns lifecycle selection. `MASTERS_NUDGE_STAGE` accepts only `design`, `build`, `evolve`, or `review`; an invalid value falls back visibly to Build through the `invalid_environment` source. The former persona environment override is not accepted.

Public UI labels describe the engineering stage and practical focus. Internal persona slugs remain available for routing and telemetry, while the corresponding person name appears only in the provider prompt as a private attention cue. Direct reliability or performance evidence may select a specialist automatically; those specialists are not public stage settings.

## Host paths

Claude Code uses three small native entry points:

- `claude_prompt.py` for `UserPromptSubmit`;
- `claude_checkpoint.py` for successful mutating tools and `PostToolUseFailure`;
- `claude_stop.py` for the async `Stop` review.

`masters_nudge/claude_adapter.py` is the sole owner of mapping a Claude hook payload to `SessionRef`; each entry point reuses that identity throughout one event.

Codex uses `hook_entry.py --host codex_cli` for prompt and tool events, plus `--detach-stop` for the fast Stop shim. `masters_nudge/codex_adapter.py` owns Codex payload normalization and its bounded per-turn tool journal.

Both paths use the classifier in `masters_nudge/checkpoints.py`. Host entry files convert payloads and delivery behavior; they do not keep a second classifier or prompt/provider implementation.

| Lifecycle | Claude Code | Codex |
|---|---|---|
| Start turn | Save the task anchor and transcript offset | Save the task anchor; do not parse the Codex transcript |
| Collect evidence | Bounded transcript/event evidence and optional Agentcam report | Bounded `PostToolUse` journal and optional Agentcam report |
| Checkpoint | Tool failure or selected successful mutation | Delivered structured failure, test output, large diff, or long-goal change |
| End turn | Async native `Stop` worker | Detached Stop worker |
| Deliver queued finding | Plain additional context at a later prompt | `hookSpecificOutput.additionalContext` at a later hook event |

## Output and delivery

The provider is prompted to return one open question or silence. Runtime sanitation bounds any returned finding to 52 characters, but does not claim to mechanically enforce question quality. If a result reaches the cap without terminal punctuation, sanitation closes it at the last available clause; it does not make another provider call.

The injected hook output contains the finding text. Effective lens, route source, trigger, and review reason belong to local reaction and telemetry records; callers must not assume those fields are present in the host wire output.

A generated reaction starts as `queued`. Successful insertion records an `injected` receipt with the receiving event; stale reactions become `expired`, skipped older reactions become `superseded`, and failed delivery remains inspectable. Detached strategy reviews are single-flight per session.

## State

New state is written under `~/.masters-nudge/data/` by default:

```text
claude_code--<session>.log
codex_cli--<session>.log
<host>--<session>.turn.json
<host>--<session>.delivery.json
<host>--<session>.checkpoints/
reviewer.json
review-telemetry.jsonl
```

One `.turn.json` record owns the task anchor, evidence offset, and current-turn state. There is no second source-state file for the same turn. Reviewer configuration is host-neutral.

The `migrate` command is a one-shot boundary for older installations. It defaults to dry-run, requires `--apply` to write, backs up an exact known host configuration before editing, refuses near matches or conflicting destinations, refuses if the source changes after preflight, and does not delete original review data.

## Failure and privacy behavior

Hooks fail open for the main coding agent: malformed native input, unavailable provider CLIs, timeouts, schema errors, and local write failures produce no Nudge and are logged locally.

Provider selection does not fail over silently. The Ollama path additionally fails closed for network privacy: only loopback HTTP is accepted, proxies and redirects are disabled, cloud-disabled status is checked, and remote model metadata is rejected.

The Codex journal is capped per turn and per tool record. Claude transcript evidence, current claims, tool evidence, and optional Agentcam evidence are also bounded before entering `ReviewCore`. Full transcripts are not copied into telemetry.

## Package and verification

The checked-in `plugins/masters-nudge/` directory is the self-contained install package. `masters_nudge/plugin_inventory.py` owns one code-defined package manifest for generated files, static files, core runtime dependencies, and optional UI assets. `tools/build_plugin.py` and `doctor` derive their inventories from that manifest; the installed package does not self-report a second inventory. Marketplace metadata points to the generated package rather than to the repository root.

Historical host-smoke evidence is preserved in the verified evidence archive linked from `evaluation/README.md`; it is not a guarantee for later host versions. Native event availability and hook trust must be rechecked during fresh-install acceptance.

See the [OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins) and [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) for the current host contracts.
