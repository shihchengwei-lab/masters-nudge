#!/bin/bash
# Buddy_similar — Stop hook entry
#
# Triggered after every Claude Code session turn.
# Pipes the hook input JSON to buddy.py, which calls the Claude CLI as Cinder.
#
# Recursion guard: BUDDY_ACTIVE=1 set by buddy.py before the inner claude call.
# Inner Stop hook re-enters this script, sees the flag, exits immediately.

set -uo pipefail
export PYTHONIOENCODING=utf-8

# --- Recursion guard ---
[[ "${BUDDY_ACTIVE:-}" == "1" ]] && exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUDDY_PY="$SCRIPT_DIR/buddy.py"
ERROR_LOG="${BUDDY_CLAUDE_DIR:-$HOME/.claude}/buddy-error.log"

# --- Resolve Python ---
PYTHON_CMD=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    PYTHON_CMD="$c"
    break
  fi
done
if [[ -z "$PYTHON_CMD" ]]; then
  echo "buddy: python not found" >&2
  exit 0  # Never block hook
fi

# --- Engine must exist ---
if [[ ! -f "$BUDDY_PY" ]]; then
  echo "buddy: $BUDDY_PY not found" >&2
  exit 0
fi

# --- Read hook input (1 MB cap) ---
INPUT=$(head -c 1048576)

# --- Fire buddy.py in background, return immediately ---
# Tradeoff: zero perceived latency for the user, but if the next prompt is
# submitted before buddy.py finishes (typically 5-15s on Sonnet), that turn's
# buddy reaction surfaces on the turn AFTER, not the next one.
( echo "$INPUT" | "$PYTHON_CMD" "$BUDDY_PY" >/dev/null 2>>"$ERROR_LOG" ) &
disown 2>/dev/null || true

exit 0
