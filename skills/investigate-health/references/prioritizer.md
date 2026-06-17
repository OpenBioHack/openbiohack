# Prioritizer step — investigate-health

The step that turns the addressable shared-node inventory into a designed first wave of
interventions plus the branch logic for what each result implies. Generalizable — no
condition, no molecule, no case is named here.

---

## What this step is — and is not

It is **not** "rank the inventory by importance and recommend the top few." Ranking by
importance / centrality / most-likely-root is the failure mode that repeatedly buries
cheap, broad, reversible probes underneath central-but-unactionable hubs — a node that
sits in many graphs is *more shared* precisely by being a generic hub, and importance-
ranking rewards exactly that.

It **is** the design of an **adaptive sequence of interventions**, for one reason that
governs everything downstream:

> Everything produced before this step — the mechanism graphs, the convergence, the
> shared-node inventory — is *observational* reasoning, and observation yields only
> **candidate** causes (T2–T3 plausibility). At N=1, the only thing that produces
> **causal** evidence (T1) is **intervention**: a `do()` on the system, watched. So the
> graphs *propose* causal edges; interventions *test* them. **The person's response to
> each action is the single most privileged piece of evidence in the whole investigation**
> — worth more than any node's centrality or any mechanistic story.

Therefore the investigation never assumes one pass yields the answer. This step emits the
**first wave** and the **rules for updating** — it hands over the first iteration of a
control loop and its branch logic, not a fixed ranking.

## Where it sits

Inputs:
- the **addressable shared-node inventory** (entity | mechanisms it spans | symptom
  domains it touches | specific reversible handle) — produced by: blind upstream builders
  → enumerate *all* shared nodes (no ranking) → addressability gate;
- the person's **findings, symptoms, and natural experiments**;
- the person's **treatment-response history** (what has been tried, what helped, what did
  not);
- the person's **hard-no list, constraints, and current regimen**.

This is the stage where person-specific context legitimately enters. The generation
(builders) stayed blind and the enumeration stayed neutral on purpose; bias is admitted
here, deliberately, because here it is being used to *prioritise actions*, not to *find
the answer*.

## The objective

Maximize **(expected quality-of-life benefit + discriminating information)** per unit
**(risk + cost + time-to-readout)**, subject to two **hard constraints handled outside the
optimization**:

- **Safety** — irreversible-harm-if-true candidates are pulled out separately; non-
  reversible interventions are gated out of the front-line set.
- **Attribution** — the sequence must preserve clean signal, or the result teaches nothing.

No weighted-sum-of-criteria formula is used — those weights are arbitrary and they collapse
a sequential problem into a static one. The objective above is the decision-theoretic core;
the steps below operationalize it.

**Why this objective is the *effective* optimum, specifically:** the binding constraint in
these cases is not effort or money — it is **uncertainty** about which candidate driver is
real. The most effective process is the one that collapses that uncertainty fastest while
delivering improvement along the way. Information-efficiency *is* effectiveness here,
because uncertainty is what blocks the result, and intervention is the only tool that
resolves it at N=1.

## The process

### 1. Partition for safety first (constraint, applied before any optimization)

