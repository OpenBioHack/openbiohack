# Changelog

All notable changes to OpenBioHack are recorded here. The bundle is generated from the canonical
engine by `build/build-bundle.sh`; entries describe the engine behaviour the public bundle ships.

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
