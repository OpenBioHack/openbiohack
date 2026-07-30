<!-- Thanks for contributing to OpenBioHack! -->

## What this changes

## Type
- [ ] New eval case (the most valued kind)
- [ ] Fix to analysis behavior / prompt / skill
- [ ] Docs
- [ ] Tooling / CI
- [ ] Other:

## Checklists

**Register (required if you touched any prompt/skill/output text)** — see root `CLAUDE.md` §2–§3:
- [ ] No directive language to the person ("take X", "you should", "I recommend")
- [ ] No outcome promises ("will fix / will resolve / solves it / fixable")
- [ ] "Diagnosis" only where attributed to a record/clinician — never originated in the tool's voice
- [ ] Claims about cause carry an honest evidence tier; no "confirms/proves/clearly" below established

**Safety & privacy:**
- [ ] No real personal health data anywhere (eval subjects are synthetic + de-identified)
- [ ] The engine stays the spine — orchestrator/references defer to `skills/investigate-health/`, no forked logic

**Tests:**
- [ ] `bash eval/register-sweep.sh` passes
- [ ] `bash eval/check-eval-structure.sh` passes
- [ ] If behavior could change: I ran the relevant `skills/investigate-health/eval/` case(s) locally and noted results below

## Notes / eval results
