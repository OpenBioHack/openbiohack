### Step 5 — Cross-check

**Patience preamble.** This step has no time pressure. Cross-check is where
the v2 run lost the most ground by rushing. Take however long you need; the
cost of a wrong verdict here propagates through Step 6 and Step 7.

**Council dispatch for load-bearing practitioner claims.** When a
practitioner-written claim is load-bearing for a T2+ candidate, the
practitioner-claim rubric is applied via the **judge council** rather than
by the orchestrator inline. Three judges (skeptical / charitable / process-
focused — templates in `references/council/`) each receive: the primary
source verbatim (not a summary), the rubric file at
`references/rubrics/practitioner-claim.md`, and the specific claim to
evaluate. They have NOT seen the synthesis. Each judge is dispatched with its own stance
folded into its prompt (the register, flat-context, and cross-subject-memory guards are
injected by the driver via `references/register.md`; the per-judge stance lives here):

- **Skeptical judge** — has NOT seen the synthesis; inputs are the primary source(s)
  verbatim + the rubric + the specific claim; DEFAULT to "claim insufficient" unless the
  evidence forces otherwise.
- **Charitable judge** — has NOT seen the synthesis; DEFAULT to "claim plausible" if
  evidence is cited; give benefit-of-the-doubt where evidence is partial but pointing the
  right way; apply the same rubric.
- **Process-focused judge** — has NOT seen the synthesis; DEFAULT to evaluating whether the
  rubric was applied correctly, not whether the claim feels right; flag rubric-design
  ambiguities.

Aggregation per
`references/council/aggregation-rule.md`: 3-of-3 agree → confident verdict;
2-of-3 → verdict + `disagreement-flag`; 1-of-3 or all-different → escalate
to human, do NOT auto-resolve. Single-judge verification is acceptable for
practitioner claims below the T2-load-bearing threshold.

For every hypothesis in the set from Step 4.5, look at the existing data and ask:
what supports this, what contradicts this, what is silent on this? The aim is to move each
hypothesis on evidence — strengthen, weaken, or break it — not to declare one the answer; convergence
happens through the discriminators over time, not by picking here.

For each hypothesis, produce a short note containing:

- **Supporting evidence:** the specific lab values, history items, or self-reported
  episodes that fit. With source IDs.
- **Contradicting evidence:** the specific items that don't fit. With source IDs.
- **Silent / not yet checked:** what we don't have data on that would matter.

For each piece of evidence, give an explicit verdict: does it *fit*, *strengthen*,
*weaken*, or *break* the candidate? A finding filed without a verdict is just sitting next
to the model, not updating it. And state plainly what each claim rests on — "what IS the
evidence for this, specifically?" — so every piece carries its basis, not just its
conclusion.

One trap to watch here: a measured level is not the same as the thing being used. A high
value can mean it isn't being taken up, not that there's plenty. Read levels as functional
states, not just numbers.

**Estimate the strength, don't just judge the direction.** A *fit / strengthen / weaken /
break* verdict gives a **direction**; it does not say **how much**. For every factor that
is going to weight a hypothesis, raise a flag, or steer a test, also estimate its
**magnitude** — how far it should actually move the picture — and do so *before* the factor
is allowed to carry weight. This is the active form of the register's verify-then-weight
rule: run it here as a procedure with an output, not as a remembered habit.

For each load-bearing factor:

