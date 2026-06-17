---
name: product-search
description: Deep-verified supplement and product recommendations that enforce ingredient-by-ingredient cross-checking against the user's documented constraints in MEMORY.md and medical-history.md. Prevents the common failure mode of recommending products based on brand reputation or search-result titles without actually reading the product page. Every recommendation requires fetching the real product page, extracting the full "Other Ingredients" list, checking each ingredient against the user's hard-no list, reading user reviews, and verifying brand reputation. Maintains persistent state (verified-products, brand-database, search-log) so repeat searches don't redo work. Use this skill WHENEVER the user says `/product-search`, asks "find me a source for X", "where do I buy X", "what's the best brand of X", "compare [product A] and [product B]", "which [product] should I get", "direct URLs for those products", or explicitly asks for a product recommendation, supplement source, or brand comparison. Do NOT use proactively — only when user explicitly requests product sourcing. Do NOT use for general mechanism or rationale questions.
user_invocable: true
---

# Product Search — Verified Supplement Sourcing

## Why this skill exists

This skill exists because of a specific, repeatable failure mode: recommending supplements based on **brand name as a proxy for clean formulation** or **Amazon search titles as if they were ingredient facts**. The typical failure looks like: "Nootropics Depot PEA is a clean brand" → recommend URL → user opens the actual product page → the supplement facts panel lists **rice** as an excipient → rice is on the user's hard-no list → recommendation was worthless.

The fix is not "try harder." The fix is **structural discipline**: every recommendation must survive a real fetch of the actual product page, a full extraction of every ingredient (active AND excipient), and a cross-check against the user's current documented constraints. No shortcuts. No assumptions from brand reputation. No guessing when a page fails to load.

This skill also builds **persistent institutional memory** — a brand database and a verified-products list — so that 3 months from now when the user asks about the same brand or SKU, the work already done is reused rather than redone.

## Core principle

Three words the skill operates under: **Fetch. Cross-check. Persist.**

- **Fetch**: every candidate product gets its actual page fetched and parsed — no shortcuts from search results.
- **Cross-check**: every ingredient is tagged against the user's current constraints, which are pulled fresh from their memory files at the time of invocation (constraints evolve — never hardcode).
- **Persist**: every verified product and brand assessment gets saved with a timestamp, so future searches benefit from the accumulated work.

## Invocation

Only on explicit user request. Triggers include:
- `/product-search`
- "find me a source for [X]"
- "where do I buy [X]"
- "what's the best brand of [X]"
- "compare [product A] and [product B]"
- "which [X] should I get"
- "direct URLs for those products"

Do NOT invoke proactively when the user mentions a supplement in passing or asks for mechanism/rationale without asking for a source.

## Procedure

The steps below are the complete workflow. Skipping steps — especially the biology research (Step 2.5), the page-fetch, and the ingredient cross-check — is the specific failure mode this skill exists to prevent. Follow them in order.

### Step 1 — Intake parsing

Before searching, extract from the user's request:
- What active ingredient or product category is being sourced?
- What is the target dose per day?
- Any supply length or budget hint?
- Are there pre-named candidates to compare, or is this an open search?
- Has the user flagged any constraint specifically this session that should take precedence?

If any of this is unclear, ask. A product search conducted with a fuzzy target produces fuzzy results that waste the user's attention.

### Step 2 — Load user constraints (fresh, every time)

Read these two files at time of invocation — do not cache or assume anything from prior sessions:
- `memory/MEMORY.md`
- `memory/medical-history.md`

Build two lists from what's in those files:
- **Hard-no** (anything in the contraindicated / "never" / "stopped" / "caused issues" lists — these auto-disqualify any product containing them)
- **Caution** (anything flagged "watch for" / "unclear" / genotype-concern — surfaced but not auto-disqualifying)

**These lists are user-contributed and grow over time — they are not hardcoded, and they are never assumed.** Three rules govern them:

