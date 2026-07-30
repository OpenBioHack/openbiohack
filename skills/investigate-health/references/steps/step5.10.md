### Step 5.10 — B3 Deep Mechanism Map (one per candidate that fits the shape)

## The move, in plain terms

B2 produced a **profile** — the properties the cause must have. This step goes hunting for the actual things
that match that profile, and for each one builds a model deep enough to do two jobs:

1. **Simulate the system** — predict what we would see if this were operating, so the next step can compare
   those predictions against what is actually observed.
2. **Locate where you could intervene** — every node in the model is a place someone could act, and the map
   is where those places come from.

**A label is not a model.** "Small-intestinal overgrowth" names a suspect; it does not tell you what feeds
it, what holds it in place, what would dislodge it, or where in the gut it sits. This step is the difference
between naming a thing and understanding it well enough to act.

## Finding candidates — cast wide

Do not just take the hypothesis you were handed. Look for **everything** that fits the B2 profile:

- the hypotheses already generated upstream;
- a **shape-fit search** — what entities have these properties, regardless of whether anyone named them;
- a **precedent / analogue search** — documented real cases matching the *whole* presentation, not one
  symptom. This is a genuine discovery move: it is how a rare named syndrome gets onto the list when
  nobody involved had thought of it. It doubles as a sanity check — if no reported case looks like this,
  that is worth knowing;
- the person's own prior thinking, treated as a **low-trust prior** to re-derive, not assume.

## Building the map — the node schema

Every node gets:

| field | what it means |
|---|---|
| `inputs` | what feeds this node |
| `outputs` | what it produces |
| `persistence` | what keeps it going once started |
| `interactions` | what else it acts on / is acted on by |
| `environment-modulation` | what conditions make it worse or better |
| `location` | the compartment/segment and cell type where it operates. For something secreted or active elsewhere, give **production-site vs action-site** separately |
| `vulnerabilities` | **what disrupts this node** — this is where intervention points come from |
| `persistence-structure` + disruptors | **what holds the process in place, and what would dislodge it** — a self-sustaining loop needs a different intervention than a continuously-driven one |

Two rules on the map itself:
- **Every node is a resolved entity** — no aggregate acting as a single actor (the grain rule from B2).
- **Every edge is tiered**, and on speculative edges (mechanistically-plausible and below) **name a
  falsifier**: what observation would show this edge is wrong.

## Composite candidates are first-class

Sometimes the answer is not one thing but **several co-residents with different roles**. Build those as a
single candidate, using role vocabulary: *output-producer / resistance-conferrer / bloomer /
sheltered-partner / cross-feeder*, plus the interaction edges (who feeds, shelters, protects, cross-feeds
whom).

A composite is **built and ranked as a unit**, but every member and every edge is individually resolved.
This matters because testing each member alone can destroy a true division-of-labour answer — the member
that looks unsupported may be the one being sheltered.

## The exclusion discipline — how a candidate may be removed

This is the rule that prevents the most damaging error in the whole pipeline: quietly dropping a candidate
that was never actually checked. **Tag every exclusion fact with its strength:**

- **(a) examined-and-excluded-with-mechanism** — it was looked for, with a method that could have found it,
  and it was not there (or a mechanism makes it impossible).
- **(b) primarily-or-mostly-true** — generally true, but not established for this case.
- **(c) not-observed-but-never-examined** — absent from the record because nobody looked.

> **Only an (a) may remove a candidate**, and it must cite the **primary-source sentence** that establishes
> it, with enough detail for an auditor to verify independently. Never a self-assigned label.
>
> **(b) and (c) are carried forward** with their strength and an explicit *"elsewhere not examined"* flag.
> They may lower a candidate. **They must never silently delete one.**

> Worked example (illustrative): "no agent with activity against this organism class appears anywhere in the
> treatment record" is an **(a)** about the *treatment*, verifiable from the record — so "treatment-refractory"
> cannot be claimed for that organism; it was never targeted. But "the stool tests did not show organism X in
> the small bowel" is a **(c)**: a stool test samples the colon and never examined the small bowel. Using that
> (c) to exclude a small-bowel candidate is exactly the error this section exists to stop.

## The measurement-edge check — before a number may bear weight

Run this on **any load-bearing edge that is quantitative, or imported from another context** (another
species, in-vitro, a different tissue or compartment, a different dose, acute-vs-chronic,
healthy-vs-diseased).

