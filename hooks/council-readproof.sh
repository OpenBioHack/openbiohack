#!/usr/bin/env bash
# council-readproof.sh — SP1 enforcement writer.
# Runs investigate-quote-verify.py on an auditor's read-proof (stdin = auditor YAML) against the
# dispatched artifact. On PASS, writes <state>/audit-tokens/<gate>.readproof-ok (+ run-root
# mirror), which audit-council-completion.sh requires before it will issue the gate token. On
# FAIL, prints the verifier reasons and exits 1 (the verdict must be discarded).
#
# Usage: council-readproof.sh <session> <gate> <dispatched-artifact-path> [min_quotes] < auditor_yaml
set -eu

[ $# -ge 3 ] || { echo "usage: $0 <session> <gate> <artifact-path> [min_quotes]" >&2; exit 2; }
SESSION="$1"; GATE="$2"; ARTIFACT="$3"; MINQ="${4:-3}"

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"

YAML="$(cat)"
if ! printf '%s' "$YAML" | python3 "$HOOK_DIR/lib/investigate-quote-verify.py" "$ARTIFACT" "$MINQ"; then
    echo "council-readproof: SP1 verification FAILED for gate '$GATE' — token will NOT be issued. Re-dispatch that auditor and have it Read and quote the exact dispatched artifact ($ARTIFACT)." >&2
    exit 1
fi

STATE_DIR="$(investigate_state_dir "$SESSION")"
mkdir -p "$STATE_DIR/audit-tokens"
: > "$STATE_DIR/audit-tokens/$GATE.readproof-ok"
# run-root mirror (compaction-proof), derived from the artifact path
RT="$(investigate_run_token_dir "$ARTIFACT" 2>/dev/null || true)"
[ -n "$RT" ] && : > "$RT/$GATE.readproof-ok" 2>/dev/null || true
echo "council-readproof: SP1 OK for gate '$GATE' (readproof-ok written)."
exit 0
