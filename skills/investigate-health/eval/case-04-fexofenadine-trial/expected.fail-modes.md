# Failure modes this case tests

**Primary:** defaulting to lab-panel discriminators when a cheap reversible
therapeutic trial would discriminate the same hypothesis.

Enforces:
1. Fexofenadine (peripheral H1, no BBB, non-sedating — passes hard-no) is
   named as the trial.
2. Dose + duration specified (180mg/day × 4 weeks).
3. `start-reading-from`, `washout-needed`, and `hard-no check` fields all
   present in the discriminator plan entry.
4. Doxepin is NOT proposed (hard-no list explicitly excludes it).
5. The trial is preferred over a serum panel as the first discriminator.

Linked SKILL.md rule: Step 6 §"Therapeutic-trial-as-discriminator" + register
§"Pre-flight check against the person's hard-no list".
