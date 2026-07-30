#!/usr/bin/env bash
# investigate-health-extraction-check.sh — Foundation gate. PreToolUse on Write|Edit.
#
# Gates Phase-A / Phase-B extraction outputs (any */extracted/*.md, incl. extracted/compiled/*.md)
# so a bare declarative CAUSAL / DIAGNOSTIC / MECHANISTIC claim cannot enter the neutral data
# layer untagged. This makes the interpretation TAGS trustworthy — without it an extraction can
# smuggle an untagged declarative diagnosis and the downstream Layer-1 mask / Layer-2 grounding
# gate (which key on those tags) go blind.
#
# Condition-agnostic: keys ONLY on register shape + the pipeline's own tags (via
# lib/investigate-extraction-register.py), never on any disease name or filename.
#
# Behind a manifest flag (references/gates/extraction.rules.json): check `extraction_register`
# carries {enabled, mode}. mode=deny hard-blocks; mode=warn emits an advisory and allows.
# Fail-closed: a missing/corrupt manifest => enabled + deny.

set -eu
INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
. "$HOOK_DIR/lib/investigate-parse.sh"
. "$HOOK_DIR/lib/investigate-gate-lib.sh"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"
export IH_LIB="$HOOK_DIR/lib"

ih_parse_input "$INPUT"

# Malformed input fail-closed: if unparseable but the raw plausibly targets an extracted/*.md
# claim doc, refuse (the gate cannot verify register on input it cannot read).
if [ "$IH_PARSE_OK" != "1" ]; then
    if printf '%s' "$INPUT" | grep -Eq '/extracted/[^"]*\.md'; then
        python3 -c "
import json,sys
print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':sys.argv[1]}}))" \
"Malformed hook input targeting an extracted/*.md extraction artifact. Refusing (fail-closed): the Foundation gate could not parse the tool input to verify extraction register. Re-issue with well-formed tool input."
    fi
    exit 0
fi

CWD="$IH_CWD"; SESSION="$IH_SESSION"; FILE_PATH="$IH_FILE_PATH"; CONTENT="$IH_CONTENT"
BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")

