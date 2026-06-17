---
name: New eval case (most valued!)
about: Turn a real failure into a regression-proof test. This is the single most valuable contribution.
title: "[eval] "
labels: ["eval-case", "good first issue"]
---

## What did the tool get wrong?
<!-- e.g. went directive ("take X"), over-claimed cause, missed an obvious possibility, mishandled evidence -->

## Minimal synthetic input that surfaces it
<!-- A small, SYNTHETIC, de-identified subject. NEVER real personal health data. -->

## What the output MUST / MUST NOT contain
<!-- The greppable assertions. At least 3 MUST and 1 MUST_NOT (the failure mode). -->
- MUST:
- MUST:
- MUST:
- MUST_NOT:

## Which rule does this enforce?
<!-- Link the CLAUDE.md section or SKILL.md rule the case protects (e.g. CLAUDE.md §2 register). -->

<!-- If you can, open a PR adding eval/case-NN-slug/ with input/, expected.md, expected.fail-modes.md.
     See skills/investigate-health/eval/README.md for the format. Even the case alone (no fix) is welcome. -->
