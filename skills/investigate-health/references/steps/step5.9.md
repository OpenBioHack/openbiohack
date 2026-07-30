### Step 5.9 — B2 Shape Deduction (per leading hypothesis)

## The move, in plain terms

B1 gave you constraints — the things that must be true if this hypothesis is real. This step turns each
constraint into a **property the cause must have**, so that what you are looking for is described as a
**profile** rather than a name.

Why that matters: if you hold a name ("small-intestinal overgrowth"), you can only ask *"is it that or not?"*
— and you will match anything that vaguely fits the label. If you hold a profile ("must produce gas without
incoming food; must sit somewhere a stool test cannot see; must survive a non-absorbed luminal
antibiotic"), you can hold up ANY
candidate — including one nobody has named yet — and check it property by property.

**You are building the wanted-poster, not picking a suspect.** The candidate hunt happens in B3, against
this profile.

## Turning a constraint into a property

Each line goes: **constraint → therefore the cause has property P → here is why that follows.**

> Worked example (illustrative):
> *Constraint:* the gas symptom continues on fasted mornings and through at least one fasted night [src:
> extracted/timeline.md, <two dated entries>].
> *→ Property:* the cause must be able to **generate gas from something other than the meal just eaten** —
> an endogenous substrate, a resident population feeding on secretions or sloughed cells, or swallowed air.
> *Why it follows:* nothing is arriving; something is still producing.

Each arrow needs to be **evidence-based, not asserted**. If the arrow is obvious, state it inline with a
tier tag. If it is novel or load-bearing, dispatch a paired `/research` + `/research-practitioner` to
establish it — but do not burn a research dispatch on a trivial arrow.

## Two rules that do the real work

### 1. Explode aggregates and vague relations — the grain rule

A property is useless if it names a **group acting as one thing**, or a **relation with a missing end**.
Before any line can bear weight, it must be broken down until the actors are individually checkable.

- ✗ *"The drug set failed to clear it."* — which drug, against which organism, at what dose reaching where?
- ✗ *"The consortium confers resistance."* — **who** confers resistance **to whom**, **by what mechanism**?
- ✗ *"It feeds the overgrowth."* — which member feeds which, on what substrate?
- ✓ *"A minimally-absorbed antibiotic acts only inside the lumen it passes through, so it exerts little
  pressure on an organism sheltering in the mucus layer of a different segment — a candidate hiding there
  is not excluded by having been through that course."*

**Where to stop:** at the level where the actors can be **individually checked against a constraint** —
family → species is usually right. Do **not** keep going down to chemicals or atoms. This is *bounded*
decomposition; the point is checkability, not reductionism for its own sake.

### 2. Grade tension on a spectrum, never binary

When a candidate property sits awkwardly against a constraint, say **how** awkwardly. A flat
"consistent / inconsistent" throws away the information that decides things at convergence.

- **contradiction** — both cannot be true. This is what deletes candidates.
- **partial tension** — fits in part; something is unexplained but not impossible.
- **fits-only-if-an-extra-mechanism-is-added** — compatible, but only by positing an additional step. Name
  that step explicitly, because it is now a claim of its own and carries its own burden of proof.

## Where the data cannot decide

Where no evidence can adjudicate a property, mark it **keep-open** — do not guess a value to fill the row.
A keep-open property is a real output: it tells B3 that candidates cannot be separated on that axis, and it
tells the test-planning step what would be worth measuring.

## Output shape

```markdown
## Required properties

- **P1 — <the property, stated as what the cause must be able to do / must be like>**
  - from constraint: <which B1 constraint it derives from>
  - why it follows: <the arrow, in one or two sentences>
  - evidence: [src: <…>] or tier tag (established / studied / mechanistically plausible / temporal-only /
    speculative), plus a research ref if one was dispatched
  - tension notes: <any candidate-shape known to sit in contradiction / partial tension /
    fits-only-if-extra-mechanism against this property>

## Keep-open (data cannot adjudicate)
- <property>: <why nothing on record can settle it; what would>
```

## Done when

- Every required property traces to a constraint from B1 and carries either an evidence reference or a tier
  tag — no free-floating properties.
- **No aggregate-as-actor and no unspecified relation survives in any load-bearing line.** This is the grain
  check the decomposition auditor enforces; a line that says "the family does X" without naming which member
  and which mechanism is a fail.
- Every tension is graded on the three-way spectrum, not as a binary.
- Anything the data cannot settle appears under keep-open rather than being guessed.

**Artifact:** `shape-profile-<Hn>.md`. **Prerequisite:** `constraints-<Hn>.md` from B1.
