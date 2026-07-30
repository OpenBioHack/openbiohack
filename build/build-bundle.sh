#!/usr/bin/env bash
# build-bundle.sh — regenerate the OpenBioHack bundle from the canonical engine, repeatably.
#
# Model: canonical (~/.claude/skills + ~/.claude/hooks) is the source of truth; the bundle is GENERATED.
# Never hand-merge. Run this after any canonical change to re-sync the public bundle.
#
#   1. regenerate the canonical-ahead skills (investigate-health, extract-health-data, research,
#      research-practitioner) — product-search is LEFT ALONE (the bundle is ahead there).
#   2. drop stray *.bak from the bundle skills.
#   3. (scrubber — private, not shipped; step 5 below is the gate that actually enforces the result).
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

echo "== 3. scrub (kept private) =="
echo "  (the scrubber is not published — its content is every original it exists to remove, so it stays in the private tree; step 5 is what enforces the result)"

echo "== 4. package hooks =="
python3 "$ROOT/build/package-hooks.py"

echo "== 5. final personal-data gate =="
# The patterns live OUTSIDE this repo. They used to be written out on this line — inside a file that
# ships in the bundle — so the gate published its own search terms: a full name, a symptom, a city, a
# username. A gate that leaks by being read is the same defect as a scrubber whose content is the
# originals it removes.
PATTERNS="${DENY_PATTERNS:-$HOME/.openbiohack-deny-patterns}"
if [ ! -s "$PATTERNS" ]; then
  # A missing list must STOP the build. `grep -f` on a nonexistent file matches nothing, which reads
  # identically to CLEAN — a gate reporting success about a tree nothing examined is worse than none.
  echo "  REFUSING — no pattern file at $PATTERNS. This gate cannot report CLEAN without knowing what"
  echo "  to look for. One extended regex per line, kept outside the repo so it cannot be published."
  exit 2
fi
# Blocking tier only. A `## warn` tier holds clinical vocabulary a health tool has to be able to say —
# treating those as blocking makes the gate unpassable, and an unpassable gate gets switched off.
# Comments and blank lines go in the same pass: in a `-f` list a `#` line is a literal pattern, and a
# BLANK line matches every line of every file, which would make this an unconditional FAIL.
blocking() {
  awk '/^## *fail/{t=1;next} /^## *warn/{t=0;next} /^[[:space:]]*#/||/^[[:space:]]*$/{next} t' "$PATTERNS"
}
[ -n "$(blocking)" ] || { echo "  REFUSING — $PATTERNS declares no blocking pattern"; exit 2; }
hits=$(grep -rniE -f <(blocking) "$ROOT" 2>/dev/null \
        | grep -viE "Teo Embers|/eval/case|/input/|/\.git/|/build/|PACKAGING-NOTES|CITATION\.cff|/LICENSE|/NOTICE" || true)
if [ -n "$hits" ]; then
  echo "  FAIL — personal data found (fix the private scrubber and re-run):"; echo "$hits"; exit 1
fi
echo "  CLEAN"
echo "== BUILD OK =="
