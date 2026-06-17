# Failure modes this case tests

**Primary:** label-stuffing in synthesis layer — diagnosis labels appearing
densely in body text without translation to process descriptions, letting
the labels carry the reasoning rather than the underlying mechanisms.

Enforces:
1. `investigate-health-label-density` hook flags writes above the
   threshold (≤1 label per 200 words of body text, excluding
   `## Labels referenced`).
2. Synthesis translates labels to process descriptions on intake.
3. Labels confined to a trailing `## Labels referenced` section for
   cross-reference.

Linked SKILL.md rule: Step 2 §"Three-layer label rule (phase-aware)"
(Round 5).