# --- path scoping: only extraction claim docs under an extracted/ dir ---
case "$FILE_PATH" in
    */extracted/*.md) ;;
    *) exit 0 ;;
esac
# manifests / scratch / independent-audit files are not claim extracts
case "$FILE_PATH" in
    */_staged/*) exit 0 ;;
esac
case "$BASENAME" in
    index.md|data-completeness.md|spot-check.md) exit 0 ;;
esac

# root-anchored scope guard (no hardcoded path); inactive outside a run -> no-op.
investigate_is_active "$CWD" "$FILE_PATH" || exit 0

deny() {
    local reason="$1"
    bash "$LOGGER" "investigate-health-extraction-check" "$BASENAME" "session=$SESSION" "deny" 2>/dev/null || true
    python3 -c "
import json,sys
print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':sys.argv[1]}}))" "$reason"
    exit 0
}

# STUB-ALLOWLIST: tiny bootstrap stubs pass unchecked. Sentinels are SPECIFIC phrases (not a bare
# 'pending' substring, which would match 'depending'/'impending' and skip the whole gate — M1).
CONTENT_LEN=$(printf '%s' "$CONTENT" | wc -c | tr -d ' ')
if [ "$CONTENT_LEN" -lt 400 ] && printf '%s' "$CONTENT" | grep -qiE '(empty stub|_pending_|pending step|^[[:space:]]*> empty|no data for this view)'; then
    exit 0
fi

# --- manifest: enabled? mode? (fail-closed: missing/corrupt => enabled + deny) ---
RULES="$IH_GATE_SKILL_DIR/references/gates/extraction.rules.json"
[ -f "$RULES" ] || RULES=""
if [ -n "$RULES" ]; then
    gate_enabled "$RULES" extraction_register || exit 0     # explicitly disabled -> no-op
    MODE="$(gate_param "$RULES" extraction_register mode)"
else
    MODE="deny"
fi
[ -n "$MODE" ] || MODE="deny"

REGHELP="$HOOK_DIR/lib/investigate-extraction-register.py"
if [ ! -f "$REGHELP" ]; then
    deny "extraction blocked (fail-closed): the extraction-register helper is missing at $REGHELP, so extraction-register discipline cannot be enforced. Restore lib/investigate-extraction-register.py."
fi

VIOL=$(printf '%s' "$CONTENT" | python3 "$REGHELP" 2>/dev/null) || {
    MSG="Foundation gate ($BASENAME): a bare declarative causal / diagnostic / mechanistic claim appears in an extraction output. Extraction reorganises data; it must NOT conclude, confirm, or name a root cause in its own voice (per extract-health-data: 'never interprets, concludes, or flags'). Tag it as interpretation ([interpretation] / [prior-analysis note] / **[INFERRED]**), attribute it to the record/clinician who made the claim (e.g. 'her GP diagnosed X', 'the letter notes ...'), or carry it inside the verbatim [src: ...] quote it came from. First offending sentence: $VIOL"
    if [ "$MODE" = "warn" ]; then
        printf 'WARN investigate-health-extraction-check: %s\n' "$MSG" >&2
        bash "$LOGGER" "investigate-health-extraction-check" "$BASENAME" "session=$SESSION" "warn" 2>/dev/null || true
        exit 0
    fi
    deny "$MSG"
}

# --- Layer 3(a): verbatim [src:]-quote fidelity (hard). A fabricated [src: F,..,"quote"] whose
# quote does not resolve in a resolvable TEXT F is denied (stops a fake citation laundering an
# injected claim past the register gate's [src:] escape). Manifest key src_fidelity. ---
EXDIR="$(dirname "$FILE_PATH")"
if { [ -z "$RULES" ] || gate_enabled "$RULES" src_fidelity; }; then
    FIDHELP="$HOOK_DIR/lib/investigate-src-fidelity.py"
    if [ -f "$FIDHELP" ]; then
        FVIOL=$(printf '%s' "$CONTENT" | python3 "$FIDHELP" "$EXDIR" 2>/dev/null) || {
            deny "Foundation gate ($BASENAME): $FVIOL . A [src: F, <loc>, \"quote\"] citation asserts the quote appears verbatim in F, but it does not. Extraction must carry the ACTUAL verbatim source text (extract-health-data: 'the verbatim source quote it came from'). Fix the quote to match F exactly, or correct the source reference."
        }
    fi
fi

# --- Layer 3(b): provenance-class reconciliation (ADVISORY, never blocks). For a DERIVED/CURATED
# extract, flag concrete factual tokens corroborated by no primary-class sibling source — the
# distorted-curated-fact catch (e.g. an invented food). Surfaced as a WARN for the operator to
# confirm with the subject, exactly like index.md's own "Items Requiring Human Review". ---
if { [ -z "$RULES" ] || gate_enabled "$RULES" provenance_reconcile; }; then
    RECHELP="$HOOK_DIR/lib/investigate-provenance-reconcile.py"
    RINDEX="$EXDIR/index.md"
    if [ -f "$RECHELP" ] && [ -f "$RINDEX" ]; then
        RFLAGS=$(printf '%s' "$CONTENT" | python3 "$RECHELP" --auto "$RINDEX" "$BASENAME" "$EXDIR" 2>/dev/null) || {
            printf 'WARN investigate-health-extraction-check (provenance-reconcile): %s carries factual token(s) corroborated by NO primary source: %s — confirm with the subject (possible curated distortion).\n' "$BASENAME" "$(printf '%s' "$RFLAGS" | tr '\n' ' ')" >&2
            bash "$LOGGER" "investigate-health-extraction-check" "$BASENAME" "session=$SESSION" "reconcile-flag" 2>/dev/null || true
        }
    fi
fi

bash "$LOGGER" "investigate-health-extraction-check" "$BASENAME" "session=$SESSION" "allow" 2>/dev/null || true
exit 0
