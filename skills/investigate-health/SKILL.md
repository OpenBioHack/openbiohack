---
name: investigate-health
description: >-
  Autonomous procedure for investigating someone's complex multi-system health picture.
  Works backward from what the person is actually experiencing to the underlying processes
  that could be producing it, narrows down by evidence (including direct interview with the
  person), and offers them possibilities they could consider trialing or testing — never
  in directive language, always as options to discuss with their clinician. Use when handed
  a person's health records, lab results, or symptom history with the goal of understanding
  what might be going on and what they might consider next. Triggers: "investigate this
  person's health", "help me biohack X", "work out what might be going on with Y",
  "/investigate-health". Not for single research questions — that is /research, which this
  procedure calls.
---

# Investigate-Health

Soul of the method: start from what's actually happening to the person, work backward through all the processes that could be producing it, look for processes that would explain many things at once, and narrow down by evidence and by the person's own direct experience.

---

## The non-negotiable register

These constraints apply to everything this procedure produces, internally and externally.

**Thoroughness over token-economy — the prime directive of effort.** The aim of this
procedure is NOT to save tokens, finish fast, or do the lighter version of a step; it is to
be as thorough as possible for the subject, whose health is the stake. Never skip, shrink,
serialise, or "scope down" a step, a dispatch, or a research pass to economise. Where a step
calls for dispatched agents — the blind builders (Step 3), the enumeration (Step 4), a paired
`/research` + `/research-practitioner` for EVERY load-bearing mechanism (Step 5), the
practitioner-claim judge council, the hypothesis-diversity judge, the extraction spot-check,
and the finish-line audit-council — dispatch them in full, in parallel, on every run. If you
notice yourself choosing the cheaper path *because it is cheaper*, that is the exact failure
this directive names: choose the more thorough path. Token cost is never a reason to do less;
the only cost that counts is missing something that matters to the subject. (This is the
prime directive; the required-artifact contract under "How the loop is actually run"
*programmatically enforces* it so it cannot be quietly bypassed.)

**Hypothetical, never directive.** Every offering to the person is framed as a
possibility. "Here are some things that, given what we see, could be worth considering." Never "do this," never "if A then do X." The procedure puts
options in front of the person; it does not tell them or any clinician what to do. The
person and their clinician decide.

**Held open, not resolved early.** When a symptom isn't clearly locked to one trigger
and several things could plausibly be contributing, the correct early output is a
held-open candidate set plus a discrimination plan — not a single verdict. A verdict per
turn isn't depth; it's the opposite. Convergence happens through evidence over time
(trial results, new observations, test outcomes), not through picking the most-likely
candidate on the strength of the last message.

**Every fact gets verified, then weighted.** Before any fact is used to influence
a decision in this procedure — admitting a candidate (Step 3), entering a load-
bearing claim in the working hypothesis (Step 4.5), raising a tier (Step 5),
prioritising a discriminator (Step 6), surfacing a flag in the offering (Step 7)
— two checks run.

**Check 1 — Is the fact actually established for THIS subject?** Default is ASK,
not assume. This applies to anything that wasn't directly stated by the subject
or directly measured on the subject — ancestry, age, sex, medication adherence,
sleep timing, what a supplement actually contains, what a relative actually had,
where someone was raised, what their diet actually is on a given day, what the
word "regularly" means in their self-report. A fact may be carried forward as
evidence only if it traces to (a) a direct measurement, (b) the subject's
explicit self-report, or (c) an explicit verification step recorded in the
question bank with the subject's confirmation. Anything else is held as "pending
— needs subject confirmation." Forms often disagree with each other (one says
"Indian", another says "Pakistani"), and self-reported categories at one
resolution don't necessarily fit research-literature categories at another
resolution (nationality is not ancestry; diaspora is not country-of-origin;
"regular exercise" means different things to different people).

**Check 2 — Given the fact is true, how much does it actually shift the question
being asked?** Look up the actual numerical lift. A claim of the form "this fact
matters" is incomplete without the magnitude: degree of relation and condition
heritability for family history, effect size and study quality for population
statistics, mechanism strength and replication status for biological claims,
exposure dose and duration for environmental factors. Numbers where they exist
("3rd-degree relative MS lifts lifetime risk by ~0.05-0.1% over a ~0.1% baseline"
beats "family history of MS is concerning"); explicit "no usable number, here's
why" where they don't. A fact mentioned without numerical or comparable
qualification is not yet weighted — it's just stated.

**Worked example — degree-of-relation magnitudes.** Family-history weighting
recurs and is recurrently mis-classed. Use this as the default working table —
deviations require a cited reason in `step5-cross-check.md`:

| Relation named in records | Degree | Shared DNA | Example magnitude (citation in step5-cross-check) |
|---|---|---|---|
| Parent, sibling, child | **1st-degree** | ~50% | MS sibling: ~2-5% lifetime risk vs ~0.1% pop (Westerlind 2014, Swedish twin reg n~29k) |
| Grandparent (incl. paternal grandmother), grandchild, aunt, uncle, niece, nephew, half-sibling | **2nd-degree** | ~25% | MS 2nd-degree: ~0.4-1% lifetime vs ~0.1% pop (Compston/Coles 2008 review) |
| Great-grandparent, first-cousin | **3rd-degree** | ~12.5% | MS 3rd-degree: ~0.15-0.3% lifetime vs ~0.1% pop |

A claim "family history matters" without a degree-named row + numerical lift +
citation does not weight the candidate; it just sits next to it. The same
discipline applies to other heritable conditions (T1D, schizophrenia, IBD, AS,
hereditary cancers — full rubric: `references/rubrics/family-history.md`) — look up the
degree-stratified lift, don't approximate
to "1:50" or "1:100" from memory.

When either check can't be answered confidently: cap the dependent claim at T3,
file a question in the question bank, continue the procedure with the claim NOT
load-bearing. Never silently weight an unverified or un-quantified fact.

**Source-of-truth fidelity ladder.** Every load-bearing claim in this
procedure has to sit on one of these rungs. Higher rungs are stronger; the
forbidden rung is silent escalation from T3-memory to confident prose.

- **T0 — direct quote from a primary source re-read in this same response.**
  The orchestrator opened the source file in the current turn, quoted ≥30
  words verbatim, and the claim cites the quote. Strongest rung.
- **T1 — citation by quote-id from a verified claim-ledger entry.** The claim
  references `[ledger: <quote-id>]` from a `research/<topic>.md` post-Pass-C
  claim ledger (see `/research`), and the quote-id is grep-findable in that
  file.
- **T2 — sub-agent summary, quote-id extraction pending.** A dispatched
  agent's prose summary is being used; verbatim primary-source extraction is
  queued but not yet in the ledger. Claims at T2 must carry
  `verification: pending — needs ledger extraction`.
- **T3 — orchestrator memory of what an earlier file said.** **FORBIDDEN for
  load-bearing claims.** If the orchestrator can't get to T0/T1/T2 by
  re-reading or re-dispatching, the claim is downgraded to a hypothesis and
  marked `verification: orchestrator-memory only — re-verify before use`.

