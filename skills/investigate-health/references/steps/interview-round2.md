# Round 2 — the few things actually worth asking

Round 2 exists to ask a small number of specific questions and nothing else. It is assembled from
exactly two places, both of which have already thrown most of their material away:

- the sections `interview_coverage.py` found thin after round 1, and
- the candidate conflicts that survived all six tests in `reconcile.py`.

If both lists are empty, round 2 does not happen. That is a good outcome, not a failure.

---

## What is never asked

- **Anything a record already answers.** A lab value, an imaging finding, a measurement — the
  person cannot resolve those by remembering them, and being asked to reads as not being
  believed. Test 5 dismisses these before they get here.
- **Anything where both answers lead to the same next step.** Test 6.
- **Anything they already answered.** If they said it in round 1, it is in the document, and it
  is quoted back to them rather than asked again.
- **Anything phrased as a challenge.** "You said X but the letter says Y" is an accusation. The
  form is: here are two things that are both in your history, and I can't tell which way round
  they go.

---

## The shape of each question

> There's something I can't work out, and you're the only one who can tell me.
>
> [the first passage, quoted exactly, with when it belongs]
>
> [the second passage, quoted exactly, with when it belongs]
>
> [one sentence: what would have to be true for both, and why I can't tell]
>
> Which of those is closer? Or is it neither and I've got the wrong end of it?

The quoted passages are hydrated from `[[TL-…]]` identifiers by `cite.py`. Nobody retypes them,
so nobody can shorten a hedge or move a date while retyping.

For a thin section, the shape is instead:

> You covered most of it. One area I didn't get much on: [section]. Here's what you did say about
> it — [quoted exactly] — is there more, or is that genuinely all there is?

---

## What happens to the answers

The answer is recorded verbatim to the corpus like any other source, and inserted as **new
blocks** with `insert.py`. It is never merged into an existing block, never used to "correct" one,
and never used to edit one. What they said in round 1 and in round 2 both stand, with
their own dates, and if they differ that difference is itself part of the record.

A dated copy is taken before the round-2 insertions, so the pre-round-2 document survives intact:

    snapshot.py --doc timeline.md --label pre-round2

An empty answer produces zero inserts.
