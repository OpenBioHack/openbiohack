#!/usr/bin/env bash
# investigate-health-read-log.sh — PostToolUse on Read.
# Records every Read into the session-read-log (anchored to the run-root mirror too).
#
# F4 — scope guard unified onto investigate_is_active (+ INVESTIGATE_SCOPE_OVERRIDE).
# F6 — newline-safe single-pass parse (no positional `sed`).
# F7 — dedup happens inside investigate_record_read_anchored.

set -eu

INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
. "$HOOK_DIR/lib/investigate-parse.sh"

ih_parse_input "$INPUT"
[ "$IH_PARSE_OK" = "1" ] || exit 0

# --- scope guard: only inside an active investigate run ---
investigate_is_active "$IH_CWD" "$IH_FILE_PATH" || exit 0

if [ -n "$IH_FILE_PATH" ] && [ -n "$IH_SESSION" ]; then
    investigate_record_read_anchored "$IH_SESSION" "$IH_FILE_PATH" "$IH_FILE_PATH"
fi

exit 0
