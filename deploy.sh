#!/usr/bin/env bash
# deploy.sh <git-ref> — materialize that ref's hooks/ into the live hook dir.
#
# This is the ONLY writer of the live investigate-health hooks. The git-tracked
# openbiohack repo is the canonical source of truth; ~/.claude/hooks is a
# materialized snapshot of whatever ref you deploy. Rollback = deploy an older tag.
#
#   ./deploy.sh ih-fix-2026-07-07          # deploy a tag
#   ./deploy.sh main                       # deploy the branch head
#   DEPLOY_TARGET=/tmp/x ./deploy.sh main  # test-materialize somewhere else
#
# Scope: only the investigate-health family (investigate-health-*.sh,
# audit-council-completion.sh, council-*.sh, hooks/lib/*). Never touches any
# other live hook. hooks.json (public-plugin registration) is NOT deployed —
# the private install registers via ~/.claude/settings.json instead.
#
# ROLLBACK FLOOR: ih-fix-2026-07-07 is the earliest safe rollback target.
# ih-seed-2026-07-07 is KNOWN-VULNERABLE (forgeable finish-line-token cleanup
# unlock) and MUST NOT be deployed once ih-fix exists.

set -euo pipefail

REPO="$(cd -- "$(dirname -- "$0")" && pwd)"
REF="${1:?usage: deploy.sh <git-ref|tag>   (rollback = deploy an older tag)}"
LIVE="${DEPLOY_TARGET:-$HOME/.claude/hooks}"
SETTINGS="${DEPLOY_SETTINGS:-$HOME/.claude/settings.json}"

git -C "$REPO" rev-parse --verify --quiet "$REF^{commit}" >/dev/null \
    || { echo "deploy.sh: unknown git ref '$REF'" >&2; exit 1; }
SHA="$(git -C "$REPO" rev-parse --short "$REF^{commit}")"

# --- known-vulnerable guard -------------------------------------------------
SEED_SHA="$(git -C "$REPO" rev-parse --quiet --verify 'ih-seed-2026-07-07^{commit}' 2>/dev/null || true)"
FIX_SHA="$(git -C "$REPO" rev-parse --quiet --verify 'ih-fix-2026-07-07^{commit}' 2>/dev/null || true)"
if [ -n "$SEED_SHA" ] && [ -n "$FIX_SHA" ] \
   && [ "$(git -C "$REPO" rev-parse "$REF^{commit}")" = "$SEED_SHA" ]; then
    echo "*** WARNING: '$REF' is the ih-seed snapshot — KNOWN-VULNERABLE ***"
    echo "It re-arms the forgeable finish-line-token cleanup unlock fixed in"
    echo "ih-fix-2026-07-07. The rollback FLOOR is ih-fix-2026-07-07."
    printf "Deploy it anyway? [y/N] "
    read -r ok
    [ "$ok" = "y" ] || [ "$ok" = "Y" ] || { echo "Aborted."; exit 1; }
fi

# --- materialize the ref into a temp dir ------------------------------------
TMP="$(mktemp -d "${TMPDIR:-/tmp}/ih-deploy.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
git -C "$REPO" archive "$REF" hooks | tar -x -C "$TMP"

# Family file list = what the ref ships (minus plugin-only hooks.json).
REF_FILES=()
while IFS= read -r f; do
    case "$(basename "$f")" in hooks.json) continue ;; esac
    REF_FILES+=("$f")
done < <(cd "$TMP/hooks" && find . -type f | sed 's#^\./##' | sort)

mkdir -p "$LIVE/lib"

echo "== deploy $REF ($SHA) -> $LIVE =="
echo
echo "-- changes (live vs ref) --"
CHANGED=0
for f in "${REF_FILES[@]}"; do
    if [ ! -f "$LIVE/$f" ]; then
        echo "  NEW      $f"; CHANGED=1
    elif ! cmp -s "$TMP/hooks/$f" "$LIVE/$f"; then
        echo "  UPDATE   $f"; CHANGED=1
    fi
done
# Live family files absent from the ref (e.g. after a rollback below a
# file-adding tag). Removing them prevents stale enforcement; a settings.json
# entry pointing at a removed file must ALSO be un-registered (checklist below).
STALE=()
for pat in "investigate-health-*.sh" "audit-council-completion.sh" "council-*.sh"; do
    for lf in "$LIVE"/$pat; do
        [ -f "$lf" ] || continue
        b="$(basename "$lf")"
        [ -f "$TMP/hooks/$b" ] || { STALE+=("$b"); echo "  REMOVE   $b (not in $REF)"; CHANGED=1; }
    done
done
[ "$CHANGED" = 1 ] || echo "  (live already matches $REF)"
echo

if [ "$CHANGED" = 1 ] && [ "${DEPLOY_YES:-}" != "1" ]; then
    printf "Apply? [y/N] "
    read -r ok
    [ "$ok" = "y" ] || [ "$ok" = "Y" ] || { echo "Aborted — nothing written."; exit 1; }
fi

for f in "${REF_FILES[@]}"; do
    install -m 0755 "$TMP/hooks/$f" "$LIVE/$f"
done
for b in ${STALE[@]+"${STALE[@]}"}; do
    rm -f "$LIVE/$b"
done

# --- verify: every settings-registered family hook file exists ---------------
echo "-- settings.json registration check --"
DANGLING=0
if [ -f "$SETTINGS" ]; then
    while IFS= read -r cmd; do
        p="${cmd/#\~/$HOME}"
        p="${p//\$HOME/$HOME}"
        if [ ! -f "$p" ]; then
            echo "  DANGLING registration: $cmd (file missing)"; DANGLING=1
        fi
    done < <(python3 -c "
import json, sys, re
try:
    s = json.load(open('$SETTINGS'))
except Exception:
    sys.exit(0)
for ev, groups in (s.get('hooks') or {}).items():
    for g in groups or []:
        for h in (g.get('hooks') or []):
            c = h.get('command') or ''
            if re.search(r'(investigate-health-[a-z-]+\.sh|audit-council-completion\.sh|council-[a-z-]+\.sh)', c):
                print(c)
")
    [ "$DANGLING" = 0 ] && echo "  all registered family hooks exist: OK"
else
    echo "  ($SETTINGS not found — skipped)"
fi

echo
echo "== deployed $REF ($SHA) =="
echo
echo "Ordered checklist:"
echo "  1. If this deploy ADDED a hook that needs registration (lock-anchors,"
echo "     activate), apply the settings.json registration AFTER this deploy:"
echo "       python3 $REPO/deploy/settings-register.py"
echo "     (Until it lands, the marker kernel-lock hook is INERT.)"
echo "  2. If this deploy ROLLED BACK below the tag that introduced"
echo "     lock-anchors/activate, un-register them FIRST (avoids a dangling"
echo "     PostToolUse:Write reference):"
echo "       python3 $REPO/deploy/settings-unregister.py"
echo "  3. Rollback at any time:  $0 <older-tag>"
echo "     Tags: $(git -C "$REPO" tag -l 'ih-*' | tr '\n' ' ')"
echo "     FLOOR: ih-fix-2026-07-07 (ih-seed-2026-07-07 is KNOWN-VULNERABLE)."
echo "  4. uchg markers in old run dirs survive any rollback; clear one with:"
echo "       chflags -R nouchg '<run-root>'"
[ "$DANGLING" = 1 ] && { echo; echo "*** FIX THE DANGLING REGISTRATION ABOVE ***"; exit 2; }
exit 0
