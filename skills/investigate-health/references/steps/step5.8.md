### Step 5.8 — B1 Constraint Harvest (per leading hypothesis)

## The move, in plain terms

Most reasoning about a hypothesis asks **"what evidence supports it?"** That question is weak, because in a
complex picture many candidates are consistent with the same evidence — supporting facts pile up on all of
them and separate none of them.

This step asks the inverted question: **"if this hypothesis were true, what ELSE would have to be true?"**

Those consequences are **constraints**. They are more powerful than supporting evidence for one reason: a
violated constraint can *delete* a candidate, whereas supporting evidence only adds weight. Every candidate
generated downstream gets tested against this list. **A constraint you fail to write down is how a wrong
candidate survives to the end.**

You also write down the opposite: **where the data is blind.** Every test has an aperture — a thing it can
see and a thing it cannot. A negative result only rules out what the test could actually have seen. If you
do not enumerate the blind spots, downstream reasoning will treat "we never looked" as "it isn't there."

## The test for whether you have written a real constraint

> **Could this line let me DELETE a candidate?**

If no, it is a description, not a constraint — rewrite it or drop it.

- ✗ *"The cause must involve the gut."* — excludes nothing. Useless.
- ✗ *"The cause is likely bacterial."* — a guess about the answer, not a constraint on it.
- ✓ *"The cause must still be active during a period when the suspected external trigger is absent
  [src: symptom log, the fasted days]."* — this deletes every mechanism that depends solely on that
  trigger being present.
- ✓ *"The cause must post-date the year-0 antibiotic course, OR pre-date it and explain why it only became
  symptomatic afterwards."* — forces every candidate to account for the timing rather than ignore it.

## What to produce

### `## Must-fit constraints`

Each line: **the constraint, phrased as "the cause must… / cannot…"** + **the source that establishes it** +
**how strongly it binds**.

Strength — say which of these it is, in plain words (do not use bare letter codes):
- **hard** — an established fact makes the opposite impossible. This one can delete a candidate on its own.
- **strong** — very likely true; a candidate violating it needs an explicit explanation to survive.
- **soft** — a suggestive pattern; it can lower a candidate but must never delete one alone.

**Two constraint types are mandatory. Harvest them explicitly — they are usually the most discriminating
lines in the file.**

**1. The onset / perturbation constraint.** What perturbed the system into this state, and what was already
true before the first symptom? Phrase it so a candidate must account for the timing.

Note what makes this powerful: it is a *hole* in the story that every candidate must fill, not a fact that
flatters one of them.

**2. The survival-explanation constraint.** Whatever this is, it has already survived everything that has
been thrown at it. List those pressures, then require the candidate to explain its own survival.

Beyond the two mandatory ones, harvest whatever else the hypothesis implies: what must be present, what must
be absent, what must have preceded what, what dose or exposure must have been reached, what must be true of
the person's response to treatment.

### `## Blind-spot constraints`

For **every** result you rely on — positive *and* negative — write what it covers and what it cannot see.

The sentence to write for each: **"<result> covers <X>; it cannot see <Y>; so a candidate that lives in <Y>
is not excluded by it."**

## Output shape

```markdown
## Must-fit constraints

### Onset / perturbation
- The cause must <…>, because <what happened when> [src: <file>, <date/locator>]. Strength: hard/strong/soft.
  Debt for any candidate that violates it: <what it would have to explain>.

### Survival explanation
- The cause must explain how it persisted through <list the pressures> [src: <file>]. Strength: <…>.
  Acceptable answer-shapes: <compartment not reached / regrows from reservoir / never the target / suppressed-and-rebounded>.

### Other must-fit constraints
- The cause must <…> [src: <…>]. Strength: <…>.
- The cause cannot <…> [src: <…>]. Strength: <…>.

## Blind-spot constraints
- <result> covers <what it saw>; it cannot see <what it did not>; so a candidate in <that space> is not excluded by it. [src: <…>]
```

## Done when

- Both sections are non-empty and every line carries a source.
- The onset constraint and the survival-explanation constraint are present — or one carries an explicit
  *"not applicable — <reason>"* (which is a real answer; e.g. an unknown onset date should be written as
  "onset unknown", never guessed).
- Every constraint passes the deletion test above. If a line could not delete any candidate, it does not
  belong here.
- Every result the hypothesis leans on has a blind-spot line. Silence about a test's aperture is the failure
  mode this section exists to prevent.

**Artifact:** `constraints-<Hn>.md`.