1. **Build fresh, every time.** Always extract the *current* list from the user's memory at invocation. A constraint removed since last time must not be enforced; one added since must be. Never carry a constraint from a prior session or from another person — only from *this* user's memory.
2. **If the memory has no documented constraints yet, ASK — don't proceed blind.** On a first run, or when the files are sparse, ask the user directly: any known allergies or intolerances; ingredients or forms that have caused problems before; anything a clinician told them to avoid; dietary pattern (vegan, etc.); and relevant genetics or labs. A product search run against an empty constraint list gives false confidence, which is exactly the failure this skill exists to prevent.
3. **Write new constraints back (this is maintenance, and it's required).** Whenever this search — or anything the user says during it — surfaces a new constraint or reaction, record it to `memory/medical-history.md` and add a one-line pointer in `memory/MEMORY.md`, so the next run inherits it. The constraint list is meant to get *more* accurate over time; that only happens if discoveries are persisted. The brand-database and verified-products caches (Steps 3–4, 12) are living files too — re-verify entries older than ~3 months, because formulations change.

The *kinds* of things that commonly end up on a hard-no/caution list (illustrative only — the real list is whatever is in this user's memory, never this generic list):
- Allergens and intolerances (e.g. dairy protein — trace casein/whey from shared facilities can matter; gluten; soy; specific nuts)
- Excipients and fillers a user reacts to (specific grain-derived fillers, certain flow agents)
- Delivery vehicles that matter for the user's situation (e.g. liposomal / phospholipid forms in some gut conditions — see `references/high-value-levers.md`)
- Forms or doses contraindicated by the user's genetics or labs (e.g. iron with high ferritin)
- Anything the user's records or clinician flagged, and anything the investigation has surfaced as a reaction

Do not treat the illustrative list as the user's constraints — extract those from their memory, and ask when they aren't documented.

### Step 2.5 — Ground the search in the user's biology (reuse the investigation first; `/research` only the gaps)

> *This is an early step **within a product-search run** — not an early step in the overall OpenBioHack
> journey. Sourcing a specific product is a **late** activity: it normally happens after the investigation
> has surfaced an option worth pursuing. So by the time you reach here, most of the biology work usually
> already exists — the job of this step is to **reuse** it, not redo it.*

Before searching for brands, make sure the search is grounded in *this person's* biology — the static
constraint list (Step 2) tells you what to *avoid*, but not what form/dose/vehicle is *right for them*.

1. **Start from what's already established — don't re-research it.** Read the existing biology context first:
   the user's `memory/` (genetics, medical-history, self-reminders), the investigation's offering /
   decision-log if one exists, and any prior `/research` output in the `research/` directory. After a real
   investigation this usually already says which form/dose/vehicle suits this person — use it.
2. **Run `/research` only to fill sourcing-specific gaps** the investigation didn't settle — and that's
   often just one or two focused calls, sometimes none. Typical gaps: which delivery vehicle or salt form
   fits their biology *for this specific compound* (e.g. a methylated form for a methylation variant; a
   non-liposomal vehicle for a gut condition — see `references/high-value-levers.md`); an interaction with
   their current stack; a contraindication not yet captured. If research surfaces a new contraindication,
   it becomes a hard-no/caution for this search **and** gets written back to memory per the Step-2
   maintenance rule.
3. **Cold-start fallback.** If product-search was invoked standalone with little prior context (someone just
   asks "where do I buy X" with no investigation behind it), there's no existing biology to reuse — so do the
   fuller version here: ASK for the key biology (per Step 2) and run `/research` to establish form / vehicle /
   contraindication before searching. This is the one case where the research is heavier up front.

Carry whatever you reused or found into the ingredient cross-check (Step 6) and the final write-up, so the
user sees *why* a form was chosen for their biology, not just that a SKU is "clean."

### Step 3 — Check verified-products.md

Read `memory/verified-products.md`.

For each potential candidate:
- If the SKU is listed AND the verification date is less than 3 months old AND the user's constraints have not changed in a way that would affect the verdict → cite the cached verification and skip to output.
- If the SKU is listed but the date is older than 3 months → formulations change; re-verify.
- If the SKU is not listed → proceed to fresh verification.

This caching is what keeps the skill efficient. But it only works if Step 12 (persistence) is done faithfully every time.

### Step 4 — Check brand-database.md

Read `memory/brand-database.md`.

For each brand represented in the candidates:
- If the brand is rated AND less than 3 months old → use the cached reputation
- Otherwise → mark the brand for re-assessment during this search (Step 9)

### Step 5 — Candidate search (aim for 8-12 candidates, be BROAD)

**Do NOT pre-filter brands based on assumption of what they contain.** This is the single most important rule in this step. "Jarrow probably has rice" or "Now Foods is mass-market so it's probably dirty" is not a valid filter — the whole point of the skill is to CHECK the actual ingredients, not assume. Brand reputation tells you about manufacturing QC and transparency; it does NOT tell you what's in a specific SKU. Include every plausible candidate and let Step 6 verification do the work.

**Mandatory breadth across all searches**:

- **Amazon US high-volume brands (ALWAYS include)** — Jarrow Formulas, NOW Foods, Doctor's Best, Swanson, BulkSupplements, NutraBio, Life Extension, Source Naturals, Pure Encapsulations, Thorne, Nutricost, Solgar, Nature's Way. These are the brands where Amazon reviews actually exist in meaningful volume. Their ingredient quality varies — check each SKU specifically.
- **Practitioner / professional brands** — Designs for Health, Ortho Molecular, Vital Nutrients, Seeking Health, Metagenics, Biotics Research, Integrative Therapeutics, Bioclinic Naturals. Often cleaner ingredients but thin consumer reviews.
- **DTC longevity / nootropic brands** — Nootropics Depot, Double Wood, Toniiq, Codeage, DoNotAge, Oxford Healthspan. Variable quality; always check the actual label.
- **iHerb listings** — often stocks practitioner brands not available on Amazon
- **Compounding pharmacies** — relevant for pure synthetic forms and Rx-only actives (gallium maltolate, pharmaceutical-grade spermidine, etc.)

**Process**: search for the active ingredient across all candidate pools. Aim for 8-12 candidates that span the price/reputation/volume spectrum. Every candidate from every pool proceeds to Step 6 verification — no pre-filtering allowed.

### Step 5a — Tool selection for web access

Use the right tool for the site. Wrong tool choice is the single biggest reason Step 6 fails with "UNVERIFIED."

| Site type | Use | Why |
|---|---|---|
| **Amazon (ALL pages)** | Playwright browser tools (`mcp__plugin_playwright_playwright__browser_navigate` + `browser_snapshot`) | Amazon blocks WebFetch/lightweight HTTP clients with 503/403 via anti-bot detection. Playwright uses a real Chromium browser Amazon can't easily distinguish from a human. This is the only reliable way to read Amazon product pages. |
| **Brand-direct sites** (Pure Encaps, Jarrow, Thorne, DFH) | WebFetch first, Playwright if JS-heavy | Most work with WebFetch. Fall back to Playwright if content is client-rendered. |
| **iHerb** | WebFetch usually works | Simple HTML for most product pages |
| **Compounding pharmacies** | WebFetch; often need to contact directly | Most just have product catalogs; actual ordering requires Rx |
| **Google / product discovery** | WebSearch | Finding candidate products by name |

**Never report a candidate as UNVERIFIED because of Amazon 503 before trying Playwright.** If WebFetch 503s on Amazon, escalate to Playwright IMMEDIATELY — don't wait, don't mark UNVERIFIED based on WebFetch failure alone.

**Playwright usage pattern for Amazon**:
1. `browser_navigate` to the Amazon product URL
2. `browser_snapshot` to capture the rendered page
3. Extract from the snapshot: supplement facts, other ingredients, star rating, review count
4. If specific sections (like "Product Details" dropdown) need expansion, use `browser_click` to open them, then `browser_snapshot` again
5. Close the browser session with `browser_close` when done with all products

For multiple products, navigate between them in the same session rather than opening new ones — faster and less likely to trip rate limiting.

### Step 6 — Deep-verify every candidate

For every candidate before it enters the comparison table, fetch the actual product page and extract all of:

1. **Active ingredient exact form** — "spermidine trihydrochloride" (synthetic) vs "wheat germ extract standardized to spermidine" (plant-matrix) are entirely different products, even though both say "spermidine" on the label
2. **Dose per capsule + serving size** — and therefore capsules per day at the user's target dose
3. **Full "Other Ingredients" list** — excipients, fillers, flow agents, capsule material. This is where rice, lactose, dairy, phospholipids hide
4. **Capsule material** — HPMC veggie, pullulan, gelatin, etc.
5. **Allergen warnings + shared-facility statements** — "manufactured in a facility that processes milk/wheat/soy/nuts" is a real consideration for protein-sensitive users
6. **Third-party testing specific to this SKU** — a brand claiming "we third-party test" is weaker than "this batch was tested by [named lab], COA available at [link]"
7. **Manufacturing location** — indicates GMP jurisdiction
8. **User reviews** — read the actual recent reviews; report star rating, rough positive/negative ratio, and a sentiment summary. Do not pre-form an opinion about the product; just read what people say and report it faithfully. Reviews often catch batch/formulation changes that the product page doesn't mention.
9. **Batch/formulation change flags** — multiple recent reviews saying "they changed the formula" or "got a different smell this batch" is a signal to flag

If the product page cannot be fetched:
- **If it's Amazon and WebFetch 503'd** → escalate to Playwright browser tools (per Step 5a). This usually resolves Amazon fetch failures. Do NOT mark Amazon pages as UNVERIFIED without trying Playwright first.
- **If it's a brand-direct site** and WebFetch fails → try Playwright (some brand sites are JS-heavy)
- **If a specific product page still fails after Playwright** → try the brand-direct site or iHerb listing for the same SKU
- **If all three fail** → report the candidate as **UNVERIFIED** — do not guess at ingredients from the brand's other products. "UNVERIFIED — do not recommend" is the honest answer.

### Step 7 — Resolve unknown ingredients

When an ingredient is unfamiliar or its compatibility with the user's specific situation is ambiguous, dispatch a sub-agent (via the Task tool) to research that specific ingredient — what it is, what it's typically sourced from, and whether it's relevant to any of the user's constraints.

Report the finding but tag the ingredient as **❓ UNKNOWN** rather than auto-disqualifying. Only the user's explicit hard-no list disqualifies; ambiguous-but-possibly-fine ingredients get flagged for user review.

Opaque ingredient terms like "natural flavor" or "proprietary blend" should be flagged transparently — there is nothing the skill can do to resolve them without manufacturer contact, but the user deserves to know the ingredient list is not fully disclosed.

### Step 8 — Cross-check every ingredient against user constraints

For each product, tag every ingredient in the supplement facts and "Other Ingredients" sections:

- **✅ ALIGN** — safe or desired
- **❌ VIOLATE** — appears on the user's hard-no list. This auto-disqualifies the product. Report which specific ingredient triggered which specific constraint.
- **⚠️ CAUTION** — on the user's caution list. Surface for user decision.
- **❓ UNKNOWN** — not verifiable, ambiguous, or flagged by Step 7.

A product with even one ❌ VIOLATE is disqualified. No exceptions. A product with multiple ⚠️ CAUTION tags may still be viable but should be clearly surfaced.

### Step 9 — Brand reputation check (if not in database or stale)

For any brand not already rated in `brand-database.md` or rated more than 3 months ago:

1. **Third-party testing transparency** — three levels:
   - **Named** — the brand specifies which lab tests their products (e.g., Eurofins, NSF). Highest trust signal.
   - **Claim-only** — the brand says "third-party tested" without naming the party. Weaker signal; could be anything.
   - **None** — no third-party testing mentioned. No signal.

2. **General reputation** — search for reviews, critiques, Consumer Lab reports, Labdoor ratings, Reddit discussions about the brand. Summarize what people actually say, not a pre-formed view.

3. **Save to `brand-database.md`** — with today's date, using the template in "Brand database format" below. Future searches benefit from this.

### Step 10 — Cost calculation

For each viable candidate, calculate exact cost per month at the user's target dose:
- Capsules per day (target daily dose / dose per capsule)
- × cost per capsule (price / capsules per bottle)
- × 30 days

This gives an honest $/month number, not a "per bottle" number that hides the real cost at therapeutic doses.

### Step 11 — Present results

**CRITICAL PRESENTATION RULES** (violating these defeats the purpose of the skill):

1. **Always present 2-3 viable options at DIFFERENT price points** when 2-3 exist — do not collapse to a single "top pick" and demote the others to "also viable." The user wants to pick from a spread, not be given a decision.

2. **Do NOT make the final decision for the user.** No "Recommended next moves: Order X." No "Best fit." No "Top pick." Present the options with full pros/cons and let the user choose. The skill's job is to produce a clean comparison, not a verdict.

3. **Each option must include all of**:
   - Direct clickable URL (brand site + Amazon if available — give both)
   - ASIN / SKU
   - Exact cost per month calculated at user's target dose (not just "price of bottle")
   - Dose per cap + how many caps/day at target
   - Full "Other Ingredients" list — every item
   - Capsule material
   - Third-party testing transparency (Named/Claim-only/None)
   - **Pros** (3-5 bullet points — why you'd pick this over the others)
   - **Cons** (3-5 bullet points — why you might NOT pick this)

4. **Order options by ASCENDING cost** (cheapest first) so the price spread is visible at a glance. If only two viable options exist, present both. If only one viable option exists, say so honestly — don't invent alternatives to hit a count.

5. **Include a compounding-pharmacy option as Option C** when relevant (pure synthetic / Rx-required forms) — this gives the user a "gold standard" price point even if it requires a physician. Don't require it when the product category doesn't warrant it (e.g., a common multivitamin).

6. **Always produce a label-check list per option** — because ingredient lists change batch-to-batch. The user needs to be able to verify each specific product on arrival.

Use this exact template:

```
## /product-search: [active ingredient], target [daily dose]

### Constraints loaded (from MEMORY.md + medical-history.md, as of [YYYY-MM-DD])
- Hard-no: [bulleted list extracted from current memory]
- Caution: [bulleted list]

### Brand database check
- [Brand A: rated YYYY-MM-DD — Green/Yellow/Red, 1-line summary]
- [Brand B: not previously in database — checked this run, saved]

---

## Options — ordered by monthly cost (cheapest first)

### Option A — [Product name] — **~$X/mo**

**Direct URL**: [brand-direct]
**Amazon**: [amazon URL if available, or "not on Amazon"]
**ASIN/SKU**: [identifier]

- **Cost/mo at target dose**: $X ([Y caps/day] × $[Z]/cap × 30)
- **Dose/cap**: [mg or IU]
- **Other ingredients (full)**: [every item — not "clean" in vague summary, the actual list]
- **Capsule**: [HPMC / pullulan / gelatin]
- **3rd-party**: Named ([lab]) / Claim-only / None
- **Reviews**: [star rating + sentiment in 1 sentence]

**Pros**:
- [specific bullet 1]
- [specific bullet 2]
- [specific bullet 3]

**Cons**:
- [specific bullet 1]
- [specific bullet 2]
- [specific bullet 3]

**Label-check on arrival**:
- Should say: [active form wording]
- Should NOT contain: [user's hard-no ingredients spelled out]
- If supplement facts show [specific concerning ingredient], formula has changed — return the bottle

### Option B — [Product name] — **~$X/mo**

[same structure as Option A]

### Option C — [Product name or compounding pharmacy route] — **~$X/mo**

[same structure as Option A — include compounding pharmacy when relevant as a "gold standard purity" price point]

---

### Disqualified
[For each: product name | SPECIFIC ingredient that triggered | SPECIFIC user constraint violated]

### Unverified (product page failed to fetch)
[List any, explicitly — do not guess at these]

### Brand database updates saved
[Any new or updated brand assessments saved this run]
```

**Do NOT add a final "recommended next moves" or "top pick" section after the options.** The options section IS the deliverable. Stop there. The user decides.

Always include the date of the check in the output. The user needs to be able to answer "how fresh is this recommendation" at a glance.

### Step 12 — Update persistent files

Every product search produces state updates. Do not skip this — the caching in Steps 3 and 4 only works if this step is done faithfully.

Append or update these files with today's date:

1. **`memory/verified-products.md`** — new entries for every product that was fully verified this run (including disqualified ones — the disqualification is useful data for next time)

2. **`memory/brand-database.md`** — new or updated brand rep assessments

3. **`memory/product-search-log.md`** — a terse audit-trail entry: what was searched, what was found, what was recommended, date

If any of these files don't exist yet, create them using the templates below.

## File templates

### verified-products.md entry
```
## [Product name] — [Brand] — [ASIN/SKU]
- Last verified: YYYY-MM-DD
- Active form: [exact wording from label]
- Dose/cap: [mg or IU]
- Other ingredients (full list): [every item from the "Other Ingredients" section]
- Capsule material: [HPMC / pullulan / gelatin / other]
- Third-party: Named ([lab]) / Claim-only / None
- Constraints checked against: MEMORY.md + medical-history.md as of YYYY-MM-DD
- Verdict: SAFE / CAUTION / VIOLATE
- Review summary: [stars, positive/negative ratio, sentiment in 1-2 sentences]
- Monthly cost at [user's target dose]: $X
- Direct URL: [link]
- Notes: [batch flags, formulation concerns, anything unusual]
```

### brand-database.md entry
```
## [Brand name]
- Last checked: YYYY-MM-DD
- Third-party testing: Named ([lab]) / Claim-only / None
- Reputation summary: [2-3 sentences reflecting what people actually say]
- Known clean SKUs: [list, if any checked]
- Known dirty SKUs: [list — products that disqualified]
- Flag: Green / Yellow / Red
```

### product-search-log.md entry
```
## YYYY-MM-DD — [Active ingredient search]
- Target dose: [daily dose sought]
- Candidates evaluated: [count]
- Top pick: [product name]
- Disqualified count: [N]
- Unverified count: [N]
```

## Anti-patterns this skill exists to prevent

The failure mode for product recommendation is specific and repeatable. These are the errors the skill must prevent, in roughly order of how often they happen:

1. **Brand-name-as-proxy** — "Pure Encapsulations is a clean brand" doesn't tell you anything about this specific SKU. Always check the specific SKU.

1b. **Pre-filtering brands based on assumed ingredients** — "Jarrow probably has rice" or "Now Foods is mass-market so it's probably dirty" is the SAME failure mode as #1, just inverted. It causes the skill to exclude candidates that might actually be clean while over-including candidates that seem clean by reputation but aren't. Include every plausible candidate in Step 5 and let Step 6 verification do the filtering. Brand reputation affects Step 9 (brand trust / third-party testing transparency), NOT the candidate pool in Step 5.

2. **Search-title-as-fact** — The Amazon search title says "gluten-free" but the "Other Ingredients" section says rice. The title lies or omits. The supplement facts panel does not. Always fetch the page.

3. **Skipping "Other Ingredients"** — The active ingredient list is the minority of what's in the capsule. The excipients are where dairy, rice, phospholipids, shared-facility cross-contamination live. This is not optional.

4. **Not pulling user constraints fresh** — A constraint list from three sessions ago may not reflect what's currently in MEMORY.md. The user's understanding of their own biology is still evolving. Re-read the files every time.

5. **Recommending when the page failed to fetch** — If WebFetch 503s and you don't know what's in the bottle, the answer is "UNVERIFIED," not a guess based on other products from the same brand. BUT before marking Amazon pages UNVERIFIED, you MUST try Playwright browser tools (see Step 5a) — WebFetch 503s are a tool-choice problem on Amazon, not a real "page inaccessible" problem.

6. **Liposomal products without the lipid-vehicle flag** — For users with gram-negative gut overgrowth concerns, phospholipid shells can feed the overgrowth (see `references/high-value-levers.md`). Always flag liposomal vehicles, even when the active ingredient is unobjectionable.

7. **Ignoring shared-facility allergen statements** — "Manufactured in a facility that processes milk" is a real signal for protein-sensitive users. Don't gloss over it.

8. **Accepting "third-party tested" at face value** — If the third party isn't named, the claim means little. A COA linked on the product page is different from a vague claim in marketing copy.

9. **Not checking the user's current multi** — If the user's existing multivitamin already provides adequate B3 (or magnesium, or zinc, or any other target), recommending a separate supplement is redundant and wastes the user's attention and money. Always cross-check the target nutrient against what the user is already getting.

10. **No label-check list** — Ingredient lists change batch-to-batch. Even a verified product can arrive with a different formula. A short checklist the user can scan on arrival ("should say X, should NOT contain Y") catches reformulations before they cause a problem.

## Scope

This skill is for supplements and wellness products. If the user asks about food products, books, equipment, or other non-supplement items, the skill can be adapted but the anti-patterns above may not all apply — use judgment.

This skill defaults to US sourcing. Ask the user for their region/country so availability, brands, and pricing match where they actually are.

This skill is explicit-trigger-only. Do not invoke proactively when the user mentions supplements in general conversation. Do not invoke when the user asks for mechanism or rationale without asking for a source.

## Key priorities, restated

- **Cite the date** of every check in the output — freshness matters
- **Include specific SKU/ASIN** so the user can independently verify
- **Always produce a label-check list** — the label changes without notice
- **Say UNVERIFIED** rather than guess — a clear "I don't know" is more useful than a fabricated answer
- **Update persistent state** — future searches get faster and better only if state is maintained
- **Re-pull user constraints** at time of invocation — never cache or hardcode, user's situation evolves
