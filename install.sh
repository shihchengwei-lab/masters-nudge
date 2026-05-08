#!/bin/bash
# Buddy_similar — install
# Copies scripts to ~/.claude/scripts/buddy/.
# After this, you still need to merge settings-snippet.json into
# ~/.claude/settings.json. install.sh does NOT touch settings.json.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${BUDDY_TARGET_DIR:-$HOME/.claude/scripts/buddy}"

echo "Buddy_similar — install"
echo "Source:  $SRC_DIR"
echo "Target:  $TARGET_DIR"
echo ""

mkdir -p "$TARGET_DIR"

cp "$SRC_DIR/buddy.sh" "$TARGET_DIR/"
cp "$SRC_DIR/buddy.py" "$TARGET_DIR/"
cp "$SRC_DIR/inject.sh" "$TARGET_DIR/"
cp "$SRC_DIR/inject.py" "$TARGET_DIR/"
cp "$SRC_DIR/cinder-prompt.txt" "$TARGET_DIR/"
cp "$SRC_DIR/buddy_window.py" "$TARGET_DIR/"
cp "$SRC_DIR/start_buddy_window.bat" "$TARGET_DIR/"

chmod +x "$TARGET_DIR/buddy.sh" "$TARGET_DIR/inject.sh" 2>/dev/null || true

echo "Installed:"
ls -la "$TARGET_DIR"
echo ""
echo "Next:"
echo "  1. Open ~/.claude/settings.json"
echo "  2. Merge the contents of settings-snippet.json into the 'hooks' section."
echo "  3. Test by running any Claude Code turn — Buddy reactions land in"
echo "     ~/.claude/buddy/<session_id>.log and inject into your next prompt."
echo "  4. Optional: double-click $TARGET_DIR/start_buddy_window.bat"
echo "     to open the floating window that tails reactions live."
