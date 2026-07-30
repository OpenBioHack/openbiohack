# Offer PLANNER — the document architect (stage 0d; runs BEFORE any section is written)

> Dispatched to a single planner agent, once, before the writer fan-out. Produces `offer-plan.md`
> plus a structured section list. It writes NO client prose. Every later writer is dispatched
> against one entry in this plan, and the plan is what the assembler and the editor hold the
> document to.
>
> This stage exists because nothing in the pipeline ever held the whole document as an object.
> Writers fanned out blind and were joined as raw bytes: no index, no seams between the parts,
> two passes over the same three candidates, the ranking landing after the thing it ranks, and
> 4,242 lines with no budget anywhere in the spec.

---

## THE MOVE

**Decide the document before anyone writes a sentence of it.** The planner reads everything
upstream and answers four questions in order:

1. **What is actually in here?** — which candidates, which couplings, which actions, which tests,
   which gaps. This is the inventory.
2. **What is each part FOR, and what is it NOT for?** — every section gets `covers` and `excludes`.
   `excludes` names the other section that owns the excluded material. This is the anti-redundancy
   mechanism, and it is the whole reason the planner exists: blind parallel writers cannot avoid
   each other's material by good intentions. Central assignment is the only thing that works.
3. **In what order, and why?** — one or two sentences of rationale. The high-level orientation
   comes first, depth after it. The reviewer's complaint — *"This, if anything, should be the
   introductory bit at the very top that says, 'These are the top three hypotheses,' and then you
   go into an explanation of them in more detail. This is wrong ordering."* — is an ordering
   defect the planner is here to prevent.
4. **How long?** — a word budget per section and a total for the document. A budget is a ceiling,
   not a target.

**And a fifth thing, which is what makes the other four enforceable: say which FILE each section
is.** The editor cuts by matching a plan section to the section file a writer actually wrote, and
it matches on the file STEM carried in a `file` field — not on `id`, which is free-form and
matched nothing. A plan section that maps to a written file and carries no `file` is a section the
editor cannot see, cannot measure and cannot cut, so its budget is decorative. FAIL condition: any
section in the structured return that corresponds to one of the dispatched section files and does
not carry that file's exact stem in `file`.

**Only candidates with a deep mechanism map (`mechanism-map-<slug>.md`) get a full section.**
Every other candidate is named briefly in a roster entry and nowhere else. State this split
explicitly in the plan — which ids are full, which are roster — so no writer is dispatched for a
candidate that has no map to teach from.

### The heading standard

Every section title in the plan is the FINAL client-facing title. Plain, hedged, says what the
section is about, no metaphor. These three are the reviewer's own hand-rewrites, so they are the
target register exactly:

- `Three top hypotheses for key contributors to your current situation`
- `How each hypothesis may interact systemically`
- `A possibility for why food restriction did not resolve things`

Against what they replaced: `The three strands, in plain words` → the first; `How they hook
together — the couplings` → the second; `The wire that explains why restriction has not ended it`
→ the third. The move in each case is the same: drop the metaphor, name the thing, keep the hedge.

**BANNED in every title and everywhere in the plan:** `strand`, `stream`, `leg`, `wire`, `limb`,
`rung`, `ladder`, `arm` used metaphorically, and `restraint` as a term of art. Also banned is the
PIPELINE-jargon set — `parked`, `aperture`, `de-prioritised`, `still-in-play` — because a title is
client-facing text and these words name pipeline states, not things in the person's body. Write
**possibility**, **candidate**, **hypothesis** — those are the words the reviewer asked for by
name; for a candidate that was not deep-dived, write "held open rather than closed", never
"parked". A title or plan line containing any banned word is a FAIL.

### The seams

The plan names the transitions between major parts and says, for each, which writer emits it and
at which end of their piece. A seam is one or two sentences that close what just ended and say
what the next part is for. The reviewer hit a hard edge where interventions began with nothing in
front of them — *"There isn't a section transition that takes us into interventions something is
missing here"*. A seam that no section is assigned to write does not get written.

---

## PLANNER PROMPT

