# Contributing to OpenBioHack

Thank you — genuinely. OpenBioHack gets sharper for everyone every time someone catches a failure, tightens
the reasoning, or adds a test that locks in a fix. This is a tool people use on their own health, so the bar
is real, but the door is wide open.

## The single most valuable contribution: a failing eval case

The heart of this project is its **eval harness** (`skills/investigate-health/eval/`). Each case is a small,
synthetic subject plus a set of `MUST` / `MUST_NOT` patterns the produced analysis has to satisfy. They are
how we accept improvements *without* having to deeply re-review every change — if the evals pass, the safety
and quality guarantees hold.

So the highest-value thing you can do is **turn a real failure into a new eval case**:

1. You found the tool doing something wrong — over-claiming, going directive, missing an obvious possibility,
   mishandling evidence.
2. Add a case under `eval/case-NN-slug/` with: a minimal synthetic `input/` that surfaces the failure;
   an `expected.md` with at least 3 `MUST` patterns and at least 1 `MUST_NOT` (the failure mode); and an
   `expected.fail-modes.md` naming what it tests and which rule it enforces.
3. Open a PR. Even just the *case* (without a fix) is a gift — it makes the bug concrete and regression-proof.

See `skills/investigate-health/eval/README.md` for the exact format and existing cases.

## The non-negotiable: register

OpenBioHack is **non-directive** by design. Everything it produces speaks in **possibilities and options**,
never instructions, verdicts, or promises. Before submitting anything that changes prompt/skill text or
output, read **§2 "The non-negotiable register"** and **§3 "epistemic backbone"** in the root `CLAUDE.md`.
In short:

- Offer options to discuss with a clinician — never "take X," "you should," "I recommend."
- No outcome promises ("will fix / will resolve / solves it / fixable").
- "Diagnosis" only when attributing to a record or clinician — never originated in the tool's voice.
- Tier every claim about cause honestly; reserve "confirms/proves/clearly" for established facts only.

PRs that introduce directive or over-claiming language will be asked to revise, even if everything else is
great. It's the thing that keeps the project trustworthy and in the educational/wellness lane.

## Running the checks locally

The deterministic gates that CI runs (and that block merges) you can run yourself:

```bash
# register sweep — fails on directive/outcome-promise/fresh-diagnosis leaks in the docs
bash eval/register-sweep.sh

# eval-case structural validation — every case has expected.md with MUST/MUST_NOT
bash eval/check-eval-structure.sh
```

The **full** eval (actually running an investigation and grepping its artifacts) requires a Claude Code
session — it can't run headless in CI today. Maintainers run it before releases; if your change could affect
analysis behavior, run it locally with `skills/investigate-health/eval/run-evals.sh` and say so in the PR.

## Ground rules

- **No real personal health data** in the repo, ever — eval subjects are **synthetic** and de-identified.
- Keep the engine the spine: the orchestrator and references **defer to** `skills/investigate-health/`;
  don't fork its logic into the orchestrator.
- Match the surrounding style; keep `MEMORY.md`-style files as indexes, not stores (see `CLAUDE.md` §7).
- Be kind in reviews and issues. People are here on their own hard health journeys.

## What we'd love to hear (issues & discussions)

- Where the tone or language felt off — too confident, too vague, or anything that read as telling someone
  what to do.
- A possibility it missed, or one it over-weighted.
- Friction with your data — formats that broke, things that were hard to get it to read.
- Cost/time on your plan (which tier, how long, did you hit limits).

See the issue templates when you open an issue. New eval cases are always the most welcome PR.
