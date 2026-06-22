---
name: research
description: General-purpose first-principles research engine that enforces genuine reasoning through structural gates — not advice to "think harder" but mandatory steps that prevent authority bias, lazy analogies, survivorship narratives, and summary-as-analysis. Use this skill whenever the user needs rigorous analysis of a complex question, strategic research, market viability analysis, technology assessment, competitive analysis, scenario planning, psychology research, processing studies, verifying clinical claims, or any deep research where getting it wrong has real consequences. Also trigger when the user says "research this deeply", "first principles", "think this through", "analyze this properly", "don't just summarize", "psych research", "find studies on", "verify this claim", or any variant suggesting they want genuine depth rather than plausible-sounding text. Especially important for novel or unprecedented questions where pattern-matching from historical precedent is unreliable. Includes specialized psychology/clinical research workflows (topic exploration, source processing, claim verification, zettelkasten connections).
user_invocable: true
---

# First-Principles Research Engine

This skill exists because AI research defaults to a specific failure mode: producing text that *looks* rigorous — good formatting, citations, logical flow — but rests on authority bias, lazy analogies, and narrative coherence rather than mechanism analysis. The skill prevents this through structural gates: mandatory steps that must be completed before proceeding. Structure beats instruction. "Think more rigorously" changes nothing. "State the prior before researching, generate three competing hypotheses before evaluating any, actively search for disconfirming evidence before concluding" produces measurable improvement.

## Core Design Principles

These five principles (derived from analysis of STORM, GPT Researcher, ReAct, claim decomposition systems, and gap-reflection architectures) shape every phase of the protocol:

1. **Separate question generation from answer generation.** The quality of research is bounded by the quality of questions asked. Generating questions and answers in the same pass means questions are shaped by what you already know — circular research. The question-engineering phase must complete before investigation begins.

2. **Enforce perspective diversity before convergence.** A single perspective produces a single frame. Multiple perspectives produce genuine coverage. The perspectives must be structurally different (economics vs. psychology vs. technology), not superficially different (slightly reworded versions of the same angle).

3. **Build in explicit disconfirmation steps.** After forming any hypothesis, actively search for contradicting evidence. This cannot be optional or implicit — it is a mandatory gate. The gap-reflection pattern: "What would change my conclusion? Go look for that."

4. **Decompose claims selectively, not universally.** Breaking everything into atoms helps weak reasoning but can hurt strong reasoning through noise. Decompose when claims rest on complex chains of reasoning. Leave simple factual claims intact. The decision of when to decompose is itself a reasoning step.

5. **Distinguish summary from analysis.** Summary asks "what does this source say?" Analysis asks "is this right, does the evidence support the conclusion, and does it apply to this specific question?" These are separate cognitive operations. The skill enforces them as separate steps.

**Architectural principle: The research loop is iterative, not linear.** A linear pipeline (search → summarize → write) produces first-draft quality. Depth comes from iteration — each cycle reveals something the previous cycle missed. The stopping criterion is not "have I done N iterations?" but "has anything in the last iteration changed my understanding?"

## Invocation

`/research <anything>` — that's it. Just say what you need.

### Auto-Routing

The user will never specify a mode. Read their input and route automatically:

| If the input looks like... | Route to | Why |
|---|---|---|
| A broad question or complex topic | **Full protocol** (Steps 1-18) | Needs the full engine — question audit, multi-lens analysis, evaluation, synthesis |
| A quick/simple question, or user says "quick" / "briefly" | **Quick protocol** (Steps 1-4, 5-9, 14-16) | Skips evaluation phase, keeps research and synthesis gates |
| A specific claim to stress-test ("is it true that...", "they say X...") | **Decompose** sub-protocol | Claim decomposition — break it apart, test each link |
| A psychology/clinical topic to explore ("what does the research say about...") | **Topic** sub-protocol | Evidence hierarchy search, clinical checklist, zettelkasten note suggestions |
| A URL or paper title to process | **Source** sub-protocol | Process into literature note, connect to existing knowledge |
| A request to fact-check something | **Verify** sub-protocol | Find original source, apply clinical checklist, verdict + caveats |
| A zettelkasten note to find research for | **Connections** sub-protocol | Supporting, challenging, and extending evidence |