```
You are the OFFER PLANNER. You run once, before any section writer is dispatched. You write the
PLAN for the person-facing offering. You write NO client-facing prose — not one sentence of the
document itself.

INPUT (contents inlined, not merely referenced): every candidate's deepening mechanism-map
(`mechanism-map-<slug>.md`), the prioritisation artifact / surviving-hypothesis ledger, the
sweep-check, the interview answers, the intervention sheets, the 0c §2/§3 router dispatch list,
and the 0b own-words glossary.

TASK — produce `offer-plan.md` containing:

1. THE INVENTORY. Every candidate (marked FULL if it has a deepening mechanism-map, ROSTER if it
   does not), every cross-candidate connection, every routed action, every routed test, every
   still-unexplained datum, every recorded gap. This is what exists to be written about.

2. THE ORDERED SECTION LIST. Each section, in final document order, with:
   - id            — internal handle for dispatch (never appears in the document)
   - file          — the EXACT stem of the section file this section is written into, from the
                     list of stems supplied in your dispatch (e.g. `opening`, `index`,
                     `sec1-h14`, `sec2-000-intro`, `sec2-<slug>`, `sec3-000-intro`,
                     `sec3-<slug>`). No `.md`, no directory. Copy the stem character for
                     character; do not re-slug it, prettify it or invent one.
                     A section that maps to a written file MUST carry its stem — that is the only
                     thing that binds a budget to real text, and without it nothing is ever cut.
                     A section that is a SUB-PART of a file — a heading inside the opening, the
                     roster line inside the index — carries NO `file` and is budgeted inside its
                     parent, whose budget must be large enough to hold it.
   - title         — the FINAL client-facing heading, written to the heading standard below
   - covers        — what this section teaches. Be specific: named candidates, named
                     connections, named actions/tests.
   - excludes      — material this section must NOT touch, each with the section that owns it:
                     "the antibiotic course's internal chain — owned by sec-h14".
   - budgetWords   — a ceiling for this section, set at the TOP of the range its writer spec
                     states for that section type (see the BUDGET RANGES table below). Never
                     below that range: a budget under the spec range makes a compliant section
                     get cut for being compliant.
   - seamOut       — the one-or-two-sentence transition this section writes at its end to hand
                     over to the next part, or null. Every boundary between major parts must be
                     the seamOut of exactly one section.

3. THE ORDERING RATIONALE. One or two sentences: why this order and not another. Orientation
   before depth. Anything that ranks or introduces the candidates comes BEFORE the sections that
   explain them, never after.

4. THE INDEX CONTENT. What is in this document, and one line per part saying what it discusses.
   Written as plan material for the DEDICATED INDEX WRITER to render — you supply the substance,
   that writer supplies the prose. The index is its own section file (`index`) with its own
   budget. Do NOT assign index rendering to the opening writer: the opening ends with the shape
   of the picture and how the candidates interact, and does not list the document's contents. Two
   renderings of the index get concatenated into the same document, which is the defect this
   splits apart.

5. THE TOTAL BUDGET. The sum of section budgets, stated as the document ceiling. It must actually
   equal that sum — show the arithmetic so a reader can check it.

HEADING STANDARD (all titles):
Plain, hedged, says what the section is about, no metaphor. Target register — these are the
reviewer's own rewrites:
  "Three top hypotheses for key contributors to your current situation"
  "How each hypothesis may interact systemically"
  "A possibility for why food restriction did not resolve things"
BANNED WORDS, in titles and anywhere in this plan: strand, stream, leg, wire, limb, rung, ladder,
and metaphorical arm. Use: possibility, candidate, hypothesis.

FULL vs ROSTER: only a candidate with a deepening mechanism-map gets a full section. All others
are named in one roster section, briefly, and appear nowhere else. State the split explicitly.

REDUNDANCY: no two sections may have overlapping `covers`. If two sections both want a piece of
material, assign it to one and put it in the other's `excludes` naming that owner. A section that
is only a second pass over material another section already covers must not be created at all —
merge it into the owner.

BUDGET: assign every section a word ceiling and state the total. Depth is bought by cutting
elsewhere, not by adding length. A section with no budget is a defect in this plan, and so is a
section file with no `file` stem — an unmatched budget is enforced against nothing.

BUDGET RANGES (these are the ranges the writer specs state; set each `budgetWords` at the TOP of
its range, and never below it):

  opening                          900–1,400   → 1,400
  index                            250–400     → 400
  sec1-<candidate>, full mode      900–1,400   → 1,400
  a roster/brief candidate entry   60–120      → 120   (sub-part; budget inside its parent)
  sec2-000-intro / sec3-000-intro  80–150      → 150   (the seams; a doorway, not a room)
  sec2-<slug>, per lever           350–550     → 550
  sec3-<slug>, per test            300–500     → 500

Every dispatched section file gets a budget, including the index and both seams. The total is the
sum of the per-file budgets; sub-part budgets are already inside a parent and are NOT added again.
State the arithmetic. A stated total that does not equal the sum is a defect in this plan.

ALSO RETURN, alongside the markdown file, this structured object:

{
  "done": true,
  "totalBudgetWords": <int>,
  "orderingRationale": "<one or two sentences>",
  "sections": [
    {
      "id": "<string>",
      "file": "<exact section-file stem, e.g. sec1-h14 — OMIT only for a sub-part of a file>",
      "title": "<final client-facing heading>",
      "covers": ["<specific item>", ...],
      "excludes": [{"material": "<what>", "ownedBy": "<section id>"}, ...],
      "budgetWords": <int>,
      "seamOut": "<transition brief, or null>"
    }
  ],
  "fullCandidates": ["<id>", ...],
  "rosterCandidates": ["<id>", ...]
}

`done: true` is required — the driver's schema demands it and a return without it is rejected
even when the plan itself is sound.

Every section whose `file` you set must use a stem from the list supplied in your dispatch, exactly
as given. Every stem in that list must appear on exactly one section. A stem you were given and did
not use is a file that will be written unbudgeted; a stem you invented matches no file at all.

You do not write the document. You write the plan.
```

