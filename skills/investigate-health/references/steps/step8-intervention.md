# Step 8 — Intervention research at the highest-leverage nodes

With the mechanism chains in hand, ask how we could act on them. Feeds the offer §2/§3 router.

## Which nodes get researched

A mechanism map can carry dozens of nodes, and researching all of them spends the same effort on a node
with no lever as on the one place with real leverage. So a selector first reads every
`mechanism-map-<candidate-slug>.md` (`step5.10.md`) and picks the **N nodes with the most intervention
leverage** (default 10, `cfg.interveneNodeCap`), judged by:

- the node names real `vulnerabilities` or `persistence-structure` disruptors — something could actually
  be done there;
- several arms or symptoms run through it, so moving it moves more than one thing;
- acting there could plausibly help on a **weeks** timescale even while the deeper causes persist — an
  upstream node nobody can act on now is an **origin**, not a lever (the 5.12 distinction);
- a cheap, reversible probe of it exists;
- it serves a high-consequence candidate.

Selection prefers spread across candidates over N nodes of a single map, unless one map genuinely holds
all the leverage. Nodes not selected are not judged lever-less — they are simply not researched this
pass, and the offer says so rather than implying the space was exhausted.

## Prompt

```
For the SELECTED nodes of a candidate's deepening mechanism-map, research how we could ACT at each.
Dispatch BOTH /research and /research-practitioner.

Cover the FULL space of ways to act, weighted by what would actually help this person:
- **Drugs and supplements are a major part of this and must be researched properly** — the agent, the
  form (which reaches where), the dose, where it acts, and the evidence behind it. Do not treat them as
  a lesser option or skip them to look holistic.
- **ALONGSIDE the non-pharmacological levers** — diet and eating patterns, breathwork, movement, sleep
  and circadian timing, stress and nervous-system practices, clinician procedures.
Neither category is the default answer. The node decides which fits: a luminal chemistry node and a
nervous-system node have different real levers, and saying so is the job.

YOUR NODES: <<the selected node handles + definitions, from the candidate's deepening mechanism-map>>

Per lever: MECHANISM OF CORRECTION (cited); TYPE [self|clinician][cheap|costly][reversible-harm|not]
[evidence tier]; PROGRAM (protocol + sequence + read-out window); DECISION BRANCH (if X→Y; if Z→W);
ETIOLOGY FIT (why it suits THIS person's root; if the root is historical/psychological the lever must
address THAT); ALREADY-TRIED (cross-check treatment-response; never a bare repeat of a failure);
SAFETY (interactions/contraindications vs meds/labs/weight).
NO known lever at this node → say so plainly (a required, valid output). Do NOT state a dose the
research doesn't give. Feeds the offer §2/§3 router.
```

## Stage-A faithfulness (driver pass over this output)
Every load-bearing figure — a dose, a lever protocol, a mechanism-of-correction claim — traces to a
cited source, OR is marked "gaps for upstream / no evidence found". An uncited, unflagged figure FAILS
(this is what stops a fabricated Step-8 dose reaching the user behind green gates).

## Driver reconciler (fail-closed)
- Every SELECTED node → an agent that returned a lever OR an explicit "no known lever at this node"
  line. A selected node with no owner FAILS assembly.
- Node selection returning zero nodes FAILS rather than silently falling back to researching every node.

## Haiku completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: per lever — mechanism of correction (cited), type tags, program
  (protocol + sequence + read-out window), decision branch, etiology fit, already-tried cross-check,
  safety; OR a plain "no known lever at this node" line.
- COMPLETE means: a lever carries all its fields, OR the node carries an honest no-lever line (a valid,
  complete output); a dose the research doesn't give is NOT invented.
