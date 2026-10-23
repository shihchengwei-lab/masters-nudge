# Masters’ Nudge

English | [繁體中文](README.zh-TW.md)

> **Passing tests settles behavior, not design.**
>
> Green light means it passes now. What about six months later?

AI can finish a feature and pass its tests while the code still relies on synchronized state, special cases and local patches. Those workarounds can grow as requirements change.

Masters’ Nudge adds a short structural suggestion while Codex writes code. After an edit, a read-only feedback model—the Provider—reviews the task and related code. The coding model—the Actor—decides whether to adopt the suggestion, then continues implementation and verification. When the Provider finds no useful direction, it stays silent.

## Watch the Actor receive a nudge and make its next edit

In Element’s device selection and bulk sign-out task, **both implementations passed the fixed acceptance checks.** After a nudge, the right-hand AI’s next edit required the selection list and updater as a pair and chose their source together.

![14-second side-by-side chat reconstruction: without a nudge on the left, with a nudge and subsequent structural edit on the right.](docs/images/element-chat-replay.en.gif)

*Chat reconstructed from actual records, with translated excerpts, paraphrased feedback and summarized edits. Work and waiting are condensed. [Source records and acceptance checks](docs/examples/element-live-recording.zh-TW.md).*

## Results and costs

With **GPT-6.1 Sol xhigh as both Actor and Provider**, complete delivery matched direct implementation at **13/24 attempts**. In the **11 jointly completed code comparisons**, structural review found **7 wins, 0 losses and 4 ties**.

The trade-off was **26.9% more total time** and **73.1% more non-cached input tokens**. The benchmark covered twelve tasks and seven configurations, with 24 attempts per configuration. Time includes all attempts; token comparison uses 19 matched task/attempt positions with complete usage records across all seven configurations, counting both Actor and Provider usage. These figures apply to the xhigh configuration above; the current Provider default is medium.

[Main benchmark](benchmark/model-comparison-20261004/REPORT.zh-TW.md) · [Code-review results](benchmark/model-comparison-20261004/taste-review/README.zh-TW.md) · [Methods and data](benchmark/README.zh-TW.md)

Separate follow-up work continued from earlier implementations and completed Regexp, Metaflow and Tracing. See the [continuation results](benchmark/unresolved-challenges-20261004/continuation-20261017/README.zh-TW.md), [challenge history](benchmark/unresolved-challenges-20261004/README.zh-TW.md) and [supplementary nine-task analysis](benchmark/model-comparison-20261004/PRIMARY.zh-TW.md).

## Why a nudge can help

The Actor's next generation is shaped by the task, existing code, and its preceding approach. When a problem appears, adding another condition or special case offers a readily available continuation of the same local repair path.

A nudge injects a concrete alternative data and responsibility arrangement into that context. Removing the need for a workaround through structure becomes another candidate direction for subsequent generation. The design expectation is that this influences the Actor's next token choices and increases the probability of adopting a better structure.

The Provider uses five taste criteria to find that direction, with no fixed priority:

1. **Invalid states**: make invalid states impossible to construct, including states forbidden by explicit task constraints.
2. **Causal direction**: let causes produce effects in one direction; avoid competing update orders.
3. **Local predictability**: make local behavior easy to understand and predict; avoid hidden side effects and dependencies.
4. **Single source**: give each fact one authoritative source; derive views instead of synchronizing copies.
5. **Necessary complexity**: keep necessary complexity at real boundaries and the core path direct; abstractions should simplify the whole path while keeping responsibilities clear.

Suggestions name checkable alternative relations so the Actor can judge and implement them. See the [behavior specification](SPEC.zh-TW.md) for the two selection steps, four-field format, and character limits.

## Limitations

- The Actor evaluates feedback, implements changes and verifies complete delivery.
- Provider calls stop for the turn after three suggestions or two silences, whichever comes first. Recognized test-only edits are skipped without a Provider call or allowance use.
- The Provider supports OpenAI/Codex only. Edits must arrive as explicit `apply_patch` content; opaque shell writes are unsupported.
- On the qualified Windows platform, interruption stops the Provider and preserves an interrupted fault; see [qualification](docs/qualification/README.zh-TW.md). Codex can still omit the matching `PostToolUse` completion event. See the [reproduction and tracking](https://github.com/openai/codex/issues/46765).

## Get started

Supported platform: **Windows 11 x64**. Requires Python 3.10+ available as `python`, a Git workspace, a signed-in Codex CLI and a supported [Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).

1. In Codex desktop’s Plugins page, choose **Add → Add Marketplace → Add from a repository**. Enter `https://github.com/shihchengwei-lab/masters-nudge`, select **Sync**, then install and enable Masters’ Nudge.
2. Review and trust the plugin hooks when Codex prompts you.
3. Start a new chat and ask: **“Check whether Masters’ Nudge is ready and show its Provider model and reasoning effort.”**
4. In your Git project, request a normal code change. After the edit, ask: **“Show recent Masters’ Nudge attempts.”** You can inspect the suggestion and the Actor’s subsequent changes.

The Provider defaults to model `auto` and reasoning effort `medium`. Ask Codex to change either setting. Restart Codex after configuration changes or plugin updates, and review any updated hook commands when prompted.

See the [detailed guide](docs/DEVELOPMENT.zh-TW.md#手動設定與診斷) for manual commands, configuration and diagnostics.

## Privacy

Task text, edits, tool results, complete changed files that fit the shared material allowance, and file-origin facts are sent to OpenAI. The Provider has read-only access to non-ignored files in the Git workspace. The full task-start file list stays local; existence facts for paths in the current patch are sent.

Records default to `.masters-nudge/data/feedback.sqlite3` and settings to `.masters-nudge/config.json` under the user directory. `MASTERS_NUDGE_DATA_DIR` can override these locations.

## Development

Source files are the single implementation source; build commands generate the plugin copy:

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

See the [documentation index](docs/README.zh-TW.md) for usage, specifications, and development guidance.
