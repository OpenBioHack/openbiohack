#!/usr/bin/env bash
# investigate-health-write-check.sh — PreToolUse on Write|Edit.
#
# Gates Writes/Edits to: working-hypothesis.md, step5-cross-check.md,
# hypothesis-set.md, step6-prioritize.md, offering.md
#
# v1.1 (2026-06-09): fixed false positives on tier-range mentions (T1-T5),
# markdown table rows, code spans, bulleted documentation lines, and small
# bootstrap stubs.
# v1.2 (2026-06-18): Working-Truth governance layer. Step-5 gate also requires
# working-truth.md (non-empty) + a research/anomaly-<slug>-*.md per [slug:] in
# step2 ## Anomalies (Dm). Step-6 gate also requires working-truth.md +
# coherence-map.md (## Deepening / ## Discrepancies / ## Verdicts, no un-tagged
# discrepancy). New Check 7: temporal/sequence/correlation claims in synthesis
# files must carry a source + date citation (Dv).

set -eu

INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

PARSED=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {}) or {}
print(d.get('cwd', ''))
print(d.get('session_id', ''))
print(ti.get('file_path', ''))
print('---CONTENT---')
c = ti.get('content', '') or ti.get('new_string', '')
print(c)
" 2>/dev/null) || exit 0

CWD=$(printf '%s' "$PARSED" | sed -n '1p')
SESSION=$(printf '%s' "$PARSED" | sed -n '2p')
FILE_PATH=$(printf '%s' "$PARSED" | sed -n '3p')
CONTENT=$(printf '%s' "$PARSED" | sed -n '/^---CONTENT---$/,$p' | tail -n +2)

BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")
case "$BASENAME" in
    working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md|offering.md) ;;
    constraints-*.md|shape-profile-*.md|mechanism-map-*.md|convergence-*.md) ;;
    *) exit 0 ;;
esac

# --- root-anchored scope guard (compaction-proof + portable; replaces hardcoded path) ---
# Active iff the cwd OR the file being written lives at/under a run root that carries the
# bootstrap's .investigate-active marker. No hardcoded project path.
investigate_is_active "$CWD" "$FILE_PATH" || exit 0
# --- end scope guard ---

INVESTIGATE_STATE_DIR="$(investigate_state_dir "$SESSION")"
export INVESTIGATE_STATE_DIR
INVESTIGATE_RUN_STATE_DIR="$(investigate_run_token_dir "$FILE_PATH" 2>/dev/null || true)"
export INVESTIGATE_RUN_STATE_DIR

