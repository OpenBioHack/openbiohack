### Step 3 — Build (blind upstream mechanism graphs)

For every process from Step 2, map the **upstream causal graph** — what causes,
contributes to, or mediates it. This is done by dispatched sub-agents, **one per process,
each working blind**: a builder receives only its single assigned mechanism — no other
findings, no symptoms, no treatment history, no memory, no knowledge of the other builders
or of why the mechanism was chosen. Blind generation keeps each graph an unbiased map of
the mechanism's real causal neighbourhood; patient-matching happens later (Step 4), cleanly
separated. Send all dispatches in one message (parallel, `subagent_type: general-purpose`);
each agent's output file `<root>/graphs/builder-<process-slug>.md` is the deliverable.

Each builder is dispatched as the blind builder. (The register, flat-context, and
cross-subject-memory guards are injected by the driver via `references/register.md`; the
blindness-reinforcement and flat-context instructions specific to this role are in the
builder prompt below.)

The dispatch is neutral (see the dispatch-neutrality rule below): name no candidate, no
condition, no expected answer. The builder prompt — verbatim, no examples, nothing
case-specific:

```
You are given one biological mechanism. Your only task is to trace its UPSTREAM causal
chain — what causes, contributes to, or mediates it — and map it as a graph. Reason from
established physiology and biochemistry. You are working in isolation: you do not know why
this mechanism was chosen, what else is being traced, or what will be done with your
output. Do not infer any of that. Trace this one mechanism.

ASSIGNED MECHANISM: {MECHANISM}

EXPANSION RULE. Start from the assigned mechanism. At every node ask: what causes,
contributes to, or mediates it? Each answer is a branch, followed upstream — a node has
many contributors, so branching is the default, not an exception to a line. Recurse
upstream, each contributor asked the same question, to a MAXIMUM OF FIVE LAYERS (layer 1 =
its direct causes; layer 5 = five steps upstream). Width is unbounded; depth stops at five.

RESOLUTION REQUIREMENT. Every node names a specific, addressable biological entity — a
named molecule, cell type, receptor, transporter, enzyme, tissue compartment, or
measurable marker. A word that names a broad process or state rather than a specific
entity (a category like "inflammation", or a vague mid-level abstraction like "barrier
compromise") is NOT a node; decompose it to the specific entity before continuing.

TIER EVERY LINK. Each edge carries a tier T1 (established/textbook) to T5 (speculative).
Every edge at T3 or weaker carries a one-line falsifier — an observation that would break
that specific link.

INCLUDE ALL REAL CONTRIBUTORS, not only the commonly-tested ones — and for any node that
accumulates, trace BOTH what produces it AND what clears/removes it. An obscure or
rarely-measured contributor (including a clearance route) is a valid node if the causal
link is real. Do not prune a branch because its node is seldom measured.

DO NOT DIAGNOSE. Do not name conditions, syndromes, or an overall picture. Trace only the
causal contributors to the assigned mechanism.

OUTPUT. Write the full graph to {OUTPUT_PATH} as a text adjacency list — each edge as
`source -> target: one-line mechanism [Tn]` with the falsifier appended for T3+ edges,
organised by layer. Then return ONLY a completion signal — "done" and the output path. Do
not return a node list, counts, or any summary; the graph file is the sole deliverable and
the orchestrator reads it.
```

Width is unbounded within the graph; depth stops at five layers. The real answer for a
hard case often isn't the most common one, and the blind upstream trace — following every
contributor, including obscure and rarely-tested ones, and tracing **clearance as well as
production** (a node whose story is "made several ways and poorly cleared" is invisible to
a production-only trace) — is what surfaces it without the orchestrator steering toward a
guess.

**Atypical-presentation gate (Q1-Q5) — applies to every "ruled out" entry.**
For any process that any input (memory, prior reasoning, sub-agent output)
declares ruled out, the synthesis agent walks five questions before treating
the process as out. The five-question walk is recorded in `step5-cross-check.md`
as a `ruled-out-gate-result` field on every relevant candidate.

> **Q1.** What category of rule-out is this — (a) test-falsified, (b)
> criteria-failed, (c) phenotype-mismatch, or (d) aperture-limited? (See
> register §"Rule-outs are typed, not blanket.") For (a) specifically,
> confirm the test's measurement window actually covers this candidate — if
> it does not, it is (d), not (a).
> **Q2.** If (b) or (c) — *if the process were happening in this patient but
> not meeting standard diagnostic criteria or not matching the textbook
> phenotype, what would the presentation look like in this specific patient?*
> Write the actual presentation, not the textbook one. If (d) — *what is the
> specific test or test-class whose aperture WOULD cover this candidate,* and
> is it different from the one that was negative? (If the only evidence
> against the candidate is a test that cannot see its class, the candidate is
> not weakened.)
> **Q3.** Does that atypical presentation — or, for (d), the residual the
> aperture-limited negative leaves unexplained — match any unexplained or
> under-explained observations in this case?
> **Q4.** If yes to Q3, what does the cheapest, most reversible intervention
> on this process — or, for (d), the aperture-closing test — look like?
> **Q5.** If a positive answer to Q4 would shift quality-of-life-affecting
> symptoms within weeks, OR an aperture-closing test would change what the
> person could do, the process is **re-entered as a T3 mediator candidate**
> (and, for (d), carried to Step 6 with the aperture-closing test named)
> regardless of the label rule-out. The label stays ruled out; the mechanism
> is back in play.

Failure mode: stopping after Q1 without walking Q2-Q5. Classifying a
rule-out as (b), (c), or (d) and then still treating the process as out is
the same failure as not classifying it at all — the classification only
matters if the gate walk follows.

**The guardrail — non-negotiable.** Generation is wide; admission to the working
picture is strict. A non-obvious candidate stays in the candidate set only if it
(a) explains more of the unexplained residual than the obvious set does, (b) has a named
way it could be ruled out, (c) has a way to discriminate it from siblings, and (d) is
honestly tiered. Otherwise it goes to a noted-but-parked list. This asymmetry — generate
freely, admit strictly — captures the upside of finding the real rare answer without
descending into "everything is mould and parasites."

*Output:* N mechanism graphs under `<root>/graphs/`, one per Step-2 process, each bounded
at five layers, every node a resolved entity, every edge tiered with falsifiers on T3+,
and clearance routes traced alongside production. These graphs are the input to Step 4's
inventory.

