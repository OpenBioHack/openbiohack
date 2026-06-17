# investigate-health eval harness

Narrow regression cases. Each exercises one specific failure mode an
end-to-end run identified. Run `./run-evals.sh` to dispatch all cases and
grep the produced artifacts for the patterns in each case's `expected.md`.
Cases that fail block the change.

## Cases

| # | Slug | Failure mode tested |
|---|---|---|
| 01 | `case-01-nccah-base-rate` | Base-rate inflation for rare-condition family history; `verification` + `impact` field discipline |
| 02 | `case-02-ms-family-history` | Degree-of-relation table application; paternal grandmother → 2nd-degree → ~0.4-1% |
| 03 | `case-03-agent-overlap` | Agent overlap as observation, not Bayesian update; phrasing "observed in N agents" |
| 04 | `case-04-fexofenadine-trial` | Therapeutic-trial-as-discriminator with `start-reading-from` + `washout-needed` + `hard-no check` |
| 05 | `case-05-practitioner-rubric` | 4-axis rubric application; T4 cap on 2-axis fail; ENT-skepticism preserved |
| 06 | `case-06-mid-run-patch` | Patch-then-rerun: next tool call after catching bug is Edit on the named upstream artifact |
| 07 | `case-07-mediator-not-origin` | Integrator = mediator-node (4 gates), not graph-upstream origin (Round 5) |
| 08 | `case-08-ruled-out-splitting` | Rule-out typing (a/b/c) + Q1-Q5 atypical-presentation gate (Round 5) |
| 09 | `case-09-memory-vs-hypothesis-conflict` | `intra-project-conflicts.md` produced + explicit resolution (Round 5) |
| 10 | `case-10-label-density` | Label-density hook + label-translation rule (Round 5) |
| 11 | `case-11-atypical-presentation-pass` | Atypical-presentation gate generalised beyond mast cells (Round 5) |
| 12 | `case-12-register` | Register discipline: no outcome-promise / fresh-diagnosis / advisory-imperative; recorded-diagnosis reporting allowed (Round 6) |
| 13 | `case-13-orchestrator-routing` | OpenBioHack orchestrator: continuum lens selection on a blended floor+ceiling presentation; defer to engine; no hard mode-binary |
| 14 | `case-14-optimization-register` | Optimization-mode register: candidate-levers-as-options, no directive prescription / outcome-promise; four-layer ceiling honored |
| 15 | `case-15-ongoing-loop` | Check-in lens integrates returned logs against pre-registered prediction; confounder accounted; probability shift not verdict |

## Per-case layout

```
case-NN-slug/
├── input/                    Subject pack (small, focused — one failure mode)
├── expected.md               Greppable expected output: required quotes, fields, regex patterns
└── expected.fail-modes.md    What this case is specifically testing (human-readable)
```

## Adding a new case

Any new rule added to `investigate-health/SKILL.md` carries a new eval case
that would have caught its violation. The case must include:
1. The minimum input that surfaces the failure mode.
2. `expected.md` with at least 3 grep patterns the produced artifact must
   match (positive assertions) and at least 1 grep pattern it must NOT match
   (anti-pattern — the failure mode).
3. `expected.fail-modes.md` naming the failure mode in one paragraph and
   linking to the SKILL.md rule the case enforces.

## Running

You ("run the evals" or "run the investigate-health eval harness") to Claude
in a session. Claude then, for each case:

1. Reads `case-NN-slug/input/`
2. Invokes `/investigate-health` against it, writing artifacts under a
   fresh per-case work dir (e.g. `$TMPDIR/eval-run-<timestamp>/case-NN/`)
3. Runs `./run-evals.sh <case-dir> <work-dir>` to grep the produced
   artifacts against `expected.md` patterns
4. Reports pass/fail per case + summary

`run-evals.sh` is the deterministic grep checker — it does NOT dispatch the
orchestrator. The orchestrator IS `/investigate-health` running inside the
Claude session.

Batch mode: `./run-evals.sh --batch <work-base-dir>` greps every
`case-NN-slug/` subdir under the base.
