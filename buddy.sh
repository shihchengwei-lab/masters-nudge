#!/bin/bash
# Buddy_similar — Stop hook entry
#
# Triggered after every Claude Code session turn.
# Pipes the hook input JSON to buddy.py, which calls the Claude CLI as Buddy.
#
# Recursion guard: BUDDY_ACTIVE=1 set by buddy.py before the inner claude call.
# Inner Stop hook re-enters this script, sees the flag, exits immediately.

set -uo pipefail
export PYTHONIOENCODING=utf-8

# --- Recursion guard ---
[[ "${BUDDY_ACTIVE:-}" == "1" ]] && exit 0

# --- Hook duration instrumentation (T_START captured after recursion guard
#     so guard exits don't pollute the measurement) ---
T_START=$(date +%s%3N)

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

# --- Run buddy.py synchronously ---
# Background execution is handled by Claude Code's native async: true in
# settings-snippet.json. No need to fork here.
echo "$INPUT" | "$PYTHON_CMD" "$BUDDY_PY" >/dev/null 2>>"$ERROR_LOG"

# --- Log hook duration ---
T_END=$(date +%s%3N)
echo "[$(date -Iseconds)] buddy.sh: hook duration $((T_END - T_START))ms" >> "$ERROR_LOG"

exit 0
