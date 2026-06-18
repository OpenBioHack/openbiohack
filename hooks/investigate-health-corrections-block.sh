#!/usr/bin/env bash
# investigate-health-corrections-block.sh — PreToolUse on any tool.
#
# Enforces the patch-then-rerun rule: if a previous Write referenced a deferral on a
# skill artifact path, the very next tool call must be Edit on that path.

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
print(d.get('tool_name', ''))
print(ti.get('file_path', ''))
print('---CONTENT---')
c = ti.get('content', '') or ti.get('new_string', '')
print(c)
" 2>/dev/null) || exit 0

SESSION=$(printf '%s' "$PARSED" | sed -n '1p')
TOOL=$(printf '%s' "$PARSED" | sed -n '2p')
FILE_PATH=$(printf '%s' "$PARSED" | sed -n '3p')
CONTENT=$(printf '%s' "$PARSED" | sed -n '/^---CONTENT---$/,$p' | tail -n +2)

deny() {
    local reason="$1"
    bash "$LOGGER" "investigate-health-corrections-block" "$TOOL" "session=$SESSION" "deny" 2>/dev/null || true
    python3 -c "
import json, sys
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': sys.argv[1]
    }
}))" "$reason"
    exit 0
}

# (1) Check pending-patch FIRST — gates any non-conforming next call
PENDING=$(investigate_get_pending_patch "$SESSION" 2>/dev/null || true)
if [ -n "$PENDING" ]; then
    if [ "$TOOL" = "Edit" ] && [ "$FILE_PATH" = "$PENDING" ]; then
        investigate_clear_pending_patch "$SESSION"
        bash "$LOGGER" "investigate-health-corrections-block" "$TOOL" "session=$SESSION patch-cleared=$PENDING" "allow" 2>/dev/null || true
    else
        deny "Pending patch: a previous Write referenced a deferral on skill artifact $PENDING but did not patch it. Rule: investigate-health SKILL.md Caught mistakes are root-caused, not memo'd / Patch-then-rerun. The next tool call after catching an upstream bug must be Edit on the named upstream artifact — deferring to next round = the catch doesn't count. To proceed: run Edit on $PENDING with the fix, then the flag clears. If the deferral wording was a false positive, edit the prior Write to remove it."
    fi
fi

# (2) Scan Writes/Edits for deferral + skill-path combo
if [ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ]; then
    HAS_DEFERRAL=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re
text = sys.stdin.read()
patterns = [
    r'to be patched in Round',
    r'logged for future',
    r'memo only',
    r'deferred to next round',
    r'Round [0-9]+ scope',
    r'suggested rewrite.*later',
    r'will patch.*next session',
]
for p in patterns:
    if re.search(p, text, re.I):
        print('deferral')
        sys.exit(0)
sys.exit(1)
" 2>/dev/null && echo yes) || true

    if [ "$HAS_DEFERRAL" = "yes" ]; then
        SKILL_PATH=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re, os
text = sys.stdin.read()
m = re.search(r'(~?/?(?:Users/[^/\s]+/)?\.claude/skills/[A-Za-z0-9_./-]+\.md)', text)
if m:
    p = os.path.expanduser(m.group(1))
    if not p.startswith('/'):
        p = '/' + p.lstrip('./')
    print(p)
" 2>/dev/null) || true
        if [ -n "$SKILL_PATH" ]; then
            investigate_set_pending_patch "$SESSION" "$SKILL_PATH"
            bash "$LOGGER" "investigate-health-corrections-block" "$TOOL" "session=$SESSION pending-set=$SKILL_PATH" "warn" 2>/dev/null || true
        fi
    fi
fi

exit 0
