# Architecture (for contributors)

A map of how OpenBioHack is put together, so you know where a change belongs.

## The shape: one orchestrator that defers to one engine

```
CLAUDE.md  ── the orchestrator (front door + shared contract)
  │   continuum + 3 lenses · intake · register · safety · refer-out ·
  │   anti-patterns · genetics · session loop · memory · the epistemic backbone
  │   (this file is also the canonical "package CLAUDE.md" the engine references
  │    for the evidence-tier apparatus)
  │
  ├── routes to ──► skills/investigate-health/   ← THE ENGINE (the spine)
  │                   8-step non-directive investigation + council + sourcing
  │                   tiers + register enforcement + eval harness
  │                 skills/extract-health-data/   raw records → structured data
  │                 skills/research/              first-principles research
  │                 skills/research-practitioner/ practitioner-grounded depth
  │                 skills/product-search/        ingredient-by-ingredient vetting
  │
  ├── references/    optimization.md (optimize lens) · high-value-levers.md
  │                  (candidate levers, examples not prescriptions) · n1-protocol.md
  │
  └── templates/     symptom-log · experiment-log · MEMORY (index) ·
                     medical-history · genetics · corrections  ← the longitudinal layer
```

## Three principles that govern where code goes

1. **The engine is the spine; the orchestrator defers to it.** Real investigation logic — generating
   candidates, weighing evidence, the council, the offering — lives in `skills/investigate-health/`. The
   orchestrator frames, routes, and holds the shared contract. **Do not fork engine logic into the
   orchestrator**; that's how the two drift and the hardened register erodes. If you're adding analysis
   behavior, it almost certainly belongs in the engine.

2. **Non-directive register is law, defined once.** The register rules (§2) and the evidence-tier apparatus
   (§3) live in the root `CLAUDE.md` — the engine points back to it as "the package `CLAUDE.md`." Don't
   duplicate the tier system elsewhere. Every output speaks in possibilities and options, never instructions
   or verdicts. See `CONTRIBUTING.md`.

3. **The continuum, not modes.** Investigate / optimize / check-in are *lenses on one machinery*, differing
   only in thrust (problem-backward vs system-forward vs longitudinal). Optimize reuses the engine,
   forward-traced (`references/optimization.md`). There is no hard mode-branch.

## Living artifacts

The memory files, the two logs, the constraint list, and the `product-search` caches are **continuously
maintained** as a person uses the system — not one-shot. `MEMORY.md` is an *index*, not a store (pointers to
deeper files; under ~200 lines). See `CLAUDE.md` §7.

## Tests

- `eval/register-sweep.sh` and `eval/check-eval-structure.sh` are the deterministic CI gates.
- `skills/investigate-health/eval/case-*/` are the behavioral regression cases (run via that dir's
  `run-evals.sh`, which needs a Claude Code session to produce artifacts to grep). New failing cases are the
  most valued contribution — see `CONTRIBUTING.md` and the eval dir's `README.md`.
