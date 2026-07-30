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
. "$HOOK_DIR/lib/investigate-parse.sh"
. "$HOOK_DIR/lib/investigate-gate-lib.sh"
. "$HOOK_DIR/lib/skill-token-lib.sh" 2>/dev/null || true
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"
# Unicode canonicalizer location (importable by the inline python content checks).
export IH_LIB="$HOOK_DIR/lib"

# L1 single rule-source: a per-file JSON manifest decides which lint checks apply. When no
# manifest exists, check_on returns true so the hardcoded check still runs (no regression).
check_on() { [ -z "${RULES:-}" ] && return 0; gate_enabled "$RULES" "$1"; }

# F6: newline-safe single-pass parse (replaces positional `sed -n '1p'..'3p'`, which a
# newline injected into file_path/cwd/session could shift to move attacker text into the
# CONTENT slot or skip a check).
ih_parse_input "$INPUT"

# Malformed input fail-closed: if the JSON could not be parsed but the RAW stdin
# plausibly targets a gated artifact, DENY rather than fall open. The gate cannot verify
# provenance/tokens on input it cannot read, so it refuses the gated write. Unrelated
# malformed input (no gated basename present) is left alone (exit 0).
if [ "$IH_PARSE_OK" != "1" ]; then
    if ih_raw_targets_gated "$INPUT"; then
        python3 -c "
import json, sys
print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':sys.argv[1]}}))" \
"Malformed hook input targeting a gated investigate-health artifact. Refusing the write (fail-closed): the gate could not parse the tool input to verify provenance and audit tokens, so it will not allow a gated write it cannot check. Re-issue the write with well-formed tool input."
    fi
    exit 0
fi

CWD="$IH_CWD"
SESSION="$IH_SESSION"
FILE_PATH="$IH_FILE_PATH"
CONTENT="$IH_CONTENT"

BASENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "")
case "$BASENAME" in
    working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md|offering.md|offering-draft.md) ;;
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

# L1: resolve this artifact's rule-source manifest (empty -> hardcoded fallback).
RULES="$(gate_rules_path "$BASENAME" 2>/dev/null || true)"

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

# STUB-ALLOWLIST: bootstrap stubs are tiny (<800 bytes) and contain explicit
# stub markers. Let them through unchecked — EXCEPT offering.md /
# offering-draft.md: a delivered offering.md is the cleanup-unlock signal
# (investigate-health-cleanup-block.sh), so no offering write may bypass the
# gates as a "stub". Bootstrap does not stub the offering, so nothing
# legitimate is lost.
CONTENT_LEN=$(printf '%s' "$CONTENT" | wc -c | tr -d ' ')
case "$BASENAME" in
    offering.md|offering-draft.md) ;;
    *)
        if [ "$CONTENT_LEN" -lt 800 ] && printf '%s' "$CONTENT" | grep -qiE '(empty stub|pending Step|in progress|_pending_|^> Empty)'; then
            bash "$LOGGER" "investigate-health-write-check" "$BASENAME" "session=$SESSION size=$CONTENT_LEN" "allow-stub" 2>/dev/null || true
            exit 0
        fi
        ;;
esac