**1. Map the edge.** Write side by side what the cited evidence **actually measured** (system / compartment /
dose / endpoint / population) versus what is being **claimed here**. Name every gap you are crossing. That
gap list *is* the edge between measured and extrapolated.

**2. Commensurability guard — refuse apples-to-oranges.** Before any number supports *or* refutes the edge,
check the two quantities are the same kind, place and basis. State in one line why you refuse, if you do:

- a concentration in one compartment used to infer another (blood vs lumen vs intracellular vs tissue —
  especially across heavy absorption or first-pass metabolism);
- total versus free/active fraction (a conjugated metabolite is not its active parent);
- dose administered versus concentration achieved;
- in-vitro added versus in-vivo achievable;
- peak versus sustained exposure.

**3. First-principles estimate — ONLY where the quantity was never measured.** A transparent
back-of-envelope: build the target quantity from its inputs (dose → moles; the volume, area or time it
distributes into; release and clearance kinetics; the relevant physiology). Then:
- tag **every** assumption with its own confidence and whether it is measured or guessed;
- carry a **range** (best case and worst case);
- give an **order-of-magnitude verdict** against the effect threshold — within ~10× = plausible;
  ~10–100× = weak/borderline; ~1000× off = implausible;
- distinguish **peak vs sustained** where the biology cares;
- run a **sensitivity check** — which single assumption is the verdict most fragile to?

**4. Verdict and propagation.** Emit a tier adjustment (e.g. established → mechanistically-plausible, or a
`dose-implausible` flag meaning the edge cannot bear weight), a one-line edge statement, the estimate with
its assumptions and range, and a **`what-would-close-this`** line naming the single measurement that would
turn the estimate into a fact. **Downstream synthesis and the offer must carry the adjusted tier** — no
silent re-promotion later.

**5. Know the limit.** A back-of-envelope is not a measurement. Output ranges and confidence, never an
estimate dressed as a fact. Where the inputs are too unknown to even estimate, mark the edge
**`unquantifiable — speculative`**. Write the full reasoning into the artifact so the person can challenge
it.

## Two per-candidate outputs

- **Fit-check** against each B2 property: **satisfies yes / no / partial**, with the evidence.
- **Cheapest discriminator.** For the candidate and for every load-bearing property: the single cheapest
  observation that would separate it from the alternatives, tagged **`askable-now` / `in-records` /
  `needs-test`**. The next step resolves these, so a missing tag stalls the pipeline.

## Output shape

```markdown
# Mechanism map — <candidate>

## Candidate provenance
<where this candidate came from: upstream hypothesis / shape-fit search / precedent case / person's prior>

## Nodes
### N1 — <resolved entity>
- inputs / outputs / persistence / interactions / environment-modulation
- location: <compartment + cell type; production-site vs action-site if they differ>
- vulnerabilities: <what disrupts this node>
- persistence-structure: <what holds it in place> — disruptors: <what would dislodge it>

## Edges
- N1 -> N2 — <mechanism> — tier: <…> — falsifier (if speculative): <what would show this is wrong>
- <for any quantitative/imported edge> measurement-edge verdict: <measured-vs-claimed gap; commensurability
  ruling; estimate + assumptions + range + sensitivity; tier adjustment; what-would-close-this>

## Composite structure (if applicable)
- member: <entity> — role: <output-producer / resistance-conferrer / bloomer / sheltered-partner / cross-feeder>
- interaction edges: <who feeds/shelters/protects/cross-feeds whom>

## Fit-check vs the shape profile
| property (from B2) | satisfies | evidence |

## Exclusions considered
| fact | strength (a)/(b)/(c) | primary-source sentence | effect: removed / lowered / carried |

## Cheapest discriminators
| what would separate this | askable-now / in-records / needs-test |
```

## Done when

- The node schema is complete, **including `vulnerabilities` and `persistence-structure`** — these are what
  the intervention step mines, so a map without them cannot be acted on.
- **Every exclusion used to remove a candidate is an (a) with a cited primary-source sentence.** No (b) or
  (c) has been used to delete anything.
- Every load-bearing quantitative or imported edge carries a measurement-edge verdict: commensurability
  checked, `dose-implausible` edges flagged and carrying no weight, estimate-only edges tagged with
  assumptions, range and the `what-would-close-this` measurement.
- Every candidate and every load-bearing property carries a cheapest-discriminator tag.
- No aggregate-as-actor survives in any load-bearing line.

**Artifact:** `mechanism-map-<candidate-slug>.md`, one per candidate. **Prerequisite:**
`shape-profile-<Hn>.md` from B2.
