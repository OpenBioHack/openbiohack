---
name: working-truth-ledger
version: 1.0.0
applies-to: investigate-health Steps 5, 5.5, 6, 7, 8 (and the OPTIMIZE lens — see §lens-agnostic)
---

# The Working-Truth Ledger (`<root>/working-truth.md`)

The governance-of-truth layer. The engine has powerful *generation* (blind builders, research,
hypotheses, recombination) but, before this, no binding *governance of truth*: it accumulated inputs
forward into a synthesis instead of continuously re-grounding every claim against a persistent,
authority-ranked, disconfirmation-pruned, veracity-checked model of what is established / open / parked.
The ledger **is** that model — one living object, held as **state on disk**, that the orchestrator reads
first at every synthesis step and updates last. Without persisted state none of this survives a long run
(compaction is lossy); the ledger is the load-bearing feasibility move.

This file is the **spec**. The per-subject instance is `<root>/working-truth.md`, created at bootstrap and
maintained through the run. The rules here are inherited by the reconcile-auditor, the veracity-auditor,
the coherence-auditor, and the structural write-check gate.

---

## The two governance principles this object enforces

### D1 — the NO-OVERRIDE rule (authority is an axis, not a new ladder)

We already have two ranking systems and do **not** add a third:
- the **evidence tiers** (established / studied / mechanistically-plausible / temporal-only / speculative) —
  they measure *causal certainty*;
- the **evidence hierarchy** (meta-analyses > RCTs > cohort > … > anecdote) — it measures *study quality*.

Neither encodes **specificity-to-this-subject (n-of-1 relevance)**. That is the missing axis: for a
conclusion *about this person*, the **person's own measured data and their directly-experienced lived
report are the top authority**, above any population/general evidence however high its study quality.

**The rule:** *a general/population claim — at any study-quality tier — may REFRAME or CONTEXTUALISE a
higher-authority own-data / directly-experienced observation about this person, but may NOT by itself
OVERTURN it.* To overturn a top-authority observation you need other top-authority evidence (the person's
own data/experience), not a textbook, a population average, or a single agent's "didn't find."

This dissolves the authority inversions: a blind agent's prior must not override the live interview; a
timeboxed agent's "no small-bowel evidence found" must not override "we have not actually looked"
(no-evidence ≠ negative); a population "usually a commensal" must not override a 555×-cutoff standout that
demands its own mechanism map (see Dm / the standout-finding rule in the SKILL).

It does **not** catch a *fabricated* relationship — that is a veracity problem (Dv), handled separately.

### Dv — the VERACITY double-check (quoted data, timing, and sequence must be real)

A *fabricated* relationship ("best while load highest," from two facts on different dates) is not an
authority failure — ranking authority cannot catch it. Before any claim that quotes data is committed —
**especially any temporal / sequencing / ordering / "X tracks · coincides-with · rose-after · best-while Y"
claim** — in a pass *separate from writing the prose*: (i) re-fetch each quoted datum (value, date, what the
source says) from its source; (ii) for any timing/sequence/ordering claim, confirm **both** endpoints are
actually dated in the record and the ordering is correct; (iii) restate the verified chain. A claim whose
endpoints do not both resolve is struck or downgraded to **"timing unknown."** This is the recombination
agent's existing temporal-claim gate, **generalised to every synthesis write.**

---

## Confidence: bands, parking, gated re-raise (D2)

- **Persisted, not ephemeral.** Per-hypothesis confidence is written into the ledger and carried across
  turns, so drift is visible and prevented.
- **Bands, not false precision.** Use coarse bands — **~80% / ~50% / ~15% / <5%** — for *relative ranking*
  and for *detecting un-justified increases* only. They are **not** real-world probabilities (the offering
  carries the D8 disclaimer saying so).
- **"Refuted" is NOT a hard latch.** When confidence falls into the bottom band (≈ <2–5%) the hypothesis is
  **PARKED — dormant, not deleted.** Nothing is struck forever.
- **Re-raise is gated by anti-escalation.** A parked hypothesis can be raised again **only** by newly logged,
  higher-authority evidence — never by an agent re-proposing it from priors, never by drift, never by the
  conversation steering it. The raise and its triggering evidence are logged in `## Parked`.
- **Parking is CONSEQUENCE-WEIGHTED.** A low-probability but **high-consequence** hypothesis (the safety
  must-excludes — irreversible / escalating / time-sensitive harm if missed) does **NOT** get parked at <5%;
  it stays visible (`status: LIVE`, `consequence: HIGH`) precisely because being wrong is costly.

**Anti-escalation, persisted.** Confidence at the end of a turn must not exceed confidence at the start
unless newly logged biological evidence justifies it. Any band *increase* must carry, in the `last-change`
cell, the specific new evidence that justified it. An increase with no new-evidence citation is the exact
drift the persisted band exists to catch.