# Unicode tripwire (targeted): a token mixing ASCII word-chars with a known Latin look-alike
# homoglyph (Cyrillic/Greek) is the signature of an evasion attempt. Legitimate accented prose
# (cafe, naive, Muller) and pure non-Latin words do NOT trigger it. The content checks below
# additionally run on the FOLDED match copy, so a homoglyph that the tripwire misses is still
# neutralized — this is defense in depth, not the only line.
MIXED_TOK=$(printf '%s' "$CONTENT" | python3 -c "
import sys, os
sys.path.insert(0, os.environ.get('IH_LIB',''))
try:
    from investigate_canon import mixed_script_token
    print(mixed_script_token(sys.stdin.read()))
except Exception:
    print('')
" 2>/dev/null)
if [ -n "$MIXED_TOK" ]; then
    deny "Mixed-script token detected: '$MIXED_TOK' mixes ASCII letters with a Latin look-alike homoglyph (Cyrillic/Greek). This is the signature of an attempt to smuggle a sensitive term (a tier marker, a register-banned phrase, a diagnosis label) past the content checks by swapping a look-alike letter. Rewrite the term in plain ASCII. Legitimate accented prose (cafe, Muller, naive) does NOT trigger this."
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
# Aggregate-as-actor detection = UNION of three vocabularies. The grain pre-check is a cheap lexical
# tripwire; the B8 decomposition auditor is the semantic backstop for phrasings the vocabulary misses
# (a regex cannot parse grammar, so some vocabulary is unavoidable — the fix is BREADTH, not removal).
#   (1) the ORIGINAL microbiome / treatment-family patterns — kept verbatim (still useful).
AGG_MICRO = (r"\bthe\s+(?:drug|antibiotic|antimicrobial|treatment|kill|supplement)[- ]?"
             r"(?:set|family|class|group|regimen|protocol|stack)\b"
             r"|\bthe\s+(?:consortium|community|biofilm community)\b")
#   (2) microbiome-SPECIALISED aggregate heads (expanded) — a collection of organisms as one actor.
AGG_MICRO_HEADS = (r"\bthe\s+(?:[A-Za-z][\w-]*\s+)?"
                   r"(?:flora|microflora|microbiota|microbiome|biofilm|genus|genera|phyl(?:um|a)|taxa|strains)\b")
#   (3) DOMAIN-NEUTRAL collective-noun heads — so the check also fires in cardiac / immune / genetic /
#       any other domain. Excludes mechanism-singletons (system/pathway/cascade/axis/complex) which
#       name ONE entity, not a collection of independently-acting members.
COLL = (r"famil(?:y|ies)|class(?:es)?|group(?:s)?|set(?:s)?|cluster(?:s)?|network(?:s)?|panel(?:s)?"
        r"|consorti(?:um|a)|communit(?:y|ies)|population(?:s)?|cohort(?:s)?|ensembles?"
        r"|categor(?:y|ies)|collections?|batch(?:es)?|arrays?|suites?|stacks?|regimens?|protocols?|series")
AGG_GENERIC = r"\bthe\s+(?:[A-Za-z][\w-]*\s+){0,2}(?:" + COLL + r")\b"
AGG = "(?:" + AGG_MICRO + "|" + AGG_MICRO_HEADS + "|" + AGG_GENERIC + ")"
# actions that make an aggregate an ACTOR — generic + microbiome-specialised (ferment / metabolise /
# colonise / deconjugate / overgrow / bloom / translocate).
ACTION = (r"\b(?:survives?|resists?|confers?|feeds?|shelters?|protects?|persists?|rebounds?|clears?"
          r"|outcompetes?|causes?|drives?|produces?|mediates?|triggers?|generates?|sustains?"
          r"|ferments?|metaboli[sz]es?|coloni[sz]es?|deconjugates?|degrades?|overgrows?|blooms?|translocates?)\b")
UNSPEC = r"\bconfers\s+resistance\b(?!\s+(?:to|against)\b)|\bis\s+resistant\b(?!\s+(?:to|against)\b)|\bfeeds\s+it\b|\bshelters\s+it\b"
DECOMP = r"→|->|\bnamely\b|\bspecifically\b|\[grain:|\bmembers?\b|\bspecies\b|\beach\s+(?:of|member)\b|\b(?:i\.e\.|e\.g\.)"
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
if check_on tier_src_pairing; then
VIOLATION=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re
import os
sys.path.insert(0, os.environ.get('IH_LIB',''))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s): return s
# Unicode-canonicalize the MATCH COPY so homoglyph/zero-width/fullwidth/combining/RTL
# evasions of the tier regex fold to their ASCII form before matching.
text = match_copy(sys.stdin.read())

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
fi

# Check 7 — temporal / sequence / correlation claims need a source + DATE (Dv).
# Applies to synthesis files (NOT offering.md — that is gated semantically by the
# veracity-auditor). Fires only on explicit correlation connectives, to keep false
# positives low; the fabricated-correlation failure is "best while X was highest"
# with two undated facts lined up.
if check_on temporal_date_cite; then
case "$BASENAME" in
    working-hypothesis.md|step5-cross-check.md|hypothesis-set.md|step6-prioritize.md|offering-draft.md)
        TVIOL=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re, os
sys.path.insert(0, os.environ.get('IH_LIB',''))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s): return s
text = match_copy(sys.stdin.read())
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
    if re.match(r'^[\|\s\-:]+$', s):
        continue
    # ReDoS guard: CONN2 has two unbounded [^.!?]* segments. Only evaluate it when the
    # cheap 'while' substring is present and the sentence length is bounded, so a
    # while-less or pathologically long line never drives regex backtracking.
    hit = bool(CONN1.search(s))
    if not hit and 'while' in s.lower() and len(s) <= 2000:
        hit = bool(CONN2.search(s))
    if hit:
        if not (DATE.search(s) and CITE.search(s)):
            print(s[:300])
            sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
            deny "Temporal/sequence/correlation claim without a source + date citation (Dv, SKILL.md register 'Veracity'). A sentence asserting two things co-vary or follow each other over time (coincided with / correlated with / tracks with / rose-after / improved-when / best-while-X-highest) must carry BOTH a date (year, month, or dd/mm) AND a [src: ...] / [ledger: ...] citation in the same sentence, so both endpoints are dated and re-derivable. This is the fabricated-correlation failure designed out. First violating sentence: $TVIOL. To proceed: add the dated source for both endpoints, or write 'timing unknown' instead of the asserted relationship."
        }
        ;;
