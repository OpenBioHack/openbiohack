# Vision & Non-Goals

## What OpenBioHack is for

To make ordinary people **more capable of investigating their own hard, ambiguous health problems** — and of
optimizing toward thriving — by giving them a rigorous, first-principles thinking partner that runs on their
own data, shows its reasoning, and hands them sharper questions to keep asking. The win condition is not a
better report; it's a person who understands their own biology well enough to keep going.

Three commitments shape every decision:

1. **Non-directive, always.** It works in possibilities and options to discuss with a clinician — never
   instructions, verdicts, diagnoses, or promises. This is both an ethical stance and what keeps the tool in
   the educational/wellness lane.
2. **Honest about uncertainty.** Every claim about cause carries an honest evidence tier. It would rather say
   "I don't know, and here's the cheapest way to find out" than manufacture confidence.
3. **It runs on your machine, on your data.** The authors never see anyone's health information. Privacy is
   structural, not a policy.

## Non-Goals (things this deliberately will not become)

- **Not a doctor, diagnosis, or medical device.** It does not treat, diagnose, or tell anyone (or their
  clinician) what to do. If something might be serious, it says: seek care.
- **Not a protocol shop.** No one-size-fits-all stacks or "do this" plans. Named supplements live in a
  reference as *candidate levers to consider*, never as prescriptions.
- **Not a data-harvesting product.** No accounts, no cloud storage of health data, no telemetry on what
  people investigate. If that ever becomes necessary for a feature, the feature loses.
- **Not a funnel.** Attribution to the maintainer (and to greaterhuman.ai) stays *bare* — a credit line, never
  a sales pitch inside someone's health analysis.
- **Not a replacement for the relationship with a clinician.** It's built to make people *better* patients and
  collaborators, not to route around care.

## How we stay canonical without gatekeeping

The project wins by being **alive and trustworthy**, not by controlling forks. The eval harness is the moat:
it encodes the safety and quality guarantees as machine-checkable tests, so good outside contributions can be
accepted quickly and the bar can't silently erode. The most valued contribution is a new failing eval case —
see `CONTRIBUTING.md`.
