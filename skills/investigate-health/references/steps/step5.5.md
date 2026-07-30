### Step 5.5 — Interview (a forced multi-pass discrimination engine)

The cheapest, fastest discriminator for many remaining ambiguities is the person's own
direct experience. But a single improvised round of questions does not capture it — a real
interview **generates** a large research-grounded question set, **subtracts** what the data
already answers, asks the survivors in **ranked passes**, **re-ranks and re-targets** from
the answers, and (when the result is messy or anomalous) **blindly recombines** all the data
to surface hypotheses no one on the team named. A hard programmatic gate (the Step-6 gate,
below) means a single shallow round cannot pass.

**The spine:** `GENERATE → SUBTRACT → PRUNE (Pass 1) → RE-RANK + TARGET → DIFFERENTIATE/RESURRECT
(Pass 2) → [trigger?] RECOMBINE-BLIND → converge | loop`.

**No question is ever improvised.** Every question asked at any pass is research-generated —
either harvested from the Step-5 `## Differentiating diagnostic questions` sections, or
produced by a real top-up `/research` + `/research-practitioner` dispatch. The orchestrator
never authors interview questions from its own head.

#### Phase 0 — Generate (mandatory, research-grounded)

Precondition (already enforced at Step 5): every per-hypothesis research output carries a
`## Differentiating diagnostic questions` section with per-question
`expected-answer-per-hypothesis` (forks flagged), qualitative `sensitivity`, and
qualitative `specificity`.

**Harvest** those sections from every `research/<hn>-…-consensus.md` and
`research/<hn>-…-practitioner.md` into `<root>/question-bank.md`, one `## Question pool — <Hn>`
section per non-null hypothesis. Aim for the full research-generated set per hypothesis
(the pilot precedent is many questions per candidate, ~20–30 generated before subtraction),
each row carrying its tags.

**Top-up where thin.** Where a hypothesis's harvested set is thin, or a round-2 hypothesis
has no harvested set yet, **dispatch a real paired `/research` + `/research-practitioner`
top-up** writing `research/<hn>-questions-topup-…-consensus.md` and
`research/<hn>-questions-topup-…-practitioner.md`, each carrying the same mandatory
`## Differentiating diagnostic questions` section. The top-up is a genuine research dispatch
— **never orchestrator-authored questions.** Harvest its output into the same pool section.

#### Phase 1 — Subtract-from-data

For each pooled question, check it against `<root>/extracted/` and the records and mark its
`disposition`: `answered (cite src)` / `partial` / `open`. Only `open` and `partial` questions
survive to be asked. This is what turns ~20–30 generated questions per hypothesis into the
~10–15 that are actually worth a person's attention.

#### Pass 1 — Prune (high-sensitivity)

Ask the top **high-sensitivity** questions plus any **fork** questions per live hypothesis —
the questions whose NO meaningfully prunes a candidate. Batch to what the person can engage
with well in one sitting (judged by their bandwidth and the discriminating value of each
question — **not** capped at a fixed number like six; a rich case warrants more, a tired person
fewer). Wait for answers. NO answers prune; a YES **strengthens but never confirms** — only
timing evidence and an on-off-on rechallenge prove causation at N=1 (the existing rule).

#### Reflect back + confirm (mandatory, before any re-ranking)

After each pass, **reflect the answers back to the person in bullet points — the key results and data
as you heard them — and get their confirmation or correction before re-ranking anything.** This is not
optional politeness; it is an error gate. Interview answers are spoken, compressed, and easy to mishear
(a single misread — e.g. "the symptom started *at* a datable event" when the person said it started *a
month or two after* — silently corrupts onset-locking and every downstream tier). The person is the only
one who can catch that, and only if you show them what you recorded. So: list what you heard per answer,
flag anything you inferred vs were told, and ask "did I get this right?" Correct the record from their
reply, then proceed. A reflected-back answer the person confirms is hardened evidence; an unconfirmed
paraphrase is a liability.

