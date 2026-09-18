# Masters’ Nudge

English | [繁體中文](README.zh-TW.md)

Small engineering feedback after the Actor changes code. [SPEC.zh-TW.md](SPEC.zh-TW.md) is the authority;
[refactor acceptance](docs/spec-refactor-progress.zh-TW.md) records current verification.

UserPromptSubmit records the task without calling a Provider. Each successful `apply_patch` starts one OpenAI/Codex
judgment through native PostToolUse with the completed patch, its result, and the updated workspace. The Provider uses one Linus Torvalds anchor and six checks, optionally searching or
reading related repository files through read-only MCP tools. The Actor owns implementation and verification.

Each user-message round stops at three feedbacks or two silences. New requests reset the allowance; latest conflicting
requirements win. Failures are visible and never counted as silence.

Requires Python 3.10+, Git, a logged-in Codex Provider, and an Actor runtime exposing UserPromptSubmit/PostToolUse
with turn_id. Opaque shell mutations are unsupported. Claude and Ollama are suspended; no fallback is used.
PostToolUse event support and feedback delivery must be verified in the actual Codex runtime.

The five optional material categories and all MCP reads share one budget. Evidence is verified against the exact
source and location received during that judgment. Only the short fact, relationship and question reach the Actor.

Task, change, tool-result and selected repository materials are sent to OpenAI. The MCP cannot write files or read
outside the repository, Git internals, or ignored files. Attempt records are stored under .masters-nudge/data in the
user directory. A recorded delivery is not evidence of Actor adoption.

```powershell
python masters_nudge_cli.py provider get
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

The source tree owns the implementation; plugin copies are generated. Test mode (MASTERS_NUDGE_TEST_MODE=1) marks
faulted trials invalid; the test runner must stop, not score Actor output. Historical experiments are not acceptance
evidence for this refactor.
