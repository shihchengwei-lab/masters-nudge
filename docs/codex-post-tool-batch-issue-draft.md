# Codex issue draft: add a pre-model `PostToolBatch` hook

Status: local draft only; not submitted.

## Suggested title

Add `PostToolBatch` after one model step's tools finish and before the next model request

## Problem

`PostToolUse` is a useful synchronous control point for a single tool call. When
one model step launches parallel tools, however, each callback sees only one
result. A hook cannot know that the complete set is ready without timers,
transcript guesses, or host-specific aggregation. Those workarounds either act
on partial evidence or delay context until the intended decision boundary has
already passed.

## Proposed hook

Trigger `PostToolBatch` exactly once after every tool call selected by one model
step has resolved, and before Codex constructs the next model request.

Suggested input:

```json
{
  "hook_event_name": "PostToolBatch",
  "session_id": "...",
  "turn_id": "...",
  "cwd": "...",
  "tool_calls": [
    {
      "tool_name": "...",
      "tool_input": {},
      "tool_use_id": "...",
      "tool_response": {}
    }
  ]
}
```

Requirements:

- preserve the model step's tool-call order;
- include success, failure, cancellation, and interruption results;
- run once for a one-tool step as well as a parallel batch;
- accept `hookSpecificOutput.additionalContext` for the next model request;
- remain synchronous and fail open if the hook errors or times out;
- document whether hosted and local tools are included.

## Why this is distinct from `PostToolUse`

The requested boundary is not a convenience alias. It guarantees that evidence
from the current model step is complete while the next model decision is still
changeable. Per-tool callbacks cannot provide both properties for parallel tool
calls.

## Acceptance example

If one model step launches three tools in parallel, Codex emits three existing
`PostToolUse` events as today and one ordered `PostToolBatch` containing all
three results. Context returned by `PostToolBatch` is present in the immediately
following model request. No batch event is emitted early or more than once.
