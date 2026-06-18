#!/usr/bin/env bash
# build-bundle.sh — regenerate the OpenBioHack bundle from the canonical engine, repeatably.
#
# Model: canonical (~/.claude/skills + ~/.claude/hooks) is the source of truth; the bundle is GENERATED.
# Never hand-merge. Run this after any canonical change to re-sync the public bundle.
#
#   1. regenerate the canonical-ahead skills (investigate-health, extract-health-data, research,
#      research-practitioner) — product-search is LEFT ALONE (the bundle is ahead there).
#   2. drop stray *.bak from the bundle skills.
#   3. genericize.py  — re-apply the personal-data scrubs (idempotent; warns if an anchor changed).
#   4. package-hooks.py — bundle the enforcement hooks (cwd-guard stripped) + hooks.json.
#   5. final personal-data gate — fails loudly if anything but intentional attribution survives.
set -uo pipefail
CAN="$HOME/.claude/skills"
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
BR="$ROOT/skills"

echo "== 1. regenerate canonical-ahead skills =="
for s in investigate-health extract-health-data research research-practitioner; do
  [ -d "$CAN/$s" ] || { echo "  !! canonical missing: $s"; exit 1; }
  rm -rf "${BR:?}/${s:?}"; cp -RL "$CAN/$s" "$BR/$s"; echo "  synced $s"
done
echo "  (product-search left as-is — bundle is ahead: Step 2.5 + maintenance)"

echo "== 2. drop stray .bak =="
find "$BR" -name '*.bak*' -delete; echo "  done"

echo "== 3. genericize =="
python3 "$ROOT/build/genericize.py" || echo "  (warnings — review, scan below will gate)"

echo "== 4. package hooks =="
python3 "$ROOT/build/package-hooks.py"

echo "== 5. final personal-data gate =="
hits=$(grep -rniE "Matteo|Trevisan|flank itch|red.?meat pattern|teotrevi|Helsinki|\bTeo\b" "$ROOT" 2>/dev/null \
        | grep -viE "Teo Embers|/eval/case|/input/|/\.git/|/build/|PACKAGING-NOTES|CITATION\.cff|/LICENSE|/NOTICE" || true)
if [ -n "$hits" ]; then
  echo "  FAIL — personal data found (fix genericize.py and re-run):"; echo "$hits"; exit 1
fi
echo "  CLEAN"
echo "== BUILD OK =="
