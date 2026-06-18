#!/usr/bin/env bash
# investigate-health-read-log.sh — PostToolUse on Read.
# Records every Read into the session-read-log.

set -eu

INPUT=$(cat)


HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"

PARSED=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {}) or {}
print(d.get('session_id', ''))
print(ti.get('file_path', ''))
" 2>/dev/null) || exit 0

SESSION=$(printf '%s' "$PARSED" | sed -n '1p')
FILE_PATH=$(printf '%s' "$PARSED" | sed -n '2p')

if [ -n "$FILE_PATH" ] && [ -n "$SESSION" ]; then
    investigate_record_read "$SESSION" "$FILE_PATH"
fi

exit 0
