---
name: coherence-map
version: 1.0.0
applies-to: investigate-health Step 5.7 (the deepen → coherence → judge loop, between Step 5/5.5 and Step 6)
---

# The coherence map (`<root>/coherence-map.md`)

The structured sense-making engine that sits between cross-check/interview and prioritisation. The engine
will **not** reliably do this depth unprompted — it needs structure and gates. This file is the artifact
contract; the loop it records is described in the SKILL at "Step 5.7 — Deepen & coherence-check."

## The principle

Once hypotheses exist, return to the subject's OWN already-collected data and work to *understand and
integrate* it **before** judging anything — and the judgment, when it comes, is **strengthen / weaken /
neutral**, never confirm/refute. Deepening (understanding) is a distinct cognitive category from judging,
and must come first or the judgment is biased toward whatever you already lean to. The subject's own data is
top authority (register §"Authority is a third axis"), so it is the thing to keep returning to.

## The loop, per live hypothesis (a few iterations)

1. **DEEPEN — understand first, do NOT judge yet.** Ask *"IF this hypothesis were true, how would we
   understand it through this data?"* Go through the symptoms, each test, the **timeline and sequencing of
   the tests**, the treatments and their dates, and work out what each piece would *mean* under the
   hypothesis — some data is silent, some speaks. Use `/research` + `/research-practitioner` to understand the
   mechanism of the relevant findings — though most of that per-finding biology should already exist from the
   test-result-anchored mechanism maps (Dm, Step 2), so deepening here mainly **reuses and integrates** it.
2. **COHERENCE / DISCREPANCY hunt** — look for alignment AND mismatch across symptoms × tests × timeline ×
   treatments, and **surface every discrepancy that demands an explanation.** Each discrepancy is then either
   explained with a mechanism or logged as an `OPEN-GAP` — never silently dropped.
3. **JUDGE — strengthen / weaken / neutral.** Only now, per hypothesis, decide whether the integrated,
   coherence-checked data **strengthens, weakens, or is neutral** to it, and record that verdict in the
   `## Verdicts` section of THIS file. Never "confirmed/refuted."
4. **LOOP** across hypotheses and re-iterate until the mechanism map is coherent end-to-end **or** the
   remaining discrepancies/gaps are clearly pinpointed.

## Required sections (the structural gate checks these exist and are populated)

### `## Deepening — <Hn>`
One per live hypothesis. The per-hypothesis understanding notes: what each symptom / test / timeline-point /
treatment-date would *mean* if this hypothesis were true; which data is silent and which speaks. This is
understanding, not verdicts — no strengthen/weaken language here. The notes must also **build or extend the
hypothesis's narrated end-to-end chain to the felt symptom** and run the **mechanism-depth interrogation**
(SKILL front matter — WHAT / BY-WHAT / WHERE / HOW-MUCH / MEASURED-OR-EXTRAPOLATED / RESIDUAL); any probe
research cannot close becomes an `OPEN-GAP` with its measurement-edge estimate.

### `## Discrepancies`
Every discrepancy the coherence hunt surfaced, each on its own line, each **either** carrying its mechanism
explanation **or** tagged `OPEN-GAP`. Format:
```
- <discrepancy>: <mechanism explanation that resolves it>
- <discrepancy>: OPEN-GAP — <why it is unresolved; the cheapest move to close it>
```
No discrepancy may be left untagged. Every `OPEN-GAP` stays in THIS file — it is the open-gap record the
later steps read (there is no separate ledger).

**FORMAT — this is load-bearing, not cosmetic.** The Step-6 governance gate reads each discrepancy bullet's
**first line**. Put the marker AND its resolution separator on that first line:

- ✓ `- **[D-1]** <short discrepancy>: <the resolution>` — resolution may continue onto wrapped lines.
- ✓ `- **[D-2] OPEN-GAP** — <short discrepancy>: <why unresolved; cheapest move to close it>`
- ✗ a bullet that opens with a long citation or quote and only reaches `**[D-n]**` or the `:` on a
  continuation line. The analysis may be perfect and the gate will still fail it as an untagged
  discrepancy, halting Step 6.

So: **lead each bullet with `**[D-n]**` (plus `OPEN-GAP` when it is one), then a colon, then the
resolution.** Push citations and long quotes to the later part of the bullet, never ahead of the marker.

### `## Verdicts`
One line per hypothesis: **strengthen / weaken / neutral**, each tied to the specific deepening that
justifies it (not asserted free-floating). Format:
```
- H1: strengthen — <which deepening point(s) justify it>
- H2: neutral — <why the data neither raises nor lowers it>
```
These verdicts are what the prioritisation step reads — they carry forward from this file directly.

## Enforcement

- **Structural (hook):** the Step-6 write (`step6-prioritize.md`) is blocked unless `coherence-map.md` exists
  with `## Deepening`, `## Discrepancies`, and `## Verdicts` sections populated, and **no discrepancy line is
  left without either an explanation or an `OPEN-GAP` tag.**
- **Semantic (dispatched coherence-auditor):** checks the discrepancies were genuinely addressed (not
  hand-waved) and the strengthen/weaken/neutral verdicts actually follow from the deepening rather than being
  asserted. Template: `references/council/dispatch-template-coherence.md`.

## Lens-agnostic (D9)

In the OPTIMIZE lens the same loop runs: deepen each bottleneck/requirement hypothesis against the person's
measured baselines and response data, hunt discrepancies, judge strengthen/weaken/neutral. The contract is
identical.

## Change-log
- **1.0.0** (2026-06-18) — Initial (D5).
