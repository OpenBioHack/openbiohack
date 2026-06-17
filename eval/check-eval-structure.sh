#!/usr/bin/env bash
# check-eval-structure.sh — validates that every investigation eval case is well-formed.
# Required CI gate. Each case must have input/, and an expected.md with >=3 MUST: and >=1 MUST_NOT:.

set -u
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
EVAL_DIR="$ROOT/skills/investigate-health/eval"

if [ ! -d "$EVAL_DIR" ]; then
  echo "FAIL: eval dir not found at $EVAL_DIR"
  exit 1
fi

fail=0
count=0
for case_dir in "$EVAL_DIR"/case-*; do
  [ -d "$case_dir" ] || continue
  count=$((count + 1))
  name="$(basename "$case_dir")"
  exp="$case_dir/expected.md"

  if [ ! -d "$case_dir/input" ]; then
    echo "FAIL $name — missing input/"; fail=1
  fi
  if [ ! -f "$exp" ]; then
    echo "FAIL $name — missing expected.md"; fail=1; continue
  fi
  musts="$(grep -cE '^MUST:' "$exp" 2>/dev/null || echo 0)"
  mustnots="$(grep -cE '^MUST_NOT:' "$exp" 2>/dev/null || echo 0)"
  # Hard gate = the true structural invariant: at least one positive and one negative assertion.
  if [ "$musts" -lt 1 ]; then
    echo "FAIL $name — no MUST: patterns"; fail=1
  fi
  if [ "$mustnots" -lt 1 ]; then
    echo "FAIL $name — no MUST_NOT: patterns"; fail=1
  fi
  # Quality guideline (warn, don't fail): new cases should aim for >=3 MUST (see CONTRIBUTING.md).
  if [ "$musts" -ge 1 ] && [ "$musts" -lt 3 ]; then
    echo "WARN $name — only $musts MUST: patterns (guideline: >=3 for new cases)"
  fi
  if [ ! -f "$case_dir/expected.fail-modes.md" ]; then
    echo "WARN $name — no expected.fail-modes.md (recommended)"
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "check-eval-structure: all $count cases well-formed ✓"
fi
exit "$fail"