- **Quantify the lift, honestly.** State the base rate and the actual increment the factor
  confers — the real number where one exists (*"a 2nd-degree relative with this condition
  moves lifetime risk from ~X% to ~Y%"*), or an explicit *"no usable number, and here is
  why"* where it doesn't. A factor asserted to "matter" without a magnitude has been
  *noticed*, not yet *weighed*. Resist both failure modes equally: inventing false
  precision, and retreating to "it's complex" to avoid estimating at all. Where the honest
  estimate is a wide range, give the range and name what would narrow it — knowing the
  *shape* of the uncertainty is itself part of the output.

- **Triangulate to the most direct evidence we already hold.** Before settling the
  magnitude, ask: *what is the most direct evidence available for this factor, and have we
  used it?* A factor is often first raised in a weak form — a family-history heuristic, a
  practitioner's interpretation, a proxy assay — while a stronger, more direct source sits
  in hand, unread. Go to it: the person's own genome for a genetic or heritable-risk
  factor; the standard or direct measure for a proxy value (a serum level beside a
  urine-metabolite proxy); the actual record for a reported trial or exposure. These grades
  are not interchangeable — a direct measurement, a proxy, a third party's interpretation,
  and a population heuristic sit at different strengths, and a factor must be weighed at the
  strength of its *best available* grounding, never at the convenience of how it first
  arrived. (The genome is a standing resource for *any* heritable-risk question, not only
  the mechanism pathways of Step 2's genetics query — consult it whenever a heritable
  possibility is raised.) Hold one nuance: the "direct" source is often itself partial — a
  single consumer-chip tag SNP carries ancestry and coverage caveats, a single timepoint is
  not a trend. Report what it does and does not settle, not just its headline.

- **Refine, then weight.** Combine the base-rate lift with what the direct data actually
  says, and output a *refined* strength for the factor — a calibrated weight, its tier, and
  what it rests on — or, where the data in hand cannot settle it, the single cheapest test
  or question that would. Triangulation at n=1 usually *narrows* uncertainty rather than
  removing it; say where it lands and how wide it remains. A factor that can be grounded
  only as a heuristic or an interpretation is held at that low strength and flagged as
  needing direct grounding — never laundered upward into evidence by repetition or by a
  confident downstream sentence.

This applies with full force to **safety flags**. A *"consider excluding X"* raised on a
weak heuristic — a distant relative's diagnosis, a non-specific sign — does not earn a test
recommendation until it has been quantified and triangulated against what we already hold.
This is not a licence to dismiss low-probability dangers: genuinely consequential ones are
surfaced regardless of likelihood (Step 7). It is that the *strength* of the flag — and
therefore the urgency and the kind of test it justifies — must track the actual evidence. A
grandparent's condition plus an unread genome is a different weight from the same history
plus a risk-allele read, and the recommendation moves with it.

*Output of this pass (added to the per-candidate note):* for each load-bearing factor — its
base-rate lift, the most-direct source actually consulted (and that source's own limits),
the resulting calibrated weight and tier, and any cheap discriminator that would sharpen it.

Two more checks, both common failure points:

- **Shape-fit, not just symptom-list match.** A candidate that matches the *list* of
  symptoms doesn't yet match the *shape*: distribution (where on the body, which systems),
  severity, episode pattern (episodic vs persistent, mild vs severe), time course, and
  whether it locks to a trigger. Worked example: a classic food allergy shows up as a generalised,
  often severe reaction within hours of the food. A mild, local, persistent finding with no clear
  meal-time link technically ticks the same boxes on a symptom list, but the shape — local not
  generalised, mild not severe, persistent not episodic, not time-locked — is wrong, and shape is
  what decides it. Same list, wrong
  shape, doesn't fit.
- **Absence of the *typical* presentation does not weaken a mechanism that can present in
  other forms.** Shape-fit cuts both ways and is easy to misuse. A mechanism whose textbook
  presentation is one thing **may also present** in localised, partial, atypical, or
  non-canonical forms; the classic presentation being absent is *not* evidence the mechanism
  is absent — it only rules out the classic form. Before shape-fit is allowed to weaken a
  candidate, the comparison must be against the mechanism's *full known range* of
  presentations — including the rare and localised ones, drawn from edge-of-practice
  sources, not only its most common textbook form. Weaken a candidate only when its
  presentation fits *none* of the forms the mechanism could take, not merely when it misses
  the modal one.
- **Reproducible reported reaction is signal, not noise.** When a clean theory requires
  explaining away something the person has reported repeatedly and consistently — a food
  trigger, a relief, a pattern they're sure of — the theory is what gets downgraded, not
  the reaction. Example: if the person says "every time I eat X, Y happens within an
  hour," and the working hypothesis says X shouldn't matter, the working hypothesis is the
  weaker piece, not their report. Build the picture around the reproducible report; don't
  subordinate it to a tidier story.
- **Visual symptoms need visual evidence.** For any symptom that can be photographed —
  a rash, lesion, swelling, redness, the way urine or stool looks, the colour or coating
  of the tongue — a written description on its own isn't enough to push a candidate
  above "mechanistically plausible" (T3). The shape of a rash often discriminates more
  sharply than any symptom list does; the photo is what lets the shape do that work.
  Worked example: a rash carried for days under one working frame on the strength of a
  written description can be overturned by the first photo — when the shape turns out to
  show, say, lacy blanching redness with no papules and an unexpected body distribution
  that the frame never predicted. If no photo exists
  for a visual symptom, flag it as a required data gap and keep any candidate whose tier
  would depend on the shape of the rash or lesion held at T3 or below until the photo is
  in `extracted/`.

- **Practitioner-written claims are evaluated on what's written, not on
  credential.** Anything authored by a third party in a subject's records (GP
  letters, specialist reports, functional-medicine letters, retreat reports) is
  evaluated on four axes before being given weight; authority-based pre-grading
  ("specialist said it" or "she's just a nutritionist") is not allowed — sloppy
  reasoning happens at every credential level and rigorous reasoning happens at
  every credential level. (1) **Direct evidence support** — is each claim
  traceable to a measurement, test result, exam finding, or observation cited in
  the same document, or is it inferred from absent or unrelated data? A letter
  that says "elevated cortisol on DUTCH" with the actual value alongside differs
  from a letter that says "your adrenals are stressed" with no underlying data.
  (2) **Within scope of methods used** — is the claim within what the
  practitioner's actual examination or testing could legitimately conclude? A
  practitioner who did a balance assessment can describe vestibular findings
  observationally; the same practitioner who did NOT perform a neurological
  exam (cerebellar function tests, gait analysis, finger-nose, heel-shin,
  Romberg) cannot competently claim "cerebellar dysfunction" — that conclusion
  requires methods they did not use, regardless of their training.
  (3) **Linguistic accuracy** — is the medical or mechanistic language used
  precisely, or as catch-all phrasing? Specific mechanisms named with specific
  pathways differ from "your nervous system is in fight-or-flight" used as a
  cover-all for any chronic symptom. Imprecise language is a signal the
  underlying reasoning is also imprecise. (4) **Logical coherence** — given the
  evidence the document itself cites, do the conclusions follow? Are there
  obvious gaps the document papered over? Claims that fail any axis are
  downgraded one tier; claims that fail two or more are capped at T3 regardless
  of source. Claims that pass all four can be weighted at the strength their
  underlying evidence supports. Any claim sourced from a practitioner-written
  document carries a `practitioner-claim-rubric` field in `step5-cross-check.md`
  with the four axes scored (pass / fail / N/A) and the resulting tier ceiling.
  Rubric definitions and eval sets live in
  `~/.claude/skills/investigate-health/references/rubrics/practitioner-claim.md`
  and (for T2+ load-bearing claims) are dispatched-applied via the judge
  council per "Council dispatch for load-bearing practitioner claims" above.

A source flagged for quality by the dispatched research agent (see "Parallel research
dispatch") can't push a candidate above the tier that its actual evidence quality
supports — flagged in, flagged out.

**Memory and prior-conclusion entries that say "X is ruled out" pass through
the same gate.** Before any cross-check downgrades or drops a candidate on
the basis of a memory entry or a prior-conclusions file saying X is ruled
out, the Q1-Q5 atypical-presentation gate from Step 3 is run and its result
recorded in the candidate's `ruled-out-gate-result` field. Memory is not a
shortcut around the gate. (See bootstrap step on memory-role separation —
memory's "frameworks RULED OUT" entries are prior synthesis output, not
ground truth.)

The same gate governs any *result used to move a candidate* — positive or
negative — not only a memory entry. Before a negative is allowed to lower a
candidate's tier, confirm the test's aperture actually covers that candidate
(register type (d)): right target, right compartment, adequate sensitivity at
the relevant magnitude, sampled when the process would be detectable; a
negative that falls outside the window is filed as "silent / not yet checked,"
never as contradicting evidence. And before a positive is allowed to *close* a
question — to mark a finding explained and stop the search on it — confirm the
test covered the whole of what could explain that finding, not only part;
whatever it did not measure stays open as type (d) regardless of the positive.
Either way, the aperture-closing test for the uncovered remainder is named for
Step 6.

The result is an updated tier for each candidate, and a clear list — per candidate — of
what's still ambiguous from existing data alone. That list feeds step 5.5.

*Output:* per-candidate evidence ledger, updated tiers, list of remaining ambiguities.

