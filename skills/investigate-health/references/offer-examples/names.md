# Offer NAME REGISTRY — plain-English names for every mechanism (stage 0a; runs BEFORE any section is written)

> Dispatched to a single registry agent, once, BEFORE the planner and before the writer fan-out.
> Produces `offer-names.md`. Every writer is dispatched with it and uses the NAME it assigns. No
> writer ever emits an internal identifier.
>
> Because it runs first, the registry cannot read `offer-plan.md` — that file does not exist yet.
> It derives its coverage from the mechanism maps and the system-integration map instead, and
> names everything those carry rather than only what a plan happens to reference.
>
> There is a working translation layer on the SYMPTOM axis — `offer-glossary.md`, mapping to the
> person's own words, and writers used it well. There has never been one on the MECHANISM axis,
> and that is where every term the reviewer objected to lives. A registry like this existed in the
> draft design and was dropped in favour of "use the map's name": a trade that bought cross-writer
> consistency and paid in translatability. This stage buys both back — one name per node, chosen
> once, and it is a plain-English one.

---

## THE MOVE

**Prohibition does not work at this length. Substitution does.** The existing spec bans exactly
four words. One of them, `aperture`, appears 43 times in the delivered document. Adding a fifth
banned word is the one fix already proven not to work.

So this is not a ban list. It is a **positive substitution table**. Every mechanism node and every
cross-candidate connection that any section will reference gets three fields:

- **identifier** — `N12`, `B3`, and so on. Recorded here for the writers' lookup ONLY, so that two
  writers referring to the same node use the same name. It never appears in client prose.
- **name** — plain English, readable by a non-expert with no glossary and no cross-reference.
  This is what writers write.
- **description** — one line, plain, saying what it is or does.

A writer who needs a node opens the registry, finds it by identifier, and writes the name. There is
nothing left to invent, so no writer coins a word — which is how `wire` got in: a compliance
attempt at plain language that broke the no-coinage rule and still failed to displace `B3`, both
appearing in the same sentence.

### When the registry has no row for something a writer needs

This will happen, and the writer must have a sanctioned move — otherwise the writer is banned from
the identifier, banned from the map's label and banned from metaphor, with nothing left but
invention. That corner is exactly where `wire` was produced.

**The fallback: describe the thing in plain words, inline, in a clause, and give it no name at
all.** Not a new term, not a label, not a metaphor, not a capitalised phrase that reads like one.
"the wave of muscle contraction that runs between meals and clears leftovers downstream" is
correct; "the sweep mechanism", "the clearance pathway" and "the wire" are all failures, because
each is a coinage the reader must now carry.

Coining a new named concept is a FAIL — including a coinage that feels plainer than the term it
replaces, which is the specific trap. A plain description is ALWAYS the correct fallback, and a
sentence that describes rather than names is never wrong on this axis. The writer also records the
missing node in its structured return so the registry can be extended; that note never appears in
the person's prose.

The failure this prevents, in the reviewer's words: *"don't fucking reference things like fucking
connectors B4 the fucking user doesn't fucking know what that means, the sentence needs to be
understandable on its own without having to reference some other part of this super fucking long
document."*

**That last clause is the standard.** A name passes if the sentence containing it can be read
alone. A name fails if reading it sends the reader somewhere else in the document.

### The naming standard

A good name is:

- **Plain** — words a non-expert already owns. If the name needs a definition to be read, it is a
  term, not a name.
- **Self-contained** — carries its own meaning in the sentence. No pointer to another part.
- **Descriptive of what it does**, not of what it is called in the literature. The technical term
  goes in a parenthetical the first time, if it goes anywhere.
- **Not a metaphor.** `wire`, `strand`, `limb`, `rung`, `ladder`, `leg`, `stream`, and metaphorical
  `arm` are all names the reviewer stopped at and asked what they meant. Say the thing.
- **Stable** — one name per node, used by every writer, every time. Two names for one node reads
  as two things.

---

## REGISTRY PROMPT

```
You are the MECHANISM NAME REGISTRY. You run once, before any section writer is dispatched. You
produce `offer-names.md`. You write NO client-facing prose.

INPUT (contents inlined): every candidate's deepening mechanism-map (`mechanism-map-<slug>.md`)
and the system-integration map with its cross-candidate connectors. That is the whole input. You
run BEFORE the planner, so `offer-plan.md` does not exist yet — do not look for it, do not wait
for it, and do not infer section assignments. Your coverage comes from the maps: name what they
carry, and the plan can then reference any of it.

TASK: for EVERY mechanism node in those maps and EVERY cross-candidate connection between them,
produce one registry row:

  identifier   — the map's own handle (N12, B3, ...). FOR WRITER LOOKUP ONLY. It must never
                 appear in client-facing text, in any form, including inside a parenthetical.
  name         — a plain-English name a non-expert reads without a glossary and without turning
                 to another part of the document.
  description  — one line, plain, saying what it is or what it does.

THE TEST every name must pass: a sentence containing this name is understandable on its own. If
reading it requires the reader to look up something else in the document, the name has failed.

NAMING STANDARD:
- Plain words a non-expert already owns. A name that needs defining is a term, not a name.
- Describe what it DOES, not what the literature calls it. If the technical term is worth
  carrying, it goes in a parenthetical on first use only.
- No metaphors. Never: strand, stream, leg, wire, limb, rung, ladder, or metaphorical arm. Never
  "restraint" as a term of art — name the actual thing doing the holding back.
- No PIPELINE jargon in a name or a description: never parked, aperture, de-prioritised,
  still-in-play. These name states of this process, not things in the person's body. A name
  containing any word on either list is a FAIL and is rewritten.
- One name per node, used by every writer. Never two names for one thing.
- Do not simply copy the map's node label — map labels are written for analysts. Translate.

COVERAGE: every node and connection in the maps must have a row. A node with no row is a gap the
writers will fill by coining, which is the failure this prevents.

WHAT YOU COULD NOT NAME. If a node resists a plain name — the map is too thin to say what it does,
or every plain phrasing you can find is longer than a sentence — do NOT stretch to a coinage to
fill the row. Record it in a closing "not yet named" list: the identifier, what the map says, and
what is missing. That list is internal and lets the registry be extended before or during the
writer fan-out. A short honest list beats a row containing an invented term of art.

THE WRITER'S FALLBACK, which you are also stating for them: where a writer needs something you did
not name, the writer describes it in plain words inline, in a clause, and gives it no name. Never
an invented term, never a label, never a metaphor. Coining a named concept is a FAIL; a plain
description is always correct.

Return `done: true` with your structured return. The driver's schema requires it and a return
without it is rejected even when the registry itself is sound.

You do not write the document. You write the registry.
```

