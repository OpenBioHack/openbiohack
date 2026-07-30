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

# STAGE FIRST, SWAP LAST.
# This used to copy the canonical tree straight over the tracked bundle and only gate afterwards. So a
# failing gate left the maintainer's real records sitting in the working tree of a repository whose
# remote is public — 81 modified paths and an entire stale references/ copy, all carrying his data.
# The gate refusing was supposed to be the safe outcome; instead it was the dangerous one.
# Now everything happens in a staging directory and the tracked tree is touched only after the gate
# passes. STAGE is gitignored, so nothing there can be committed even mid-build.
STAGE="$ROOT/.build-stage"
rm -rf "${STAGE:?}"; mkdir -p "$STAGE/skills"

echo "== 1. regenerate canonical-ahead skills (into the staging tree) =="
for s in investigate-health extract-health-data research research-practitioner; do
  [ -d "$CAN/$s" ] || { echo "  !! canonical missing: $s"; exit 1; }
  cp -RL "$CAN/$s" "$STAGE/skills/$s"; echo "  staged $s"
done

# NEVER-SHIP list, applied to the staging tree only. See the note at the top of this section: these are
# excluded because of what they are, not because of a value inside them.
echo "== 1b. drop what never ships =="
NEVER_SHIP="references/REWORK-CORRECTIONS-LOG.md
references/REWORK-PHASE1-CONTRACT.md
references/REWORK-PHASE2-BUILD-SPEC.md
references/REWORK-PROGRESS.md
references/PACKAGING.md
references/PACKAGING-NOTES.md
references/narrative-source.md
references/steps/_superseded
references.OLD-numbered-step-20260716"
printf '%s\n' "$NEVER_SHIP" | while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  for d in "$STAGE"/skills/*/; do
    target="$d$rel"
    [ -e "$target" ] || continue
    rm -rf -- "${target:?}"
    echo "  dropped ${target#"$STAGE"/skills/}"
  done
done
# compiled Python, wherever it sits in the staged tree
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf -- {} + 2>/dev/null || true
find "$STAGE" -name '*.pyc' -delete 2>/dev/null || true
echo "  dropped any __pycache__ and *.pyc"
# product-search is left alone in the bundle, so carry the committed copy through unchanged.
[ -d "$BR/product-search" ] && cp -R "$BR/product-search" "$STAGE/skills/product-search"
echo "  (product-search left as-is — bundle is ahead: Step 2.5 + maintenance)"

echo "== 2. drop stray .bak =="
find "$STAGE" -name '*.bak*' -delete; echo "  done"

echo "== 3. scrub the staged tree =="
# The scrubber is gitignored and never published: its content is pairs of the subject's verbatim text
# and a generic replacement, because a replacement needs the original as its search anchor — so
# publishing it publishes everything it exists to remove. It runs on the STAGING tree, not the tracked
# one. If it is missing, the build stops: continuing would mean gating an unscrubbed tree and relying on
# the gate's pattern list to be exhaustive, which is exactly the assumption that failed.
if [ ! -f "$ROOT/build/genericize.py" ]; then
  echo "  REFUSING — no scrubber at $ROOT/build/genericize.py."
  echo "  It is gitignored by design, so a fresh clone will not have it. Restore it from the private"
  echo "  tree before building a bundle for publication."
  exit 2
fi
python3 "$ROOT/build/genericize.py" "$STAGE" || echo "  (warnings above — anchors that moved in canonical; step 5 is the backstop)"

echo "== 4. package hooks =="
python3 "$ROOT/build/package-hooks.py"

echo "== 5. final personal-data gate =="
# The patterns live OUTSIDE this repo. They used to be written out on this line — inside a file that
# ships in the bundle — so the gate published its own search terms: a full name, a symptom, a city, a
# username. A gate that leaks by being read is the same defect as a scrubber whose content is the
# originals it removes.
# Default is a sibling of the repo root — outside the repo, so it can never be committed, and
# reachable without an environment variable. Override with DENY_PATTERNS.
PATTERNS="${DENY_PATTERNS:-$ROOT/../.deny-patterns}"
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
hits=$(grep -rniE -f <(blocking) "$STAGE" 2>/dev/null \
        | grep -viE "Teo Embers|/eval/case|/input/|/\.git/|/build/|PACKAGING-NOTES|CITATION\.cff|/LICENSE|/NOTICE" || true)
if [ -n "$hits" ]; then
  echo "  FAIL — personal data found (fix the private scrubber and re-run):"; echo "$hits"; exit 1
fi
echo "  CLEAN"

echo "== 6. swap the staged tree in (only now, and only because step 5 passed) =="
for s in investigate-health extract-health-data research research-practitioner product-search; do
  [ -d "$STAGE/skills/$s" ] || continue
  rm -rf "${BR:?}/${s:?}"; mv "$STAGE/skills/$s" "$BR/$s"; echo "  installed $s"
done
rm -rf "${STAGE:?}"
echo "== BUILD OK =="
