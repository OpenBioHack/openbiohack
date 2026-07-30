#!/usr/bin/env bash
# investigate-health-faithful-strip.sh — PreToolUse on Write|Edit.
#
# L2/L3: offering.md (the client doc) must be a MECHANICAL strip of offering-draft.md (the
# audited, provenance-bearing draft). This hook validates that every client section equals the
# matching draft section after removing ONLY the allowed provenance tags (verbatim prose,
# modulo whitespace). Enforces the section-by-section client write (L3): each Edit-append of a
# section is validated against the draft as it fires.
#
# Activates only when offering.rules.json enables faithful_strip (the two-document model).
set -eu

INPUT=$(cat)
HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
. "$HOOK_DIR/lib/investigate-parse.sh"
. "$HOOK_DIR/lib/investigate-gate-lib.sh"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

ih_parse_input "$INPUT"
# Malformed input is handled (fail-closed) by write-check; this hook only acts on a parsed,
# in-scope offering.md write.
[ "$IH_PARSE_OK" = "1" ] || exit 0
CWD="$IH_CWD"; SESSION="$IH_SESSION"; FILE_PATH="$IH_FILE_PATH"; CONTENT="$IH_CONTENT"
BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")
[ "$BASENAME" = "offering.md" ] || exit 0
investigate_is_active "$CWD" "$FILE_PATH" || exit 0

RULES="$(gate_rules_path "$BASENAME" 2>/dev/null || true)"
# M5 fix: default ON (fail-closed, consistent with every other check's "no manifest -> still
# enforce" rule). The hook goes inert ONLY when a manifest is present AND explicitly disables
# faithful_strip. With no manifest, offering.md is still held to the strip — it must not be
# possible to write an unstripped client offer just because a config file is absent.
if [ -n "$RULES" ] && ! gate_enabled "$RULES" faithful_strip; then
    exit 0
fi

deny() {
    bash "$LOGGER" "investigate-health-faithful-strip" "$BASENAME" "session=$SESSION" "deny" 2>/dev/null || true
    python3 -c "
import json, sys
print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':sys.argv[1]}}))" "$1"
    exit 0
}

ROOT="$(dirname "$FILE_PATH")"
DRAFTNAME="$(gate_param "$RULES" faithful_strip draft 2>/dev/null || true)"
[ -n "$DRAFTNAME" ] || DRAFTNAME="offering-draft.md"
DRAFT="$ROOT/$DRAFTNAME"
if [ ! -s "$DRAFT" ]; then
    deny "offering.md blocked: $DRAFTNAME does not exist or is empty in the run root. The client offer is a MECHANICAL strip of the audited draft - write and audit offering-draft.md first, then produce offering.md by stripping it section by section (each section validated against the draft)."
fi

ALLOWED="$(gate_param "$RULES" faithful_strip allowed_provenance 2>/dev/null || true)"
REASON="$(printf '%s' "$CONTENT" | python3 "$HOOK_DIR/lib/investigate-faithful-strip.py" "$DRAFT" "$ALLOWED")" || deny "$REASON"

bash "$LOGGER" "investigate-health-faithful-strip" "$BASENAME" "session=$SESSION" "allow" 2>/dev/null || true
exit 0