When in doubt, default to the full protocol — it's better to do too much thinking than too little. If the input genuinely fits multiple modes (e.g., "is this claim true and what does the broader research say?"), combine: decompose the specific claim, then run a topic exploration on the broader question.

---

## Phase 1: Pre-Research (Steps 1-4)

This phase completes before any investigation begins. Its purpose: interrogate the question itself, classify the problem, identify what you think you know before looking, and surface the assumptions that will otherwise operate invisibly throughout the analysis.

### Step 1 — Question Audit (Targeted Assumption Attack)

Do NOT mechanically run through a checklist of Socratic categories. Instead, do three things that actually matter:

**1a. Identify the Most Dangerous Assumption.** What is the single assumption embedded in this question that, if wrong, would make the entire analysis worthless? Not a list of every assumption — the ONE that carries the most weight. Name it explicitly. This assumption gets researched FIRST in Phase 2, before anything else.

Example: "Will AI replace coaches?" — the most dangerous assumption is that "coaching" is a stable, unified category. If coaching is actually 5 different functions bundled together, some replaceable and some not, then the question itself is malformed. Answering it as-asked guarantees a shallow answer.

**1b. List the embedded assumptions that feel obviously true.** These are the ones most likely to be adopted conventions mistaken for facts. "Obviously true" is a red flag — it means the assumption hasn't been examined. Classify each as:
   - *Empirical* — can be checked against evidence
   - *Logical* — follows necessarily from definitions
   - *Adopted convention* — a choice mistaken for a truth ← most hidden assumptions live here

**1c. Reframe the question.** Reframe at least two ways. The reframes must be structurally different — they should change what kind of answer would satisfy the question. Pick the framing (original or reframed) that best serves the user's actual need. State which and why.

### Step 2 — Novelty Assessment

Classify the question:
- **Well-precedented**: Expert consensus exists. Pattern-matching appropriate. Search for consensus, verify via evidence. Don't over-engineer.
- **Partially novel**: Some precedent, but genuinely new elements. Hybrid: use precedent for known parts, decompose novel parts from first principles.
- **Genuinely unprecedented**: No reliable precedent. Full decomposition required. Historical analogies are hypotheses, not evidence. This is where first-principles reasoning has the highest payoff — and where it's most commonly skipped in favor of lazy analogy.

This classification determines the depth of every subsequent step.

### Step 3 — Constraint Classification

Identify all stated or implied constraints on the problem. Classify each as:

- **Physical / logical** (immovable): Laws of physics, mathematical necessity, definitional truths. These are genuine boundaries.
- **Conventional / historical** (potentially movable): "It's always been done this way," "the market expects X," "industry standards require Y." These are choices that became invisible. Most "it can't be done" claims rest on conventional constraints dressed up as physical ones.

Focus disproportionate research attention on conventional constraints — that's where hidden opportunities and errors live.

### Step 4 — Prior Statement

Before any research, state:
- **Prior probability** for the main question (numeric, not "likely" or "probably")
- **Basis** for the prior: base rate, domain knowledge, previous evidence, or reasoning
- **Key uncertainty**: What are you least sure about?

This prevents anchoring to the first source found. With an explicit prior, you can track how evidence actually updates belief rather than replacing it wholesale.

---

## Phase 2: Research (Steps 5-9)

Investigation with structural diversity built in. This phase uses the STORM insight: quality of research is bounded by quality of questions. Generate questions from multiple perspectives before gathering evidence.

### Step 5 — Decomposition into Sub-Questions

Break the main question into atomic sub-questions. For each sub-question:
- **Label**: Is this empirically answerable (can be checked against data) or fundamentally uncertain (depends on future events, values, or unmeasurable factors)?
- **Identify dependencies**: Which sub-questions must be answered before others can be?

Organize sub-questions into a research tree. The tree structure makes the reasoning chain visible — you can see which conclusions rest on which foundations.

### Step 6 — Base-Rate Search (Outside View First)

Before analyzing the specific case, find the base rate. "How often do things like this happen in situations like this?"

If 90% of AI startups fail → your analysis of a specific AI startup starts from 90% failure.
If 70% of "new category" plays turn out to be repositioned existing categories → your "category creation" analysis starts from 30% genuine novelty.

