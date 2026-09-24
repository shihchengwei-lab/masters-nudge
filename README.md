# Masters’ Nudge

English | [繁體中文](README.zh-TW.md)

> **Passing tests settles behavior, not design.**
>
> Green light means it passes now. What about six months later?

## Latest benchmark

The [eighth benchmark report](benchmark/formal-v8/ROUND-8-REPORT.zh-TW.md) evaluates the current Buddy prompt on this branch with GPT-6 Sol medium for both Actor and Provider. The formal contract scores were A 9/12 and B 9/12, with an ambiguity in the clap task's acceptance criteria. Of the eight pairs eligible for blind code-taste review, B won four and four tied. B used about 50% more total execution time and 77% more non-cached input tokens. This is a positive taste signal, but it does not establish that the added cost is worthwhile or that the individual nudges caused the wins. The report also identifies two Vue CSS nudges whose proposed direction was unsound.

The plugin manifest remains at `0.6.0+codex.20260922164420`. Round eight evaluated changes on this branch; its result is not a release validation of an installed plugin. The sixth benchmark below documents an earlier version and a different model and task set.

## Earlier example: generic type resolution in the Vue compiler

The task was to support generic parameters inside intersection types. Both arms passed the same contract, but their structures differed.

**A | only “Please complete it with good taste”: mutate the shared AST node**

```ts
;(type as ScopeTypeNode)._ownerScope = scope
genericScope.types[param.name] = type as ScopeTypeNode
```

**B | Masters’ Nudge: give this generic instance its own node**

```ts
genericScope.types[param.name] = {
  ...type,
  _ownerScope: typeArgumentScope
} as ScopeTypeNode
```

B's first draft also mutated the shared node. The Provider flagged that `createTypeScope` was writing call-site ownership into shared AST state. After receiving that feedback, the Actor's final implementation copied the node before attaching its scope, so another generic resolution cannot overwrite this binding's `_ownerScope` through the same type-argument node.

> **Blind judge 1:** “B copies the generic argument before attaching `_ownerScope`; A mutates the original AST argument, making shared-node scope depend on resolution order and introducing hidden side effects.”
>
> **Blind judge 2:** “B confines this binding to a new node, improving local predictability and one-way data flow.”

The [sixth benchmark report](benchmark/formal-v6/RESULTS.zh-TW.md#各組盲評) preserves the full judgment and all eleven other pairs.

Below is the complete result across six tasks and twelve paired comparisons.

![Sixth benchmark: Masters' Nudge won seven code-taste comparisons, a generic taste request won two, and three tied. Both arms completed 12 of 12 contracts; B used 44.8 percent more time and 94.5 percent more non-cached input.](docs/assets/benchmark-v6.svg)

Same six repository tasks, same model, same contract. A added one sentence: “Please complete it with good taste.” B omitted that sentence and used Masters’ Nudge after code changes. **B won 7–2, with 3 ties; both arms completed 12/12 contracts.** B used 44.8% more time and 94.5% more non-cached input tokens.

Masters’ Nudge provides small engineering feedback after the Actor changes code, without taking over implementation. [SPEC.zh-TW.md](SPEC.zh-TW.md) is the authority. The [sixth benchmark](benchmark/formal-v6/RESULTS.zh-TW.md) remains a historical result for the earlier version.

UserPromptSubmit records the task without calling a Provider. Each successful `apply_patch` triggers native
PostToolUse, which synchronously calls the persistent Codex-facing MCP tool `review_patch`. The core combines the
task, completed patch, successful tool result, and updated workspace into one judgment. The OpenAI/Codex Provider
uses six structural checks. Its prompt directs it to trace related code and declared types or APIs, using a separate read-only repository MCP to search or read files. The Actor owns implementation and
verification.
When feedback exists, the adapter preserves the successful tool result and appends the `OBSERVED`, `VIOLATES`, and
`PREFER` fields to that same result. A fixed follow-up asks the Actor to decide whether the observed relation is
required by the task before continuing; implementation authority remains with the Actor.

Each user-message round stops at three feedbacks or two silences. New requests reset the allowance; latest conflicting
requirements win. Failures are visible and never counted as silence.

## Evidence boundary

Round eight used six repository tasks and two runs per arm. A used preserved results; B was rerun independently. Only pairs where both arms passed the contract were blind reviewed. Because the Actor runs were independent, their difference cannot be attributed entirely to Provider feedback. The [round-eight report](benchmark/formal-v8/ROUND-8-REPORT.zh-TW.md) records the method, costs, contract ambiguity, and limitations. The [sixth benchmark](benchmark/formal-v6/RESULTS.zh-TW.md) used an earlier setup and is not a like-for-like trend comparison.

## Known limitation

On Windows, interrupting a turn while synchronous `PostToolUse` is running can emit `hook/started` without a matching
`hook/completed` for the same run ID. Masters’ Nudge then cannot determine from lifecycle events alone whether that Hook
was cancelled or is still running; this state is not Provider silence. The isolated reproduction, event sequence, and
requested behavior are tracked in [openai/codex#46765](https://github.com/openai/codex/issues/46765), which remains open.
See the local [Codex PostToolUse lifecycle specification](experiments/champion-vs-preserved-result-20260920/CODEX-POSTTOOLUSE-LIFECYCLE-SPEC.md).

Requires Python 3.10+, Git, a logged-in Codex Provider, and an Actor runtime exposing UserPromptSubmit/PostToolUse
with turn_id. Opaque shell mutations are unsupported. Only the OpenAI/Codex Provider is supported.
The source runtime and generated plugin copy are synchronized. Installation state, Codex-version-specific lifecycle
behavior, and a complete task after updating an installed copy still require checks in that target environment.

The five optional material categories and all read-only repository MCP reads share one budget. Evidence names the
source and location received during that judgment; the core checks JSON shape and limits but does not independently verify the quoted text. Only `OBSERVED`, `VIOLATES`, `PREFER`, and the fixed resolution
sentence reach the Actor.

## Privacy

Task, change, tool-result and selected repository materials are sent to OpenAI. The read-only repository MCP cannot write files or read
outside the repository, Git internals, or ignored files. Attempt records are stored under .masters-nudge/data in the
user directory. A recorded delivery is not evidence of Actor adoption.

## Configuration and development

The code fallback model is `gpt-5.6-sol` at medium reasoning; a saved Provider selection overrides it. Round eight used `gpt-6-sol` at medium reasoning. Check the active selection with `provider get`.

```powershell
python masters_nudge_cli.py provider get
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```