esac
fi

# Check 2 — [src: ...] references match session-read-log
if check_on src_in_readlog; then
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
fi


# Check 3 (Round 5) — offering.md label-pairing (external python).
# M4 fix: the helper is resolved from $HOOK_DIR/lib (where the hook sources its other libs),
# NOT a separate hardcoded $HOME path, and a MISSING helper on a gated offering write now
# DENIES (fail-closed) instead of silently skipping the check.
if [ "$BASENAME" = "offering.md" ] && check_on label_pairing; then
    TOKENS_FILE="$HOME/.claude/skills/investigate-health/references/label-tokens.md"
    PYHELP="$HOOK_DIR/lib/investigate-label-pairing.py"
    if [ ! -f "$PYHELP" ]; then
        deny "offering.md blocked (fail-closed): the label-pairing helper is missing at $PYHELP, so diagnosis-label-pairing cannot be enforced. Restore lib/investigate-label-pairing.py before writing the offer."
    fi
    if [ -f "$TOKENS_FILE" ]; then
        VIOLATION=$(printf '%s' "$CONTENT" | python3 "$PYHELP" "$TOKENS_FILE" 2>/dev/null) || {
            deny "Diagnosis label appears in offering.md without process description in the same paragraph. Rule: investigate-health SKILL.md Step 2 (Three-layer label rule). At the offering layer, every label must be paired with a process word (meaning / pathway / process / mediator / mechanism / etc.) in the same paragraph. Offending: $VIOLATION"
        }
    fi
fi

# Check 4 — gated Writes need audit-council tokens
case "$BASENAME" in
    offering.md)
        # F2: token gate now VERIFIES integrity, not just file existence — a token opens
        # the gate only if it is non-empty AND a valid HMAC AND bound to this gate name
        # AND within the 2400s (40-min) audit window. Empty/forged/wrong-gate/stale tokens
        # are rejected.
        if ! investigate_verify_audit_token_anchored "$SESSION" "offering" "$FILE_PATH"; then
            deny "Write to offering.md requires a VALID audit-council token (offering gate). The finish-line audit-council must pass before the person-facing offering is written, and the token must be a non-empty, HMAC-valid, gate-bound token issued within the last 40 minutes (empty/forged/wrong-gate/expired tokens are rejected). Run audit-council-completion.sh <session> offering <claim-id> AND audit-council-completion.sh <session> finish-line <claim-id> after audit dispatch, then write within the window."
        fi
        # New B8 council auditors — each must pass and issue its (verified) token before the offer ships.
        AUDIT_MISSING=""
        for g in decomposition structure register substance; do
            investigate_verify_audit_token_anchored "$SESSION" "$g" "$FILE_PATH" || AUDIT_MISSING="$AUDIT_MISSING $g"
        done
        if [ -n "$AUDIT_MISSING" ]; then
            deny "Write to offering.md requires the four B8 council auditors to PASS first, each with a VALID (non-empty, HMAC-valid, gate-bound, within-40-min) token. MISSING/invalid tokens:$AUDIT_MISSING . Dispatch each auditor (INVESTIGATE-ROLE: investigate-audit-<role>, templates in references/council/), aggregate per references/council/aggregation-rule.md, and on a confident PASS run: audit-council-completion.sh <session> <role> <claim-id> for each of decomposition (grain), structure (7-section completeness), register (non-diagnosis), substance (every actionable item carries the full B6 record). A FAIL bounces the artifact to the owning step before the offer is written."
        fi
        ;;
esac

# Check 5 — register lint. Whitespace-tolerant: the match copy collapses every run of
# whitespace (incl. newlines) to one space, so 'you  should' (double space) and a
# line-split 'you\nshould' are caught like 'you should'. Closed gaps: 'this resolves',
# 'you'll want to' / 'you want to', 'the genuine driver'.
if check_on register_lint; then
REG_HITS=$(printf '%s' "$CONTENT" | python3 -c "
import sys, re, os
sys.path.insert(0, os.environ.get('IH_LIB',''))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s): return s
text = match_copy(sys.stdin.read())
text = re.sub(r'\`\`\`.*?\`\`\`', '', text, flags=re.DOTALL)
text = re.sub(r'\`[^\`]*\`', '', text)
mc = re.sub(r'\s+', ' ', text)
PAT = re.compile(
    r'\b(?:fixable|will resolve|will fix|solves it|this resolves)\b'
    r'|\byou(?:\x27ll)? (?:should|must|need to|want to)\b'
    r'|\bthe (?:actual|real|genuine) (?:finding|cause|driver|issue)\b'
    r'|PROVES? at n=1', re.I)
