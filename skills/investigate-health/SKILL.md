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

> **Single source for the register + evidence tiers:** `references/register.md`. The workflow
> driver injects it into every analytical dispatch, and it is the canonical home of the 0.1
> rule, the T1–T5 causal-certainty tiers, the T0–T3 source-fidelity ladder, and the
> cross-subject / prompt-injection guards. The tier tables restated in the framing below are
> for the human reader; when they and `register.md` differ, `register.md` wins — do not
> re-home the tiers here.

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

**Held open, not resolved early — a PHASE-A rule, not a permanent ban on convergence.**
*During locating (Phase A),* when a symptom isn't clearly locked to one trigger and several
things could plausibly be contributing, the correct early output is a held-open candidate set
plus a discrimination plan — not a single verdict. A verdict per turn isn't depth; it's the
opposite. Convergence happens through evidence (trial results, new observations, test outcomes,
documented elimination), not through picking the most-likely candidate on the strength of the
last message. **The scope of this rule is Phase A.** It governs the breadth stage, where holding
open is correct because the work of discriminating hasn't been done yet. It is **not** a mandate
to hedge flatly forever: once Phase B has *earned* convergence through documented elimination
(each demotion citing the constraint or observation that did it), the offer probabilistically
prioritises and states a leading plausible narrative. Holding everything equally possible after
the elimination work is done is the same failure as declaring a single winner before it — both ignore the
evidence. Held-open early; prioritised (never declared a single winner) once earned.

**Register — probabilistic prioritisation expressed as a plausible narrative (the 0.1 rule,
applies to EVERY operation and prompt, internal and external).** The output of a finished
investigation is neither a diagnosis nor a flat "everything is equally possible" hedge. It is a
*probabilistic prioritisation expressed as a plausible narrative.* The offer says, in substance:
*"the hypothesis that appears to most closely align with the facts so far is X; a plausible
narrative tying your symptoms and results together is …; some of these may be running
concurrently; here is why X is prioritised over Y, and why Z was demoted (with the evidence that
demoted it)."* It is always **a plausible narrative, not an explanation** — everything stays
probabilistic and open; nothing is ever stated as "definitely this," and nothing is presented as settled. This
register is written into **every prompt this skill runs**, including the internal synthesis and
depth-dispatch prompts, not only the final offer. Banned in service of it: declaring-a-single-winner / diagnosis
language; superlatives ("single biggest"); a flat hedge with no committed lean once the
elimination work is done; presenting **process-completion** ("all PASS / the council cleared it")
as if it were a **quality** claim; and offering a needless opt-in **(a)/(b) menu** when both steps
obviously need doing (just do both — see the banned-class list below).

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
| Grandparent, grandchild, aunt, uncle, niece, nephew, half-sibling | **2nd-degree** | ~25% | MS 2nd-degree: ~0.4-1% lifetime vs ~0.1% pop (Compston/Coles 2008 review) |
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

**Context recovery (the 0.7 rule) — after any compaction or context loss, re-read before
continuing.** A long investigation will be compacted. A compacted summary is a lossy interpretation
of the work, not the work. After any compaction or context loss, the first action before any further
reasoning is to **re-read the session's actual research files and working documents** — the
`extracted/` and `compiled/` views, the per-step artifacts, the working-truth ledger, the convergence
and mechanism-map files — and reason from those, never from the compressed summary. A post-compaction
state is **not trusted** until the underlying documents are re-read; treat the summary only as an index
of what to re-open. This mirrors the project-level rule that the user should never have to re-paste
context: the documents on disk are the source of truth, and recovering them is the first move, not an
optional one.

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