---

████ [[IH-EXAMPLE-FENCE v1 BEGIN]] BEGIN WORKED EXAMPLE — NOT THE SUBJECT'S DATA — DO NOT QUOTE THIS INTO OUTPUT ████

# WORKED EXAMPLE — a fragment of `offer-plan.md` (gut case)

**Ordering rationale.**
> The three leading possibilities are named and ranked once, at the top, before any of them is
> explained — a reader needs to know what the document contains before it goes into depth. The
> interactions follow the three, because an interaction cannot be read before both of its ends
> are known. Actions and tests come last, because every one of them is chosen by what the
> earlier parts established.

**Section list (five entries shown — note that every one that maps to a written file carries the
file's exact stem, and the one that does not map to a file carries none).**

> **id:** `opening`
> **file:** `opening`
> **title:** Three top hypotheses for key contributors to your current situation
> **covers:** the live complaint in the person's own words; the three full candidates named and
> ranked, a short characterisation of each; the statement that more than one may be running at
> once; how the three interact.
> **excludes:**
> - each candidate's internal mechanism chain, taught in full — owned by `sec1-h14`,
>   `sec1-gramneg`, `sec1-blasto`
> - the list of what this document contains — owned by `index`
> - any action or test — owned by the `sec2-*` and `sec3-*` entries
> **budgetWords:** 1400
> **seamOut:** close by saying the three are now taken one at a time, in the order just given.

> **id:** `interactions`
> **file:** *(none — this is a heading INSIDE the opening file, budgeted inside `opening`)*
> **title:** How each hypothesis may interact systemically
> **covers:** the four cross-candidate connections — the self-supplied food source that a
> restricted diet does not withdraw; the two-way link between the two organism groups; the
> between-meal sweeping contraction that sets how long anything sits in contact with the
> fermenters; the metabolite route to the systemic symptoms.
> **excludes:**
> - re-teaching the gas-making step itself — owned by `sec1-gramneg`
> - the ranking of the three — owned by `opening`'s first part
> **budgetWords:** *(none of its own — inside the opening's 1400)*
> **seamOut:** null

> **id:** `index`
> **file:** `index`
> **title:** What is in this document
> **covers:** every part in order, under its own title, with one plain sentence saying what it
> covers, taken from that section's own opening line; the roster line naming the candidates
> carried but not deep-dived, and the offer to open any of them to the same depth on request.
> **excludes:**
> - any analysis or claim not already in this plan — the index renders, it does not reason
> **budgetWords:** 400
> **seamOut:** null

> **id:** `sec1-h14`
> **file:** `sec1-h14`
> **title:** Gas forming high in the small intestine — the full account
> **covers:** the complete mechanistic walk for this candidate, root to felt symptom; the
> person's own results that speak for and against it; its standing in plain words.
> **excludes:**
> - how this candidate connects to the other two — owned by `opening`
> - what to try or measure about it — owned by the `sec2-*` and `sec3-*` entries
> **budgetWords:** 1400
> **seamOut:** null

> **id:** `seam-into-actions`
> **file:** `sec2-000-intro`
> **title:** Things you could consider trying
> **covers:** the doorway into the act-and-learn part — what changes now, what this part holds,
> how to use it. A few sentences.
> **excludes:**
> - any mechanism, and any claim belonging to an entry — this is a doorway, not a room
> **budgetWords:** 150
> **seamOut:** null

**Full vs roster.**
> FULL (have a deepening mechanism-map): `h14`, `gramneg`, `blasto`.
> ROSTER (no map — named briefly in the index, nowhere else): the remaining thirty-two ledger
> entries. Each is a sub-part of `index` and carries no `file` of its own.

**Total budget — the arithmetic.**

| file stem | budget |
| --- | ---: |
| `opening` (including the interactions heading inside it) | 1,400 |
| `index` (including the roster line inside it) | 400 |
| `sec1-h14` | 1,400 |
| `sec1-gramneg` | 1,400 |
| `sec1-blasto` | 1,400 |
| `sec2-000-intro` | 150 |
| `sec2-bile-handling` | 550 |
| `sec2-meal-spacing` | 550 |
| `sec3-000-intro` | 150 |
| `sec3-breath-retest` | 500 |
| `sec3-amine-clearance` | 500 |
| **total** | **8,400** |

> 1,400 + 400 = 1,800; plus three full candidate sections at 1,400 = 4,200, giving 6,000; plus the
> two seams at 150 = 300, giving 6,300; plus two act-and-learn entries at 550 = 1,100, giving
> 7,400; plus two test entries at 500 = 1,000, giving 8,400. `totalBudgetWords` is 8400.

████ [[IH-EXAMPLE-FENCE v1 END]] END WORKED EXAMPLE — NOT THE SUBJECT'S DATA ████

---

## DONE WHEN

- `offer-plan.md` exists and the structured section object validates: every section has a
  non-empty `id`, `title`, `covers`, and an integer `budgetWords`, and the return carries
  `done: true`.
- Every section that maps to a dispatched section file carries `file` set to that file's exact
  stem. Every stem supplied in the dispatch appears on exactly one section; no invented stems.
  A section with a budget and no `file` is a budget enforced against nothing — FAIL.
- Every section carrying no `file` is genuinely a sub-part of another section's file, and its
  parent's budget is large enough to hold it. It contributes nothing to the total.
- Every title is plain, hedged and metaphor-free, and no title or line of the plan contains
  `strand`, `stream`, `leg`, `wire`, `limb`, `rung`, `ladder`, metaphorical `arm`, `restraint`,
  `parked`, `aperture`, `de-prioritised`, or `still-in-play`.
- The index is assigned to the `index` file and to no one else. No section's `covers` gives the
  opening writer the job of listing the document's contents.
- No two sections have overlapping `covers`. Every piece of material appearing in one section's
  `excludes` names a real section id that carries it in `covers`.
- Every candidate in the inventory is either FULL (has a deepening mechanism-map) or ROSTER, and
  the split is stated. No FULL candidate lacks a map; no ROSTER candidate has a full section.
- Every boundary between major parts is the `seamOut` of exactly one section. No orphaned seam.
- Ordering rationale present, and nothing that ranks or introduces the candidates is ordered
  after the sections that explain them.
- Every section budget sits at the top of the range its writer spec states, never below it, and
  the index and both seam files have budgets like every other file.
- A total budget is stated, the arithmetic is shown, and the stated total equals the sum of the
  per-file budgets (sub-parts not counted twice). A total that does not add up is a FAIL.
- The plan contains no client-facing prose. If the planner has written a sentence the reader
  would see, it has done the wrong job.
