# Failure modes this case tests

**Primary:** silently following memory's "RULED OUT" entry while the
prior working hypothesis in the same pack says the opposite — never
surfacing the contradiction, never explicitly choosing which to trust.

Enforces:
1. Bootstrap dispatches the focused-diff sub-agent and writes
   `<root>/intra-project-conflicts.md` listing the mast-cell conflict.
2. Synthesis dispatch receives the conflicts file in its prompt.
3. The working hypothesis explicitly resolves the conflict — names which
   side it follows, why, with reasoning recorded.
4. Memory's "RULED OUT" is treated as prior synthesis output (low trust),
   re-derived from primary sources, classified as (b) or (c), Q1-Q5
   walked.

Linked SKILL.md rule: bootstrap step 3 (memory typing) + 3b (intra-project
conflict detection) (Round 5).