deny() {
    local reason="$1"
    bash "$LOGGER" "investigate-health-write-check" "$BASENAME" "session=$SESSION" "deny" 2>/dev/null || true
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

# STUB-ALLOWLIST: bootstrap stubs are tiny (<500 bytes) and contain explicit
# stub markers. Let them through unchecked.
CONTENT_LEN=$(printf '%s' "$CONTENT" | wc -c | tr -d ' ')
if [ "$CONTENT_LEN" -lt 800 ] && printf '%s' "$CONTENT" | grep -qiE '(empty stub|pending Step|in progress|_pending_|^> Empty)'; then
    bash "$LOGGER" "investigate-health-write-check" "$BASENAME" "session=$SESSION size=$CONTENT_LEN" "allow-stub" 2>/dev/null || true
    exit 0
fi

# Check S - step-sequence / required-artifact gate (forces the mandated dispatches happened).
# Fails closed; the only escape is the explicit "none" artifact named in the deny message.
ROOT="$(dirname "$FILE_PATH" 2>/dev/null || echo .)"
if [ "$BASENAME" = "step5-cross-check.md" ]; then
    HSET="$ROOT/hypothesis-set.md"
    MISSING=""
    if [ ! -s "$HSET" ]; then
        MISSING="$MISSING hypothesis-set.md(Step-4.5-must-precede-Step-5)"
    else
        HYPS=$(grep -iE '^#{2,4}[[:space:]]+H[0-9]+' "$HSET" 2>/dev/null | grep -iv 'null' | grep -oiE 'H[0-9]+' | tr '[:upper:]' '[:lower:]' | sort -u || true)
        for hn in $HYPS; do
            ls "$ROOT/research/${hn}"*consensus*.md >/dev/null 2>&1 || MISSING="$MISSING research/${hn}-*-consensus.md"
            ls "$ROOT/research/${hn}"*practitioner*.md >/dev/null 2>&1 || MISSING="$MISSING research/${hn}-*-practitioner.md"
        done
    fi
    [ -s "$ROOT/hypothesis-diversity-judge.md" ] || MISSING="$MISSING hypothesis-diversity-judge.md"
    [ -s "$ROOT/research/practitioner-claim-rubric.md" ] || MISSING="$MISSING research/practitioner-claim-rubric.md"
    # (d) governance ledger must exist + be non-empty (D11 state-on-disk)
    [ -s "$ROOT/working-truth.md" ] || MISSING="$MISSING working-truth.md(governance-ledger-must-exist)"
    # (e) per-anomaly mechanism map (Dm): each [slug: X] in step2 ## Anomalies needs research/anomaly-X*.md
    STEP2="$ROOT/step2-mechanism-map.md"
    if [ -s "$STEP2" ] && ! grep -qiE 'NO OUT-OF-BOUNDS RESULTS' "$STEP2" 2>/dev/null; then
        SLUGS=$(grep -oiE '\[slug:[[:space:]]*[a-zA-Z0-9_-]+' "$STEP2" 2>/dev/null | sed -E 's/.*slug:[[:space:]]*//' | tr '[:upper:]' '[:lower:]' | sort -u || true)
        for sl in $SLUGS; do
            ls "$ROOT/research/anomaly-${sl}"*.md >/dev/null 2>&1 || MISSING="$MISSING research/anomaly-${sl}-*.md(Dm-mechanism-map)"
        done
    fi
    if [ -n "$MISSING" ]; then
        deny "Step-5 gate: step5-cross-check.md blocked until the mandated upstream dispatches have produced their artifacts. MISSING:$MISSING . Per the SKILL required-artifact contract, dispatch a paired /research + /research-practitioner for EACH non-null hypothesis in hypothesis-set.md, the hypothesis-diversity judge, and the practitioner-claim judge council (consolidate verdicts to research/practitioner-claim-rubric.md, or write that file containing 'NO LOAD-BEARING PRACTITIONER CLAIMS - <reason>'). Also required: working-truth.md (the governance ledger) must exist and be non-empty, and each out-of-bounds result enumerated in step2-mechanism-map.md '## Anomalies' as [slug: X] needs a research/anomaly-X-*.md mechanism map (Dm) - or the section must say 'NO OUT-OF-BOUNDS RESULTS - <reason>'. Thoroughness over tokens - this step cannot be skipped."
    fi
fi
if [ "$BASENAME" = "step6-prioritize.md" ]; then
    QBANK="$ROOT/question-bank.md"
    MISSING=""
    if [ ! -s "$QBANK" ]; then
        MISSING="$MISSING question-bank.md(Step-5.5-interview-must-precede-Step-6)"
    elif grep -qiE '^(INTERVIEW-BLOCKED|INTERVIEW-SATURATED-AFTER-PASS-1)' "$QBANK" 2>/dev/null; then
        : # first-line escape marker present — interview legitimately closed; gate satisfied
    else
        # (a) per non-null Hn in hypothesis-set.md, a harvested question-pool section
        HSET6="$ROOT/hypothesis-set.md"
        if [ -s "$HSET6" ]; then
            HYPS6=$(grep -iE '^#{2,4}[[:space:]]+H[0-9]+' "$HSET6" 2>/dev/null | grep -iv 'null' | grep -oiE 'H[0-9]+' | tr '[:upper:]' '[:lower:]' | sort -u || true)
            for hn in $HYPS6; do
                grep -qiE "^##[[:space:]]+Question pool[[:space:]]*[—–-].*${hn}([^0-9]|$)" "$QBANK" 2>/dev/null || MISSING="$MISSING question-pool-section-for-${hn}"
            done
        fi
        # (b) dispositions in use
        grep -qiE '\b(answered|partial|open)\b' "$QBANK" 2>/dev/null || MISSING="$MISSING dispositions(answered|partial|open)"
        # (c) >= 2 '### Pass N' blocks under the pass log
        PASSCOUNT=$(grep -ciE '^###[[:space:]]+Pass[[:space:]]+[0-9]+' "$QBANK" 2>/dev/null || true)
        [ "${PASSCOUNT:-0}" -ge 2 ] || MISSING="$MISSING >=2-###-Pass-N-blocks(found=${PASSCOUNT:-0})"
        # (d) recombination-check entry
        grep -qiE '^##[[:space:]]+Recombination-check' "$QBANK" 2>/dev/null || MISSING="$MISSING ##-Recombination-check"
    fi
    if [ -n "$MISSING" ]; then
        deny "Step-6 gate: step6-prioritize.md blocked until the multi-pass interview (Step 5.5) produced question-bank.md to its contract. MISSING:$MISSING . Per the SKILL required-artifact contract: harvest each hypothesis's '## Differentiating diagnostic questions' into a '## Question pool - <Hn>' section, subtract what the data already answers (dispositions), ask in >=2 ranked passes (each a '### Pass N' block under '## Pass log'), and record a '## Recombination-check' entry. A single shallow round cannot pass. The only escapes are a first-line 'INTERVIEW-BLOCKED - <reason>' or 'INTERVIEW-SATURATED-AFTER-PASS-1 - <reason>' marker. Thoroughness over tokens - this step cannot be skipped."
    fi
    # Step-6 governance gate (additive) — working-truth ledger + coherence map (D5).
    GMISSING=""
    [ -s "$ROOT/working-truth.md" ] || GMISSING="$GMISSING working-truth.md(governance-ledger-must-exist)"
    CMAP="$ROOT/coherence-map.md"
    if [ ! -s "$CMAP" ]; then
        GMISSING="$GMISSING coherence-map.md(Step-5.7-deepen-coherence-loop-must-precede-Step-6)"
    else
        grep -qiE '^##[[:space:]]+Deepening' "$CMAP" 2>/dev/null || GMISSING="$GMISSING coherence-map.md:##-Deepening-section"
        grep -qiE '^##[[:space:]]+Discrepancies' "$CMAP" 2>/dev/null || GMISSING="$GMISSING coherence-map.md:##-Discrepancies-section"
        grep -qiE '^##[[:space:]]+Verdicts' "$CMAP" 2>/dev/null || GMISSING="$GMISSING coherence-map.md:##-Verdicts-section"
        # no un-tagged discrepancy: every '- ' bullet under ## Discrepancies must carry OPEN-GAP or a ':' explanation
        UNTAGGED=$(awk '
            /^##[[:space:]]+Discrepancies/ {insec=1; next}
            /^##[[:space:]]/ {insec=0}
            insec && /^[[:space:]]*-[[:space:]]/ {
                if ($0 !~ /OPEN-GAP/ && $0 !~ /:/) { c++ }
            }
            END { print c+0 }
        ' "$CMAP" 2>/dev/null || echo 0)
        [ "${UNTAGGED:-0}" -eq 0 ] || GMISSING="$GMISSING coherence-map.md:un-tagged-discrepancy(count=${UNTAGGED})"
    fi
    if [ -n "$GMISSING" ]; then
        deny "Step-6 governance gate: step6-prioritize.md blocked until the Working-Truth ledger and the Step-5.7 coherence loop have produced their artifacts. MISSING:$GMISSING . Per the SKILL required-artifact contract: working-truth.md (the governance ledger) must exist and be non-empty, and coherence-map.md must carry '## Deepening - <Hn>', '## Discrepancies', and '## Verdicts' sections with EVERY discrepancy line either explained (':'-separated resolution) or tagged 'OPEN-GAP' - no silent drop. See references/coherence-map.md and references/working-truth-ledger.md."
    fi
fi
if [ "$BASENAME" = "offering.md" ]; then
    if [ ! -s "$ROOT/extracted/spot-check.md" ]; then
        deny "Step-7 gate: offering.md blocked until extracted/spot-check.md exists (the independent extraction spot-check). Dispatch the spot-check agent first, then retry."
    fi
fi

# ============================================================================
# Phase-B deepening-loop gates (Steps 5.8-5.13). Each B-chain Write is blocked
# until its upstream artifact is well-formed. Plus the lexical GRAIN pre-check on
# shape-profile / convergence (flags aggregate-as-actor for the decomposition auditor).
# ============================================================================

# --- lexical grain pre-check (used by B2 + B5 below) ---
# Denies a line that uses an AGGREGATE as a single ACTOR ("the drug family confers
# resistance", "the consortium survives") or an UNSPECIFIED relation ("confers resistance"
# with no named target) UNLESS the same line carries a decomposition acknowledgement
# (an explicit member/species breakdown, an arrow, 'namely/specifically', or a [grain:] tag).
# This is a pre-check, not the final word — the decomposition auditor confirms semantically.
grain_check() {
    local content="$1" where="$2"
    local hit
    hit=$(printf '%s' "$content" | python3 -c '
import sys, re
text = sys.stdin.read()
# strip fenced + inline code
text = re.sub(r"\x60\x60\x60.*?\x60\x60\x60", "", text, flags=re.DOTALL)
text = re.sub(r"\x60[^\x60]*\x60", "", text)
AGG = r"\bthe\s+(?:drug|antibiotic|antimicrobial|treatment|kill|supplement)[- ]?(?:set|family|class|group|regimen|protocol|stack)\b|\bthe\s+(?:consortium|community|biofilm community)\b"
ACTION = r"\b(survives?|resists?|confers?|feeds?|shelters?|protects?|persists?|rebounds?|clears?|outcompetes?)\b"
UNSPEC = r"\bconfers\s+resistance\b(?!\s+(?:to|against)\b)|\bis\s+resistant\b(?!\s+(?:to|against)\b)|\bfeeds\s+it\b|\bshelters\s+it\b"
DECOMP = r"→|->|\bnamely\b|\bspecifically\b|\[grain:|\bmember\b|\bspecies\b|\beach\s+(?:of|member)\b"
bad = []
for raw in text.split("\n"):
    line = raw.strip()
    if not line or line.startswith("|") or line.startswith("#"):
        continue
    agg_actor = re.search(AGG, line, re.I) and re.search(ACTION, line, re.I)
    unspec = re.search(UNSPEC, line, re.I)
    if (agg_actor or unspec) and not re.search(DECOMP, line, re.I):
        bad.append(line[:160])
print("\n".join(bad[:3]))
' 2>/dev/null)
    if [ -n "$hit" ]; then
        deny "Grain check ($where): a load-bearing line treats an AGGREGATE as a single actor, or asserts an UNSPECIFIED relation, without decomposing it to checkable members. Per SKILL.md B2 (Shape Deduction) the decomposition is part of shape-finding: explode 'the drug family / the consortium' to its members (family -> species, NOT to atoms) and specify every relation's end + mechanism ('confers resistance TO whom, BY what') before it bears weight. Add the member-level breakdown on the line (or tag it [grain: decomposed] once the members are spelled out elsewhere). Offending: $hit"
    fi
}

# --- B1 (5.8): constraints-<Hn>.md ---
case "$BASENAME" in
  constraints-*.md)
    MISS=""
    printf '%s' "$CONTENT" | grep -qiE '^##[[:space:]]+Must-fit constraints' || MISS="$MISS ##-Must-fit-constraints-section"
    printf '%s' "$CONTENT" | grep -qiE '^##[[:space:]]+Blind-spot constraints' || MISS="$MISS ##-Blind-spot-constraints-section"
    printf '%s' "$CONTENT" | grep -qiE '\bonset\b|\bperturb' || MISS="$MISS onset/perturbation-constraint(or 'not applicable - reason')"
    printf '%s' "$CONTENT" | grep -qiE 'surviv|reservoir' || MISS="$MISS survival-explanation-constraint(or 'not applicable - reason')"
    if [ -n "$MISS" ]; then
        deny "B1 gate (Step 5.8): constraints-$BASENAME blocked until it is well-formed. MISSING:$MISS . Per SKILL.md B1, a constraints file needs a '## Must-fit constraints' section (each line 'the cause must / cannot ...', source-traced) INCLUDING an onset/perturbation constraint and a survival-explanation constraint (or an explicit 'not applicable - <reason>' for either), plus a non-empty '## Blind-spot constraints' section (what each result, positive AND negative, cannot see)."
    fi
    ;;
  shape-profile-*.md)
    # B2: requires the matching constraints file to exist first.
    HN=$(printf '%s' "$BASENAME" | sed -E 's/^shape-profile-(.*)\.md$/\1/')
    [ -s "$ROOT/constraints-$HN.md" ] || deny "B2 gate (Step 5.9): shape-profile-$HN.md blocked until constraints-$HN.md exists (B1 must precede B2 — the shape is deduced FROM the constraints). Write constraints-$HN.md first."
    grain_check "$CONTENT" "B2 shape-profile"
    ;;
  mechanism-map-*.md)
    # B3: requires at least one shape-profile in the root; schema + exclusion-discipline + discriminator.
    ls "$ROOT/shape-profile-"*.md >/dev/null 2>&1 || deny "B3 gate (Step 5.10): mechanism-map blocked until a shape-profile-<Hn>.md exists in the run root (B2 must precede B3 — candidates are matched against the deduced shape). Write the shape profile first."
    MISS=""
    printf '%s' "$CONTENT" | grep -qiE 'vulnerab' || MISS="$MISS vulnerabilities-node(what-disrupts-each-node)"
    printf '%s' "$CONTENT" | grep -qiE 'persistence[- ]structure|persistence structure' || MISS="$MISS persistence-structure(+disruptors)"
    printf '%s' "$CONTENT" | grep -qiE 'askable-now|in-records|needs-test' || MISS="$MISS cheapest-discriminator-tag(askable-now/in-records/needs-test)"
    # exclusion discipline: any exclusion must be (a)-strength; a (b)/(c) tag used to EXCLUDE is denied.
    BADEXCL=$(printf '%s' "$CONTENT" | grep -niE '\((b|c)\)' 2>/dev/null | grep -iE 'exclud|ruled out|removed|eliminat' | grep -ivE '\bnot\b|\bnever\b|kept in|retained|may (lower|reduce|down-weight)|lowers? weight|only an?[[:space:]]*\(a\)|claim-strength|legend' || true)
    [ -z "$BADEXCL" ] || MISS="$MISS (b)/(c)-strength-used-to-exclude[$(printf '%s' "$BADEXCL" | head -1 | cut -c1-80)]"
    if [ -n "$MISS" ]; then
        deny "B3 gate (Step 5.10): mechanism-map $BASENAME blocked until the domain-neutral schema and exclusion discipline are complete. MISSING:$MISS . Per SKILL.md B3: every node needs a 'vulnerabilities' entry and a 'persistence-structure' (+ disruptors); every candidate/load-bearing property carries a cheapest-discriminator tag (askable-now / in-records / needs-test); and ONLY an (a) examined-and-excluded-with-mechanism finding (citing a primary-source sentence) may EXCLUDE a candidate — a (b) primarily/mostly or (c) never-examined tag may lower but must NOT exclude."
    fi
    ;;
  convergence-*.md)
    # B5: requires a mechanism-map present; ruled-out ledger; no unresolved cheap discriminator; grain.
    HN=$(printf '%s' "$BASENAME" | sed -E 's/^convergence-(.*)\.md$/\1/')
    MISS=""
    ls "$ROOT/mechanism-map-"*.md >/dev/null 2>&1 || MISS="$MISS mechanism-map-<candidate>.md(B3-must-precede-B5)"
    printf '%s' "$CONTENT" | grep -qiE '^##[[:space:]]+Ruled-out ledger|ruled-out ledger' || MISS="$MISS ##-Ruled-out-ledger(every-demotion-cites-evidence)"
    # B4: no weight assigned while an askable-now / in-records discriminator is still unresolved.
    UNRES=$(printf '%s' "$CONTENT" | grep -niE '(askable-now|in-records)' 2>/dev/null | grep -iE 'unresolved|pending|TODO|not yet (asked|read)' || true)
    [ -z "$UNRES" ] || MISS="$MISS unresolved-askable/in-records-discriminator(B4-resolve-before-weighting)[$(printf '%s' "$UNRES" | head -1 | cut -c1-60)]"
    if [ -n "$MISS" ]; then
        deny "B5 gate (Step 5.12): convergence-$HN.md blocked until the simulation/convergence artifact is well-formed. MISSING:$MISS . Per SKILL.md B5: a per-candidate mechanism-map must exist; a '## Ruled-out ledger' must list every demoted candidate WITH the specific evidence that demoted it (every rank-change cites a constraint/observation); and per B4 no candidate may carry an unresolved 'askable-now' or 'in-records' discriminator (resolve those by asking the person or reading the record BEFORE weighting, never by scheduling a test)."
    fi
    grain_check "$CONTENT" "B5 convergence"
    ;;
