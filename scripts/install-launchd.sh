#!/usr/bin/env bash
# Register the daily 09:00 local-time sync agent.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.void.cursor-plugin.sync"
DEST="$HOME/Library/LaunchAgents/${LABEL}.plist"

mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/.cache"
sed "s|__ROOT__|${ROOT}|g" "$ROOT/launchd/${LABEL}.plist" > "$DEST"

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DEST"
launchctl enable "gui/$(id -u)/${LABEL}"
echo "Installed $DEST (daily 09:00)"
echo "Manual run: launchctl kickstart -k gui/$(id -u)/${LABEL}"
