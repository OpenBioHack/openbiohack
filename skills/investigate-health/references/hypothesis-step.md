# Hypothesis step — investigate-health (validated mechanic)

The missing middle of the pipeline: turns the Step-4 inventory + the person's data, timeline,
and treatment history into a **set of competing, testable, differentiated hypotheses plus a
discrimination plan.** Sits between Step 4 (Inventory) and Step 5 (Cross-check); feeds Step 5.5
(cheap observational splits) and Step 6 (interventional splits / the on-off-on trials).

Framing anchor: `root-cause-research/00-FRAMING-LOCKED.md`. This is an **inquiry engine, not a
diagnosis engine** — the goal is not the best explanation, it's the best-designed *contest
between explanations*, because the differences between competing testable hypotheses are what
turn "we don't know" into "here's the test that tells us." Truth is what's left standing after
cheap discriminating tests kill the rest (Chamberlin's multiple working hypotheses + Platt's
strong inference).

The mechanic below was tested on a real case and rated by a *blind* structural judge (no
knowledge of any expected answer): genuinely diverse-and-differentiated, 8/10 diversity, 8/10
discrimination-plan quality. The four refinements marked **[R1]–[R4]** are the specific
weaknesses that blind test surfaced — they are part of the spec, not optional.

## Inputs
- The Step-4 shared-node inventory (the addressable candidates + the complete table).
- The person's findings and symptoms (Step 1), and the **timeline of events/exposures**.
- **Treatment-response history** (what was tried, what helped, what didn't) — fed as ordinary
  data among the rest, never flagged as pointing at an answer.
- The Step-3 mechanism graphs — used to derive each hypothesis's *signature* and to check that
  a proposed mechanism has a real path. A resource, not the engine.

## The mechanic

**1. Three-bucket sort on the timeline.** Sort the factors into: (a) standing vulnerabilities
(born-with / constitutional); (b) what flipped the switch — events preceding symptom onset;
(c) what's keeping it going now — currently active drivers. Note (c) usually grows out of (a).
This is the grounding; the timeline is also one of only two real n=1 confirmation tools.

**2. Generate by contrast (the diversity engine).** Write the single most conventional/modal
explanation first. THEN deliberately construct the strongest **rivals** — each must explain the
same load-bearing findings through a genuinely *different* underlying mechanism (a different lead
driver, or a different structure: one-process-driving-many / several-parallel / a-chain). Push
for different mechanisms, not relabels. Aim for 3–5. *(Naively asking for "several hypotheses"
collapses to variants of the modal one — building rivals by contrast is what forces real
diversity, and the blind test confirmed it does.)*

**3. Per-hypothesis bar.** Each hypothesis must:
- account for the **load-bearing** findings, and **explicitly name which findings it does not
  explain and why** (incidental? noise?) — "explains everything" is overfitting, not a virtue;
- rest on a believable step-by-step mechanism (each link real — check against the graphs);
- be as simple as it can be **but no simpler** — do not collapse genuinely separate things to
  force tidiness;
- note whether it's something one could act on;
- **[R3] over-fit flag:** if a single mechanism is stretched to resolve *every* tension at once,
  flag it — "explains everything risks predicting nothing." It stays only if it's still testable.

**4. Signature for each hypothesis.** If this story is true: (i) what *other* symptoms would tend
to be present → become **interview questions**; (ii) what specific **test results** would show;
(iii) could it be turned off as a reversible **trial**, and what response would be expected.
Derive from the graphs + `/research`. A hypothesis without its signature is untestable and
worthless here.

**5. Discrimination plan.** Lay the signatures side by side; find where hypotheses predict
*different* things. Each difference is a discriminator (question / test / trial that some pass
and others fail). Rank by **split-power × cheap/fast/safe** — cheap observational splits first,
then tests, then on-off-on trials. **[R4]** Label each discriminator's *real* cost honestly:
don't call a read "cheap" if its load-bearing half isn't a standard assay, and don't count
already-known data as new information. Mark non-splitters (resolvers, safety items, data-cleanup)
as such — they're fine, just not discriminators.

*(No dedup here — deliberately. This step is **generative**; collapsing near-identical
hypotheses is premature. If two hypotheses are hard to tell apart, that's fine — the
cross-check (Step 5) and interview (Step 5.5) are the selection stages that discriminate or
merge them against real data. Over-collapsing at generation risks killing a rival the data
could actually have separated. The blind-test over-collapse — fusing a mast-cell hub with
glucocorticoid-resistance even though tryptase/antihistamine would split them — is exactly why
collapsing belongs downstream, not here.)*

**6. Completeness — [R2].** Two sweeps before output:
- **No orphan findings:** every load-bearing finding must be explained by ≥1 hypothesis. A
  finding no hypothesis touches is a flag — open a hypothesis for it. (In the blind test, a high
  B12 finding silently fell out — and it pointed at the missing class below.)
- **Missing mechanism classes, including must-not-miss:** sweep for whole classes of cause no
  hypothesis represents — especially dangerous ones (neoplastic/clonal, structural, autoimmune)
  where being wrong and silent does real harm. Add the strand or the safety must-exclude even if
  it isn't a "hub." (The blind test missed clonal/neoplastic eosinophilia on a textbook trigger.)

## Confirmation discipline
Mark which discriminators merely *narrow* (observational, suggestive) vs which actually *prove*
at n=1: only **timing** (preceded onset, sensible lag) and the **on-off-on test** (remove →
fades, restore → returns) give real individual causal proof. Drive the survivors toward those.

## Output
Not a ranked answer. **The competing hypothesis set + the ranked discrimination plan** (the
cheapest questions/tests that would *eliminate* members) + the parallel safety must-excludes,
held in parallel. Each new result kills losers; regenerate the survivors' rivals; repeat
(Step 8). The cheap observational splits go to the interview (5.5); the trials go to the
prioritizer (6) — whose "discriminating power" axis this set is what finally feeds.

## Integration into SKILL.md
- New step between Step 4 (Inventory) and Step 5 (Cross-check). Patient context legitimately
  enters here (interpretive stage) — generation (3) and enumeration (4) stayed blind/neutral.
- Step 5 (Cross-check) is rewired: it cross-checks *the hypothesis set* against the data, rather
  than a single working hypothesis.
- Step 5.5 (Interview) and Step 6 (Prioritize) are the discrimination machinery this step feeds.
- Neutrality at this stage = no named candidate, no answer-shape, treatment-response fed flat.
  The completeness and over-fit checks are the guardrails; a blind structural judge on
  the output is the eval. Discrimination/selection (including collapsing near-identical
  hypotheses) is deliberately deferred to Step 5/5.5 — this step only generates.

## Eval cases to add
- `20-generate-by-contrast`: fixture where the modal story is obvious — PASS if the set contains
  ≥3 mechanistically distinct rivals (blind judge ≥7/10 diversity), FAIL if they're relabels.
- `21-no-orphans`: a fixture with a finding only one obscure mechanism explains — PASS if a
  hypothesis covers it, FAIL if it's dropped. [R2]
- `23-must-not-miss`: a fixture with a textbook dangerous-class trigger — PASS if the safety
  strand is raised. [R2]
- `24-overfit-flag`: a hypothesis using one mechanism to explain every tension — PASS if flagged. [R3]