---

████ [[IH-EXAMPLE-FENCE v1 BEGIN]] BEGIN WORKED EXAMPLE — NOT THE SUBJECT'S DATA — DO NOT QUOTE THIS INTO OUTPUT ████

# WORKED EXAMPLE — rows from `offer-names.md` (gut case)

| identifier *(lookup only)* | name | description |
| --- | --- | --- |
| N12 | the gas these bacteria make when they ferment | Several of the raised bacterial groups break sugars and starches down without oxygen, and gas comes off as a by-product. |
| N14 | the food supply your own gut provides | The mucus your gut lining continuously secretes, plus shed lining cells and digestive secretions — a supply that reaches the bacteria whatever you eat. |
| B3 | the between-meal sweep, and how long food sits in contact with the bacteria | Between meals the small intestine runs a sweeping contraction that clears residue downstream. How often it sweeps sets how long anything stays in contact with the bacteria that would ferment it. |
| B8 | the compounds bacteria make from protein, and how well your gut clears them | Bacteria can make histamine and related compounds from amino acids; the gut lining clears them with an enzyme (called diamine oxidase). Both the making and the clearing matter. |
| B7 | how loudly your gut's signals arrive | Some people's nervous systems report ordinary gut events more strongly than others. This changes how much you feel, without changing how much gas is there. |

**How the good rows were arrived at.**

> `N12` — the map calls it **mixed-acid fermentation gas**. Every word of that is a term. What it
> IS, to a reader, is the gas these bacteria make when they ferment. The chemistry name adds
> nothing the reader can use.

> `N14` — the map calls it **host-derived substrate**. "Host" means you, and "substrate" means
> food; said plainly it is the food supply your own gut provides. That name also does the work the
> section needs, because the point of the node is that this supply does not go away when you
> restrict your diet — and the name says whose supply it is.

> `B3` — the delivered document wrote *"In the integration model that is connector **B3**, and it
> is the wire that makes the motility strands and the fermentation strands one system"*. The
> reviewer's response was *"what the fuck does this mean?"* Three separate failures in one clause:
> an identifier, a metaphor, and a reference to a model the reader has never seen. The name says
> what it is: the between-meal sweep, and how long food sits in contact with the bacteria.

> `B7` — the delivered document used **afferent gain**, glossed as *"how loudly ordinary gut
> events are registered centrally"*. The reviewer could not parse either: *"what the fuck does
> this mean? How loudly gut events are registered that makes no fucking sense."* The gloss failed
> because "registered centrally" is as technical as the term it explains. The name has to be about
> the reader: **how loudly your gut's signals arrive** — some nervous systems report ordinary gut
> events more strongly than others; it changes how much you feel, not how much gas is there.

**Names that would have FAILED, and why.**

| rejected | why it fails |
| --- | --- |
| `connector B4` | An identifier. The reader has no B-list. The sentence cannot be read alone. |
| `the wire under the head symptoms` | Metaphor. Reviewer: *"what the fuck is a wire?"* |
| `the amine limb` | Metaphor. Reviewer: *"what the fuck is a limb? Just fucking speak like a normal fucking person."* |
| `afferent gain` | A term, not a name. Unparseable, and its own gloss was unparseable too. |
| `the host-derived substrate node (N14)` | Copies the map label AND carries the identifier. Two failures. |
| `the mucus pathway` | Nearly right, but "pathway" is a term doing no work, and it hides whose mucus. |

████ [[IH-EXAMPLE-FENCE v1 END]] END WORKED EXAMPLE — NOT THE SUBJECT'S DATA ████

---

## DONE WHEN

- `offer-names.md` exists and carries a row for every mechanism node and every cross-candidate
  connection in the mechanism maps and the system-integration map. No node in those maps is
  missing. (The registry does not consult `offer-plan.md` — it runs first, and that file does not
  exist yet. A registry that claims to have read it has read something else.)
- The structured return carries `done: true`.
- Every row has all three fields: identifier, name, one-line description.
- Every name passes the standing-alone test: a sentence using it is understandable without
  turning to another part of the document.
- No name contains an identifier, in any form.
- No name or description contains `strand`, `stream`, `leg`, `wire`, `limb`, `rung`, `ladder`,
  metaphorical `arm`, `restraint` as a term of art, or the pipeline words `parked`, `aperture`,
  `de-prioritised`, `still-in-play` — and no name is a metaphor of any other kind.
- Anything that could not be named is listed in a "not yet named" section rather than filled with
  an invented term. An empty list is fine; a coined row is a FAIL.
- No node has two names. One node, one name, across every writer.
- No name is a verbatim copy of the map's analyst-facing label.
- The registry contains no client-facing prose beyond the names and their one-line descriptions.
