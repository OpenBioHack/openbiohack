# Step 2a — Broad per-view generator (cause-family sweep, root-cause discipline)

Broad hypothesis generation over the compiled cross-source view(s) handed to this agent. The point of
this step is VARIETY — the widest set of genuinely-different candidate ROOT causes the material can
support. Every generator sweeps the full cause-family roster (below); the driver inlines the view
CONTENTS into the prompt (never just a path — the "lost-examples" failure must not recur).

## Prompt

```
Generate candidate ROOT CAUSES and SYSTEMIC CONTRIBUTING FACTORS of THIS PERSON'S PRESENTATION (the
problem + symptoms stated in the presentation given to you), using the material below as EVIDENCE. Read
the presentation FIRST, then read ALL of the material (one or more compiled cross-source views). You are
NOT explaining the data for its own sake — you are explaining the presentation, drawing on the data. If
the material is empty, output `EMPTY-INPUT` and stop — never invent data.

════════ THE BODY IS ONE SYSTEM — CONNECT EVERY FINDING TO THE PRESENTATION ════════
You are mapping candidate contributors to the presentation: ROOT CAUSES (the strongest — upstream drivers)
AND SYSTEMIC CONTRIBUTING FACTORS (states that modulate, amplify, slow, or feed the presentation through
the body's interconnections). Every candidate's chain must ARRIVE AT the presentation — explain it AS A
WHOLE (do NOT force convergence on one single symptom, and do not invent a "must explain symptom X or it's
invalid" rule the presentation did not state).

NO FINDING IS EXPLAINED IN ISOLATION, AND NONE IS DISCARDED. The body is entirely interconnected. When a
finding looks unrelated (an out-of-range hormone, a lone lab value), do NOT explain it for its own sake
("SHBG is high because of a set-point" — worthless), and do NOT drop it. Instead ASK: through what systemic
chain could THIS contribute to the presentation? Trace it explicitly:
   <finding / family state>  →  <physiological link>  →  <effect on a relevant system>  →  the presentation.
Only if, after genuine effort, NO plausible systemic contribution exists at all do you set it aside — the
DEFAULT and the goal is to FIND the connection, because in an interconnected system distant nodes usually
do connect.

  HOW TO TURN AN "INCIDENTAL" FINDING INTO A SYSTEMIC CONTRIBUTOR (do this, don't restate or drop):
  ✗ isolated restatement: "High SHBG reflects a constitutional set-point" — explains the hormone, not the
    person's problem. Worthless.
  ✓ systemic contribution: "A high-SHBG / altered sex-hormone-handling state could lower the free-androgen
    tone that helps maintain gut smooth-muscle motility → slower small-bowel transit / a weaker migrating
    motor complex → stasis that favours bacterial overgrowth → adds to the fermentation-driven symptoms
    the person reports." FAMILY: endocrine/regulatory. ROLE: contributing factor. Now it is a testable
    node in the web, not a restatement.

════════ WHAT A ROOT CAUSE IS (be strict — most candidates people write are NOT roots) ════════
A root cause is the most UPSTREAM node in THIS person's causal chain that passes ALL of:

 • TERMINAL-WHY (the investigator's 5-Whys). Keep asking "…and what causes THAT, in this person?"
   A node is terminal ONLY when the honest next answer LEAVES THE BODY or hits a FIXED GIVEN:
     – an external input (a food, drug, toxin, microbe, exposure),
     – an inherited / anatomical given (a gene, a structural variant, an irreversible past event), or
     – a SELF-SUSTAINING primary process that persists with no upstream driver
       (a neoplastic clone, an autoimmune loop, a fixed structural lesion).
   If the next "why" is another modifiable factor in this person, you have NOT reached the root.

 • DEPTH — the 5-Whys are MANDATORY. Every candidate's REASONING must show a why-chain of AT LEAST
   FIVE steps down to the terminal node — no candidate with fewer, no exceptions. If you think you
   reached the root in three, you stopped at a mediator: the 4th and 5th "why" are exactly what force
   you past it. If at five you are STILL on a modifiable mediator, keep going beyond five. Somewhere in
   the chain you MUST name a SPECIFIC mechanism — a named transporter, enzyme, tissue, organism, gene,
   or exposure; a chain of vague nouns is not a real chain.

 • NO-REGENERATION. If this node were removed/corrected, the effects below it would not rebuild
   themselves. A mediator fails this — remove its driver and it resolves.

 • NO CIRCULAR / RESTATEMENT "roots". A candidate that renames the missing function or the symptom as
   its own cause — "X because the X-doing part is defective/insufficient" (e.g. "malabsorption because
   the gut doesn't absorb", "fatigue because low energy production", "pain because the nerve is
   irritated") — has ZERO explanatory power and is NOT a root. Name WHY that part fails, at the level
   of a specific molecule / tissue / organism / gene / exposure, and WHEN.

 Physics framing: mediators are STATE VARIABLES that relax back once the forcing is removed; a root
 cause is the FORCING TERM (boundary condition) holding the system away from baseline. Name the
 forcing, not the state.

 MEDIATORS ARE NEVER ROOTS (held in place from upstream; cannot self-start): inflammation, dysbiosis,
 oxidative stress, insulin resistance, high/low cortisol, immune activation, "leaky gut" / intestinal
 permeability, mitochondrial dysfunction, "a hormone imbalance". "Inflammation" is always inflammation
 OF a tissue BY a trigger — naming it is naming the smoke, not the fire. For each, fan OUT to the
 cause-classes that could produce it.

════════ COVERAGE: sweep EVERY cause family ════════
For EACH family, ask "if THIS family were involved in what the material shows, what specifically could
it be?" and produce AT LEAST ONE candidate for it — MANDATORY, every family, no exceptions and no
"nothing here" line. Forcing a candidate out of every family is the entire point of this sweep: when a
family looks irrelevant is exactly when its candidate must be non-obvious — reach for the rare one.
  1.  external-exposure       — foods, additives, water, toxins / heavy metals, occupational / environmental
  2.  infective / organismal  — bacterial / viral / fungal / parasitic, overgrowth / dysbiotic organisms, post-infectious
  3.  immune-mediated         — autoimmune, allergic / hypersensitivity, mast-cell / histamine, immunodeficiency
  4.  neoplastic / proliferative — benign or malignant growths, clonal expansion, paraneoplastic
  5.  vascular / circulatory  — perfusion, ischaemia, thrombosis, congestion, vascular-autonomic
  6.  structural / anatomic   — mechanical / obstructive, anatomical variant, absorptive-surface defect, injury, degenerative
  7.  endocrine / regulatory  — hormonal axes and feedback loops, receptor / signalling
  8.  metabolic / nutritional — enzyme / cofactor defect, deficiency or excess, energy production, storage / handling
  9.  iatrogenic / treatment-caused — drugs, procedures, and their sequelae
  10. constitutional / genetic — inherited variants, congenital, connective-tissue
  11. psychological / stress / nervous-system — autonomic dysregulation, gut-brain signalling, central sensitisation, functional

════════ COUNT + DIVERSITY ════════
Produce AT LEAST 20 genuinely-distinct candidates — MANDATORY, no exceptions; the whole point of this
step is variety. The space easily supports it (11 families × obvious + rare). If you are struggling to
reach 20 you are not sweeping the families or not reaching for the rare — that is NOT a licence to pad
with restatements, trivial subdivisions, or the same root in another costume. Order the list obvious →
rare. At least ~10 % (≥2) must be genuinely RARE / long-shot. If two candidates collapse to the same
root, keep one and find another.

════════ CARD FORMAT — one per candidate, exactly like the worked example ════════
### HYP «view-slug»-«n»
CLAIM: <the candidate, one plain line — a specific mechanism / event / systemic state, never a restatement>
ROLE: root cause | contributing factor
FAMILY: <which cause family / families it comes from>
REASONING: <ROOT: the ~5-step why-chain to the terminal node; show WHERE it exits the body / hits a given;
            why it is not a mediator and not circular.
            CONTRIBUTING FACTOR: the systemic chain FROM the finding/state TO the presentation
            (finding → physiological link → effect on a system → the presentation) — ≥5 steps, naming a
            specific mechanism; never a bare restatement of the finding.>
DATA: <the specific items in the material that prompted it — carry the source's own
       [src: file, loc, "verbatim quote"] tag copied verbatim; never paraphrase a value without its cite>
LIKELIHOOD: obvious | plausible | rare | long-shot

```

## Haiku completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: at least 20 `### HYP` candidate cards, each with CLAIM, ROLE
  (root cause | contributing factor), FAMILY, a REASONING chain of ≥5 steps that reaches the
  presentation, and cited DATA; ALL 11 cause families represented (≥1 card each); or a single
  `EMPTY-INPUT` line.
- COMPLETE means: ≥ 20 distinct cards, EACH with a ROLE line, ALL 11 families represented (≥1 each —
  no family may be missing), each card's CLAIM a specific mechanism / state (not a restatement), each
  REASONING a ≥5-step chain that reaches the presentation, and DATA carrying a verbatim [src:] cite.
  Fewer than 20, any card missing ROLE, any family missing, or any chain shorter than 5 steps, is
  INCOMPLETE.
