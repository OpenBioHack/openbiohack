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

# --- root-anchored activation (compaction-proof + portable) ---------------------------
# Walk up from a starting dir to the nearest ancestor that contains a `.investigate-active`
# marker file (the way git finds `.git`). Echoes the run-root path and returns 0 if found;
# returns 1 otherwise. No hardcoded project path — works for any user / the public repo.
#
# The marker is written by the skill bootstrap (step 1b) into <root>/.investigate-active and
# removed only at the finish-line (cleanup-block protects it until then), so activation holds
# for the WHOLE run regardless of session-id changes across compaction.
#
# Optional belt-and-suspenders for a private install: if INVESTIGATE_LEGACY_ROOT is set and the
# start dir is at/under it, the install is considered active even without a marker. Public
# OpenBioHack hooks ship with this UNSET, so they stay strictly path-agnostic.
investigate_find_active_root() {
    local d="$1"
    [ -n "$d" ] || return 1
    # if given a file path, start from its directory
    [ -d "$d" ] || d="$(dirname "$d" 2>/dev/null)"
    local probe="$d"
    while [ -n "$probe" ] && [ "$probe" != "/" ] && [ "$probe" != "." ]; do
        if [ -f "$probe/.investigate-active" ]; then
            printf '%s' "$probe"
            return 0
        fi
        probe="$(dirname "$probe" 2>/dev/null)"
    done
    [ -f "/.investigate-active" ] && { printf '%s' "/"; return 0; }
    # legacy fallback (private install only)
    if [ -n "${INVESTIGATE_LEGACY_ROOT:-}" ]; then
        case "$d/" in
            "$INVESTIGATE_LEGACY_ROOT"/*|"$INVESTIGATE_LEGACY_ROOT/") printf '%s' "$INVESTIGATE_LEGACY_ROOT"; return 0 ;;
        esac
    fi
    return 1
}

# True iff EITHER the cwd OR the file path resolves to an active run root. Hooks pass both so a
# write into a run root still fires even if cwd has drifted to a sibling dir.
investigate_is_active() {
    local cwd="$1" file="$2"
    investigate_find_active_root "$cwd" >/dev/null 2>&1 && return 0
    [ -n "$file" ] && investigate_find_active_root "$file" >/dev/null 2>&1 && return 0
    return 1
}
# --- end root-anchored activation -----------------------------------------------------

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

# --- run-root-anchored audit tokens (compaction-proof; mirrors .investigate-active activation) ---
# session_id can roll across compaction, orphaning session-keyed tokens. These also store/check tokens
# under <run-root>/.investigate-tokens so a gated write survives a session-id change.
investigate_run_token_dir() {
    local start="$1" root
    root="$(investigate_find_active_root "$start" 2>/dev/null)" || return 1
    [ -n "$root" ] || return 1
    local d="$root/.investigate-tokens"
    mkdir -p "$d" 2>/dev/null || true
    command -v investigate_register_root >/dev/null 2>&1 && investigate_register_root "$root"
    printf '%s' "$d"
}
investigate_has_audit_token_anchored() {
    local session="$1" gate="$2" start="$3" td
    investigate_has_audit_token "$session" "$gate" && return 0
    td="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 1
    [ -n "$td" ] && [ -f "$td/$gate.token" ]
}
investigate_has_finish_line_token_anchored() {
    local session="$1" start="$2" td
    investigate_has_finish_line_token "$session" && return 0
    td="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 1
    [ -n "$td" ] && [ -f "$td/finish-line.token" ]
}
# --- end run-root-anchored audit tokens ---

# --- run-root-anchored read-log + pending-patch (compaction-proof) ----------------------------------
investigate_record_read_anchored() {
    local session="$1" path="$2" start="$3" d
    investigate_record_read "$session" "$path"
    [ -n "$path" ] || return 0
    d="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 0
    [ -n "$d" ] && printf '%s\n' "$path" >> "$d/read-log" 2>/dev/null || true
}
investigate_was_read_anchored() {
    local session="$1" path="$2" start="$3" d
    investigate_was_read "$session" "$path" && return 0
    d="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 1
    [ -n "$d" ] && [ -f "$d/read-log" ] && grep -Fxq "$path" "$d/read-log"
}
investigate_set_pending_patch_anchored() {
    local session="$1" sp="$2" start="$3" d
    investigate_set_pending_patch "$session" "$sp"
    d="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 0
    [ -n "$d" ] && printf '%s\n' "$sp" > "$d/pending-patch" 2>/dev/null || true
}
investigate_get_pending_patch_anchored() {
    local session="$1" start="$2" d v
    v="$(investigate_get_pending_patch "$session" 2>/dev/null || true)"
    [ -n "$v" ] && { printf '%s' "$v"; return 0; }
    d="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 1
    [ -n "$d" ] && [ -s "$d/pending-patch" ] && cat "$d/pending-patch"
}
investigate_clear_pending_patch_anchored() {
    local session="$1" start="$2" d
    investigate_clear_pending_patch "$session"
    d="$(investigate_run_token_dir "$start" 2>/dev/null)" || return 0
    [ -n "$d" ] && : > "$d/pending-patch" 2>/dev/null || true
}
# --- end run-root-anchored read-log + pending-patch ---

# --- session-independent active-run registry (so the cwd-only injector survives a session-id roll) ---
# A run-root has a path INSIDE it (the gated writes), so the gating hooks can register it; the
# UserPromptSubmit injector only has cwd (often the PARENT of the run root), so walk-up can't find a
# child-dir marker. This registry + a bounded down-search make the injector session-independent.
INVESTIGATE_REGISTRY="${INVESTIGATE_REGISTRY:-${INVESTIGATE_STATE_BASE:-/tmp/claude}/active-roots}"
investigate_register_root() {
    local root="$1" key
    [ -n "$root" ] && [ -d "$root" ] || return 0
    mkdir -p "$INVESTIGATE_REGISTRY" 2>/dev/null || return 0
    key="$(printf '%s' "$root" | sed 's#[/ ]#_#g')"
    printf '%s\n' "$root" > "$INVESTIGATE_REGISTRY/$key" 2>/dev/null || true
}
investigate_cwd_has_active_run() {
    local cwd="$1" f root m d
    [ -n "$cwd" ] || return 1
    # (a) marker at/above cwd
    investigate_find_active_root "$cwd" >/dev/null 2>&1 && return 0
    # (b) registry: a still-active root related to cwd (root under cwd, cwd under root, or equal)
    if [ -d "$INVESTIGATE_REGISTRY" ]; then
        for f in "$INVESTIGATE_REGISTRY"/*; do
            [ -f "$f" ] || continue
            root="$(cat "$f" 2>/dev/null)"; [ -n "$root" ] || continue
            [ -f "$root/.investigate-active" ] || continue
            case "$cwd/" in "$root"/*) return 0;; esac
            case "$root/" in "$cwd"/*) return 0;; esac
            [ "$cwd" = "$root" ] && return 0
        done
    fi
    # (c) bounded down-search fallback (self-registers what it finds)
    m="$(find "$cwd" -maxdepth 3 -name .investigate-active -type f 2>/dev/null | head -n1)"
    if [ -n "$m" ]; then d="$(dirname "$m")"; investigate_register_root "$d"; return 0; fi
    return 1
}
# --- end active-run registry ---
