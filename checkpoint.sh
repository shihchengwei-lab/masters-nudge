#!/bin/bash
# Masters' Nudge — synchronous mid-work checkpoint hook entry

set -uo pipefail
export PYTHONIOENCODING=utf-8

[[ "${BUDDY_ACTIVE:-}" == "1" ]] && exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHECKPOINT_PY="$SCRIPT_DIR/checkpoint.py"
ERROR_LOG="${BUDDY_CLAUDE_DIR:-$HOME/.claude}/buddy-error.log"

PYTHON_CMD=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    PYTHON_CMD="$c"
    break
  fi
done
[[ -z "$PYTHON_CMD" ]] && exit 0
[[ ! -f "$CHECKPOINT_PY" ]] && exit 0

INPUT=$(head -c 1048576)
LOG_SIZE=$(stat -c%s "$ERROR_LOG" 2>/dev/null || echo 0)
if [[ "$LOG_SIZE" -lt 262144 ]]; then
  echo "$INPUT" | "$PYTHON_CMD" "$CHECKPOINT_PY" 2>>"$ERROR_LOG" || true
else
  echo "$INPUT" | "$PYTHON_CMD" "$CHECKPOINT_PY" 2>/dev/null || true
fi

exit 0