**Authority is a third axis — and it carries a NO-OVERRIDE rule.** The tiers above measure *causal
certainty*; the evidence hierarchy (further down) measures *study quality*. Neither measures
**specificity-to-this-subject (n-of-1 relevance)** — and that is a distinct axis. For a conclusion *about
this person*, the **person's own measured data and their directly-experienced lived report are the top
authority**, above any population/general evidence however high its study quality. (T1 already says "or
direct measurement of this person's own data"; this makes that explicit and adds lived report.) The rule:
*a general/population claim — at any study-quality tier — may REFRAME or CONTEXTUALISE a higher-authority
own-data / directly-experienced observation about this person, but may NOT by itself OVERTURN it.* To
overturn a top-authority observation you need other top-authority evidence (the person's own
data/experience), not a textbook, a population average, or a single timeboxed agent's "didn't find." This
is what stops the authority inversions: a blind agent's prior must not override the live interview; a
timeboxed null must not override "we have not actually looked" (no-evidence ≠ negative); a population
average must not override a standout finding that demands its own mechanism. This axis is held as
persistent state — see the **Working-Truth Ledger** (`<root>/working-truth.md`; full spec
`references/working-truth-ledger.md`), the authority-ranked, status-latched, disconfirmation-pruned object
the engine reads first and updates last at every synthesis step. **It is lens-agnostic:** in the OPTIMIZE
lens the person's own *response data* is still top authority, reconciled against, looped back to, and
parked/re-raised by evidence in exactly the same way.

**Veracity — quoted data, timing and sequence must be real (a separate check from authority).** The
no-override rule cannot catch a *fabricated* relationship — two facts from different dates lined up and
asserted as a correlation ("best while load was highest"). That is a veracity failure, and it needs its own
pass. Before any claim that quotes data is committed — **especially any temporal / sequencing / ordering /
"X tracks · coincides-with · rose-after · best-while Y" claim** — in a pass *separate from writing the
prose*: re-fetch each quoted datum (value, date, what the source says) from its source; for any
timing/sequence/ordering claim confirm **both** endpoints are actually dated in the record and the ordering
is correct; restate the verified chain. A claim whose endpoints do not both resolve is struck or downgraded
to "timing unknown." This generalises the recombination agent's temporal-claim gate to every synthesis
write, and is enforced both structurally (a temporal/sequence sentence must carry a source **+ date**
citation) and semantically (the Step-7 veracity-auditor re-derives each quoted fact from source).

**Register vocabulary (canonical, enforced — applies to EVERY artifact, EVERY dispatched sub-agent, AND
every word the orchestrator narrates to the person in chat).**
This is the single source of truth for register words. The `subagent-context` hook injects it into every
role; the `write-check` hook lints every written artifact against it; `eval/case-12-register` regression-
tests it. **But the hooks govern files and sub-agents only — no hook can lint the orchestrator's chat. The
chat is therefore the one place the register runs on the honour system, and (per the live-run post-mortem)
the place it most often slips: disciplined, hedged, unranked files get narrated back to the person as bald,
ranked, over-confident assertions. Apply every rule below to your chat narration exactly as rigorously as to
a gated file — see "Conversational register" below.** Banned vocabulary, by class:

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
- **Hyperbole, ranking & false-precision (never — possibilities are held in parallel; the procedure does
  not declare a single winner):** *the biggest / single biggest / biggest single / single most / the main / the
  primary / the dominant [thread / driver / factor / story], the strongest frame, the key thing, what's
  really going on.* Do **not** rank a "winner" or a "biggest" anything — the hypotheses are held in
  parallel, and it is the *differences between them* (the cheap discriminating tests), **not** a ranking,
  that define the next step. Also banned as causal overreach below T1: *likely explains, explains the,
  accounts for, is driven by, points to [X] (as a verdict), reads as [X], doesn't actually
  [support / mean / meet], didn't touch / didn't help.* State trial results as plain observations —
  *"the elimination trial did not noticeably change the symptom"* is fine; *"the trial didn't touch it, so
  it's not fermentation"* is not. Replace every one of these with a possibility frame.
  **Scope note (declaring-a-single-winner vs earned prioritisation).** This bans *declaring a single winner* — flat superlatives and
  stating a single winner as the answer. It does **not** ban the **earned probabilistic prioritisation**
  the 0.1 rule requires at the Phase-B offer: *"the hypothesis that appears to most closely align with the
  facts so far is X; here is why it is prioritised over Y, and the evidence that demoted Z."* The
  difference is the work behind it and the framing on top of it — a prioritisation carries its
  demotion-evidence and stays probabilistic ("appears to most closely align," "a plausible narrative");
  presenting one as settled asserts a winner as settled fact. Hold-open during Phase A; prioritise-with-reasons (never
  declare a single winner) at the Phase-B offer.
- **Process-completion-as-quality (never — finishing a process is not evidence the output is good):**
  presenting the *completion of an internal process* as if it were a *quality* claim about the findings.
  Markers: *"all auditors PASS," "the council cleared it," "every gate passed, so this is solid," "fully
  validated," "the checks all came back green."* That a council ran and returned PASS means the procedure
  was followed — it is **not** a claim that the analysis is deep, correct, or complete, and must never be
  narrated to the person (or written into an artifact) as though it were. The June post-mortem run passed
  its own auditor council while being shallow; that is exactly the failure this ban names. Report findings
  on their own merits and at their own tier; never substitute "the process cleared it" for substance.
- **Needless opt-in menu (never — do not offer an (a)/(b) choice when both steps obviously need doing):**
  presenting a fork — *"would you like me to (a) do X or (b) do Y?"* — when both X and Y plainly need to
  happen for the work to be right. Offering the menu pushes a decision onto the person that isn't really
  theirs to make and reads as the procedure looking for permission to do less. Just do both, then report.
  (A genuine either/or where only the person can choose — their goal, their geography, which targets to
  source — is *not* this; that is a real choice and belongs to them. The ban is on the *false* menu where
  the honest answer is "both.")

**Required probabilistic frame (use instead):** *candidate, possible, may, could, one pattern that could
fit, one of the things that could be contributing, it might point toward, possibly has features of, on the
evidence so far it could be, worth considering, worth discussing with your clinician, among the more
addressable possibilities here.* When you repeat a claim a research sub-agent produced, **carry its hedge
and attribute it** — *"one consensus source frames the finding one way, though that describes
the general population rather than your case"* — never restate an agent's claim as a bald fact.

**Conversational register — the chat is in scope, and is where it slips.** Everything you *say* to the
person obeys the rules above, not only what you write to disk. **Think with the nuance of a Keegan level-5
thinker — everywhere, in the files and *especially* in the chat.** Concretely:
- **Never rank or declare a single winner.** No "the biggest single thread," "the strongest frame," "the main driver."
  Present the competing possibilities as a *set* and let the cheap discriminating tests — not a ranking —
  carry the next step. Declaring a single winner in chat also contradicts `hypothesis-set.md`, which is held in
  parallel and **not ranked** by design.
- **Carry the tier into the sentence.** If a file states something at *mechanistically-plausible* with a
  ledger cite, the chat says "one possibility that could fit…," not "X reads as Y." Never upgrade a hedged,
  attributed file line into a chat verdict.
- **Synthesise the whole set, not document-by-document.** Don't narrate a running verdict as you read each
  artifact ("read this → weakens H1; read that → reframes H5"). Read the relevant set, *then* give one
  holistic, hedged summary — per-document verdicts both anchor your thinking and read as overconfident.
- **The honest sentence is usually longer and softer.** "It could be one of the contributors to the
  symptom, alongside a couple of other possibilities we can't separate yet" beats "the symptom reads as
  a single mechanism." Choose the former every time.

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

## Mechanism-depth interrogation (close shallow holes before a human has to)

Every load-bearing mechanistic explanation this procedure produces — a hypothesis's causal chain (drafted
as a skeleton at Step 4.5, fully interrogated when the hypothesis is deepened at Step 5.7 / B3), a node in a
mechanism map (B3), or how a proposed intervention acts on a node (Step 6) — must pass this interrogation
**before that explanation is relied on** (before a deepened hypothesis, a mechanism map, or a proposed item
is accepted). Ask each probe **of your own draft**. A probe is **closed** only when
it is either (i) answered from cited evidence, or (ii) explicitly marked as an *evidence-edge* with a
measurement-edge estimate (see the measurement-edge check in B3). An unclosed probe is **not a finished
explanation**: it triggers a targeted `/research` + `/research-practitioner` dispatch on *exactly that hole*,
after which the probe is re-asked. **Loop until every probe is closed. Terminate on closure — never because
the prose "reads well" or you judge it good enough.** The purpose is to make the procedure catch its own
shallowness the way a rigorous reader would, instead of a person having to push back round after round.

