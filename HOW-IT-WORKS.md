# How this workflow thinks — the logic in plain words

This document explains, in ordinary language, **how the driver moves through its
work** — no jargon, no domain terms. If you can read a recipe, you can read this.

It goes **stage by stage and prompt by prompt**: what each step reads, what it asks
a worker to do, what it writes down, and how it decides whether to move on or stop.

Everything below describes `investigate-health-orchestrator.js`. Wherever this says
"a worker," the code calls it an *agent*; wherever it says "a note" or "a file," the
code writes a real file to a folder on disk.

---

## 1. The big picture — what kind of program this is

The driver is a **conductor**, not a performer. It never does the creative thinking
itself. For every piece of thinking, it hands a single, written instruction to a
worker, waits for the answer, checks that the answer actually landed on disk, and
only then moves to the next thing.

Three rules make this trustworthy:

1. **The code owns the order.** There is one fixed list of stages. A worker cannot
   skip ahead, reorder, or invent a shortcut — the conductor walks the list.
2. **Disk is the truth, not the worker's word.** After every step, the conductor
   asks a trusted counter: *"Did the file actually get written, and is it complete?"*
   A worker can claim `"done: true"` all it likes — if the file isn't really there,
   the conductor does not advance.
3. **When something expected is missing, it stops and says so.** Instead of limping
   forward on half-finished work, it writes a short *"here is where we stopped and
   why"* note and returns. The code calls this a **halt**.

---

## 2. The five building blocks (the whole vocabulary)

| Term | Plain meaning |
|---|---|
| **dispatch(instruction)** | Send **one** written instruction to a worker; get back a small structured answer. |
| **census** | A trusted headcount of which files exist on disk and whether each is complete. Re-taken after every write. |
| **isDone(file)** | Ask the census: *"Is this particular file there and complete?"* |
| **halt(where, why)** | Write a *"stopped here, because…"* note and return. Nothing downstream runs. |
| **stage** | One named chunk of work. There are **18**, in a fixed order. |

A recurring pattern you'll see in every stage:

```
do the work (dispatch one or more instructions)
re-take the census        ← look at disk again
if the expected file isn't there and complete:
    halt("stage X", "the thing named <file> is missing")   ← stop, name the gap
otherwise:
    move to the next stage
```

That pattern is the whole safety story. The worker's self-report is never the gate;
the file on disk is.

---

## 3. The two control knobs (run the whole thing, or just a slice)

By default the conductor runs the entire list from top to bottom — this is unchanged
and is what a normal run does.

On top of that, two optional knobs let you run just **one contiguous slice**:

