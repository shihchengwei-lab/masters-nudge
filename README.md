# Masters’ Nudge

English | [繁體中文](README.zh-TW.md)

> **Passing tests settles behavior, not design.**
>
> Green light means it passes now. What about six months later?

AI can implement a feature and pass its tests while the code still depends on synchronization, special branches, and local patches to stay correct. As requirements change, those workarounds can keep growing.

Masters’ Nudge aims to improve this: it adds a short structural suggestion while AI writes code, bringing an alternative data and responsibility arrangement into the next generation and making a better structure more likely.

## Results and costs

The latest complete comparison is the **six-arm study from September 30 to October 2, 2026**: 12 tasks, two attempts per task and arm, totaling 144 deliveries. Sol means GPT-6.1 Sol; Astra means GPT-6 Astra.

**With Sol medium providing feedback, this study found a structural taste benefit for a Sol medium Actor. For a Sol xhigh Actor, taste tied direct implementation while taking more time.** These two comparisons change only whether Sol medium feedback is added:

| Coding model | Tool-assisted taste versus direct implementation | Total time | Non-cached input tokens |
|---|---|---|---|
| Sol medium | 5 wins, 1 loss | +14.2% | +88.9% |
| Sol xhigh | 3 wins, 3 losses, 2 ties | +27.7% | +51.1% |

Anonymous judges compare code only where both implementations completely delivered the same task and attempt position. Time covers all 24 attempts per arm; tokens use the same 19 positions with complete usage records across all six arms. These are structure, time, and usage measurements, not monetary bills.

Complete deliveries were:

| Arm | Coding model | Feedback model | Complete deliveries |
|---|---|---|---|
| A | Sol medium | None | 6/24 |
| B | Sol medium | Sol medium | 8/24 |
| C | Sol xhigh | None | 13/24 |
| D | Sol medium | Astra medium | 8/24 |
| E | Sol xhigh | Astra medium | 10/24 |
| F | Sol xhigh | Sol medium | 11/24 |

Complete delivery includes functionality, execution rules, the 30-minute deadline, and uniform compatibility checks for original requirements. Delivery count is **C > F > E > B = D > A**. B completed two more deliveries than A; F completed two fewer than C. B versus C split four to four on taste. Jointly completed populations differ, so these comparisons cannot form an overall taste ranking.

See the [six-arm report](benchmark/sol61-six-arm-20261002/REPORT.zh-TW.md) for task results, CLI version differences, and all comparisons. The harness and original evidence are included for [offline statistical reconstruction](benchmark/sol61-six-arm-20261002/HARNESS.zh-TW.md). Earlier studies are listed in the [benchmark index](benchmark/README.zh-TW.md).

## What the tool does

The coding model is the Actor; the feedback model is the Provider. After an Actor edit, the Provider reads the task and related code and returns one short structural suggestion. It enters the Actor's context automatically. The Actor decides whether to adopt it and continues implementation and verification.

```mermaid
flowchart LR
    A["Actor completes apply_patch"] --> B["Provider reads task, edit, and related code"]
    B -->|Concrete direction| C["One four-field suggestion enters Actor context"]
    B -->|No concrete direction| D["Silence"]
    C --> E["Actor judges, implements, and verifies"]
    D --> E
```

### A real example

The latest six-arm study's Element task required multi-device selection, a selection count, cancellation, and bulk sign-out. Compare **A1, direct implementation**, with **B1, using the tool**: both Actors used GPT-6.1 Sol medium, the same CLI, task, and base commit.

| | Without the tool: A1 | With the tool: B1 |
|---|---|---|
| Selection IDs and the method that updates them | Independently optional, with separate source selection | Both supplied or both omitted, with one source decision |
| Supplying only one half | The interface permits displaying external IDs while clicks update local IDs | The type excludes this combination; runtime also keeps reads and writes together |
| Complete-delivery judgment | Passed | Passed |

B1's first edit also selected read and write sources separately. The Provider's actual feedback was:

```text
OBSERVED: FilteredDeviceList: ids??local,set??own
WHY: 單邊 prop 可能使選取更新失效
STRUCTURE: selection props 成對或皆省略；同源讀寫→checked/count/signOut
REQUIRED: 選取、計數與批次登出使用同一組 IDs
```

The Actor then required both halves together and used one decision to choose their source. This makes a component call that displays one state but updates another invalid, without later synchronization or special-case repairs.

