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

**Two kinds of mechanism map — build BOTH, early.** The map above is built **blind from symptoms** (process
maps for what could produce the felt experience). That blind, symptom-driven mapping is valuable and stays —
and it is worth keeping *some* maps deliberately symptom-only, because reasoning forward from the felt
experience surfaces routes a result-anchored map would miss. But on its own it misses the deep biology of
the person's *actual measured anomalies*. So **also** build, at this same stage:

- **Test-result-anchored mechanism maps (Dm).** For **each out-of-bounds / anomalous result** — each
  overgrown organism, each out-of-range lab / hormone / marker — build a dedicated mechanism map of its core
  biology via a paired `/research` + `/research-practitioner` dispatch (named output files per the research
  contract). Each asks *what this thing actually is and does*: what it consumes and produces (gases,
  metabolites, proteases, mediators), what is **upstream** (what could drive this value out of range) and
  **downstream** (what this value in turn affects / drives), and the conditions under which it shifts from
  benign to meaningful — and the anatomical location of each step (which segment and cell type; for a secreted or active factor, where it is produced vs where it acts). This **generalises** the standout/extreme-finding → mechanism-map rule (see "How the
  loop is actually run") from *the largest-magnitude* outlier to **every** anomaly — scaled by degree-out-of-
  range so it stays tractable, but comprehensive in principle. Build it **early, not in loop-back:** doing the
  deep per-anomaly biology now makes the Step-4.5 hypotheses mechanism-grounded in the person's actual data
  from the start, and lets the Step-5→6 deepening loop (D5) mostly *integrate and sequence* pre-built maps
  rather than start mechanism research late. (Enforced: the Step-5 gate requires a per-anomaly mechanism-map
  artifact for each flagged out-of-bounds result — see the required-artifact contract.)

*Output:* a mechanism map — observations paired with the underlying processes that might
have to be happening to produce them — **plus** a test-result-anchored mechanism map per out-of-bounds
result (`research/anomaly-<slug>-*` files), built early via paired research.

**PINNED on-disk process format (load-bearing — the driver counts the Step-3 fan-out from this).**
List each candidate process as its own line beginning with a bold marker in exactly this shape:

```
**P1 — <short-slug>** — <one-line description of the process>
**P2 — <short-slug>** — <one-line description>
```

`Pn` is a running integer id (`P1`, `P2`, …); `<short-slug>` is a hyphenated handle (e.g. `energy-shortfall`).
The `— ` (em-dash + space) between the id and the slug, and the closing `**`, are required: the trusted
census parses these markers to drive one blind builder per process, so a process written in any other
shape is silently dropped from the fan-out. Put the markers under a `## Processes` heading; keep one
process per line.

**Density floor (anti-rushing — the documented failure mode of the synthesis writes).** This is the
step that was rushed in the v2 run, so give it depth: in a real (non-smoke) run a synthesis write
(this map, `working-hypothesis.md`, `step5-cross-check.md`, `step6-prioritize.md`) is not done until
every observation has an actual mechanism, not a restatement, and every load-bearing claim cites
`[src:]` re-read this turn or `[ledger: <quote-id>]` from the post-Pass-C claim ledger — never
orchestrator memory. Treat a thin synthesis artifact as a failure to be re-run, not an acceptable
output. (Smoke/plumbing runs deliberately override this with thin placeholders — that override does
not apply to a real run.)

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

