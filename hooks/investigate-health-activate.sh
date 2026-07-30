#!/usr/bin/env bash
# investigate-health-activate.sh — PreToolUse on Skill.
#
# When /investigate-health is invoked, inject an activation reminder:
#   - no active run at/under cwd  -> remind the model to write the
#     <root>/.investigate-active marker FIRST (bootstrap step 1b), once, with
#     the Write tool — the marker is what arms every enforcement hook.
#   - a run is already active     -> remind the model the marker exists and is
#     kernel-locked (chflags uchg): do NOT rewrite it (write-once; a rewrite
#     fails with EPERM), just resume.
# Idempotent and immutability-aware: this hook never writes the marker itself
# and never drives a Write into a locked marker. The skill invocation is never
# blocked — the output is additionalContext only.
set -eu
INPUT=$(cat)
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh" 2>/dev/null || exit 0
. "$HOOK_DIR/lib/investigate-parse.sh" 2>/dev/null || exit 0

SKILL=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print((json.load(sys.stdin).get('tool_input',{}) or {}).get('skill',''))
except Exception: print('')" 2>/dev/null || echo "")
[ "$SKILL" = "investigate-health" ] || exit 0

ih_parse_input "$INPUT"
[ "$IH_PARSE_OK" = "1" ] || exit 0

if investigate_cwd_has_active_run "$IH_CWD" 2>/dev/null; then
    CTX="INVESTIGATE-HEALTH ACTIVATION — a run is already ACTIVE at/under this directory: its .investigate-active marker exists and is kernel-locked (chflags uchg). Do NOT rewrite the marker (write-once; a rewrite fails with EPERM and is never needed). Re-read the decision log and resume from the last logged step."
else
    CTX="INVESTIGATE-HEALTH ACTIVATION — before any other step: choose the run root <root> and write the <root>/.investigate-active activation marker (bootstrap step 1b) ONCE, with the Write tool. The marker arms every enforcement hook for the whole run and is kernel-locked on write; never rewrite it. Then proceed with bootstrap."
fi

python3 -c "import json,sys; print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','additionalContext':sys.argv[1]}}))" "$CTX"
exit 0
