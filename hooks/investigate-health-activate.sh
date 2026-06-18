#!/usr/bin/env bash
# investigate-health-activate.sh — PreToolUse on Skill.
# When /investigate-health is invoked, set the investigation-active marker so
# orchestrator-context injects the register reminder ONLY during a real investigation.
set -eu
INPUT=$(cat)
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh" 2>/dev/null || exit 0
SKILL=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print((json.load(sys.stdin).get('tool_input',{}) or {}).get('skill',''))
except Exception: print('')" 2>/dev/null || echo "")
SESSION=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print(json.load(sys.stdin).get('session_id','no-session'))
except Exception: print('no-session')" 2>/dev/null || echo "no-session")
[ "$SKILL" = "investigate-health" ] || exit 0
touch "$(investigate_state_dir "$SESSION")/investigation-active" 2>/dev/null || true
exit 0
