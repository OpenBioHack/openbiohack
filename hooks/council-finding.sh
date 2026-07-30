#!/usr/bin/env bash
# council-finding.sh — L4 findings ledger + misclassification guard.
#
# A blocking council finding is OPENED with a fix_class (artifact_local | upstream_gap). The
# gate token cannot issue while any finding for that gate is open (enforced in
# audit-council-completion.sh). artifact_local findings are closed by the targeted-edit +
# diff-confirm + same-auditor-reconfirm loop; upstream_gap findings are closed by bouncing to
# the owning step and re-auditing.
#
# Misclassification guard: certain issue types CANNOT be artifact_local (they are grounding /
# missing-record gaps that an in-place wording edit cannot fix) and are forced to upstream_gap.
#
# Usage:
#   council-finding.sh open  <session> <gate> <finding-id> <artifact_local|upstream_gap> <issue> [span-sha]
#   council-finding.sh close <session> <gate> <finding-id> <diff-ok:ok|bad> <reconfirm:PASS|FAIL>
#   council-finding.sh status <session> <gate>     # prints "<open-count>"; exit 0 iff none open
set -eu

CMD="${1:-}"; shift || true
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"

# issue substrings that MUST route upstream (never artifact_local)
FORCED_UPSTREAM="ungrounded fabricated undated missing-b6 missing-record missing-section no-upstream no-record per-member demotion-no-ledger"

_ledgers() {  # echoes state-ledger [newline] run-ledger for a gate; mkdirs
    local session="$1" gate="$2" sd rt
    sd="$(investigate_state_dir "$session")"; mkdir -p "$sd/audit-tokens"
    printf '%s\n' "$sd/audit-tokens/findings-$gate.jsonl"
    rt="$(investigate_run_token_dir "$PWD" 2>/dev/null || true)"
    [ -n "$rt" ] && printf '%s\n' "$rt/findings-$gate.jsonl" || printf '%s\n' ""
}

_append() {  # _append <record-json> <session> <gate>
    local rec="$1" session="$2" gate="$3" L
    while IFS= read -r L; do
        [ -n "$L" ] || continue
        printf '%s\n' "$rec" >> "$L" 2>/dev/null || true
    done <<EOF
$(_ledgers "$session" "$gate")
EOF
}

_open_count() {  # _open_count <session> <gate> -> integer on stdout
    # H1 fix: union BOTH the state-dir ledger AND the run-root mirror ledger, de-duping ids
    # across them. Counting only the state-dir copy let a session-id roll (every compaction)
    # hide an open finding written to the run-root mirror, unlocking the gate token.
    local session="$1" gate="$2"
    _ledgers "$session" "$gate" | python3 -c '
import json, sys, os
opened, closed = set(), set()
for p in sys.stdin.read().split():
    if not p or not os.path.exists(p):
        continue
    for line in open(p):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("ev") == "open":
            opened.add(d.get("id"))
        elif d.get("ev") == "close":
            closed.add(d.get("id"))
print(len(opened - closed))
'
}

case "$CMD" in
    open)
        SESSION="$1"; GATE="$2"; FID="$3"; FIXCLASS="$4"; ISSUE="$5"; SHA="${6:-}"
        if [ "$FIXCLASS" = "artifact_local" ]; then
            for w in $FORCED_UPSTREAM; do
                case "$ISSUE" in
                    *"$w"*)
                        echo "council-finding: MISCLASSIFICATION - issue '$ISSUE' matches a forced-upstream class ('$w') and cannot be routed artifact_local. A grounding / missing-record / missing-section gap is fixed by bouncing to its owning step and re-auditing, never by an in-place wording edit. Re-open this finding as upstream_gap." >&2
                        exit 4 ;;
                esac
            done
        elif [ "$FIXCLASS" != "upstream_gap" ]; then
            echo "council-finding: fix_class must be artifact_local or upstream_gap (got '$FIXCLASS')." >&2
            exit 2
        fi
        _append "{\"id\":\"$FID\",\"ev\":\"open\",\"fix_class\":\"$FIXCLASS\",\"issue\":\"$ISSUE\",\"sha\":\"$SHA\"}" "$SESSION" "$GATE"
        echo "opened finding $FID ($FIXCLASS) on gate $GATE"
        ;;
    close)
        SESSION="$1"; GATE="$2"; FID="$3"; DIFFOK="$4"; RECON="$5"
        if [ "$DIFFOK" != "ok" ] || [ "$RECON" != "PASS" ]; then
            echo "council-finding: cannot close $FID - requires diff-ok=ok (got '$DIFFOK') AND reconfirm=PASS (got '$RECON'). The targeted edit must pass diff-confirm AND the same single auditor must reconfirm (satisfying SP1) before the finding closes." >&2
            exit 5
        fi
        _append "{\"id\":\"$FID\",\"ev\":\"close\"}" "$SESSION" "$GATE"
        echo "closed finding $FID on gate $GATE"
        ;;
    status)
        SESSION="$1"; GATE="$2"
        N="$(_open_count "$SESSION" "$GATE")"
        echo "$N"
        [ "$N" = "0" ]
        ;;
    *)
        echo "usage: $0 open|close|status ..." >&2; exit 2 ;;
esac
