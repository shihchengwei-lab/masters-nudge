# Independent reproduction

Requirements: Windows, Python 3, and an authenticated `codex` CLI on `PATH`.

Run:

```powershell
python reproduce.py
```

The script starts the official `codex app-server`, disables plugins, creates an ephemeral thread,
executes one `apply_patch`, waits for the blocking `PostToolUse` hook to start, and sends
`turn/interrupt`. It then counts terminal events for the started hook run.

Exit code `0` means the defect was reproduced: the turn reached status `interrupted`, but the
matching `hook/completed` event was absent. This fixture imports no Masters' Nudge code and invokes
no Masters' Nudge hook or Provider.
