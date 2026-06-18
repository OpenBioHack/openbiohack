#!/usr/bin/env bash
# Shared state helpers for the investigate-health hook family.
#
# Tracks, per session:
#   - session-read-log: paths the model has Read in this session (for [src:] validation)
#   - pending-patch flag: set when a corrections.md / "to be patched" mention names a
#     skill path; cleared when the next tool call is Edit on that path
#   - audit tokens: HMAC tokens issued by audit-council-completion.sh, verified before
#     gated Writes
#   - finish-line token: issued at Step 7 audit-council pass; gates cleanup operations
#
# State dir per session: /tmp/claude/.investigate-state-<session>/

INVESTIGATE_STATE_BASE="${INVESTIGATE_STATE_BASE:-/tmp/claude}"

investigate_state_dir() {
    local session="$1"
    [ -n "$session" ] || session="no-session"
    local d="$INVESTIGATE_STATE_BASE/.investigate-state-$session"
    mkdir -p "$d/audit-tokens" 2>/dev/null || true
    printf '%s' "$d"
}

investigate_record_read() {
    local session="$1"
    local path="$2"
    [ -n "$path" ] || return 0
    local d
    d="$(investigate_state_dir "$session")"
    printf '%s\n' "$path" >> "$d/read-log"
}

investigate_was_read() {
    local session="$1"
    local path="$2"
    local d
    d="$(investigate_state_dir "$session")"
    [ -f "$d/read-log" ] || return 1
    grep -Fxq "$path" "$d/read-log"
}

investigate_set_pending_patch() {
    local session="$1"
    local skill_path="$2"
    local d
    d="$(investigate_state_dir "$session")"
    printf '%s\n' "$skill_path" > "$d/pending-patch"
}

investigate_get_pending_patch() {
    local session="$1"
    local d
    d="$(investigate_state_dir "$session")"
    [ -f "$d/pending-patch" ] || return 1
    cat "$d/pending-patch"
}

investigate_clear_pending_patch() {
    local session="$1"
    local d
    d="$(investigate_state_dir "$session")"
    rm -f "$d/pending-patch" 2>/dev/null || true
}

investigate_has_finish_line_token() {
    local session="$1"
    local d
    d="$(investigate_state_dir "$session")"
    [ -f "$d/finish-line.token" ]
}

investigate_has_audit_token() {
    local session="$1"
    local gate="$2"
    local d
    d="$(investigate_state_dir "$session")"
    [ -f "$d/audit-tokens/$gate.token" ]
}
