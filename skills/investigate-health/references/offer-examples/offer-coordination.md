# Offer coordination layer — prep (0a/0b/0c/0d) + audit (3a/3b/3c)

> The coordination prompts that are NOT per-section writers. Two prep stages are REINSTATED, and
> they run at opposite ends of prep: the **name registry** (`names.md` → `offer-names.md`) is
> **Stage-0a** and runs FIRST, giving every mechanism node and cross-candidate connection a
> plain-English name; the **planner** (`planner.md` → `offer-plan.md`) is **Stage-0d** and runs
> LAST in prep, deciding the document before anyone writes it. That order is not arbitrary — the
> planner writes client-facing titles and needs the names to exist, and the registry must not
> depend on a plan that has not been written. Both run before the section fan-out. The
> deepening mechanism-maps remain the source of what a node IS; the registry is the source of what a
> node is CALLED in client text. Redundancy control is no longer left to the writers — the plan
> assigns covers/excludes centrally. Every other clause below is carried verbatim from the draft.

---

## STAGE 0 — Pre-fan-out prep (driver + prep agents)

Before any writer is dispatched, build the shared scaffold. This resolves the document structure,
mechanism naming, the §2/§3 partition, own-words, and the dispatch/coverage contract in one place.

**0a — Name registry (runs first, before everything else in prep; see `names.md`).**

- The **name registry** writes `offer-names.md`: for every mechanism node and every cross-candidate
  connection in the mechanism maps and the system-integration map, an internal identifier (writer
  lookup ONLY), a plain-English name, and a one-line plain description. It does not read
  `offer-plan.md` — that file does not exist yet — and it closes with a "not yet named" list of
  anything it could not name plainly, so the registry can be extended rather than guessed at.

