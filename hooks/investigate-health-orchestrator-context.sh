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
SESSION=$(printf '%s' "$INPUT" | python3 -c "import sys,json
try: print(json.load(sys.stdin).get('session_id',''))
except Exception: pass" 2>/dev/null) || exit 0
[ -n "$SESSION" ] || exit 0
STATE_DIR="$(investigate_state_dir "$SESSION")"
[ -e "$STATE_DIR/investigation-active" ] || exit 0   # not an active investigate run -> no-op
if [ "$ONESHOT" = "1" ]; then
    [ -e "$STATE_DIR/orch-context-injected" ] && exit 0
    touch "$STATE_DIR/orch-context-injected" 2>/dev/null || true
fi
CTX="INVESTIGATE-HEALTH — gated-write compliance (you are the orchestrator; inline synthesis gets no agent injection, so apply this yourself). Before writing working-hypothesis.md / step5-cross-check.md / hypothesis-set.md / step6-prioritize.md / offering.md: (1) every tier marker T0-T5 needs [src:]/[ledger:] in the SAME sentence — or write tiers as word-forms (established / studied / mechanistically plausible / temporal-only / speculative) so no Tn token exists. (2) code trials TR1.. and waves W1.. — never T1.. (collides with the tier regex). (3) a [src: file] must be a file you READ this session (not one you only wrote); use [ledger: id] for research you have summaries of. (4) keep diagnosis-label tokens <=1 per 200 words, all in a trailing '## Labels referenced' section (must be LAST); spell out acronyms in body (C-reactive protein not CRP; likewise ESR, HbA1c, HRV, TSH); never put a label token inside a slug or [ledger:] id. (5) offering.md: pair every diagnosis label with a plain-language process in the SAME paragraph. (6 lexical, Check 5) NEVER write: 'fixable' / 'will fix' / 'will resolve' / 'solves it'; 'you should/must/need to'; 'the actual/real cause/finding/driver'; 'PROVES at n=1' (use 'n=1 causal proof') — but 'reversible' is fine and wanted. (6b, Check 6) use 'diagnosis'/'diagnoses' ONLY in a sentence that attributes it to a record/clinician ('records note a PCOS diagnosis'); for tool-voice/meta uses write 'diagnostic' (does not match) or rephrase. (6c, SEMANTIC — audit-council, NOT a keyword) phrase every high-consequence flag as information a clinician acts on ('a clinician would want it excluded prior to any steroid course'), never 'before you take X'; offer possibilities, never instruct. (7) no rm/mv/delete under the subject root before the finish-line; finish line is now 7 items (item 7 = register, council-verified). Full reference: SKILL.md 'Gated-write compliance quick-reference'. (8) CONVERSATIONAL REGISTER — applies to your CHAT to the person, not only files: think with the nuance of a Keegan level-5 thinker; hold possibilities in parallel and never crown a winner — no 'biggest single thread / the main driver / the strongest frame / what is really going on', and no 'likely explains / reads as / accounts for / does not actually / did not touch' as a verdict. Carry the tier into the sentence and hedge ('it could be one of the contributors, alongside others we cannot separate yet' — not 'the belching reads as upper-GI gas handling'). When repeating a sub-agent claim, carry its hedge and attribute it. Synthesise the whole set holistically, not document-by-document."
python3 -c "import json,sys; print(json.dumps({'hookSpecificOutput':{'hookEventName':'UserPromptSubmit','additionalContext':sys.argv[1]}}))" "$CTX"
exit 0
