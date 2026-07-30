# Round 1 — one pass, seven things to cover

This is asked once, in one sitting, in chat. The person is never asked to open a document, fill
in a form, or read anything back. They talk; it gets recorded verbatim; a script does the rest.

The old shape asked seven separate times and got seven separate starts. This asks once and then
checks what actually got covered — `interview_coverage.py` reads the answer back and names the
sections that came out thin, and only those get a follow-up.

---

## What is said to them

> I want to hear the whole thing in your own words, once, without me interrupting.
>
> Take as long as you want. Ramble. Go out of order — I can put things back in order afterwards,
> and I would rather have it messy and complete than tidy and thin. If you remember something
> forty minutes later that belongs at the start, just say it then.
>
> Three things that make this work:
>
> **Say the uncertainty out loud.** "I think", "around", "I can't remember whether" — those are
> data, and they are kept exactly as you say them. Nothing gets tidied into false confidence.
>
> **Don't decide what's relevant.** You don't know what turns out to matter and neither do I yet.
> The thing you nearly left out because it seemed unrelated is often the thing.
>
> **Nothing you say gets rewritten.** It gets copied, word for word. If a machine can't copy it
> exactly, it stops rather than guessing.
>
> Here are the seven things I want to make sure we get to. Don't answer them in order — just
> talk, and use this as a checklist at the end for anything you skipped.
>
> 1. **The whole story.** From whenever you think it starts to now. Whatever "it" is to you.
> 2. **Your life, decade by decade.** Where you lived, what you ate, what you were doing, what
>    was going on around you. Including the parts that don't feel medical.
> 3. **Before any of it started.** Childhood, your family's health, anything you were told about
>    your birth or your early years. What "normal" was for you before there was a problem.
> 4. **Your body, one part at a time.** Head to feet. Skin, eyes, mouth, chest, breathing, heart,
>    stomach, bowels, urinary, genitals, joints, muscles, nerves, sleep, energy, mood. For each:
>    is anything off now, was anything ever off, and when did it change.
> 5. **Everything you've tried.** Drugs, supplements, diets, protocols, procedures, practices.
>    What, how much, for how long, and what happened. Including the things you stopped.
> 6. **What made no difference.** The things that did nothing are as much information as the
>    things that worked, and they usually get left out.
> 7. **What you think is going on.** Your own theory. It matters, and it gets recorded as yours.

---

## How the answer is handled

The recording is transcribed and saved verbatim to the corpus. Nothing is summarised at any
point. The transcript becomes source blocks by byte range, exactly like a clinic letter does.

Then `interview_coverage.py` scores each of the seven sections and names the thin ones. A section
is thin if the answer barely touches it — the checker reports what it found, and a follow-up is
asked **for that section only**, in the person's own terms, quoting back what they already said
about it so they are not asked to repeat themselves.

A section that came out thin because there is genuinely nothing to say is marked as covered and
empty. That is an answer.
