#!/bin/sh
# Load the daily 06:00 local Helsinki extract agent into launchd.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
LABEL="ai.helsinki-large-buildings.extractor"
SRC="$ROOT/schedule/${LABEL}.plist"
DEST="$HOME/Library/LaunchAgents/${LABEL}.plist"
UID_NUM="$(id -u)"

mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/data/cache"
cp "$SRC" "$DEST"
launchctl bootout "gui/${UID_NUM}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${UID_NUM}" "$DEST"
launchctl enable "gui/${UID_NUM}/${LABEL}"
echo "Loaded ${LABEL} — daily 06:00 local, runs python3 agent.py"
launchctl print "gui/${UID_NUM}/${LABEL}" | sed -n '1,40p'