## Refuters carry full weight (D3)

Two refuter classes the synthesis under-weighted, recorded in `## Refuters` and feeding the bands directly
(they are top-authority own-data observations under D1):
- **Gross physical/mechanistic implausibility** — e.g. a behavioural air-handling mechanism cannot produce
  voluminous continuous gas; the physics caps confidence regardless of how well other features fit.
- **Positive treatment-response that only one mechanism explains** — e.g. oral serum-derived bovine
  immunoglobulins reducing the burping is a luminal/immune fingerprint a behavioural cause cannot produce;
  it raises the luminal hypotheses and refutes behavioural.

## Already-tried is state-dependent (D6)

An intervention's effect is a function of the system **STATE** when it was applied. The ledger records
**"tried X IN STATE S → result,"** not "tried X → result"; sequencing is a first-class variable.
Re-proposing a tried-and-failed intervention requires three things, backed by real `/research` +
`/research-practitioner` (not assertion): (i) the **different state S′**; (ii) a **mechanism-grounded reason
it failed in state S**; (iii) **why S′ changes the prediction.** Absent those, it stays dropped.

---

## Schema — the six sections

The instance file MUST contain these six `##` sections (the structural gate checks the file exists and is
non-empty; the auditors check the contents semantically).

### `## Hypotheses`
One row per hypothesis (`Hn`):

```
| id | one-line | confidence-band | status | consequence | last-change (+ justifying evidence) |
|----|----------|-----------------|--------|-------------|-------------------------------------|
| H1 | <plain>  | ~50%            | LIVE   | med         | 2026-06-18 raised from ~15% — [src: ...] new ... |
```
- `confidence-band` ∈ {~80%, ~50%, ~15%, <5%}.
- `status` ∈ {LIVE, PARKED, ESTABLISHED}.
- `consequence` ∈ {low, med, HIGH}. Park only when `consequence` is low/med; HIGH stays LIVE however low the band.
- `last-change` records every band move with the evidence that justified it (an *increase* MUST cite new evidence).

### `## Top-authority observations`
The subject's own data + lived reports — the override-proof anchors (D1). Each row:
```
| obs | provenance | confidence-% | source |
```
- `provenance` ∈ {from-notes, clear-recent-memory, hazy-memory, inference} (D7).
- `confidence-%` is the subject's stated % for an interview answer (or "measured" for own data).
- Weight is set by provenance + % together: a hazy long-ago memory or an inference weights down even at a high stated %.

### `## Refuters`
Observations that *lower* a hypothesis (incl. the D3 classes), each pointing at the hypothesis it cuts:
```
| refuter | class (physical-implausibility / treatment-response / data-counterexample / other) | cuts (Hn) | source |
```

### `## Tried interventions (X in state S → result)`
The D6 log — the basis for the already-tried check:
```
| intervention | state S when applied | result | dates | source |
```

### `## Parked`
Parked hypotheses + why + the specific evidence that would re-raise each (so re-raise is auditable):
```
| Hn | parked-when | evidence that parked it | specific new evidence that would re-raise |
```

### `## Open gaps`
What the loop-back (D5 / `coherence-map.md`) located as genuinely unresolved + the cheapest move to close each:
```
| gap | which hypothesis it bears on | cheapest move to close it |
```

---

## How the engine uses it (read first, update last)

- **Read first** at the start of Steps 5, 5.5 re-rank, 6, 7, and 8 — before any synthesis claim is formed.
- **Update last** at the end of each of those steps — band moves, new observations, new refuters, new
  tried-in-state rows, parks/re-raises, new/closed gaps.
- **The reconcile gate (D4)** reads the ledger to check each load-bearing synthesis claim: (a) does not
  contradict an ESTABLISHED or PARKED entry; (b) carries authority-tier + source and lets no lower-authority
  input overturn a higher one; (c) names the strongest own-data disconfirmer — single decisive fact *and/or*
  the convergent pattern — and survives it; (d) for any test/trial, passes value-of-information + already-tried.

---

## Lens-agnostic (D9)

This object is **not** investigate-only. In the OPTIMIZE lens the person's own **response data** is still the
top authority: you still reconcile against the ledger, still loop back to it (D5), still track
intervention × state (D6), still park and gate-re-raise by evidence (D2). The schema and the gate are
lens-neutral; the OPTIMIZE lens populates `## Hypotheses` with bottleneck/requirement hypotheses and
`## Top-authority observations` with the person's measured baselines and response data.

## Change-log
- **1.0.0** (2026-06-18) — Initial. The Working-Truth governance layer (D1–D11 + Dv + Dm).
