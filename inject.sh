#!/bin/bash
# Buddy_similar — UserPromptSubmit hook entry
#
# Reads pending Buddy reactions from buddy.log and prints them to stdout,
# which Claude Code appends as additional context to the user's next prompt.
#
# Recursion guard: BUDDY_ACTIVE=1 set by buddy.py during its inner claude call.

set -uo pipefail
export PYTHONIOENCODING=utf-8

[[ "${BUDDY_ACTIVE:-}" == "1" ]] && exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INJECT_PY="$SCRIPT_DIR/inject.py"
ERROR_LOG="${BUDDY_CLAUDE_DIR:-$HOME/.claude}/buddy-error.log"

PYTHON_CMD=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    PYTHON_CMD="$c"
    break
  fi
done
[[ -z "$PYTHON_CMD" ]] && exit 0
[[ ! -f "$INJECT_PY" ]] && exit 0

# Pipe the UserPromptSubmit JSON input through to inject.py — it needs
# session_id from the hook input to read the per-session log.
INPUT=$(head -c 1048576)
echo "$INPUT" | "$PYTHON_CMD" "$INJECT_PY" 2>>"$ERROR_LOG" || true

exit 0
