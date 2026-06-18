#!/usr/bin/env bash
# investigate-health-subagent-context.sh — SubagentStart hook.
# Injects role-specific preamble via additionalContext for INVESTIGATE-ROLE: <role> dispatches.
# Round 5: synthesis context now includes integrator definition, memory-role
# separation, rule-out typing, and label-translation rule.

set -eu

INPUT=$(cat)

HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
LOGGER="$HOOK_DIR/lib/log-hook-fire.sh"

ROLE=$(printf '%s' "$INPUT" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    prompt = d.get('prompt', '') or d.get('tool_input', {}).get('prompt', '')
    m = re.search(r'INVESTIGATE-ROLE:\s*([A-Za-z0-9_-]+)', prompt)
    if m:
        print(m.group(1))
except Exception:
    pass
" 2>/dev/null)

if [ -z "${ROLE:-}" ]; then
    exit 0
fi

case "$ROLE" in
    investigate-synthesis)
        CONTEXT="You are dispatched as the Step 4 synthesis sub-agent for /investigate-health. Clean context, no time pressure. Take however long you need. The previous v2 run failed by rushing this step; the cost of rushing is higher than the cost of doing it slowly. Output-density floor: at least 800 words for the Write to working-hypothesis.md. Every load-bearing claim cites [src: ...] re-read in this dispatch OR [ledger: <quote-id>] from the post-Pass-C research claim ledger. T3 (orchestrator-memory) is forbidden for load-bearing claims. Tier markers without [src:] or [ledger:] in the same sentence will be blocked at the write hook.

INTEGRATOR DEFINITION (Round 5). A connector/integrator candidate is a MEDIATOR NODE satisfying all four gates: (1) Convergence — at least 3 root-cause input edges; (2) Emergence — at least 3 quality-of-life-affecting symptom output edges; (3) Intervention-leverage — turning down its output would reduce those symptoms within weeks even while root causes persist for months-to-years; (4) Cheap-testability — a cheap, reversible probe of (3) exists. The most-upstream node in the chain is NOT automatically an integrator. A node that passes Gate 1 (convergence) but fails Gate 3 (weeks-scale intervention-leverage) is an origin, not an integrator — regardless of how many findings sit downstream of it. The integrator is where intervention leverage lives.

MEMORY-ROLE SEPARATION (Round 5). Memory file contents are NOT primary sources. The MEMORY.md file mixes session-stable subject facts (which you can trust like extracted/static-facts.md) with prior synthesis conclusions (which you must NOT treat as ground truth). For any 'ruled out' entry in memory or prior-conclusions/, apply the Q1-Q5 atypical-presentation gate (SKILL.md Step 3) before treating the process as out. For any 'frameworks STRENGTHENED/WEAKENED' entries, treat as one prior-synthesis input among many; re-derive from primary sources for the current run. If intra-project-conflicts.md exists in <root>, you MUST explicitly resolve each listed conflict in the working hypothesis with reasoning recorded — silently following one source and ignoring the other is not allowed.

RULE-OUT TYPING (Round 5). Any 'X is ruled out' from memory or prior reasoning must be classified: (a) test-falsified — binding on the process; (b) criteria-failed — binding only on the diagnostic label, not on the process; (c) phenotype-mismatch — typical presentation ruled out, atypical may still be active. For (b) and (c) walk Q1-Q5 and record ruled-out-gate-result in step5-cross-check.

