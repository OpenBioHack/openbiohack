---
name: lab-result
version: 1.0.0
applies-to-claim-class: lab-result
---

# Lab-result rubric

Applied to any claim resting on a lab value. The Vibrant within-sample
contradiction case from the v2 run motivated this — same panel had two
different reference ranges for the same analyte on adjacent rows; the
contradiction was silently smoothed in synthesis.

## Axes

### Axis 1 — vendor quality

**Definition.** Is the vendor's methodology validated and published, or
proprietary/black-box? CLIA-certified labs with peer-reviewed methods score
higher than direct-to-consumer panels with proprietary scoring.

- **1:** Vendor methodology undisclosed; no published validation.
- **2:** Partial validation (e.g. CLIA-certified but proprietary scoring).
- **3:** Methodology published; peer-reviewed validation in matched
  populations.

### Axis 2 — reference-range validity

**Definition.** Is the reference range derived from a population matched to
this subject (sex, age, ethnicity where relevant), and does it represent
"optimal" or "absence-of-disease"? "Normal" ranges built from sick
populations differ from optimal ranges built from healthy populations.

- **1:** Reference range not population-matched, or origin undisclosed.
- **2:** Reference range disclosed but partial population match.
- **3:** Reference range population-matched and origin published.

### Axis 3 — intra-vendor consistency

**Definition.** Within the same panel from the same vendor, are values for
the same analyte consistent across rows / pages? Adjacent-cell errors and
row-misalignment are common silent failures.

- **1:** Within-sample contradiction present and unaddressed.
- **2:** Possible within-sample inconsistency surfaced and flagged.
- **3:** Clean — same analyte same value across the panel.

### Axis 4 — sample-handling integrity

**Definition.** Was the sample handled per vendor protocol (fasting state,
time of day, temperature, hemolysis flag)? Out-of-protocol handling can
shift values substantially.

- **1:** Protocol breach known (non-fasting where fasting required, etc.).
- **2:** Protocol adherence partially documented or unclear.
- **3:** Protocol fully documented and adhered.

### Axis 5 — biological-vs-technical variation

**Definition.** Is the observed difference larger than the analyte's known
biological + technical CV? A 5% difference in a marker with 20% CV is
noise, not signal.

- **1:** Observed change is within or below known CV — likely noise.
- **2:** Observed change is ~1-2× CV — possible signal.
- **3:** Observed change is ≥3× CV — likely signal.

## Tier ceilings on axis failure

| Axes failing | Tier ceiling |
|---|---|
| 0 | No ceiling |
| 1 | Downgrade one tier |
| 2 | T3 maximum |
| 3+ | T4 maximum (the value is noted, not weighted) |

## Eval set

### Case 1 — Vibrant within-sample contradiction (Axis 3 fails)

**Primary source.** "Panel A row 14: zonulin 87 ng/mL (reference <45).
Panel A row 32: zonulin 41 ng/mL (reference <90). Same sample, same draw
date. No vendor note explaining the discrepancy."

**Expected scores.** Axis 1: 2 (Vibrant proprietary). Axis 2: 1
(reference range differs across rows — unclear which applies). Axis 3: 1
(within-sample contradiction). Axis 4: 3. Axis 5: N/A (single timepoint).

**Expected verdict.** 2 axes fail → **T3 cap**. Value noted as "vendor data
inconsistent — not weighted at face."

### Case 2 — clean NHS basic metabolic panel

**Primary source.** "Na 139 mmol/L (ref 135-145). K 4.1 (3.5-5.0). Cr 73
umol/L (60-110). Fasting glucose 5.2 (3.9-5.5)."

**Expected scores.** All 3. **Expected verdict.** No ceiling.

### Case 3 — out-of-protocol non-fasting glucose

**Primary source.** "Glucose 7.1 mmol/L. Note: sample drawn at 14:00, 2h
post-meal."

**Expected scores.** Axis 1: 3. Axis 2: 1 (fasting reference range applied
to non-fasting sample). Axis 3: 3. Axis 4: 1 (protocol breach). Axis 5:
N/A.

**Expected verdict.** 2 axes fail → **T3 cap**.

### Case 4 — within-CV "change" treated as signal

**Primary source.** "Ferritin moved from 178 to 192 over 6 weeks.
Trending up."

**Expected scores.** Axis 1: 3. Axis 2: 3. Axis 3: 3. Axis 4: 3. Axis 5:
1 (ferritin CV is ~10-15%; 14 ng/mL change on baseline 178 is 8% —
within noise).

**Expected verdict.** 1 axis fails → downgrade one tier.

### Case 5 — clean change well above CV

**Primary source.** "TSH 1.2 → 4.8 mIU/L over 8 weeks; reference 0.4-4.0.
Same lab, same time-of-day, same protocol."

**Expected scores.** All 3.

**Expected verdict.** No ceiling. T1 (direct measurement, change > biologic
+ technical CV).

## Change-log

- **1.0.0** (2026-06-09) — Initial. Motivated by Vibrant within-sample
  contradiction in v2 run.