esac

# Check 1 — tier marker without [src:] / [ledger:] in same sentence.
# Exemptions:
#   - tier-range mentions (T1-T5, T0-T5, T1 through T5, T1 to T5)
#   - markdown table rows (lines starting with |)
#   - markdown bullet lines that are documentation, not claims
#     (a line whose only tier-marker context is "tier:" or "T1-T5" range syntax)
#   - inline code spans (`T1`) and fenced code blocks
#   - sentences explicitly marked verification: pending OR orchestrator-memory only
VIOLATION=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re
text = sys.stdin.read()

# Strip fenced code blocks first
text = re.sub(r'\`\`\`.*?\`\`\`', '', text, flags=re.DOTALL)

# Strip backtick code spans
text = re.sub(r'\`[^\`]*\`', '', text)

# Strip tier-range mentions before sentence checking (treat T1-T5, T0-T5 as not-a-claim)
text = re.sub(r'\bT[0-5]\s*[-–—]\s*T[0-5]\b', '', text)
text = re.sub(r'\bT[0-5]\s+(through|to)\s+T[0-5]\b', '', text, flags=re.I)
# Strip trial/wave/round/step codes that collide with evidence-tier tokens
# (e.g. 'trial T2', 'wave T1', 'T2/T3' code lists) — these are NOT evidence tiers.
text = re.sub(r'\bT[0-5](?:\s*/\s*T[0-5])+\b', '', text)
text = re.sub(r'\b(?:trial|trials|wave|round|step|arm)\s+T[0-5]\b', '', text, flags=re.I)

