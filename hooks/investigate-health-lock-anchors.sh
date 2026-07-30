#!/usr/bin/env bash
# investigate-health-lock-anchors.sh — PostToolUse on Write.
#
# When the run activation marker (<root>/.investigate-active) is written, make
# it KERNEL-IMMUTABLE with `chflags uchg`. From that moment no deletion method
# — rm, unlink, shutil.rmtree, a novel interpreter one-liner — can remove it:
# the kernel refuses regardless of how the command is spelled. This is the
# HARD guarantee behind cleanup-block's best-effort trigger set: the harness
# cannot be silently un-armed and a run cannot be falsely completed.
#
# Lifecycle:
#   - The marker is WRITE-ONCE. The activation reminder and the resume nudge
#     never rewrite an existing marker; a legitimate rewrite (rare) is
#     `chflags nouchg <marker>` -> rewrite -> re-lock.
#   - Teardown (SKILL.md Step 7 cleanup): `chflags -R nouchg <root>` before
#     the end-of-run delete. Crashed-run escape: the same command, any time.
#   - The .investigate-tokens/ dir is deliberately NOT locked: uchg on a
#     directory blocks entry add/remove, which would break token writes.
#
# Idempotent: re-setting uchg on an already-locked file is a no-op. On a
# non-darwin host (no chflags) the hook degrades to a silent no-op — the
# best-effort deny in cleanup-block still applies, the kernel lock does not.
set -eu

INPUT=$(cat)

[ "$(uname -s 2>/dev/null)" = "Darwin" ] || exit 0
command -v chflags >/dev/null 2>&1 || exit 0

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-parse.sh" 2>/dev/null || exit 0
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

ih_parse_input "$INPUT"
[ "$IH_PARSE_OK" = "1" ] || exit 0

FP="$IH_FILE_PATH"
[ -n "$FP" ] || exit 0
case "$FP" in
    /*) ;;
    *) [ -n "$IH_CWD" ] && FP="$IH_CWD/$FP" || exit 0 ;;
esac
[ "$(basename "$FP")" = ".investigate-active" ] || exit 0
[ -f "$FP" ] || exit 0

chflags uchg "$FP" 2>/dev/null \
    && bash "$LOGGER" "investigate-health-lock-anchors" "marker" "path=$FP" "locked-uchg" 2>/dev/null || true
exit 0