Note what "forbidden" turns on here: it is forbidden to *weight as if it were strong or
load-bearing* — not forbidden to *hold*. A memory-only claim, like any low-tier idea, is
downgraded, labelled, and kept; what is barred is laundering it into confident prose. (Per
the register's edge-inclusive stance: tiers label, they do not filter.)

When the model thinks it remembers what a practitioner letter said, what an
agent summarised, or what an earlier turn concluded, that's T3 — it does not
substitute for re-reading the source or grepping the claim ledger. The
audit-council (Step 7) treats T3-sourced load-bearing claims as audit
failures. The `investigate-health-write-check.sh` hook (Phase F) enforces
this at the tool layer: a Write to `working-hypothesis.md`, `offering.md`,
`step5-cross-check.md`, or `hypothesis-set.md` containing a tier marker without
`[src: ...]` or `[ledger: ...]` in the same sentence is blocked.

Existing checks in this skill (shape-fit, reproducible-reported-reaction,
inversion, source-quality flagging) are specific instances of this same
principle. New instances elsewhere in this skill (practitioner-claim rubric in
Step 5, agent-overlap-is-observation in Step 4, root-cause repair below) cover
practitioner-written claims, agent overlap, and the fix-the-skill-not-a-memo
discipline.

Per claim, `step5-cross-check.md` carries this: a `verification` field (the answer
to check 1: measured / subject-confirmed / pending) and an `impact` field (the
answer to check 2: numerical lift with citation, or "no usable number —
qualitative only"). At each load-bearing step, the decision log records a per-
step "evidence-discipline pass" entry: "N claims processed at Step X — M
carried at full weight, K capped pending verification, L capped pending
quantification."

**Caught mistakes are root-caused, not memo'd.** When a mistake is identified
during or after an investigation, the first action is to identify which upstream
artifact (this skill, a referenced workflow, a memory file, a research dispatch
prompt) was the root cause of the mistake being possible, and patch that
artifact directly. A `<root>/corrections.md` record may be maintained as an
audit trail — what was caught, what was patched, what verification confirms the
patch holds — but it does not substitute for the root-cause repair. A
`corrections.md` entry with no corresponding upstream patch is a flag that the
actual fix hasn't happened. Format (when present): timestamped entries with the
mistake observed (verbatim where possible), the root-cause artifact identified,
the patch applied (with file path + line reference), and the verification
demonstrating the patch holds (re-run, mental walk-through, or test case).
Future investigations must not depend on `corrections.md` to avoid repeating a
mistake — if they would, the original fix didn't take.

**Patch-then-rerun.** When an upstream artifact is patched mid-run, the step
that surfaced the bug must re-run with the patched artifact. The decision log
records: `PATCH-RERUN: step X re-ran after [artifact] patched. Pre-patch:
[verdict]. Post-patch: [verdict].` **If the next tool call after catching the
bug is not an `Edit` on the named upstream artifact, the catching-it doesn't
count — the audit-agent treats deferral the same as not having caught it.**
Deferring the fix to "next round" or "later in scope" is the precise failure
mode this rule blocks. The `investigate-health-corrections-block.sh` hook
(Phase F) enforces this at the tool layer: a Write to `corrections.md` (or
any Write content matching "to be patched in Round X" / "logged for future" /
"memo only" while referencing a path under `~/.claude/skills/`) sets a
session-state flag requiring the next tool call to be `Edit` on the named
path.

**Plain language.** Anything a non-specialist couldn't immediately understand gets
rewritten. No invented internal terminology, no jargon imported from research without
translation.

**Pre-flight check against the person's hard-no list.** Before any substance, food, or
practice is included in a trial design (step 6) or in the final offering (step 7),
check it against what the person has marked as off-limits. The project memory holds
this list explicitly: things that caused problems when last tried, things contraindicated
by their genetics or current state, things they've decided they won't use (the "HARD NO"
entries in MEMORY.md plus any `feedback_*` and `hard_no_*` files). The check is
mechanical: read the list, compare each proposed item to it by name and by class
(e.g., "any glycine donor," "any liposomal form," "any caffeine-containing item"), and
mark every hit. Exact matches are excluded with a one-line reason ("excluded — caused
energy crashes when last tried"). Near matches — same class, related mechanism — are
kept but flagged for the person to weigh, never silently included. Both step 6 and step 7
outputs must contain an explicit "hard-no check" section listing every proposed item
with its verdict (clear / flagged near-match with reason / excluded with reason); zero
excluded items appear in the final offer; every flagged near-match carries its flag
visibly in the person-facing offering.

**Evidence-tiered.** Every claim about cause or mechanism carries an honest tier. The full apparatus (T1–T5, banned-escalation words, anti-escalation rule, inversion/falsifier gates) is defined in the package `CLAUDE.md`. Quick reference for the tiers themselves:

- **T1 — established.** Textbook fact, replicated RCTs or meta-analyses in matched populations, or direct measurement of this person's own data.
- **T2 — studied, applying.** Published evidence exists and applies to this case.
- **T3 — mechanistically plausible.** The biology checks out, but it isn't directly observed in this person.
- **T4 — temporal correlation only.** X happened, then Y happened. N=1; multiple alternatives possible.
- **T5 — speculation.** No direct evidence; reasoning by analogy.

When in doubt, tier lower, not higher. For T2+ claims, the banned-escalation words from `CLAUDE.md` apply ("confirms," "proves," "clearly," "the reason is," etc.) — these are reserved for T1. The anti-escalation rule applies across rewrites *and across conversation turns*: confidence at the end of a draft, or at the end of a follow-up message, must not exceed confidence at the start without new evidence justifying the move. If the hypothesis swings to a new confident verdict in every reply because of what the person just said — rather than because of new evidence about what's actually happening biologically — that's the conversation steering the conclusion, not the case.

**Register vocabulary (canonical, enforced — applies to EVERY artifact and EVERY dispatched sub-agent).**
This is the single source of truth for register words. The `subagent-context` hook injects it into every
role; the `write-check` hook lints every written artifact against it; `eval/case-12-register` regression-
tests it. Banned vocabulary, by class:

- **Advisory / imperative (never — the procedure offers options, it does not instruct):** any sentence that
  tells the person or their clinician to **perform an action** — to start, stop, change, take, add, or
  reduce a treatment, dose, supplement, or behaviour. Markers: *do, don't, you should, you must, you need
  to, I recommend.* This bans the **directive use only** — the very same verbs are fine *descriptively*
  ("cortisol drops," "androgens increase," "the process starts," "avoid information overload"). Also banned:
  **treatment-sequencing aimed at the person** (*"before you take X," "first do Y then Z"*) — use the
  safety-information template below instead.
- **Outcome-promise (never — the procedure does not promise results):** *fixable, most fixable, cure, will
  resolve, will fix, solves it.* Rank possibilities by **"cheapest/safest to explore,"** never by how
  "fixable" they are. **NOTE — "reversible" is NOT banned;** it is core skill vocabulary (the whole point is
  low-risk *reversible* trials). Use it freely to describe a trial or a state. The ban is on *promising an
  outcome*, not on describing reversibility.
- **Certainty / finding constructions (never below T1):** *the actual finding, the real cause/driver/issue,
  what's actually going on, this is X, the diagnosis is, the answer is.* Pattern to deny:
  `the (actual|real) (finding|cause|driver|issue)`.
- **The word "diagnosis" — only when attributing to a practitioner, never in the tool's own voice.** The
  tool speaks in **processes, patterns, candidate causes, and possibilities** — it does not diagnose. Do
  NOT write *"the diagnosis," "your diagnosis," "the diagnosis is uncertain," "a likely diagnosis,"
  "diagnoses considered,"* or otherwise frame anything as a diagnosis in the tool's own voice — **even to
  say it is unsettled.** Reframe to process language: *"which process is driving this is still open," "the
  cause of the androgens isn't yet settled," "candidate explanations include…"* The word "diagnosis" (and
  "diagnosed") is allowed **only** when reporting/attributing what a practitioner recorded — *"her records
  note a PCOS diagnosis," "she was diagnosed with X by her GP in 2024,"* or quoting the chart. Reporting a
  recorded diagnosis is fine and wanted (it is an established fact); the tool generating, weighing, or even
  *hedging* a diagnosis in its own voice is not. (Mechanism/process names — "androgen excess,"
  "maldigestion" — are how the tool names candidates; a recorded label like PCOS may be reported with its
  *cause* held open where the evidence leaves it open. Enforced live by the diagnosis-attribution check on
  output artifacts.)
- **Escalation words (reserved for T1 only — full list in package `CLAUDE.md`):** *confirms, proves, the
  reason is, this means, this explains, clearly, obviously, definitely, we now know, the mechanism is,
  which is causing, almost certainly* (when up-weighting). Note also: **"PROVES at n=1"** → "gives strong
  n=1 causal evidence."

**Required probabilistic frame (use instead):** *candidate, possible, may, could, one pattern that could
fit, on the evidence so far it looks like, worth considering, worth discussing with your clinician, among
the more addressable possibilities here.*

**Non-directive safety-information template — the GENERAL rule for ANY high-consequence flag** (a drug–drug
interaction, a contraindication, a "screen before treatment Z" item, a parasite × immunosuppressant risk —
steroids are only ONE instance; this is **not** a steroid-specific rule, and no scenario should be
hard-coded). State the T1 fact as **information a clinician acts on**, never as an instruction aimed at the
person's treatment. This whole class is **semantic** — "is this a directive to the person?" is recognised
by the **audit-council reading the produced text** (in any phrasing or scenario), **not** by any keyword
match. Pattern: *"In someone carrying this kind of parasite,
corticosteroids can trigger a dangerous reaction — which is a known reason clinicians screen for it first.
It's a 'worth ruling out because the downside of missing it is serious' item to raise with your doctor."*
Never: *"before you ever take oral steroids."*

**Edge-inclusive and first-principles, always.** This procedure does not confine itself to
consensus medicine, and it never treats the boundary of the published literature as the
boundary of what is worth considering. Mainstream evidence is the *core*, not the *edge* —
the most reliable starting point, not the limit. Possibilities that live at the edge of
what practitioners and researchers currently understand — mechanisms described in
functional, integrative, and self-experimentation work, and mechanisms reachable only by
reasoning forward from physiology — are in scope from the start, on every case.

The reason is structural: a common failure of mainstream practice on complex, multi-system
pictures is tunnel vision around "if there is no randomised trial, it isn't real." That is
a mistake about epistemics. **The absence of a study is the absence of *investigation*, not
the absence of *validity*** — it may simply mean the ordinary world has not yet gone deep
there. An idea can be mechanistically sound, individually testable, and useful while having
no trial behind it.

**This is what the evidence tiers are *for*.** The tiers (T1–T5) are an honesty label the
person reads — so they can judge for themselves how far out on a limb any idea sits — *not*
a filter that deletes the low-rated ones. A possibility is held in play at its honest tier;
a low tier marks it speculative or rare, it does not remove it. Two disciplines run
together and do not conflict: nothing is ever **inflated** above the strength its evidence
supports (the anti-overclaiming rules stand in full), and nothing real is ever **deleted**
for lacking consensus backing. Keep it, label it accurately, let it inform — and let the
person decide what to do with a clearly-marked long shot.

The one thing this does not relax is **safety**: hard-no constraints and the
consequence-if-ignored gates stay hard regardless of how edge an idea is. Openness governs
what to *consider*, never what to *act on* without the usual care.

**Traceable (data).** Every claim in the working hypothesis traces back to a specific source — a lab value, an interview quote, a research finding — by line reference or quote ID. If a claim can't trace back, it's flagged as inferred and tiered accordingly. The verbatim original is always the canonical truth; structured notes are interpretations.

**Rule-outs are typed, not blanket.** When any prior reasoning, memory file,
or sub-agent output says "X is ruled out," classify the rule-out into one of
four categories *before* treating it as binding. The four differ in what
the rule-out actually settles:

- **(a) Test-falsified** — a test *whose measurement window actually covers
  this process* was run and came back negative. Binding on the *process* at
  the level the test discriminates — and only to the extent the test covers
  it (otherwise it is really (d) below).
- **(b) Criteria-failed** — a diagnostic threshold isn't met. Binding ONLY
  on the *diagnostic-label assignment*. The underlying process can be
  active without meeting criteria — diagnostic criteria are set
  conservatively to limit label-assignment, not to settle whether the
  biology is happening.
- **(c) Phenotype-mismatch** — symptom shape doesn't match the textbook
  presentation. The *typical* presentation is ruled out; an *atypical*
  presentation of the same process may still be active.
- **(d) Aperture-limited** — a test was run and came back negative, but the
  test's measurement window does not actually cover this candidate. The
  candidate falls outside what the instrument can see: wrong target (the
  assay or panel does not include this class), wrong compartment (it samples
  a different site than where the process lives), insufficient sensitivity
  at the relevant magnitude, or it detects only a transient state the
  process need not be in when sampled. A negative outside the test's
  aperture is *uninformative, not exonerating.* Binding on **nothing** about
  the process.

Concrete rule: (a) is binding on the process — but only within the test's
aperture. (b), (c), and (d) are NOT binding on the process: (b) settles only
the label, (c) only the typical presentation, (d) nothing at all. When
memory or prior reasoning says X is ruled out, the synthesis agent must
answer: which category? If (b), (c), or (d), proceed to the
**atypical-presentation gate** in Step 3 / Step 5 before treating the
process as out.

**Bound on (d) — so it does not become "doubt every negative."** Type (d)
applies only when there is *both* a specific, named candidate in the class
the test fails to cover *and* a non-trivial reason to hold it (an exposure,
a history item, or an unexplained residual the negative leaves standing). A
clean negative is the default rule-out (a); (d) is the exception that fires
when a live candidate provably sits outside the test's window. Without that
bound nothing is ever ruled out and the procedure cannot converge — which is
its own failure mode, equal and opposite to the one (d) prevents.

**Aperture bounds a result in both directions — positives too, not only negatives.** A
result speaks only to what the test actually measures, whichever way it reads. A negative
rules out only within the aperture (above); a positive confirms only within it. Many tests
cover just part of the range of things that could explain a finding — some of the
possibilities on a question, not all of them — and such a test can read positive for the
part it covers while the rest of that same question stays unmeasured. Taking that positive
as if it had settled the whole question — marking the finding explained and stopping the
search on it — is the same aperture error as taking a negative for a rule-out: it silently
writes off whatever the test was never built to detect. So whenever a result settles part
of a question, name what else could account for the finding that this test does not measure,
and hold that remainder as type (d) until a test whose aperture reaches it is run.

Failure mode: collapsing a (b) or (c) rule-out into an (a) rule-out without
the gate walk — i.e. treating "label doesn't fit" as "biology isn't
happening" — **or collapsing a (d) aperture-limited negative into an (a)
test-falsified — i.e. treating "the test we ran was negative" as "the
process is absent" when the test never covered it.** Both drop candidates
whose mechanism is intact: the first when the textbook presentation isn't
met, the second when the instrument simply could not see the process.

**Traceable (process).** Every step also leaves a trace of *how its output came to be*, so the process itself can be audited and improved over time. This lives in a single per-investigation **decision log** file with timestamped entries.

- **Granularity:** significant decisions only, not every micro-thought. Specifically: which candidates were considered and which set aside (and why); which questions were rejected as not discriminating (and why); where the inner loop between cross-check and interview was exited (interview-saturated, moved to discriminator) and on what evidence; where a candidate's tier was changed and what triggered it; where the procedure was halted to re-audit; where a sub-agent's conclusion was downgraded on relay.
- **Timing:** entries are written **close to the moment** of the decision — not reconstructed at the end of a session or step. Reconstructed traces drift toward post-hoc justification; near-real-time capture preserves the actual reasoning.
- **Aggregation:** combined with the per-step output artifacts and the `/research` files, the decision log gives a complete trace of how the investigation reached its conclusions, where it might have gone better, and where the procedure itself needs improvement.

---

## The procedure

The procedure is **not linear.** Steps 5 and 5.5 cycle internally — each interview answer can send the relevant piece back to cross-check, or up to step 3 for more routes if a new candidate appears. Different candidates exit the inner loop at different times. Step 8 lets new evidence re-enter the procedure at any earlier step.

### Step 1 — Observe

**Read first, analyse second.** Before producing any analysis, ingest what already exists.
For a new investigation that means the source material. For any follow-up — and most
turns are follow-ups — it means the project's existing memory, prior research files, the
symptom log, and the load-bearing person-facts right now: what they're currently taking,
where they are, what they've already tried, what they've chosen to stop. Examples of the
kind of stale assumption that breaks the reasoning: noting "they could try supplement X"
when the symptom log already shows they tried it and stopped; building a plan around
their being in city A when last week's note says they moved to city B; assuming they're
taking a brand of antihistamine you suggested when they actually chose a different one.
Checking these is not optional. Context-gathering isn't the warm-up; it's the work.

First, get the data into trustworthy, pattern-ready form: invoke `/extract-health-data`
on everything the person has shared. That sub-skill produces, in `extracted/`, the
faithful per-source extracts (its Phase A) and the compiled cross-source views (its Phase
B) — the event log, the timeline (overview + period chunks), lab-trends, symptom-matrix,
treatment-response, active-exposure, natural-experiments, static-facts, data-gaps,
normals-and-negatives, and conflicts. Do not re-do that restructuring here — it is owned
by the sub-skill. Verify its output is complete and traced before going on; if it flags
anything as uncertain, resolve it here, not later.

Then read the compiled views to orient. Two things are primary evidence, not side notes,
and deserve special attention as you read:

- **Natural experiments** — any episode where the person reports better or worse
  functioning than their baseline. These are within-person, high-contrast comparisons and,
  when they exist, are worth more than most single lab values. Catalogue *all* of them from
  `extracted/natural-experiments.md`, and for each note what changed and what held constant,
  how large and how reliable the shift was, and how confounded it is (one variable moved, or
  many at once). Evidential weight varies: a clean single-variable shift is strong; a
  holiday where eight things changed together is suggestive at best. Do **not** assume one
  "strongest" experiment must carry the case — there may be several worth explaining, one,
  or **none at all**. Many pictures have no natural experiment; that is a normal, valid
  state, not a gap to force-fill. Any that exist are findings a later hypothesis should be
  able to account for; their absence simply means this evidence type isn't available here.
- **Reliable triggers and reliefs** — anything that reliably worsens or improves a
  symptom.

Then read the data for structure, before any mechanism is named. Ask of the raw
observations: what co-occurs? what clusters together? what's anomalous against the rest?
what trends over time? are there dose or quantity relationships (more of X, more of Y)?
This produces a pattern inventory — the structure the data actually shows — that the
mechanism work then has to account for.

**Read each negative and normal for its aperture, not just its sign.** A negative or normal
result rules out only what its assay can actually see. For every "negative / normal / not
detected / within range" in the record, note alongside it *what that test covers and what it
does not* — the classes of cause it targets, the compartment or site it samples, the
magnitude range it can resolve, and the time-window it captures. A result that is negative
for what it measures says nothing about a process it never targeted. Carry these aperture
notes forward: they are what keep Step 5 from reading a narrow negative as a broad rule-out
(register §"Rule-outs are typed, not blanket," type (d)).

Don't name any mechanisms yet. The job here is to absorb what's actually there.

*Output:* the `extracted/` set produced and verified via `/extract-health-data`, plus a
short note cataloguing any natural experiments with their weight and confounding (or
recording that there are none), the clearest reliable triggers/reliefs, the aperture notes
on key negatives, and the pattern inventory to carry into the mechanism work.

### Step 2 — Mechanism

For every observation, restate it as the underlying process that could be
happening for it to show up. Not the diagnosis label — the process. The
form is *"a pathway / mechanism / signal that does X, which would produce
Y"* — a phrase that names what's happening at the biology level, in terms
that don't presuppose any one named entity.

Why this matters: diagnosis labels close the search to one named entity. Process
descriptions open the search to every pathway that could produce that process.

**Three-layer label rule (phase-aware).** Diagnosis labels (acronyms and
named syndrome categories of any kind) play different roles at different
phases of this procedure. Different rules apply at each phase:

- **Research layer** (`/research`, `/research-practitioner` outputs):
  Labels permitted freely as search and citation tokens. No constraint.
- **Synthesis layer** (Steps 2-6 writes to `step2-mechanism-map.md`,
  `working-hypothesis.md`, `step5-cross-check.md`, `step6-prioritize.md`):
  Labels are **TRANSLATED to process descriptions on intake.** When citing
  a research output that uses a label, restate as process before reasoning
  forward. Label-density (count of label-tokens per 1000 words) is
  soft-capped; above the threshold, the `investigate-health-label-density`
  hook flags the write for rewriting. Labels permitted in a single named
  section per file (`## Labels referenced` at end) for cross-reference with
  the research outputs.
- **Offering layer** (Step 7 write to `offering.md`): Labels permitted as
  communication tokens, but **every label must be paired with its process
  description in the same paragraph** — the form is *"[label] — meaning
  [plain-language description of what's happening at the biology level],
  contributing to [the symptoms it would produce]."* The write-check hook
  blocks `offering.md` writes where a label appears without its process
  pairing in the same paragraph.

The maintained list of recognized labels lives at
`~/.claude/skills/investigate-health/references/label-tokens.md` — extensible
without hook code changes.

These moves sharpen this:

- **Entity → products → effects.** When an observation is "X is present" (a bacterium, a
  high level of something), don't stop there — ask what X *produces*, and what those
  products would do downstream. "She has bacterium X" becomes "X makes byproduct Y, and Y
  would do Z."
- **Demand a mechanism, refuse a summary.** For each observation, ask "why would this be
  happening, and how would it lead to what the person feels?" If the answer just restates
  the observation in other words, no process has been named yet.
- **Persistent unexplained marker → dispatch the differential, don't reach for the modal
  cause.** When a finding is *both* abnormal-and-persistent *and* not fully accounted for by
  the obvious explanation, that residual is a trigger: flag it for a **paired** research
  dispatch (run through the Step-3 machinery) — **`/research` for the consensus differential
  AND `/research-practitioner` for the edge / integrative / self-experimentation
  differential** — each enumerating the *complete* set of what produces that finding **and**
  asking "what would a standard work-up for this finding routinely miss?" — the rare, the
  aperture-escaping, and the dangerous-but-treatable causes included. The practitioner pass
  is not optional here: the causes a standard work-up misses are often precisely the ones
  consensus reviews omit, so dropping it re-creates the blind spot. Reaching for the single
  modal cause from memory (a T3 move) instead of dispatching both is the failure that lets a
  specific, nameable, missed cause hide behind a generic label.

*Output:* a mechanism map — observations paired with the underlying processes that might
have to be happening to produce them.

**Mechanism-driven genetics query.** When the working mechanism map identifies
pathways that may be load-bearing AND raw-genetics data is available for the
subject (registered at intake by `/extract-health-data` — see its raw-genetics
note), dispatch a `/research` round to enumerate the SNPs known to modulate
each pathway. **The same machinery is also triggered from Step 5's
strength-estimation pass for any heritable-risk factor** — a family history of a heritable
condition, an ancestry-linked risk — not only mechanism pathways: read the subject's actual
risk alleles to refine that factor's weight, rather than weighting the family-history
heuristic on its own. The query covers first-order variants (the gene whose protein
directly catalyses or regulates the pathway) and second-order variants
(regulators of the first-order gene's expression, cofactor enzymes, pathway-
adjacent variants known to modify outcome). For each SNP surfaced, the research
dispatch returns: rsID, gene, mechanism touched, direction of effect, magnitude
(effect size where published), study quality, replication status, and
population context (in which populations has this been demonstrated). Then
query the subject's raw-genetics file at those rsIDs and produce per-mechanism
extracts at `<root>/extracted/genetics-<mechanism>.md`, each row tying genotype
directly to the mechanism it modulates and to the evidence supporting the
effect. The query may take multiple rounds — finding SNPs, finding effect
details, finding interaction effects with other variants in the subject's data.
This is dispatched from the investigation orchestrator after the mechanism map
exists, not at intake, because the mechanism map is the query specification.
Per the verify-then-weight rule above: any genetic claim used to weight a
candidate carries its verification (it was in the raw file) and its impact
(the effect-size lift with study quality).

### Step 3 — Build (blind upstream mechanism graphs)

For every process from Step 2, map the **upstream causal graph** — what causes,
contributes to, or mediates it. This is done by dispatched sub-agents, **one per process,
each working blind**: a builder receives only its single assigned mechanism — no other
findings, no symptoms, no treatment history, no memory, no knowledge of the other builders
or of why the mechanism was chosen. Blind generation keeps each graph an unbiased map of
the mechanism's real causal neighbourhood; patient-matching happens later (Step 4), cleanly
separated. Send all dispatches in one message (parallel, `subagent_type: general-purpose`);
each agent's output file `<root>/graphs/builder-<process-slug>.md` is the deliverable.

**Prepend `INVESTIGATE-ROLE: builder` as the first line of every builder dispatch prompt.**
This routes `investigate-health-subagent-context.sh` to inject the blindness-reinforcement
and flat-context guardrails (and the cross-subject-memory guard) onto each builder. Without
the marker the hook cannot fire and the guardrails never engage.

The dispatch is neutral (see the dispatch-neutrality rule below): name no candidate, no
condition, no expected answer. The builder prompt — verbatim, no examples, nothing
case-specific:

```
You are given one biological mechanism. Your only task is to trace its UPSTREAM causal
chain — what causes, contributes to, or mediates it — and map it as a graph. Reason from
established physiology and biochemistry. You are working in isolation: you do not know why
this mechanism was chosen, what else is being traced, or what will be done with your
output. Do not infer any of that. Trace this one mechanism.

ASSIGNED MECHANISM: {MECHANISM}

EXPANSION RULE. Start from the assigned mechanism. At every node ask: what causes,
contributes to, or mediates it? Each answer is a branch, followed upstream — a node has
many contributors, so branching is the default, not an exception to a line. Recurse
upstream, each contributor asked the same question, to a MAXIMUM OF FIVE LAYERS (layer 1 =
its direct causes; layer 5 = five steps upstream). Width is unbounded; depth stops at five.

RESOLUTION REQUIREMENT. Every node names a specific, addressable biological entity — a
named molecule, cell type, receptor, transporter, enzyme, tissue compartment, or
measurable marker. A word that names a broad process or state rather than a specific
entity (a category like "inflammation", or a vague mid-level abstraction like "barrier
compromise") is NOT a node; decompose it to the specific entity before continuing.

TIER EVERY LINK. Each edge carries a tier T1 (established/textbook) to T5 (speculative).
Every edge at T3 or weaker carries a one-line falsifier — an observation that would break
that specific link.

INCLUDE ALL REAL CONTRIBUTORS, not only the commonly-tested ones — and for any node that
accumulates, trace BOTH what produces it AND what clears/removes it. An obscure or
rarely-measured contributor (including a clearance route) is a valid node if the causal
link is real. Do not prune a branch because its node is seldom measured.

DO NOT DIAGNOSE. Do not name conditions, syndromes, or an overall picture. Trace only the
causal contributors to the assigned mechanism.

OUTPUT. Write the full graph to {OUTPUT_PATH} as a text adjacency list — each edge as
`source -> target: one-line mechanism [Tn]` with the falsifier appended for T3+ edges,
organised by layer. Then return the flat list of every node name, node/edge counts, the
deepest layer reached, and a 3-sentence summary.
```

Width is unbounded within the graph; depth stops at five layers. The real answer for a
hard case often isn't the most common one, and the blind upstream trace — following every
contributor, including obscure and rarely-tested ones, and tracing **clearance as well as
production** (a node whose story is "made several ways and poorly cleared" is invisible to
a production-only trace) — is what surfaces it without the orchestrator steering toward a
guess.

**Atypical-presentation gate (Q1-Q5) — applies to every "ruled out" entry.**
For any process that any input (memory, prior reasoning, sub-agent output)
declares ruled out, the synthesis agent walks five questions before treating
the process as out. The five-question walk is recorded in `step5-cross-check.md`
as a `ruled-out-gate-result` field on every relevant candidate.

> **Q1.** What category of rule-out is this — (a) test-falsified, (b)
> criteria-failed, (c) phenotype-mismatch, or (d) aperture-limited? (See
> register §"Rule-outs are typed, not blanket.") For (a) specifically,
> confirm the test's measurement window actually covers this candidate — if
> it does not, it is (d), not (a).
> **Q2.** If (b) or (c) — *if the process were happening in this patient but
> not meeting standard diagnostic criteria or not matching the textbook
> phenotype, what would the presentation look like in this specific patient?*
> Write the actual presentation, not the textbook one. If (d) — *what is the
> specific test or test-class whose aperture WOULD cover this candidate,* and
> is it different from the one that was negative? (If the only evidence
> against the candidate is a test that cannot see its class, the candidate is
> not weakened.)
> **Q3.** Does that atypical presentation — or, for (d), the residual the
> aperture-limited negative leaves unexplained — match any unexplained or
> under-explained observations in this case?
> **Q4.** If yes to Q3, what does the cheapest, most reversible intervention
> on this process — or, for (d), the aperture-closing test — look like?
> **Q5.** If a positive answer to Q4 would shift quality-of-life-affecting
> symptoms within weeks, OR an aperture-closing test would change what the
> person could do, the process is **re-entered as a T3 mediator candidate**
> (and, for (d), carried to Step 6 with the aperture-closing test named)
> regardless of the label rule-out. The label stays ruled out; the mechanism
> is back in play.

Failure mode: stopping after Q1 without walking Q2-Q5. Classifying a
rule-out as (b), (c), or (d) and then still treating the process as out is
the same failure as not classifying it at all — the classification only
matters if the gate walk follows.

**The guardrail — non-negotiable.** Generation is wide; admission to the working
picture is strict. A non-obvious candidate stays in the candidate set only if it
(a) explains more of the unexplained residual than the obvious set does, (b) has a named
way it could be ruled out, (c) has a way to discriminate it from siblings, and (d) is
honestly tiered. Otherwise it goes to a noted-but-parked list. This asymmetry — generate
freely, admit strictly — captures the upside of finding the real rare answer without
descending into "everything is mould and parasites."

*Output:* N mechanism graphs under `<root>/graphs/`, one per Step-2 process, each bounded
at five layers, every node a resolved entity, every edge tiered with falsifiers on T3+,
and clearance routes traced alongside production. These graphs are the input to Step 4's
inventory.

### Step 4 — Inventory (enumerate shared nodes, then gate by addressability)

**Patience preamble.** This step has no time pressure. Take however long you need; the
cost of rushing is higher than the cost of doing it slowly. The enumeration and the
addressability gate are dispatched to sub-agents (`subagent_type: general-purpose`) with
clean context; the orchestrator prepares the packet (the Step-3 graphs) and does not
synthesise inline. **Prepend `INVESTIGATE-ROLE: enumerate` as the first line of the
enumeration/addressability dispatch prompt** — the `investigate-health-subagent-context.sh`
hook (Phase F) matches that marker to inject this preamble plus the flat-context and
cross-subject-memory guardrails as `additionalContext` on the dispatched agents. Without
the marker the hook does not fire.

**Dispatch-neutrality rule (non-negotiable).** The dispatch packet is the unranked,
unweighted set of Step-3 mechanism graphs. The orchestrator must NOT, in the dispatch
prompt or any wrapper text:

- name specific nodes or candidates as worth special evaluation, "the likely connector,"
  "must be held as a parallel layer," or any other singling-out language
- mention candidates by clinical name that did not also appear in the graphs under the
  same name
- describe the expected shape of the answer ("evaluate whether X is the connector")
- reference what prior runs concluded, what manual analyses found, or
  what the orchestrator "knows" about this kind of case
- pre-weight by warning the agent against specific candidates
  ("don't crown X automatically") — the warning still elevates X by
  putting it in front

If a specific candidate name appears in the dispatch wrapper, the dispatch is biased and
must be rewritten. The agent enumerates every shared node equally; the orchestrator does
not pre-select which nodes the agent attends to. This rule is the structural equivalent of
blinded evaluation — the agent should not be able to reconstruct, from the dispatch prompt
alone, what the orchestrator suspects the answer is.

Failure mode this prevents: the orchestrator, having seen prior runs or having background
knowledge of the case, leaks the suspected answer into the dispatch by naming it "for
evaluation." Even neutrally framed, the name's appearance gives it disproportionate
attention versus the other nodes the graphs surfaced — the agent then re-derives a similar
answer not because the rules drove it, but because the dispatch seeded it.

When in doubt: name no candidate. Point the agent at the graphs and let it enumerate.

**Do not hunt for "the connector" or rank nodes by importance.** Ranking by
importance/centrality silently buries cheap, broad, reversible nodes underneath
central-but-unactionable hubs — a node that appears in many graphs is *more shared*
precisely by being a generic hub, and importance-ranking rewards exactly that. Enumerate
first; judge last. Convergence is **read off** the finished graphs, never used to steer
them. Strict admission has not gone away — it has moved to Step 6, where the prioritizer's
safety/attribution constraints and value-as-a-move ranking do the disciplined selection.
Generate wide (Step 3, blind), enumerate complete (Pass 1), gate honestly (Pass 2),
prioritise strictly (Step 6).

**Pass 1 — enumerate every shared node.** List EVERY node appearing in ≥2 of the Step-3
graphs, matched at the resolved-entity level (clear synonyms for the same
molecule/cell/receptor/microbe are one node). For each: which graphs it appears in, and the
count. Be exhaustive — include every shared node, central or peripheral; do **not** omit a
node because it seems minor or because it appears in only two graphs. The burying failure
mode is real: a cheap, addressable node that sits in only two or three graphs is exactly
what importance-ranking loses, and exactly what the person can often act on. A node shared
across mechanisms representing *different* symptom domains spans more of the picture than
one shared across near-duplicate mechanisms — record the domain diversity, but never let it
(or any importance judgment) drop a node from the enumeration.

**Match on the shared underlying mechanism, not the shared word — and escalate it.**
Convergence is not only exact-name overlap. Different labels can be facets of one underlying
thing — a mediator, the cell that releases it, the pathway it sits on, the enzyme that
clears it can be the *same axis* under different names. When nodes across graphs are
mechanistically linked this way, recognise the underlying shared mechanism, group the
facets, and **name the axis explicitly** — sharpening a scattered set of near-relations into
one identified thing. Treat a strong cross-graph convergence as a signal to **investigate
that axis more deeply** (its sources, its clearance, its localised and non-canonical forms —
via `/research` and `/research-practitioner`), not as a node to read off and move past.
Convergence *raises* investigation; it does not substitute for it.

**Pass 2 — gate by addressability.** For each shared node, mark whether a DIRECT, specific,
reversible real-world handle exists (a drug, supplement, diet change, specific microbe or
its substrate, cofactor, behavioural lever) — Yes/No, and name the handle if Yes. A node may
be a generic non-addressable hub (a broad cytokine, a master transcription switch) and still
belong in the *complete* table — it is simply marked not-cheaply-addressable, not excluded.

**Multi-route note.** When a single addressable node is produced/accumulated through more
than one distinct route across the graphs (and, for accumulating compounds, also poorly
cleared), record every route and every clearance gap. Such a node is both a high-value
target and the reason a single-route intervention gives only partial relief — that is
information for Step 6, surfaced here, not a reason to crown it now.

The addressable subset is the candidate set Step 6 prioritises.

**Agent overlap is observed and noted, not used as evidence.** When multiple
research agents independently surface the same candidate, hypothesis, or
recommended test, that's a process observation — not a Bayesian update on the
candidate's likelihood. Agents reading the same input data through similar
training priors reach similar conclusions; that's the architecture, not
evidence. Even when inputs are partially non-overlapping, training-prior shared
structure makes "independent convergence" difficult to verify from the outside.
What IS weight-bearing: the underlying *content* the agents cite — specific
primary studies, named mechanisms, falsifiers, discriminators. When two agents
cite the same primary RCT, the RCT is the evidence; the agents are reporters.
When the underlying evidence in agent outputs is the same fact cited from
different angles, that fact gets weighted once at its actual strength, not N
times. Record "candidate X surfaced by N of the dispatched agents" as a process
observation in the decision log using the phrase **"observed in N agents,"** not
"converged on by N agents." No tier is lifted on the strength of agent overlap
alone.

**Completeness audit — what's absent, not just what's present.** Pass 1–2 inventory what is
*present* across the graphs. This asks what is *missing*: list every
observation the hypothesis doesn't explain; name any body system or category of cause that
isn't represented at all; ask what a specialist in an unrelated field would notice is
missing. Absences found here are honest gaps to carry forward (step 7), and sometimes
point back to a route step 3 never opened.

Concrete checklist — go through these seven categories of body system and ask, for
each: is this represented in the working hypothesis? If not, why not — is it genuinely
irrelevant to this case, or has it just not been considered?

- **Digestion and absorption** — gut, microbiome, nutrient uptake, bile
- **Immune system and inflammation** — defence, repair, infection, allergy
- **Energy production** — mitochondria, thyroid, adrenal output, blood sugar
- **Detoxification and elimination** — liver, kidneys, sweat, bowel
- **Transport** — blood vessels, lymph, blood cells
- **Hormones and nerve-signalling** — endocrine, neurotransmitters, autonomic balance
- **Structural integrity** — cell membranes, connective tissue, joints, fascia

Used as a checklist of *what's been looked at*, not as a framework that claims any of
these is the right answer. A category where the working hypothesis has nothing to say
is either a gap to go fill (back to step 3) or an honest "not relevant here because X"
entry — both are fine, an empty category with no justification is not. The audit produces
a 7-row table — category / verdict (represented with cited claim / not relevant because X
/ unexplored) — and no "unexplored" verdict remains by the time the working hypothesis
is offered.

*Output:* `<root>/shared-node-inventory.md` — the complete shared-node table plus the
addressable shared-node subset, plus the 7-system completeness table flagging honest gaps.
This inventory is the input to Step 4.5; the technical working hypothesis emerges from the
hypotheses that survive cross-check, interview, and prioritisation.

### Step 4.5 — Hypothesize

**This step is an inquiry engine, not a diagnosis engine.** Its output is not "the cause"
or even the most-likely one — it is a **set of competing, testable, differentiated
hypotheses** (narratives of what is driving the picture) whose value is that the
*differences between them* define the cheapest tests and questions that will tell them
apart. Truth is what survives after cheap discriminating tests kill the rest — the method
of multiple working hypotheses (hold several alive in parallel; don't marry one) plus
strong inference (design a crucial test that excludes some, run it, repeat). Patient context
— findings, timeline, treatment-response history — legitimately enters here; generation
(Step 3) and enumeration (Step 4) stayed blind/neutral on purpose. Full spec:
`references/hypothesis-step.md`.

**Inputs:** the Step-4 shared-node inventory; the Step-3 graphs (for each hypothesis's
signature and to check a mechanism has a real path); the findings, the **timeline of
events/exposures**, and treatment-response history (fed flat, never as a pointer to an
answer).

**When this step is dispatched to a sub-agent, prepend `INVESTIGATE-ROLE: hypothesize` as
the first line of the dispatch prompt** — this routes `investigate-health-subagent-context.sh`
to inject the flat-context discipline (inputs are data, not a pointer to an answer) and the
cross-subject-memory guard. Without the marker the hook does not fire.

The mechanic:

1. **Three-bucket sort on the timeline.** Sort the factors into standing vulnerabilities
   (born-with / constitutional); what flipped the switch (events preceding onset); and
   what's keeping it going now (currently active drivers — usually grown out of the first).
   The timeline is also one of only two real n=1 confirmation tools (the other is the
   on-off-on trial).

2. **Generate by contrast.** Write the single most conventional explanation first; then
   deliberately construct the strongest **rivals** — each explaining the same load-bearing
   findings through a genuinely *different* mechanism (a different lead driver, or a
   different structure: one-process-driving-many / several-parallel / a-chain). Push for
   different mechanisms, not relabels. Aim for 3–5. Naively asking for "several hypotheses"
   collapses to variants of the modal one; building rivals by contrast is what forces real
   diversity.

3. **Per-hypothesis bar.** Each must account for the **load-bearing** findings and *name
   which it does not explain and why* ("explains everything" is overfitting); rest on a
   coherent step-by-step mechanism (each link real — check against the graphs); be as simple
   as it can be **but no simpler** (don't collapse genuinely separate things to force
   tidiness); note its actionability; and carry an **over-fit flag** if a single mechanism
   is stretched to resolve every tension at once (explains everything → predicts nothing).

4. **Signature.** For each: the *other* symptoms it would produce (→ interview questions),
   the test results it would give (→ tests), and whether it could be turned off as a
   reversible trial and the expected response. A hypothesis without its signature is
   untestable and worthless here.

5. **Discrimination plan.** Where do the signatures *differ*? Each difference is a
   discriminator (a question / test / trial that some hypotheses pass and others fail). Rank
   by split-power × cheap/fast/safe — observational splits first, then tests, then on-off-on
   trials. Label each discriminator's *real* cost honestly; mark non-splitters (resolvers,
   safety items, data-cleanup) as such rather than as discriminators.

6. **Completeness — three sweeps.** *No orphan findings:* every load-bearing finding must be
   explained by ≥1 hypothesis (a finding nothing touches is a flag — open a hypothesis for
   it). *Missing mechanism classes, including must-not-miss:* walk the **complete
   etiologic-category checklist below** — for each category ask "is this kind of cause
   represented among the hypotheses, or has a whole class been skipped?" Every category gets
   equal billing: infection is one cell of the checklist, not a special case, so the sweep
   can neither be accused of nor fall into pointing only at the cause already suspected. Add
   the strand or the safety must-exclude for any unrepresented class. A dangerous-if-missed
   class — one where being wrong and leaving it unaddressed risks irreversible, escalating, or
   time-sensitive harm — is retained on consequence-if-ignored, not on likelihood, and is not
   exempted by a prior negative test whose aperture did not cover it (register §"Rule-outs are
   typed, not blanket," type (d)). *Exposure × finding cross-product:* for every standing
   exposure or environmental fact on record — wherever the person has lived or travelled,
   occupation, animal or water contact, prior infections, medications, implants, whatever the
   record actually holds — ask which otherwise-low-prior cause of an unexplained finding *that
   exposure lifts*. An exposure raises specific candidates that a finding-first sweep alone
   would leave sitting at base rate.

**Etiologic-category checklist (the "what kind of cause" axis).** Completeness has two
orthogonal axes. Step 4's 7-system audit covers *where* — which body system / compartment.
This covers *what kind of cause*, the classic diagnostic sieve, widened for a multi-system,
edge-inclusive investigation. It is a guard against *overlooking* a class — **not** a mandate
to *assign* one. For each load-bearing finding, walk every category and ask "has this kind of
cause been considered, or skipped?" Overlaps are fine (the goal is "no whole class skipped,"
not a clean partition). The sweep is complete only when each finding has been considered
against **both** axes — system and cause-category.

- **Vascular / perfusion** — ischaemia, infarction, haemorrhage, thrombosis, vasculitis,
  orthostatic or perfusion failure.
- **Infectious (single-pathogen) / post-infectious** — acute, chronic, occult, latent,
  reactivation, and post-infectious sequelae — including organisms outside whatever standard
  panel was run.
- **Inflammatory, immune-mediated & immunodeficiency** — immune *over*-activity (autoimmune,
  autoinflammatory, allergic/atopic, mast-cell/type-2, complement) **and** immune
  *under*-activity (primary or acquired immunodeficiency → susceptibility, poor clearance,
  recurrent or unresolving infection).
- **Neoplastic / clonal** — solid (benign or malignant), haematologic/clonal, paraneoplastic,
  hormone-secreting.
- **Structural / mechanical / traumatic** — compression, obstruction, malformation,
  instability, connective-tissue laxity, injury, anatomic variant.
- **Endocrine / metabolic** — hormonal-axis dysfunction, electrolyte and acid-base,
  glucose-insulin, mitochondrial/bioenergetic.
- **Nutritional** — deficiency *and* excess/toxicity; malabsorption; refeeding.
- **Toxic / environmental / iatrogenic — chemical *and* physical** — drugs, supplements,
  interactions, withdrawal, heavy metals, mould/biotoxin; physical agents (radiation,
  thermal, barometric/altitude, electrical, electromagnetic, noise); occupational or
  environmental exposure.
- **Genetic / congenital / constitutional** — inherited variants, enzyme blocks, heritable
  connective-tissue or metabolic conditions, congenital anatomy.
- **Degenerative** — progressive *pathological* tissue decline (neurodegenerative, articular,
  organ) — distinct from normal ageing, below.
- **Neuro-regulatory / autonomic / functional** — dysautonomia, central sensitisation,
  gut-brain axis, HPA / stress-axis dysregulation — a real process level, not a dismissal.
- **Psychological / psychosocial / behavioural** — trauma, mood/anxiety, sleep-behavioural,
  somatic — as genuine contributors, not a wastebasket.
- **Physiological / life-stage / reproductive-state** — *normal* states that drive findings
  and are misread as pathology (or mask it): pregnancy, menstrual-cycle phase, puberty,
  peri-/menopause and andropause, normal ageing, deconditioning, growth, adaptation.
- **Microbiome / ecological** — community-level dysfunction not reducible to a single
  pathogen: loss of diversity, overgrowth (e.g. small-intestinal), niche displacement, lost
  colonisation resistance.

**If a finding fits no category, that is a valid result, not a gap to force-fill.** Record it
as unclassified / not-yet-explained (idiopathic) and hold it as-is. The checklist guards
against *overlooking* a class; forcing a finding into the nearest box just to empty a cell is
the opposite-direction failure and must not happen. The list is intentionally complete rather
than short: a complete checklist walked every run is what keeps the must-not-miss sweep from
being steered by — or toward — whichever cause is already suspected.

**No dedup here, deliberately.** This step is generative. Collapsing near-identical
hypotheses is premature — if two are hard to tell apart, that is for the cross-check
(Step 5) and interview (Step 5.5) to discriminate or merge against real data. Over-collapsing
at generation risks killing a rival the data could have separated.

**Confirmation discipline.** Mark which discriminators merely *narrow* (observational,
suggestive) versus which actually *prove* at n=1: only timing (preceded onset, sensible lag)
and the on-off-on test (remove → fades, restore → returns) give real individual causal
proof. Drive the survivors toward those.

*Output:* `<root>/hypothesis-set.md` — the competing hypotheses (each with its three-bucket
grounding, mechanism, what it explains and doesn't, signature, and over-fit flag) + the
ranked discrimination plan + the parallel safety must-excludes. Held in parallel; not ranked
to a winner. This set is what Step 5 cross-checks, Step 5.5 interviews on, and Step 6
prioritises trials for.

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
evaluate. They have NOT seen the synthesis. **Prepend the matching role marker as the
first line of each judge's dispatch prompt — `INVESTIGATE-ROLE: investigate-judge-skeptical`,
`INVESTIGATE-ROLE: investigate-judge-charitable`, `INVESTIGATE-ROLE: investigate-judge-process-focused`
respectively** — so `investigate-health-subagent-context.sh` injects each judge's stance
plus the cross-subject-memory guard. Aggregation per
`references/council/aggregation-rule.md`: 3-of-3 agree → confident verdict;
2-of-3 → verdict + `disagreement-flag`; 1-of-3 or all-different → escalate
to human, do NOT auto-resolve. Single-judge verification is acceptable for
practitioner claims below the T2-load-bearing threshold.

For every hypothesis in the set from Step 4.5, look at the existing data and ask:
what supports this, what contradicts this, what is silent on this? The aim is to move each
hypothesis on evidence — strengthen, weaken, or break it — not to crown one; convergence
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
  whether it locks to a trigger. Worked example: alpha-gal allergy classically shows up as
  generalised hives a few hours after eating mammal meat, often severe. A mild, persistent
  itch limited to two patches of skin with no clear meal-time link technically ticks "itch
  + swelling" from the symptom list, but the shape — local not generalised, mild not
  severe, persistent not episodic, not time-locked to meals — is wrong. Same list, wrong
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
  written description can be overturned in thirty seconds by the first photo — when the
  shape turns out to show, say, lacy blanching redness with no papules and an unexpected
  body distribution that the frame never predicted. The picture would have changed at the
  start if a photo had been required then. If no photo exists
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

### Step 5.5 — Interview

The cheapest, fastest discriminator for many remaining ambiguities is the person's own
direct experience. For each ambiguity that subjective experience could speak to,
formulate sharp diagnostic questions whose answer would shift the candidate's tier.
To make sure the questions are sharp, research deeper on the specific mechanisms and/or connectors and/or working hypotheses via `/research` + `/research-practitioner` before formulating them — looking not just for practitioner-grade knowledge, but also directly reported details from people confirmed to have experienced that hypothetical situation.

**What makes a question sharp:**

- Research based.
- It targets a specific candidate pathway, not general intake.
- The answer would tilt at least one candidate up or down.
- It's answerable from direct experience without needing a test.
- It's specific enough to get a specific answer ("when the head-heaviness happens, what
  foods or activities preceded it in the last 6 to 24 hours?") rather than open-ended
  ("tell me about your headaches").

Sort questions by how much they would change the picture; present them in batches; wait
for answers.

**This step is iterative.** Answers feed back into step 5 (cross-check), which can
produce a deeper second round of questions, or surface a new candidate that sends a
piece back into step 3 (more routes) and then a third round of questions. Continue until
interview answers stop substantially shifting the picture for the candidate in question.

**Per-candidate loop control.** Interviews aren't a global phase. For each candidate
individually, ask: is this candidate still discriminable by subjective experience? If
yes, keep interviewing for it. Has interviewing stopped shifting this candidate's tier
substantially? If yes, this candidate is interview-saturated — move it to step 6. Some
candidates saturate early; others stay interview-discriminable longer. Handle each
candidate's switch independently. Also: where remaining ambiguity is between candidates
that subjective experience genuinely can't separate (two different biological pathways
producing the same felt experience), interviewing more is futile — go to step 6.

Concretely: after each interview round, look at the candidate's ledger entry before and
after the round. If nothing changed — no new supporting evidence, no new contradicting
evidence, no tier movement, no new ambiguity surfaced — that's a "no-shift round." Log
it as such in the decision log. Two no-shift rounds in a row for the same candidate
means it's saturated by interview, regardless of how many more questions you could in
principle still ask. Move it to step 6. One no-shift round isn't enough — a single round
of poorly-aimed questions could explain it.

**Interview substrate — pre-existing transcripts.** If `<root>/extracted/` already
contains interview transcripts or daily symptom notes (i.e., the subject was interviewed
before this run started, or the pack arrived with prior interviews), Step 5.5 reads from
those as the primary interview substrate and generates questions only for the
ambiguities the existing material doesn't resolve. Generated questions go into
`<root>/question-bank.md` under "Pending" (waiting for the next live touchpoint with
the subject) or "Deferred" (lower-priority, can wait). The procedure continues without
blocking on live answers — pending questions are part of the deliverable and are
surfaced in the offering as "to ask next time." If `<root>/extracted/` has no interview
material *and* no live interlocutor is available, every Step 5.5 question is filed as
Pending and the procedure exits at Step 7 with the offering plus the question list,
marking the run "interview-blocked" in the decision log.

**Data hygiene — interview transcripts and daily notes are sources too.** They carry the
same drift risk as any source: structured notes diverging from what the person actually
said, with the drift then becoming "the data." So they go through `/extract-health-data`
like any other source — an incremental update that preserves the verbatim original, tags
every derived claim back to its source line, and re-derives the affected compiled views.
That sub-skill owns the verbatim-original and traceability discipline; don't re-implement
it here. Each new daily note triggers the same incremental update, then cross-check
(step 5), then the loop re-enters at the affected step regardless of where the broader
procedure was.

*Output:* interview rounds (verbatim source files plus traced structured notes), updated
working hypothesis after each round, per-candidate status of "still interview-discriminable"
versus "needs a discriminator."

### Step 6 — Prioritize

Prioritisation is **not** ranking the addressable inventory by importance — that buries
cheap, broad, reversible probes under central-but-unactionable hubs. It is the design of an
**adaptive sequence of interventions**, because at N=1 only intervention yields *causal*
evidence (the graphs and inventory are *candidate* causes, T2–T3); the person's response to
each action is the most privileged evidence in the investigation and rewrites the order
each cycle. The full spec — objective (maximise QoL-benefit + discriminating-information per
unit risk + cost + readout-time), the safety and attribution hard constraints, value-as-a-
move ranking (not centrality/importance), and the emit-first-wave-plus-branch-logic output
— lives in `~/.claude/skills/investigate-health/references/prioritizer.md`. This step never
assumes one pass finds the answer: it emits the designed first wave plus the
if-this-then-that update rules, then re-runs on each new response (Step 8). Patient context
— findings, symptoms, treatment-response history, hard-no list — enters here; generation
(Step 3) and enumeration (Step 4) stayed blind/neutral on purpose.

The operational mechanics below — trial-vs-test, the value-of-information gate, the scoring
axes, build-up and washout, the hard-no pre-flight, therapeutic-trial-as-discriminator, the
high-risk exception — are special cases of that objective and those constraints. Apply them
to the addressable shared-node candidates from Step 4.

For each candidate that interview can no longer separate from its siblings, design what
would. For each, ask: **trial or test?**

First, a value-of-information gate — before designing any discriminator, ask what decision
its result would change. *"If the result is A we'd consider X; if B we'd consider Y."* If
A and B lead to the same place, the discriminator earns nothing — drop it. The same gate
kills distinctions that don't matter: *"what difference would telling these two apart
actually make to what the person could try?"* If none, stop trying to separate them.

**Test-sensitivity / aperture check — the discriminator must be able to detect the thing.**
Before a test earns a slot, confirm it can actually return positive when the candidate is
true: its target, its compartment, its sensitivity at the expected magnitude, and its timing
must cover the candidate. A test whose aperture misses the candidate cannot discriminate it —
a negative would be uninformative (register §"Rule-outs are typed, not blanket," type (d)),
so it buys nothing and risks being mis-read later as a rule-out. In particular, when a
candidate survived *because* a prior test was aperture-limited, the new discriminator must
**close that exact aperture gap** — a different test or test-class that covers what the first
one missed — never a repeat of the same-aperture test, which would only recreate the original
false-negative.

A **trial** is the person trying a small, safe, reversible and observing the
response — the response is the data, so the trial *is* the test. Prefer a trial when:
feedback is fast (days to weeks); the intervention is reversible; safety is high (no
known contraindications, low side-effect profile); and there's therapeutic upside if the
candidate is right.

A **test** is a measurement (blood, urine, imaging, breath). Prefer a test when: the
intervention that would test the candidate is risky enough that doing it blind would be
a problem; feedback from a trial would be too slow to be useful (months); or the result
would fundamentally change which direction to go.

Score each trial or test option on:

- **Cost** — what would the person actually pay
- **Access realism** — can they actually get this, where they are
- **Invasiveness and reversibility**
- **What it discriminates** — the specific candidates that a positive vs negative
  result would tilt
- **Multi-mechanism leverage** — does this option act on (or test for) more than one
  candidate at once
- **Expected effect size** — if this candidate is right and the person acts on it, how big
  is the likely benefit? Evidence tier says how *sure* we are; this asks how *much* it
  would matter. A well-supported but trivial effect ranks below a less-certain large one.
  

**Therapeutic-trial-as-discriminator.** For each T3 candidate, explicitly ask:
is there a cheap, reversible therapeutic trial that would discriminate this
hypothesis from its siblings within weeks? Many T3 candidates have cheap
interventional probes (OTC antihistamine, elimination-diet window, sleep-
environment change, single-supplement pause-and-rechallenge). These often
produce more information per pound spent than a serum panel. A trial result
that shifts symptoms in days at low cost discriminates directly; an expensive
blood panel can produce ambiguous numbers that don't change action. The trial
is the test. Do not default to lab panels when a reversible OTC trial would
discriminate the same hypothesis. For every T3 candidate in the discriminator
plan, the plan must include either an explicit therapeutic trial option OR a
written reason no cheap reversible trial exists.

**The high-risk exception is non-negotiable.** When the intervention required to test a
candidate is risky enough that doing it blind would be a problem, a measurement is
called for first. This is the only situation where a test is offered before a trial has
been considered.

**Design for clean signal.** A discriminator only works if its result is readable. Where
attribution matters, change one thing at a time rather than starting several at once. Order
options by feedback speed, so the fast-reading ones come first. Derive "by when should we
expect to see something" from the mechanism, not an arbitrary review date. And name the
confounders in the person's routine (meal timing, other new supplements) that would need
to hold steady for the signal to mean anything.

Two specific timing checks before any trial is finalised:

- **Build-up period.** Some things don't act until they've accumulated — minerals,
  certain hormones, gut-microbiome interventions, anything that has to remodel something
  before its effect shows up. For these, the window for reading the result starts at the
  end of the build-up, not at first dose. A two-week trial of something with a three-week
  build-up looks like a failure when it's actually a too-short trial.
- **Let the previous thing clear out.** If anything is being stopped or swapped at the
  same time as the trial starts, allow long enough for the previous item's effect to
  fade before reading the new item's signal. Without this gap, the stopped thing's
  tail-off masquerades as either the new thing working or the new thing not working,
  depending on which way it's drifting.

Both checks are derived from the mechanism — what's known about how long the
intervention takes to build up, and how long the previous thing takes to clear — not from
a default calendar number. Each trial in the discriminator plan carries two named fields:
`start-reading-from` (date or day number) and `washout-needed` (substance + days, or
"none — nothing being stopped"). A trial with either field empty is flagged for re-design
before going to step 7.

**Hard-no pre-flight (per the register).** Before any item enters the discriminator plan,
run it through the person's hard-no list as described in the register. Each trial in the
plan carries a `hard-no check` field with the verdict (clear / flagged near-match with
reason / excluded — should never reach here).

**Symptom-relief / load-reducer track (a parallel output, ranked differently).** The
discriminator plan above ranks moves by **discriminating power** — how much each result
re-ranks the map. That is correct for *learning which hypothesis is right*, and it
systematically drops a different, legitimate kind of move: the **broadly-acting, reversible
lever that reduces symptom load without telling the hypotheses apart** (an antihistamine
when a histamine/mast-cell axis spans many graphs, a barrier-support layer, a sleep or
stress lever). These ease what the person actually feels *while the discrimination loop runs
in the background* — relief sits in the objective right beside information, so it gets its
own track. Full spec: `references/prioritizer.md` §3b.

- **Source.** Draw from the **Step-4 addressable shared-node subset** ("The addressable
  subset is the candidate set Step 6 prioritises" — Step 4) — the same set the discriminator
  wave draws from. A node belongs here when acting on it is expected to *reduce a symptom the
  person lives with* across one or more mechanisms it spans, regardless of whether its result
  separates any two hypotheses. A node may appear in both tracks; a broad-safe-but-non-
  discriminating node appears **only** here (which is the point — it would otherwise be lost).
- **Ranking — NOT by discrimination.** Order by **symptom-relief expected × breadth (distinct
  symptom domains) × safety/reversibility × speed-of-readout.**
- **Constraints unchanged.** The Step-1 safety partition and the **hard-no pre-flight** run
  on every relief item identically. Relief relaxes only the requirement that a move
  discriminate — never safety or attribution.
- **Framing.** Each item carries the explicit note: **"this does not test which hypothesis is
  right — it aims to ease symptoms while we sort out the cause."** A relief trial that
  incidentally informs (e.g. antihistamine helping → weak support for a histamine axis) is
  noted at its honest low tier, never as the reason it is in this track.

*Output:* a discriminator plan — per candidate, the trial or test option, with what each
possible result might suggest, plus `start-reading-from`, `washout-needed`, `hard-no
check`, and (for any rule-out-regardless candidate) `consequence-if-ignored` per trial —
**plus a "## Symptomatic-relief / load-reducer track" section** in
`step6-prioritize.md` listing the relief levers ranked by relief × breadth × safety × speed,
each with its handle, target symptom domains, readout window, hard-no verdict, and the
"eases symptoms, does not discriminate" note. Hypothetical language throughout.

### Step 7 — Offer

**Patience preamble.** This step has no time pressure. The finish-line check
is the last line of defence against rushed output. Take however long you
need. Self-grading by the synthesis agent is **explicitly forbidden** —
finish-line audit is dispatched to an **audit-council** (3 auditors with
diverse priors) whose verdicts gate the Write of `<root>/offering.md` via the
`audit-council-completion.sh` token issuer (Phase F). **Prepend `INVESTIGATE-ROLE:
investigate-audit` as the first line of each auditor's dispatch prompt** so
`investigate-health-subagent-context.sh` injects the auditor guardrails (verify against
primary sources, not the synthesizer's prose) plus the cross-subject-memory guard.
Auditors receive: primary sources directly, the finish-
line checklist below, and an explicit instruction to verify each item
against primary sources (not against the synthesizer's prose).

**Before anything goes out, run the pre-audit checklist (advisory — it is the synthesis
agent's own pre-check, NOT the gate).** Passing it does **not** satisfy the finish-line gate;
only the audit-council token does (see the patience preamble above — self-grading by the
synthesis agent is forbidden as the *gate*; this checklist is allowed as a pre-dispatch
surface-the-gaps pass). Take the working hypothesis and the discriminator plan through it —
each item is a question that has to get a real answer, not a nod:

One specific check that's earned its own line: the **inversion check.** For each
load-bearing claim in the working hypothesis, ask: if the opposite observation had
happened instead — the symptom didn't improve when we'd expect it to, the lab moved the
wrong way, the trigger didn't trigger — could I tell an equally convincing story with
a different mechanism? If yes, that claim has no real predictive power; it would
survive any outcome by being re-told. That's rationalising, not analysing. Downgrade or
remove it before the offer goes out. A failed inversion check sends the claim back to
step 5 (re-tier) or step 4 (re-form working hypothesis).

- Is each piece a root cause (or a named load-reducer), or just a restatement of a finding?
- Is the unifying mechanism actually named, or is this a list wearing the word "hypothesis"?
- Is each intervention ranked by likely effect size, not just by how plausible it is?
- Does each test earn its keep — a different action depending on the result?
- For each thing to learn: is it a trial or a test, and is that the right call?
- Is every price, dose, source, and availability verified, or honestly tagged as an estimate?
- Has confidence escalated anywhere across rewrites without new evidence?
- Does the picture explain the natural experiments from step 1 that carry real weight (if any exist)?
- For each load-bearing claim: has the inversion check been run, and would each claim
  actually have failed under the opposite observation?
- For each candidate: if it turned out to be the actual answer and went unaddressed,
  would the downside be irreversible, escalating, or time-sensitive? Where yes, has it
  been marked separately as "worth taking seriously even if it isn't the most likely"?

Anything that fails goes back to the step that owns it before the offer is made.

Present the working hypothesis and the discriminator plan back to the person in plain
language, hypothetically.

**Two artifacts, separate, separate purposes:**

- **The working hypothesis (technical).** Full detail, every claim traced and tiered. For
  ongoing investigation use and for sharing with their clinician if they choose.
- **The person-facing offering (clear and without jargon).** Hypothetical register throughout, structured
  as "here's what we think might be going on, here's the evidence we're basing it on,
  here are some things you could consider — these are options to discuss with your
  clinician, not instructions."

The person-facing offering covers:

- A plain-language picture of the leading interacting pathways, with honest confidence
  ("we think this is likely," "this one we're less sure about")
- The natural experiment the picture explains — usually the strongest evidence the
  person already has from their own body
- Options they could consider trialing (low-risk, reversible), with what each option is
  aimed at
- **Things that could ease symptoms while we work out the cause** — the broadly-acting,
  reversible levers from the Step-6 symptom-relief track, offered as their own group with
  the honest framing that *these aim to reduce what you're feeling, not to tell us which
  explanation is right.* A lever that does both is noted as such; a relief-only lever is
  still offered here so comfort isn't held hostage to the investigation finishing.
- Tests they might consider for the higher-risk explorations, with what each possible
  result might suggest
- **Anything worth taking seriously even if it's not the most likely.** Where ignoring a
  candidate and being wrong about it would do real harm — irreversible damage, a
  condition that worsens with time, a window that closes — that candidate gets flagged
  on its own, separately from the most-likely ordering. A candidate that's third on
  likelihood but high on consequence shouldn't be buried behind two lower-consequence
  ones.
- What's still unexplained — the parts of their picture this account doesn't yet cover,
  honestly named
- **Hard-no check (per the register).** An explicit section listing every proposed item —
  trial, test, and relief-track lever — with its verdict (clear / flagged near-match with
  reason / excluded with reason). Zero excluded items reach the offering; every flagged
  near-match carries its flag visibly. (Re-runs the Step-6 pre-flight; surfaces it to the
  person.)

Phrasing throughout: "could be worth considering," "might be consistent with," "if you
and your clinician decided to explore A, what we'd be hoping to see is B." Never "do,"
never "should," never "must."

**Finish-line auto-check.** After the pre-audit checklist passes, walk the finish-line checklist
explicitly and log each verdict:

1. Working hypothesis exists, connected, tier-tagged, every claim source-traced,
   any weight-carrying natural experiments from step 1 explained (or N/A — none exist)? **Y / N.**
2. Each load-bearing pathway has at least one trial or test attached? **Y / N.**
3. Trial options ranked by safety, breadth of mechanism, and feedback speed? **Y / N.**
4. Test option named for any pathway lacking a safe trial? **Y / N.**
5. Honest gaps named — what the picture doesn't yet explain? **Y / N.**
6. Hard-no check present — every proposed item (trial / test / relief lever) carries a verdict,
   and zero excluded items appear in the offering? **Y / N.**
7. Register clean (per §"Register vocabulary") — **verified by the audit-council against the
   produced text, not self-graded by the synthesis agent.** Every line hypothetical; no
   advisory/imperative verb; no outcome-promise ("fixable" / "cure" / "will resolve"); no
   certainty/finding construction below T1 ("the actual finding" / "the real cause"); no
   escalation word below T1; **the word "diagnosis" never appears in the tool's own voice (not even
   "the diagnosis is uncertain") — only when attributing to a practitioner's record/writing ("records
   note X")**; no fresh assertion of a cause still being discriminated; **any directive or treatment-sequencing aimed at the person — in any phrasing or scenario, not just a
   matched keyword — is a register failure** (e.g. "before you take X," "start/stop Y"); high-consequence
   flags are stated as information a clinician acts on, never as an instruction to the person. **Y / N.**

All seven **Y** → write `<root>/offering.md`, log "finish-line pass" in the decision log,
end the run. Any **N** → return to the step that owns the gap (1 → Step 4; 2 → Step 6;
3 → Step 6 reorder; 4 → Step 6; 5 → Step 4 completeness audit; 6 → Step 6 hard-no pre-flight;
7 → register rewrite per §"Register vocabulary," then re-audit), log the bounce, loop.
If three consecutive bounces on the same N, write `<root>/RESUME.md` naming the
persistent gap and exit — never loop indefinitely.

*Output:* `<root>/working-hypothesis.md` (technical) and `<root>/offering.md` (plain).

### Step 8 — Iterate

Every new piece of evidence — a new lab result, a daily symptom note, the outcome of a
trial, an answer from a clinician — re-enters the loop at the appropriate step. Append
to the source file verbatim, run cross-check (step 5), propagate updates through the
working hypothesis. If the new evidence raises a candidate that wasn't on the map, go back
to step 3 and re-do routes for it.

The procedure is never "finished" in the sense of being closed. The finish line below
describes a state where the picture is detailed enough to support useful action — not a
state where investigation stops.

**Resume-on-block.** When a discriminator or a piece of cross-check needs data the
subject doesn't have yet (a test not yet run, an observation not yet collected, an
interview answer not yet given), do not stall in-conversation. Write `<root>/RESUME.md`
containing: what's blocked (specific item, specific step), what's needed to unblock
(test result / observation / interview answer / external source), which step the run
resumes from when the block clears, and a pointer to where in the artifacts work picks
up. Then exit cleanly. The next run reads `RESUME.md` first (per bootstrap step 2) and
either resumes if the block has cleared or re-emits the same RESUME and exits again.

---

## How the loop is actually run

**No cleanup mid-run.** No deletion, removal, move, or `git clean`-style
operation may occur between bootstrap and the Step 7 finish-line pass.
Intermediate scratch files, false-start drafts, and superseded
working-hypothesis stubs stay on disk until end-of-run. Cleanup is a single
named step that runs only after Step 7 emits `<root>/offering.md` and the
audit-council issues a finish-line token. Mid-run `rm` / `mv` / `rmdir` /
`git clean` against any path under the active `<root>` is blocked by
`investigate-health-cleanup-block.sh` until that token exists. The reason: a
mid-run cleanup that deletes something the audit will look for converts a
recoverable mistake into an undetectable one.

**Operational notes (sandbox + subject-root).**

- **`audit-council-completion.sh` must run unsandboxed.** The token issuer signs its
  finish-line / offering tokens with an HMAC secret at `~/.keys/claude-skill-token-secret`,
  which the command sandbox denies for read. When the orchestrator runs
  `audit-council-completion.sh <session> <gate> <claim-id>` it must disable the sandbox for
  that one command (it will otherwise fail with a secret-file-missing / permission error,
  not a logic error). This is the only investigate-health command that needs the
  sandbox-disable; everything else runs sandboxed normally.
- **Run under the subject's own root.** The ambient-project-memory inheritance described in
  bootstrap step 1 is a harness behaviour, not something a hook can suppress. The
  operational requirement — investigate a subject only under that subject's own project root
  / own `MEMORY.md` — is the structural fix; the `INVESTIGATE-ROLE` cross-subject-memory
  guard is defense-in-depth. See bootstrap step 1.

**Bootstrap — first actions on any new run.** Every run starts by establishing the
subject's root directory and instantiating state files. No analytical work happens before
this completes. The bootstrap is observable: every run must produce a bootstrap entry as
the first decision-log entry — a run with no bootstrap entry was started incorrectly.

1. **Identify the subject root.** Either given explicitly (`/investigate-health <path>`)
   or inferred from the input pack location. From here on, `<root>` refers to this
   directory. Every artifact this procedure produces lives under `<root>`. The subject's
   own memory, hard-no list, and prior data are canonical to `<root>` — do not
   substitute another subject's memory.

   **Run under the subject's OWN root — the structural fix for cross-subject contamination.**
   The harness inherits the *ambient project* `MEMORY.md` into dispatched sub-agents
   regardless of `<root>`. If the active project directory belongs to a *different* subject
   than the one being investigated (e.g. investigating subject B while the session's project
   memory holds subject A's hard-no list), that other subject's facts leak into "blind" enumeration
   and synthesis agents through ambient inheritance — an additive hook cannot suppress an
   injection the harness performs. The structural fix is operational: an investigation of a
   subject whose memory is not the ambient project memory must run under *that subject's own
   root* (own project directory / own `MEMORY.md`), so the ambient inheritance is the
   correct subject's. The `INVESTIGATE-ROLE` cross-subject-memory guard (below) is
   defense-in-depth on top of this, not a substitute for it. Record in the bootstrap
   decision-log entry which subject's memory is ambient and confirm it matches `<root>`.
2. **Resume check.** If `<root>/RESUME.md` exists, read it first. It names what blocked
   the previous run, what's needed to unblock, and which step resumes. If the blocking
   condition is now resolved, proceed from the named step; otherwise re-emit the same
   RESUME and exit.
3. **Locate and TYPE the memory contents.** Search `<root>/memory/` for
   `MEMORY.md`, `hard_no_*.md`, `feedback_*.md`, and any other memory files.
   **Memory contains different content types with different roles** — read
   each for a specific purpose, NEVER as general synthesis input:

   | Memory file / section | Role | Trust at synthesis |
   |---|---|---|
   | `MEMORY.md` "HARD NO" section + `hard_no_*.md` | Hard-no constraint | Binding — used at Step 6 + 7 pre-flight only |
   | `feedback_*.md` | Procedural corrections (how to work, not what is true) | Binding on procedure; surface to synthesis dispatch as "feedback discipline rules" |
   | `MEMORY.md` session-stable facts (ancestry, genotype confirmations, lifelong patterns, hard biographical facts) | Subject-fact constraint | Trusted like extracted/static-facts.md; surface as `subject-stable-facts` packet |
   | `MEMORY.md` "frameworks RULED OUT" / "STRENGTHENED" / "WEAKENED" / "current working hypothesis" / "layer model" sections | **Prior synthesis output, NOT ground truth** | Low trust — re-derive from primary sources; any "ruled out" entry MUST go through Q1-Q5 atypical-presentation gate (Step 3) before being treated as binding on the process |
   | `<root>/prior-conclusions/*.md` (if directory exists) | Prior synthesis output | Same low-trust treatment as above |

   Bootstrap surfaces these distinctions to the synthesis dispatch in
   *separate sections* of the dispatch prompt: `## Subject-stable facts
   (ground truth)`, `## Hard-no list (constraint only)`, `## Procedural
   feedback rules`, `## Prior synthesis outputs (NOT ground truth — re-derive
   from primary sources; ruled-out entries subject to Q1-Q5 gate)`. **Prepend
   `INVESTIGATE-ROLE: investigate-synthesis` as the first line of every synthesis
   dispatch prompt** — that marker is what routes `investigate-health-subagent-context.sh`
   to inject this memory-role separation rule (plus the integrator definition, rule-out
   typing, label-translation rule, and the cross-subject-memory guard). Without the
   marker on the prompt, the hook cannot fire and none of those guardrails engage.

   **Clean-room exception — when synthesis need NOT be dispatched.** The synthesis-dispatch
   requirement exists for ONE purpose: to stop a *different* subject's ambient project memory
   leaking into synthesis (the cross-subject-memory guard). When the run is in a verified-clean
   root — the ambient project `MEMORY.md` confirmed at bootstrap to carry no other subject's
   facts, and this subject's own `memory/` empty or subject-only — that contamination risk is
   moot, and the orchestrator MAY perform synthesis (Steps 2, 4.5, 5, 6, 7) inline rather than
   via a dispatched `investigate-synthesis` agent. Record the determination in the bootstrap
   decision-log entry ("ambient memory verified clean → inline synthesis permitted"). This
   exception covers ONLY the synthesis dispatch; it does NOT relax the blind-builder (Step 3),
   enumeration (Step 4), per-hypothesis research (Step 5), judge-council, diversity-judge,
   spot-check, or audit-council dispatches — those are required on every run regardless of
   contamination state, and are programmatically enforced by the required-artifact contract.

   If none of these files exist, note in the decision log — the register's
   pre-flight check then only matches future-added entries.

3b. **Intra-project conflict detection.** If `<root>/` contains BOTH (i) a
   memory file with conclusion-shaped content ("ruled out," "is the
   integrator," "STRENGTHENED," "WEAKENED") AND (ii) any file matching
   `working-hypothesis*.md` or `prior-conclusions/*.md`, dispatch a focused
   diff sub-agent: read both, identify load-bearing claims where they
   disagree (e.g. memory says X ruled out, working-hypothesis says X is the
   integrator), and write `<root>/intra-project-conflicts.md` listing each
   conflict with source citations. The dispatch uses
   `subagent_type: general-purpose` and emits the file deterministically;
   summary is for orientation, the file is the deliverable.

   This file is then included in every `investigate-synthesis` dispatch as
   `## Intra-project conflicts to resolve before synthesizing`. The synthesis
   agent must explicitly choose which to trust and record the reasoning,
   rather than silently following one and ignoring the other. If no
   conflicts exist, write the file with a single line "No intra-project
   conflicts detected at bootstrap" — its presence is the audit trail.
4. **Instantiate state files** under `<root>/` (skip any that already exist):
   - `decision-log.md` — copy from
     `~/.claude/skills/investigate-health/decision-log-template.md`, replace `[Subject ID]`
     with the subject name. If that template is unreachable from this root, create
     `decision-log.md` self-contained, each entry a line `## <timestamp> — <step> —
     <decision> — <trigger>`. Bootstrap must not block on the template being present.
   - `extracted/` — directory. If empty, Step 1's first action invokes
     `/extract-health-data` on `<root>/data/` (or whatever the raw-source directory is).
     If already populated, verify completeness and skip re-extraction.
   - `step2-mechanism-map.md` — empty stub; Step 2 writes the observation→process map here.
   - `working-hypothesis.md` — empty stub with section headers (Candidate drivers /
     Load-bearing pathways / Honest gaps). These three are this file's own headers, not
     separate files. The header is "Candidate drivers," **not** "Connector candidates" —
     Step 4 forbids hunting "the connector"; the file enumerates drivers, it never crowns one.
   - `question-bank.md` — empty stub (Asked / Pending / Deferred sections).

   The per-candidate fields that earlier versions held in a standalone
   `candidate-ledger.md` are now carried inside the step files that already produce
   them — there is no separate ledger file:
   - cross-check / evidence fields (supporting / contradicting / silent / tier /
     verification / impact / practitioner-claim-rubric / ruled-out-gate-result) live in
     `step5-cross-check.md` (Step 5);
   - signature / falsifier / discriminator fields live in `hypothesis-set.md` (Step 4.5);
   - consequence-if-ignored / hard-no check / trial-vs-test / build-up / washout fields
     live in `step6-prioritize.md` (Step 6).
   Bootstrap stubs the gated step files so their write-checks have a target:
   - `step5-cross-check.md` — empty stub; Step 5 writes the per-candidate evidence ledger.
   - `step6-prioritize.md` — empty stub; Step 6 writes the discriminator plan plus the
     symptomatic-relief / load-reducer track.
   - `offering.md` — **DO NOT STUB.** The file is created only at Step 7
     finish-line pass, with its Write gated by an audit-council token issued
     by `audit-council-completion.sh`. Creating an empty stub at bootstrap
     conflicts with the gating hook and either bootstrap fails or the gate
     is meaningless. Just don't write the file until Step 7.
   - `research/` — directory for dispatched `/research` outputs.
   - `graphs/` — directory for the Step-3 blind upstream mechanism graphs
     (`builder-<process-slug>.md`, one per Step-2 process).
   - `shared-node-inventory.md` — empty stub; Step 4 writes the complete shared-node
     table plus the addressable subset here.
   - `hypothesis-set.md` — empty stub; Step 4.5 writes the competing hypotheses, their
     signatures, and the discrimination plan here.
5. **Write the bootstrap entry** to the decision log: timestamp, subject root identified,
   hard-no list located (or absent + searched paths), state files instantiated (or
   already-present and reused), resume-state if any.

**Parallel research dispatch — MANDATORY, one paired dispatch per load-bearing mechanism.**
For EVERY hypothesis carried into Step 5 (each non-null `Hn` in `hypothesis-set.md`) you MUST
dispatch BOTH a consensus `/research` agent AND an edge `/research-practitioner` agent, writing
to the named files `research/<hn>-…-consensus.md` and `research/<hn>-…-practitioner.md` (the
`<hn>` prefix is the contract the write-check hook enforces — see the required-artifact contract
below). **Name research files and ledger quote-ids label-free** — no diagnosis-label tokens in a
filename or `[ledger: …]` id (e.g. use `androgen-axis`, not `androgen-pcos`; `h2-inflammation`, not
`L2-CRP`), because the label-density hook matches tokens *inside* slugs and ids when they are later
cited in a gated synthesis file. This is not reserved for "hard cases" or "when step 3 needs wide enumeration"; it is
standard on every run, dispatched in parallel (all Agent calls in one message). The persistent-
unexplained-marker differential (Step 2) is dispatched the same way. Skipping or scoping this
down to save effort violates the thoroughness directive and is blocked at the Step-5 gate. (You
may *also* dispatch one `/research` per Step-3 process for wide route enumeration; that is
additive, not a substitute for the per-hypothesis paired dispatch.)

**Source the edges, not only the consensus.** Alongside `/research`, dispatch
`/research-practitioner` for the load-bearing mechanisms — practitioner-grounded,
integrative, and self-experimentation knowledge that mainstream reviews may omit or dismiss.
This is standard on every run, not reserved for hard cases. Edge sources are tiered honestly
like everything else (often T3–T5) and flagged as edge — but they are *pulled in and kept*,
never skipped for lacking consensus backing. The point is to surface the mechanisms the
consensus literature doesn't describe, which on complex pictures can be where the answer
lies.

**How, concretely:** use the Agent tool with `subagent_type:
general-purpose`, invoking the `/research` skill in the prompt. Send all the parallel
calls in a single message (multiple Agent tool uses in one block — the harness runs them
concurrently). Each agent's prompt names its output path explicitly:
`<root>/research/<short-topic-slug>.md` (where `<root>` is the subject root established
in bootstrap). The agent's returned summary is for orientation; the file is the
deliverable. Instruct the agents with the tier system,
encourage not rushing to conclusions, thinking like a Keegan level 5 person, and
approaching things systemically like a good scientist. Instruct them to report findings
probabilistically and to issue no recommendations or treatment advice — research-layer
mechanism and diagnosis labels are fine for naming the biology, but advisory or
outcome-promise language must not be imported downstream. Also instruct them to flag any
source that fails basic quality markers — no methods section, conclusions drawn from a
single small or uncontrolled study, undisclosed funding or conflict of interest, blog or
marketing content presented as evidence, or claims that don't actually appear in the
source's own findings. Flagged sources still get reported (sometimes they're the only
thing on a topic), but they're marked clearly so they don't get weighted like proper
evidence later. Each research output file must contain either an explicit "no sources
flagged" line or one or more flagged-source entries.

**State on disk, always.** The investigation's working state lives in files under
`<root>/`, not in the conversation:

- `<root>/extracted/` — verbatim source extracts and compiled views, owned and
  maintained by `/extract-health-data`
- `<root>/step2-mechanism-map.md` — observation→process map (Step 2)
- `<root>/working-hypothesis.md` — current best account, multi-layered, tier-tagged
- `<root>/shared-node-inventory.md` — complete shared-node table + addressable subset (Step 4)
- `<root>/hypothesis-set.md` — competing hypotheses, each with signature / falsifier /
  discriminator (Step 4.5)
- `<root>/step5-cross-check.md` — per candidate, support / contradict / silent / tier /
  verification / impact / practitioner-claim-rubric / ruled-out-gate-result
- `<root>/question-bank.md` — interview questions Asked / Pending / Deferred
- `<root>/step6-prioritize.md` — trial-vs-test decisions (build-up + washout + hard-no +
  consequence-if-ignored per trial) plus the symptomatic-relief / load-reducer track
- `<root>/research/` — outputs from dispatched `/research` agents
- `<root>/decision-log.md` — the process trace (significant decisions, tier changes,
  halts and what they triggered), per the "Traceable (process)" rule above
- `<root>/offering.md` — the person-facing deliverable, only written at Step 7
  finish-line pass
- `<root>/RESUME.md` — present only when the previous run blocked on missing data;
  read first on next run

Update these at every step. Never rely on the conversation to remember state.

**Required-artifact contract (PROGRAMMATICALLY ENFORCED — the sequence cannot be skipped).**
Prose intent is not enough to force thoroughness; the `investigate-health-write-check.sh` hook
gates the synthesis Writes on the existence of the upstream artifacts that *prove the required
dispatches actually happened*. This is the harness that forces the sequence. The contract:

- **Step 2 →** `step2-mechanism-map.md` contains a `## Processes` section enumerating each
  process as a `**Pn —` line (so the required builder-graph count is machine-readable).
- **Step 3 →** one `graphs/builder-<slug>.md` per process (blind, `INVESTIGATE-ROLE: builder`).
- **Step 4.5 →** `hypothesis-set.md` enumerates the hypotheses as `### Hn —` headers; the
  parallel-null hypothesis's header contains the word "null" (so the gate exempts it from the
  research requirement). Safety must-excludes are `S1/S2…` and are not subject to the
  per-hypothesis research requirement (they ride on the relevant mechanism's research).
- **Step 5 gate — the Write of `step5-cross-check.md` is BLOCKED unless ALL exist:** (a) for
  every non-null `Hn`, both `research/<hn>*consensus*.md` and `research/<hn>*practitioner*.md`;
  (b) `hypothesis-diversity-judge.md` (the diversity judge's verdict); (c)
  `research/practitioner-claim-rubric.md` (the consolidated practitioner-claim judge-council
  verdicts, OR an explicit `NO LOAD-BEARING PRACTITIONER CLAIMS — <reason>` line).
- **Step 7 gate — the Write of `offering.md` is BLOCKED unless:** the audit-council `offering`
  token exists (existing gate) AND `extracted/spot-check.md` exists (the independent extraction
  spot-check).

The gate fails closed with an actionable message naming what is missing. The ONLY legitimate
way past a genuinely-absent requirement is to write the explicit "none" artifact (e.g.
`research/practitioner-claim-rubric.md` containing `NO LOAD-BEARING PRACTITIONER CLAIMS —
<reason>`); there is no silent skip. These artifacts are the machine-checkable proof that the
thoroughness directive was honoured on this run.

**Gated-write compliance quick-reference (READ THIS BEFORE WRITING ANY GATED FILE — get it right
the first time).** Several PreToolUse hooks block Writes/Edits to the gated files and the right
language must be used *up front*, not discovered by trial-and-error. (Dispatched `INVESTIGATE-ROLE`
agents receive most of this automatically via `subagent-context.sh`; the **orchestrator doing inline
synthesis does NOT** — so when synthesis is inline, follow this list deliberately.) Gated files:
`working-hypothesis.md`, `step5-cross-check.md`, `hypothesis-set.md`, `step6-prioritize.md`,
`offering.md`. Hooks fire on Write AND Edit (an Edit is checked on its `new_string` only).

1. **Tier + source, same sentence.** Any sentence containing a tier marker `T0`–`T5` must also
   contain, in the *same* sentence, `[src: <file-or-S##>]` or `[ledger: <id>]` (or
   `verification: pending` / `orchestrator-memory only`). **Most robust: write tiers as register
   word-forms** — *established / studied / mechanistically plausible / temporal-only / speculative* —
   so no `Tn` token exists at all. If you must use `Tn`, put the citation right next to it. Never
   leave a bare `Tn` in prose.
2. **Never use `Tn`-style codes for non-tiers.** Code trials as **TR1…TRn** and waves as **W1…Wn** —
   NEVER `T1…Tn` or `T2/T3` (they collide with the tier regex). Discriminators as `D1…Dn` are fine.
3. **`[src:]` must resolve.** The filename must be a file you have **Read this session** (basename
   match) or an `S##` id. A file you only *wrote* is NOT in the read-log — Read it first, or cite it
   as `[ledger: <id>]`. Use `[ledger:]` for research findings you have summaries of but haven't Read.
4. **Label density (working-hypothesis / step2 / step5 / step6 / hypothesis-set).** Keep
   diagnosis-label tokens ≤ 1 per 200 body words; put ALL of them in a trailing `## Labels referenced`
   section, which must be the **last** section. Tokens (from `references/label-tokens.md`) are
   whole-word case-insensitive and **include acronyms ≥3 chars** — so spell out in body: *C-reactive
   protein* (not CRP), *erythrocyte sedimentation rate* (not ESR), *long-term blood sugar* (not
   HbA1c), *heart-rate variability* (not HRV), *thyroid-stimulating hormone* (not TSH). GOTCHA:
   tokens also match **inside hyphenated slugs and citation ids** — `[ledger: androgen-pcos …]` counts
   "PCOS", `[ledger: L2-CRP]` counts "CRP". Use label-free slugs/ids (`androgen-axis`,
   `h2-inflammation`). Edits < 100 words are exempt; mid-size edits get a tiny budget, so keep them
   label-token-free.
5. **Offering label-pairing (offering.md).** Every diagnosis label must be paired with a
   plain-language process description (meaning / pathway / process / mediator / mechanism) in the
   *same paragraph*.
6. **Register — lexical lint (write-check Check 5, ALL gated files; these exact patterns hard-deny).**
   Never write `fixable`, `will resolve`, `will fix`, `solves it`; `you should / you must / you need
   to`; `the actual/real finding/cause/driver/issue`; `PROVES at n=1` (write "n=1 causal proof").
   **"reversible" is PROTECTED, not banned** — "low-risk reversible trials" is core vocabulary; only
   *outcome-promises* (fixable/cure/will resolve/solves) are barred.
6b. **Register — "diagnosis" attribution (write-check Check 6, gated files).** `diagnosis`/`diagnoses`
   is denied in any sentence without a practitioner-attribution marker (record / note / chart /
   clinician / doctor / GP / practitioner / diagnosed / history of / listed / labelled / on file / was
   told / prior / previous / past medical). Use it ONLY when reporting a recorded one ("your records
   note a PCOS diagnosis"); for the tool's own or meta uses write **"diagnostic"** (label/conclusion) —
   `diagnostic` does NOT match the regex — or rephrase ("settles nothing", "which label fits").
6c. **Register — semantic class (NOT a regex; audit-council, finish-line item 7).** Directives to the
   person, treatment-sequencing, and high-consequence-flag phrasing are caught *semantically* by the
   audit-council in ANY wording — there is deliberately no keyword (the old `…steroid` regex was
   removed). So phrase every high-consequence flag as *information a clinician acts on* ("a clinician
   would want X excluded prior to any steroid course"), never a "before you take X" instruction; offer
   possibilities, never instruct; rank by cheapest/safest-to-explore. The finish line is now **7 items**
   (item 7 = register, audit-council-verified).
7. **Gate tokens / sequence.** `step5-cross-check.md` needs the research pairs + diversity judge +
   practitioner-rubric on disk first; `offering.md` needs the audit-council token + `extracted/spot-check.md`
   (see the required-artifact contract above).
8. **No deletion / no `rm` in scripts** under `<root>` before the finish-line (pre-tool-scan +
   cleanup-block). OCR scratch renders go to `<root>/extracted/_staged/_verify/` and are left in place.

**When something goes systematically wrong — halt, don't patch.** If a systematic
problem is discovered (an extraction error in the source data, an over-confidence
pattern in the working hypothesis, the same wrong assumption appearing in multiple places),
stop and re-audit all work done while the problem was active. Don't fix the one symptom
and move on — the same root cause will have affected other parts.

**When the same characterisation fails twice — stop and reorient.** If two successive
attempts to characterise the same observation have been wrong (a verdict given,
corrected, a second verdict given, corrected again), do not produce a third. Worked
example: a recurring skin itch is called "hives from heat" — the person says no, that's
not it. Next try: "contact dermatitis from the new soap" — also no. Do not now produce a
third confident verdict. Stop. Write down what each attempt actually ruled out (heat
isn't the trigger; the soap isn't the trigger), name the assumption all the attempts
shared (in this case: that the answer can be pinned to one cause right now from what's
already known), and switch the output from a verdict to a held-open candidate set plus a
discrimination plan — the few specific things to observe or try that would tell the
remaining candidates apart. Two failures at the same outcome — even via different routes
— means the shared assumption is the problem, not the next theory. The most common shared
assumption to check first: that the hypothesis has been shifting based on what the person
just said rather than on new evidence about the underlying biology.

**Audience separation.** The working hypothesis file is for the investigation; the
person-facing offering is for the person. Don't conflate them. Don't show internal
candidate-set noise to the person; don't dilute the working hypothesis with hypothetical-
register phrasing intended for the person.


---

## The finish line — what "ready to offer something" looks like

The investigation is detailed enough to offer something to the person when all of these
hold:

1. A working hypothesis exists that ties many of the observations into a connected account,
   with each claim tier-tagged and traced to a source, and with any weight-carrying natural
   experiments from step 1 explained (where such experiments exist).
2. For each load-bearing pathway in the working hypothesis, there's at least one possible
   way the person could interact with it — a trial, a practice, or where appropriate a test.
3. The set of trial options has been ranked by safety, breadth of mechanism they
   touch, and how quickly the person would know if it was helping.
4. For any pathway where no safe trial exists — because the relevant intervention would
   be high enough risk that taking it blind would be a problem — a test option is named
   alongside, with a plain description of what each possible result might suggest.
5. Anything the working hypothesis doesn't yet account for is named plainly. Honest gaps
   are part of what's offered, not a failure of the procedure.

If a connected picture can't be reached, what gets offered instead is **a clear
statement of what is still unexplained, and what evidence — a test, an observation, an
interview question — would help most.** That's a real result, not a failed procedure.

---

## Failure modes — recognise and stop

- **Restating known findings as a "hypothesis"** If your synthesis is a list of what was
  already in the inputs, you have a list, not a hypothesis. Re-do step 4.
- **Locking on the modal diagnosis.** If you named the most common condition without the
  blind upstream mechanism graphs (Step 3) and the complete shared-node enumeration
  (Step 4), you skipped the engine. Re-do them.
- **Recommending a test without saying what each result would change.** Every test in
  the offering needs "if A, these candidates become more likely; if B, these become less
  likely." Without that, the test is theatre.
- **Ranking by plausibility instead of effect size.** A candidate can be well-supported
  and still barely matter. If interventions are ordered by how sure we are rather than how
  much they'd likely help, re-rank.
- **Starting several things at once where attribution matters.** If a trial result can't
  be traced to one change, the signal is lost. Sequence for clean attribution (step 6).
- **Pricing or sourcing things from inference.** Any cost, availability, URL, or dose
  in the offering without a verified source isn't allowed. Verify, or tag as estimate.
- **Letting confidence escalate across rewrites.** If a claim was "mechanistically
  plausible" in the first draft of the working hypothesis and "studied" in the third
  without new evidence, the tiering has drifted. Re-check.
- **Producing the person-facing offering in directive language.** Anything that says
  "do X" or "you should Y" is a register failure. Rewrite hypothetically before
  delivery.
- **Treating structured notes as the data.** If you've stopped going back to the
  verbatim originals during cross-check, you're working from your own summary of the
  data, which will have drifted. Audit.
- **Continuing to interview when answers stop shifting the picture.** That's the signal
  to move to step 6 for the candidates that have saturated.
- **Treating "one model" as a constraint to lock down early.** The working hypothesis is
  meant to be multi-layered and to hold several parallel candidate accounts early on.
  Convergence happens through evidence over time, not through premature picking.
- **Proposing something already on the hard-no list.** Re-run the pre-flight check; this
  never reaches the person.
- **Weighting an unverified or un-quantified fact.** Any claim driving test
  priority, discriminator weight, or offering emphasis must trace to both a
  verification verdict and an impact qualification. If either is missing, the
  claim hasn't earned its weight. Cap and ask.
