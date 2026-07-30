### Step 5.14 — B5 System Simulation + Convergence (the ranking step)

## The move, in plain terms

This is where the deepening loop lands. Every surviving candidate now has a mechanism map; the connected
system has been modelled (5.12) and its connections independently checked (5.13). Now you **run each
mechanism forward against reality** and **prioritise**.

**Prioritise — never single one out as the cause.** The output is a ranked, probabilistic set with reasons,
not a winner. In a complex picture several things are usually operating at once, and the honest output says
which are best supported, which are weaker, which were dropped and exactly what dropped them.

This step runs **last** in the loop — after integration and the plausibility check — so that the ranking is
connection-aware. Rank before you understand how the arms couple and you will demote a candidate for failing
alone at something it never had to do alone.

## Simulate first, rank second

For each candidate (and each composite), **predict what we would observe if it were operating**, then lay
those predictions next to what is actually observed.

> The discipline: write the prediction *before* looking at the match. A prediction generated after reading
> the observation is not a test — it is a description with the answer already in it.

A **failed prediction weakens or drops** the candidate. And:

> **Every drop names the exact observation or constraint that did it.** No silent demotions — a candidate
> that disappears without a named killer is a defect, because the next reader cannot tell whether it was
> refuted or forgotten.

## Three protections against dropping something true

These exist because each corresponds to a way the engine has destroyed a correct answer before.

**1. A composite is ranked as a unit; consistency is checked per member INSIDE it.**
If one member fails the survival check *on its own* but the composite explains its survival — it is
sheltered, cross-fed, or protected by another member — it is **not** demoted. Testing each member in
isolation is exactly how a true division-of-labour answer gets destroyed: the sheltered member always looks
unsupported when you remove its shelter from the analysis.

**2. A cross-cluster hypothesis is ranked as the connected whole.**
If a hypothesis spans more than one symptom cluster, and 5.12 + 5.13 established a plausible connection
across those clusters, it is **not** demoted for failing on one cluster alone. Simulate and rank it as the
connected whole — the same way a composite is ranked as a unit.

**3. The standing location re-check — poor fit is enough to re-open.**
This fires on **poorly-fitting** facts, not only on flat contradictions. If a real fact fits no surviving
candidate well, that is a signal the location may be wrong: spawn a new hypothesis and re-enter the earlier
phase. Do not force the fact into the nearest candidate to keep the model tidy.

## The ruled-out ledger

Every demoted or excluded candidate is recorded **with the specific evidence that demoted it**. This is not
bookkeeping — the offer needs both halves: why the surviving candidates rank where they do, *and* why the
obvious-looking alternative was set aside. A person who has been told "it might be X" for years is owed the
reason X is now ranked lower.

Carry the demoted set forward; nothing is deleted, and anything demoted on soft evidence stays reopenable at
the sweep.

## Output shape

```markdown
## Simulation
### <candidate>
| predicted if operating | actually observed | match: yes / partial / no | source |
- prediction written before matching: <confirm>
- net effect on standing: <strengthened / weakened / dropped> — because <the specific observation>

## Ruled-out ledger
| candidate | what demoted it (the exact observation or constraint) | strength of that evidence | reopenable? |

## Location re-check
- facts fitting no surviving candidate well: <list, or "none">
- action: <new hypothesis spawned + re-entered / none needed>

## Ranking
| rank | candidate (or composite, as a unit) | why here | what would move it up or down |
- composites ranked as units: <note which, and which member is sheltered by which>
- cross-cluster candidates ranked as wholes: <note which, citing the 5.13 verdict that licensed it>
- **This is a prioritisation, not a verdict** — no single candidate is named as the cause.
```

## Done when

- Every candidate has a simulation with predictions laid against observations.
- **The ruled-out ledger is present, and every rank-change cites a constraint or observation.**
- No composite member was demoted in isolation where the composite explains its survival; no cross-cluster
  candidate was demoted for one cluster where a plausible connection was established.
- The location re-check has been run against poorly-fitting facts, not only contradictions.
- No aggregate-as-actor survives in any load-bearing line (the grain rule still applies here).
- No candidate carries an unresolved `askable-now` or `in-records` discriminator — those should have been
  resolved before ranking; if one is still open, say so rather than ranking around it.
- The ranking reads as a prioritised set with reasons — **not** as a settled single answer.

## The loop

Deepen all non-demoted hypotheses B1 → B2 → B3 → B4 → 5.12 (integration) → 5.13 (plausibility) → 5.14
(convergence). A second interview and the reverse-engineered treatment responses feed back to re-integrate,
re-check plausibility, and re-converge. **Continue until the ranking stops shifting and the option set is
stable** — that stability, not a fixed number of passes, is the exit condition. Only then proceed to
prioritise-and-offer.

**Artifact:** `convergence-<Hn>.md`. **Prerequisites:** the mechanism maps, `system-integration.md`, and
`connection-plausibility.md`.