The probes:
- **WHAT** — is every actor named at the specific level (the exact molecule, enzyme, gene, cell type,
  microbial family/species)? A vague noun standing in for a mechanism — *"certain bacteria," "the barrier,"
  "inflammation," "supports gut health"* — is an **unclosed** probe.
- **BY-WHAT** — is each step a *verb-chain* (X does this to Y, which causes Z), or a *noun-claim* asserting an
  outcome with no mechanism behind it (*"improves the barrier," "calms inflammation"*)? An outcome with no
  chemistry is **unclosed**: name what binds / cleaves / activates / blocks / fuels what.
- **WHERE** — is the anatomical location of each step given (which compartment or segment, which cell type;
  for a secreted or active factor, where it is produced vs where it acts)? Absent location is **unclosed**.
- **HOW-MUCH** — for any step whose strength depends on an amount, has the measurement-edge check run
  (concentration needed vs reachable, commensurable comparison, measured-or-estimated)? An amount-dependent
  step with no measurement-edge verdict is **unclosed**.
- **MEASURED-OR-EXTRAPOLATED** — is it stated whether this was actually measured in *this* subject / *this*
  context, or carried over from another species, an in-vitro system, a different compartment, or a different
  dose? Silence is **unclosed**.
- **RESIDUAL** — after the research, what about this mechanism is *still* not known or not explained? Name it.
  "Nothing unexplained" is acceptable only if every probe above closed with evidence; otherwise the residual
  **is** the honest hole — flag it (and it feeds the B9 back-of-envelope invitation).

