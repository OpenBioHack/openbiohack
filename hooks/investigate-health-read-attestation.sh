#!/usr/bin/env bash
# investigate-health-read-attestation.sh — PreToolUse on Write|Edit.
# Denies a gated synthesis write while any research/*.md or graphs/*.md file that
# exists for the run is NOT in the session read-log. Enforces "always read the
# actual document; never synthesise from a summary." Issues a signed read-attest
# token on completeness (same HMAC lib as the audit-council).
#
# F4 — scope guard unified onto investigate_is_active (+ INVESTIGATE_SCOPE_OVERRIDE).
# F6 — newline-safe single-pass parse (no positional `sed`).
set -eu
INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
. "$HOOK_DIR/lib/investigate-parse.sh"
. "$HOOK_DIR/lib/skill-token-lib.sh" 2>/dev/null || true

ih_parse_input "$INPUT"
[ "$IH_PARSE_OK" = "1" ] || exit 0
SESSION="$IH_SESSION"
FILE_PATH="$IH_FILE_PATH"
BASE="$(basename "$FILE_PATH" 2>/dev/null || echo "")"

# scope guard — only inside an active investigate run
investigate_is_active "$IH_CWD" "$FILE_PATH" || exit 0

# only gate the synthesis files
case "$BASE" in
  working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md|offering-draft.md) ;;
  *) exit 0 ;;
esac

ROOT="$(dirname "$FILE_PATH")"
# required raw inputs = top-level research/*.md and graphs/*.md that exist (exclude bak/subdirs)
UNREAD=""
COUNT=0; READN=0
for d in "$ROOT/research" "$ROOT/graphs"; do
  [ -d "$d" ] || continue
  for f in "$d"/*.md; do
    [ -e "$f" ] || continue
    case "$f" in *.bak*|*"/_"*) continue ;; esac
    COUNT=$((COUNT+1))
    if investigate_was_read_anchored "$SESSION" "$f" "$FILE_PATH"; then
      READN=$((READN+1))
    else
      UNREAD="$UNREAD
  - $f"
    fi
  done
done

if [ -n "$UNREAD" ]; then
  REASON="Read-attestation gate: refusing to write ${BASE}. The orchestrator must READ every research/ and graphs/ file before synthesising from it (investigate-health SKILL.md 'No summaries, ever' / 'four hard rules'). These required files exist on disk but are NOT in this session's read-log — open each with the Read tool first:${UNREAD}
($READN of $COUNT required files read.) Grep/awk/task-notification text do NOT count as a Read. This prevents synthesising from agent summaries instead of the raw documents."
  python3 -c "
import json, sys
print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':sys.argv[1]}}))" "$REASON"
  exit 0
fi

# complete: issue a signed read-attestation token (best-effort; read-log is source of truth)
if command -v issue_token >/dev/null 2>&1; then
  GATE="read-attest-${BASE%.md}"
  if TOK=$(issue_token "$GATE" 2>/dev/null); then
    D="$(investigate_state_dir "$SESSION")"
    printf '%s\n' "$TOK" > "$D/audit-tokens/${GATE}.token" 2>/dev/null || true
  fi
fi
exit 0
