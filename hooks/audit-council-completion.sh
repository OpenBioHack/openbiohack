#!/usr/bin/env bash
# audit-council-completion.sh — token issuer for the investigate-health audit-council.
#
# Called by the orchestrator (NOT a hook) after a council aggregation produces a
# confident verdict (per references/council/aggregation-rule.md). Issues an
# HMAC-signed token to /tmp/claude/.investigate-state-<session>/audit-tokens/<gate>.token
# that the investigate-health-write-check.sh hook then verifies before allowing the
# gated Write.
#
# Usage:
#   audit-council-completion.sh <session-id> <gate-name> [claim-id]
#
# gate-name conventions:
#   matrix          — gates Write to verification-matrix.md
#   offering        — gates Write to offering.md
#   finish-line     — issues the finish-line pass token (gates cleanup)

set -eu

if [ $# -lt 2 ]; then
    echo "usage: $0 <session-id> <gate-name> [claim-id]" >&2
    exit 1
fi

SESSION="$1"
GATE="$2"
CLAIM_ID="${3:-unspecified}"

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=lib/skill-token-lib.sh
. "$HOOK_DIR/lib/skill-token-lib.sh"
# shellcheck source=lib/investigate-state.sh
. "$HOOK_DIR/lib/investigate-state.sh"

LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

TOKEN_SKILL="investigate-audit-$GATE"

if ! TOKEN=$(issue_token "$TOKEN_SKILL"); then
    bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "issue-failed" 2>/dev/null || true
    exit 2
fi

STATE_DIR="$(investigate_state_dir "$SESSION")"
TOKEN_PATH="$STATE_DIR/audit-tokens/$GATE.token"

umask 077
printf '%s\n' "$TOKEN" > "$TOKEN_PATH"
chmod 600 "$TOKEN_PATH" 2>/dev/null || true

if [ "$GATE" = "finish-line" ]; then
    touch "$STATE_DIR/finish-line.token"
fi

# Run-root-anchored copy (compaction-proof): if a run-root is supplied (4th arg or $INVESTIGATE_RUN_ROOT),
# also write the token next to .investigate-active so it survives a session-id roll.
RUN_ROOT="${4:-${INVESTIGATE_RUN_ROOT:-}}"
if [ -n "$RUN_ROOT" ] && [ -d "$RUN_ROOT" ]; then
    RT_DIR="$RUN_ROOT/.investigate-tokens"
    mkdir -p "$RT_DIR" 2>/dev/null || true
    ( umask 077; printf '%s\n' "$TOKEN" > "$RT_DIR/$GATE.token" ) 2>/dev/null || true
    chmod 600 "$RT_DIR/$GATE.token" 2>/dev/null || true
    [ "$GATE" = "finish-line" ] && touch "$RT_DIR/finish-line.token" 2>/dev/null || true
fi

bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "issued" 2>/dev/null || true
exit 0
