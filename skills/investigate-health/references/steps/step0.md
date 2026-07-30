### Step 0 — Onboarding

**Purpose: make sure the facts are straight and the goal is clear before any reasoning
starts.** There is no hypothesis yet, so there is nothing to question here — this step only
verifies the data and establishes what the person wants. It runs once, at the front of a fresh
investigation, before Step 1's analytical read.

**0.1 — Run extraction.** Invoke `/extract-health-data` on everything the person has shared (this
is the same invocation Step 1 documents in detail; running it here is the onboarding's first move,
and Step 1 then orients on its output). The product is the faithful per-source extracts in
`extracted/`, and the ONE cross-source document `extracted/timeline.md` — in which every
character is copied from a source by script and nothing is summarised.

**0.2 — Completeness pre-flight.** Before reasoning on the data, list the records a competent
investigator would *expect* to see for this presentation — for example: the full treatment regimen
with durations and co-administered agents; the onset timeline (what changed when, and what
pre-dated the first symptom); every intervention trialed and its result; the panels/imaging a
clinician would have ordered for this complaint. Check each expected record against what is
actually present. **An expected-but-absent record is a hole — name it explicitly, never silently
skip it.** Write the expected-vs-present map and the holes to `data-completeness.md`.

**0.3 — Hand the documents to the person (verification + empowerment).** Strongly suggest the
person read the extracted documents themselves — **name them and give a reading order** — because
verifying the raw facts is essential, and reading their own data is how they stay empowered rather
than handed a verdict. If they grant permission, open the documents for them (outside the sandbox
if needed). Ask them to confirm completeness and correctness — **the timeline especially** — and
to surface anything missing: a document they never provided, a source the extraction missed, a
record they forgot. (This is not hypothesis-questioning; it is fact-checking the inputs.)

**0.4 — Clarify the goal.** Ask what they are experiencing *now* and what they most want to
change, plus any priorities or constraints on what they're willing to consider. Write this to
`goals.md`. This is what the whole investigation is steered toward.

**0.5 — Write the explanandum: `presentation.md`.** This is the target the whole investigation aims
at. Every later stage reads it, and every candidate root cause is a candidate root cause of *this* —
not an explanation of incidental findings for their own sake. It is a REQUIRED output of this step:
if it is not on disk, the run halts here rather than handing the generators a dead path.

It carries two things.

*Prose* — the primary problem in the person's own framing, what they most want changed, and how to
treat findings that look unrelated. The body is one system: a finding that looks unconnected (an
out-of-range hormone, a lone lab value) is neither explained for its own sake NOR dropped — trace how
it could CONTRIBUTE to this presentation through systemic links. Carry forward whatever prose the
person gave you in 0.4; nothing from that is dropped in favour of the register below.

*An enumerated register* — every thing to be explained, one per line, each with a stable id, a date,
and a current/resolved marker:

```markdown
## E1 — <short name for the thing to be explained>
- state: current | resolved
- since: <YYYY[-MM[-DD]]>          (when it began, per the sources)
- as-of: <YYYY-MM-DD>              (the date of the latest source that speaks to it)
- source: <which source says so, with its `[src:]`>
- <one or two lines of specifics: what exactly is to be explained, in the person's own words where
  you have them>
```

Rules for the register:

- **Ids are stable.** `E1..En`, assigned once. Later stages cite them; renumbering breaks those cites.
- **`state:` is mandatory and is read off the latest source that speaks to the finding, not off the
  earliest.** A symptom every document describes but the person now says has stopped is `resolved`,
  and it says so with the date and the source that establishes it. Getting this wrong is expensive:
  an investigation that builds its whole explanatory set around a symptom the person no longer has
  has spent itself on the wrong target.
- **A resolved item stays in the register.** It is still something to be explained — what it was, and
  what changed. Never drop it for being historical.
- **Nothing is included on the strength of an untested claim.** Where a specific in the register rests
  on something the person said but has not actually tried, mark it so rather than stating it flat.
- Where `data/narrative/coverage.md` exists, an entry whose evidence is `never-asked` is a hole, not a
  finding — say which it is.

**0.6 — Compile-fidelity check.** Confirm every raw item is either carried into the compiled views
or explicitly excluded with a reason, and every supplement/treatment is tagged active / shelved /
past. (This dovetails with the extract sub-skill's own client-verification step.)

**Artifacts:** `extracted/`, `extracted/timeline.md`, `data-completeness.md` (expected vs present, holes
flagged), `goals.md`, `presentation.md` (prose + the `E1..En` register).
**Gate:** Phase A / the analytical steps cannot proceed until completeness is confirmed (or the
holes are explicitly accepted by the person) and `goals.md` exists.