**0b — Own-words glossary.** The driver injects the person's own words for their symptoms/experience
(from the interview + symptom artifacts) as a glossary. Writers MUST prefer these for anything the
person experiences. (Without this, "use the person's own words" is unfollowable and writers invent
words that *feel* like the person's — the "screen-and-demand load" failure.)

**0c — §2/§3 router (the partition arbiter).** One prep step takes the UNION of all candidate
actions (Step-8 levers) and tests (Step-4 discriminators + Step-7 sweep flags), **dedupes by
underlying action** (the same pill proposed as both a lever and a discriminator is ONE item), and
assigns each to exactly one section by explicit written criteria:
- **§3 (test-first)** if acting carries lasting/acute harm risk, meaningful cost, or
  irreversibility-of-*harm* (not merely "you can stop taking it"), OR it is a pure diagnostic; OR
  there is a **contraindication** against the person's med list / labs / weight. **Default to §3 on
  any ambiguity.**
- **§2 (act-and-learn)** only if safe and harm-reversible enough to just do, and the response yields
  data.
Output: a dispatch list — every item tagged §2 or §3, deduped, each with the chain-step it touches.
Barren chain-steps (no lever) are emitted here as explicit "no known lever at this step" lines.

**The coverage contract (defined by this dispatch list; asserted later at Stage-3a).** The dispatch
list enumerates, and the STAGE-3 reconciler later asserts, that each of these resolves to exactly
one owner: every surviving candidate (full §1), every candidate carried but not deep-dived (a brief
roster entry), every integration-map cross-edge (the interaction owner), every sweep-check
`still_unexplained` datum (a §3 flag), every chain-step (a §2 lever or a no-lever line), every
routed test.

**0d — Planner (runs last in prep, after the registry, the glossary and the router; see
`planner.md`).** The **planner** reads all upstream material and writes `offer-plan.md`: the
complete ordered section list, each with the EXACT stem of the section file it maps to in `file`,
its FINAL client-facing title, its `covers`, its `excludes` (naming the section that owns the
excluded material), its word budget, and its seam; plus the ordering rationale, the index content,
the total document budget, and the FULL-vs-ROSTER split (only a candidate with a deepening
mechanism-map gets a full section). The `file` stem is what binds a budget to real text: the editor
matches plan sections to written files by stem, so a section with a budget and no stem is a budget
enforced against nothing.

**Each writer's obligation to the plan and the registry — all three are FAIL conditions:**

1. Write what your plan entry's `covers` assigns you, and nothing in its `excludes`. Overlap with
   another section's assigned material is a FAIL, not a stylistic preference.
2. Use your plan entry's title verbatim as your heading, and stay inside its word budget.
3. Refer to every mechanism node and connection by its **name** from `offer-names.md`. Never emit
   an internal identifier (`N12`, `B3`, …) in client-facing text, in any form, including inside a
   parenthetical. The mechanism-map remains the source of what a node is; the registry is the source
   of what it is called. Where the registry has no entry, describe the thing in plain words in a
   clause and give it no name — inventing a term of art is a FAIL, and a plain description is
   always the correct fallback.

---

## STANDING RULES (apply to every writer and to the assembled document)

**Seams between the major parts.** The document must not jump from one part to the next with
nothing in between. The **planner specifies** every seam — where it sits and what it has to do —
as the `seamOut` of exactly one section; that section's **writer writes it**, as the closing one or
two sentences of its own piece, closing what just ended and saying what the next part is for. A
boundary with no assigned `seamOut` is a planner defect; an assigned `seamOut` that was not written
is a writer FAIL. This is the gap behind *"there isn't a section transition that takes us into
interventions something is missing here"* — the jump into interventions was nobody's job.

Two seams are their own section files rather than the tail of a writer's piece: the doorway into
the act-and-learn part and the doorway into the test-first part. **Each has a budget of 80–150
words**, and the planner sets it at 150. A seam says what changes now, what the part that follows
holds, and how to use it. It teaches no mechanism and makes no claim that belongs to a section —
it is a doorway, not a room. A seam that teaches is over its remit as well as its budget, and is
cut back to the doorway.

**The index has exactly one owner.** The dedicated index writer renders it, from the plan, into its
own section file, with a budget of 250–400 words. No other section lists the document's contents.
In particular the opening does NOT: it ends with the shape of the picture and how the candidates
interact, and stops. Two writers each rendering an index produces two indexes concatenated into one
document, which is a FAIL attributable to whichever writer rendered one it did not own.

**No pipeline meta in client text.** The document is written for the person. It never talks about
how it was made. Specifically banned from any client-facing text: prompt-injection or safety
attestations (`Possible injected instructions in any source file: none observed.` — reviewer:
*"why the fuck would you have this sentence?"*), audit or checker notes, stage names, agent or
dispatch language, and any sentence whose subject is the pipeline rather than the person or their
biology. Incident notes are internal-facing and belong in the run artifacts, never in the offering.
This is unconditional — it is not a conditional footer that writers may generalise.

**Gaps: two kinds, two destinations.** This rule and the "gaps for upstream" instruction used to
contradict each other, and writers resolved the contradiction by putting a literal *"gaps for
upstream: …"* line into the person's document. That is pipeline meta and it FAILS.

- A gap that matters TO THE READER — something the picture rests on that nobody has measured, or
  that the shared records do not contain — is stated in the document, in plain reader-facing
  language, as part of the account: *"no test in the records shared with us reaches this, which is
  why it stays open."* No label, no colon-prefixed marker, no mention of stages, upstream, sources
  or this process. It reads as a sentence about their situation, because that is what it is.
- A note addressed to the PIPELINE or to an upstream stage — a missing dose, an artifact that
  should have carried something and did not, a registry entry that does not exist — goes in the
  writer's **structured return only**, never in the document.

The test: could the person read this sentence and learn something about their own situation? Then
it belongs in the document, phrased as prose. Is it telling someone else to go fix an artifact?
Then it belongs in the structured return. A literal `gaps for upstream:` string anywhere in
client-facing text is a FAIL, regardless of what follows it.

**Length is a defect.** Over-budget length fails at the same severity as a missing section. Every
other gate in this pipeline checks for omission; this one checks for excess, and it is the only
force pushing back. "Teach until a non-specialist could retell it" is a depth standard, not a
licence to exceed budget: depth is bought by cutting elsewhere.

---

## STAGE 3 — Assemble + audit (the gates that replace the Haiku-only check)

**3a — Coverage reconciler (assembly-level, FAIL-closed).** Assert every item in the Stage-0c
coverage contract resolved to exactly ONE emitted owner: each surviving candidate and each
candidate carried but not deep-dived, each integration cross-edge, each sweep `still_unexplained`
datum, each chain-step (lever or no-lever line), each routed test. Any item with zero owners, or any duplicate, FAILS assembly (not a warning).
This is the only thing that can catch a piece that was never dispatched — the per-piece Haiku cannot.

**3b — Plain-language auditor (commission errors — the 44-annotation class).** A dedicated pass with
explicit FAIL categories, each mapped to a prior annotation type: (1) undefined term on first use;
(2) invented label / coined name; (3) leaked analytic OR pipeline jargon; (4) stacked/over-hedge;
(5) cross-reference to a node/candidate name not present in assembly; (6) missing paragraph breaks;
(7) a mechanism step not retellable with technical names removed; (8) a coined word where an
own-words-glossary term exists. FAIL → the piece is rewritten. (The completeness-checker catches
omissions; it is blind to these — they make text look MORE complete.)

**3c — Faithfulness / citation pass.** Every load-bearing claim (dose, mechanism step, interaction,
location) traces to a cited artifact path, OR is declared as a gap. An uncited, undeclared claim
FAILS. AND the completeness-checker is rescoped: a declared gap is a PASSING state, so a writer is
never pressured to fabricate to pass. A gap is declared in ONE of two places and the checker
accepts either: as reader-facing prose in the document ("nothing in the records shared with us
measures this"), or as a gap note in the writer's structured return. What the checker does NOT
accept is a literal `gaps for upstream:` marker inside client text — that fails 3b as pipeline
meta even while satisfying 3c, and the two gates must not be satisfiable only by contradicting
each other. Plus: the driver guarantees the
artifact CONTENTS are inlined into each writer's context (not just referenced) — the "lost-examples"
plumbing failure must not recur.

**3d — Editor (the stage that can CUT).** One agent holds the WHOLE assembled document as an object
and is empowered to remove text. Every other gate in this pipeline is an omission check — "what is
missing" — so every force pushes the document longer and none pushes back. This is the one that
pushes back. Its remit:

- **Cut to budget.** Any section over its `offer-plan.md` `budgetWords`, or a document over the
  total, is cut back. Over-budget length is a defect of the same severity as a missing section; it
  is not a warning and it is not traded away for depth.
- **Cut redundancy.** Any passage covering material assigned to another section by the plan's
  `covers`/`excludes` is removed, not merged. The owner keeps it.
- **Check the seams.** Every seam the plan specified is present at the boundary it named.
- **Check the index.** The document carries the index the plan supplied, exactly once, from the
  dedicated index section, and every part it lists exists under the title the plan assigned. A
  second list of the document's contents anywhere else — most likely at the end of the opening —
  is cut outright, not merged.
- **Strip pipeline meta.** Any attestation, audit note, stage name or sentence about the pipeline is
  deleted outright.
- **Strip identifiers.** Any `N`-number, `B`-number or other internal handle surviving in client
  text is replaced with its `offer-names.md` name.

The editor does not add content. If it finds a genuine omission it reports it upstream; its own
lever is the cut.
