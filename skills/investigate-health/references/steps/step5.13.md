### Step 5.13 — B5.6 Connection Plausibility Check (one independent assessor)

## The move, in plain terms

The previous step (5.12) deliberately went looking for **connections** — shared nodes, one arm feeding
another, a single upstream driver behind several arms. That instruction is useful but dangerous: an agent
told to find connections will find them, because almost anything in one body can be linked to anything else
through enough steps.

This step is the counterweight. **One assessor, who did not write the integration, judges whether those
proposed connections are actually real** — before any ranking happens, so a fabricated bridge never gets to
influence the rank.

The failure it exists to prevent: a self-certified system picture where the synthesis proposes a connection
and the same reasoning then treats it as established.

## Who runs it

**ONE agent, clean context** — it must not be the agent that wrote `system-integration.md`. It receives all
the proposed bridging connections and shared-driver claims, plus the relevant data for the arms involved, and
assesses **all of them together in a single pass**.

**One agent, one artifact — never an agent per connection.** Per-connection agents lose the cross-view that
lets an assessor notice that three "separate" bridges are the same claim wearing different words, and they
explode the artifact count for no gain.

It may do whatever research it needs, and it **may surface a plausible connection the integration missed** —
that is a legitimate output, not scope creep.

## What to judge, per connection

**Verdict one — is the connection real?**
- **plausible** — a named mechanism connects these arms, and the evidence supports it.
- **partial** — a mechanism is conceivable but under-evidenced, or holds only under conditions not
  established here.
- **not-plausible** — the proposed link does not survive scrutiny.

**Verdict two — is it specific, or a generic hub?** This is the one that catches the most common failure.

> A bridge must be a **named, mechanistically load-bearing connector whose modulation would plausibly move
> BOTH arms**. A node that connects nearly everything is not a bridge — it is a truism wearing a mechanism's
> clothes.
>
> - ✗ *"inflammation links them"* — links almost any two findings in any body. Generic.
> - ✗ *"the microbiome connects them"* — the whole system as a single actor. Generic.
> - ✗ *"oxidative stress"* — same problem.
> - ✓ *"The upstream substance arriving in larger amounts acts on a specific receptor, which is the same
>   pathway the second arm's symptom runs through — so changing how much arrives would be expected to move
>   both."* — named, mechanistic, and modulating it should move both arms.
>
> If the claim is generic, do not soften it — mark it generic and send it back to be **named specifically or
> dropped**.

## The reasoning standard

For each verdict, give the mechanism and the evidence — not an impression. A verdict of "plausible" with no
named mechanism is the same failure as the generic hub: it looks like a judgement and carries no content.

Where a connection is **directional** (arm A drives arm B rather than the reverse), say which way and on what
basis; where the direction cannot be established from the data, say that, because a bidirectional assumption
smuggled in as fact will distort the ranking downstream.

## What happens to your verdicts (why they matter)

- **not-plausible** → the claim is downgraded in `system-integration.md` to *"held open — unproven"*. It is
  not deleted, but it may no longer be asserted or used to support the rank.
- **generic hub** → returned to 5.12 to be named specifically or dropped.
- **newly surfaced plausible connection** → added to 5.12.
- Nothing proceeds to ranking (5.14) until every bridging-connection and shared-driver claim carries a
  verdict from this step.

## Output shape

```markdown
## Connection verdicts

| connection (as proposed) | arms it links | verdict | specific or generic | mechanism + reasoning | evidence cited |
|---|---|---|---|---|---|
| <…> | <Hn> ↔ <Hn> | plausible / partial / not-plausible | specific / generic | <named mechanism, direction if known> | [src: …] / research ref |

## Connections the integration missed (if any)
- <connection>: <mechanism> — <evidence> — proposed for addition to system-integration.md

## Notes
- <any case where two proposed connections are the same claim restated>
```

## Done when

- Every bridging connection and shared-driver claim in `system-integration.md` has a row with **both**
  verdicts (real? and specific-or-generic?).
- Every verdict names a mechanism and cites evidence — no bare impressions.
- Any generic hub is flagged as such rather than quietly accepted.
- A "no new connections found" is a complete and acceptable answer for the second section.

**Artifact:** `connection-plausibility.md`. **Prerequisite:** `system-integration.md` from 5.12.
