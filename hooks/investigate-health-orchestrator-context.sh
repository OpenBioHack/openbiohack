#!/usr/bin/env bash
# investigate-health-orchestrator-context.sh — UserPromptSubmit hook.
# While an investigate-health run is ACTIVE for this session (its state read-log exists),
# inject the gated-write compliance checklist into the main loop so the orchestrator's INLINE
# synthesis (which gets no subagent-context injection) writes gated files compliant first time.
# Instant no-op for every non-investigate session.
set -eu
ONESHOT=0
INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
. "$HOOK_DIR/lib/investigate-state.sh" 2>/dev/null || exit 0
. "$HOOK_DIR/lib/investigate-parse.sh" 2>/dev/null || exit 0
# Portable scoping: no hardcoded project path — active iff a run marker exists
# at/under cwd (session-independent, marker walk-up + registry).
ih_parse_input "$INPUT"
[ "$IH_PARSE_OK" = "1" ] || exit 0
__ih_cwd="$IH_CWD"
SESSION="$IH_SESSION"
[ -n "$SESSION" ] || exit 0
STATE_DIR="$(investigate_state_dir "$SESSION")"
investigate_cwd_has_active_run "$__ih_cwd" || exit 0
if [ "$ONESHOT" = "1" ]; then
    [ -e "$STATE_DIR/orch-context-injected" ] && exit 0
    touch "$STATE_DIR/orch-context-injected" 2>/dev/null || true
fi

# Resolve the run root for the resume nudge: marker walk-up from cwd, else the
# registry (root under cwd / cwd under root), else a bounded down-search —
# the same three lanes as investigate_cwd_has_active_run.
RUN_ROOT="$(investigate_find_active_root "$__ih_cwd" 2>/dev/null || true)"
if [ -z "$RUN_ROOT" ] && [ -d "${INVESTIGATE_REGISTRY:-${INVESTIGATE_STATE_BASE:-/tmp/claude}/active-roots}" ]; then
    for __rf in "${INVESTIGATE_REGISTRY:-${INVESTIGATE_STATE_BASE:-/tmp/claude}/active-roots}"/*; do
        [ -f "$__rf" ] || continue
        __rr="$(cat "$__rf" 2>/dev/null)"; [ -n "$__rr" ] || continue
        [ -f "$__rr/.investigate-active" ] || continue
        case "$__ih_cwd/" in "$__rr"/*) RUN_ROOT="$__rr"; break ;; esac
        case "$__rr/" in "$__ih_cwd"/*) RUN_ROOT="$__rr"; break ;; esac
        [ "$__ih_cwd" = "$__rr" ] && { RUN_ROOT="$__rr"; break; }
    done
fi
if [ -z "$RUN_ROOT" ]; then
    __m="$(find "$__ih_cwd" -maxdepth 3 -name .investigate-active -type f 2>/dev/null | head -n1)"
    [ -n "$__m" ] && RUN_ROOT="$(dirname "$__m")"
fi
[ -n "$RUN_ROOT" ] || RUN_ROOT="$__ih_cwd"

# Fixed compaction-resume nudge (no parser, no format contract — the model
# re-reads the skill and the decision log itself). Kept FIRST so a
# fresh-context model sees it before the compliance detail.
RESUME="RESUME CONTEXT — an investigate-health run is ACTIVE at $RUN_ROOT. If this context is fresh (post-compaction or a new session), do not improvise from memory: re-read the investigate-health SKILL.md and $RUN_ROOT/decision-log.md, then resume from the last logged step. Do NOT rewrite $RUN_ROOT/.investigate-active — it is kernel-locked (chflags uchg); a rewrite fails with EPERM and is never needed. // "

CTX="INVESTIGATE-HEALTH — gated-write compliance (you are the orchestrator; inline synthesis gets no agent injection, so apply this yourself). Before writing working-hypothesis.md / step5-cross-check.md / hypothesis-set.md / step6-prioritize.md / offering.md: (1) every tier marker T0-T5 needs [src:]/[ledger:] in the SAME sentence — or write tiers as word-forms (established / studied / mechanistically plausible / temporal-only / speculative) so no Tn token exists. (2) code trials TR1.. and waves W1.. — never T1.. (collides with the tier regex). (3) a [src: file] must be a file you READ this session (not one you only wrote); use [ledger: id] for research you have summaries of. (4) keep diagnosis-label tokens <=1 per 200 words, all in a trailing '## Labels referenced' section (must be LAST); spell out acronyms in body (C-reactive protein not CRP; likewise ESR, HbA1c, HRV, TSH); never put a label token inside a slug or [ledger:] id. (5) offering.md: pair every diagnosis label with a plain-language process in the SAME paragraph. (6 lexical, Check 5) NEVER write: 'fixable' / 'will fix' / 'will resolve' / 'solves it'; 'you should/must/need to'; 'the actual/real cause/finding/driver'; 'PROVES at n=1' (use 'n=1 causal proof') — but 'reversible' is fine and wanted. (6b, Check 6) use 'diagnosis'/'diagnoses' ONLY in a sentence that attributes it to a record/clinician ('records note a PCOS diagnosis'); for tool-voice/meta uses write 'diagnostic' (does not match) or rephrase. (6c, SEMANTIC — audit-council, NOT a keyword) phrase every high-consequence flag as information a clinician acts on ('a clinician would want it excluded prior to any steroid course'), never 'before you take X'; offer possibilities, never instruct. (7) no rm/mv/delete under the subject root before the finish-line; finish line is now 7 items (item 7 = register, council-verified). Full reference: SKILL.md 'Gated-write compliance quick-reference'. (3b) CITATION FORMAT: a [src: file, sub-id] sub-id follows a COMMA not a space (the hook reads the filename up to the first comma/]) — '[src: working-truth.md, A-2]' not '[src: working-truth.md A-2]'; and only cite files you READ this session. (3c) READ-ATTESTATION: step6-prioritize.md and offering.md are blocked until every research/*.md + graphs/*.md in the run root has been Read this session. (3d) DELEGATION DEFAULT: prefer dispatching the owning role to write each gated file; inline synthesis is memory-contaminated AND gets none of this injected — re-derive from primary sources, do not reproduce remembered conclusions. (8) CONVERSATIONAL REGISTER — applies to your CHAT to the person, not only files: think with the nuance of a Keegan level-5 thinker; prioritise with reasons where the evidence ranks, and say what demoted the rest, but never state anything as certain and never present a single candidate as the settled answer — no 'biggest single thread / the main driver / the strongest frame / what is really going on', and no 'likely explains / reads as / accounts for / does not actually / did not touch' as a verdict. Carry the tier into the sentence and hedge ('it could be one of the contributors, alongside others we cannot separate yet' — not 'the symptom reads as a single mechanism'). When repeating a sub-agent claim, carry its hedge and attribute it. Synthesise the whole set holistically, not document-by-document."
python3 -c "import json,sys; print(json.dumps({'hookSpecificOutput':{'hookEventName':'UserPromptSubmit','additionalContext':sys.argv[1]}}))" "$RESUME$CTX"
exit 0
