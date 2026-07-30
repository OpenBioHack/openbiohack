---
name: practitioner-claim
version: 1.0.0
applies-to-claim-class: practitioner-claim
---

# Practitioner-claim rubric

Formalises the 4-axis test from investigate-health/SKILL.md §"Practitioner-
written claims are evaluated on what's written, not on credential". Used by
the judge council for any practitioner-sourced claim that is load-bearing
for a T2+ candidate.

## Axes

### Axis 1 — direct-evidence support

**Definition.** Is each claim traceable to a measurement, test result, exam
finding, or observation cited in the same document, or is it inferred from
absent or unrelated data? A letter saying "elevated cortisol on DUTCH
[value: 245 ng/mg]" is supported; a letter saying "your adrenals are
stressed" with no underlying data is not.

**Scoring.**

- **1 (fail):** Conclusion stated without underlying data in the same
  document, or supported only by data that doesn't connect to the
  conclusion's mechanism.
- **2 (pass-with-caveat):** Conclusion has some supporting data in the
  document, but the data is partial or indirect.
- **3 (pass):** Conclusion is directly traceable to a measurement, exam
  finding, or observation cited verbatim in the same document.

### Axis 2 — within-scope-of-methods

**Definition.** Is the claim within what the practitioner's actual
examination or testing could legitimately conclude? A balance assessment can
yield observational vestibular findings; a balance assessment cannot
diagnose "cerebellar dysfunction" without the neurological exam that
diagnosis requires (cerebellar function tests, gait analysis, finger-nose,
heel-shin, Romberg).

**Scoring.**

- **1 (fail):** Conclusion requires methods the practitioner did not perform
  (regardless of their credentials or training).
- **2 (pass-with-caveat):** Conclusion is at the edge of what the methods
  used can support; reasonable but stretching.
- **3 (pass):** Conclusion sits squarely within what the methods used can
  legitimately conclude.

### Axis 3 — linguistic-accuracy

**Definition.** Is the medical or mechanistic language used precisely, or
as catch-all phrasing? "Mitochondrial uncoupling driven by elevated UCP3
expression" is precise; "your nervous system is in fight-or-flight" used as
a cover-all for any chronic symptom is not. Imprecise language signals
imprecise underlying reasoning.

**Scoring.**

- **1 (fail):** Catch-all phrasing where specific mechanisms should be
  named; jargon used to dress up vague claims.
- **2 (pass-with-caveat):** Mostly precise language with one or two slips.
- **3 (pass):** Specific mechanisms named with specific pathways throughout.

### Axis 4 — logical-coherence

**Definition.** Given the evidence the document itself cites, do the
conclusions follow? Are there obvious gaps the document papered over (a
finding mentioned then ignored; a contradicting result not addressed)?

**Scoring.**

- **1 (fail):** Conclusions don't follow from the cited evidence, or
  important contradicting evidence in the same document is ignored.
- **2 (pass-with-caveat):** Conclusions mostly follow but with a notable
  inferential leap or unaddressed gap.
- **3 (pass):** Conclusions follow cleanly from the cited evidence; gaps
  acknowledged where present.

## Tier ceilings on axis failure

| Axes failing (score 1) | Tier ceiling |
|---|---|
| 0 | No ceiling — weight at evidence strength |
| 1 | Downgrade one tier from the evidence-supported strength |
| 2 | **T3 maximum** |
| 3+ | **T4 maximum** (temporal-correlation only — practitioner observation noted, conclusion not weighted) |

## Eval set

### Case 1 — clean pass (all axes 3)

**Primary source (verbatim).** "Patient's morning cortisol on DUTCH testing
was 245 ng/mg (reference 91-217). Free cortisol AUC over 24h was 1.4×
upper reference. Pattern of elevated morning + flattened diurnal slope is
consistent with sustained HPA-axis activation. Recommend stress-load
reduction trial 8 weeks then re-test."

**Expected scores.** Axis 1: 3 (direct measurement cited). Axis 2: 3 (DUTCH
testing legitimately yields cortisol values). Axis 3: 3 (mechanism named
precisely). Axis 4: 3 (conclusion follows from cited data).

