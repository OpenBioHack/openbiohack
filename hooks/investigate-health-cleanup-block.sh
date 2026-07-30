#!/usr/bin/env bash
# investigate-health-cleanup-block.sh — PreToolUse on Bash.
#
# NO CLEANUP MID-RUN. While an investigate-health run is active, every
# destructive command that targets the run (its root, its artifacts, its
# activation marker, its token dir) is silently DENIED — never prompted.
# Cleanup unlocks only when the run legitimately ends: a delivered
# <root>/offering.md exists (>= 800 bytes; writing it required passing the
# HMAC-gated audit council, so the signal is not forgeable — and the tiny-stub
# allowlist is closed for offering.md in write-check). There is NO finish-line
# token in this path any more: the old existence-only token check was forgeable
# with a bare `touch` (review 2026-07-06), which let `rm -rf <root>` through
# mid-run.
#
# The trigger set is deliberately BROAD (verbs + interpreters + copy/overwrite
# forms): the verdict is a silent deny, so over-matching costs nothing, while a
# missed form would be irreversible. Honest residual: a genuinely novel
# deletion method (e.g. `python3 somescript.py`) can evade this tripwire; the
# compensating hard guarantee is the kernel-locked (`chflags uchg`) activation
# marker — the harness cannot be silently un-armed and a run cannot be falsely
# completed (see investigate-health-lock-anchors.sh).
#
# Earlier fixes retained: F1 fail-open crash fix, F4 portable marker scoping +
# INVESTIGATE_SCOPE_OVERRIDE hermetic lane, F6 newline-safe single-pass parse.

set -eu

INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
. "$HOOK_DIR/lib/investigate-parse.sh"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

ih_parse_input "$INPUT"
# Malformed Bash input: we cannot identify a command to gate -> allow (this hook only
# ever BLOCKS specific destructive commands; a command we cannot read cannot be run
# meaningfully either). Fail-closed handling for gated WRITES lives in write-check.
[ "$IH_PARSE_OK" = "1" ] || exit 0

SESSION="$IH_SESSION"
CMD="$IH_CMD"
CWD="$IH_CWD"

# Normalize path strings before any prefix comparison: collapse duplicate
# slashes, strip a trailing slash. Candidates are python-normpath'd; the cwd
# (and thus the walk-up root) and registry roots must match that form, or a
# cwd like "/tmp//x" (e.g. from a trailing-slash $TMPDIR) breaks the
# glob-prefix overlap and a targeting deny is silently missed.
norm_path() { printf '%s' "$1" | sed 's#//*#/#g; s#\(.\)/$#\1#'; }
CWD="$(norm_path "$CWD")"

# --- destructive trigger? (cheap grep gate; most Bash calls exit here) --------
# Verbs that delete/move/overwrite, interpreter one-liners that can (python -c,
# node -e, ...), bulk tools with delete/overwrite modes, and '>'-redirection
# onto a tracked artifact. cp/tee/install/ln are included because overwriting
# offering.md is how the run-ended signal would be forged.
ART_RE='extracted|working-hypothesis|step5-cross-check|hypothesis-set|shared-node-inventory|step6-prioritize|offering|decision-log|question-bank|\.investigate'
DESTRUCTIVE=0
printf '%s' "$CMD" | grep -Eq \
    '(^|[^[:alnum:]_./-])(rm|rmdir|mv|cp|tee|install|ln|unlink|shred|truncate|dd)([[:space:]]|$)' \
    && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_-])git([[:space:]][^;|&]*)?[[:space:]]clean([[:space:]]|$)' && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]])find([[:space:]]|$).*-delete([[:space:]]|$)' && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_-])sed[[:space:]][^;|&]*-i' && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_-])rsync[[:space:]][^;|&]*--delete' && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_-])tar[[:space:]][^;|&]*--overwrite' && DESTRUCTIVE=1
printf '%s' "$CMD" | grep -Eq \
    '(^|[^[:alnum:]_-])(python[0-9.]*|node|perl|ruby|sh|bash|zsh)[[:space:]][^;|&]*-(c|e)([[:space:]]|$|['"'"'"])' \
    && DESTRUCTIVE=1
# truncating/appending redirection onto a tracked artifact: '> ... <artifact>'
printf '%s' "$CMD" | grep -Eq ">[[:space:]]*[^|&;]*($ART_RE)" && DESTRUCTIVE=1
[ "$DESTRUCTIVE" = "1" ] || exit 0

# --- candidate path operands ---------------------------------------------------
# Newline-separated normalized absolute candidates: shell-token operands
# (quotes handled by shlex, ~/$HOME expanded, glob tails stripped to their
# literal prefix, relatives resolved against cwd) plus quoted string literals
# inside interpreter payloads. Best-effort tripwire (see header), not a proof;
# paths containing a literal newline are not supported here.
CANDS="$(printf '%s' "$CMD" | IH_CWD_FOR_CANDS="$CWD" python3 -c '
import os, re, shlex, sys

cmd = sys.stdin.read()
cwd = os.environ.get("IH_CWD_FOR_CANDS", "")
home = os.path.expanduser("~")
out = set()

def add(tok: str) -> None:
    t = tok
    if not t or t.startswith("-"):
        return
    if t == "~" or t.startswith("~/"):
        t = home + t[1:]
    t = t.replace("${HOME}", home).replace("$HOME", home)
    for gc in "*?[":
        i = t.find(gc)
        if i != -1:
            t = t[:i]
    if not t:
        return
    if not t.startswith("/"):
        if not cwd:
            return
        t = os.path.join(cwd, t)
    out.add(os.path.normpath(t))

try:
    toks = shlex.split(cmd, posix=True)
except ValueError:
    toks = cmd.split()

