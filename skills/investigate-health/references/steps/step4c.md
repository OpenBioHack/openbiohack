# Step 4c — Diagnostic-question generator + redundancy check (writes the interview's harvest contract)

Generate the questions that would most strengthen/weaken each survivor, drop the ones the records
already answer, and emit the section the UNCHANGED interview (`step5.5.md`, Phase-0 harvest) reads
verbatim. The interview harvests `## Differentiating diagnostic questions` FROM the per-hypothesis
`research/<hn>-…-consensus.md` and `research/<hn>-…-practitioner.md` files, so Step 4c must write that
section, in that exact shape, into those files — or the interview silently degrades.

## Prompt

```
From the 4b dossier + full compiled data, write the questions that would most strengthen/weaken this
hypothesis; DROP any the records already answer (note what the data says).

OUTPUT CONTRACT — emit the section the existing interview harvests VERBATIM, appended into this
hypothesis's `research/<hn>-…-consensus.md` and `research/<hn>-…-practitioner.md` files:

`## Differentiating diagnostic questions`
One question per line, each carrying (the interview's Phase-0 harvest expects exactly these three
attributes — see step5.5.md):
- `expected-answer-per-hypothesis`: what each live hypothesis predicts the answer to be (flag any
  FORK — where two hypotheses predict different answers, that is the sharpest separator);
- `sensitivity`: qualitative (how strongly a positive answer confirms);
- `specificity`: qualitative (how strongly the answer separates THIS hypothesis from the others).

Also tag whether each kept question is answerable-by-person or needs-a-test.

The interview harvests these sections and tops up where thin with its own paired /research +
/research-practitioner dispatch — so a hypothesis with a thin or empty set is acceptable, but the
SECTION HEADER must be present so the harvest finds it. Never author generic filler to pad the count.
```

## Haiku completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: a `## Differentiating diagnostic questions` section in each
  per-hypothesis research file, each kept question carrying expected-answer-per-hypothesis (forks
  flagged), qualitative sensitivity, qualitative specificity, and a person/test tag; dropped questions
  noted with what the records already say.
- COMPLETE means: the section header is present (even if the harvested set is thin — the interview tops
  up); no generic filler questions; the three per-question attributes are present on kept questions.