# Now split into sentences. Also treat newlines as sentence boundaries
# (multi-line bulleted lists are not one sentence).
# Join soft-wrapped continuation lines within a markdown block, so a hard-wrapped
# sentence (its tier marker and its [src:] on different physical lines) is treated as
# ONE sentence. A newline only starts a new unit when the next line begins a new block
# (blank, bullet, heading, table row, blockquote, or numbered item) — preserving the
# original anti-borrow protection between separate bullets.
_lines = text.split('\n')
_joined = []
for _ln in _lines:
    _s = _ln.lstrip()
    _is_block = (_s == '' or (_s[:1] in '-*#|>') or bool(re.match(r'\d+[.)]\s', _s)))
    if _joined and not _is_block and _joined[-1].strip() != '':
        _joined[-1] = _joined[-1].rstrip() + ' ' + _s
    else:
        _joined.append(_ln)
text = '\n'.join(_joined)
sentences = re.split(r'(?<=[.!?])\s+|\n', text)

for s in sentences:
    s = s.strip()
    if not s:
        continue
    # Skip markdown table rows (they're structural, not claims)
    if s.startswith('|'):
        continue
    # Skip table separator lines
    if re.match(r'^[\|\s\-:]+$', s):
        continue
    # Skip lines that are pure field-definition documentation
    # (start with '- \`fieldname:\`' style)
    if re.match(r'^[-*]\s+\`[a-z_-]+:\`', s, re.I):
        continue
    # Skip lines whose only T[0-5] context is the literal 'tier: T?' label
    # without an actual claim (e.g. 'tier: T3')
    # Only check sentences that actually have T[0-5] as a word
    if not re.search(r'\bT[0-5]\b', s):
        continue
    # Sentence has a tier marker — check for source citation
    if (re.search(r'\[src:\s*[^\]]+\]', s)
            or re.search(r'\[ledger:\s*[^\]]+\]', s)
            or re.search(r'verification:\s*pending', s, re.I)
            or re.search(r'orchestrator-memory only', s, re.I)):
        continue
    # Allow tier mentions in section headers (start with #)
    if s.startswith('#'):
        continue
    # Allow when tier is being defined (e.g., 'T1 = established', 'T1 means', 'T1 candidate is one that')
    if re.search(r'\bT[0-5]\s*[=:]\s*\w', s) and not re.search(r'\bT[0-5]\b.*\b(candidate|claim|tier)\b.*\bis\b', s, re.I):
        continue
    print(s[:300])
    sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
    deny "Tier marker (T0-T5) appears in a sentence without [src: ...] or [ledger: ...] in the same sentence. Rule: investigate-health SKILL.md register / source-of-truth fidelity ladder. Every load-bearing tier claim cites a specific source by ID, OR is downgraded to T3 with verification: pending, OR is marked orchestrator-memory only. First violating sentence: $VIOLATION. To proceed: add [src: S##] matching a file you have Read this session, OR add [ledger: <quote-id>] from a /research output, OR downgrade the tier and add verification: pending."
}

