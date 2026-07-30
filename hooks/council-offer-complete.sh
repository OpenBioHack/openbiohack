#!/usr/bin/env bash
# council-offer-complete.sh — H2 completeness gate for the client offer.
# Verifies offering.md includes EVERY client-required section of offering-draft.md (every draft
# section whose heading is NOT marked [[draft-internal]]). On pass, writes an offer-complete-ok
# marker (required by the finish-line). On fail, prints each missing section AND the exact
# provenance-stripped text to append via a targeted Edit, then exits 1.
#
# Usage: council-offer-complete.sh <session> <offering-draft.md path> <offering.md path>
set -eu

[ $# -ge 3 ] || { echo "usage: $0 <session> <offering-draft.md> <offering.md>" >&2; exit 2; }
SESSION="$1"; DRAFT="$2"; CLIENT="$3"
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"

[ -s "$DRAFT" ]  || { echo "council-offer-complete: offering-draft.md missing/empty: $DRAFT" >&2; exit 1; }
[ -f "$CLIENT" ] || { echo "council-offer-complete: offering.md missing: $CLIENT" >&2; exit 1; }

if ! cat "$CLIENT" | python3 "$HOOK_DIR/lib/investigate-faithful-strip.py" --completeness "$DRAFT"; then
    echo "" >&2
    echo "council-offer-complete: offering.md is INCOMPLETE. Append each missing section above with a targeted Edit, then re-run this check. The finish-line will not issue until offering.md is complete." >&2
    exit 1
fi

SD="$(investigate_state_dir "$SESSION")"; mkdir -p "$SD/audit-tokens"
: > "$SD/audit-tokens/offer-complete-ok"
RT="$(investigate_run_token_dir "$CLIENT" 2>/dev/null || true)"
[ -n "$RT" ] && : > "$RT/offer-complete-ok" 2>/dev/null || true
echo "council-offer-complete: OK — all client-required sections present (offer-complete-ok written)."
exit 0
