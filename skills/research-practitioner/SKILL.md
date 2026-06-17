---
name: research-practitioner
description: Practitioner-grounded deep research that extends the standard /research engine with structural enforcement against shallow vendor-flavored synthesis. Use this skill whenever the user says "/research-deep", "deep research", "not just docs", "find practitioners", "what experts who shipped X learned", "deeper research", or asks any research question where prior research output was rejected as superficial. Also trigger automatically when the topic is a fast-moving technical domain (AI agents, LLM infrastructure, novel architectures) where documentation-deep answers reliably mislead and only practitioner experience reports carry signal. Trigger especially when the user is visibly frustrated with a previous shallow research output, when they explicitly ask for named experts/practitioners, when they say "I need to actually understand X", or when the user mentions wanting to build / ship / operate something rather than just compare options. The skill enforces tier-tagged claims, verbatim primary-source quotes, mandatory named-practitioner citations, three-pass adversarial iteration, banned confidence theater, and Norton-safe output. Includes a reference-doc sub-protocol for building structured foundational understanding split across multiple files per question cluster.
user_invocable: true
---

# Research-Practitioner Protocol

This skill extends the standard `/research` skill (see `~/.claude/skills/research/SKILL.md`) with additional structural enforcement designed to prevent a recurring failure mode: sub-agents reading aggregator pages for 4-12 minutes and returning confident-sounding synthesis dressed as expertise.

**Anchor incident**: a five-pass research project on agent infrastructure for B2B ops automation produced rising confidence theater (60% → 65% → 86% → 84%) while the user, a domain practitioner, repeatedly caught the research agents missing entire harness categories (OpenClaw, Hermes Agent), category-erroring Claude as a model rather than a platform, and parroting vendor capability claims without verifying against source code. Each pass was 4-12 minutes of aggregator skimming. The confidence numbers were performance, not estimates.

The standard `/research` skill already does most of the right things (18-step protocol, tier classification, banned probability words, pre-mortem, steel-man, anti-escalation rule). This skill adds the layers that specifically address documentation-deep failure: practitioner experience as a non-negotiable input, verbatim primary-source quotes, mechanism-before-marketing, three-pass adversarial iteration, mandatory output sections that make gaps visible, and Norton-safe markdown.

## Relationship to the standard `/research` skill

This skill **inherits** the entire standard `/research` protocol. Run all 18 steps of the standard skill as the base process. The additions below are layered on top, not in replacement of, that protocol.

- Phase 1 (Steps 1-4: Question Audit, Novelty, Constraints, Prior) — run as written.
- Phase 2 (Steps 5-9: Decomposition, Base Rate, Multi-Lens, Counter-Evidence, Causal Tagging) — run as written, with the practitioner mandate (Section 2 below) added inside Step 7.
- Phase 3 (Steps 10-13: Hypothesis Competition, Analogy Stress Test, Source-Independence, Survivorship) — run as written.
- Phase 4 (Steps 14-17: Pre-Mortem, Steel-Man, Confidence Calibration, Uncertainty) — run as written, with confidence calibration constrained per Section 7 below (tier tags, no numeric percentages in output).
- Phase 5 (Step 18: Blind Spots) — run as written.

The additions in this skill are gates that fire DURING and AFTER those steps.

## Invocation

`/research-deep <anything>` — full protocol.

Also auto-routes from any `/research` invocation where the topic matches the trigger conditions in the description (fast-moving technical domain, user frustrated with prior shallow output, user explicitly asking for practitioners, user mentions building/shipping).

### Reference-doc sub-protocol

`/research-deep reference <domain> [questions: <list>]` — produces a structured foundational reference doc on a domain, NOT a recommendation. Output is typically multiple files, one per question cluster, under a single directory. Used when the user wants to build mental scaffolding before making any decisions. The recommendation is a separate decision-making step that uses the reference doc as input — never combined into the same artifact.

When invoked in reference-doc mode, Steps 14-17 (Synthesis, Pre-Mortem, Confidence Calibration, Uncertainty) are reframed: the synthesis is "what is now understood about this domain" not "what to do." Recommendations are explicitly excluded.

---

