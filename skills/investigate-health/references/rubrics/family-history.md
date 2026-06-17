---
name: family-history
version: 1.0.0
applies-to-claim-class: family-history
---

# Family-history rubric

Companion to the worked-example degree-of-relation table in SKILL.md
register §"Every fact gets verified, then weighted".

## Axes

### Axis 1 — degree of relation

**Definition.** Is the relation classified correctly per the worked-example
table?

- **1:** Misclassified (e.g. paternal grandmother called 1st-degree).
- **2:** Classified correctly but no degree explicitly stated in ledger.
- **3:** Classified correctly with degree explicit + cited table row.

### Axis 2 — condition heritability

**Definition.** Is the condition's heritability quantified at the degree
named (sibling-recurrence-risk-ratio λs where published; or condition-
specific lift estimates from published cohorts)? Without this, "family
history matters" is unweighted.

- **1:** Heritability quoted from memory / round number, no citation.
- **2:** Heritability cited but population mismatch.
- **3:** Heritability cited with population-matched cohort.

### Axis 3 — source of family-history report

**Definition.** Is the family-history report a medical record (formal
diagnosis with records), a verified family-told story (multiple relatives
confirm), or a single patient-report retelling? Mis-remembered family
diagnoses are common.

- **1:** Single patient-report retelling of a relative's condition; no
  cross-check.
- **2:** Patient-report consistent with at least one other family member.
- **3:** Medical record or formal diagnosis available.

### Axis 4 — recency

**Definition.** When was the relative diagnosed, and is the diagnostic
category still the same now? "Schizophrenia" diagnosed in 1965 may not map
cleanly to DSM-5 schizophrenia.

- **1:** Diagnosis is decades old AND the category has shifted (e.g.
  pre-DSM-III ADHD).
- **2:** Recent enough OR category stable.
- **3:** Recent diagnosis with stable category.

### Axis 5 — age-of-onset

**Definition.** Is the age-of-onset noted, and does it matter for the
heritability estimate (early-onset cancers carry higher familial risk
than late-onset; early-onset Alzheimer's vs late-onset is the canonical
example)?

- **1:** Age-of-onset unknown but matters for the heritability estimate.
- **2:** Age-of-onset known, applied loosely.
- **3:** Age-of-onset known and the heritability estimate is age-stratified.

## Tier ceilings on axis failure

| Axes failing | Tier ceiling |
|---|---|
| 0 | No ceiling |
| 1 | Downgrade one tier |
| 2 | T3 |
| 3+ | T4 |

## Eval set

### Case 1 — paternal grandmother MS (the Case 02 eval case)

**Primary source.** "Paternal grandmother diagnosed with MS in her 50s."

**Expected scores.** Axis 1: must be 3 (2nd-degree, table-cited). Axis 2:
needs Compston/Coles or equivalent citation → score depends on whether
orchestrator cites it. Axis 3: 1 (patient-report only). Axis 4: 2. Axis 5:
3 (50s = late onset, late onset has lower familial penetrance).

**Expected verdict.** Risk-lift to ~0.4-1% lifetime (NOT inflated to ~10%);
MRI retained on cost-of-miss grounds.

### Case 2 — sibling T1D, early onset

**Primary source.** "Brother diagnosed with type 1 diabetes at age 8.
Medical records available."

**Expected scores.** Axis 1: 3 (1st-degree). Axis 2: 3 if λs cited
(λs ~ 15 for T1D). Axis 3: 3 (records). Axis 4: 3. Axis 5: 3 (early
onset = higher familial risk).

**Expected verdict.** Lifetime T1D risk to subject ~5-7% vs ~0.4% pop. No
ceiling.

### Case 3 — cousin "had cancer"

**Primary source.** "Cousin had cancer, I think breast, sometime in her 40s."

**Expected scores.** Axis 1: 3 (3rd-degree). Axis 2: 1 (cancer type
unclear; "cancer" alone isn't quantifiable). Axis 3: 1 (single patient
report, hedged). Axis 4: 1 (age uncertain). Axis 5: 2.

**Expected verdict.** 3+ axes fail → **T4 cap**. Noted, not weighted.
Request: confirm cancer type + age + records before weighting.

### Case 4 — recent sibling formal IBD diagnosis

**Primary source.** "Sister diagnosed with Crohn's by colonoscopy + biopsy
2024, age 31."

**Expected scores.** All 3.

**Expected verdict.** No ceiling. Sibling λs for Crohn's ~17-25 (Halme
2006); subject lifetime risk ~5% vs ~0.3% pop.

### Case 5 — great-grandparent "dementia"

**Primary source.** "Great-grandfather had dementia, died around 1955 in
his 80s."

**Expected scores.** Axis 1: 3 (3rd-degree). Axis 2: 2 (dementia
heritability at 3rd-degree is small; quantifiable if APOE assumed). Axis 3:
1 (oral family history, 70 years old). Axis 4: 1 (pre-DSM dementia
category). Axis 5: 3 (late onset = lower familial penetrance).

**Expected verdict.** 2 axes fail → **T3 cap**.

## Change-log

- **1.0.0** (2026-06-09) — Initial. Pairs with the SKILL.md degree-of-
  relation worked-example table.