# Check 7 — temporal / sequence / correlation claims need a source + DATE (Dv).
# Applies to synthesis files (NOT offering.md — that is gated semantically by the
# veracity-auditor). Fires only on explicit correlation connectives, to keep false
# positives low; the fabricated-correlation failure is "best while X was highest"
# with two undated facts lined up.
case "$BASENAME" in
    working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md)
        TVIOL=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re
text = sys.stdin.read()
text = re.sub(r'\`\`\`.*?\`\`\`', '', text, flags=re.DOTALL)
text = re.sub(r'\`[^\`]*\`', '', text)
sentences = re.split(r'(?<=[.!?])\s+|\n', text)
CONN1 = re.compile(r'\b(coincided with|coincides with|correlat(?:ed|es|ion) with|tracks with|tracked with|rose after|fell after|rose when|fell when|improved when|worsened when|peaked when|peaked while)\b', re.I)
CONN2 = re.compile(r'\b(?:best|worst|highest|lowest)\b[^.!?]*\bwhile\b[^.!?]*\b(?:highest|lowest|peak|peaked|elevated|raised|load|most|greatest|maximal)\b', re.I)
DATE = re.compile(r'\b(?:19|20)\d{2}\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', re.I)
CITE = re.compile(r'\[src:\s*[^\]]+\]|\[ledger:\s*[^\]]+\]')
for s in sentences:
    s = s.strip()
    if not s or s.startswith('|') or s.startswith('#'):
        continue
    if re.match(r'^[\|\s\-:]+\$', s):
        continue
    if CONN1.search(s) or CONN2.search(s):
        if not (DATE.search(s) and CITE.search(s)):
            print(s[:300])
            sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
            deny "Temporal/sequence/correlation claim without a source + date citation (Dv, SKILL.md register 'Veracity'). A sentence asserting two things co-vary or follow each other over time (coincided with / correlated with / tracks with / rose-after / improved-when / best-while-X-highest) must carry BOTH a date (year, month, or dd/mm) AND a [src: ...] / [ledger: ...] citation in the same sentence, so both endpoints are dated and re-derivable. This is the fabricated-correlation failure designed out. First violating sentence: $TVIOL. To proceed: add the dated source for both endpoints, or write 'timing unknown' instead of the asserted relationship."
        }
        ;;