- **startAt: "some stage"** — skip every stage *before* that one. (Their outputs must
  already exist on disk from a previous run — the conductor assumes they're there.)
- **stopAfter: "some stage"** — stop right *after* that one.

```
for each stage in the fixed list of 18:
    if this stage is BEFORE startAt:   skip it (assume its work is already on disk)
    if this stage is AFTER stopAfter:  stop and return

    otherwise: run the stage normally
```

Guardrails on the knobs:

- **No knobs set → the whole chain runs, byte-for-byte as before.** The knobs are
  inert when unused.
- **A nonsense knob is refused.** `startAt: "banana"` returns an error immediately and
  runs *nothing* — not even the first setup step. It never silently runs the whole
  thing instead.
- **A slice with a missing input stops loud.** If you ask to run a middle slice but a
  file it needs was never produced, the conductor halts and *names the missing file*,
  rather than quietly producing empty results.
- **Setup always runs.** The first setup step and the first headcount always run (even
  for a slice) so the conductor can see the real state of the disk before starting.

---

## 4. The 18 stages, in order — prompt by prompt

The names in **bold** are the stage names. Under each, the → lines are the individual
instructions sent to workers (the "prompts").

### 1. Bootstrap — open and sign the job
Sets up the working folder, writes a signed "this run is active" marker, and creates
the blank note-files the later stages fill in.

```
→ ONE trusted setup instruction: sign the run, register the folder, make blank notes.
if it didn't confirm a signed setup:  halt (refuse to run an unsigned job)
```
Why the signature matters: the very last stage (the finished write-up) is *refused*
unless this signature checks out. There is no way to sneak a write-up out the side
door.

### 2. Onboard — write down the goal and what we have
```
→ ONE instruction: write "here's the goal" and "here's what data we were given."
advance only if both notes are on disk.
```

### 3. Extract — turn the raw pile into tidy notes
Hands the raw material to a separate, dedicated helper that reorganizes it into clean,
sorted notes (and a small self-check). This stage does no interpreting — just tidying.
```
→ delegate to the extraction helper.
advance only if the tidy notes exist.
```

### 4. Generate — brainstorm many possible explanations, widely
The goal here is *breadth*: get lots of candidate explanations on the table, not just
the obvious one.
```
→ FIRST, one "list the documents" instruction (just enumerate what to read).
→ THEN one brainstorming worker PER document, each looking through a DIFFERENT angle
  (the angles are rotated so the pile isn't twenty copies of the same idea).
→ THEN one or more "look across all documents at once" workers, to catch explanations
  that only show up when you hold everything together (including "it's TWO things at
  once" combinations).
if any expected brainstorm file is missing:  halt.
```

### 5. Integrate — merge the duplicates into one clean list
Lots of workers brainstormed separately, so there are duplicates. This stage merges
them — carefully keeping each distinct line of reasoning, never flattening two real
ideas into one.
```
→ one merge worker per "family" of related ideas (kept separate, reasoning preserved).
→ THEN one assembler writes the single clean list: each idea gets a stable label
  (Item 1, Item 2, …), plus a marker for the "what if none of these" placeholder and
  for any must-not-miss safety item.
The clean list on disk is now the AUTHORITY for how many ideas there are — a worker
that under-reports cannot shrink the list.
(If the slice skipped this stage, a read-only re-parse recovers the list from disk.)
```

### 6. Disconfirm — try to knock each idea down using the person's own records
For every idea, a worker actively tries to *rule it out* against the person's own
records. Each gets a standing: still in play, or **set aside** (parked).
```
→ one "try to rule this out" worker per idea.
→ THEN, separately, a DIFFERENT worker re-examines each set-aside idea and asks
  "was this dismissed too hastily?" — if so, it flips back to in-play.
→ THEN one assembler writes the tidy standings ledger.
Parking is provisional and reversible — nothing is ever deleted.
```

### 7. Select — split into "still standing" vs "set aside"
```
→ ONE instruction: write the split — which ideas are still in play (to be researched)
  and which are set aside (kept on a bench they can be called back from later).
advance only if that split file exists.
```

### 8. Research — deeply look up ONLY the ideas still standing
**This is the key efficiency rule.** Deep research is slow and expensive, so it runs
**only on the ideas that survived the previous step** — never on the ones just set
aside.
```
→ FIRST, a read-only worker reads the split file and returns the list of survivors.

    IMPORTANT SAFETY VALVE (fail-closed):
    if the split file can't be found:
        HALT — "can't tell who the survivors are; refusing to just research everyone."
        (It must NEVER fall back to researching all of them — that's the exact
         expensive behavior this whole design removes.)

→ THEN, for EACH survivor only, two deep-research workers (two different angles),
  each of which also writes down the sharpest questions that would tell the ideas
  apart.
```
The set-aside ideas get **no** research here. (They can still be called back later —
see stage 13.)

### 9. Interview — ask the person the deciding questions, then PAUSE
This is the **one and only** place the whole run stops to wait for a human. A program
can't pause mid-run for a person to type, so the conductor produces the question set,
hands it back, and stops.
```
→ ONE instruction: turn the research into a clean list of questions for the person.
if the person's answers aren't on disk yet:
    PAUSE — hand back the questions, and wait to be resumed once answers are written.
if the answers ARE already there:
    keep going without pausing.
```

### 10. Cohere — check the whole picture still hangs together
After the answers come back, one worker checks that everything is consistent — the
records, the standings, and the new answers all tell a coherent story.
```
→ ONE instruction: write the "does it all hang together?" check.
advance only if that check exists.
```

### 11. Deepen — build a cause-and-effect map for each leading idea
For each of the top ideas, workers build a small step-by-step map of how one thing
leads to another.
```
→ per leading idea, in a chain: set the boundaries → sketch the shape → draw the map.
→ THEN, once, a single "how do all the maps fit together" pass and a "are the
  connections plausible" pass.
→ THEN one "here's where it all converges" summary per leading idea.
if any leading idea failed to converge:  halt (every one must finish).
```

### 12. Prioritize — rank them, and note what each would predict
```
→ ONE instruction: write the ranked list.
→ THEN, per leading idea, a note of "what would get better / worse / stay the same
  if this were the real driver" (a prediction sheet).
if any prediction sheet is missing:  halt.
```
(Small detail for slice control: stopping at the code label `'6'` stops *before* the
prediction sheets; stopping at `'prioritize'` runs the *whole* stage including them.)

### 13. Sweep — re-check every piece of data; call back anything set aside too soon
Go back over **every** piece of data, one at a time, against the maps. If a piece
that got an idea set aside is actually explained by a *combination* of causes, that
idea is **reopened**.
```
→ ONE instruction: check every datum; return the list of reopened ideas + anything
  still unexplained.

A reopened idea was set aside earlier, so it has NEITHER research NOR a map yet.
Give it BOTH, in order:
→ FIRST: run the same deep research on it now (so it doesn't reach the write-up as a
  map with no evidence behind it).
→ THEN: build its cause-and-effect map now, so the later stages can use it.
if a reopened idea's map is still missing afterward:  halt.
```

### 14. Intervene — for each map, look up what could be done about it
```
→ one worker per map: walk each step of the map and look up what could be acted on
  there (broadly — not just one narrow kind of action). "Nothing to do here" is a
  valid, required answer.
if any of these action sheets is missing:  halt.
```

### 15. Compose — write the person-facing write-up
Assemble the write-up as an opening plus several sections, each written by its own
worker and then stitched together deterministically.
```
→ build a small "the person's own words" glossary (so the write-up uses their words).
→ decide which items go in which section.
→ write the opening, then one worker per section (each pointed at the right map).
→ stitch the sections together into a single draft — by a fixed, mechanical join, not
  by a worker (so the order is always identical).
→ TWO coordination checks over the draft: is it plain-language? is every claim traceable?
if a section is missing, or a check fails:  halt.
```

### 16. Audit — seven independent checkers read the draft
Seven separate checkers each read the finished draft against the original sources
(not against the draft's own prose). Each must prove it actually read the draft.
```
→ seven checkers in parallel; each returns pass / fail and a proof-of-reading marker.
The finished write-up is refused unless:
  • all seven returned (a silent, dropped checker does NOT count as a pass),
  • all seven passed,
  • the earlier self-check exists,
  • and each checker left a fresh proof-of-reading marker with no open complaints.
otherwise:  halt.
```

### 17. Finalise — produce the clean final version
```
→ ONE trusted step: mechanically strip the internal tags off the approved draft to
  produce the clean, person-facing final file (by a fixed tool, never a hand-edit).
advance only if the final file exists.
```

### 18. Open threads — note what's still open, invite going deeper
```
→ ONE instruction: write "here's what's still open" + an invitation to go further.
Then the run is complete.
```

---

## 5. The two ideas worth remembering

Almost everything above is bookkeeping around **two** ideas:

1. **Only research what survived scrutiny.** Brainstorm widely, then knock ideas down
   against the person's own records first, and spend the expensive research *only* on
   the ones left standing. If an idea was set aside too soon, a later full sweep can
   call it back — and when it does, it gets its research **then**, on demand, so it
   never reaches the write-up as a claim with nothing behind it. And if the survivor
   list can't be read, the whole thing **stops** rather than quietly researching
   everyone (which is the exact waste this removes).

2. **Every stage can run on its own.** The default is still the whole chain, top to
   bottom, unchanged. But because every stage reads what it needs from disk, you can
   also say "just re-run this one part" — start anywhere, stop anywhere — and each
   stage that runs standalone either finds its inputs on disk or stops and names what's
   missing.

Underneath both: **the code owns the order, the disk owns the truth, and a missing
file is a loud stop — never a quiet guess.**
