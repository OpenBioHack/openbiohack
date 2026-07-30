# Step 3 — Disconfirmation (one agent per hypothesis; try to kill each one with the person's own data)

This step is a **falsification filter, not a ranking.** Its only job is to shrink the candidate set by
confronting each hypothesis with the person's real data: the ones the data actively contradicts get parked
(reversibly); everything else survives to research. It does NOT decide which survivors are best — that is
the later prioritisation step. Nothing is deleted; parking here is PROVISIONAL and reversible at the Step-7
sweep-check, and a SEPARATE adversarial agent re-checks every parked hypothesis for myopia.

One agent handles ONE hypothesis and sees ONLY its own card (`hypotheses/cards/<Hn>.md`) plus the person's
compiled data — never the other hypotheses (seeing rivals biases the skeptic and adds nothing).

## Prompt (per-hypothesis disconfirmer)

```
Disconfirm one hypothesis — try to kill it with the person's own data.

You are a skeptic. You have been handed ONE candidate explanation for this person's health picture, and
your only job is to find where it FAILS against their real data. You are NOT ranking it, NOT comparing it
to other hypotheses, NOT deciding how likely it is — only: does the person's own data actively contradict
it, or not?

YOUR HYPOTHESIS: <<the one card: its claim, reasoning, and the data it cited>>
THE EVIDENCE:     <<the person's compiled data>>

A hypothesis dies only two ways:
  1. A finding it REQUIRES is confirmed ABSENT — but only if a test that could actually SEE it looked.
     APERTURE: a negative result disconfirms only within what that test can observe — and this covers
     PROCEDURES and graded-sensitivity tests, not just labs (a normal colonoscopy is silent on the upper
     gut; a normal calprotectin is silent on the small bowel). If you cannot tell what a test could see,
     assume it could NOT refute — FAIL OPEN.
  2. A finding is PRESENT that this cause cannot produce.

THE DISCIPLINE THAT KEEPS YOU HONEST: silence is not refutation. The records not mentioning something is
NOT evidence against it — "not mentioned" ≠ "ruled out." You demote ONLY on an active clash, never on a gap.

Hold your kills loosely. If the contradicting datum could just as well be the fingerprint of a DIFFERENT
cause acting alongside this one, do NOT kill it — record that datum as CONTESTED, so a later pass can check
whether a co-cause owns it. This is how a genuine co-cause avoids a false kill.

Also sanity-check the hypothesis's own reasoning is grounded: is the data it cites accurate, and does the
timing hold? Use a real symptom ONSET, not a diagnosis date or first-mention date; if onset is unknown, say
"onset unknown" and do NOT demote on a sequence you cannot establish. One shaky reasoning does not sink a
hypothesis its other reasonings still support.

If COMPOUND ("X AND Y"): test the combination's fit and give a per-member note — a compound can be
half-supported.

WRITE your verdict:
  STANDING: survives | parked
    - survives  = the data is consistent with it, or cannot yet distinguish it (this is the default; most
      survive). If the data POSITIVELY fits it, note that as an evidential observation (name the measured
      data) — but do NOT rank it or call it "leading"; whether it is a top candidate is decided later.
    - parked    = the data actively contradicts it (a hard disconfirmer within a valid aperture, or a
      wholly ungrounded core).
  REASON:      the exact finding behind the standing (the specific hard-disconfirmer datum if parked) —
               stored and revisited at the sweep.
  CONTESTED-BY: any datum that seems to sink THIS but might be explained by ANOTHER hypothesis.
```

## Separate adversarial reframe (a DIFFERENT agent, per parked hypothesis)

A different agent — not the one that parked it — is given the parked hypothesis + its REASON and asked ONLY:
"give the strongest case this was parked myopically — a subtype, a less obvious form, a co-cause context, or
an aperture the parker missed." If it finds one, the standing reverts to `survives`. (One anchored agent
rubber-stamps its own reframe; the myopia guard must be adversarial and separate.)

## Driver reconcilers (fail-closed)
- Every hypothesis card → exactly one STANDING (survives | parked).
- Every `parked` → an adversarial-reframe pass ran; its CONTESTED-BY datum is carried forward — this set is
  the Step-7 reopen pool and MUST reach the sweep.

## Completeness check (driver fills the checker slots)
- WHAT THIS STEP SHOULD CONTAIN: per hypothesis — the grounding sanity-check, the two-way disconfirmation
  pass with aperture reasoning, a STANDING (survives | parked), a REASON, and CONTESTED-BY where a datum
  might belong to a co-cause. For a COMPOUND, a per-member note.
- COMPLETE means: a standing is assigned with its supporting reason; a parked hypothesis carries the specific
  hard-disconfirmer datum in REASON; "onset unknown" and "aperture unknown → fail-open" notes are complete
  and correct answers. It does NOT rank survivors and never labels one "leading".