**Capture a confidence % + provenance per answer (D7) — this sets the answer's authority.** Interview
answers are top-authority evidence (the no-override rule, register §"Authority is a third axis"), but not all
answers are equally reliable, and **certainty is not reliability.** For each answer, capture two things and
record them with the answer in `interview-answers.md`:
- a **confidence as a percentage** — *always a %, never a 1–5 scale* (ask "how sure are you, as a rough
  percent?");
- the answer's **provenance**, captured by asking in plain language: *how long ago was this? how sure are you
  of the memory? is this from memory, or from your notes / records? or is it something you're assuming or
  inferring rather than something you directly experienced?* Record one of: `from-notes`,
  `clear-recent-memory`, `hazy-memory`, `inference`.

Do **not** use a "directly-experienced vs recalled" axis — you always recall even something you directly
experienced, so it is not a clean boundary. Weight (and authority under D1) is set by **provenance + the %
together**: a from-notes/records or recent-clear-memory answer weights high; a hazy long-ago memory, or an
inference/assumption, weights **down even if the person states high confidence.** This feeds the persisted
confidence band (D2). Full axes and tier-ceilings: `references/rubrics/self-report-pattern.md`.

**Conduct — ask the questions directly.** A person who came to understand their body will answer however
many questions the investigation needs. Do not pad questions with apology, time-anxiety, or "if it's
quick / sorry to bother / I know you're busy" hedging, and do not shrink the set to seem fast — that
underserves them. Ask plainly. Cap each round at ~10 questions (a readable batch), and make each question
a distinct discriminating axis (see Pass 1 — dedupe the pool so you are not asking the same axis five
ways). Thoroughness over speed: the cost that counts is a missed discriminator, never a few more honest
questions.

**Never force a false either/or — offer the open option.** When a question contrasts two patterns ("many
small meals vs few large," "morning vs evening," "better vs worse after X"), do not make the person pick one
of two when the truth may be **neither, both, or a third pattern.** Always include the open alternative —
"…or is it something else / neither / it varies / you're not sure?" A forced binary manufactures a
data-point the person didn't actually have, which then corrupts the ledger. The dimension is the question;
the two named patterns are only examples of where on it the answer might land.

**Ground every question in what is already known.** Before asking, check the question against
`medical-history.md`, the diet/intake on file, and the available test list — and drop or rewrite any
question the known context already moots. Asking someone who eats a near-identical diet every day to
"compare big-meal vs small-meal days," or someone who never eats between meals to "eat at the symptom
peak," or asking to "track symptoms against a test" when only two tests exist, wastes the person's
goodwill and signals you didn't read their file. A question must be answerable *given this person's
actual life*, not a generic patient's.

#### Re-rank + target

Update the Step-5 ledger (`step5-cross-check.md`) from the answers and re-rank the hypotheses
by evidence weight (anti-escalation rule intact — confidence at the end of the round may not
exceed confidence at the start unless new biological evidence justifies it). Then select the
Pass-2 questions per candidate by its post-Pass-1 state:

- **Eliminated and conclusively so** (a high-sensitivity NO, aperture adequate) ⇒ **stop**
  that candidate; no Pass-2 questions for it.
- **Eliminated but not conclusively** (weak NO, or a NO whose aperture doesn't fully cover the
  candidate) ⇒ pick **falsification-framed resurrection** questions — phrased to give the
  candidate a fair chance to come back, never to lead the person toward reviving it.
- **Co-strengthened across several candidates** (two or more rose together) ⇒ pick
  **high-specificity / fork** questions that separate the co-leaders — the shared-question /
  different-expected-answer items are the sharpest separators.

#### Pass 2 — Differentiate / resurrect (+ anomaly capture)

Ask the selected Pass-2 questions **from the existing bank** (no new research needed for Pass 2
itself; new research is only triggered by a *new hypothesis* — see recombination). Capture, in
a `## Anomalies` section, any answer that fits **no** current hypothesis, is internally
contradictory, or just doesn't sit right — do not discard it to keep the model tidy; a
weird answer is often the thread to a missed candidate.

#### Recombine-blind (triggered, not mandatory) — a NEW-HYPOTHESIS GENERATOR, never a synthesizer

Trigger this when Pass 2 came out **messy** — no clean discrimination, co-leaders still
unseparated, or no candidate reaches a confident tier — **OR** when ≥1 anomaly answer suggests
something outside the current hypothesis set.

**Its job is narrow and additive.** The recombination agent exists to answer ONE question: *given all
the evidence, is there a process the current hypothesis set does NOT already name?* It is a generator of
**candidate new hypotheses**, nothing more. It must **NOT** re-rank, weight, or issue verdicts on the
existing candidates; **NOT** demote or promote anything; **NOT** synthesize the step or declare what the
answer is. (The cross-check, Step 5, is the synthesizer — never this agent.) If it finds nothing the set
is missing, the correct output is "**no new candidate**." Treating its output as the step's synthesis —
or letting it pass judgement on existing hypotheses — is a defect; that misuse is exactly how an
unverified guess once got propagated as a finding.

**Feed it structured, dated facts — not raw files to timeline itself.** The hallucination risk is highest
when the agent must reconstruct a timeline from raw documents (it will align two facts from different
dates and invent a correlation). So the orchestrator first builds a clean input packet:
- a **normalised observation list** — each load-bearing fact written as one line with its **source and
  date already attached** (`<observation> [src: <file>, <value/date>]`), so the agent reasons over
  pre-dated facts and never has to derive timing itself;
- the **existing hypothesis names only** (so it knows what "new" means) — **without** their tiers,
  rankings, or verdicts (so it is not anchored);
- the task: "Propose any process these observations require that is NOT already in the named list. For
  each, cite the specific observations that demand it. If none, write 'no new candidate.'"

**Anti-hallucination output contract (enforced in the prompt and checked on return):**
- **Every assertion carries an inline citation** to a specific datum (`[src: <file>, <exact value/date>]`).
  An uncited assertion is not allowed in the main body — it goes in a fenced **"speculative — do NOT
  weight"** section or not at all.
- **Temporal / causal claims are high-risk and gated:** any "coincided with / rose after / best while X
  was highest / improved when Y" claim must cite **both** dated endpoints and show they actually
  co-occur. If both dates are not in the record, the claim is **forbidden** — write "timing unknown"
  instead. (This is the exact failure to design out: do not infer a correlation by aligning two undated
  or differently-dated facts.)
- It states only what the evidence supports; it does not "explain everything."

**Verification gate before any use.** The orchestrator (or a dispatched verifier pass) checks that **every
cited claim resolves to the actual datum** in the named source before anything from the recombination file
is used; any claim that fails is struck. Nothing from this agent is written into a gated artifact
(`step5-cross-check.md`, `step6-prioritize.md`, `offering.md`) as a weighted finding. A genuinely new,
verified candidate **re-enters through the normal pipeline** — a paired **round-2 `/research` +
`/research-practitioner`** dispatch ⇒ re-entry at **Step 3** (routes) and **Step 4.5** (hypothesis-set),
where it then earns its own `## Differentiating diagnostic questions` and Phase-0 harvest and is tiered by
the cross-check like any other hypothesis. Record the outcome (new candidate + verification result, or "no
new candidate") in `## Recombination-check`. Per "No summaries, ever," the agent writes
`<root>/recombination-<n>.md` and returns done + path.

#### Converge / loop

Stop interviewing when **no pair of live candidates is subjectively separable** any further,
recombination yields nothing new, and anomalies are either explained or explicitly parked.
Two guards prevent infinite looping:
- **Per-candidate two-no-shift-rounds.** After each round, compare the candidate's ledger entry
  before and after. If nothing changed — no new supporting/contradicting evidence, no tier
  movement, no new ambiguity — that's a **no-shift round**; log it. Two no-shift rounds in a row
  for the same candidate ⇒ it is interview-saturated; move it to Step 6. One isn't enough (one
  poorly-aimed round could explain it).
- **Hard pass-ceiling.** A run may not exceed a small fixed number of full passes
  (default 4); reaching it forces convergence to Step 6 with whatever separation exists, the
  remainder handed to the discriminator design. Complexity sets the *minimum* (≥2 passes, gated);
  the ceiling sets the maximum.

**Per-candidate, not global.** Passes aren't a single global phase — some candidates saturate at
Pass 1 while others stay interview-discriminable into Pass 3. Handle each candidate's switch to
Step 6 independently. Where two candidates are two biological pathways producing the *same* felt
experience, subjective report genuinely can't separate them — stop interviewing that pair and let
Step 6's discriminator design do it.

**Anti-leading-question guard (applies to every pass, hardest at resurrection).** Self-report bias
bites most when a question telegraphs the answer the investigation is hoping for. Before asking any
question — especially a resurrection question, where the pull to revive a favoured candidate is
strongest — check it does not name the expected answer, the condition, or the mechanism. Describe
the dimension; let the person fill it in.

**Interview substrate — pre-existing transcripts.** If `<root>/extracted/` already contains
interview transcripts or daily symptom notes (the subject was interviewed before this run, or the
pack arrived with prior interviews), those are the primary substrate: harvest answers from them in
Phase 1's subtract step (each pooled question they answer is marked `answered (cite src)`), and
only `open`/`partial` questions survive to be asked live. Questions with no live touchpoint yet are
kept in their pool with `disposition: open` and surfaced in the offering as "to ask next time."

**Interview-blocked — no live interlocutor.** If there is no live interlocutor *and* no
pre-existing interview material to subtract against, a multi-pass interview cannot run. Write the
escape marker `INTERVIEW-BLOCKED — <reason>` as the **first line** of `question-bank.md`, leave the
harvested pools in place as the "to ask next time" deliverable, and proceed to Step 6 / Step 7 with
the offering plus the question list. Symmetrically, if Pass 1 genuinely saturates every live
candidate at once (every pair either separated or proven inseparable, no anomalies, no
recombination trigger), write `INTERVIEW-SATURATED-AFTER-PASS-1 — <reason>` as the first line. Both
markers are the legitimate ways the Step-6 gate's ≥2-pass requirement is satisfied without two
passes — they are not silent skips; each names its reason and leaves the pools on disk.

**Data hygiene — interview transcripts and daily notes are sources too.** They carry the same drift
risk as any source. So they go through `/extract-health-data` like any other source — an incremental
update that preserves the verbatim original, tags every derived claim back to its source line, and
re-derives the affected compiled views. That sub-skill owns the verbatim-original and traceability
discipline; don't re-implement it here. Each new daily note triggers the same incremental update,
then cross-check (Step 5), then the loop re-enters at the affected step.

#### `question-bank.md` — machine-checkable contract

`question-bank.md` is the deliverable of Step 5.5 and the surface the Step-6 gate verifies. It
contains, in this structure:

- **Escape markers (first line only, when applicable):** `INTERVIEW-BLOCKED — <reason>` or
  `INTERVIEW-SATURATED-AFTER-PASS-1 — <reason>`. Either one closes the ≥2-pass requirement
  legitimately.
- `## Question pool — <Hn>` — one per non-null hypothesis, holding the harvested (and topped-up)
  questions as rows: `q-id | text | expected-answer-per-hyp | sensitivity | specificity |
  disposition (answered | partial | open) | src-if-answered`.
- `## Pass log` — one `### Pass N` block per pass (N ≥ 1), each recording the questions asked, the
  person's answers, the resulting tier movements, and any no-shift flags.
- `## Anomalies` — answers that fit no current model (may be empty, but the section exists).
- `## Recombination-check` — a line `triggered: yes/no — <reason>`; if `yes`, the new-candidate
  verdict and a pointer to `recombination-<n>.md`.

The Step-6 gate (see the required-artifact contract) blocks the Write of `step6-prioritize.md`
unless this file shows: a `## Question pool — <Hn>` section for each non-null `Hn`, dispositions in
use, **≥2 `### Pass N` blocks**, and a `## Recombination-check` entry — OR an escape marker on the
first line.

*Output:* `<root>/question-bank.md` to the contract above (harvested pools, pass log, anomalies,
recombination-check), plus the updated `step5-cross-check.md` ledger after each pass and a
per-candidate status of "still interview-discriminable" versus "needs a discriminator."