esac

# Check 2 — [src: ...] references match session-read-log
UNREAD=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re, os
text = sys.stdin.read()
state_dir = os.environ.get('INVESTIGATE_STATE_DIR', '')
read_paths = set()
for _d in (state_dir, os.environ.get('INVESTIGATE_RUN_STATE_DIR','')):
    if not _d:
        continue
    _rl = os.path.join(_d, 'read-log')
    if os.path.exists(_rl):
        with open(_rl) as f:
            for line in f:
                p = line.strip()
                if p:
                    read_paths.add(p)
                    read_paths.add(os.path.basename(p))
for m in re.finditer(r'\[src:\s*([^,\]]+)', text):
    ref = m.group(1).strip()
    refname = os.path.basename(ref)
    if re.match(r'^S\d+$', ref):
        continue
    if ref not in read_paths and refname not in read_paths:
        print(ref)
        sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
    deny "Source reference [src: $UNREAD] does not match any file Read in this session. Rule: investigate-health SKILL.md register / source-of-truth fidelity ladder. To proceed: Read the referenced source file first, then retry. S## subject-pack IDs (e.g. [src: S02]) are accepted without read-log check."
}


# Check 3 (Round 5) — offering.md label-pairing (fixed: external python).
LABEL_PAIRING_CHECK=1
if [ "$BASENAME" = "offering.md" ]; then
    TOKENS_FILE="$HOME/.claude/skills/investigate-health/references/label-tokens.md"
    PYHELP="$HOME/.claude/hooks/lib/investigate-label-pairing.py"
    if [ -f "$TOKENS_FILE" ] && [ -f "$PYHELP" ]; then
        VIOLATION=$(printf '%s' "$CONTENT" | python3 "$PYHELP" "$TOKENS_FILE" 2>/dev/null) || {
            deny "Diagnosis label appears in offering.md without process description in the same paragraph. Rule: investigate-health SKILL.md Step 2 (Three-layer label rule). At the offering layer, every label must be paired with a process word (meaning / pathway / process / mediator / mechanism / etc.) in the same paragraph. Offending: $VIOLATION"
        }
    fi
