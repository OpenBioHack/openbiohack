---
name: self-report-pattern
version: 1.1.0
applies-to-claim-class: self-report-pattern
---

# Self-report-pattern rubric

Applied to any claim that a subject's symptom pattern is signal (vs noise,
recall bias, or post-hoc narrative). Pairs with SKILL.md §"Reproducible
reported reaction is signal, not noise".

## Axes

### Axis 1 — reproducibility

**Definition.** Has the pattern been observed multiple times, ideally with
the subject able to count instances?

- **1:** Single observation, narrated as pattern.
- **2:** 2-3 observations, loosely time-linked.
- **3:** 4+ observations, time-stamped or logged.

### Axis 2 — specificity

**Definition.** Is the trigger named specifically (an ingredient, a class,
a measurable condition) or vaguely ("stress," "fatty food," "weather")?

- **1:** Vague — class too broad to act on.
- **2:** Specific to a category (e.g. "high-histamine foods" without
  per-food breakdown).
- **3:** Specific to an item, dose, or measurable condition.

### Axis 3 — magnitude

**Definition.** Is the response magnitude distinguishable from background
variation in the same symptom?

- **1:** Within day-to-day noise.
- **2:** Above noise but only somewhat.
- **3:** Clearly above noise; subject would notice without prompting.

### Axis 4 — time-locking

**Definition.** Is the temporal link between trigger and response tight
enough to be informative (minutes to hours for histaminergic; longer for
other mechanisms — but specified)?

- **1:** Loose ("sometime that week").
- **2:** Within a day but not tighter.
- **3:** Within hours, consistent across instances.

### Axis 5 — provenance + stated confidence % (D7)

**Definition.** For an answer given live in the interview, capture two things and weight by them
*together*. **Certainty is not reliability** — a confidently-stated hazy memory weights down.

- **Confidence %** — captured as a percentage, *always* a %, never a 1–5 scale ("how sure, as a
  rough percent?"). This is the subject's own certainty.
- **Provenance** — one of:
  - `from-notes` — read from the subject's own notes / records / logs. Highest reliability.
  - `clear-recent-memory` — recent and the subject is sure of the memory. High.
  - `hazy-memory` — long-ago and/or the subject is unsure of the memory. Weights down.
  - `inference` — the subject is assuming / inferring, not reporting a direct experience. Weights down.

Do NOT use a "directly-experienced vs recalled" split — every answer is recalled, so the boundary
is not clean and does not help. Provenance + % is the replacement.

**Reliability weighting.** A `from-notes` or `clear-recent-memory` answer carries its stated % at
face value (top-authority own-data observation, register §"Authority is a third axis"). A
`hazy-memory` or `inference` answer is weighted **down even when the stated % is high** — record it
in `working-truth.md`'s `## Top-authority observations` with the provenance attached so downstream
synthesis cannot launder a hazy answer into hardened evidence.

| Provenance | Effect on weight |
|---|---|
| from-notes | full (at stated %) |
| clear-recent-memory | full (at stated %) |
| hazy-memory | downgrade one tier regardless of stated % |
| inference | downgrade one tier and flag as not-yet-observed; hold at T3 or below |

## Tier ceilings on axis failure

Axes 1–4 govern whether a *pattern* is signal; Axis 5 governs the *reliability of a single live
answer*. Apply whichever is in scope (a logged diary uses 1–4; a spoken interview answer uses 5,
and 1–4 too if it asserts a pattern). Ceilings stack — take the lowest.

| Axes failing (1–4) | Tier ceiling |
|---|---|
| 0 | No ceiling |
| 1 | Downgrade one tier |
| 2 | T3 |
| 3+ | T4 |

## Eval set

### Case 1 — recurring food→symptom pattern (synthetic)

**Primary source.** "Every time I eat aged cheese in the evening, within ~3-6
hours I get facial flushing and a headache that same evening. Observed at least 5 times
over a couple of months."

**Expected scores.** Axis 1: 3. Axis 2: 3 (aged cheese as a class — could
narrow further). Axis 3: 3. Axis 4: 2 (3-6h is loose for histamine but
consistent).

**Expected verdict.** No ceiling. The report is signal.

### Case 2 — "Stress triggers my migraines"

**Primary source.** "Stress is what triggers my migraines, I'm sure of it."

**Expected scores.** Axis 1: 2 (claimed but not enumerated). Axis 2: 1
(vague). Axis 3: 2. Axis 4: 1 (loose).

**Expected verdict.** 2 axes fail → **T3 cap**. Ask: count last 5
migraines, what preceded each in last 24h?

### Case 3 — single-event narrative

**Primary source.** "Last Tuesday I had a glass of wine and felt terrible
the next day. Wine must be the trigger."

**Expected scores.** Axis 1: 1 (single). Axis 2: 2 (wine is specific but
the active ingredient unclear — alcohol? sulfites? histamine? tannins?).
Axis 3: 2. Axis 4: 3.

**Expected verdict.** 2 axes fail → **T3 cap**. Hypothesis worth testing,
not yet a pattern.

### Case 4 — logged daily diary

**Primary source.** Daily symptom log 6 weeks, columns for sleep, food,
stress, symptom-score. "Symptom score correlates with previous-day sugar
intake, r=0.42 across 42 days."

**Expected scores.** Axis 1: 3. Axis 2: 3. Axis 3: 3 (r=0.42 is real).
Axis 4: 2 (next-day, not within hours).

**Expected verdict.** No ceiling.

### Case 5 — recall-bias case

**Primary source.** "Every time I've had this flare, I'd just eaten
gluten."

**Expected scores.** Axis 1: 2 (claimed multiple but not counted). Axis 2:
3 (gluten specific). Axis 3: 3. Axis 4: 2.

**Expected verdict.** 1 axis fails → downgrade one tier. Worth blinded
re-challenge to discriminate from recall bias.

## Change-log

- **1.1.0** (2026-06-18) — Added Axis 5 (provenance + stated confidence %, D7); ceilings stack.
- **1.0.0** (2026-06-09) — Initial.
