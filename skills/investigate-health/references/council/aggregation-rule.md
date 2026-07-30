# Council aggregation rule

After all 3 judges return their YAML verdicts, the aggregator combines
them into a single council decision. The aggregator runs as a small
deterministic step in the orchestrator (NOT another LLM call — aggregating
verdicts via LLM reintroduces the trust-the-grader problem we built the
council to fix).

## Decision table

| Verdicts (sorted) | Decision |
|---|---|
| All 3 agree on tier ceiling | **Confident verdict** = agreed ceiling. Token issued. |
| 2 agree, 1 differs by 1 tier | **Verdict + disagreement-flag.** Use the 2-agreed ceiling. Flag recorded in decision log with the dissenting judge's rationale. Token issued. |
| 2 agree, 1 differs by 2+ tiers | **Escalate to human.** Do NOT auto-resolve. No token issued. The Write to the gated artifact (offering / verification-matrix) is blocked until human resolves. |
| 1-of-3 each different | **Escalate to human.** No token issued. |

## What "agree" means

Tier ceilings are compared by ordinal level (T0 < T1 < T2 < T3 < T4 < T5).
"No ceiling" is treated as the strongest level (= weight at evidence-
supported strength). "Agree" means same level. Adjacent levels = 1 tier
apart.

## Per-axis disagreement

In addition to verdict, the aggregator records per-axis disagreement
spread. If all 3 judges scored axis X at 3 different levels, that axis is
flagged for rubric-design review even if the overall verdict converged
(the rubric definition for that axis is likely ambiguous).

## Token issuance

On confident verdict OR verdict-with-disagreement-flag, the aggregator
shells out to `~/.claude/hooks/audit-council-completion.sh <claim-id>
<verdict>` which issues an HMAC-signed token to
`/tmp/claude/.audit-tokens/<session>-<gate>.token` per the
`skill-token-lib.sh` pattern. The gate hook
(`investigate-health-write-check.sh`) verifies the token before allowing
Writes to `verification-matrix.md` or `offering.md`.

On escalation, no token is issued. The orchestrator writes
`<root>/council-escalation-<timestamp>.md` containing all 3 judge YAMLs
verbatim + the dissent axes + a request for human resolution, and exits
the step cleanly.

## Recording

Every council dispatch produces, in the decision log:

```
COUNCIL DISPATCH: <step> / <claim-id>
  rubric: <rubric file>
  judges: skeptical, charitable, process-focused
  verdicts: skep=<T?>, char=<T?>, proc=<T?>
  aggregated: <verdict>
  disagreement-flag: <yes/no, on which axis>
  rubric-design-flags: <any from process-focused judge>
  token: issued | escalated
```

## Cost note

Council dispatch is scoped to T2+ load-bearing claims (per user decision
W2). Single-judge verification is used for practitioner claims below the
T2-load-bearing threshold and for all non-practitioner Step 5 cross-checks.
At Step 7 finish-line, council dispatch is unconditional — there is only
one finish-line per run, and the cost of an unaudited offering exceeds the
cost of 3 dispatches.
