# Masters’ Nudge

English | [繁體中文](README.zh-TW.md)

> **Passing tests settles behavior, not design.**
>
> Green light means it passes now. What about six months later?

Masters’ Nudge gives the coding agent (Actor) one small structural suggestion after a code edit. A separate model (Provider) reads the task, the edit, and relevant repository code. The Actor decides what to implement. [SPEC.zh-TW.md](SPEC.zh-TW.md) defines the behavior.

## Example: a cache key without inherited entries

In a recent evaluation, the task was to let Express render a view with a custom `cacheKey`. The first B-arm edit used the key for cache reads and writes, while the cache itself was still initialized as an ordinary object. The Provider returned:

```text
OBSERVED: cache['toString'] -> Function
VIOLATES: inherited key -> false hit
PREFER: cache := Object.create(null)
```

The B-arm final patch changed the cache initialization to `Object.create(null)`; the A arm retained `{}`. A key such as `toString` can therefore only refer to an entry actually stored in B's cache. Both arms passed the task contract, and two blind judges preferred B's structure. The feedback was delivered before B's final change, but the arms were independent runs, so this example alone does not prove that the feedback caused the difference.

## Current evidence

In the latest formal evaluation, both arms passed 9/12 contract checks; one task had ambiguous acceptance criteria. Among eight pairs eligible for blind code-taste review, B won four and four tied. B used about 50% more total execution time and 77% more non-cached input tokens. This shows a positive taste signal, while the value of the extra cost remains unproven. Two Vue CSS suggestions also pointed in the wrong direction. The [formal benchmark report](benchmark/formal-v8/ROUND-8-REPORT.zh-TW.md) contains the method and limitations. These results assess an unreleased prompt on this branch, not an installed release.

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

The formal evaluation used six repository tasks and two runs per arm. A used preserved results; B was rerun independently. Only pairs where both arms passed the contract were blind reviewed. Because the Actor runs were independent, their difference cannot be attributed entirely to Provider feedback. The [formal report](benchmark/formal-v8/ROUND-8-REPORT.zh-TW.md) records the method, costs, contract ambiguity, and limitations.

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

The plugin manifest version is `0.6.0+codex.20260922164420`; this branch includes unreleased prompt changes. The code fallback model is `gpt-5.6-sol` at medium reasoning; a saved Provider selection overrides it. The evaluation above used `gpt-6-sol` at medium reasoning. Check the active selection with `provider get`.

```powershell
python masters_nudge_cli.py provider get
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```