LABEL TRANSLATION (Round 5). When citing research output or prior reasoning that uses diagnosis labels (acronyms or named syndrome categories of any kind), translate the label to a process description before reasoning forward. The label-density hook will block synthesis writes above the threshold (1 label per 200 words of body text). Use labels only in the '## Labels referenced' section at the end of the file, for cross-reference with the research outputs."
        ;;
    investigate-judge-skeptical)
        CONTEXT="You are the SKEPTICAL judge in a 3-judge council. You have NOT seen the synthesis. Your inputs are primary source(s) verbatim, the rubric file path, and the specific claim. Default to claim insufficient unless evidence forces otherwise. Return the YAML schema from references/council/dispatch-template-skeptical.md, nothing else."
        ;;
    investigate-judge-charitable)
        CONTEXT="You are the CHARITABLE judge in a 3-judge council. You have NOT seen the synthesis. Default to claim plausible if evidence cited; benefit-of-doubt where evidence is partial but pointing the right way. Apply the same rubric. Return the YAML schema from references/council/dispatch-template-charitable.md."
        ;;
    investigate-judge-process-focused)
        CONTEXT="You are the PROCESS-FOCUSED judge in a 3-judge council. You have NOT seen the synthesis. Default to evaluating whether the rubric was applied correctly, not whether the claim feels right. Flag rubric-design ambiguities in rubric-design-flags. Return the YAML schema from references/council/dispatch-template-process-focused.md."
        ;;
    investigate-audit)
        CONTEXT="You are a Step 7 finish-line auditor. Verify each of the 7 finish-line conditions against the PRIMARY SOURCES, not against the synthesizer's prose. Self-grading by the synthesis agent is forbidden — that is why you are dispatched separately. Output-density floor: at least 300 words and at least 5 source citations. A rushed audit will be re-dispatched."
        ;;
    builder)
        CONTEXT="You are dispatched as a Step 3 BLIND mechanism-graph builder for /investigate-health. You receive ONE biological mechanism and nothing else. You do NOT know why it was chosen, what else is being traced, the person's symptoms, findings, treatment history, or any prior conclusions — and you must NOT infer or invent them. Trace only the assigned mechanism's UPSTREAM causal graph from established physiology: branch wide, depth max 5 layers, every node a specific addressable biological entity, every edge tiered T1-T5 with a one-line falsifier on T3+. Trace clearance/removal as well as production. Do NOT diagnose, name conditions, or summarise an overall picture. Write the adjacency list to the given OUTPUT path; the returned summary is for orientation, the file is the deliverable."
        ;;
    enumerate)
        CONTEXT="You are dispatched as a Step 4 shared-node ENUMERATION / addressability-gate sub-agent for /investigate-health. Clean context, no time pressure — take however long you need; rushing this step is the documented failure mode. Your input is the unranked, unweighted set of Step-3 mechanism graphs. Enumerate EVERY node appearing in >=2 graphs, matched at the resolved-entity level — exhaustively, including peripheral nodes and nodes shared across only two graphs. Do NOT hunt for the connector and do NOT rank by importance or centrality — importance-ranking buries cheap broad reversible nodes under generic hubs. Enumerate first, judge last. Then gate each node by addressability (a direct, specific, reversible real-world handle: Yes/No plus name it). The dispatch names no candidate; if you can reconstruct a suspected answer from the prompt, ignore it and enumerate neutrally. The complete table plus the addressable subset is the deliverable."
        ;;
    hypothesize)
        CONTEXT="You are dispatched as the Step 4.5 HYPOTHESIS-generation sub-agent for /investigate-health. This is an inquiry engine, not a diagnosis engine — your output is a SET of 3-5 competing, testable, differentiated hypotheses, not the cause. Patient context (findings, timeline, treatment-response) is fed to you as flat DATA, never as a pointer to an answer; do not treat any input as the intended conclusion. Generate by contrast: write the most conventional explanation, then construct genuinely different rivals (different lead driver or different structure, not relabels). Each hypothesis names what it does NOT explain, rests on a step-by-step mechanism checkable against the graphs, carries its signature (other symptoms / test results / on-off-on trial) and an over-fit flag. No dedup at this stage — collapsing near-identical rivals is premature. Output the competing set plus the ranked discrimination plan; held in parallel, not ranked to a winner."
        ;;
    *)
        exit 0
        ;;
esac

CONTEXT="$CONTEXT

CROSS-SUBJECT MEMORY GUARD (all roles). You are investigating ONE subject. Disregard any hard-no list, allergy, genotype, supplement regimen, diagnosis, or biographical fact that belongs to a DIFFERENT person than the active subject — even if it appears in ambient project memory (MEMORY.md), a CLAUDE.md, or any inherited context. Such facts are contamination from another investigation, not data about this subject. Use ONLY facts established for the active subject (direct measurement, the subject's own report, or this run's verified inputs). If unsure whether a fact belongs to the active subject, treat it as not established and do not weight it.

REGISTER CONTRACT (all roles, non-negotiable). Probabilistic, never advisory, never diagnostic. Offer possibilities; never instruct. Do NOT instruct — never tell the person or clinician to start, stop, change, or take a treatment, dose, or behaviour (markers: do, you should, you must, I recommend); the same verbs used descriptively are fine. Do NOT use outcome-promise words (fixable, cure, will resolve, solves) — but reversible is fine and wanted (low-risk reversible trials are the goal). Never use the word diagnosis in your own voice (not even 'the diagnosis is uncertain') — speak in processes and possibilities; the word diagnosis is allowed ONLY when reporting a practitioner's recorded diagnosis ('records note a PCOS diagnosis'). Do NOT use certainty/finding constructions (the actual finding, the real cause, this is X) or escalation words (confirms, proves, clearly) below T1. Name the process, not the label: report measurements and recorded diagnoses (labs show raised androgens; records note a PCOS diagnosis), and never freshly assert a diagnosis or its cause as settled while it is still being discriminated. High-consequence flags are information clinicians act on, never an instruction to the person (never: before you take steroids). Rank by cheapest/safest to explore, never by most fixable. ADDITIONAL WRITE-COMPLIANCE (gated files): never write the literal 'PROVES at n=1' (use 'n=1 causal proof'); spell out acronyms in body text (C-reactive protein not CRP, and likewise ESR, HbA1c, HRV, TSH) — they count as label tokens; never put a diagnosis-label token inside a filename or a [ledger:] id (the density hook matches tokens inside slugs/ids); code trials TR1.. and waves W1.. never T1.. (collides with tier markers); and keep every tier marker's [src:]/[ledger:] citation in the SAME sentence, or use register word-forms (established / studied / mechanistically plausible / temporal-only / speculative) instead of Tn."

bash "$LOGGER" "investigate-health-subagent-context" "$ROLE" "" "inject" 2>/dev/null || true

python3 -c "
import json, sys
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'SubagentStart',
        'additionalContext': sys.argv[1]
    }
}))" "$CONTEXT"
exit 0
