#!/bin/bash
# Masters' Nudge — UserPromptSubmit hook entry
#
# Reads pending nudges from the legacy-compatible buddy log and prints them,
# which Claude Code appends as additional context to the user's next prompt.
#
# Recursion guard: both new and legacy variable names are supported.

set -uo pipefail
export PYTHONIOENCODING=utf-8

[[ "${MASTERS_NUDGE_ACTIVE:-}" == "1" || "${BUDDY_ACTIVE:-}" == "1" ]] && exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INJECT_PY="$SCRIPT_DIR/inject.py"
if [[ -n "${MASTERS_NUDGE_DATA_DIR:-}" ]]; then
  ERROR_LOG="$MASTERS_NUDGE_DATA_DIR/error.log"
elif [[ -n "${BUDDY_CLAUDE_DIR:-}" ]]; then
  ERROR_LOG="$BUDDY_CLAUDE_DIR/buddy-error.log"
else
  ERROR_LOG="$HOME/.masters-nudge/data/error.log"
fi
mkdir -p "$(dirname "$ERROR_LOG")" 2>/dev/null || true

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
# Only append stderr if error log is under 256 KB (matches Python-side rotation)
LOG_SIZE=$(stat -c%s "$ERROR_LOG" 2>/dev/null || stat -f%z "$ERROR_LOG" 2>/dev/null || echo 0)
if [[ "$LOG_SIZE" -lt 262144 ]]; then
  echo "$INPUT" | "$PYTHON_CMD" "$INJECT_PY" 2>>"$ERROR_LOG" || true
else
  echo "$INPUT" | "$PYTHON_CMD" "$INJECT_PY" 2>/dev/null || true
fi

exit 0