m = PAT.search(mc)
if m:
    s = max(0, m.start()-40); e = min(len(mc), m.end()+40)
    print(mc[s:e].strip())
    sys.exit(1)
sys.exit(0)
" 2>/dev/null) || {
    deny "Register violation (SKILL.md Register vocabulary): advisory / outcome-promise / certainty / fresh-diagnosis phrasing. Rephrase probabilistically (possible / candidate / worth discussing); report recorded diagnoses as 'your records note X', not fresh assertions; high-consequence flags = information clinicians act on, never 'before you take X'. ('reversible' is fine.) Offending: $REG_HITS"
}
fi

# Check 6 — "diagnosis" only when attributing to a practitioner (attribution-pairing)
# M4 fix: resolve the helper from $HOOK_DIR/lib; a missing helper on a gated offering/draft
# write DENIES (fail-closed) rather than silently skipping.
if check_on diagnosis_attribution; then
DIAGHELP="$HOOK_DIR/lib/investigate-diagnosis-attribution.py"
if [ ! -f "$DIAGHELP" ]; then
    case "$BASENAME" in
        offering.md|offering-draft.md)
            deny "${BASENAME} blocked (fail-closed): the diagnosis-attribution helper is missing at $DIAGHELP, so diagnosis-in-own-voice cannot be enforced. Restore lib/investigate-diagnosis-attribution.py before writing." ;;
    esac
fi
if [ -f "$DIAGHELP" ]; then
    DVIOL=$(printf '%s' "$CONTENT" | python3 "$DIAGHELP" 2>/dev/null) || deny "Register: the word diagnosis must not appear in the tool's own voice (not even 'the diagnosis is uncertain'). The tool speaks in processes, patterns, and candidate causes. The word diagnosis is allowed ONLY when reporting what a practitioner recorded (e.g. 'her records note a PCOS diagnosis', 'diagnosed with X by her GP'). Reframe to process/possibility language. Offending sentence: $DVIOL"
fi
fi

# Layer 2 (memory-interpretation quarantine) — grounding provenance-anchor gate.
# Applies to the hypothesis candidate docs only. Each ### H block must carry >=1 admissible
# anchor (a non-DERIVED [src:], or a **[STATED]**/[self-report]/[experiential:] line); a block
# grounded SOLELY on a memory/curated INTERPRETATION or on index-flagged DERIVED/CURATED sources
# is inadmissible. Condition-agnostic: keys on the extractor's tags + index.md provenance-class
# strings, never on a filename. Fail-closed: a missing helper DENIES; a helper error -> DENY.
if check_on grounding_primary_anchor; then
case "$BASENAME" in
    hypothesis-set.md|working-hypothesis.md)
        GHELP="$HOOK_DIR/lib/investigate-grounding-anchor.py"
        if [ ! -f "$GHELP" ]; then
            deny "${BASENAME} blocked (fail-closed): the grounding-anchor helper is missing at $GHELP, so Layer-2 grounding provenance cannot be enforced. Restore lib/investigate-grounding-anchor.py before writing the hypothesis candidates."
        fi
        GINDEX="$ROOT/extracted/index.md"
        GVIOL=$(printf '%s' "$CONTENT" | python3 "$GHELP" "$GINDEX" 2>/dev/null) || {
            deny "Layer-2 grounding gate: hypothesis [$GVIOL] grounds SOLELY on a memory/curated INTERPRETATION or on index-flagged DERIVED/CURATED sources, with no admissible primary anchor. A candidate cannot be grounded on interpretation (a prior AI's, a clinician's inference, or the subject's own gloss) or on lower-authority derived sources alone. Add at least one admissible anchor to the block: a [src: F] whose F is a PRIMARY/raw source (or a pipeline-internal compiled/research view), OR a first-person **[STATED]** / [self-report] / [experiential: <verbatim lived report>] line. Re-derive the claim from primary data; the interpretation may point to WHERE to look but may not itself be the ground."
        }
        ;;
esac
fi

bash "$LOGGER" "investigate-health-write-check" "$BASENAME" "session=$SESSION" "allow" 2>/dev/null || true
exit 0
