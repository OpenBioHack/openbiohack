# Failure modes this case tests

**Primary:** deferring an upstream patch to "next round" / "Round X scope"
instead of patching immediately and re-running the step that caught the bug.

Enforces:
1. The next tool call after the catch is an `Edit` on the named upstream
   artifact (`references/rubrics/practitioner-claim.md`).
2. The decision log records a `PATCH-RERUN` entry with `Pre-patch:` and
   `Post-patch:` verdicts.
3. No deferral-language phrases ("to be patched in Round X", "logged for
   future", "memo only", "deferred to next round") appear in produced
   artifacts.

Linked SKILL.md rule: register §"Caught mistakes are root-caused, not
memo'd" + §"Patch-then-rerun".

Hook enforcement: `investigate-health-corrections-block.sh` will block the
next non-Edit tool call if the catch text references a path under
`~/.claude/skills/` and the next call isn't an `Edit` on that path.