Both judges, with anonymous presentation order swapped, preferred B1. The difference is whether the component interface prevents split read/write ownership: both actual pages supplied the complete pair and both completed the contract. See the [case comparison](docs/examples/element-sessions.zh-TW.md) for original feedback, code, and judgment evidence; use the [six-arm report](benchmark/sol61-six-arm-20261002/REPORT.zh-TW.md) for overall benefits and costs.

## Why a nudge can help

The Actor's next generation is shaped by the task, existing code, and its preceding approach. When a problem appears, adding another condition or special case offers a readily available continuation of the same local repair path.

A nudge injects a concrete alternative data and responsibility arrangement into that context. Removing the need for a workaround through structure becomes another candidate direction for subsequent generation. The aim is to influence the Actor's next token choices and increase the probability of adopting a better structure.

The Provider uses five taste criteria to find that direction: make invalid states unrepresentable, keep causality one-way and behavior predictable, give facts one authoritative source, and keep necessary complexity at real boundaries. Suggestions name checkable alternative relations so the Actor can judge and implement them. See the [behavior specification](SPEC.zh-TW.md) for the two selection steps, four-field format, and character limits.

## Limitations

- The Actor owns complete delivery, evaluation of feedback, implementation, and verification. The tool does not take over acceptance.
- A turn stops after three suggestions or two silences, whichever comes first. Recognized test-only edits are skipped without a Provider call or allowance use.
- The Provider supports OpenAI/Codex only. Edits must arrive as explicit `apply_patch` content; opaque shell writes are unsupported.
- A recorded Windows interruption during synchronous `PostToolUse` lacked a matching `hook/completed` event. See the [reproduction and tracking](https://github.com/openai/codex/issues/46765).

## Requirements

Requires Python 3.10+, a Git workspace, an executable and signed-in Codex CLI, and an Actor runtime supporting `UserPromptSubmit`, synchronous MCP `PostToolUse`, and `turn_id`.

The repo plugin manifest version is `0.6.0+codex.20260925224104`. Provider reasoning is fixed at medium; without a saved model selection, the default is `gpt-5.6-sol`. Saved selections override that default and do not change the Actor model.

## Install, enable, and try it

1. Make sure Python, Git, and Codex CLI are installed. If the CLI is not signed in, run `codex login` in PowerShell.
2. In the Codex desktop Plugins page, choose **Add → Add Marketplace → Add from a repository**, enter `https://github.com/shihchengwei-lab/masters-nudge`, and select **Sync**. The repo's [marketplace](.agents/plugins/marketplace.json) exposes Masters’ Nudge; open it, install it, and enable it. See the [official installation steps](https://developers.openai.com/learn/developers-codex-plugin).
3. Review and trust the plugin hooks when Codex prompts you. In the CLI, use `/hooks` to inspect Masters’ Nudge's `UserPromptSubmit` and `PostToolUse` hooks. Installation and enablement do not automatically trust hooks; see the [official hook guidance](https://learn.chatgpt.com/docs/hooks).
4. Open a new chat and ask Codex: “Check whether Masters’ Nudge is ready and set its Provider to gpt-6.1-sol.” The plugin supplies configuration and diagnostic skills; readiness reports dependencies, login, and enablement.
5. Start a new chat in your own Git project and give the Actor a normal code change. After a product-code `apply_patch`, ask Codex: “Show recent Masters’ Nudge attempts.” `feedback` means a suggestion was produced; `silence` means a successful judgment found no suggestion. Faults have separate reasons. For feedback, inspect the four-field suggestion in the Actor context and the subsequent code changes.

If you downloaded this repo, you can also configure and inspect the tool manually from its root in PowerShell:

```powershell
python masters_nudge_cli.py provider set openai --model gpt-6.1-sol
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
```

## Privacy

Task text, edits, tool results, complete changed files that fit the shared material allowance, and file-origin facts are sent to OpenAI. The Provider may read non-ignored files in the Git workspace; it cannot edit the Actor's files. The full task-start file list stays local; only existence facts for paths in the current patch are sent. Unknown provenance remains unknown.

Records default to `.masters-nudge/data/feedback.sqlite3` and settings to `.masters-nudge/config.json` under the user directory. `MASTERS_NUDGE_DATA_DIR` can override these locations. Delivery receipts do not establish Actor adoption or task completion.

## Development

Source files are the single implementation source; build commands generate the plugin copy:

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

The [documentation index](docs/README.zh-TW.md) distinguishes current guidance from historical records.
