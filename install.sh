#!/bin/bash
# Masters' Nudge — install
# Installs the shared runtime and optional Claude Code/Codex CLI adapters.
# It deliberately never edits either host's settings file.
# Legacy Claude compatibility target: ~/.claude/scripts/buddy

set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${BUDDY_TARGET_DIR:-$HOME/.claude/scripts/buddy}"
RUNTIME_DIR="${MASTERS_NUDGE_RUNTIME_DIR:-$HOME/.masters-nudge/runtime}"
HOST="${1:---all}"

case "$HOST" in
  --all|--claude|--codex) ;;
  *) echo "Usage: ./install.sh [--all|--claude|--codex]" >&2; exit 2 ;;
esac

echo "Masters’ Nudge — install"
echo "Source:  $SRC_DIR"
echo "Runtime: $RUNTIME_DIR"
echo ""

mkdir -p "$RUNTIME_DIR/masters_nudge" "$RUNTIME_DIR/personas"
cp "$SRC_DIR/hook_entry.py" "$RUNTIME_DIR/"
cp "$SRC_DIR/source_context.py" "$RUNTIME_DIR/"
cp "$SRC_DIR/persona_config.py" "$RUNTIME_DIR/"
cp "$SRC_DIR/lens_router.py" "$RUNTIME_DIR/"
cp "$SRC_DIR/review_telemetry.py" "$RUNTIME_DIR/"
cp "$SRC_DIR/buddy-prompt.txt" "$RUNTIME_DIR/"
cp "$SRC_DIR/reaction-schema.json" "$RUNTIME_DIR/"
cp "$SRC_DIR/codex-hooks-snippet.json" "$RUNTIME_DIR/"
cp "$SRC_DIR/masters_nudge/"*.py "$RUNTIME_DIR/masters_nudge/"
cp "$SRC_DIR/personas/"*.txt "$RUNTIME_DIR/personas/"

if [[ "$HOST" == "--all" || "$HOST" == "--claude" ]]; then
mkdir -p "$TARGET_DIR"

cp "$SRC_DIR/buddy.sh" "$TARGET_DIR/"
cp "$SRC_DIR/buddy.py" "$TARGET_DIR/"
cp "$SRC_DIR/checkpoint.sh" "$TARGET_DIR/"
cp "$SRC_DIR/checkpoint.py" "$TARGET_DIR/"
cp "$SRC_DIR/source_context.py" "$TARGET_DIR/"
cp "$SRC_DIR/persona_config.py" "$TARGET_DIR/"
cp "$SRC_DIR/lens_router.py" "$TARGET_DIR/"
cp "$SRC_DIR/review_telemetry.py" "$TARGET_DIR/"
cp "$SRC_DIR/inject.sh" "$TARGET_DIR/"
cp "$SRC_DIR/inject.py" "$TARGET_DIR/"
cp "$SRC_DIR/buddy-prompt.txt" "$TARGET_DIR/"
cp "$SRC_DIR/reaction-schema.json" "$TARGET_DIR/"
cp -R "$SRC_DIR/personas" "$TARGET_DIR/"
cp "$SRC_DIR/buddy_window.py" "$TARGET_DIR/"
cp "$SRC_DIR/start_buddy_window.bat" "$TARGET_DIR/"
cp "$SRC_DIR/spritesheet.webp" "$TARGET_DIR/"
cp -R "$SRC_DIR/masters_nudge" "$TARGET_DIR/"

chmod +x "$TARGET_DIR/buddy.sh" "$TARGET_DIR/checkpoint.sh" "$TARGET_DIR/inject.sh" 2>/dev/null || true
fi

echo "Installed:"
ls -la "$RUNTIME_DIR"
echo ""
echo "Next:"
echo "  Claude Code: merge settings-snippet.json into ~/.claude/settings.json."
echo "  Codex CLI: merge $RUNTIME_DIR/codex-hooks-snippet.json into ~/.codex/hooks.json,"
echo "             then trust the hooks in /hooks (or use the documented trust flag)."
echo "  Reactions and metadata are written to ~/.masters-nudge/data by default."
echo "  Optional UI: launch $TARGET_DIR/start_buddy_window.bat on Windows."
