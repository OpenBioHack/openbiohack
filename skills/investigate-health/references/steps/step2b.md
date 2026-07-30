# Step 2b — Cross-document generator (fan out by symptom-cluster, not one flat agent)

Whole-picture generation: the hypotheses that ONLY appear across documents. The driver fans this out
per major symptom-cluster (plus a "whole-picture" pass) so cross-document coverage scales — one flat
agent misses links. Same output format and root-not-reaction discipline as 2a.

## Prompt

```
Same output format and root-not-reaction discipline as 2a, but you hold ALL documents and hunt the
hypotheses that ONLY appear across documents — a lab in one document whose TIMING lines up with a
symptom in another; a pattern no single document shows.

YOUR FOCUS: <<symptom-cluster or "whole-picture">> (the driver fans this out per major symptom-
cluster so cross-document coverage scales; one flat agent misses links).

Include explicit COMPOUND candidates — "X AND Y together" — where the data fits a combination better
than any single cause. Mark them `### HYP whole-<n> [COMPOUND]` and name both members.
```

(The 2a card format applies: for each candidate emit `### HYP …` with CLAIM / LENS / REASONING /
DATA / LIKELIHOOD. COMPOUND cards additionally name both members.)

## Haiku completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: `### HYP` cards for cross-document candidates, including at least the
  explicit COMPOUND candidates the data supports (each naming both members); each card carries CLAIM,
  REASONING, and the cross-document DATA (from ≥2 documents) that prompted it.
- COMPLETE means: candidates are genuinely cross-document (cite data from more than one document); a
  COMPOUND names both members; "no cross-document hypothesis for this focus" is complete and correct.
