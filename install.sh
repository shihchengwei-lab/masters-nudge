#!/bin/bash
# Masters' Nudge — install
# Copies scripts to ~/.claude/scripts/buddy/.
# After this, you still need to merge settings-snippet.json into
# ~/.claude/settings.json. install.sh does NOT touch settings.json.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${BUDDY_TARGET_DIR:-$HOME/.claude/scripts/buddy}"

echo "Masters’ Nudge — install"
echo "Source:  $SRC_DIR"
echo "Target:  $TARGET_DIR"
echo ""

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

chmod +x "$TARGET_DIR/buddy.sh" "$TARGET_DIR/checkpoint.sh" "$TARGET_DIR/inject.sh" 2>/dev/null || true

echo "Installed:"
ls -la "$TARGET_DIR"
echo ""
echo "Next:"
echo "  1. Open ~/.claude/settings.json"
echo "  2. Merge the contents of settings-snippet.json into the 'hooks' section."
echo "  3. Test with a Claude Code tool failure or a >80-line diff — checkpoint"
echo "     nudges inject directly into the main agent. Stop reactions still land"
echo "     in ~/.claude/buddy/<session_id>.log for next-prompt injection."
echo "  4. Optional: double-click $TARGET_DIR/start_buddy_window.bat"
echo "     to open the floating window that tails reactions live."
