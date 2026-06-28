# Changelog

All notable changes to OpenBioHack are recorded here. The bundle is generated from the canonical
engine by `build/build-bundle.sh`; entries describe the engine behaviour the public bundle ships.

## 0.3.1

Bundle-quality follow-up to 0.3.0.

### Changed
- Scrubbed register-borderline wording from the offer-example library (s2/s3/s6) — removed "fixable",
  "you should", and stray "clearly" so the worked examples hold the same non-directive, person-facing
  register the offer-writer must match (they are the bar it copies).

### CI
- `register-sweep` now also lints the offer-example library (`references/offer-examples/*.md`), not just
  the standalone content docs — closing a gap where the register-critical examples weren't being checked.

## 0.3.0

The engine now produces its mechanistic depth itself — and checks its own work for shallowness — so the
person-facing offer is genuinely educational without a human having to drag it deeper. This release adds a
self-interrogation depth loop, a measurement-edge / dose-reachability check, an anatomical-location
requirement, a re-shaped offer, section-by-section offer writing against a worked-example library, and
tightened council auditors. (It is the outcome of a second post-mortem: a run that produced the right
structure but still explained mechanisms too shallowly to teach from.)

### Added
- **Mechanism-depth interrogation.** Every load-bearing mechanism must pass a self-check — WHAT (specific
  actor: molecule / enzyme / gene / cell / microbial family), BY-WHAT (a verb-chain, not a bare outcome),
  WHERE (anatomical location), HOW-MUCH (the measurement-edge below), MEASURED-OR-EXTRAPOLATED, and RESIDUAL.
  An unclosed probe triggers targeted research until it closes or is honestly flagged as an evidence-edge.
  This automates the "go deeper" pushback that previously needed a human.
- **Measurement-edge / dose-reachability check** (deep mechanism map + intervention mapping). For any claim
  whose weight depends on an amount, or is imported from another context (other species, in-vitro, a
  different compartment or dose): an evidence-edge map; a commensurability guard that refuses
  apples-to-oranges comparisons (e.g. a blood concentration used to infer a gut-lumen concentration); and —
  only where the quantity was never actually measured — a transparent first-principles estimate with its
  assumptions, a range, and an order-of-magnitude plausibility verdict. Surfaced honestly, never as measured.
- **Narrated end-to-end chains + anatomical location** required at the producers (hypothesis step, deepen /
  coherence, deep mechanism map): each leading hypothesis carries a chain from root → each step → the felt
  symptom, naming the segment / cell where each step happens (and produced-vs-acts for a factor) — so the
  offer integrates depth instead of inventing it.
- **Per-section offer-example library** (`references/offer-examples/s1–s7.md`): worked, multi-domain teaching
  exemplars that set the depth and register bar for each section of the offer.
- **Unstudied-gap invitation.** The closing offer surfaces the questions no existing study can settle and
  offers a transparent first-principles estimate, with every assumption shown for the person to challenge.

### Changed
- **Offer sections 5 and 6 re-shaped.** §5 = low-risk things to try (Category 1 to ease symptoms / Category 2
  also possibly acting on a root cause); §6 = higher-risk, mostly-root-cause options that warrant a test
  *before* trying, each paired with the test that should precede it (cheap-at-home vs more-expensive, each
  naming the decision its result would change).
- **The offer is written section by section.** Each section is produced by a dedicated pass that loads only
  that section's worked examples plus the upstream artifacts it integrates — so the depth-and-register bar is
  met per section rather than diluted across one long pass.
- **Council auditors tightened.** The structure auditor checks the new §5/§6 shape; the substance auditor now
  fails any load-bearing mechanism with an unclosed depth probe and requires the measurement-edge verdict on
  any dose-reachability claim.

## 0.2.0

The investigation engine now performs the deep reasoning itself instead of needing a human to drag
it there. This release adds an onboarding step, a full deepening loop, a grain/decomposition
enforcement layer, a restructured offer, and new council auditors — the outcome of a post-mortem of
a real run that passed its own auditor council while staying shallow.

### Added
- **Phase 0 — Onboarding.** Before any reasoning: a completeness pre-flight (which expected records
  are present vs missing, holes flagged), a hand-the-documents-to-the-person verification step
  (read your own data, confirm the timeline), and explicit goal-clarification. New artifacts
  `data-completeness.md` and `goals.md`; the first analytical write is gated on them.
- **The Phase-B deepening loop (Steps 5.8–5.13).** For each leading hypothesis: constraint harvest
  (incl. onset/perturbation and survival-explanation constraints) → shape deduction with built-in
  **decomposition** → a deep, domain-neutral mechanism map (with `vulnerabilities` and
  `persistence-structure`) → resolve cheap discriminators *before* weighting → simulation &
  convergence → cross-hypothesis system integration. Composite/consortium hypotheses are
  first-class objects (typed roles + interaction edges), ranked as a unit but consistency-checked
  per member.
- **Grain / decomposition enforcement.** A load-bearing claim may not treat an aggregate as a single
  actor ("the drug family confers resistance") or assert an unspecified relation — it must be
  exploded to checkable members (family → species, not to atoms) first. Enforced by a write-hook
  pre-check and a new decomposition auditor.
- **Restructured offer (B6–B9).** Per-node intervention discovery; a mandatory per-item record
  (mechanism → vulnerability node, evidence tier + source, administration: form / dose / timing /
  co-intake / interactions); reverse-engineering of *all* prior responses (not just the ones that
  worked); a seven-part "offer of possibilities"; and a closing deeper-pass + invitation that hands
  the person the means to keep investigating themselves.
- **Four new council auditors** — decomposition/grain, structure/completeness, register/
  non-diagnosis, and substance (every actionable item carries the full per-item record) — each
  gating the final offer.
- **Claim-strength tagging** in `research` / `research-practitioner`: every locational /
  exclusionary / prevalence claim is tagged (a) examined-and-excluded-with-mechanism / (b)
  primarily-mostly / (c) never-examined; only an (a) claim, citing a verifiable primary-source
  sentence, may exclude a candidate.

### Changed
- **Register.** "Held open" is now scoped to the breadth phase; once the elimination work is done
  the offer *probabilistically prioritises* a leading plausible narrative ("a plausible narrative,
  not an explanation") rather than flatly hedging — while still never crowning or diagnosing. New
  bans: presenting process-completion ("all auditors passed") as a quality claim, and offering a
  needless opt-in menu when both steps obviously need doing.
- **Context recovery.** After any compaction, the engine re-reads its working documents before
  continuing — it never reasons from a compressed summary.
- **Reconcile auditor** no longer rewards history-suppression: dropping a documented treatment
  response or an established prior without an explanation is now a failure.
- **Activation is compaction-proof and portable.** Hooks activate by walking up from the working
  directory to a `.investigate-active` marker the run writes into its own folder (the way git finds
  `.git`) — no session-id dependency, no hardcoded path.

## 0.1.0

Initial bundle: the non-directive investigation engine + extract / research / research-practitioner
/ product-search skills, the orchestrator front door (continuum + three lenses), enforcement hooks,
templates, and eval harness.
