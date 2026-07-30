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

# SP1: the council gates require a readproof-ok marker (the auditor proved, via verbatim
# line-numbered quotes verified against the dispatched artifact, that it actually read the
# file). The marker is written by council-readproof.sh. Without it, refuse the token — a
# verdict from an auditor that did not demonstrably read the artifact cannot open the gate.
case "$GATE" in
    offering|decomposition|structure|register|substance)
        _rp=0
        _sd="$(investigate_state_dir "$SESSION")"
        [ -f "$_sd/audit-tokens/$GATE.readproof-ok" ] && _rp=1
        if [ "$_rp" = 0 ]; then
            _rt="$(investigate_find_active_root "$PWD" 2>/dev/null || true)"
            [ -n "$_rt" ] && [ -f "$_rt/.investigate-tokens/$GATE.readproof-ok" ] && _rp=1
        fi
        if [ "$_rp" = 0 ]; then
            bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "no-readproof" 2>/dev/null || true
            echo "audit-council-completion: refusing to issue '$GATE' token — no SP1 readproof-ok marker for this gate. Run council-readproof.sh <session> $GATE <dispatched-artifact> with the auditor's read-proof first (the auditor must quote >=3 verbatim line-numbered spans from the artifact it was dispatched on, not from the worked examples)." >&2
            exit 3
        fi
        ;;
esac

# L4: refuse the token while any council finding for this gate is still open. Findings are
# opened by council-finding.sh and closed only via the targeted-edit + diff-confirm + reconfirm
# loop (artifact_local) or an upstream bounce + re-audit (upstream_gap).
if [ -x "$HOOK_DIR/council-finding.sh" ]; then
    OPEN_N="$("$HOOK_DIR/council-finding.sh" status "$SESSION" "$GATE" 2>/dev/null || echo 0)"
    if [ "${OPEN_N:-0}" != "0" ]; then
        bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "open-findings=$OPEN_N" 2>/dev/null || true
        echo "audit-council-completion: refusing to issue '$GATE' token - $OPEN_N open council finding(s) for this gate. Close each via the targeted-edit + diff-confirm + same-auditor reconfirm loop (artifact_local) or bounce to the owning step + re-audit (upstream_gap)." >&2
        exit 6
    fi
fi

# H2: the finish-line cannot issue until offering.md completeness is verified (every client-
# required section of offering-draft.md is present). The marker is written by
# council-offer-complete.sh.
if [ "$GATE" = "finish-line" ]; then
    _oc=0
    _sd="$(investigate_state_dir "$SESSION")"
    [ -f "$_sd/audit-tokens/offer-complete-ok" ] && _oc=1
    if [ "$_oc" = 0 ]; then
        _rt="$(investigate_find_active_root "$PWD" 2>/dev/null || true)"
        [ -n "$_rt" ] && [ -f "$_rt/.investigate-tokens/offer-complete-ok" ] && _oc=1
    fi
    if [ "$_oc" = 0 ]; then
        bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "offer-incomplete" 2>/dev/null || true
        echo "audit-council-completion: refusing finish-line — offering.md completeness has not been verified. Run council-offer-complete.sh <session> <offering-draft.md> <offering.md>, add any missing required sections it reports, then retry." >&2
        exit 7
    fi
fi

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

# Run-root-anchored copy (compaction-proof): write the token next to .investigate-active
# so it survives a session-id roll across compaction.
# F3: the mirror used to be CONDITIONAL on a 4th arg / $INVESTIGATE_RUN_ROOT being passed
# — when the orchestrator forgot it, the token was session-only and a later session-id roll
# orphaned the offering gate. Now the run-root is ALWAYS derived: explicit arg/env first,
# else walk up from $PWD (the orchestrator invokes this from inside the run root) to the
# nearest .investigate-active marker. The mirror is therefore unconditional.
RUN_ROOT="${4:-${INVESTIGATE_RUN_ROOT:-}}"
if [ -z "$RUN_ROOT" ]; then
    RUN_ROOT="$(investigate_find_active_root "$PWD" 2>/dev/null || true)"
fi
if [ -n "$RUN_ROOT" ] && [ -d "$RUN_ROOT" ]; then
    RT_DIR="$RUN_ROOT/.investigate-tokens"
    mkdir -p "$RT_DIR" 2>/dev/null || true
    ( umask 077; printf '%s\n' "$TOKEN" > "$RT_DIR/$GATE.token" ) 2>/dev/null || true
    chmod 600 "$RT_DIR/$GATE.token" 2>/dev/null || true
    [ "$GATE" = "finish-line" ] && touch "$RT_DIR/finish-line.token" 2>/dev/null || true
fi

bash "$LOGGER" "audit-council-completion" "$GATE" "session=$SESSION claim=$CLAIM_ID" "issued" 2>/dev/null || true
exit 0