## The 9 layered enforcement rules

Each rule fires at specific points in the standard `/research` protocol. A draft that violates any of these is **rejected before delivery**.

### Rule 1 — Source hierarchy with verbatim quotes

Every load-bearing claim gets an evidence tier. This refines the standard skill's Step 9 (Causal Level Tagging) by also classifying source quality, independently of causal level:

- **T1 Verified primary** — verbatim from peer-reviewed paper, official source code, or official spec. URL + verbatim quote required, inline with the claim.
- **T2 Docs + practitioner** — vendor docs PLUS at least one NAMED independent practitioner reporting consistent shipped experience.
- **T3 Single source** — one source only, marked "single-source." Treat with caution.
- **T4 Inferred** — reasoned from primitives, marked "inferred." No direct observation.
- **T5 Speculative** — untested hypothesis, marked "speculative."

A sentence in the final output without a tier tag is not a claim — it is a sentence to delete or restructure. Tier tags appear inline (e.g., "Anthropic's Agent SDK supports session resume via JSONL files (T1)"), not in a separate column.

**T1 verbatim requirement is non-negotiable.** A T1 claim that paraphrases instead of quoting verbatim is automatically downgraded to T3.

### Rule 2 — Practitioner experience is mandatory, not decorative

This is the most important addition to the standard skill. Vendor docs tell you what is **intended**. Practitioner reports tell you what actually **happens**. The gap between the two is where failures live.

Every cluster, every major section, every recommendation-adjacent claim must cite at least one **named practitioner** who **shipped** something — not opined, not theorized, not benchmarked in isolation. Where the cited practitioner is, what they built, what they learned.

Trusted anchor sources (non-exhaustive — actively look for others):

