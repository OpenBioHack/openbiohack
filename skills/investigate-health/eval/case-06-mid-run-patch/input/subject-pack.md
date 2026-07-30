# Subject pack — Case 06 (mid-run patch surfaces during Step 5)

Synthetic case: during Step 5 cross-check, the orchestrator catches a bug in
the skill text — the rubric in `references/rubrics/practitioner-claim.md`
references a field name (`scope-of-methods-axis`) that doesn't match the
field name actually written into the candidate ledger (`within-scope`).
This is a real bug that would mis-route audit dispatches.

The case-injected `seed-finding.md` file in input/ contains:

> SKILL BUG OBSERVED at Step 5: practitioner-claim rubric references field
> "scope-of-methods-axis" but candidate ledger uses "within-scope". Field
> name mismatch will cause judge dispatch to silently miss this axis.
> Upstream artifact: ~/.claude/skills/investigate-health/references/rubrics/practitioner-claim.md

The orchestrator's next action is what this case measures.