**Expected verdict.** No ceiling. Weight at evidence strength (T2 — DUTCH
diurnal cortisol has published validity in matched populations).

### Case 2 — within-scope failure (Axis 2 fails)

**Primary source.** "Based on her balance-board assessment and history of
dizziness, I am diagnosing cerebellar dysfunction. Recommend cerebellar
rehabilitation protocol."

**Expected scores.** Axis 1: 1 (no underlying neuro exam data cited).
Axis 2: 1 (balance-board cannot diagnose cerebellar dysfunction — that
needs finger-nose, heel-shin, Romberg, gait analysis). Axis 3: 2
("cerebellar dysfunction" used as catch-all). Axis 4: 1 (conclusion doesn't
follow — diagnosis requires methods not used).

**Expected verdict.** 3 axes fail → **T4 cap**. Conclusion noted as
practitioner observation; cannot be weighted as a working diagnostic claim.

### Case 3 — catch-all language failure (Axis 3 fails)

**Primary source.** "Your nervous system is dysregulated and your gut is
leaky. Inflammation is driving all of this. We need to calm the nervous
system and heal the gut. Recommend grounding, vagal-tone work, glutamine."

**Expected scores.** Axis 1: 1 (no measurements cited). Axis 2: 2
(intervention category broadly within scope). Axis 3: 1 (every term is
catch-all). Axis 4: 2 (loosely coherent).

**Expected verdict.** 2 axes fail → **T3 cap**.

### Case 4 — direct-evidence and coherence pass, linguistic precision slip (Axis 3 = 2)

**Primary source.** "Stool DNA panel: Akkermansia 0.02% (low; reference
>1%), F. prausnitzii 0.4% (low; reference 1-5%), SCFA-producer load
reduced overall. Pattern fits mucin-degrader/butyrate-producer depletion
seen in post-antibiotic dysbiosis. Suggest targeted prebiotic (PHGG 5g/d)
8 weeks then repeat panel."

**Expected scores.** Axis 1: 3. Axis 2: 3. Axis 3: 2 ("dysbiosis" is loose
but the surrounding language is precise). Axis 4: 3.

**Expected verdict.** 0 axes at score-1 → no ceiling. Weight at evidence
strength.

### Case 5 — logical-coherence failure (Axis 4 fails)

**Primary source.** "ANA negative. dsDNA negative. C3/C4 normal. ESR 8. CRP
<1. Patient meets clinical criteria for lupus and we will initiate
hydroxychloroquine."

**Expected scores.** Axis 1: 3 (data cited). Axis 2: 3 (within rheumatology
scope). Axis 3: 3 (precise terminology). Axis 4: 1 (cited evidence is
entirely negative; conclusion contradicts the data; clinical criteria not
itemised).

**Expected verdict.** 1 axis fails → downgrade one tier from
evidence-supported strength.

### Case 6 — partial-evidence + partial-coherence (Axes 1 and 4 each = 2)

**Primary source.** "Patient reports fatigue, brain fog, intermittent
joint pain. CRP slightly elevated at 6 mg/L. Likely chronic low-grade
inflammation, recommend anti-inflammatory diet trial."

**Expected scores.** Axis 1: 2 (one supporting datum, mostly symptom
report). Axis 2: 3. Axis 3: 2. Axis 4: 2.

**Expected verdict.** 0 axes at score-1 → no ceiling, but evidence-supported
strength is itself low (single mildly-elevated marker) — claim weights at
T3.

## Change-log

- **1.0.0** (2026-06-09) — Initial rubric. Author Pass 1 + adversarial
  Pass 2 (3 breakers attempted: practitioner-with-elite-credentials boundary
  case, functional-medicine-but-with-data case, evidence-cited-but-from-
  unvalidated-test case) + judge Pass 3 (no breaker survived; rubric
  shipped). Derived from investigate-health/SKILL.md Step 5 cross-check
  practitioner-claim language.
