# Rubric schema

Every rubric file in this directory follows this fixed schema. The judge
council reads rubric files programmatically — schema drift breaks dispatch.

```yaml
name: <kebab-case-slug>
version: <semver, e.g. 1.0.0>
applies-to-claim-class: <one of: practitioner-claim | lab-result | family-history | self-report-pattern | study-tier>
axes:
  - id: <kebab-case>
    name: <human label>
    definition: <2-3 sentences>
    scoring:
      "1": <what a fail looks like, concrete>
      "2": <what a pass-with-caveat looks like>
      "3": <what a clean pass looks like>
tier-ceiling-on-N-axis-failure:
  "1": <tier ceiling when 1 axis fails>
  "2": <tier ceiling when 2 axes fail>
  "3+": <tier ceiling when 3+ axes fail>
eval-set:
  - case: <short label>
    primary-source: <verbatim quote, ≥30 words>
    expected-axis-scores: { <axis-id>: <1|2|3>, ... }
    expected-verdict: <tier ceiling>
    rationale: <one paragraph — why this scoring>
change-log:
  - version: <semver>
    date: <ISO>
    change: <one line>
```

A rubric file MUST have at least 4 axes and at least 5 eval-set cases.
Empty axes / empty eval sets are not allowed — the rubric is then not
fit for council dispatch.

## Three-pass adversarial design (required before any rubric ships)

1. **Pass 1 — Author drafts.** Write the rubric end-to-end.
2. **Pass 2 — Attacker.** Dispatch a separate sub-agent with the rubric and
   ask: "Find a case where the rubric scoring gives the wrong verdict.
   Adversarial — try to break it." Attacker writes ≥3 attempted breakers.
3. **Pass 3 — Judge.** A third sub-agent reads the rubric + attacker
   breakers and decides per breaker whether the attacker or the rubric is
   right. Rubric ships only when no breaker survives judge review.

The change-log records each adversarial pass and what was patched.
