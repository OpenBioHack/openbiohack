#!/usr/bin/env bash
# investigate-health-label-density.sh — PreToolUse on Write|Edit.
#
# Round 5 (Phase C2): blocks synthesis-layer writes that exceed the
# label-density threshold (1 diagnosis-label token per 200 words of body text,
# excluding the `## Labels referenced` section).
#
# Applies to: working-hypothesis.md, step2-mechanism-map.md,
# step5-cross-check.md, step6-prioritize.md.
#
# Threshold deliberately loose initially; tighten after FP monitoring.

set -eu

INPUT=$(cat)


HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"
TOKENS_FILE="$HOME/.claude/skills/investigate-health/references/label-tokens.md"

PARSED=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {}) or {}
print(d.get('session_id', ''))
print(ti.get('file_path', ''))
print('---CONTENT---')
c = ti.get('content', '') or ti.get('new_string', '')
print(c)
" 2>/dev/null) || exit 0

SESSION=$(printf '%s' "$PARSED" | sed -n '1p')
FILE_PATH=$(printf '%s' "$PARSED" | sed -n '2p')
CONTENT=$(printf '%s' "$PARSED" | sed -n '/^---CONTENT---$/,$p' | tail -n +2)

BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")
case "$BASENAME" in
    working-hypothesis.md|step2-mechanism-map.md|step5-cross-check.md|step6-prioritize.md|hypothesis-set.md) ;;
    *) exit 0 ;;
esac

if [ ! -f "$TOKENS_FILE" ]; then
    # Tokens file missing — fail-open with log
    bash "$LOGGER" "investigate-health-label-density" "$BASENAME" "session=$SESSION" "allow-no-tokens" 2>/dev/null || true
    exit 0
fi

deny() {
    local reason="$1"
    bash "$LOGGER" "investigate-health-label-density" "$BASENAME" "session=$SESSION" "deny" 2>/dev/null || true
    python3 -c "
import json, sys
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': sys.argv[1]
    }
}))" "$reason"
    exit 0
}

VIOLATION=$(printf '%s' "$CONTENT" | TOKENS_FILE="$TOKENS_FILE" python3 -c "
import sys, re, os

text = sys.stdin.read()
tokens_path = os.environ['TOKENS_FILE']

# Load tokens (skip comments and blank lines)
tokens = []
with open(tokens_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        # Skip table-like lines
        if line.startswith('|'):
            continue
        tokens.append(line)
# Filter very short acronyms (<3 chars) — too many false positives
tokens = [t for t in tokens if len(t) >= 3]

# Strip out '## Labels referenced' section if present
# (Find any section header matching that name to end-of-file or next section)
parts = re.split(r'(?im)^##\s+labels referenced.*?$', text, maxsplit=1)
body = parts[0] if len(parts) >= 1 else text
# Further: if there's anything after the Labels section header, exclude it
# (assume Labels section is last)

# Strip fenced code blocks
body = re.sub(r'\`\`\`.*?\`\`\`', '', body, flags=re.DOTALL)
# Strip inline code
body = re.sub(r'\`[^\`]*\`', '', body)

# Count body words
words = re.findall(r'\b\w+\b', body)
n_words = len(words)
if n_words < 100:
    sys.exit(0)  # too small to meaningfully measure

# Count label tokens (whole-word, case-insensitive)
label_hits = []
for tok in tokens:
    # Escape regex specials but keep alphanumerics + spaces + hyphens
    pat = re.escape(tok)
    matches = re.findall(r'(?i)\b' + pat + r'\b', body)
    if matches:
        label_hits.extend([tok] * len(matches))

n_labels = len(label_hits)

# Threshold: 1 label per 200 words of body
threshold = n_words / 200.0
if n_labels > threshold:
    # Find a sample offending paragraph
    paragraphs = re.split(r'\n\s*\n', body)
    sample = ''
    for p in paragraphs:
        c = 0
        for tok in tokens:
            c += len(re.findall(r'(?i)\b' + re.escape(tok) + r'\b', p))
        if c >= 2:
            sample = p.strip()[:400]
            break
    print(f'LABEL_DENSITY: {n_labels} labels in {n_words} body words (threshold ~{threshold:.1f}). Sample paragraph: {sample}')
    sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
    deny "Label-density too high: $VIOLATION. Rule: investigate-health SKILL.md Step 2 §'Three-layer label rule (phase-aware)'. Synthesis-layer files translate diagnosis labels to process descriptions on intake. Keep label-density in body text ≤ 1 label per 200 words. Move enumerated labels to a trailing '## Labels referenced' section (exempt). Maintained token list: ~/.claude/skills/investigate-health/references/label-tokens.md."
}

bash "$LOGGER" "investigate-health-label-density" "$BASENAME" "session=$SESSION" "allow" 2>/dev/null || true
exit 0
