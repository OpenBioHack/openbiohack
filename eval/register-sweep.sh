#!/usr/bin/env bash
# register-sweep.sh — deterministic register linter for OpenBioHack.
#
# Fails (exit 1) if any person-facing CONTENT doc contains a directive / outcome-promise /
# fresh-diagnosis / escalation leak. This is a required CI gate.
#
# Scope note: this sweeps the docs that deliver content to the person and therefore must NEVER
# contain these patterns. It deliberately does NOT scan CLAUDE.md or the single-file prompt — those
# DEFINE the banned patterns (quoting them is correct), so a lexical sweep there false-positives.
# Those two are reviewed by humans against CLAUDE.md §2–§3. Skill files are skill-internal
# instructions (imperative voice to the assistant is expected) and are likewise out of scope here.

set -u
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"

FILES=(
  "references/optimization.md"
  "references/high-value-levers.md"
  "references/n1-protocol.md"
  "templates/symptom-log.md"
  "templates/experiment-log.md"
)

# Also sweep the offer-example library: these are client-facing OFFER prose (the bar the
# offer-writer matches), so they must hold the person-facing register even though they live in
# the skill. Globbed so newly-added examples are covered automatically.
for _oe in "$ROOT"/skills/investigate-health/references/offer-examples/*.md; do
  [ -f "$_oe" ] && FILES+=("${_oe#"$ROOT"/}")
done

# Pattern => human label. Each is a register leak when it appears in a content doc.
PATTERNS=(
  '\b(fixable|will resolve|will fix|solves it)\b|\bwill (boost|cure|enhance)\b::outcome-promise'
  'the (actual|real) (cause|finding|driver|issue)::certainty/finding construction'
  'the diagnosis (is|remains)|a (likely|working|probable|possible) diagnosis::fresh-diagnosis (tool voice)'
  'you should|you must|you need to|I recommend|we recommend::directive to the person'
  '\b(confirms|proves|clearly|obviously|definitely)\b::escalation word below established-tier'
)

fail=0
for f in "${FILES[@]}"; do
  path="$ROOT/$f"
  [ -f "$path" ] || { echo "MISSING: $f"; fail=1; continue; }
  for entry in "${PATTERNS[@]}"; do
    pat="${entry%%::*}"; label="${entry##*::}"
    if hits="$(grep -nEi "$pat" "$path")"; then
      echo "REGISTER LEAK [$label] in $f:"
      echo "$hits" | sed 's/^/    /'
      fail=1
    fi
  done
done

if [ "$fail" -eq 0 ]; then
  echo "register-sweep: clean ✓ (${#FILES[@]} content docs)"
fi
exit "$fail"
