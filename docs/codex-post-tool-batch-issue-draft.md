# Add a hook after all tool calls from one assistant response complete

## Problem

Codex currently invokes `PostToolUse` once per tool result. When one assistant
response issues parallel tool calls, each hook invocation sees only a partial
set of results.

A hook cannot reliably act on the complete set before the next model inference
without guessing batch boundaries.

## Requested behavior

Add a batch-level hook that runs exactly once after all tool calls from one
assistant response have completed and before the next model inference.

The hook input should include every tool call and its result, including failures,
cancellations, and interruptions. Context returned by the hook should be
included in the immediately following model inference.

The same event should be emitted for assistant responses containing a single
tool call, so consumers have one consistent control point.

## Acceptance example

If one assistant response launches three tools in parallel:

1. Codex emits the existing `PostToolUse` event for each result.
2. After all three resolve, Codex emits one batch-level event containing all
   three calls and results.
3. Context returned by that event is present in the immediately following model
   inference.

The batch-level event is not emitted early or more than once.

Related: #21753 tracks `PostToolBatch` as a missing hook at the umbrella level.
