# Codex issue spec: synchronous `PostToolUse` can remain permanently running after cancellation

## Proposed issue title

Synchronous `PostToolUse` can emit `HookStarted` without a terminal `HookCompleted` when its owning tool task is cancelled

## Affected version

- Platform: Windows 11
- Installed binary: `codex-cli 0.155.0-alpha.9.2`
- Matching source tag: `rust-v0.155.0-alpha.9.2`
- Matching source commit: `4607249e430dac1c961df4dc615beae88e33cec8`
- Current `origin/main` inspected at: `5c5308fc9a9ee789049d646ef11e5400384b9c6f`

The relevant cancellation and command-runner behavior is still present on the inspected `origin/main`.

The documented contract says synchronous command hooks are awaited before Codex continues and that
their configured `timeout` is measured in seconds:
[Codex hooks documentation](https://developers.openai.com/zh-Hant/docs/hooks).

## Expected lifecycle behavior

After Codex publishes `HookStarted(run.id)`, it must publish exactly one terminal
`HookCompleted` with the same `run.id`.

Cancellation is a terminal outcome. It must not be represented by dropping the only future that can
publish `HookCompleted`.

For a cancelled synchronous command hook, the observable result must:

- be terminal rather than remain `Running`
- identify cancellation as the outcome
- include complete timing fields
- deliver no feedback, additional context, or block decision from the cancelled hook

## Observed behavior

A real Codex run executed `apply_patch`, entered the Masters' Nudge synchronous `PostToolUse` hook,
and persisted these events for one batch:

```text
11:22:41.925  queued   batch afb00aed26044accaefd6c0d3573a54c
11:22:41.929  started  batch afb00aed26044accaefd6c0d3573a54c
```

No `feedback`, `silence`, or `fault` terminal event followed. The Actor continued and completed its
task. The batch therefore remained unresolved even though the hook's configured timeout was 180
seconds and the Provider's internal timeout was 90 seconds.

Replaying the exact recorded hook payload directly, outside the Codex hook host, completed normally:

```json
{
  "elapsed_seconds": 16.265,
  "returncode": 0,
  "stdout": "",
  "stderr": ""
}
```

This separates the hook payload and Provider execution from the Codex-owned cancellation boundary.
The initiating cancellation source in this particular run has not been identified.

## Static cause

The source currently has this ownership chain:

1. `core/src/hook_runtime.rs::run_post_tool_use_hooks` publishes `HookStarted`.
2. The same future awaits `hooks.run_post_tool_use(request)`.
3. Only after that await returns can the same future publish `HookCompleted`.
4. `core/src/tools/registry.rs::dispatch_any_with_terminal_outcome` runs the synchronous
   `PostToolUse` hook before it marks the tool's terminal outcome.
5. `core/src/tools/parallel.rs` sees the terminal flag as false during the hook. When the turn's
   cancellation token fires, it aborts the whole dispatch task.
6. Aborting the dispatch task drops the hook future.
7. `hooks/src/engine/command_runner.rs::ProcessTreeGuard::drop` attempts to terminate the command
   process tree, but no value returns to `run_post_tool_use_hooks`.
8. The only code that could publish `HookCompleted` has been dropped.

The captured process stopped, but lifecycle completion has no surviving owner. The state
`HookStarted without HookCompleted` is therefore legal in the current control flow.

## Acceptance criteria

When a synchronous command hook is cancelled because its owning tool or turn is aborted:

1. Every published `HookStarted(run.id)` has exactly one terminal `HookCompleted` with the same
   `run.id`.
2. The terminal event identifies cancellation and contains complete timing fields.
3. The cancelled hook contributes no feedback, additional context, or block decision to the model.
4. No hook run remains permanently `Running` after the owning tool or turn has ended.

## Acceptance test

Add a cross-platform integration test with Windows coverage. The current
`core/tests/suite/hooks.rs` module is excluded by `#[cfg(not(target_os = "windows"))]`, so this test
must live in a test surface that actually runs on Windows; removing the guard from the entire existing
suite is not required.

Test sequence:

1. Configure a synchronous `PostToolUse` command hook for `apply_patch`.
2. The hook writes a marker after reading stdin, then blocks longer than the test window.
3. Execute `apply_patch` and wait for `HookStarted` plus the marker.
4. Interrupt the active turn.
5. Assert exactly one terminal `HookCompleted` with the same `run.id` is emitted.
6. Assert the result identifies cancellation and its timing fields are complete.
7. Assert no hook feedback, additional context, or block decision is delivered to the model.

Suggested test name:

```text
interrupted_post_tool_use_emits_terminal_hook_event
```

## Scope boundaries

This report does not claim to identify what initiated the cancellation in the captured run. It does
identify the Codex-owned lifecycle defect that turns any such cancellation into an unresolved public
hook state.

This is distinct from:

- [#46060](https://github.com/openai/codex/issues/46060), which covers Windows process-tree cleanup
  and missing lifecycle reporting for asynchronous hooks.
- [#32974](https://github.com/openai/codex/issues/32974), which covers a broader CLI exit while
  waiting on a tool and was also observed without hooks.

## Local evidence

- local-only `PARTIAL.zh-TW.md`: experiment stop record
- `replay_fault.py`: exact-payload replay driver
- `%TEMP%/mn-ab-preserved-result-expanded-20260920-v2/fault-replay/result.json`: replay result
- `%TEMP%/mn-ab-preserved-result-expanded-20260920-v2/runs/django__django-12273/repeat-1/B/masters-nudge-data/feedback.sqlite3`: queued/started facts
- `%TEMP%/masters-nudge-provider-nljnlujk/reads.jsonl`: Provider process reached repository reads before the host ended it