The base rate is almost always more informative than the specific case. Most bad predictions come from ignoring base rates. The specific case must provide *strong, specific evidence* to justify moving significantly from the base rate — not just a compelling narrative.

### Step 7 — Multi-Lens Analysis

Examine the question through at least three structurally different disciplinary lenses. These must differ in their foundational assumptions about how the world works, not just in emphasis.

Common lens combinations:
- **Technology** (capability, trajectory, physical constraints) + **Economics** (incentives, cost structures, market dynamics) + **Psychology/Behavioral** (adoption patterns, resistance, habit formation, identity)
- **Historical** (precedent patterns — but stress-tested, see Step 11) + **Institutional** (regulatory, legal, organizational) + **Cultural** (values, norms, meaning-making)
- **Supply-side** (what's technically possible) + **Demand-side** (what people actually want and will pay for) + **Structural** (what the system architecture rewards and punishes)

For each lens, generate 2-3 specific sub-questions that this discipline would ask. These questions drive the investigation.

**When subagents are available**: Spawn one agent per lens for parallel investigation. Each agent researches its assigned questions, presents findings with citations, flags uncertainties, and notes contradictions with other lenses. The contradictions are where the most important insights live.

### Step 8 — Mandatory Counter-Evidence Search

*This step is non-negotiable. It is the single highest-leverage intervention against confirmation bias.*

After the initial investigation produces an emerging picture, actively search for evidence that would make it wrong. Not "consider the other side" — *actually go look for data, studies, cases, or mechanisms* that contradict the emerging conclusion.

Search specifically for:
- Cases where the identified pattern broke down
- Data pointing the opposite direction
- Mechanisms that would prevent the predicted outcome
- Stakeholders whose incentives run counter to the conclusion
- The smartest people who disagree, and why

If you can't find disconfirming evidence after genuine effort → note this (it increases confidence).
If you find it and it's weak → explain specifically why it's weak.
If you find it and it's strong → revise the conclusion. The goal is accuracy, not consistency.

### Step 8b — Evidence Evaluation Gate (Summary ≠ Analysis)

*This gate enforces Design Principle 5. Without it, the research phase produces summaries that feel like analysis but aren't.*

After gathering evidence from Steps 7-8, evaluate each major piece of evidence BEFORE proceeding to synthesis. For each key source or finding:

1. **What does it claim?** (Summary — what the source says)
2. **Is the methodology sound?** (Analysis — is the evidence strong enough to support the claim? Sample size, controls, confounders, measurement validity)
3. **Does the evidence actually support the conclusion the source draws?** (Analysis — authors routinely overstate implications. "Significant" means statistically detectable, not necessarily meaningful.)
4. **Does this apply to THIS specific question?** (Analysis — a study about CBT chatbots may not apply to an IFS coaching app. A finding about Gen Z trust patterns may not apply to 40-year-olds. Specify the gap.)

If you catch yourself writing "Research shows that..." or "Studies have found..." without having answered questions 2-4, you are summarizing, not analyzing. Stop and do the analysis.

**When evaluating clinical or psychology studies**, also apply the Clinical Study Checklist (below). Clinical research has specific methodological pitfalls that general evidence evaluation misses.

### Clinical Study Checklist

This checklist is a mandatory gate for any clinical, psychology, or therapy-related study encountered during research. Apply it in addition to the general evidence evaluation in Step 8b.

**1. What exactly was measured?**
- "Depression improvement" could mean: self-report questionnaire, clinician rating, functional outcome, or symptom count
- "Therapy works" could mean: better than nothing, better than placebo, better than another therapy
- Be specific about what the numbers actually represent

**2. What was the comparison group?**
- Therapy vs. no treatment (a low bar)
- Therapy vs. active placebo (a meaningful bar)
- Therapy A vs. Therapy B (the real question)
- No comparison group at all (not evidence for effectiveness)

**3. How were participants selected?**
- Self-selected volunteers behave differently from random samples
- Clinical trials exclude the most complex cases (comorbidity, suicidality)
- University students are not representative of the general population
- Note any selection bias that limits generalizability

**4. What's the effect size in human terms?**
- Never present raw effect sizes (d, g, r) to readers
- Translate: "Out of 100 people who tried this, roughly X did better than they would have without it"
- Compare to meaningful benchmarks

**5. Has this replicated?**
- Single studies are hypotheses, not facts
- Pre-registered replications carry more weight than original findings
- If the finding hasn't replicated (or replication was attempted and failed), say so explicitly

**6. Who funded it?**
- Industry-funded therapy studies show systematically larger effects
- Note funding source — it doesn't invalidate the finding, but it's context

**7. What's the dropout rate?**
- ITT (intention-to-treat) includes everyone who started
- Completer analysis only includes people who finished
- High dropout (>30%) means the intervention may not work for many people
- "50% of completers improved" sounds different from "30% of everyone who started improved"

**8. What does this mean vs. what does the author claim?**
- Authors often overstate implications
- "Significant" means statistically detectable, not necessarily meaningful
- Check whether the conclusions actually follow from the data presented

### Step 9 — Causal Level Tagging

Tag every claim produced during research with its causal level (Pearl's Ladder of Causation):

- **Level 1 — Association** (seeing): X and Y co-occur. "Companies with coaching programs have higher retention." This is correlation. It does not establish that coaching causes retention — companies that invest in coaching may differ systematically from those that don't.
- **Level 2 — Intervention** (doing): Changing X causes Y. "Introducing coaching increased retention by 15% in a controlled trial." Requires controlled evidence with an identifiable mechanism.
- **Level 3 — Counterfactual** (imagining): "If coaching hadn't been introduced, retention would have dropped to X%." Requires the strongest causal model and is rarely fully supported.

For any Level 2+ claim, require an explicit mechanism — *how* does X cause Y? Through what specific pathway? If you can't describe the mechanism, downgrade to Level 1. This single check catches most "correlation presented as causation" errors.

**The Mechanism Beneath the Mechanism.** For every causal claim, go one level deeper than the first explanation. If the initial explanation is "X caused Y," ask: what specifically about X caused Y, through what pathway, driven by what incentive or force? The first-level mechanism is often a narrative summary that sounds explanatory but isn't. The real insight lives one level down.

Example: "Recorded music made live concerts more popular" is a first-level explanation. One level deeper: did recordings create *desire* for live music, or did streaming destroy album revenue, forcing artists to tour as their primary income source? These are different mechanisms with different implications. The first says demand pulled supply. The second says supply economics pushed supply. Only by going one level deeper do you discover which is actually happening — and which one matters for your question.

### Step 9.5 — Claim-Strength Tagging (locational / exclusionary / prevalence claims)

Causal-level tagging (Step 9) measures *how causal* a claim is. This step measures *how strongly the source actually establishes it* — a separate axis that a downstream investigator (e.g. `/investigate-health`, which dispatches this skill) relies on to decide whether a claim may **remove a candidate** from consideration. The failure this prevents: rendering a "we didn't look there" claim as if it were a "we looked and it's absent" claim — the exact slip that lets a wrong candidate be excluded on no evidence.

**Tag every locational claim** ("X lives in / acts in compartment C"), **every exclusionary claim** ("X is not present / not the cause / has been ruled out"), and **every prevalence claim** ("X is rare / common / found in N% of cases") with one of:

- **(a) examined-and-established-with-mechanism** — a source directly examined this and reports the finding *with the mechanism or measurement behind it*. This is the only strength that may be used downstream to **exclude** a candidate. It must cite the **primary-source sentence** that establishes it (quote or precise locator), with enough sources that an auditor could independently verify it.
- **(b) primarily / mostly** — the source states it as a general tendency ("X is *primarily* colonic"), not an examined-and-excluded finding for the specific case. Carries real weight but **may not exclude** anything — a "primarily" leaves the minority case open.
- **(c) not-observed-but-never-examined** — the claim is an *absence of evidence*, not evidence of absence: no source actually looked at this question, or the test that would show it was never run. **May not exclude anything**; carry it with an explicit "not examined here" flag.

**Rules.** Never render a (b) or (c) claim in (a)'s language — no "is absent" / "has been ruled out" / "is not found" wording on a claim that is really "primarily" or "never examined." When a tag is (a), include the citation an auditor needs to verify it *in the same line*. When the honest tag is (b) or (c), say so plainly — "sources describe X as primarily colonic, but I found none that examined the small bowel directly, so its presence there is not-examined, not excluded." A downstream skill treats only (a)-tagged exclusions as binding.

---

## Phase 3: Evaluation (Steps 10-13)

Stress-test every conclusion before it enters the synthesis. This phase exists because the most insidious failure mode of AI research is structural correctness without substantive depth — output that *reads* like good research because it has the shape of good research, while the actual reasoning underneath is thin.

### Step 10 — Hypothesis Competition (Inference to Best Explanation)

Generate at least three genuinely different explanations for the evidence gathered. They must be structurally distinct — different proposed mechanisms, not minor variations of the same idea.

Evaluate each against Inference to Best Explanation criteria:
- **Simplicity**: Which requires the fewest assumptions?
- **Scope**: Which explains the most evidence?
- **Unification**: Which connects previously separate phenomena?
- **Mechanism**: Which provides the clearest causal pathway?
- **Fertility**: Which generates the most testable predictions?

Then identify **discriminating evidence**: What evidence *would* distinguish between these hypotheses? If no discriminating evidence exists or is obtainable, acknowledge that the question is currently underdetermined — do not pick a winner by default. Underdetermined questions should be presented as such, with the confidence level reflecting the ambiguity.

### Step 11 — Analogy Stress Test

Every analogy used anywhere in the analysis must pass this test:

1. **Structural mapping**: What specific structural relationships (mechanisms, causal pathways, feedback loops) does this analogy map?
2. **Structural differences**: What structural differences exist between the source and target domains?
3. **Do the differences matter?**: For the specific conclusion being drawn from this analogy, do the structural differences affect the validity?

If (3) is yes → the analogy is misleading for this purpose. Flag it, set it aside, and reason from mechanism instead.

Example of a failed stress test: "Live music survived streaming, therefore human coaching will survive AI." The structural mapping is: "human activity that coexists with a cheaper technological alternative." But the *mechanism* of live music value (physical co-presence, sensory immersion, social event, unreproducible acoustic experience) is structurally different from the mechanism of coaching value (relational attunement, personalized challenge, accountability, felt safety). The analogy maps a surface feature while ignoring the structural question: *what specific mechanism makes the human version irreplaceable, and does AI replicate that mechanism or not?*

### Step 12 — Source-Independence Test

For every claim supported by a prestigious or authoritative source:

"If this exact same claim were made by an anonymous person with no credentials, would the evidence and reasoning still be convincing?"

If no → the analysis is leaning on authority, not evidence. The source's identity tells you whether to investigate further. It never tells you whether the claim is true.

This catches:
- "McKinsey says the market is $X billion" → Evaluate the methodology, not the brand
- "A Stanford study found..." → Evaluate the study design, not the institution
- "Woebot failed, therefore D2C mental health doesn't work" → Decompose *why* Woebot failed, test whether those specific mechanisms apply to this specific situation
- "Yara wrote that the space is too hard" → What specific obstacles did Yara identify? Are they structural or circumstantial?

### Step 13 — Survivorship & Base-Rate Check

For any argument of the form "X survived Y, therefore Z will survive W":
1. What's the **base rate** of survival for things like Z? How many *didn't* survive?
2. Name at least three things that **didn't survive** similar disruption
3. Identify the **mechanism** differentiating survivors from casualties — what structural feature protected survivors?
4. Does Z share the survivors' protective mechanism, or the casualties' vulnerability?

Without this check, you're constructing narratives from winners only. "Netflix survived the streaming transition" is a survivorship story — it ignores Blockbuster, Hollywood Video, and hundreds of other companies in the same space.

---

## Phase 4: Synthesis (Steps 14-17)

Assemble the analysis. Every claim traces to evidence. Every conclusion has explicit confidence. The reader can follow the full reasoning chain from foundation to conclusion.

### Step 14 — Inversion / Pre-Mortem

"This analysis was published six months ago and turned out to be completely wrong. Why?"

List three specific, plausible failure modes. They must be *specific* — not "we didn't have enough data" but "the assumption that [X] would remain stable was wrong because [Y] is actively changing it."

This technique (developed by Gary Klein) gives psychological permission to surface concerns that forward-looking analysis suppresses. It works because projecting into a future where failure has already occurred removes the social/cognitive pressure to agree with the developing consensus.

### Step 15 — Steel-Man the Counter

State the strongest possible argument against the main conclusion. Not the weak version that's easy to dismiss — the version a smart, informed, well-prepared critic would make. The version that would be stated by someone who genuinely believes the opposite and has good reasons.

Then explain:
- Where the counter-argument is strongest (acknowledge this)
- Why the main conclusion survives it (or how the conclusion should be modified to account for it)
- What would make the counter-argument decisive (what evidence would tip the balance)

### Step 16 — Confidence Calibration

For every major conclusion:
- **Numeric confidence**: X% — not "likely" or "probably." Vague probability language is banned in this skill. Translate: what probability are you actually assigning?
- **Key supporting evidence**: The 2-3 pieces of evidence that most justify this confidence level
- **Update triggers**: What specific, observable evidence would move confidence significantly up or down? By roughly how much?
- **Known unknowns**: What information would meaningfully improve the analysis but isn't available?

### Step 17 — Uncertainty Transparency

Explicitly separate:
- **Known**: What the evidence clearly supports
- **Assumed**: What the analysis takes as given but hasn't verified (flag each assumption)
- **Unknown**: What cannot currently be determined and why
- **Unknowable**: What is genuinely unpredictable (vs. merely unknown — an important distinction)

This map prevents the common failure of presenting assumptions with the same confidence as evidence.

---

## Phase 5: Meta-Check (Step 18)

### Step 18 — Blind Spots and Forward-Looking Self-Critique

Do NOT ask "was this protocol appropriate?" (the answer is always yes — the user asked for it). Instead, do something harder:

**18a. Name three things this analysis most likely got wrong that you can't currently see.** Not generic risks — specific blind spots in THIS analysis. What are you most uncertain about that you've treated as settled? Where did you make a judgment call that could go the other way? What evidence would you find in 6 months that would make you cringe at this analysis?

**18b. Identify the strongest piece of evidence that this analysis under-weighted.** Every analysis implicitly weights some evidence more than others. Find the piece of evidence you encountered that most challenged your emerging conclusion — the one you may have minimized because it didn't fit the narrative. State it clearly and explain why it might matter more than you gave it credit for.

**18c. What should the next researcher look for?** If this analysis is being updated in 3-6 months, what specific data points, events, or developments would most change the picture? Not generic "watch for more data" — specific: what publication, what metric, what event?

---

## Output Structure

Every research output MUST end with a **claim ledger** (schema below). The
ledger is the load-bearing handoff to callers like /investigate-health,
which cite into the ledger by `quote-id`. A research output without a
claim ledger is incomplete.

### Claim ledger schema (required at the bottom of every output)

```
## Claim ledger

| quote-id | claim | tier | primary-source-verbatim-quote (≥30 words) | study-metadata (n, design, year, population) | falsifier | magnitude |
|---|---|---|---|---|---|---|
| C001 | <claim text> | T1-T5 | "<≥30 words verbatim from the source, NOT paraphrase>" | <n=?, RCT/cohort/etc, YYYY, population> | <one observation that would disprove> | <effect size where applicable, else "qualitative">
```

**Rule 1 (T1 verbatim — non-negotiable, imported from /research-practitioner):**
A T1 claim that paraphrases instead of quoting verbatim is **automatically
downgraded to T3**. The ≥30-word verbatim requirement is the gate that
prevents the "I summarised the source close enough" failure mode.

**quote-id** is unique within the file (C001, C002, ...). Callers cite by
`[ledger: C001]`. Grep-findability is required — the ID format must be
mechanically searchable.

**Two-pass extraction (Pass B — between Phase 3 Evaluation and Phase 4 Synthesis).**
After candidate evidence is identified in Phase 3, re-read each cited
primary source and extract verbatim quotes into the claim ledger. This is
the step that converts "I read it" into "the verbatim is in the ledger
where downstream callers can verify." Done in the same sub-agent for
single-output research; dispatched as a separate Pass-B agent for
multi-source research where total verbatim volume warrants it.

**Adversarial review (Pass C — added to Phase 5 after Step 18 Blind Spots).**
A separate sub-agent reads ONLY the claim ledger (not the prose synthesis)
and identifies the weakest claim — the one whose verbatim quote least
supports the claim text, or whose tier feels inflated. Pass-C output is
appended to the file as `## Pass-C adversarial review`. The ledger the
orchestrator works from is the **post-Pass-C version**.

### Prose synthesis structure (above the ledger)

Present the final analysis in this structure:

```
## Question
[Final framing from Step 1, with note on why this framing was chosen]

## Prior
[What was believed before research (Step 4), and basis]

## Key Findings
[Organized by sub-question (Step 5), with evidence level and causal level tags (Step 9)]
[Every locational / exclusionary / prevalence claim carries its claim-strength tag (a)/(b)/(c) (Step 9.5); only (a) may be used to exclude, and (a) carries its primary-source citation inline]
[For each finding: what the evidence says, how strong it is, what it doesn't tell us]

## Competing Hypotheses
[The 3+ hypotheses from Step 10, with comparative IBE evaluation]
[Discriminating evidence identified]

## Synthesis
[Integrated conclusion — what the evidence, across all lenses, taken together suggests]
[Numeric confidence for each major claim (Step 16)]

## What Could Make This Wrong
[Pre-mortem results (Step 14)]
[Steel-man counter (Step 15)]

## Uncertainty Map
[Known / Assumed / Unknown / Unknowable (Step 17)]
[Update triggers (Step 16)]

## Sources
[With evidence level tags (Step 7) and methodology notes for key sources]
```

### Data Translation Rules

When research is used in any content or output:

1. **Running text**: Plain language only. "Roughly 55 out of 100 people improved" not "effect size g = 0.56"
2. **Footnotes**: Raw statistics, author names, publication details
3. **Context**: Every number needs a comparison. "55 out of 100 improved — compared to 45 out of 100 with just a placebo" tells the reader what the number means
4. **Honest framing**: If the effect is small, say it's small. If the evidence is mixed, say it's mixed. Never oversell.

### Regulatory Awareness

When using research in any public-facing content:
- Keep "here's what the evidence shows about [topic]" clearly separate from "here's what I do / what this product does." Researching a clinical topic is not a claim that you or your product treat it.
- Never imply a service or product provides medical or psychological treatment unless it lawfully does. Stay in the lane your credentials and registration support.
- If a `reference/regulatory-guardrails.md` exists for your context, follow it.

---

## The `/research decompose` Sub-Protocol

For stress-testing a specific claim rather than researching a broad question:

1. **State the claim** clearly and completely
2. **Identify the causal chain**: What premises does this claim rest on? Map every link — each is a sub-claim. Missing even one link means the chain could break where you're not looking.
3. **Classify each sub-claim**:
   - *Empirical* — checkable against evidence → verify
   - *Logical* — follows from definitions → check the logic
   - *Judgment* — requires criteria and values → present strongest arguments for and against
   - *Predictive* — not currently verifiable → assess probability based on mechanism, not narrative
4. **Verify empirical sub-claims** against evidence using the source hierarchy from Step 7
5. **Stress-test logical sub-claims**: Do the conclusions actually follow from the premises? Are there hidden assumptions in the logical steps?
6. **For judgment and predictive sub-claims**: Present the strongest case for and against. Do not resolve ambiguity by picking a side — present the balance.
7. **Find the weakest link**: Which sub-claim has the least support? This is where the overall claim is most vulnerable.
8. **Reassemble**: Does the full claim hold when every link has been independently tested? Tag overall confidence (numeric). State what would break it.

---

## Psychology Research Sub-Protocols

These commands handle psychology-specific workflows: processing studies into the knowledge base, exploring topics through the evidence hierarchy, verifying claims, and connecting findings to existing notes. They use the full research engine (including the Clinical Study Checklist) but with domain-specific output formats.

### `/research topic <topic>`

Explore a psychology research topic and find relevant findings.

**Process**:
1. Search for key studies, meta-analyses, and reviews on the topic
2. Prioritize: meta-analyses > RCTs > longitudinal studies > cross-sectional
3. Apply the Clinical Study Checklist to every study before including it
4. Present findings organized by:
   - **What we know** (well-replicated, strong evidence)
   - **What we think** (suggestive but not definitive)
   - **What we don't know** (important gaps, conflicting evidence)
5. For each finding:
   - Plain-language summary (no jargon, no raw statistics in running text)
   - Strength of evidence (how many studies, how large, how well-designed)
   - Relevance to your goals / the focus areas you're working in
   - Raw data/citations in footnotes
6. Suggest zettelkasten notes that could be created from the findings

### `/research source <url-or-title>`

Process a specific research source into the knowledge base.

**Process**:
1. Read/fetch the source
2. Apply the Clinical Study Checklist (all 8 points)
3. If the source passes the checklist, create a literature note:
   - Use the literature note frontmatter schema from `zettelkasten/_conventions.md`
   - Summarize key findings in your own words (never copy)
   - Note methodology, sample size, limitations
   - Translate all statistics to plain language
   - Save to `zettelkasten/literature/`
4. Identify connections to existing permanent notes
5. Suggest new permanent notes if the source reveals genuinely new insights

### `/research verify <claim>`

Fact-check a specific claim against available evidence.

**Process**:
1. Search for the specific claim
2. Find the original source (not secondary citations)
3. Apply the Clinical Study Checklist to the source
4. Report:
   - **Verdict**: Supported / Partially supported / Not supported / Mixed evidence
   - **Best evidence**: What the strongest study says, in plain language
   - **Caveats**: Limitations, alternative interpretations, replication status
   - **For content**: How to state this claim accurately and honestly

### `/research connections <note>`

Find research that supports, challenges, or extends a zettelkasten note.

**Process**:
1. Read the permanent note
2. Search for research that:
   - Directly supports the claim
   - Directly challenges the claim
   - Extends it into new territory
3. For each finding, apply the Clinical Study Checklist
4. Present as: supporting evidence, challenging evidence, extensions
5. Suggest updates to the note if the research changes the picture

---

## Anti-Patterns This Skill Prevents

These are the specific failure modes that prompted the creation of this skill, drawn from actual research failures. If you catch yourself doing any of them, stop and apply the relevant gate.

**Authority-as-evidence**: "Woebot failed, therefore D2C mental health apps fail." Woebot failed for specific, decomposable reasons (CBT chatbot with no relational depth, launched pre-GPT, clinical framing, no community layer). Whether those reasons apply to a different product requires mechanism analysis, not analogy. → Apply Step 12 (Source-Independence) and decompose the failure to its root causes.

**Lazy historical analogy**: "The live music effect means human practitioners will thrive alongside AI." This maps a surface feature (human activity coexisting with technology) while ignoring structural differences in the value mechanism. → Apply Step 11 (Analogy Stress Test). If the analogy fails, reason from mechanism instead.

**Survivorship narrative**: "These companies survived disruption by doing X, so this company should do X." How many tried X and failed? Without the base rate and the failure cases, you're constructing a post-hoc narrative from winners only. → Apply Step 13 (Survivorship Check).

**Summary masquerading as analysis**: Restating what sources say without evaluating whether they're right, whether their evidence supports their conclusions, or whether their framing fits this specific question. → Design Principle 5: enforce the distinction between "what does it say?" and "is it right and does it apply?"

**Confident imprecision**: "Likely," "probably," "could," "may" used as weasel words that sound careful but communicate no information. → Step 16 requires numeric probabilities and specific update triggers.

**Narrative coherence over accuracy**: Resolving contradictions in favor of a clean story rather than flagging them. Contradictions in the evidence are *information* — they mean something in the model is wrong. → Step 10 (Hypothesis Competition) makes contradictions productive rather than suppressed.

**Correlation-as-causation**: "Countries with more coaching have higher GDP" presented as evidence that coaching drives economic growth. → Step 9 (Causal Level Tagging) forces every claim to identify its causal level and mechanism.

**Anchoring to first source**: The first retrieved result shapes the frame for all subsequent research. If the first result is wrong or misleading, the entire trajectory distorts. → Step 4 (Prior Statement) establishes a frame before any sources are consulted. Step 8 (Mandatory Disconfirmation) forces active search outside the initial frame.
