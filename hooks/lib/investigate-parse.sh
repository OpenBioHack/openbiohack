#!/usr/bin/env bash
# investigate-parse.sh — newline-safe single-pass parse of a hook's JSON stdin.
#
# F6 fix: the hooks previously extracted fields with positional `sed -n '1p'/'2p'/'3p'`
# over a multi-line `python3 print(...)`. A literal newline inside file_path / cwd /
# session_id / command would shift those line indices and could move attacker text into
# the CONTENT slot or skip a check. This helper parses every field in ONE python pass
# keyed by name. Structural fields are returned as shlex-quoted assignments (eval-safe,
# never contain content); the document body is captured separately and raw.
#
# Usage:
#   . "$HOOK_DIR/lib/investigate-parse.sh"
#   ih_parse_input "$INPUT"
#   # then: $IH_PARSE_OK (1/0), $IH_CWD $IH_SESSION $IH_TOOL $IH_FILE_PATH $IH_CMD $IH_CONTENT

ih_parse_input() {
    local _input="$1" _evals
    IH_PARSE_OK=0; IH_CWD=""; IH_SESSION=""; IH_TOOL=""; IH_FILE_PATH=""; IH_CMD=""; IH_CONTENT=""

    _evals="$(printf '%s' "$_input" | python3 -c '
import sys, json, shlex
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    print("IH_PARSE_OK=0"); sys.exit(0)
if not isinstance(d, dict): d = {}
ti = d.get("tool_input") or {}
if not isinstance(ti, dict): ti = {}
def g(o, k):
    v = o.get(k, "")
    if v is None: return ""
    return v if isinstance(v, str) else str(v)
print("IH_PARSE_OK=1")
print("IH_CWD="       + shlex.quote(g(d,  "cwd")))
print("IH_SESSION="   + shlex.quote(g(d,  "session_id")))
print("IH_TOOL="      + shlex.quote(g(d,  "tool_name")))
print("IH_FILE_PATH=" + shlex.quote(g(ti, "file_path")))
print("IH_CMD="       + shlex.quote(g(ti, "command")))
' 2>/dev/null)"

    # Structural fields only (shlex-quoted, no document body) -> safe to eval.
    eval "$_evals" 2>/dev/null || IH_PARSE_OK=0

    # Document body captured separately and raw; never eval'd, so newlines/backticks/
    # quotes/unicode round-trip byte-exactly.
    if [ "$IH_PARSE_OK" = "1" ]; then
        IH_CONTENT="$(printf '%s' "$_input" | python3 -c '
import sys, json
try:
    d = json.loads(sys.stdin.read()); ti = d.get("tool_input") or {}
    sys.stdout.write((ti.get("content") or ti.get("new_string") or ""))
except Exception:
    pass
' 2>/dev/null)"
    fi
}

# Raw fallback: when IH_PARSE_OK=0 (malformed JSON) a gated-file hook still needs to
# decide fail-closed. This greps the RAW stdin for any gated artifact basename so the
# hook can DENY a malformed write that plausibly targets a gated file, while leaving
# unrelated malformed writes alone. Returns 0 if a gated basename is present in raw.
ih_raw_targets_gated() {
    local _input="$1"
    printf '%s' "$_input" | grep -Eq \
'offering-draft\.md|offering\.md|working-hypothesis\.md|step5-cross-check\.md|hypothesis-set\.md|step6-prioritize\.md|constraints-[A-Za-z0-9_-]+\.md|shape-profile-[A-Za-z0-9_-]+\.md|mechanism-map-[A-Za-z0-9_-]+\.md|convergence-[A-Za-z0-9_-]+\.md'
}
