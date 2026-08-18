#!/usr/bin/env bash
# Symlink this repo into Cursor's local plugin directory.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCAL_DIR="$HOME/.cursor/plugins/local"
TARGET="$LOCAL_DIR/cursor-plugin"
OLD="$LOCAL_DIR/mattpocock-skills"

mkdir -p "$LOCAL_DIR"

if [[ -L "$OLD" || -d "$OLD" ]]; then
  echo "Removing previous local plugin $OLD (avoid duplicate skills)"
  rm -rf "$OLD"
fi

ln -sfn "$ROOT" "$TARGET"
echo "Linked $TARGET -> $ROOT"
echo "Reload Cursor (Developer: Reload Window) to pick up the plugin."
