---
name: study-tier
version: 1.0.0
applies-to-claim-class: study-tier
---

# Study-tier rubric

Applied to any published study cited as evidence for a load-bearing claim.

## Axes

### Axis 1 — study quality

**Definition.** Methodology grade. Meta-analyses of well-conducted RCTs > a
single well-conducted RCT > prospective cohort > retrospective cohort >
case-control > case series > case report > expert opinion.

- **1:** Case report, expert opinion, or undisclosed methodology.
- **2:** Cohort or case-control with limitations.
- **3:** RCT or meta-analysis with low risk of bias.

### Axis 2 — sample size

**Definition.** Is N large enough for the effect-size claimed?

- **1:** N too small to detect claimed effect with reasonable power.
- **2:** Adequately powered for the primary endpoint.
- **3:** Large multi-site cohort (n>1000) or pooled analysis.

### Axis 3 — replication status

**Definition.** Has the finding replicated in independent populations?

- **1:** Single study, not replicated.
- **2:** One or two replication attempts, mixed results.
- **3:** Replicated in multiple independent cohorts.

### Axis 4 — population match

**Definition.** Was the study population similar enough to this subject
(sex, age, ethnicity, comorbidities, disease severity) that the findings
apply?

- **1:** Population mismatch likely to invalidate transfer (e.g. male-only
  trial extrapolated to female subject for a sex-dimorphic condition).
- **2:** Partial match; transfer requires assumptions.
- **3:** Strong population match.

### Axis 5 — time-since-publication

**Definition.** Has the field moved since the study was published in a way
that would change the conclusion?

- **1:** Pre-1990 and field has moved substantially (e.g. Mithal 1988 on
  vitamin D cited in 2026 without acknowledging subsequent literature).
- **2:** >15 years old and partial movement.
- **3:** Current, OR older but conclusion still consistent with current
  literature.

## Tier ceilings on axis failure

| Axes failing | Tier ceiling |
|---|---|
| 0 | No ceiling |
| 1 | Downgrade one tier |
| 2 | T3 |
| 3+ | T4 |

## Eval set

### Case 1 — well-replicated RCT in matched population

**Primary source.** Cochrane meta-analysis of 14 RCTs, n=3,847, statin
therapy in primary-prevention CVD in adults 40-75 with elevated LDL.

**Expected scores.** All 3.

**Expected verdict.** T2 for primary-prevention claim in matched subject.

### Case 2 — outdated foundational study

**Primary source.** Mithal et al. 1988 on vitamin D supplementation,
n=42, single-site, no comparator. Cited in 2026 without acknowledgement
of subsequent literature.

**Expected scores.** Axis 1: 1. Axis 2: 1. Axis 3: 1 (superseded). Axis
4: 2. Axis 5: 1.

**Expected verdict.** 4 axes fail → **T4 cap**. Cite contemporary
meta-analyses instead.

### Case 3 — mouse-model-only mechanism

**Primary source.** Single mouse study, n=24, showing TUDCA upregulates
ASBT.

**Expected scores.** Axis 1: 2. Axis 2: 1. Axis 3: 1. Axis 4: 1
(mouse → human). Axis 5: 2.

**Expected verdict.** 4 axes fail → **T4 cap** for human claim. Use as
mechanism hypothesis only.

### Case 4 — large registry cohort

**Primary source.** Swedish twin registry, n=29,000, lifetime MS risk in
1st-degree relatives.

**Expected scores.** Axis 1: 2 (registry, observational). Axis 2: 3.
Axis 3: 3 (replicated in Danish, UK registries). Axis 4: 3 (population
matched). Axis 5: 3.

**Expected verdict.** 0 axes fail → no ceiling.

### Case 5 — single small RCT in mismatched population

**Primary source.** RCT n=42, postmenopausal women, calcium supplementation
on bone density. Cited for 34-year-old male.

**Expected scores.** Axis 1: 3. Axis 2: 2. Axis 3: 2. Axis 4: 1
(population mismatch). Axis 5: 3.

**Expected verdict.** 1 axis fails → downgrade one tier.

## Change-log

- **1.0.0** (2026-06-09) — Initial.