fi

# Check 4 — gated Writes need audit-council tokens
case "$BASENAME" in
    offering.md)
        if ! investigate_has_audit_token_anchored "$SESSION" "offering" "$FILE_PATH"; then
            deny "Write to offering.md requires an audit-council token. The finish-line audit-council must pass before the person-facing offering is written. Run audit-council-completion.sh <session> offering <claim-id> AND audit-council-completion.sh <session> finish-line <claim-id> after audit dispatch."
        fi
        # New B8 council auditors — each must pass and issue its token before the offer ships.
        AUDIT_MISSING=""
        for g in decomposition structure register substance; do
            investigate_has_audit_token_anchored "$SESSION" "$g" "$FILE_PATH" || AUDIT_MISSING="$AUDIT_MISSING $g"
        done
        if [ -n "$AUDIT_MISSING" ]; then
            deny "Write to offering.md requires the four B8 council auditors to PASS first. MISSING tokens:$AUDIT_MISSING . Dispatch each auditor (INVESTIGATE-ROLE: investigate-audit-<role>, templates in references/council/), aggregate per references/council/aggregation-rule.md, and on a confident PASS run: audit-council-completion.sh <session> <role> <claim-id> for each of decomposition (grain), structure (7-section completeness), register (non-diagnosis), substance (every actionable item carries the full B6 record). A FAIL bounces the artifact to the owning step before the offer is written."
        fi
        ;;
