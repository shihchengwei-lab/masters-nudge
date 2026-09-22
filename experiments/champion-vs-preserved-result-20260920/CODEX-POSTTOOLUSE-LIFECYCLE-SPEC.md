# Interrupted synchronous `PostToolUse` emits `hook/started` without `hook/completed`

After the interrupted turn has ended, app-server consumers still see the hook run as started, with
no terminal state distinguishing cancellation from continued execution.

## Versions

- Platform: Windows 11
- Originally observed: `codex-cli 0.155.0-alpha.9.2`
- Reproduced with an isolated fixture: `codex-cli 0.155.1`

The current official documentation says synchronous command hooks are awaited before Codex
continues:
[Codex hooks documentation](https://developers.openai.com/zh-Hant/docs/hooks).

## Reproduction

The Windows reproduction used an empty working directory containing `target.txt`:

```text
before
```

`.codex/hooks.json` configured one synchronous `PostToolUse` hook:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "^apply_patch$",
        "hooks": [
          {
            "type": "command",
            "commandWindows": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .codex\\blocking-post-tool-use.ps1",
            "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .codex\\blocking-post-tool-use.ps1",
            "timeout": 180
          }
        ]
      }
    ]
  }
}
```

`.codex/blocking-post-tool-use.ps1` recorded that the hook had started, then blocked:

```powershell
$ErrorActionPreference = 'Stop'
$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$markerPath = Join-Path $PSScriptRoot 'hook-started.json'
$payload | ConvertTo-Json -Depth 20 -Compress |
    Set-Content -LiteralPath $markerPath -Encoding utf8
Start-Sleep -Seconds 180
```

The Codex app server was launched from that directory with plugins disabled:

```powershell
codex --dangerously-bypass-hook-trust `
  -c features.plugins=false `
  -c features.hooks=true `
  app-server --stdio
```

An ephemeral turn applied this patch:

```text
Call apply_patch exactly once with this exact patch and then stop:
*** Begin Patch
*** Update File: target.txt
@@
-before
+after
*** End Patch
```

After both `hook/started(postToolUse, run.id)` and `.codex/hook-started.json` were observed,
`turn/interrupt` was sent. The relevant event sequence was:

```text
apply_patch
hook/started(postToolUse, run.id)
turn/interrupt
turn/completed(status=interrupted)
```

In the verified run, the turn reached status `interrupted`, but no matching `hook/completed` was
observed for the same `run.id` during the following five seconds. Plugins were disabled, and this
was the only configured hook.

## Requested observable result

A cancelled synchronous hook run is represented by a terminal outcome with the same `run.id`,
without delivering its output to the model. The existing `core/tests/suite/hooks.rs` coverage
excludes Windows, where this reproduction was verified.

## Source locations

`core/src/hook_runtime.rs::run_post_tool_use_hooks` publishes `HookStarted` before awaiting the hook
and publishes `HookCompleted` only after the await returns. The tool remains non-terminal in
`core/src/tools/registry.rs::dispatch_any_with_terminal_outcome` during that wait, while
`core/src/tools/parallel.rs` aborts the non-terminal dispatch task on interruption. Once that task
is dropped, no remaining path publishes `HookCompleted` for the started run.

## Related issues

[#46060](https://github.com/openai/codex/issues/46060) covers Windows process-tree cleanup and
missing lifecycle events for non-builtin asynchronous hooks. This report covers a synchronous hook
that publishes `hook/started` but loses its terminal event after turn interruption.
