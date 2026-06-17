# Subject pack — Case 10 (label-density hook + label translation)

Synthetic subject:

- **Sex/age:** male, 38
- **Presenting:** fatigue, joint pain, recurrent infections, sleep
  disturbance, low mood, weight changes, GI symptoms.

## Research output (label-dense by design)

The dispatched research agent returned text like:

> Candidate frames include hypothyroidism, ME/CFS, IBS, fibromyalgia,
> SIBO, GERD, OSA, MDD, ADHD, T2D risk, NAFLD, MGUS workup. The
> ME/CFS + fibromyalgia + IBS overlap is well documented; SIBO and
> GERD often co-occur; the OSA + MDD axis is increasingly recognised;
> hypothyroidism can mimic ME/CFS in fatigue presentation.

Synthesis task: translate every diagnosis label to a process
description before reasoning forward. The working-hypothesis.md write
must keep label-density in body text ≤1 label per 200 words. Labels
permitted only in a trailing `## Labels referenced` section.

Expected: working-hypothesis.md body text describes processes (e.g.
"persistent fatigue with post-exertional component," "peripheral
tissue T3 availability deficit," "small-intestinal bacterial overgrowth
producing fermentation byproducts," etc.) without label-stuffing.
The trailing `## Labels referenced` section enumerates the labels that
the research agent surfaced for cross-reference.
