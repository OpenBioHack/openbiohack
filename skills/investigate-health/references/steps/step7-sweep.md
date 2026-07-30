# Step 7 — Sweep-check — ONE loop; reconciles UNEXPLAINED **and** CONTESTED

After the mechanism deepening, go back to ALL the original data one datum at a time and check it
against the current picture (which may be several things at once). One reopening loop only; anything
still unexplained after that single pass is flagged honestly in the offer §3.

The mechanism chains this reads are the UNCHANGED deepening step's per-candidate
`mechanism-map-<candidate-slug>.md` files (`step5.10.md`) — there is no separate node registry. A
hypothesis REOPENED here was never selected for deepening, so it has NO mechanism map yet: reopening
it triggers an on-demand deepening pass that builds its `mechanism-map-<slug>.md` before Step 8 / offer
§1 can consume it. Until that map exists the reconciler treats the reopened hypothesis as
validly-owned (deepening-pending), not a zero-owner FAIL.

## Prompt

```
INPUT: every compiled datum (inlined, enumerated by the driver as a manifest), the leading/in-play
hypotheses with their deepening per-candidate mechanism maps (`mechanism-map-<candidate-slug>.md`),
AND the parked-provisional set with reasons + CONTESTED-BY data.

Per datum — MATCH: explained | partial | UNEXPLAINED (cite the chain node that explains it).

RECONCILE (two triggers, not one):
- UNEXPLAINED + load-bearing → check the parked-provisional pool; a fit → REOPEN <Hn>.
- CONTESTED datum (from Step 3's CONTESTED-BY): re-examine now that the full picture exists — was the
  parked hypothesis killed by a datum its co-cause actually explains? If so → REOPEN <Hn>. (This is
  the co-cause false-kill rescue; without it "nothing is deleted" is a lie.)
A REOPEN routes to 4b deep-research + a fresh 4c question (and an on-demand deepening pass that builds
its `mechanism-map-<slug>.md` if it has none).

ONE LOOP. After this pass, still-UNEXPLAINED data → `still_unexplained[]` (surfaced honestly in offer
§3). Coverage: the driver asserts every manifest datum got a MATCH verdict — an un-verdicted datum is
a FAIL, not a silent drop.
```

## Driver reconcilers (fail-closed)
- Every manifest datum → a MATCH verdict (explained | partial | UNEXPLAINED). An un-verdicted datum
  FAILS (not a silent drop).
- Every REOPEN → routed to 4b + 4c, and an on-demand deepening pass scheduled if it has no
  `mechanism-map-<slug>.md`; the reconciler counts a deepening-pending reopened hypothesis as owned.
- Every `still_unexplained[]` datum → an offer §3 owner.

## Haiku completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: a per-datum MATCH verdict for every manifest datum (citing the
  explaining node where explained), the reconcile decisions for unexplained-and-load-bearing and for
  contested data (with any REOPENs named), and a `still_unexplained[]` list.
- COMPLETE means: no manifest datum is left without a verdict; a REOPEN names the hypothesis and its
  trigger; an empty `still_unexplained[]` is complete and correct if every datum matched.
