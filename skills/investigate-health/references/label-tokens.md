# Diagnosis-label tokens

Maintained list of diagnosis-label tokens that trigger the
`investigate-health-label-density` hook check on synthesis-layer writes
(working-hypothesis.md, step2-mechanism-map.md, step5-cross-check.md,
step6-prioritize.md). Above the density threshold (default: 1 label per
200 words of body text, excluding `## Labels referenced` section), the
hook blocks the write and the synthesis agent must translate labels to
process descriptions before retry.

Tokens are matched case-insensitively as whole words. Comments and blank
lines are ignored. Hyphenated forms are matched as-written.

## Acronym labels

MCAS
NC-CAH
POTS
hEDS
EDS
IBS
SIBO
SIFO
IBD
GERD
PCOS
MTHFR
CFS
ME/CFS
PEM
PMDD
PMS
GAD
OCD
ADHD
PTSD
CPTSD
MDD
BPD
TBI
ALS
MS
RA
SLE
T1D
T2D
NAFLD
NASH
CKD
COPD
OSA
# GAS — REMOVED: whole-word match collides with the everyday gut term "gas" (intestinal/luminal gas),
# which is high-frequency in SIBO/gut investigations and would silently inflate label-density →
# false blocks. Group A Streptococcus is caught by its full name, which is not density-problematic.
MGUS
DIO
LBM
DOMS
HRV
TSH
TPO
TGAb
ANA
ANCA
CRP
ESR
LDL
HDL
ApoB
Lp(a)
HbA1c
TIBC
UIBC
DUTCH
# OAT — REMOVED: whole-word match collides with the food "oat"/"oat milk"; it is a test name
# (Organic Acids Test), not a diagnosis label, so it does not belong in the density list anyway.
GI-MAP
HTMA

## Named syndromes / conditions (full names)

mast cell activation syndrome
mast cell activation disorder
non-classical congenital adrenal hyperplasia
congenital adrenal hyperplasia
postural orthostatic tachycardia syndrome
hypermobile Ehlers-Danlos syndrome
Ehlers-Danlos syndrome
irritable bowel syndrome
small intestinal bacterial overgrowth
small intestinal fungal overgrowth
inflammatory bowel disease
Crohn's disease
ulcerative colitis
gastroesophageal reflux disease
polycystic ovary syndrome
chronic fatigue syndrome
myalgic encephalomyelitis
post-exertional malaise
premenstrual dysphoric disorder
premenstrual syndrome
generalized anxiety disorder
obsessive compulsive disorder
attention deficit hyperactivity disorder
post-traumatic stress disorder
complex post-traumatic stress disorder
major depressive disorder
borderline personality disorder
traumatic brain injury
amyotrophic lateral sclerosis
multiple sclerosis
rheumatoid arthritis
systemic lupus erythematosus
type 1 diabetes
type 2 diabetes
non-alcoholic fatty liver disease
chronic kidney disease
chronic obstructive pulmonary disease
obstructive sleep apnea
vestibular migraine
cervicogenic dizziness
benign paroxysmal positional vertigo
alpha-gal syndrome
histamine intolerance
DAO deficiency
leaky gut syndrome
adrenal fatigue
chronic Lyme
mold illness
CIRS
candida overgrowth
dysautonomia
Hashimoto's thyroiditis
Graves' disease
Sjögren's syndrome
fibromyalgia
endometriosis
adenomyosis
Malassezia folliculitis
seborrheic dermatitis
atopic dermatitis
psoriasis
urticaria
angioedema
chronic spontaneous urticaria

## Notes on maintenance

- When a new label triggers a false-positive block, add a more specific
  match here or add an exception note to the hook's logic.
- Acronyms shorter than 3 characters are NOT matched (too many
  false-positives — "MS" matches mass spec, "RA" matches retinoic acid in
  research-layer extracts). The hook only matches the 3+ char list above.
- The `## Labels referenced` section in any synthesis file is exempt
  from density counting — that's the safe place to enumerate labels for
  cross-reference.