Split the inventory into three **safety tracks** (numbered to stay distinct from the skill
register's rule-out *types* (a)–(d), which mean something different):
- **(Track 1) Rule-out-regardless** — any candidate where being wrong and leaving it unaddressed
  would cause irreversible, escalating, or time-sensitive harm. These go on a separate
  definitive-test track *regardless of how likely they are*, because the expected cost of
  missing them is high even at low probability.
- **(Track 2) Measurement-before-trial** — interventions not cleanly reversible, or carrying
  non-trivial harm. These require a measurement before any trial (the high-risk exception).
- **(Track 3) The safe, reversible pool** — everything else. **Optimize only over Track 3.**

### 2. Characterize each candidate on the axes that drive sequencing

Not to sum into a score — to feed step 3:
- **Breadth** — how many *distinct* symptom domains it touches (via the mechanisms it is
  shared across).
- **Expected magnitude** if it is active.
- **Prior that it is active in *this* person.** Treatment-response history enters here: a
  past response to something acting on a pathway *raises* the prior on that pathway's nodes;
  a clean non-response *lowers* it.
- **Speed of readout** — how fast you would know.
- **Reversibility / safety** (degrees remain within Track 3, the reversible pool).
- **Cost / access.**
- **Durability** — would acting on it correct a source (improvement persists after
  stopping, but slow to shift) or interrupt a cascade (faster, reverts on stopping)?
- **Discriminating power** — which of the competing shared-driver hypotheses its result
  would confirm or kill.
- **Confound footprint** — what other candidates it overlaps with (matters for attribution).

### 3. Value each as a *first move*, not by importance

The best first move is the one that — **whatever its result** — leaves you best positioned:
it banks likely benefit **and** its outcome re-ranks the remaining map. The properties that
dominate are **breadth × speed-of-readout × discriminating-power × reversibility**, because
those compound the learning loop. Centrality and "most likely root cause" are explicitly
**not** the objective. A candidate need not be the most central or the most likely driver
to be the best first move — it needs to be the safest, fastest-readout, broadest, most-
discriminating reversible probe, with its prior bumped by any prior response.

### 3b. Symptomatic-relief / load-reducer track (a parallel output, ranked differently)

The whole of step 3 ranks moves by their **value as a first move** — and a move's value
there is dominated by **discriminating power**: how much each result re-ranks the map. That
is the correct objective for *learning which hypothesis is right*. It systematically
under-values a different, legitimate kind of move: the **broadly-acting, reversible lever
that reduces symptom load without telling the hypotheses apart**. An antihistamine when a
histamine/mast-cell axis spans many of the graphs, a barrier-support layer, a sleep or
stress lever, a gentle anti-inflammatory — these can ease what the person actually feels
*while the discrimination loop runs in the background*, even though their result discriminates
nothing. Ranked only by discriminating power, they get dropped. That is a failure to deliver
**relief**, which sits in the objective (the "expected quality-of-life benefit" term) right
beside information.

So this step emits a **second, parallel track** — distinct from the discriminator wave and
ranked by a different rule.

- **What goes in it.** Draw from the **Step-4 addressable shared-node subset** (the same
  candidate set the discriminator wave draws from). A node belongs in the relief track when
  acting on it is expected to *reduce a symptom the person is living with* across one or
  more of the mechanisms it spans — independent of whether its result would separate any two
  hypotheses. A node can appear in **both** tracks (broad + discriminating is ideal); a node
  that is broad-and-safe-but-non-discriminating appears **only** here, which is exactly the
  point — it would otherwise be lost.
- **How it is ranked — NOT by discrimination.** Order by **symptom-relief expected ×
  breadth (distinct symptom domains it touches) × safety/reversibility × speed-of-readout.**
  Discriminating power is explicitly *not* a ranking term here; a relief lever earns its
  place by easing load broadly, safely, and fast, not by what its result teaches.
- **The same hard constraints still apply.** The safety partition from step 1 (rule-out-
  regardless, measurement-before-trial, reversible pool) and the **hard-no pre-flight** run
  on every relief item before it is surfaced, identically. Relief is not a licence to relax
  safety or attribution; it relaxes only the *requirement that a move discriminate*.
- **How it is framed — honestly, as relief not diagnosis.** Every relief item carries the
  explicit note: **"this does not test which hypothesis is right — it aims to ease symptoms
  while we sort out the cause."** It must not be read as evidence about the answer. (A relief
  trial *can* incidentally inform — e.g. antihistamine helping is weak support for a
  histamine axis — but that is a side-effect to note at its honest low tier, never the
  reason the item is in this track.)

The two tracks run in parallel and are offered together: the discriminator wave optimises
for *learning*, the relief track optimises for *living better while we learn*. Neither
replaces the other.

### 4. Prefer interventions that are simultaneously therapeutic and diagnostic

- **Trial-as-test.** Do not spend a slot on a pure measurement when a safe reversible
  *trial* would discriminate the same hypothesis and might also help. The response is the
  test.
- **Combination rule.** Combine interventions only when they act on **independent** pathways
  (so a win is still interpretable) — *or* deliberately combine when a single node is fed
  through multiple routes and acting on one route alone would give only partial relief, in
  which case the combined hit (e.g. reduce the dominant source + support clearance + blunt
  the action) is the correct unit, and a partial response to a single route is itself
  informative (the pathway is live; other routes remain).

