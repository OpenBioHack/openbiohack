#!/usr/bin/env bash
# investigate-health-cleanup-block.sh — PreToolUse on Bash.
# Blocks rm/mv/rmdir/git-clean against investigate-health artifacts until finish-line token.

set -eu

INPUT=$(cat)


HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

PARSED=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {}) or {}
print(d.get('session_id', ''))
print(ti.get('command', ''))
" 2>/dev/null) || exit 0

SESSION=$(printf '%s' "$PARSED" | sed -n '1p')
CMD=$(printf '%s' "$PARSED" | sed -n '2p')

case "$CMD" in
    rm\ *|*\ rm\ *|mv\ *|*\ mv\ *|rmdir\ *|*\ rmdir\ *|*git\ clean*) ;;
    *) exit 0 ;;
esac

case "$CMD" in
    *extracted/*|*working-hypothesis*|*step5-cross-check*|*hypothesis-set*|*shared-node-inventory*|*step6-prioritize*|*offering.md*|*decision-log*|*question-bank*) ;;
    *) exit 0 ;;
esac

if investigate_has_finish_line_token "$SESSION"; then
    bash "$LOGGER" "investigate-health-cleanup-block" "bash" "session=$SESSION" "allow-post-finish-line" 2>/dev/null || true
    exit 0
fi

REASON="Mid-run cleanup blocked. Cleanup of investigate-health artifacts is forbidden until the Step 7 audit-council issues a finish-line pass token. Rule: investigate-health SKILL.md How the loop is actually run / No cleanup mid-run. A mid-run rm/mv/rmdir against extracted/, working-hypothesis, step5-cross-check, hypothesis-set, shared-node-inventory, step6-prioritize, offering.md, decision-log, or question-bank can silently delete something the audit will look for, converting a recoverable mistake into an undetectable one. Command attempted: $CMD. To proceed: complete the run through Step 7 finish-line. The audit-council issues finish-line.token via audit-council-completion.sh <session> finish-line <claim-id>; cleanup is then permitted as a single named end-of-run step."

bash "$LOGGER" "investigate-health-cleanup-block" "bash" "session=$SESSION" "deny" 2>/dev/null || true

python3 -c "
import json, sys
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': sys.argv[1]
    }
}))" "$REASON"
exit 0