- Hamel Husain — hamel.dev — evals, error analysis, "Your AI Product Needs Evals"
- Simon Willison — simonwillison.net — security, prompt injection, daily experiments
- Eugene Yan — eugeneyan.com — production ML/LLM patterns
- swyx / Shawn Wang — latent.space — interviews with shipping practitioners
- Jason Liu — jxnl.co — structured output, instructor library, consulting
- Chip Huyen — huyenchip.com — ML systems, LLM eval
- Andrej Karpathy — Twitter/YouTube — fundamentals and agent design philosophy
- Anthropic engineering blog — post-mortems, Building Effective Agents
- OpenAI engineering — Practices for Governing Agentic AI
- LangChain engineering case studies (despite framework bias, real production data)
- Sierra (Bret Taylor's B2B agent company) blog
- HackerNews — search specific products, filter for top comments from people running it for 3+ months
- Reddit r/LocalLLaMA and r/MachineLearning practitioner threads
- AI Engineer Summit, NeurIPS, ICML conference talks
- arXiv post-2024 papers that include production deployment data, not just benchmarks
- Substacks of named engineers writing about agents they actually shipped

If a section cannot cite a named practitioner with shipped experience after a genuine search, mark it at the top of the file:

> **WARNING: DOCUMENTATION-DEEP ONLY — no practitioner experience found.**

Documentation-deep is not invalid — sometimes the practitioner literature genuinely doesn't exist yet. But the user must see the flag so they know to discount accordingly.

### Rule 3 — Mechanism before marketing

For each tool, technique, pattern, or system discussed, the output must answer "what does it actually DO at the primitive level" — quoting source code or official spec — BEFORE describing vendor positioning, market category, or comparative narrative.

The order is:
1. What is the actual code path, data flow, or specification? (Quote it.)
2. What primitives does it compose? (Loop, state, tools, memory, permission, etc.)
3. What does the vendor SAY it does? (Their positioning, with skepticism.)
4. Does (3) match (1)?

This catches the failure mode where vendor positioning is repeated as fact. If the source code shows X and the marketing page says Y, both go in the output with the discrepancy flagged.

### Rule 4 — Three forced passes

The standard skill's iterative loop is good in principle but in practice sub-agents return after one pass. This rule makes three passes explicit and non-optional.

**Pass 1 — Draft.** Structured answers to the assigned questions following all standard `/research` steps plus Rules 1-3 above.

**Pass 2 — Self-adversarial review.** Re-read the pass 1 draft. Identify the 5 weakest claims (those resting on a single source, those with the largest jump from evidence to conclusion, those that match vendor positioning suspiciously closely, those whose tier feels inflated). For each:
- Re-research with new searches
- Either strengthen with new evidence, OR downgrade the tier, OR mark UNVERIFIED
- Document what changed in a `## Pass 2 changes` section that survives into the final output

**Pass 3 — Hostile search.** For each major claim that could anchor a downstream decision, actively search for the OPPOSITE — "why X is wrong," "X failure modes," "X problems in production," "alternatives to X and why people moved." Quote any credible critic found, with their context. When dissent is genuinely absent (not just unsearched), say so explicitly: "Searched for critics of X using [search terms]; no credible dissent found." Absence of dissent must be earned through search, not assumed through silence.

The three passes are NOT optional. A draft that skips Pass 2 or Pass 3 is rejected.

### Rule 5 — Mandatory output sections

Every cluster document (or single document, in non-reference-doc mode) must contain these sections. Empty sections must be noted explicitly with a one-line explanation — never silently omitted. Empty sections are themselves information.

- `## What sources say` — the verified claims with tier tags
- `## What this actually means / where it might be wrong` — analysis (not summary), explicitly separating "what the source claims" from "whether it's right and whether it applies"
- `## Practitioner experience` — named shippers, what they built, what they learned. If empty, the file gets the DOCUMENTATION-DEEP warning at top.
- `## Where the evidence is thin` — explicit unknowns, single-sourced claims, places where the search didn't yield depth
- `## What I couldn't verify` — claims expected to find evidence for but didn't; tools/products checked but where docs are missing or behind login walls
- `## Hostile sources / dissenting voices` — what credible critics say, with quotes. If empty, must include the searched-for-dissent statement from Pass 3.

These sections force the analysis-vs-summary distinction structurally instead of relying on the writer to remember.

### Rule 6 — Norton-safe markdown

Norton antivirus has quarantined `.md` files in this project because of HTTP-pattern heuristics. To prevent data loss in the produced reference docs:

- Plain URL footnotes only — drop `http://` and `https://` prefixes. Use `docs.anthropic.com/...` not the full URL.
- No raw HTTP request blocks (no `GET /x HTTP/1.1` style).
- No stacked headers (`Host:` / `User-Agent:` / `Cookie:` on consecutive lines).
- No multi-line curl chains with stacked `-H` flags.
- No long base64 blobs adjacent to URLs.
- Don't stack 5+ URLs in an unbroken block — separate with prose.
- No raw fetched HTML pasted into the document.
- Prefer writing to stable project directories (under `~/Documents/0 Ai/projects/`) over `/tmp/`, since Norton scans `/tmp/` aggressively.

When delegating to sub-agents, paste the relevant subset of these rules into the sub-agent prompt — sub-agents do not inherit this skill.

### Rule 7 — Banned words and confidence theater

In addition to the standard skill's banned probability words ("likely," "probably," "could," "may"), this skill also bans:

- Marketing intensifiers: "leverages," "robust," "seamless," "delve," "nuanced," "tapestry," "utilize," "comprehensive," "production-ready," "battle-tested," "industry-leading"
- Numeric output confidence percentages on synthesis claims ("85% confident") — these are theater. They suggest Bayesian rigor that is not present. Use evidence tier tags (T1-T5) instead, which are honest about source quality rather than feigning probability calibration.
- "Best practices" without naming who practices them and at what scale
- "Research shows" or "studies have found" without naming the study, sample size, and methodology

The anti-escalation rule from the standard skill applies with extra force here: confidence at the END of any synthesis must not exceed confidence at the START. If the document gets more certain as it gets longer, you are being persuaded by your own prose.

### Rule 8 — Output is reference, not recommendation (in reference-doc mode)

When invoked in reference-doc mode (Section "Reference-doc sub-protocol" above), the output is structured knowledge to be consulted later, NOT a recommendation. Do not include "what to build," "recommended architecture," "best choice for X," or similar.

Recommendations are a separate decision step using the reference doc as input. Combining them into the same artifact causes the writer to bias the research toward supporting the conclusion they want to reach. Separation is structural protection against motivated reasoning.

In non-reference-doc mode, recommendations are allowed but must respect Rules 1-7.

### Rule 9 — Per-claim audit trail

Every output file ends with `## Sources` — every URL cited in the body appears here, tagged with evidence tier and a one-line note on what was actually extracted from it. URLs consulted but not cited go in `## Sources consulted, not cited` (with a one-line note on why they were not used — usually "marketing-only, no primitive detail" or "behind login wall" or "404").

This makes the audit trail inspectable. The user can sample-check any source to verify the quote is accurate.

---

## Reference-doc sub-protocol — concrete workflow

Use this workflow when the user wants foundational understanding of a domain split across multiple cluster files.

### Step A — Question generation (separated from answer generation, per standard skill's Design Principle 1)

The user provides the questions, OR the parent skill invocation generates them and the user validates BEFORE research begins. Questions are organized into clusters — typically 5-12 clusters of 3-6 questions each.

### Step B — Output directory

Create one directory for all cluster files. Naming convention: `<domain>-reference/` under the appropriate project path. Each cluster gets its own file: `<letter>-<short-name>.md` (e.g., `a-foundations.md`).

### Step C — Per-cluster sub-agent spawn

For each cluster, spawn a sub-agent with:
- The cluster's questions, verbatim
- The full Rules 1-9 in the sub-agent prompt (sub-agents do not inherit this skill)
- The output file path
- The skill's mandatory output sections list
- The Norton-safe markdown rules
- An instruction NOT to produce a recommendation

Sub-agents can run in parallel (one per cluster). Parallel sub-agents will all read overlapping source material — that's expected and acceptable; the cluster-specific framing produces different extraction.

### Step D — Parent-skill review before delivery

After all sub-agents return, the parent skill (or invoking conversation) MUST:
1. Read each cluster file end-to-end
2. Check that every mandatory section is present (Rule 5)
3. Check that the practitioner section is non-empty OR the documentation-deep warning is at top (Rule 2)
4. Spot-check 2-3 tier-1 claims by opening the cited URLs and verifying the verbatim quote (Rule 1)
5. Flag the 3 claims per cluster that the user is most likely to want to challenge

This review is what prevents the failure mode of relaying sub-agent output uncritically. The parent does not delegate trust; it delegates work and verifies the result.

### Step E — Index file

After all cluster files exist, write an `INDEX.md` at the top of the directory listing each cluster file with a one-line summary of what it contains. The user uses this as the navigation entry point.

---

## What this skill does NOT do

- Doesn't replace operating experience. A 60-minute research pass with rigorous practitioner citations is still documentation-deep. Some questions can only be answered by building the thing and watching it break.
- Doesn't guarantee correctness. It guarantees that claims are appropriately tier-tagged, sourced, and accompanied by visible gaps — not that the underlying field has reached consensus.
- Doesn't substitute for the user's domain knowledge. The user is the final filter. The skill makes their filtering possible by making the evidence base inspectable.

## Failure modes this skill prevents

| Failure mode | Mechanism in this skill |
|---|---|
| Aggregator-summary as expertise | Rule 1 (T1 requires verbatim primary) + Rule 2 (named practitioners) |
| Vendor narrative capture | Rule 3 (mechanism before marketing) + Rule 4 Pass 3 (hostile search) |
| Summary masquerading as analysis | Rule 5 (separate "what sources say" from "what it means / where it might be wrong") |
| Single-pass shallow | Rule 4 (three forced passes including self-adversarial) |
| Confidence theater | Rule 7 (no numeric percentages on output; tier tags instead) |
| Silent gaps | Rule 5 (mandatory sections including "what I couldn't verify"; empty must be noted) |
| Motivated reasoning toward predetermined recommendation | Rule 8 (reference-doc mode separates understanding from recommendation) |
| Untrustable citation chain | Rule 9 (per-claim audit trail with extraction notes) |
| File quarantined by AV | Rule 6 (Norton-safe markdown) |

Each rule maps to a specific failure that has actually happened in past research delegations on this codebase. The rules are not theoretical — they are countermeasures.
