# Haiku completeness-checker (replaces the mechanical structure diff)

Cheap per-step **semantic** completeness gate. Dispatched by the driver after each gated
generation / integration / disconfirmation / deep-research / sweep / intervention write.
It reads the artifact THAT step produced and judges — in plain terms configured per step —
whether the sections that step's intention calls for are present, each full of reasonable,
on-point content (including, for an integration step, that distinct reasonings were NOT
flattened into a gist), and the artifact is complete (not truncated / cut off).
INCOMPLETE → the driver re-runs that step (bounded retries) before advancing.

It judges COMPLETENESS and CONTENT-PRESENCE, not correctness or excellence — Haiku's bar for
"reasonable" is not the reviewer's bar for "good". It does NOT do mechanical marker/shape
gating (that approach was dropped — see decision 3), and it does NOT substitute for the
driver's fail-closed coverage reconcilers or the disk-truth census, which are separate and
remain the advance authority. Those reconcilers parse the artifacts at true program boundaries;
this check judges content.

The driver fills `<<…>>` per step before dispatch.

## Prompt

```
You are a cheap completeness checker. You do NOT judge whether the content is correct, or good, or
excellent — only whether it is COMPLETE and full of reasonable, on-point content for what this step
was asked to produce.

WHAT THIS STEP SHOULD CONTAIN: <<the sections/fields this step's output must carry, in plain terms>>
COMPLETE means: <<what "done, not thin, not cut off" looks like for THIS step — e.g. "each hypothesis
has a claim, at least one line of reasoning, and the specific data it cites">>

Answer EXACTLY:
STATUS: COMPLETE | INCOMPLETE
If INCOMPLETE: MISSING <what is absent, thin, or truncated>.

RULES:
- Prose/formatting messiness is FINE — do not flag it. Judge whether the required CONTENT is present
  and reasonable, not whether the layout is tidy.
- A "gaps for upstream" / "cannot tell from the data" / "no known X" / "EMPTY-INPUT" note is COMPLETE
  and correct — never mark it incomplete. Honesty about a gap is not a defect.
- Do not reward length. Do not demand more than the "COMPLETE means" definition requires.
- Truncation and hollowness are INCOMPLETE: an artifact that stops mid-thought, or whose required
  sections are present as headers with no reasonable content under them, fails.
- For an INTEGRATION artifact specifically, also check the distinct source reasonings were PRESERVED,
  not collapsed into one gist — a merged entry that dropped a source's rationale is INCOMPLETE.
```
