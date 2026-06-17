#!/usr/bin/env bash
# run-evals.sh — the grep-checker half of the eval harness.
#
# How the harness actually works:
#   1. You ("run the evals") tell Claude in a session.
#   2. Claude reads eval/case-*/input/ for each case, invokes /investigate-health
#      against it, producing artifacts under a per-case work dir.
#   3. Claude then runs THIS script against each case's work dir to grep the
#      produced artifacts for the MUST / MUST_NOT patterns in expected.md.
#   4. This script returns pass/fail per case. Claude reports the summary.
#
# This script does NOT dispatch the orchestrator. The orchestrator is /investigate-health
# invoked inside the session. This script is the deterministic checker.
#
# Usage (Claude invokes this after producing artifacts):
#   ./run-evals.sh <case-dir> <work-dir>
#     case-dir: path to eval/case-NN-slug/ (contains expected.md)
#     work-dir: path where Claude wrote the run's artifacts
#
# Or for batch (greps every case-*/work/ under a base dir):
#   ./run-evals.sh --batch <work-base-dir>
#     work-base-dir contains one subdir per case (named case-NN-slug)

set -eu

EVAL_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

check_case() {
    local case_dir="$1"
    local work_dir="$2"
    local case_name
    case_name="$(basename "$case_dir")"
    local expected="$case_dir/expected.md"

    if [ ! -f "$expected" ]; then
        echo "SKIP $case_name — no expected.md"
        return 0
    fi
    if [ ! -d "$work_dir" ]; then
        echo "FAIL $case_name — work dir $work_dir not found"
        return 1
    fi

    local failed=0
    while IFS= read -r line; do
        case "$line" in
            MUST:*)
                pat="${line#MUST:}"; pat="${pat# }"
                if ! grep -rqE "$pat" "$work_dir" 2>/dev/null; then
                    echo "  FAIL pattern not found: $pat"
                    failed=1
                fi
                ;;
            MUST_NOT:*)
                pat="${line#MUST_NOT:}"; pat="${pat# }"
                if grep -rqE "$pat" "$work_dir" 2>/dev/null; then
                    echo "  FAIL anti-pattern matched: $pat"
                    failed=1
                fi
                ;;
        esac
    done < "$expected"

    if [ $failed -eq 0 ]; then
        echo "PASS $case_name"
        return 0
    fi
    echo "FAIL $case_name"
    return 1
}

if [ "${1:-}" = "--batch" ]; then
    base="$2"
    fail_count=0
    for case_dir in "$EVAL_DIR"/case-*; do
        [ -d "$case_dir" ] || continue
        name="$(basename "$case_dir")"
        check_case "$case_dir" "$base/$name" || fail_count=$((fail_count + 1))
    done
    echo
    echo "═══ $fail_count case(s) failed ═══"
    exit $fail_count
fi

# Single-case mode
if [ $# -lt 2 ]; then
    echo "usage: $0 <case-dir> <work-dir>" >&2
    echo "   or: $0 --batch <work-base-dir>" >&2
    exit 2
fi
check_case "$1" "$2"