### 5. Sequence for clean attribution

- Change one variable at a time where pathways overlap.
- Respect **build-up** and **washout** lags; derive the readout window from the mechanism,
  not a calendar default. A trial read before its build-up completes looks like a failure
  when it is a too-short trial; a new trial started before the previous thing has cleared
  reads the tail of the old thing.
- Name and hold steady the confounders in the person's routine.
- Apply attribution discipline **proportionally**: for moves that are broadly safe *and*
  broadly beneficial you may stack several; clean one-at-a-time attribution matters most
  when an intervention is costly, risky, or when learning is the explicit purpose.

### 6. Emit, then loop

Output is not a ranking. It is **two parallel tracks plus the supporting sets**:

- **First wave (discriminator track)** — the small set to try first *for learning*. Each
  carries: what it targets (which node / which mechanisms / which symptom domains), the
  specific reversible handle, *why it is in the first wave* (breadth / speed / discrimination
  / safety), the readout window (derived from mechanism, with build-up and washout named),
  and how to read the result.
- **Symptomatic-relief / load-reducer track (parallel)** — the broadly-acting, reversible
  levers from §3b, ranked by **relief × breadth × safety × speed, not discrimination**, each
  carrying its handle, the symptom domains it is aimed at, its readout window, and the
  explicit "this eases symptoms, it does not test which hypothesis is right" note. Surfaced
  *alongside* the first wave, never folded into it and never dropped for failing to
  discriminate. Hard-no pre-flight already run.
- **Branch logic** — for each first-wave probe: *if it helps* → what that confirms and what
  comes next; *if it does not* → what that rules down and what comes next. This is what
  makes it a loop rather than a list.
- **Parallel safety track** — the rule-out-regardless items from step 1, Track 1, surfaced on
  their own regardless of likelihood.
- **Deferred set** — every candidate not in the first wave, each held with the specific
  trigger (a result, an observation, a new datum) that would promote it.
- **Re-entry rule** — every new response or observation is T1 causal evidence that
  re-weights the whole map; the prioritizer re-runs. The loop continues until quality of
  life is adequate or the candidate map is exhausted.

## Register (inherited from the skill's non-negotiables)

- **Hypothetical, options-not-directives** throughout — "could be worth considering," "if
  you and your clinician chose to try A, what we'd be watching for is B." Never "do X."
- **Hard-no pre-flight** on every proposed item before it reaches the first wave.
- **Tier-honesty.** The graphs and the inventory are candidate causes (T2–T3). Only the
  person's response to an intervention upgrades a pathway toward T1. Confidence does not
  escalate across the loop except on the strength of actual response evidence.

## One-line statement of the principle

> Prioritise the interventions that buy the most quality-of-life improvement **and** the
> most causal information per unit of risk, cost, and waiting time — and let the person's
> response to each one rewrite the order. It is the optimum because it attacks uncertainty
> (the real constraint) with the only tool that resolves it (intervention), in the order
> that learns fastest without doing harm.

## Integration note

This file **is** the spec for the skill's Step 6 (Prioritize); it feeds Step 7 (Offer). The
trial-vs-test, sequencing, build-up / washout / hard-no / value-of-information / trial-as-test
/ consequence-if-ignored elements are special cases of the objective and constraints above,
folded in here rather than duplicated in a separate step. The load-bearing additions over the
older skill logic are: (1) the explicit
reframe of prioritisation as N=1 sequential causal experimentation with response as
privileged evidence; (2) value-as-first-move replacing rank-by-importance; (3) the emit-
first-wave-plus-branch-logic output replacing a static ranked offer; (4) the enumerate-
then-gate-then-prioritise ordering that prevents importance-ranking from burying cheap
broad reversible probes; (5) the parallel **symptomatic-relief / load-reducer track**
(§3b), ranked by relief × breadth × safety × speed rather than discrimination, so broadly-
acting reversible levers that ease symptoms without discriminating are surfaced instead of
dropped for "not telling the hypotheses apart."
