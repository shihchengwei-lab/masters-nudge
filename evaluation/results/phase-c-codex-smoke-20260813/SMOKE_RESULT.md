# Phase C Codex CLI smoke result

Date: 2026-08-13
Host: Windows, Codex CLI 0.147.0
Main agent: `gpt-5.6-sol`
End-to-end reviewer: Anthropic `sonnet`

## Result

The real-host transport passed for all three configured lifecycle points:

- `UserPromptSubmit` captured the prompt as a bounded task anchor with Codex
  `session_id` and `turn_id`.
- A successful real Bash tool call reached `PostToolUse`; its command and
  model-facing output were added to the host-namespaced turn journal.
- `Stop` launched the detached background worker and produced a content-free
  telemetry record without delaying the completed Codex turn.

The real-provider run also passed. Both the large-diff checkpoint and Stop
review reached Anthropic and returned schema-valid `no_finding` outcomes.
Observed reviewer latency was 8,398 ms for the checkpoint and 7,374 ms for
Stop. `host=codex_cli`, `turn_id`, routing metadata, usage, and status were
present; prompts and tool output were absent from telemetry.

The reproducible smoke command is:

```powershell
python evaluation\phase_c\run_codex_smoke.py --provider transport
```

Use `--provider anthropic` or `--provider openai` to include a reviewer call.
The script refuses to overwrite an existing repo-local `.codex/hooks.json`,
uses a temporary data directory, and removes its temporary hook file in
`finally`.

## 0.147 compatibility findings

Two release-specific behaviors were characterized instead of hidden:

1. This installed 0.147.0 build printed `async hooks are not supported yet`
   and skipped a native `async: true` Stop handler. The shipped snippet
   therefore uses a synchronous hook that only spools the payload and launches
   `hook_entry.py --detach-stop`; the reviewer still runs off the critical path.
2. A real Bash command exiting with status 7 did not emit `PostToolUse` in this
   build, although current documentation says non-zero Bash results are
   covered. Therefore immediate Codex failure checkpoints are best-effort on
   0.147. Successful tools, large-diff checkpoints, and Stop review work; when
   Codex does deliver a structured failure payload, the adapter classifies it.

These findings bound the compatibility claim. They are host-runtime behavior,
not reviewer quality results.