OPS = {";", "&&", "||", "|", "&"}
expect_cmd = True   # next non-assignment token is a command word, not an operand
for tok in toks:
    if tok in OPS:
        expect_cmd = True
        continue
    if expect_cmd:
        if re.match(r"^[A-Za-z_][A-Za-z_0-9]*=", tok):
            continue          # env assignment prefix; command word still pending
        if tok in ("sudo", "env", "nohup", "xargs", "time", "nice", "command"):
            continue          # wrapper; real command word still pending
        expect_cmd = False
        continue              # the command word itself is never an operand
    if tok.startswith("-"):
        continue
    # interpreter payloads / code-ish tokens: ALSO mine their quoted string
    # literals (a shlex token can be both a spacey path and a payload — adding
    # the raw token too means a legitimate path with spaces is never dropped,
    # and a cwd-joined garbage candidate is harmless over-match)
    if any(ch in tok for ch in (" ", ";", "(", ")")):
        for m in re.findall(r"\x27([^\x27]+)\x27|\"([^\"]+)\"", tok):
            for s in m:
                if s:
                    add(s)
    add(tok)

sys.stdout.write("\n".join(sorted(p for p in out if "\n" not in p)))
' 2>/dev/null || true)"

# --- resolve the run roots this command implicates ------------------------------
# A root is implicated when a candidate lives at/under it (marker walk-up from
# the candidate), when a candidate is a string-ancestor/glob-prefix of it
# (deleting an ancestor deletes the root), or when the command names a tracked
# artifact while cwd is inside a run. Registry roots cover sibling-cwd and
# glob forms whose walk-up cannot see the marker.
CWD_ROOT="$(investigate_find_active_root "$CWD" 2>/dev/null || true)"
if [ -n "${INVESTIGATE_SCOPE_OVERRIDE:-}" ] && [ -z "$CWD_ROOT" ]; then
    CWD_ROOT="${INVESTIGATE_OVERRIDE_ROOT:-$CWD}"   # hermetic test lane (F4)
fi
REGISTRY_DIR="${INVESTIGATE_REGISTRY:-${INVESTIGATE_STATE_BASE:-/tmp/claude}/active-roots}"

TARGETED=""    # newline-separated unique roots
NL='
'
add_root() {
    [ -n "$1" ] || return 0
    case "$NL$TARGETED$NL" in *"$NL$1$NL"*) return 0 ;; esac
    TARGETED="$TARGETED$NL$1"
}

overlap() {    # overlap <candidate> <root> -> 0 if the op implicates the root
    local c="$1" r="$2"
    [ -n "$c" ] && [ -n "$r" ] || return 1
    [ "$c" = "$r" ] && return 0
    case "$c/" in "$r"/*) return 0 ;; esac    # candidate under root
    case "$r/" in "$c"*) return 0 ;; esac     # candidate = ancestor or glob prefix of root
    return 1
}

while IFS= read -r c; do
    [ -n "$c" ] || continue
    CROOT="$(investigate_find_active_root "$c" 2>/dev/null || true)"
    [ -n "$CROOT" ] && add_root "$CROOT"
    [ -n "$CWD_ROOT" ] && overlap "$c" "$CWD_ROOT" && add_root "$CWD_ROOT"
    if [ -d "$REGISTRY_DIR" ]; then
        for rf in "$REGISTRY_DIR"/*; do
            [ -f "$rf" ] || continue
            rr="$(norm_path "$(cat "$rf" 2>/dev/null)")"; [ -n "$rr" ] || continue
            [ -f "$rr/.investigate-active" ] || continue
            overlap "$c" "$rr" && add_root "$rr"
        done
    fi
done <<EOF_CANDS
$CANDS
EOF_CANDS

# artifact-name mention while inside an active run also implicates that run
if [ -n "$CWD_ROOT" ] && printf '%s' "$CMD" | grep -Eq "$ART_RE"; then
    add_root "$CWD_ROOT"
fi

# No implicated run -> not ours to gate.
[ -n "$(printf '%s' "$TARGETED" | tr -d '[:space:]')" ] || exit 0

# --- verdict: mid-run -> silent deny; run ended (delivered offering) -> allow ---
offering_delivered() {   # <root> -> 0 iff a substantial, regular offering.md exists
    local f="$1/offering.md"
    [ -f "$f" ] && [ ! -L "$f" ] || return 1
    [ "$(wc -c < "$f" | tr -d ' ')" -ge 800 ]
}

MIDRUN_ROOT=""
while IFS= read -r r; do
    [ -n "$r" ] || continue
    offering_delivered "$r" || { MIDRUN_ROOT="$r"; break; }
done <<EOF_ROOTS
$TARGETED
EOF_ROOTS

if [ -z "$MIDRUN_ROOT" ]; then
    bash "$LOGGER" "investigate-health-cleanup-block" "bash" "session=$SESSION" "allow-post-offering" 2>/dev/null || true
    exit 0
fi

REASON="No cleanup mid-run. This destructive command targets the active investigate-health run at $MIDRUN_ROOT and is denied while the run is in progress. Rule: investigate-health SKILL.md 'No cleanup mid-run'. Nothing under the run root may be deleted, moved, or overwritten before the run ends — a mid-run deletion can silently remove something the audit will look for, converting a recoverable mistake into an undetectable one. Cleanup unlocks automatically once the run legitimately ends: the delivered offering ($MIDRUN_ROOT/offering.md, written through the audit-council gates) is the end-of-run signal — no token, no prompt. Until then: continue the run; do not clean up. Command attempted: $CMD"

bash "$LOGGER" "investigate-health-cleanup-block" "bash" "session=$SESSION" "deny" 2>/dev/null || true

python3 -c "
import json, sys
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': sys.argv[1]
    }
}))" "$REASON"
exit 0
