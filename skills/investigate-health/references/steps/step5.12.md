### Step 5.12 — B5.5 System Integration (model the connected system, BEFORE any ranking)

## The move, in plain terms

Up to now each hypothesis has been developed on its own. The natural next instinct is to line them up and
ask *"which one wins?"* — and that instinct is wrong here, because it assumes the body is running one
process at a time.

**It is rare for co-occurring factors in one person to be independent.** Several things are usually running
at once, feeding each other, or riding on something shared and upstream. So before anything is ranked or
cut, model the survivors as **concurrent interacting layers of one system**.

This runs deliberately **before** the ranking step, so that a connected account gets examined while every
candidate is still alive. Rank first and you cut a member of a system you never modelled.

**What you are looking for:** where two arms share a node; where one arm's output is another arm's input;
and whether a **single upstream driver** sits behind several of them, such that correcting *it* would move
several at once. That last case can open an intervention space that does not exist candidate-by-candidate —
acting at the root instead of at each arm separately.

## The bridge test — specific connector, not everything-hub

The failure mode here is easy to fall into and hard to see afterwards: because almost anything in a body can
be linked to anything else through enough steps, an agent looking for connections will always find some.

> A shared node counts as a **real bridge** between two arms only if it is a **specific, mechanistically
> load-bearing connector whose modulation would plausibly move BOTH arms** — a named mediator, transporter,
> barrier node, shared substrate, or a concrete exposure or behaviour.

A node that connects nearly everything is **not** a bridge:

- ✗ *"inflammation"* — sits under almost every finding in almost every body.
- ✗ *"the microbiome"* — the whole system named as a single actor (and a grain-rule violation besides).
- ✗ *"oxidative stress"*, *"gut-brain axis"* — same shape: true of everything, therefore discriminating of
  nothing.
- ✓ *"Both arms run through the same upstream delivery step: the change that drives the first arm also
  changes what is available to the second — so moving that one step should move both."* — named,
  mechanistic, and testable by modulating one thing.

**If you cannot name the specific sub-node doing the connecting, mark the connection unproven rather than
softening the language.** Default to *looking* for connection — but the connection must be carried by a
mechanism, not by a truism. Everything you propose here is judged in 5.13 by an independent assessor, and a
generic hub will come straight back.

## Integrator vs origin — the four gates

Not every shared node is worth building an intervention around. A shared node is an **INTEGRATOR** — a hub
worth naming and mining for levers — only if it passes **all four**:

1. **Convergence** — at least three distinct root-cause input edges feed into it.
2. **Emergence** — at least three quality-of-life-affecting symptom output edges hang off it.
3. **Intervention-leverage** — turning its output down would ease those symptoms on a **weeks** timescale,
   *even while the root causes persist* for months or years.
4. **Cheap-testability** — a cheap, reversible probe of gate 3 exists.

**The most upstream node is NOT automatically the integrator.** A node that passes gate 1 (everything traces
back to it) but fails gate 3 (nothing you do to it helps within weeks) is an **origin**, not an integrator —
however many findings sit downstream of it. History is an origin; you cannot intervene on a past event.

> Why this distinction earns its place: the origin tells you *how you got here*, the integrator tells you
> *where a lever exists now*. Confusing them produces an offer that explains the past and cannot act on the
> present.

Test each candidate hub against the four gates **explicitly**, and record which it meets and which it fails.
A hub that meets some and not others is a **partial hub** — say which gates it fails. Never leave "hub" as
an unexamined label.

## Finally: simulate the combined system

Run the whole connected model against the **full** symptom set — including symptoms outside the primary
complaint, and including the test and measurement results.

Every symptom and every result must end up in one of two places: **accounted for by the combined model**, or
**explicitly named as not-yet-explained**. Nothing may be left silent. An unexplained finding that is named
is a lead for the sweep; an unexplained finding that is quietly skipped is how a whole arm goes missing.

## Output shape

```markdown
## Concurrent layers
- <arm/hypothesis>: <what it contributes to the picture, in one or two lines>

## Bridging connections
| connection | arms linked | the specific connector (named node/mediator/substrate) | why modulating it would move BOTH | evidence |
|---|---|---|---|---|
- <any connection where no specific sub-node could be named — listed here explicitly as unproven>

## Shared systemic driver
<the upstream driver and the arms it sits behind — or "none found — <reasoning>">

### Hub assessment (four gates)
| candidate hub | (1) convergence ≥3 inputs | (2) emergence ≥3 symptoms | (3) weeks-scale leverage | (4) cheap reversible probe | verdict: integrator / origin / partial (which gates fail) |

## Independent plausibility verdicts
<filled in from Step 5.13 — leave the section header in place>

## Combined simulation vs full symptom set
| symptom or result | accounted for by | or: not-yet-explained (say so plainly) |
```

## Done when

- Every surviving hypothesis appears as a layer.
- Every proposed bridge names a **specific** connector, or is explicitly marked unproven — no generic hubs
  asserted as connections.
- Every candidate hub carries an explicit four-gate assessment, with integrator vs origin distinguished.
- **Every symptom AND every test/measurement result** is either accounted for or explicitly named as
  not-yet-explained. Silence about a finding is the failure this step exists to prevent.
- The shared-driver section is filled in — *"none found"* with reasoning is a complete and acceptable answer.

**Artifact:** `system-integration.md`. **Next:** 5.13 judges every connection proposed here before anything
is ranked.