If a probe cannot be closed even after targeted research, it is an **evidence-edge**: record the
measurement-edge estimate and the explicit "this has not been measured/studied" flag, and stop — that is
closure by honest limit, not by giving up.

---


## The procedure — the workflow drives it (this skill is thin)

The Step 0→8 procedure is no longer walked from this document. It is owned by a
deterministic **Workflow driver** (`investigate-health-orchestrator`) that runs the fixed
sequence, dispatches each step to a fresh sub-agent pointed at its canonical
`references/<step>.md` spec, injects the register (`references/register.md`) into every
analytical dispatch, and verifies each artifact on disk before advancing. A step cannot be
skipped or reordered, because CODE — not this prose — decides what comes next.

This skill owns only the three **non-deterministic, conversational** turns the driver
cannot: (1) locating the person's data, (2) running the live interview, and (3) surfacing
the finished offer. Everything between is the driver's.

### 1 — Locate the data and launch

Establish the investigation **run root** (the directory holding the person's `data/`), then
launch the workflow. The root is where every artifact is written; `data/` holds the raw
sources the driver's Step 1 extraction reads.

```
Workflow({
  name: 'investigate-health-orchestrator',
  args: {
    root: '<ABSOLUTE run root>',     // the subject's investigation dir (contains data/)
    failClosed: false,               // warn-mode first; arm (true) only after a clean warn run
    // refsDir defaults to ~/.claude/skills/investigate-health/references (ABSOLUTE);
    // pass an explicit absolute refsDir if the skill is not installed at the default path.
  }
})
```

Register and evidence discipline live in `references/register.md` (the single source the
driver injects). The tiers and guards quoted in the framing above are canonical **there** —
this document does not re-home them.

### 2 — The interview pause (the one human turn)

Workflows cannot take mid-run input, so the driver runs to the Step-5.5 interview, writes
`question-bank.md`, and **returns `{ paused: 'interview' }`** without blocking. When it
does:

1. Present the questions in `<root>/question-bank.md` to the person, in their language.
2. Write their answers to `<root>/interview-answers.md`.
3. **Resume** the same workflow with `args.resumeFrom` set (plus the same `root`).
   The driver continues 5.7 → Phase-B → 6 → offer with no orchestrator in between.

Do not answer the interview questions yourself, and do not skip the pause — it is the only
point where the person's lived report enters, and the whole investigation is calibrated on it.

### 3 — Surface the offer

When the driver completes it returns the path to `<root>/offering.md` (a faithful,
provenance-stripped strip of the audited draft). Surface it to the person as **possibilities
to consider and discuss with their clinician** — never as instructions, never as a diagnosis
— honouring the register above. Then offer the Step-7.5 deeper-pass invitation
(`open-threads-and-invitation.md`) if they want to go further.

### If the driver halts

The driver returns `{ halted: true, atStep, reason }` and writes `RESUME.md` when a gated
artifact is missing/malformed on disk (a write-gate denial or a skipped step). Read the
reason, address it (usually: the named artifact was not produced), and resume. A halt is the
driver refusing to proceed on incomplete work — it is the safety behaviour, not a failure to
route around.