esac

# Check 5 — register lint (high-precision deny; subtle cases caught by council + eval)
REGISTER_DENY='\b(fixable|will resolve|will fix|solves it)\b|\byou (should|must|need to)\b|the (actual|real) (finding|cause|driver|issue)\b|PROVES? at n=1'
REG_HITS=$(printf '%s' "$CONTENT" | grep -niE "$REGISTER_DENY" 2>/dev/null || true)
if [ -n "$REG_HITS" ]; then
    deny "Register violation (SKILL.md Register vocabulary): advisory / outcome-promise / certainty / fresh-diagnosis phrasing. Rephrase probabilistically (possible / candidate / worth discussing); report recorded diagnoses as 'your records note X', not fresh assertions; high-consequence flags = information clinicians act on, never 'before you take X'. Offending: $REG_HITS"
fi

# Check 6 — "diagnosis" only when attributing to a practitioner (attribution-pairing)
DIAGHELP="$HOME/.claude/hooks/lib/investigate-diagnosis-attribution.py"
if [ -f "$DIAGHELP" ]; then
    DVIOL=$(printf '%s' "$CONTENT" | python3 "$DIAGHELP" 2>/dev/null) || deny "Register: the word diagnosis must not appear in the tool's own voice (not even 'the diagnosis is uncertain'). The tool speaks in processes, patterns, and candidate causes. The word diagnosis is allowed ONLY when reporting what a practitioner recorded (e.g. 'her records note a PCOS diagnosis', 'diagnosed with X by her GP'). Reframe to process/possibility language. Offending sentence: $DVIOL"
fi

bash "$LOGGER" "investigate-health-write-check" "$BASENAME" "session=$SESSION" "allow" 2>/dev/null || true
exit 0
