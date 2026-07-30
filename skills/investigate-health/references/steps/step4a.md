# Step 4a — Selection (deterministic): the top-N survivors by cited raw data

Deep research (Step 4b) is onerous, so it runs on a bounded set, not on every hypothesis. The selector is
DETERMINISTIC — a small program, not an agent — because the choice is a count, and a count is exactly what
code does reliably and a model does not: for each hypothesis, count the raw data it quotes among its reasons
(`[src: ...]` citations in its card), drop the ones disconfirmation actively PARKED (the data refuted them —
we do not deep-research a refuted candidate), rank the survivors by that count, and take the top N (default
10). "Most raw data quoted" is a proxy for "built on the fullest evidential picture."

Nothing is eliminated. Every hypothesis not selected — the survivors below the cut AND the parked ones — is
carried forward as the Step-7 reopen pool.

## What the selector does (`lib/integrate/select-top.py`)

- Reads each root's card (`hypotheses/cards/H*.md`, the ids from `_families.json`) and counts its `[src:]`
  citations.
- Reads each root's disconfirmation standing (`disconfirm/h*.md`): a `parked` root is excluded; a root a
  reframe reverted back to `survives` counts as a survivor; a missing/unparseable standing is treated as
  survives (a parse miss must never silently drop a candidate).
- Ranks survivors deterministically: citations DESC, then fixed family order, then id number — so the same
  inputs always give the same selection.
- Writes `selection.md`: a `## Deep-research set (top N)` list (what Step 4b researches) and a
  `## Carried forward (reopen pool)` list (survivors below the cut + all parked, each with its standing).

## Note

`N` is a soft ceiling (default 10), not a claim that the rest are wrong — it bounds the expensive research
step. Because the count tracks how much test data a hypothesis cites, it can favour whichever body system
was most heavily tested; that is a known property of the proxy, revisited when the survivor set is small or
one family dominates.
