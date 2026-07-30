export const meta = {
  name: 'investigate-health-orchestrator',
  description: 'Deterministic driver for /investigate-health. Walks a fixed chain of five movements — Prepare → Hypothesise → Investigate → Model → Share — each a named step (no step numbers). Hypothesise widens to every candidate root cause then proves down to survivors; Investigate deep-researches them and asks the person; Model builds the mechanism maps, ranks, sweep-checks nothing is unexplained, and researches how to act at each node; Share composes the person-facing write-up, audits it, and hands it over. The deepening loop runs over EVERY leading hypothesis; the write-up is an Opening + §1/§2/§3 fan-out; each dispatch is pointed at its canonical references/<X>.md, never inlined. The driver (code) owns the global sequence so a step cannot be skipped or reordered; the write/bash hooks own local write integrity (fail-closed). The model is only in the loop for the non-deterministic pieces (the interview, the write-up voice, subject-facing turns).',
  whenToUse: 'The /investigate-health entry point IS this workflow. Bootstrap emits a signed run-manifest; the final write-up is denied unless a valid manifest exists — there is no model-driven escape hatch.',
  phases: [
    { title: 'Bootstrap', detail: 'signed .investigate-active + run-manifest, register root, instantiate state stubs (dispatched bash)' },
    { title: 'Prepare · Onboard',   detail: 'goals.md + data-completeness.md (gate: blocks the first analytical write)' },
    { title: 'Prepare · Extract',   detail: '/extract-health-data → extracted/ + extracted/timeline.md (the ONE verbatim document) + spot-check.md' },
    { title: 'Hypothesise · Generate',  detail: 'per-document (lens-rotated) + cross-document broad generation, explicit COMPOUND → hypotheses/*' },
    { title: 'Hypothesise · Integrate', detail: 'family-sharded integration (no-flatten, reasonings verbatim) → hypothesis-set.md' },
    { title: 'Hypothesise · Disconfirm', detail: 'family-batched disconfirmation (provisional parking) + separate adversarial reframe → disconfirm/*.md standings' },
    { title: 'Hypothesise · Select',    detail: 'partition in-play (→ deep research) vs parked-provisional (→ the Sweep reopen pool) → selection.md' },
    { title: 'Investigate · Research',  detail: 'per survivor: /research + /research-practitioner + the differentiating diagnostic questions the interview harvests' },
    { title: 'Investigate · Interview', detail: 'question-bank.md → the person answers (the one interactive pause) → resume [skill-retained]' },
    { title: 'Model · Cohere', detail: 'coherence-map.md (deepen → coherence → verdict on the post-interview ledger)' },
    { title: 'Model · Deepen',    detail: 'over every leading hypothesis: constraints → shape → mechanism-maps → system-integration → plausibility → convergence' },
    { title: 'Model · Prioritize', detail: 'step6-prioritize.md + responses-mechanism-<Hn>.md' },
    { title: 'Model · Sweep',     detail: 'sweep-check.md — every datum vs the deepening maps; reopen (on-demand deepening) + still_unexplained[]' },
    { title: 'Model · Intervene', detail: 'interventions-<candidate>.md — typed levers per deepening-map node (feeds the §2/§3 router)' },
    { title: 'Share · Compose',     detail: 'own-words glossary + §2/§3 router → Opening + §1(per candidate) + §2(per lever) + §3(per test) → concat → offering-draft.md' },
    { title: 'Share · Audit',   detail: '7 finish-line auditors → readproof → findings → disk-proofed via census.councilState' },
    { title: 'Share · Finalise',     detail: 'faithful strip offering-draft.md → offering.md (+ working-hypothesis.md)' },
    { title: 'Share · Open Threads', detail: 'open-threads-and-invitation.md — the frontier + invitation to go deeper; surface to the person' },
  ],
}

// GO-LIVE 2026-07-16: this IS the canonical, live investigate-health driver (consolidated onto the
// five-movement engine + the Step-1 flip + the A7/B1/atom-diff fixes; deployed to ~/.claude/workflows
// via symlink into this repo). The former ihEnabled DEPLOY GUARD was removed at go-live — the trusted
// scripts (investigate-bootstrap/census/resume-write.sh, council-*.sh), the convert-source pipeline,
// and the references/ dir are all installed and present, so /investigate-health runs directly.

// =============================================================================
// The driver is SANDBOXED: no filesystem, no bash, no network. It only builds
// strings and calls agent()/parallel()/pipeline()/phase()/log(). Every action
// that touches disk or verifies a token/marker is done by a DISPATCHED agent
// running a trusted script in Bash — because the JS cannot stat disk, all
// disk-truth and verification lives in the hooks + trusted scripts. Schemas
// gate transitions, but the AUTHORITATIVE gate is always the write/bash hook on
// the next write: a lying schema value cannot unlock a downstream gated write.
// =============================================================================

// ───────────────────────── config ─────────────────────────
// Trusted scripts (council-*.sh, audit-council-completion.sh, the manifest emitter,
// the trusted census) live in the protected hooks/ dir; the canonical prompt refs
// live in the skill's references/ dir. Both are overridable via args for the
// hermetic test lane (an un-installed scratchpad build).
let HOOKS = '"$HOME/.claude/hooks"'
let REFS  = '"$HOME/.claude/skills/investigate-health/references"'
const hookScript = (name) => HOOKS.replace(/"$/, '') + '/' + name + '"'
// refPath is a DISPLAY path handed to the agent (it Reads the file itself); keep it literal.
const refPath = (rel) => REFS.replace(/^"|"$/g, '') + '/' + rel

// ───────────────────────── the procedure as data ─────────────────────────
// Gated-basename set — SINGLE SOURCE consumed by the write-check case list, the
// Bash-gate, and the gate JSONs (a drift test enforces consistency across all
// four sites). A gated write's authority is the hook, never the schema value.
const GATED_BASENAMES = [
  // synthesis family
  'step2-mechanism-map.md', 'working-hypothesis.md', 'step5-cross-check.md',
  'hypothesis-set.md', 'step6-prioritize.md',
  // phase-B family (globs — matched by prefix in the hooks)
  'constraints-', 'shape-profile-', 'mechanism-map-', 'convergence-',
  'system-integration.md', 'connection-plausibility.md', 'coherence-map.md',
  // offer family
  'offering-draft.md', 'offering.md',
]

// STEPS — the fixed LINEAR spine. Fan-outs (Step 3 per-process, Step 5 research
// per-Hn, Phase-B per-Hn/per-candidate, offer per-section, council per-auditor)
// are driven by the dedicated loops below, referencing the tables that follow.
// Each row: { id, phase, ref, inputs, output, schema, gated }. `ref` is the
// canonical prompt file the dispatched agent Reads in full and follows verbatim.
const STEPS = [
  { id: '0',   phase: 'Prepare · Onboard',   ref: 'steps/step0.md',
    inputs: ['data/ raw sources', 'memory/MEMORY.md', 'hard_no_*'],
    // presentation.md is DECLARED here, which is what gives it a producer AND a halt in one element:
    // runStep's census gate refuses to advance when a declared output is absent, so a missing
    // explanandum stops the run instead of handing the 2a/2b generators a dead path (:1116, :1144).
    output: ['goals.md', 'data-completeness.md', 'presentation.md'], schema: 'WROTE', gated: false },
  { id: '1',   phase: 'Prepare · Extract',   ref: null,   // delegates to the /extract-health-data skill/workflow
    inputs: ['data/ raw sources'],
    output: ['extracted/', 'extracted/timeline.md', 'extracted/spot-check.md'], schema: 'WROTE', gated: true },
  { id: '2',   phase: 'Mechanism', ref: 'steps/step2.md',
    inputs: ['extracted/*', 'extracted/timeline.md'],
    output: ['step2-mechanism-map.md', 'research/anomaly-<slug>-*.md'], schema: 'WROTE', gated: true },
  // Step 3 is a fan-out (one blind builder per process) — see runBuilders().
  { id: '4',   phase: 'Inventory', ref: 'steps/step4.md',
    inputs: ['graphs/builder-*.md'],
    output: ['shared-node-inventory.md'], schema: 'WROTE', gated: false },
  { id: '4.5', phase: 'Hypothesize', ref: 'hypothesis-step.md',
    inputs: ['shared-node-inventory.md', 'graphs/*', 'extracted/timeline.md'],
    output: ['hypothesis-set.md'], schema: 'HYPSET', gated: true },
  // (legacy step '5' CrossCheck removed — it was never dispatched, and step5-cross-check.md is retired.)
  { id: '5.5', phase: 'Investigate · Interview', ref: 'steps/step5.5.md',
    // The Phase-0 harvest reads the per-hypothesis research dossiers (their `## Differentiating diagnostic
    // questions` sections ARE the question pool) + selection.md (which hypotheses are live) + the compiled
    // data (to subtract questions the records already answer). step5-cross-check.md was retired.
    inputs: ['selection.md', 'research/*', 'extracted/*'],
    output: ['question-bank.md'], schema: 'WROTE', gated: false, skillRetained: true },
  { id: '5.7', phase: 'Model · Cohere', ref: 'coherence-map.md',
    // step5-cross-check.md retired → read the disconfirm standings + selection.md instead.
    inputs: ['hypothesis-set.md', 'selection.md', 'disconfirm/*', 'question-bank.md', 'interview-answers.md', 'extracted/*'],
    output: ['coherence-map.md'], schema: 'WROTE', gated: true },
  // Steps 5.8–5.14 are the Phase-B loop — see runPhaseB().
  { id: '6',   phase: 'Model · Prioritize', ref: 'prioritizer.md',
    // working-truth.md retired — prioritise reads the primary artifacts directly (the interview answers and
    // the disconfirm standings), never a summary ledger that invites reading the summary over the sources.
    inputs: ['convergence-<Hn>.md', 'mechanism-map-*.md', 'interview-answers.md', 'disconfirm/*', 'sweep-check.md'],
    output: ['step6-prioritize.md'], schema: 'WROTE', gated: true },
  // Step 7 (offer + council + strip) — see runOffer().
  { id: '7.5', phase: 'Share · Open Threads', ref: 'steps/step7.5.md',
    inputs: ['offering.md', 'full doc set'],
    output: ['open-threads-and-invitation.md'], schema: 'WROTE', gated: false },
]

// PHASE_B_SUBSTEPS (5.8 → 5.14). Fan-out is per-hypothesis EXCEPT B3 (per-candidate)
// and system-integration / connection-plausibility (single cross-hypothesis files).
const PHASE_B_SUBSTEPS = [
  { id: '5.8',  code: 'B1',   name: 'constraints',           ref: 'steps/step5.8.md',
    outPattern: 'constraints-<Hn>.md',            fan: 'per-hypothesis' },
  { id: '5.9',  code: 'B2',   name: 'shape-profile',         ref: 'steps/step5.9.md',
    outPattern: 'shape-profile-<Hn>.md',          fan: 'per-hypothesis', needs: 'constraints-<Hn>.md' },
  { id: '5.10', code: 'B3',   name: 'mechanism-map',         ref: 'steps/step5.10.md',
    outPattern: 'mechanism-map-<candidate>.md',   fan: 'per-candidate',  needs: 'shape-profile-<Hn>.md' },
  // B4 (5.11): resolve cheap discriminators — no own file; askable-now → 5.5 second interview,
  // in-records → re-read source. Enforced at the convergence-write gate. (folded)
  { id: '5.12', code: 'B5.5', name: 'system-integration',    ref: 'steps/step5.12.md',
    outPattern: 'system-integration.md',          fan: 'single' },
  { id: '5.13', code: 'B5.6', name: 'connection-plausibility', ref: 'steps/step5.13.md',
    outPattern: 'connection-plausibility.md',     fan: 'single', needs: 'system-integration.md' },
  { id: '5.14', code: 'B5',   name: 'convergence',           ref: 'steps/step5.14.md',
    outPattern: 'convergence-<Hn>.md',            fan: 'per-hypothesis',
    needs: 'mechanism-map-*.md + system-integration.md + connection-plausibility.md' },
]

// OFFER_SECTIONS — the restructured offer: Opening + §1/§2/§3 (the two old triplicate clusters collapsed).
// §1 fans per candidate, §2 per routed lever, §3 per routed test — each written to its own
// offer-sections/<...>.md file, then deterministically concatenated into offering-draft.md. Node names come
// from the deepening mechanism-maps (no registry); the coordination layer is the §2/§3 router + coverage
// reconciler + plain-language auditor + faithfulness pass + own-words glossary. Old s1..s7 refs are kept
// in-tree (unreferenced) until the offer is verified on real data.
const OFFER_SECTIONS = [
  { id: 'opening', ref: 'offer-examples/opening.md', title: 'The shape of it (opening synthesis + across-candidate interaction)' },
  { id: 'sec1',    ref: 'offer-examples/sec1.md',    title: 'What may be going on (per candidate; taught once)' },
  { id: 'sec2',    ref: 'offer-examples/sec2.md',    title: 'What you could do about it (act-and-learn levers)' },
  { id: 'sec3',    ref: 'offer-examples/sec3.md',    title: 'Tests to run first (before, or instead of, acting)' },
]
const offerRef = (id) => (OFFER_SECTIONS.find(s => s.id === id) || {}).ref

// AUDITORS — the 7 finish-line council auditors, keyed by GATE (5 gates; Group A's 3 auditors share the
// `offering` gate, Group B mint one each). The driver dispatched them, so it reads their verdicts directly
// and finish-line-verifies their disk proof-of-work via census.councilState (Fix 2) — there is no HMAC
// finish-line token in the JS path (the old cryptographic-token gate was dropped when the driver was
// dehooked; the live SKILL flow still uses tokens, which this driver deliberately does not touch).
const AUDITORS = [
  { role: 'reconcile',     ref: 'council/dispatch-template-reconcile.md',     group: 'A', gate: 'offering',      minSpans: 3 },
  { role: 'veracity',      ref: 'council/dispatch-template-veracity.md',      group: 'A', gate: 'offering',      minSpans: 3 },
  { role: 'coherence',     ref: 'council/dispatch-template-coherence.md',     group: 'A', gate: 'offering',      minSpans: 3 },
  { role: 'decomposition', ref: 'council/dispatch-template-decomposition.md', group: 'B', gate: 'decomposition', minSpans: 3 },
  { role: 'structure',     ref: 'council/dispatch-template-structure.md',     group: 'B', gate: 'structure',     minSpans: 5 },
  { role: 'register',      ref: 'council/dispatch-template-register.md',      group: 'B', gate: 'register',      minSpans: 3 },
  { role: 'substance',     ref: 'council/dispatch-template-substance.md',     group: 'B', gate: 'substance',     minSpans: 5 },
]

// ───────────────────────── reused prompt rules (mirror extract-health-data) ─────────────────────────
const NO_SIDEWORK_RULE =
  'UNATTENDED RUN — do ONLY the single task described, nothing else. Do NOT create backup / probe / ' +
  '"before"/"after" / temp copies of any file (no *_bak, *_probe, *.orig). Do NOT run your own ' +
  'verification, diff, or "gate check" — the workflow re-verifies your output automatically. Do NOT run ' +
  'any shell command beyond the one(s) explicitly shown in this prompt. Do NOT delete, move, or clean up ' +
  'anything (no rm/rmdir/mv/find -delete) — a single cleanup/permission prompt halts an unattended run. ' +
  'Edit the target file IN PLACE; the workflow keeps its own history via resume.'
const SCRATCH_RULE =
  'NEVER delete anything under the investigation root (no rm/rmdir/mv/find -delete), and never create ' +
  'backup or scratch copies of an artifact. ' + NO_SIDEWORK_RULE
const RETURN_RULE =
  'Return ONLY a completion signal (done + the file path(s) + your promptBindSha). NEVER a summary, ' +
  'headline, orientation, or any account of the contents — the files are the sole deliverable ' +
  '(No summaries, ever: the orchestrator reads the raw file, not your prose).'
// The register travels into EVERY analytical dispatch (the 0.1 rule). SINGLE SOURCE: the compact rule
// below is the inline half; the FULL tier tables + cross-subject/injection guards live once in
// references/register.md and are @-referenced (NOT inlined — inlining would inflate the 7 council
// auditors × every Phase-B substep). Injection is centralised in dispatch() (below); parse-only
// dispatches (step3-plan, resume-parse-hyp) and trusted bash steps deliberately do NOT go through it.
const REGISTER_RULE =
  'REGISTER (the 0.1 rule — applies to this artifact and everything you write): hypothetical never ' +
  'directive (offer possibilities, never instruct — no "do/should/must/take/stop"); probabilistic ' +
  'prioritisation expressed as a plausible narrative — rank by fit ("appears to most closely align"), ' +
  'never single one possibility out as "the biggest/main/real/primary/single cause" or as settled; ' +
  'carry each claim\'s evidence tier into the sentence; the word ' +
  '"diagnosis" only when attributing to a practitioner, never in the tool\'s own voice; no ' +
  'process-completion-as-quality ("the council cleared it"); no needless (a)/(b) opt-in menu when both ' +
  'plainly need doing. DO the prioritisation SILENTLY — never comment on the ranking discipline itself: ' +
  'any aside about how you are ranking (a meta-note that you are not settling on one, that possibilities ' +
  'are "held in parallel", that there is "no single culprit", or any sentence describing your ranking ' +
  'method rather than actually ranking) is BANNED from the output — just rank, never narrate that you ' +
  'are ranking. Every load-bearing claim carries [src:]/[ledger:] + tier in the same sentence.'
// The single-source register block prepended by dispatch(): compact 0.1 rule inline + an @-ref to the
// full tier tables/guards. Lazy (refPath resolves REFS after cfg parse). The exact
// "REGISTER (the 0.1 rule" prefix is load-bearing (orchestrator.test.mjs asserts it).
const registerBlock = () =>
  REGISTER_RULE + '\n\nSee `@' + refPath('register.md') + '` (read that file at that path) for the full ' +
  'T1–T5 causal-certainty tiers, the T0–T3 source-fidelity ladder, and the cross-subject, ' +
  'prior-conclusion, prompt-injection and example-fence guards — read it and apply every clause.'
// dispatch() — the SINGLE chokepoint that injects the register. Every analytical-write dispatch goes
// through it; parse-only dispatches (step3-plan, resume-parse-hyp) and trusted() bash steps call agent()
// directly and carry no register.
const dispatch = (prompt, opts) => agent(registerBlock() + '\n\n' + prompt, opts)
// SMOKE / minimal-plumbing directive — injected into EVERY dispatch when cfg.smoke is on. The driver's
// cap1 only limits fan-outs the DRIVER controls (builders, hypotheses, candidates); it cannot stop a
// single stage-agent from branching INTERNALLY the way its canonical spec tells it to (e.g. Step 2
// building a mechanism map for every anomaly → 6 of them). This directive tells that one agent to do the
// ABSOLUTE MINIMUM so a full-chain plumbing test stays tiny and cheap.
const SMOKE_RULE =
  '\n\n### SMOKE / MINIMAL-PLUMBING TEST — do the ABSOLUTE MINIMUM (this run proves the stage handoff ' +
  'ONLY, never completeness):\n' +
  '- If this step would enumerate or branch over multiple items (anomalies, processes, candidates, ' +
  'hypotheses, questions, connections, research topics), handle ONLY ONE representative item and add a ' +
  'single line: "(smoke: N others intentionally skipped for the plumbing test)".\n' +
  '- Do NOT dispatch /research, /research-practitioner, or any sub-agent, and do NOT run extra shell. ' +
  'Reason only from data already in the run root. If a downstream gate needs a research/anomaly file, ' +
  'write ONE thin placeholder with the required headers and a one-line "(smoke placeholder)" body.\n' +
  '- Step 4.5 specifically: produce exactly ONE working hypothesis + the parallel-null + ONE safety ' +
  'must-exclude — not the full 3–5 set (so downstream per-hypothesis gates stay minimal).\n' +
  '- Keep every artifact deliberately THIN: the required headers/anchors + one representative entry, ' +
  'nothing more. A tiny well-formed artifact that lets the next stage run is the ENTIRE goal.'
// The prompt-bind forcing function — every gated write must carry the SHA of the current ref, and the
// ref must be in the read-log; the write-check verifies both. Source of truth stays in references/.
const bindRule = (rel) =>
  'PROMPT-BIND: Read `' + refPath(rel) + '` IN FULL and follow it verbatim — it is the canonical spec ' +
  'for this step; do not paraphrase from memory. Compute the SHA-256 of that exact file and return it ' +
  'as `promptBindSha`. The write-gate verifies your promptBindSha matches the current ref AND that the ' +
  'ref is in your read-log; a missing/stale/swapped bind is DENIED.'

// ───────────────────────── schemas ─────────────────────────
// Every dispatched write returns a completion signal + its prompt-bind SHA. `done`/`tokenMinted` are
// SELF-REPORTS used only to advance the display; the real gate is the hook on the next write, and the
// trusted census (which stats disk) is what the driver believes — never a schema field.
const WROTE_SCHEMA = {
  type: 'object', required: ['done'],
  properties: { done: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } },
                promptBindSha: { type: 'string' }, note: { type: 'string' } },
}
// Step 4.5 returns the parsed hypothesis set so Phase-B knows which Hn lead and their candidate slugs.
const HYPSET_SCHEMA = {
  type: 'object', required: ['done', 'hypotheses'],
  properties: {
    done: { type: 'boolean' }, promptBindSha: { type: 'string' }, note: { type: 'string' },
    hypotheses: { type: 'array', items: {
      type: 'object', required: ['id'],
      properties: { id: { type: 'string' }, slug: { type: 'string' },
                    isNull: { type: 'boolean' }, isSafety: { type: 'boolean' }, leading: { type: 'boolean' },
                    candidates: { type: 'array', items: { type: 'string' } } } } },
  },
}
// A council auditor's verdict + its readproof result. tokenMinted is a self-report; token existence is
// re-checked on disk by the census before the strip.
const COUNCIL_SCHEMA = {
  type: 'object', required: ['gate', 'verdict'],
  properties: { gate: { type: 'string' }, role: { type: 'string' },
                verdict: { type: 'string' },                 // PASS | FAIL | ESCALATE
                readproofOk: { type: 'boolean' },
                findingsOpen: { type: 'array', items: { type: 'string' } },
                tokenMinted: { type: 'boolean' }, note: { type: 'string' } },
}
// The TRUSTED census — produced by a dispatched agent running the census script that STATS DISK
// (never an in-sandbox self-report). This is the authority the driver's resume + finish-line trust.
const CENSUS_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    manifestValid: { type: 'boolean' },                      // signed run-manifest present + valid
    // (Fix 5: the dead `tokensPresent` field was removed — the JS finish line uses councilState, not tokens.
    // The census may still emit tokensPresent for the live skill flow; the schema simply no longer names it,
    // and unnamed extra keys are ignored — parseCensus reads only `artifacts`/`councilState`/`parsed`.)
    // councilState (Fix 2) — disk-truth of the finish-line council, unioned across both audit mirrors.
    // Absent on an older census / the test mock → the driver falls back to today's verdict+spot-check gate.
    councilState: { type: 'object', properties: {
      readproofGates: { type: 'array', items: { type: 'string' } },   // gates with a marker FRESH for the current draft
      openFindings: { type: 'number' } } },                           // blocking findings opened-and-not-closed
    // parsed (Fix 1) — the work COUNTED from disk (pinned `### Hn` / `**Pn**` formats), so an agent that
    // under-reports cannot shrink the loop. Absent on an older census / the test mock → agent-return fallback.
    parsed: { type: 'object', properties: {
      hypotheses: { type: 'array', items: { type: 'object', properties: {
        id: { type: 'string' }, slug: { type: 'string' }, isNull: { type: 'boolean' }, isSafety: { type: 'boolean' } } } },
      processes: { type: 'array', items: { type: 'object', properties: {
        id: { type: 'string' }, slug: { type: 'string' } } } } } },
    artifacts: { type: 'array', items: {
      type: 'object', required: ['path', 'exists'],
      properties: { path: { type: 'string' }, exists: { type: 'boolean' }, wellFormed: { type: 'boolean' } } } },
    note: { type: 'string' },
  },
}
// Bootstrap's signed run-manifest result.
const MANIFEST_SCHEMA = {
  type: 'object', required: ['done'],
  properties: { done: { type: 'boolean' }, root: { type: 'string' }, manifestPath: { type: 'string' },
                signed: { type: 'boolean' }, note: { type: 'string' } },
}
// The deterministic 2c assembler's --json summary (echoed by the trusted-bash dispatch). ranSuccessfully
// is the authority the driver HALTs on: a non-zero assembler exit prints ranSuccessfully:false, so a
// stale hypothesis-set.md can NEVER be silently accepted (the old free-form-assembler failure class).
const ASSEMBLE_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    nRoots: { type: 'number' }, nCF: { type: 'number' }, nSafety: { type: 'number' },
    anti_flatten_ok: { type: 'boolean' }, grounding_ok: { type: 'boolean' }, note: { type: 'string' },
  },
}
// The bounded 2c JUDGE's instruction map — the ONE cross-family semantic call (which roots are the SAME
// root). The judge composes NO document and writes NO file; it returns only these instructions, which the
// deterministic assembler applies. An empty map is valid (identity assembly = Phase-1 behaviour).
const JUDGE_SCHEMA = {
  type: 'object', required: ['merges', 'moves', 'safety'],
  properties: {
    merges: { type: 'array', items: { type: 'array', items: {
      type: 'object', required: ['family', 'id'],
      properties: { family: { type: 'string' }, id: { type: 'string' } } } } },
    moves: { type: 'array', items: {
      type: 'object', required: ['family', 'id', 'to'],
      properties: { family: { type: 'string' }, id: { type: 'string' }, to: { type: 'string' } } } },
    safety: { type: 'array', items: {
      type: 'object', required: ['slug'],
      properties: { slug: { type: 'string' }, reason: { type: 'string' }, src: { type: 'string' } } } },
    nullSlug: { type: 'string' }, note: { type: 'string' },
  },
}
// The DETERMINISTIC existence check (check-exist.py) — a tiny, fixed-size present/non-empty verdict for a
// KNOWN set of paths. Used INSTEAD of the full census for resume/skip gates over a small known file set:
// the census walks the whole tree and its large artifact list is relayed by an agent that truncates it
// (dropping real files → the driver redoes finished work). `missing` is usually empty, so the relay is tiny.
const EXIST_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' }, checked: { type: 'number' },
    missing: { type: 'array', items: { type: 'string' } }, note: { type: 'string' },
  },
}
// The assembler's family manifest, parsed read-only so the disconfirm stage can batch one agent per family.
const FAMILIES_SCHEMA = {
  type: 'object', required: ['groups'],
  properties: {
    groups: { type: 'array', items: {
      type: 'object', required: ['family', 'ids'],
      properties: { family: { type: 'string' }, ids: { type: 'array', items: { type: 'string' } } },
    } },
  },
}
// Step-8 node selection: the mechanism-map nodes judged to carry the most intervention leverage.
const NODESEL_SCHEMA = {
  type: 'object', required: ['nodes'],
  properties: {
    nodes: { type: 'array', items: {
      type: 'object', required: ['candidate', 'node'],
      properties: { candidate: { type: 'string' }, node: { type: 'string' }, why: { type: 'string' } },
    } },
  },
}
// The deterministic Step-4a selector's summary (select-top.py): the top-N survivors chosen for deep research.
const SELECT_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' }, note: { type: 'string' },
    nTop: { type: 'number' }, nSurvivors: { type: 'number' }, nParked: { type: 'number' }, nCarried: { type: 'number' },
    top: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, slug: { type: 'string' }, citations: { type: 'number' } } } },
  },
}
// Structural-synthesis tools (flag-gated Step-4a replacement). weave_parse mints the canonical edge
// worklist; build-groups computes the groups → selection.md.
const WEAVE_PARSE_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' }, note: { type: 'string' },
    nNodes: { type: 'number' }, nEdges: { type: 'number' }, nDangling: { type: 'number' }, nSelfEdges: { type: 'number' },
  },
}
const BUILD_GROUPS_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' }, note: { type: 'string' }, backend: { type: 'string' },
    nNodes: { type: 'number' }, nGroups: { type: 'number' }, nEdgesTotal: { type: 'number' },
    nEdgesInGraph: { type: 'number' }, nEdgesContradicted: { type: 'number' },
    largestGroupFrac: { type: 'number' }, nSingletons: { type: 'number' },
    groupSizes: { type: 'array', items: { type: 'number' } },
    groups: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, anchor: { type: 'string' }, size: { type: 'number' },
      memberCards: { type: 'array', items: { type: 'string' } } } } },
  },
}

// ───────────────────────── dispatch spine ─────────────────────────
// The thin fixed spine every canonical-prompt step shares. Source of truth is the ref; this only wires
// inputs/output and the reused rules. Gated steps additionally carry the prompt-bind forcing function.
const dispatchPrompt = (step) =>
  '## Step ' + step.id + ' — ' + (step.phase || '') + '\n\n' +
  (step.ref
    ? bindRule(step.ref) + '\n\n'
    : '(This step delegates to the `/extract-health-data` skill — invoke it on everything the person ' +
      'has shared; it owns its own faithful-extraction + compiled-views contract.)\n\n') +
  'The investigation run root is `' + root + '`. ALL paths below are ABSOLUTE — read inputs from and ' +
  'write outputs to exactly these paths (your working directory is NOT the run root; never write a ' +
  'relative path, and never write anywhere outside this run root).\n\n' +
  'Inputs to read first (every one must be in your read-log before you write a gated file):\n' +
  step.inputs.map(i => '- `' + abs(i) + '`').join('\n') + '\n\n' +
  'Write ONLY: ' + step.output.map(o => '`' + abs(o) + '`').join(', ') + '.\n' +
  (step.gated ? 'This is a GATED write — the write-check hook verifies provenance, prompt-bind, ' +
    'read-log, and (at the finish line) audit tokens. A write that violates the spec is DENIED.\n' : '') +
  (smoke ? '\n' + SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + '\nStructured output only.'

const schemaOf = (name) => ({ WROTE: WROTE_SCHEMA, HYPSET: HYPSET_SCHEMA }[name] || WROTE_SCHEMA)

// ───────────────────────── input ─────────────────────────
// args = { root, resumeFrom?, hooksDir?, refsDir?, leadingLimit?, __exposeInternals? }
let cfg = args
if (typeof cfg === 'string') { try { cfg = JSON.parse(cfg) } catch (e) { cfg = {} } }
if (!cfg || typeof cfg !== 'object') cfg = {}

// Test seam (mirrors extract-health-data's cfg.libDir): expose the pure tables + helpers so the
// hermetic harness can unit-test census parsing and assert the procedure tables without a full run.
// Fix 3 (Phase 3) — the deterministic offer concat command (pure; exposed for the golden test). A
// python-STDIN heredoc (NOT a shell `>`/`cp`/`python -c` to the gated draft — those the bash-gate denies).
// It reads each section file in order and writes their byte concatenation to the draft (the emitter then
// parses that single draft by headings → byte-identical to the old single-file append). It SKIPS the write
// when the draft is already present, structurally complete (>=7 `## ` sections), and newer than every
// section file — so a resume re-concat cannot bump the draft mtime past fresh council readproof markers.
const buildOfferConcatCmd = (draftPath, sectionPaths) =>
  'python3 - "' + draftPath + '" ' + sectionPaths.map(p => '"' + p + '"').join(' ') + " <<'PY'\n" +
  'import sys, os\n' +
  'draft = sys.argv[1]\n' +
  'secs = sys.argv[2:]\n' +
  'def mt(p):\n' +
  '    try:\n' +
  '        return os.path.getmtime(p)\n' +
  '    except OSError:\n' +
  '        return None\n' +
  'dm = mt(draft)\n' +
  'if dm is not None:\n' +
  "    try:\n" +
  "        with open(draft, encoding='utf-8', errors='replace') as fh:\n" +
  "            nsec = sum(1 for ln in fh.read().split(chr(10)) if ln.startswith('## '))\n" +
  "    except OSError:\n" +
  "        nsec = 0\n" +
  '    newest = max([mt(s) or 0 for s in secs] or [0])\n' +
  '    if nsec >= 7 and dm >= newest:\n' +
  "        print('concat skipped: offering-draft.md already complete and newer than all sections')\n" +
  '        sys.exit(0)\n' +
  'parts = []\n' +
  'for s in secs:\n' +
  "    with open(s, encoding='utf-8', errors='replace') as fh:\n" +
  '        parts.append(fh.read())\n' +
  "with open(draft, 'w', encoding='utf-8') as fh:\n" +
  "    fh.write(''.join(parts))\n" +
  "print('offering-draft.md assembled from %d sections' % len(secs))\n" +
  'PY'
// Is this path one of the GATED basenames (exact, or a `foo-` prefix glob)? Fix 4 makes the census
// compute structural wellFormed for exactly these, and parseCensus fail-closed on them.
const isGatedBasename = (p) => {
  const base = String(p).split('/').pop()
  return GATED_BASENAMES.some(g => g.endsWith('-') ? base.startsWith(g) : base === g)
}
const parseCensus = (census, wantPaths) => {
  // Pure: given a trusted census + a list of artifact paths, return which are present-and-well-formed.
  // Used by resume (skip a step only if its output is already on disk AND well-formed) and by the
  // finish-line (all tokens + spot-check present). NEVER trusts a schema self-report — only census.
  // Fix 4: for a GATED basename, "done" requires wellFormed === true (structurally complete on disk) —
  // an undefined/absent wellFormed ("can't tell") counts as NOT done. Non-gated files keep the lenient
  // wellFormed !== false rule. Backward-compat: an older census still emits a boolean size>0 wellFormed,
  // so === true holds for a non-empty gated file; no half-migration hard-halt.
  const byPath = {}
  if (census && Array.isArray(census.artifacts)) for (const a of census.artifacts) if (a && a.path) byPath[a.path] = a
  const done = [], missing = []
  for (const p of (wantPaths || [])) {
    const a = byPath[p]
    const wellFormed = isGatedBasename(p) ? (a && a.wellFormed === true) : (a && a.wellFormed !== false)
    if (a && a.exists && wellFormed) done.push(p); else missing.push(p)
  }
  return { done, missing, complete: missing.length === 0 }
}
// (Fix 5: the dead `tokensSatisfied` helper was removed — nothing consumed it after the JS finish line
// switched from HMAC gate tokens to council verdicts + census.councilState disk-proof.)
// Coverage reconciler (Phase 3): every item (document / hypothesis / datum / map-step) must resolve to
// EXACTLY one owner — zero owners OR more than one both FAIL (a silent drop and a double-count are equally
// wrong). A deepening-pending reopened hypothesis counts as owned by its pending deepening pass. Pure.
const reconcileOwnership = (items, ownersOf) => {
  const failures = []
  for (const it of items) {
    const owners = ownersOf(it) || []
    if (owners.length !== 1) failures.push({ item: it, owners: owners.length })
  }
  return { ok: failures.length === 0, failures }
}

// ── A7: fail-closed extraction accuracy gate (ported with the Step-1 flip) ────────────────────────
// extract-health-data.js embeds a single-line ACCURACY-VERDICT token in extracted/spot-check.md
// (`<!-- ACCURACY-VERDICT {"clean":bool,"failures":[...]} -->`, right after the H1). runStep1 reads it
// off disk and HALTS Step 1 unless clean:true — ONE predicate, SAME on the fresh finish gate AND the
// resume early-return, so resume cannot bypass the check. No "proceed anyway" flag; recovery is fix the
// source, remove extracted/spot-check.md, re-run.
const VERDICT_READ_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: { ranSuccessfully: { type: 'boolean' }, line: { type: 'string' }, note: { type: 'string' } },
}
// The exact grep the reader runs (pure; exposed for the shared-artifact round-trip test). Position-
// independent — matches the ACCURACY-VERDICT line wherever it sits and prints only that line; `|| true`
// so an absent token / missing file is a clean exit (fail-closed handled in parseVerdictLine).
const verdictGrepCmd = (spotPath) =>
  "grep -m1 -o 'ACCURACY-VERDICT .*-->' " + JSON.stringify(spotPath) + ' || true'
// Parse a grepped verdict line, FAIL-CLOSED: no token / bad JSON / missing boolean clean ⇒ clean:false
// (pure; exposed for the round-trip test). The regex is whitespace/position tolerant.
const parseVerdictLine = (line) => {
  const m = (typeof line === 'string' ? line : '').match(/ACCURACY-VERDICT\s+(\{.*\})\s*-->/)
  if (!m) return { clean: false, failures: [{ kind: 'verdict-missing', detail: 'no ACCURACY-VERDICT token on spot-check.md' }] }
  let v
  try { v = JSON.parse(m[1]) } catch (e) { return { clean: false, failures: [{ kind: 'verdict-malformed', detail: 'verdict token JSON did not parse' }] } }
  if (!v || typeof v.clean !== 'boolean') return { clean: false, failures: [{ kind: 'verdict-malformed', detail: 'verdict token has no boolean clean' }] }
  return { clean: v.clean, failures: Array.isArray(v.failures) ? v.failures : [] }
}
const verdictReason = (v) => (((v && v.failures) || []).map(f => (f && f.kind ? f.kind : '?') + (f && f.detail ? ' (' + f.detail + ')' : '')).join('; ')) || 'unknown accuracy failure'
// Read + parse the verdict off spot-check.md via a dispatched grep (the driver is sandboxed — all
// disk-truth goes through a trusted bash step). Fail-closed on any read failure.
const readVerdict = async (spotPath) => {
  const r = await agent(
    '## Read the extraction accuracy verdict (trusted grep)\n\n' +
    'Run EXACTLY this command and return the single line it prints (empty string if it prints nothing) ' +
    'as `line` — do not judge, reformat, filter, or add anything.\n\n```bash\n' + verdictGrepCmd(spotPath) + '\n```\n\n' +
    'Return {ranSuccessfully:true, line:"<the printed line, verbatim, or empty>"}. ' + NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'verdict-read', phase: 'Prepare · Extract', schema: VERDICT_READ_SCHEMA })
  return parseVerdictLine(r && typeof r.line === 'string' ? r.line : '')
}

// Deterministic genome-hold sniff (pure; exposed for tests). Prints the basename of every converted
// source that is a large raw-genotype file (>1MB AND a majority of the first 4000 lines are rsID/i-ID
// genotype rows — a consumer genotyping service/Ancestry raw exports). No '>'/'rm' — read-only, safe under any gate.
const genomeSniffCmd = (dir) =>
  'for gtxt in "' + dir + '"/*.txt; do\n' +
  '  [ -f "$gtxt" ] || continue\n' +
  '  case "$(basename "$gtxt")" in _genome-references.txt) continue;; esac\n' +
  '  gb=$(wc -c < "$gtxt" | tr -d " ")\n' +
  '  [ "${gb:-0}" -gt 1000000 ] || continue\n' +
  '  gs=$(head -n 4000 "$gtxt" | grep -cE "^(rs|i)[0-9]+" || true)\n' +
  '  gt=$(head -n 4000 "$gtxt" | wc -l | tr -d " ")\n' +
  '  [ "${gt:-0}" -gt 0 ] && [ "${gs:-0}" -gt $((gt/2)) ] && basename "$gtxt"\n' +
  'done'
const GENOME_REFS_SCHEMA = {
  type: 'object', required: ['basenames'],
  properties: { basenames: { type: 'array', items: { type: 'string' } } },
}
// Read the raw-genetics files to hold OUT of extraction via a trusted sniff (the driver is sandboxed).
// The run must NOT depend on the convert agent echoing the optional genomeRefs field — it silently
// omitted it (2026-07-16), which would have dumped the 16MB genome into extraction. Fail-open to []
// (a sniff miss extracts the genome — wasteful but not wrong); the result is unioned with rep.genomeRefs.
const readGenomeRefs = async (dir) => {
  const r = await agent(
    '## Identify raw-genetics files to hold out of extraction (trusted sniff)\n\n' +
    'Run EXACTLY this command and return EVERY line it prints as an element of `basenames` (an empty ' +
    'array if it prints nothing). Do not judge, filter, reformat, or add anything — just the printed lines.\n\n' +
    '```bash\n' + genomeSniffCmd(dir) + '\n```\n\n' +
    'Return {basenames:[...]}. ' + NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'genome-refs-read', phase: 'Prepare · Extract', schema: GENOME_REFS_SCHEMA })
  return Array.isArray(r && r.basenames) ? r.basenames.map(String) : []
}

// B1 — the finish-line proof-of-read predicate: which required gates lack a FRESH readproof marker.
// The required set derives from the SINGLE source of truth (AUDITORS[].gate, deduped) — the exact set
// the council readproof dispatch writes markers under — so writer and reader can never disagree. Pure;
// exposed for the behavioral finish-gate test.
const finishLineMissingProof = (readproofGates) => {
  const need = [...new Set(AUDITORS.map(a => a.gate))]
  const fresh = new Set(Array.isArray(readproofGates) ? readproofGates : [])
  return need.filter(g => !fresh.has(g))
}

// Per-source EXTRACTION KIND (Phase-2 wiring) — the deterministic route for stage-1 extraction, derived
// from the convert receipt (no new record field): `vector-pdf` when word-geometry positions exist (geom
// reconstructs the tables), `image` when the ORIGINAL source is an image file (the dual-vision path Reads
// that image), else `text` (the LLM extract over converted text, incl. scanned PDFs with no positions).
// Pure; exposed for tests.
const IMG_EXT = /\.(png|jpe?g|tiff?)$/i
const srcKind = (r) => (r && r.positions) ? 'vector-pdf'
  : (IMG_EXT.test(String((r && r.source) || '')) ? 'image' : 'text')

if (cfg.__exposeInternals) {
  return { __internals: {
    STEPS, PHASE_B_SUBSTEPS, OFFER_SECTIONS, AUDITORS, GATED_BASENAMES,
    parseCensus, dispatchPrompt, bindRule, refPath, registerBlock,
    isGatedBasename, buildOfferConcatCmd, reconcileOwnership,
    verdictGrepCmd, parseVerdictLine, finishLineMissingProof, srcKind,
  } }
}

if (!cfg.root) {
  return { error: 'investigate-health-orchestrator needs args = { root, resumeFrom?, hooksDir?, refsDir? }. ' +
                  'root is the subject investigation directory.' }
}
if (cfg.hooksDir) HOOKS = '"' + cfg.hooksDir.replace(/\/$/, '') + '"'
if (cfg.refsDir)  REFS  = '"' + cfg.refsDir.replace(/\/$/, '') + '"'
const root = cfg.root.replace(/\/$/, '')
const at = (rel) => root + '/' + rel
// Pure-JS UTF-8 → base64 (the Workflow runtime has NO `Buffer`/`TextEncoder`/`unescape` — a `Buffer.from`
// crashed a live run with "Buffer is not defined"). Used to thread the judge's instruction map to the
// assembler inline (base64 survives shell quoting incl. apostrophes). Handles multibyte + surrogate pairs.
const b64FromString = (s) => {
  const A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  const bytes = []
  for (let i = 0; i < s.length; i++) {
    let c = s.charCodeAt(i)
    if (c < 0x80) { bytes.push(c) } else if (c < 0x800) {
      bytes.push(0xc0 | (c >> 6), 0x80 | (c & 0x3f))
    } else if (c >= 0xd800 && c < 0xdc00) {
      const cp = 0x10000 + ((c & 0x3ff) << 10) + (s.charCodeAt(++i) & 0x3ff)
      bytes.push(0xf0 | (cp >> 18), 0x80 | ((cp >> 12) & 0x3f), 0x80 | ((cp >> 6) & 0x3f), 0x80 | (cp & 0x3f))
    } else { bytes.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 0x3f), 0x80 | (c & 0x3f)) }
  }
  let out = ''
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i], b = i + 1 < bytes.length ? bytes[i + 1] : 0, d = i + 2 < bytes.length ? bytes[i + 2] : 0
    out += A[a >> 2] + A[((a & 3) << 4) | (b >> 4)] +
      (i + 1 < bytes.length ? A[((b & 15) << 2) | (d >> 6)] : '=') +
      (i + 2 < bytes.length ? A[d & 63] : '=')
  }
  return out
}
// Dispatched sub-agents do NOT run with their cwd in the run root, so EVERY path handed to an agent must
// be ABSOLUTE (run-root-anchored) — a relative "write step2-mechanism-map.md" lands nowhere resolvable
// and the census then correctly reports the output missing (the step-2 halt bug). `abs()` anchors a
// run-root artifact to the root; it leaves already-absolute paths, external refs (memory/, hard_no*),
// and descriptive phrases (containing a space) untouched.
const abs = (p) => (p.startsWith('/') || p.includes(' ') || p.startsWith('memory/') || p.startsWith('hard_no')) ? p : at(p)
// Slugify a process/candidate label for use INSIDE a filename — a sub-agent can return a whole sentence
// as a "slug" (observed: "Interview: symptom onset tracks…"), which makes an unwieldy, space-laden path.
// Filenames are matched downstream by glob (builder-*.md / mechanism-map-*.md), so the exact slug is not
// load-bearing; this just keeps them clean and shell-safe.
const slugify = (s) => (String(s == null ? '' : s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'x')
// A stable session id for the council/token scripts. The audit tokens verify by run-root mirror + HMAC
// (both session-independent), so the exact value is not load-bearing — it just needs to be consistent
// and non-empty (dispatched agents have no shared $IH_SESSION env var, which was why minting failed).
const IH_SESSION = 'wf-' + (root.split('/').filter(Boolean).pop() || 'run')
let leadingLimit = cfg.leadingLimit || 3   // how many top hypotheses run the full Phase-B deep-dive

// SMOKE / LIMIT mode — the cheap testing rung. Caps EVERY fan-out to 1 (one blind builder, one leading
// hypothesis, one candidate per B3) so a real run dispatches the minimum agents needed to prove a step
// works, instead of burning the full fleet. `cfg.stopAfter = '<stepId>'` halts the driver right after
// that step so a dry run does exactly one thing. (The full all-agents run — the "true test" — is smoke
// off, run last.) Neither knob weakens a gate: capped fan-out still writes real artifacts through the
// real hooks; it just does fewer of them.
const smoke = !!cfg.smoke
const cap1 = (arr) => (smoke && Array.isArray(arr) && arr.length > 1) ? arr.slice(0, 1) : arr

// ── Modular stages (default UNCHANGED) ───────────────────────────────────────────────────────────────
// The whole chain is 18 ordered stages. Two SYMMETRIC knobs carve out a contiguous slice for standalone
// invocation: `cfg.startAt` (lower bound — stages before it are SKIPPED; their outputs must already exist
// on disk) and `cfg.stopAfter` (upper bound — the driver returns right AFTER that stage). With NEITHER set
// the whole chain runs exactly as before (stageActive is always true; the stopAfter returns never fire),
// so a normal run's dispatch labels / halts / order are byte-identical. A sliced run is disk-authoritative:
// bootstrap + the initial census always run (in resume posture) so downstream isDone() reads see disk
// truth, every stage re-derives its inputs from the census, and the existing `halt` machinery fails loud
// (naming the input) on a missing prerequisite — so a slice stands alone once its upstream artifacts exist.
const STAGE_ORDER = ['bootstrap', 'onboard', 'extract', 'generate', 'integrate', 'disconfirm', 'select',
  'research', 'interview', 'cohere', 'deepen', 'prioritize', 'sweep', 'intervene', 'compose', 'audit',
  'finalise', 'openthreads']
// Legacy stopAfter aliases (the step-ids used before stage-ids existed) → the stage they stop after.
// Preserved so existing callers/tests (stopAfter:'0','1','2b','5.14','phaseB','6','7','sweep','8','intervene')
// keep working unchanged; the smokeReturn values at those sites also stay the legacy step-ids.
const STAGE_ALIAS = { '0': 'onboard', '1': 'extract', '2': 'generate', '2b': 'generate',
  'phaseB': 'deepen', '5.14': 'deepen', '6': 'prioritize', '7': 'sweep', '8': 'intervene' }
const stageId = (x) => (x == null ? null : (STAGE_ALIAS[String(x)] || String(x)))
const startAtStage = stageId(cfg.startAt)
const stopStage = stageId(cfg.stopAfter)
if (startAtStage != null && !STAGE_ORDER.includes(startAtStage))
  return { root: cfg.root, error: 'cfg.startAt="' + cfg.startAt + '" is not a known stage. Stages: ' + STAGE_ORDER.join(', ') }
if (stopStage != null && !STAGE_ORDER.includes(stopStage))
  return { root: cfg.root, error: 'cfg.stopAfter="' + cfg.stopAfter + '" is not a known stage/alias. Stages: ' + STAGE_ORDER.join(', ') }
const startIdx = startAtStage ? STAGE_ORDER.indexOf(startAtStage) : 0
const sliced = startAtStage != null
// A standalone slice runs the driver in RESUME POSTURE so each stage reads disk truth (census) rather than
// a prior in-run stage's return; the stageActive lower-bound then hard-skips the fan-out of any earlier stage.
const resuming = !!cfg.resumeFrom || sliced
const stageActive = (id) => STAGE_ORDER.indexOf(id) >= startIdx
const stopAfter = (id) => stopStage != null && stageId(id) === stopStage
const smokeReturn = (afterId, extra) => ({ root: cfg.root, smoke, stoppedAfter: afterId, halted: false, ...(extra || {}) })
if (smoke) { leadingLimit = 1; log('SMOKE MODE: every fan-out capped to 1 (one process / one leading hypothesis / one candidate).' + (cfg.stopAfter != null ? ' Stop after step ' + cfg.stopAfter + '.' : '')) }
if (sliced || cfg.stopAfter != null) log('MODULAR RUN: ' + (startAtStage ? 'startAt=' + startAtStage : 'startAt=bootstrap') + (stopStage ? ', stopAfter=' + stopStage : '') + ' (stages outside the range are skipped; their outputs must pre-exist on disk).')

// A dispatched agent that runs a trusted script in Bash and returns a schema — the ONLY way the
// sandboxed driver reaches disk-truth. The script itself is the trust boundary, not the agent's word.
const trusted = (title, bash, schema, label, phase) =>
  agent(
    '## ' + title + ' (trusted disk step)\n\n' +
    'Run EXACTLY the command(s) below and report what they print. This is NOT a judgement task — do ' +
    'not improvise, do not add "gate check" or cleanup commands.\n\n```bash\n' + bash + '\n```\n\n' +
    'Return the structured result the command prints. Set ranSuccessfully/done=false with the error in ' +
    'note if a command failed. ' + NO_SIDEWORK_RULE + ' Structured output only.',
    { label, phase, schema }
  )

let __censusN = 0
const censusBash = () =>
  // A UNIQUE --nonce per call. The census command is otherwise byte-identical every step, and
  // cumulatively across a session it trips the rate-limiter's "same command 8+ times" LOOP block — which
  // surfaced as ranSuccessfully:false / an empty census and a false "output missing" halt. The census
  // script ignores unknown args (its `*) shift`), so --nonce is a harmless uniquifier.
  // --session lets the census locate the /tmp session-keyed audit mirror (readproof markers + findings
  // ledgers) it unions with the run-root mirror for councilState (Fix 2). Same session string the
  // council-readproof/finding dispatches carry, so both sides resolve the same mirror dir.
  'bash ' + hookScript('investigate-census.sh') + ' --root "' + root + '" --session "' + IH_SESSION + '" --json --nonce c' + (++__censusN)

// Structured hard-stop: write RESUME.md and return (mirrors the plan's RESUME.md-style structured return).
const halt = async (stepId, reason) => {
  log('HALT at step ' + stepId + ': ' + reason)
  await trusted('Write RESUME.md (blocked)',
    'bash ' + hookScript('investigate-resume-write.sh') + ' --root "' + root + '" --step "' + stepId +
    '" --reason ' + JSON.stringify(reason),
    WROTE_SCHEMA, 'resume:' + stepId, 'Share · Open Threads')
  return { root: cfg.root, halted: true, atStep: stepId, reason }
}

log('investigate-health-orchestrator: root=' + root + (cfg.resumeFrom ? ' (resume from ' + cfg.resumeFrom + ')' : '') +
    '; leading deep-dive limit=' + leadingLimit + '.')

// ───────────────────────── Bootstrap — signed manifest + state (forcing function) ─────────────────────────
// The forcing function: emit a signed run-manifest and the signed .investigate-active, register the root
// on the allowlist, and instantiate the state stubs (working-truth.md, decision-log.md, …). Done by a
// dispatched bash agent — the driver cannot sign or write. The finish-line offer write is later DENIED
// unless this manifest verifies, removing the model-driven escape hatch.
phase('Bootstrap')
const boot = await trusted(
  'Bootstrap: sign run-manifest, activate + register root, instantiate state stubs',
  'bash ' + hookScript('investigate-bootstrap.sh') + ' --root "' + root + '"' +
  (resuming ? ' --resume' : '') + (cfg.failClosed ? ' --fail-closed' : '') + ' --emit-manifest --register --stubs',
  MANIFEST_SCHEMA, 'bootstrap', 'Bootstrap')
if (!boot || !boot.done) return await halt('bootstrap', 'bootstrap did not confirm a signed run-manifest — refusing to run unenforced.')

// Trusted census up front — on a fresh run everything is missing; on resume it tells us what already
// exists well-formed so we neither re-run a passed gated step nor skip an incomplete one (idempotent-resume).
let census = { ranSuccessfully: false, artifacts: [] }
for (let i = 0; i < 6; i++) {
  // Same flake-rejection as refreshCensus: a bootstrapped root ALWAYS has stubs (decision-log.md,
  // working-truth.md) + the marker/manifest, so an empty census here is a sub-agent flake. Reject it and
  // retry — trusting it on resume would make every isDone() false and needlessly re-run finished steps.
  const c0 = await trusted('Initial census (stat disk)' + (i ? ' [retry ' + i + ']' : ''), censusBash(),
    CENSUS_SCHEMA, 'census:init' + (i ? '-r' + i : ''), 'Bootstrap')
  if (c0 && c0.ranSuccessfully && Array.isArray(c0.artifacts) && c0.artifacts.length > 0) { census = c0; break }
}
const isDone = (rel) => parseCensus(census, [at(rel)]).complete
// (Fix 3 replaced the all-or-nothing anyDone() fan-out skip with per-item isDone() checks — every fan-out
// stage now resumes exactly the missing items and halts on any expected artifact still absent.)
// The census is produced by a dispatched LLM agent running the census script; that agent can transiently
// flake (return null / an incomplete list). A single bad read must NOT cause a false halt, so refreshCensus
// RETRIES (up to 3, distinct labels so nothing caches), accepts only a ranSuccessfully census, and — when
// the caller names the artifact(s) it just wrote (`expect`) — keeps retrying until they appear (this also
// absorbs write-flush timing). Only a genuinely-absent artifact after 3 honest reads is treated as missing.
const refreshCensus = async (labelSuffix, ph, expect) => {
  for (let i = 0; i < 6; i++) {
    const c = await trusted('Census (stat disk)' + (i ? ' [retry ' + i + ']' : ''), censusBash(),
      CENSUS_SCHEMA, 'census:' + labelSuffix + (i ? '-r' + i : ''), ph)
    // A TRUSTWORTHY census ran AND saw the run root's always-present bootstrap stubs (decision-log.md,
    // working-truth.md are written at bootstrap; the marker + manifest always exist). An EMPTY artifact
    // list from a bootstrapped root is a sub-agent flake — the census agent can return
    // {ranSuccessfully:true, artifacts:[]} without faithfully reporting the deterministic script output.
    // Trusting it caused a false "output missing" halt at a step whose file was actually on disk. So we
    // REJECT a degenerate census, KEEP the last good one, and retry (6×) — a real absence survives 6
    // honest reads; a flake does not.
    if (c && c.ranSuccessfully && Array.isArray(c.artifacts) && c.artifacts.length > 0) {
      census = c
      if (!expect || !expect.length || parseCensus(census, expect).complete) return
      log('census: expected artifact not yet visible (' + parseCensus(census, expect).missing.join(', ') + ') — re-reading.')
    } else {
      log('census: degenerate/empty result (sub-agent flake) — not trusting it, retrying.')
    }
  }
}

// ───────────────────────── linear spine driver ─────────────────────────
// Walk the fixed STEPS chain. Because CODE (not model memory) walks the chain, a step cannot be
// skipped or reordered. Each step: dispatch its canonical-prompt agent → refresh census → advance
// only if the OUTPUT is on disk well-formed (census truth), else halt. Resume skips a step only when
// the census already shows its output complete.
const runStep = async (step) => {
  const outs = step.output.filter(o => !o.endsWith('/') && !o.includes('<')).map(at)
  if (cfg.resumeFrom && outs.length && parseCensus(census, outs).complete) {
    log('resume: step ' + step.id + ' already complete on disk — skipping.'); return true
  }
  phase(step.phase)
  const r = await dispatch(dispatchPrompt(step), { label: 'step:' + step.id, phase: step.phase, schema: schemaOf(step.schema) })
  await refreshCensus('step-' + step.id, step.phase, outs)
  // AUTHORITATIVE gate = disk truth (census), NOT the agent's self-reported done. A lying schema value
  // cannot advance past a gated write: the output must actually exist well-formed (the write-hook must
  // have let it through).
  if (outs.length && !parseCensus(census, outs).complete) {
    await halt(step.id, 'step ' + step.id + ' output not present/well-formed on disk after dispatch (write-gate denied or agent skipped it): missing ' +
      parseCensus(census, outs).missing.join(', '))
    return false
  }
  return { r }
}

// ── Step 1 (Prepare · Extract) — CODE-OWNED conversion → receipt-derived extraction (the flip) ─────────
// Was: a prose delegation telling an agent to "invoke /extract-health-data on everything the person
// shared" — the load-bearing source list left to LLM improvisation. Now the DRIVER runs the converter
// (dispatched, since the driver is sandboxed), reads its receipt, and either HALTS naming every
// non-converted source or builds the exact sources[] from the role=document converted records and invokes
// the extraction workflow. The source list is receipt-derived, never free-hand. Encrypted files escalate
// as blocked-environment (never a silent blank); pass a DOB/name hint via cfg.pdfDob (DDMMYYYY)/cfg.pdfName.
// A7 (fail-closed accuracy gate) rides here: after extraction, the ACCURACY-VERDICT token on spot-check.md
// is read and the run HALTS unless clean — the SAME predicate on the fresh finish AND the resume skip.
const CONVERSION_SCHEMA = {
  type: 'object', required: ['ranSuccessfully', 'records'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    summary: { type: 'object', properties: {
      total: { type: 'number' }, converted: { type: 'number' }, failed: { type: 'number' } } },
    records: { type: 'array', items: {
      type: 'object', required: ['source', 'status', 'role'],
      properties: {
        source: { type: 'string' }, status: { type: 'string' }, role: { type: 'string' },
        tool: { type: 'string' }, reason: { type: 'string' }, output: { type: 'string' },
        declared: {}, produced: {}, positions: { type: 'string' } } } },
    genomeRefs: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
}
const CONVERT_DIR = cfg.convertDir
  ? '"' + cfg.convertDir.replace(/\/$/, '') + '"'
  : '"$HOME/.claude/skills/extract-health-data/scripts"'
const convScript = CONVERT_DIR.replace(/"$/, '') + '/convert-source.sh"'
const sourcesDir = root + '/extracted/sources'
// A1/A2/A3 — the orchestrated extraction runs its coverage-diff (+ the byte-verbatim chunker/manifest the
// extract-health-data seam repoints alongside it) from a Claude-owned lib dir, so the CORRECTED atom-diff
// reaches the orchestrator path WITHOUT editing the write-blocked skills/ copy. Overridable via
// cfg.atomLibDir. Unify-later: cp the corrected atom-diff into skills/scripts/ AND drop this arg.
const ATOM_LIB_DIR = cfg.atomLibDir ? cfg.atomLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/atom-diff'
// The verifier is reached through its OWN explicit path (NOT the flat atom-diff libDir seam): the
// extract-health-data driver reads args.verifyLibDir to locate lib/verify/cite_verify.py. Passing it
// here is what makes the atom-diff → cite_verify cutover a driver+orchestrator co-change (red-team
// hidden-coupling-2). libDir still points chunker + manifest at lib/atom-diff. Overridable via
// cfg.verifyLibDir.
const VERIFY_LIB_DIR = cfg.verifyLibDir ? cfg.verifyLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/verify'
// The timeline layer — the ONE cross-source artifact every later stage reads. Its own explicit path
// (args.timelineLibDir), for the same reason the verifier has one: a cutover here must be a visible
// co-change across the orchestrator AND the driver, never a silent overload of libDir.
const TIMELINE_LIB_DIR = cfg.timelineLibDir ? cfg.timelineLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/timeline'
const TIMELINE_SOURCES = cfg.timelineSources || '$HOME/.claude/skills/investigate-health/references/timeline-source.md'
// The deterministic geometry extractor (geom-extract.py) for the vector-pdf kind route; the driver
// reads args.convertLibDir to locate it. Overridable so an E2E can point at the repo before install.
const CONVERT_LIB_DIR = cfg.convertLibDir ? cfg.convertLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/convert'
// The deterministic 2c helpers (assemble-hypset.py, check-exist.py) — reached by name so the bash-gate
// allows the assembler's direct write (a read ARG, not an inline redirect). Default points STRAIGHT at the
// canonical repo (the helper runs in an agent's bash, which reads the repo directly), so NO ~/.claude
// symlink install is needed — unlike the older lib seams that default to $HOME/.claude/workflows/lib/*.
// Overridable via cfg.assembleLibDir.
const INTEGRATE_LIB_DIR = cfg.assembleLibDir ? cfg.assembleLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/integrate'
// The structural-synthesis stdlib tools (weave_parse.py, build-groups.py). Same repo-canonical location
// convention as INTEGRATE_LIB_DIR. Overridable via cfg.synthesizeLibDir.
const SYNTHESIZE_LIB_DIR = cfg.synthesizeLibDir ? cfg.synthesizeLibDir.replace(/\/$/, '') : '$HOME/.claude/workflows/lib/synthesize'
// Deterministic present/non-empty check for a KNOWN, small set of absolute paths — via check-exist.py,
// NOT the full census. Returns the ABSOLUTE paths that are absent/empty, or null if the check could not be
// run (dispatch failed / malformed) so the caller can fail-closed rather than guess. The relayed payload is
// tiny (usually `missing:[]`), so it does not hit the census's artifact-list truncation.
const missingAbs = async (absPaths, label, ph) => {
  const cmd = 'python3 "' + INTEGRATE_LIB_DIR + '/check-exist.py" --paths ' +
    absPaths.map(p => '"' + p + '"').join(' ') + ' --json'
  const r = await trusted('Existence check — ' + absPaths.length + ' known file(s)', cmd, EXIST_SCHEMA, label, ph)
  if (!r || r.ranSuccessfully !== true || !Array.isArray(r.missing)) return null
  return r.missing
}
// Which of a fan-out's items still need (re)doing on a resume/slice. On a fresh run → all of them. On a
// resume/slice → only the items whose output is absent/empty per the DETERMINISTIC check-exist (NOT the
// census artifact list, which the relaying agent truncates → wrongly redoing finished LLM work). If the
// existence check itself cannot run, fail SAFE by redoing all (these outputs are individually regenerable —
// unlike the family integrations, whose destructive-overwrite case fail-CLOSED with a halt instead).
const resumeTodo = async (items, relOf, label, ph) => {
  if (!resuming) return items
  const miss = await missingAbs(items.map(i => at(relOf(i))), label, ph)
  if (miss === null) return items
  const missSet = new Set(miss)
  return items.filter(i => missSet.has(at(relOf(i))))
}
const runStep1 = async () => {
  // halt then return FALSY (mirrors runStep's `await halt(...); return false`) so the caller's
  // `if (!(await runStep1()))` early-return fires — halt() itself returns a TRUTHY object. Declared
  // before the resume early-return so BOTH the resume path and the finish gate can bail via it.
  const bail = async (reason) => { await halt('1', reason); return false }
  // A7 — resume path: the SAME accuracy gate as the fresh finish gate. A previously-run Step 1 is only
  // skipped if its spot-check.md is present AND its verdict is clean; a dirty/missing/malformed verdict
  // HALTS (fail-closed). Guard is cfg.resumeFrom (NOT the wider `resuming`): a pure startAt='extract'
  // slice must PRODUCE the extraction, not skip on presence (matches runStep's own resume guard).
  if (cfg.resumeFrom && isDone('extracted/spot-check.md')) {
    const v = await readVerdict(at('extracted/spot-check.md'))
    if (!v.clean)
      return await bail('resume: Step 1 was previously run but its extraction accuracy verdict is NOT ' +
        'clean: ' + verdictReason(v) + '. The offer must not be built on flawed extraction. Fix the ' +
        'source(s), remove ' + at('extracted/spot-check.md') + ', and re-run the extraction (a plain ' +
        'resume re-halts by design — that IS the gate working).')
    log('resume: Step 1 already complete (extracted/spot-check.md present, accuracy verdict clean) — skipping.'); return true
  }
  phase('Prepare · Extract')
  const shq = (v) => "'" + String(v).replace(/'/g, "'\\''") + "'"
  const dobEnv  = cfg.pdfDob  ? 'PDF_DOB='  + shq(cfg.pdfDob)  + ' ' : ''
  const nameEnv = cfg.pdfName ? 'PDF_NAME=' + shq(cfg.pdfName) + ' ' : ''
  const convBash =
    'mkdir -p "' + sourcesDir + '"\n' +
    dobEnv + nameEnv + 'bash ' + convScript + ' "' + root + '/data" "' + sourcesDir + '" || true\n' +
    'echo "=== REPORT ==="\n' +
    'cat "' + sourcesDir + '/conversion-report.json"\n' +
    'echo "=== POSFILES ==="\n' +
    'ls "' + sourcesDir + '"/*.pos.json 2>/dev/null | xargs -n1 basename 2>/dev/null || true\n' +
    // Genome-reference rule (extract-step instruction): a large raw-genotype file (a consumer genotyping service/Ancestry-style
    // rsID rows) is NOT dumped into full extraction — dumping a 16MB SNP table just burns context. Sniff
    // the converted .txt outputs: >1MB AND a majority of the first lines are rsID genotype rows → list its
    // basename under GENOME-REFS and index it in _genome-references.txt (a discoverable standing resource
    // the deepen/research steps query at specific rsIDs — steps/step2.md, step5.md).
    'echo "=== GENOME-REFS ==="\n' +
    // Index is APPEND-ONLY and idempotent — NO truncate (`: >`) and NO `rm` under the run root (the
    // mid-run cleanup-block hook denies those, and rightly: nothing under the run root may be deleted/
    // overwritten mid-run). The grep-guard makes a resume re-append a no-op instead of duplicating; the
    // file is only created when a genome IS found, so there is no empty file to clean up.
    'GREFIDX="' + sourcesDir + '/_genome-references.txt"\n' +
    'for gtxt in "' + sourcesDir + '"/*.txt; do\n' +
    '  [ -f "$gtxt" ] || continue\n' +
    '  case "$(basename "$gtxt")" in _genome-references.txt) continue;; esac\n' +
    '  gb=$(wc -c < "$gtxt" | tr -d " ")\n' +
    '  [ "${gb:-0}" -gt 1000000 ] || continue\n' +
    '  gs=$(head -n 4000 "$gtxt" | grep -cE "^(rs|i)[0-9]+" || true)\n' +
    '  gt=$(head -n 4000 "$gtxt" | wc -l | tr -d " ")\n' +
    '  if [ "${gt:-0}" -gt 0 ] && [ "${gs:-0}" -gt $((gt/2)) ]; then\n' +
    '    basename "$gtxt"\n' +
    '    grep -qF "$gtxt |" "$GREFIDX" 2>/dev/null || echo "$gtxt | raw-genetics standing resource (unread) — query at specific rsIDs only, do not extract" >> "$GREFIDX"\n' +
    '  fi\n' +
    'done'
  const rep = await agent(
    '## Step 1a — convert every source (deterministic, non-LLM)\n\n' +
    'Run EXACTLY the command below and report what the receipt says. This is NOT a judgement task — run it ' +
    'and echo the JSON. The converter writes one record per discovered source to conversion-report.json and ' +
    'exits non-zero if ANY source did not convert (expected and fine — still cat the report so every failure ' +
    'is named).\n\n```bash\n' + convBash + '\n```\n\n' +
    'Return the parsed report: `summary` = {total, converted, failed}; `records` = the array from the JSON ' +
    '(each {source, status, role, tool, declared, produced, reason, output}); AND for each record whose ' +
    'output has a sibling `<base>.pos.json` in the POSFILES list, set that record\'s `positions` to the ' +
    'absolute sidecar path (' + sourcesDir + '/<base>.pos.json). ALSO set `genomeRefs` = the list of ' +
    'basenames printed under the `=== GENOME-REFS ===` marker (raw-genetics files held as a targeted-search ' +
    'standing resource — NOT extracted); an empty array if none are printed. Set ranSuccessfully=false ONLY ' +
    'if the command could not run at all / no report was produced. ' + NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'convert', phase: 'Prepare · Extract', schema: CONVERSION_SCHEMA })

  if (!rep || rep.ranSuccessfully === false || !Array.isArray(rep.records) || !rep.records.length) {
    return await bail('conversion did not produce a readable receipt (convert-source.sh failed to run or ' +
      'wrote no conversion-report.json). Check that ' + root + '/data exists and the converter is installed at ' +
      CONVERT_DIR.replace(/"/g, '') + '.')
  }
  // A HEIC/image the converter cannot decode in this environment is CATALOGUED (status 'catalogued',
  // role 'image-undecoded') — present on disk, not OCR'd — and must NOT halt the run. Documents that
  // fail still halt (the no-hole guarantee holds for text sources).
  const catalogued = rep.records.filter(r => r.status === 'catalogued')
  // Halt-on-any-failure — name EVERY non-converted, non-catalogued source at once (one round-trip, not N).
  const failed = rep.records.filter(r => r.status !== 'converted' && r.status !== 'catalogued')
  if (failed.length) {
    const named = failed.map(r => '  [' + r.status + '] ' + r.source + (r.reason ? ' — ' + r.reason : '')).join('\n')
    return await bail(failed.length + ' source(s) did not convert; the run must not proceed with a hole in ' +
      'the data:\n' + named + '\n(Encrypted files escalate as blocked-environment — re-run with ' +
      'args.pdfDob=DDMMYYYY / args.pdfName, or provide an unencrypted copy. A no-plugin file must be exported ' +
      'to PDF/CSV. A blocked-environment tool must be installed.)')
  }
  if (catalogued.length)
    log('Step 1: ' + catalogued.length + ' image(s) catalogued but NOT OCR-able in this environment ' +
        '(kept on disk, excluded from extraction): ' + catalogued.map(r => String(r.source).split('/').pop()).join(', '))
  // Build sources[] from the role=document converted records ONLY — a zip (role=container-manifest) never
  // enters sources[]. name = output basename minus .txt (the converter's collision-proof slug).
  // Genome-reference rule: a large raw-genotype file (flagged in rep.genomeRefs) is held OUT of full
  // extraction — dumping a 16MB SNP table just burns context; it stays on disk (extracted/sources/ +
  // _genome-references.txt) as a standing resource the deepen/research steps query at specific rsIDs
  // (steps/step2.md, step5.md). It is a successful conversion, so it never trips the halt-on-failure above.
  const outBase = (r) => String(r.output).split('/').pop()
  // Deterministic disk sniff (authoritative) UNION the convert agent's optional return (belt+suspenders).
  const genomeRefsDisk = await readGenomeRefs(sourcesDir)
  const genomeRefSet = new Set([...(Array.isArray(rep.genomeRefs) ? rep.genomeRefs : []), ...genomeRefsDisk].map(String))
  const isGenomeRef = (r) => genomeRefSet.has(outBase(r))
  const heldRefs = rep.records.filter(r => r.status === 'converted' && r.role === 'document' && r.output && isGenomeRef(r))
  const docs = rep.records.filter(r => r.status === 'converted' && r.role === 'document' && r.output && !isGenomeRef(r))
  const extractionSources = docs.map(r => {
    const base = String(r.output).split('/').pop().replace(/\.txt$/, '')
    const s = { name: base, converted: r.output }
    if (r.positions) s.positions = r.positions
    if (r.tool && /OCR/i.test(r.tool)) s.ocr = true
    // kind routing (Phase-2 wiring): the deterministic stage-1 route. `image` carries the ORIGINAL
    // source path for the dual-vision path to Read. Flags-off, the driver ignores kind (legacy path).
    s.kind = srcKind(r)
    if (s.kind === 'image') s.image = r.source
    return s
  })
  if (heldRefs.length)
    log('Step 1: holding ' + heldRefs.length + ' raw-genetics file(s) OUT of full extraction (kept on disk at ' +
        sourcesDir + '/ + _genome-references.txt as a standing resource for targeted rsID lookup, per ' +
        'steps/step2.md): ' + heldRefs.map(outBase).join(', '))
  if (!extractionSources.length) {
    return await bail('conversion produced no role=document sources to extract' +
      (heldRefs.length ? ' (only raw-genetics reference(s) held for targeted lookup: ' + heldRefs.map(outBase).join(', ') + ')'
                       : ' (only manifests / none)') +
      '. Nothing to investigate under ' + root + '/data.')
  }
  log('Step 1: ' + extractionSources.length + ' document source(s) converted (' +
      ((rep.summary && rep.summary.converted) || extractionSources.length) + '/' +
      ((rep.summary && rep.summary.total) || rep.records.length) + ' incl. manifests' +
      (heldRefs.length ? ', ' + heldRefs.length + ' genetics ref held' : '') + '); invoking extraction.')
  // Invoke the extraction workflow with the RECEIPT-DERIVED sources (one-level nested workflow).
  let ext
  try {
    ext = await workflow('extract-health-data', { root: root, sources: extractionSources, libDir: ATOM_LIB_DIR, verifyLibDir: VERIFY_LIB_DIR, timelineLibDir: TIMELINE_LIB_DIR, timelineSources: TIMELINE_SOURCES, convertLibDir: CONVERT_LIB_DIR,
      // Phase-2 kind-routing flags (default OFF → legacy text path for every kind). Set on the
      // top-level orchestrator args to enable the geom PDF / dual-vision image producers per run.
      useVisionImages: cfg.useVisionImages === true, useGeomExtract: cfg.useGeomExtract === true })
  } catch (e) {
    return await bail('extraction workflow threw: ' + (e && e.message ? e.message : String(e)))
  }
  // AUTHORITATIVE gate = disk truth: the extraction must have produced extracted/spot-check.md.
  await refreshCensus('step-1', 'Prepare · Extract', [at('extracted/spot-check.md')])
  if (!parseCensus(census, [at('extracted/spot-check.md')]).complete) {
    return await bail('extraction ran but extracted/spot-check.md is not present/well-formed on disk ' +
      '(the finish-line accuracy summary). Extraction summary: ' + ((ext && ext.summary) || 'n/a'))
  }
  // A7 — the accuracy gate: read the machine-readable verdict off the spot-check.md just produced and
  // HALT unless clean. SAME predicate as the resume path above (readVerdict on the same file).
  const v = await readVerdict(at('extracted/spot-check.md'))
  if (!v.clean)
    return await bail('extraction ran but its accuracy verdict is NOT clean: ' + verdictReason(v) +
      '. The offer must not be built on flawed extraction data. Fix the source(s), remove ' +
      at('extracted/spot-check.md') + ', and re-run the extraction.')
  return { r: ext }
}

// Step 0 (onboard)
if (stageActive('onboard') && !(await runStep(STEPS.find(s => s.id === '0')))) return { root: cfg.root, halted: true }
if (stopAfter('0')) return smokeReturn('0')
// Step 1 (extract) — CODE-OWNED conversion + receipt-derived extraction (the flip) + A7 accuracy gate.
if (stageActive('extract') && !(await runStep1())) return { root: cfg.root, halted: true }
if (stopAfter('1')) return smokeReturn('1')
// ═══════════ NEW FRONT-HALF — broad generation → integration → disconfirmation → deep research ═══════════
// Replaces the mechanism-graph front-half (old Step 2 mechanism-map / Step 3 blind builders / Step 4
// inventory / Step 4.5 hypothesize / Step 5 cross-check). It produces the SAME downstream contracts the
// unmodified steps read: hypothesis-set.md (`### Hn — <slug>` + candidate slugs), the HYPSET object,
// step5-cross-check.md, the working-truth.md ledger, and research/<hn>-*-{consensus,practitioner}.md
// carrying the interview's `## Differentiating diagnostic questions` section. The disk-truth census stays
// the advance authority; each fan-out is completeness-checked and HALTS (never silently advances) on a
// missing item. (The per-step Haiku semantic-completeness check is wired in a follow-up increment.)

// Cause-family taxonomy used by 2c to SHARD integration (one family per integrator). MUST stay aligned
// with the 11 families the generators sweep in references/steps/step2a.md — a card in a family with no
// shard is a zero-owner and fails assembly. Slug-safe (hyphens, no slashes) since it names files
// (integrated-<family>.md). 2a no longer rotates a single lens per document — every 2a/2b generator
// sweeps the full roster itself, so breadth comes from the sweep, not from doc count.
const LENSES = ['external-exposure', 'infective-organismal', 'immune-mediated', 'neoplastic-proliferative',
  'vascular-circulatory', 'structural-anatomic', 'endocrine-regulatory', 'metabolic-nutritional',
  'iatrogenic-treatment', 'constitutional-genetic', 'psychological-nervous-system']

// Per-step Haiku SEMANTIC-completeness check (decision 3): a cheap agent reads the just-written artifact
// and judges whether the sections the step intends are present, full of reasonable on-point content, and
// not truncated (for an integration artifact, that distinct reasonings were not flattened). Returns true
// if COMPLETE. It is ADVISORY on top of the disk-truth census (which still gates advance) — NOT mechanical
// marker gating. A flake / absent status counts as COMPLETE so a real run never blocks on a checker hiccup.
const haikuComplete = async (artifactRel, whatContains, completeMeans, ph) => {
  const r = await agent(
    '## Completeness check (cheap, semantic) — judge completeness only, not correctness\n\n' +
    'Read `' + at(artifactRel) + '` and follow `' + refPath('haiku-completeness-checker.md') + '`.\n\n' +
    'WHAT THIS STEP SHOULD CONTAIN: ' + whatContains + '\nCOMPLETE means: ' + completeMeans + '\n\n' +
    'Answer EXACTLY `STATUS: COMPLETE` or `STATUS: INCOMPLETE` (+ MISSING <what> if incomplete). ' + RETURN_RULE,
    { label: 'haiku:' + slugify(artifactRel.split('/').pop()), phase: ph, model: 'claude-haiku-4-5-20251001',
      schema: { type: 'object', required: ['status'], properties: { status: { type: 'string' }, missing: { type: 'string' } } } })
  return !r || !/INCOMPLETE/i.test(String(r.status || ''))
}
const HAIKU_RETRIES = 2   // bounded re-runs on an INCOMPLETE verdict before advancing on census truth

// ── Step 2a/2b — BROAD GENERATION. 2a: one generator per extracted document, each through a rotated
//    divergence LENS. 2b: cross-document generators (whole-picture + per symptom-cluster), incl. COMPOUND.
if (stageActive('generate')) {
phase('Hypothesise · Generate')
// There is no document manifest and there are no views to enumerate. The run has ONE cross-source
// artifact — extracted/timeline.md — in which every character is copied from a source by script.
// Nothing chooses which parts of the record to compile, so nothing has to be asked what it chose.
//
// The three view-shaped generators are kept, because three lenses on the same material genuinely
// find different things. What changed is that a lens is now an INSTRUCTION, not a file: each agent
// reads the whole timeline and sweeps it one way. A lens cannot drop what it does not emphasise,
// which is precisely what a compiled view did.
const TIMELINE_REL = 'extracted/timeline.md'
const GEN_LENSES = [
  { slug: 'chronology', lens:
    'Read it as a SEQUENCE. What came before what; what began when something else began; what ' +
    'started after an exposure, a treatment, a move, an illness. Order is your evidence.' },
  { slug: 'measurements', lens:
    'Read it for MEASURED VALUES — labs, imaging, tests, anything with a number or a reference ' +
    'range. What is out of range, what moved, what stayed put, what was never measured. Quote the ' +
    'value and its units exactly as the record states them.' },
  { slug: 'symptoms', lens:
    'Read it for what the PERSON experiences. Each distinct symptom: when it began, how it ' +
    'changed, what it moved with, what it did NOT move with, and whether it is present now. ' +
    'Carry their hedges — "I think", "around", "I can\'t quite remember" — exactly as they said ' +
    'them; a hedge removed is data destroyed.' },
]
const docSlug = (d) => slugify(String(d))
const genRel = (d) => 'hypotheses/2a-' + docSlug(d) + '.md'
const genDocs = cap1(GEN_LENSES.map(g => g.slug))
const lensOf = (d) => (GEN_LENSES.find(g => g.slug === d) || {}).lens || ''
{
  const todo = await resumeTodo(genDocs, genRel, 'gen2a-exist', 'Hypothesise · Generate')
  if (todo.length) {
    await parallel(todo.map(d => () => dispatch(
      '## Step 2a — broad root-cause generation, through ONE lens\n\n' +
      bindRule('steps/step2a.md') + '\n\n' +
      'THE PRESENTATION (read this FIRST — it is what you must explain): `' + at('presentation.md') + '`. The body ' +
      'is ONE system: every candidate must connect to this presentation as a ROOT CAUSE or a SYSTEMIC CONTRIBUTING ' +
      'FACTOR (never explain a finding in isolation, never discard one — trace how it could contribute), using the ' +
      'record as evidence.\n' +
      'YOUR MATERIAL (evidence): `' + at(TIMELINE_REL) + '` — the whole record, every character of it copied from a ' +
      'source. Read it IN FULL. Every block carries an identifier like `TL-S0042`; cite a passage by writing ' +
      '`[[TL-S0042]]` and a script substitutes the exact words, so NEVER retype a quotation.\n' +
      'YOUR LENS: ' + lensOf(d) + '\n' +
      'Follow steps/step2a.md EXACTLY: sweep every one of ' +
      'the 11 cause families (≥1 candidate per family — mandatory, no family skipped), producing AT LEAST 20 ' +
      'genuinely-distinct `### HYP` cards (root cause OR systemic contributing factor), each with CLAIM / ROLE / FAMILY ' +
      '/ a ≥5-step REASONING chain that reaches the presentation / DATA carrying a verbatim `[src:]` cite / LIKELIHOOD. ' +
      'Write `' + at(genRel(d)) + '`. ' +
      (smoke ? SMOKE_RULE + '\n' : '') + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
      { label: 'gen:2a:' + docSlug(d), phase: 'Hypothesise · Generate', schema: WROTE_SCHEMA })))
    await refreshCensus('step-2a', 'Hypothesise · Generate', genDocs.map(d => at(genRel(d))))
  }
  // Verify deterministically (check-exist; hypotheses/2a-* are SUBDIR files the census relay can truncate,
  // which would false-halt a fully-reused resume where the fan-out re-dispatched nothing).
  const missingA = await missingAbs(genDocs.map(d => at(genRel(d))), 'gen2a-verify', 'Hypothesise · Generate')
  if (missingA === null || missingA.length) return await halt('2a', 'Step-2a generation incomplete: missing/ill-formed per-view hypotheses: ' + ((missingA || ['(existence check failed)']).join(', ')))
}
// The 4th generator: ONE agent that reads the record with NO lens at all (same step2a sweep), so it
// can reach roots that only become visible when nothing is being emphasised — including explicit
// compound "X AND Y together" candidates.
const clusters = cap1(['whole-picture'])
const bRel = (cl) => 'hypotheses/2b-' + slugify(cl) + '.md'
{
  const todo = await resumeTodo(clusters, bRel, 'gen2b-exist', 'Hypothesise · Generate')
  if (todo.length) {
    await parallel(todo.map(cl => () => dispatch(
      '## Step 2b — broad root-cause generation across the WHOLE record (no lens)\n\n' +
      bindRule('steps/step2a.md') + '\n\n' +
      'THE PRESENTATION (read this FIRST — it is what you must explain): `' + at('presentation.md') + '`. The body ' +
      'is ONE system: every candidate must connect to this presentation as a ROOT CAUSE or a SYSTEMIC CONTRIBUTING ' +
      'FACTOR (never explain a finding in isolation, never discard one — trace how it could contribute), using the ' +
      'record as evidence.\n' +
      'YOUR MATERIAL (evidence): `' + at(TIMELINE_REL) + '` — this person\'s whole record, every character ' +
      'copied from a source. Read it IN FULL, with no lens: the other three generators each sweep it one ' +
      'way, and your job is what none of those emphasise. Cite a passage as `[[TL-S0042]]`; never retype a ' +
      'quotation.\n\n' +
      'Follow steps/step2a.md EXACTLY (sweep every cause family, ≥1 each, AT LEAST 20 genuinely-distinct ' +
      'root-cause cards, each with a ≥5-step why-chain and a verbatim `[src:]` cite). Because you hold the ' +
      'WHOLE record at once, ALSO surface roots that only become visible across periods and sources, and emit explicit ' +
      '`[COMPOUND]` "X AND Y together" candidates where the data fits a combination. Write `' +
      at(bRel(cl)) + '`. ' + (smoke ? SMOKE_RULE + '\n' : '') + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
      { label: 'gen:2b:' + slugify(cl), phase: 'Hypothesise · Generate', schema: WROTE_SCHEMA })))
    await refreshCensus('step-2b', 'Hypothesise · Generate', clusters.map(cl => at(bRel(cl))))
  }
  // Deterministic verify (check-exist; hypotheses/2b-* are SUBDIR files, census-truncation-vulnerable).
  const missingBb = await missingAbs(clusters.map(cl => at(bRel(cl))), 'gen2b-verify', 'Hypothesise · Generate')
  if (missingBb === null || missingBb.length) return await halt('2b', 'Step-2b generation incomplete: missing/ill-formed whole-picture hypotheses: ' + ((missingBb || ['(existence check failed)']).join(', ')))
}
}  // end stageActive('generate')
if (stopAfter('2') || stopAfter('2b')) return smokeReturn('2b')

// ── Step 2c — INTEGRATION sharded by cause-family (DO NOT FLATTEN; carry each source REASONING
//    verbatim), then assemble the downstream hypothesis-set.md contract + return the HYPSET.
if (stageActive('integrate')) {
phase('Hypothesise · Integrate')
const FAMILIES = LENSES   // integration shards by the SAME 11-family taxonomy the generators sweep
const cRel = (fam) => 'hypotheses/integrated-' + fam + '.md'
{
  const fams = cap1(FAMILIES)
  const famAbs = fams.map(f => at(cRel(f)))
  // Which family integrations are already on disk? Decide with the DETERMINISTIC existence check
  // (check-exist.py over these 11 KNOWN paths), NOT the full census. The census walks the whole run tree and
  // its large artifact list is relayed by an agent that intermittently TRUNCATES it (dropping the
  // hypotheses/ files); on a slice that made isDone() false for every family and the fan-out re-integrated
  // all 11 — overwriting/corrupting the reused corpus (what the plan's settled decision forbids, and what a
  // live run did). check-exist.py returns a tiny fixed-size `missing`, immune to that truncation.
  // A fresh (non-resume, non-slice) run always (re)integrates; a resume/slice reuses whatever exists.
  let todo = fams
  if (resuming) {
    const miss = await missingAbs(famAbs, 'integrate-exist', 'Hypothesise · Integrate')
    if (miss === null)
      return await halt('2c', 'could not verify the family integrations on disk (existence check failed) — ' +
        'refusing to blindly re-integrate, which would overwrite the family files. Resolve and retry.')
    const missSet = new Set(miss)
    todo = fams.filter(f => missSet.has(at(cRel(f))))
  }
  if (todo.length) {
    await parallel(todo.map(fam => () => dispatch(
      '## Step 2c — integrate ONE cause-family (DO NOT FLATTEN; carry each source REASONING verbatim)\n\n' +
      bindRule('steps/step2c.md') + '\n\n' +
      'YOUR FAMILY: ' + fam + '. Read every `### HYP` card in `' + at('hypotheses') + '/` whose PRIMARY family ' +
      'is this one, and merge per steps/step2c.md. A card belongs to the family named FIRST in its `FAMILY:` ' +
      'tag (ignore any parenthetical "touches …" secondaries), matched by meaning not exact spelling ' +
      '(e.g. this shard "' + fam + '" claims cards tagged the equivalent slash form). KEEP each card\'s ROLE: ' +
      'ROOT-cause cards merge into `### HYP H<n>` entries; CONTRIBUTING-FACTOR cards merge into `### CF<n>` ' +
      'entries (with a FEEDS: line naming the root they contribute to) — never merge a contributing factor ' +
      'into a root or promote it. Identity = same-root AND same-test; when unsure keep separate; copy each ' +
      'source REASONING line verbatim — a dropped rationale FAILS. Every card lands in exactly ONE entry. ' +
      'Write `' + at(cRel(fam)) + '`. ' +
      (smoke ? SMOKE_RULE + '\n' : '') + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
      { label: 'gen:2c:' + fam, phase: 'Hypothesise · Integrate', schema: WROTE_SCHEMA })))
    await refreshCensus('step-2c', 'Hypothesise · Integrate', famAbs)
  }
  // Fail-closed post-check — DETERMINISTIC (check-exist.py; no census, no truncation): every family file
  // must now be present and non-empty, whether it was reused or freshly (re)integrated.
  const missingC = await missingAbs(famAbs, 'integrate-exist-verify', 'Hypothesise · Integrate')
  if (missingC === null || missingC.length)
    return await halt('2c', 'Step-2c integration incomplete: missing/ill-formed family files: ' +
      ((missingC || ['(existence check failed)']).join(', ')))
}
}  // end stageActive('integrate') — the 2c family fan-out (the derivation below ALWAYS runs from disk)
// Assemble the integrated ledger → hypothesis-set.md (pinned `### Hn — <slug>` + candidate slugs +
// [null]/[safety]) and return the HYPSET the loop needs. When integrate is active and not already on disk,
// WRITE it; otherwise (a resume, or integrate before startAt) re-parse the existing file (read-only) so the
// derivation below still has the candidate slugs — the disk-authoritative hypSet re-derivation is unconditional.
// Rebuild the hypothesis set whenever the integrate stage is active — EXCEPT on a genuine resume
// (cfg.resumeFrom) where the file already exists (idempotent resume). A sliced startAt:'integrate' is an
// explicit request to (re)assemble, NOT a resume, so it must rebuild over the current generators rather
// than re-parse a stale hypothesis-set.md left from an earlier run.
if (stageActive('integrate') && !(cfg.resumeFrom && isDone('hypothesis-set.md'))) {
  // DETERMINISTIC assembler (assemble-hypset.py) — NOT a free-form LLM step. It parses every
  // integrated-*.md, renumbers roots as `### Hn — <slug>`, buckets every CF verbatim, emits the null +
  // safety blocks, enforces anti-flatten + a grounding self-check IN CODE, and WRITES hypothesis-set.md
  // itself (overwrite). No LLM in the writing path → the compose-hang + silent-no-op failure class is
  // gone, and because it rewrites the file wholesale every run a leftover stale file cannot survive.
  // The bash-gate ALLOWS this named `python3 …assemble-hypset.py --out …/hypothesis-set.md` (a read ARG,
  // not an inline `>`/`tee`/`cp`/`sed -i` redirect); write-check is Write/Edit-tool-only, so it never
  // fires on the helper's internal write.
  //
  // The bounded LLM JUDGE (the ONE cross-family semantic call) runs first and returns ONLY the
  // merge/move/safety instruction map — it writes NO file and composes no prose. Its map is threaded to
  // the assembler inline as base64 (the sandboxed driver cannot write a temp file, and base64 survives
  // shell quoting even when a safety reason carries an apostrophe). A dead/empty judge → empty map →
  // identity assembly (the Phase-1 behaviour), so the assembler is never blocked on the judge.
  const judge = await agent(
    '## Step 2c judge — cross-family SAME-ROOT + safety instructions ONLY (compose NO document)\n\n' +
    'Read every `' + at('hypotheses') + '/integrated-*.md`. Return ONLY a bounded instruction map for the ' +
    'deterministic assembler — you write NO file and compose no prose.\n' +
    '- merges: groups of roots (each `{family, id}`, id like `H<n>`) that are the SAME underlying root AND ' +
    'would be confirmed/treated by the SAME test/intervention. A different root, or the same downstream ' +
    'label reached by a DIFFERENT confirming test, is DISTINCT — keep separate. When unsure, keep separate.\n' +
    '- moves: `{family, id, to: "root"|"contributing"}` for an entry that sits in the wrong place (rare).\n' +
    '- safety: any dangerous-to-miss must-exclude as `{slug, reason, src}` (a real `[src:]` citation).\n' +
    '- nullSlug: a short slug for the parallel-null block.\n' +
    'Return {merges, moves, safety, nullSlug}. Merge only across roots you actually read; never invent an id. ' +
    RETURN_RULE + ' Structured output only.',
    { label: 'step:integrate:judge', phase: 'Hypothesise · Integrate', schema: JUDGE_SCHEMA })
  const instrB64 = b64FromString(JSON.stringify({
    merges: (judge && Array.isArray(judge.merges)) ? judge.merges : [],
    moves: (judge && Array.isArray(judge.moves)) ? judge.moves : [],
    safety: (judge && Array.isArray(judge.safety)) ? judge.safety : [],
    nullSlug: (judge && judge.nullSlug) || '',
  }))
  const assembleBash =
    'python3 "' + INTEGRATE_LIB_DIR + '/assemble-hypset.py"' +
    ' --integrated-dir "' + at('hypotheses') + '"' +
    ' --out "' + at('hypothesis-set.md') + '"' +
    ' --cards-dir "' + at('hypotheses/cards') + '"' +   // one standalone card per root, so each disconfirmer reads ONLY its own
    ' --index "' + at('extracted/index.md') + '"' +
    ' --grounding-lib ' + hookScript('lib/investigate-grounding-anchor.py') +
    ' --instructions-b64 ' + instrB64 +
    ' --json'
  const asm = await trusted(
    'Step 2c assembly — deterministic collate of the family files → hypothesis-set.md',
    assembleBash, ASSEMBLE_SCHEMA, 'step:integrate:assemble', 'Hypothesise · Integrate')
  // HALT on the assembler's own verdict FIRST — never fall back to isDone on a possibly-stale file. A
  // non-zero exit / anti-flatten / grounding failure prints ranSuccessfully:false; the file was NOT
  // written (atomic), so a leftover stale file must NOT let the run continue (the original silent-stale bug).
  if (!asm || asm.ranSuccessfully === false)
    return await halt('2c', 'deterministic assembler FAILED (exit non-zero / anti-flatten / grounding) — ' +
      'NOT falling back to a stale hypothesis-set.md. ' + ((asm && asm.note) || '') +
      ' Fix the family files or the instruction map and re-run integrate.')
  // Confirm the write landed with the DETERMINISTIC existence check (check-exist.py), not the census
  // artifact list (which the relaying agent can truncate → a false "not on disk" halt after a good write).
  const missHS = await missingAbs([at('hypothesis-set.md')], 'integrate-exist-hs', 'Hypothesise · Integrate')
  if (missHS === null || missHS.length)
    return await halt('2c', 'hypothesis-set.md not on disk after the deterministic assembly (existence check).')
  // Refresh the census so census.parsed (the pinned `### Hn` set) drives the hypSet derivation below.
  await refreshCensus('step-integrate', 'Hypothesise · Integrate')
} else {
  log('resume/slice: recovering the hypothesis set from the existing hypothesis-set.md via the census (disk authority).')
  await refreshCensus('step-integrate-resume', 'Hypothesise · Integrate')
}
// The deterministic assembler produces NO candidate sub-slugs (those were an LLM-head artifact never
// persisted to disk); census.parsed — parsed from the pinned `### Hn` headings the assembler wrote — is
// the sole authority for the set, and Phase-B deep-dives once per root via the [slug] fallback below.
cfg.__hyp = null
// Re-derive the hypothesis set from disk via the census-backed parser so a truncated schema list can't
// shrink the Phase-B loop (full-chain-over-every-hypothesis). census.parsed (from the pinned `### Hn`
// headings) is AUTHORITATIVE for the set + null/safety flags; the agent return is demoted to supplying
// candidate slugs + any leading flag, merged in by id.
const agentHyp = (cfg.__hyp && Array.isArray(cfg.__hyp.hypotheses)) ? cfg.__hyp.hypotheses : []
const parsedHyp = (census && census.parsed && Array.isArray(census.parsed.hypotheses)) ? census.parsed.hypotheses : null
let hypSet
if (parsedHyp && parsedHyp.length) {
  const byId = {}
  for (const a of agentHyp) if (a && a.id) byId[String(a.id).toUpperCase()] = a
  hypSet = parsedHyp.map(p => {
    const a = byId[String(p.id).toUpperCase()] || {}
    // Census is authoritative for {id,slug,isNull,isSafety}; the agent supplies candidate slugs ONLY.
    // Its `leading` flag is deliberately NOT carried — it is partial/unreliable (the agent only flagged
    // the subset it reported), so leading falls to the deterministic first-N-of-the-disk-set below. That
    // is what makes an under-reporting agent unable to shrink the deep-dive.
    return { id: p.id, slug: p.slug || a.slug || p.id, isNull: !!p.isNull, isSafety: !!p.isSafety,
             candidates: Array.isArray(a.candidates) ? a.candidates : [] }
  })
  log('Hypothesis set from census (disk authority): ' + hypSet.length + ' vs agent-reported ' + agentHyp.length + '.')
} else if (parsedHyp && parsedHyp.length === 0) {
  // Zero-parse guard (RT-rollback-3): the census emitted a `parsed` block but found ZERO pinned `### Hn`
  // headings. After a successful deterministic assemble this is impossible (the parallel-null block is
  // itself an `### Hn`), so a zero-parse means the file on disk is absent / stale / malformed. Shipping
  // would silently truncate to a zero-hypothesis investigation — HALT loudly rather than proceed on nothing.
  return await halt('4.5', 'hypothesis-set.md parsed to ZERO pinned `### Hn — <slug>` headings (absent, ' +
    'stale, or malformed on disk). A successful assembly always emits at least the parallel-null `### Hn`. ' +
    'Re-run the integrate stage so the deterministic assembler rewrites the file, then resume.')
} else {
  hypSet = agentHyp   // backward-compat: an older census with no `parsed` field at all (parsedHyp === null)
}
const nonNull = hypSet.filter(h => h && !h.isNull && !h.isSafety && h.id)
// Leading = flagged leading, else the first N (deterministic); every leading Hn runs the FULL loop.
let leading = nonNull.filter(h => h.leading)
if (!leading.length) leading = nonNull.slice(0, leadingLimit)
leading = cap1(leading)   // SMOKE: one leading hypothesis runs the full Phase-B loop
log('Hypotheses: ' + hypSet.length + ' total, ' + nonNull.length + ' non-null; ' + leading.length +
    ' leading run the full Phase-B loop (' + leading.map(h => h.id).join(', ') + ').')
if (stopAfter('integrate')) return smokeReturn('integrate', { hypotheses: hypSet.map(h => h.id), leading: leading.map(h => h.id) })

// ── Step 3 — DISCONFIRMATION (per hypothesis; parking is provisional & reversible) → the per-candidate
//    evidence-tier ledger step5-cross-check.md + the working-truth.md seed. A separate adversarial reframe
//    re-checks each parked-provisional hypothesis. Smoke skips the fan-out (the cheap plumbing lane).
if (stageActive('disconfirm') && !smoke && nonNull.length && !isDone('selection.md')) {
  phase('Hypothesise · Disconfirm')
  const dRel = (h) => 'disconfirm/' + String(h.id).toLowerCase() + '.md'
  const cardRel = (h) => 'hypotheses/cards/' + h.id + '.md'   // the ONE card the assembler wrote for this root
  const famSlug = (s) => (String(s || 'grp').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 28) || 'grp')
  // Batch the disconfirm fan-out by CAUSE-FAMILY: one skeptic per family reads the person's compiled data ONCE
  // and verdicts that family's roots — each INDEPENDENTLY (no ranking, no cross-standing) — instead of ~43 agents
  // each re-reading the full data. Same-family roots cite overlapping data; the only cross-link allowed is the
  // co-cause CONTESTED-BY note. Grouping is the assembler's `_families.json`, parsed read-only (the sandboxed
  // driver can't read disk); a missing/empty manifest degrades to one group per root (== per-root behaviour).
  const byId = new Map(nonNull.map(h => [String(h.id).toUpperCase(), h]))
  const fam = await agent(
    '## Parse the family grouping (read-only)\n\n' +
    'Read `' + at('hypotheses/cards/_families.json') + '` and return `groups`: its list of {family, ids} ' +
    'verbatim (ids as written). Do NOT write or modify any file — parsing only. ' + RETURN_RULE + ' Structured output only.',
    { label: 'parse-families', phase: 'Hypothesise · Disconfirm', schema: FAMILIES_SCHEMA })
  let groups = ((fam && Array.isArray(fam.groups)) ? fam.groups : [])
    .map(g => ({ family: String(g.family || ''), hs: (Array.isArray(g.ids) ? g.ids : []).map(x => byId.get(String(x).toUpperCase())).filter(Boolean) }))
    .filter(g => g.hs.length)
  const grouped = new Set(groups.flatMap(g => g.hs.map(h => String(h.id).toUpperCase())))
  const strays = nonNull.filter(h => !grouped.has(String(h.id).toUpperCase()))
  if (strays.length) groups = groups.concat(strays.map(h => ({ family: (h.slug || h.id), hs: [h] })))
  log('Disconfirm: ' + nonNull.length + ' roots in ' + groups.length + ' family batches (' +
      groups.map(g => famSlug(g.family) + ':' + g.hs.length).join(', ') + ').')
  // Resume-aware: dispatch a family only if any of its roots' disconfirm files are missing (fresh run = all).
  const missPre = resuming ? await missingAbs(nonNull.map(h => at(dRel(h))), 'disconfirm-exist', 'Hypothesise · Disconfirm') : null
  if (resuming && missPre === null) return await halt('3', 'Step-3 disconfirm existence pre-check failed on resume.')
  const missSet = new Set((missPre || nonNull.map(h => at(dRel(h)))).map(String))
  const djobs = groups.filter(g => g.hs.some(h => missSet.has(at(dRel(h))))).map(g => () => dispatch(
    '## Step 3 — disconfirm the ' + (g.family || 'unnamed') + ' family (' + g.hs.length + ' hypotheses)\n\n' +
    bindRule('steps/step3-disconfirm.md') + '\n\n' +
    'You are a skeptic. For EACH hypothesis below, INDEPENDENTLY try to KILL it with the person\'s own data. ' +
    'Verdict each one on its own merits — do NOT rank them, do NOT compare which is stronger, and do NOT let one ' +
    'hypothesis\'s standing change another\'s. They are related (one cause-family) and may cite overlapping data; ' +
    'the ONLY cross-link you may draw is the co-cause note — a datum that seems to refute one may be owned by ' +
    'another, recorded as CONTESTED-BY.\n' +
    'YOUR HYPOTHESES (read each card; nothing else from the set):\n' +
    g.hs.map(h => '  - ' + h.id + ' (' + (h.slug || '') + '): `' + at(cardRel(h)) + '`').join('\n') + '\n' +
    'THE EVIDENCE (the person\'s compiled data): the cross-source views under `' + at('extracted/compiled') + '/`.\n\n' +
    'Per steps/step3-disconfirm.md, for each hypothesis: it dies ONLY if a finding it REQUIRES is confirmed absent ' +
    '(within a test whose aperture could see it — fail OPEN on an unknown aperture) or a finding is PRESENT it ' +
    'cannot produce. SILENCE IS NOT REFUTATION: never demote on a gap. Sanity-check its grounding + timing (a real ' +
    'symptom ONSET, not a diagnosis date). Verdict — STANDING: survives | parked; REASON (the exact datum if ' +
    'parked); CONTESTED-BY. Do NOT rank or label anything "leading". Parking is provisional. Write ' +
    g.hs.map(h => '`' + at(dRel(h)) + '`').join(', ') + ' — one file per hypothesis (each its own verdict). ' +
    SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'disconfirm:' + famSlug(g.family), phase: 'Hypothesise · Disconfirm', schema: WROTE_SCHEMA }))
  if (djobs.length) { await parallel(djobs); await refreshCensus('step-3-disconfirm', 'Hypothesise · Disconfirm', nonNull.map(h => at(dRel(h)))) }
  // Deterministic verify (check-exist; disconfirm/* are SUBDIR files, census-truncation-vulnerable — a
  // fully-reused resume re-dispatches nothing, so a truncated census would false-halt here).
  const missingD = await missingAbs(nonNull.map(h => at(dRel(h))), 'disconfirm-verify', 'Hypothesise · Disconfirm')
  if (missingD === null || missingD.length) return await halt('3', 'Step-3 disconfirmation incomplete: missing/ill-formed disconfirm files: ' + ((missingD || ['(existence check failed)']).join(', ')))
  // Separate adversarial reframe, batched by family (a DIFFERENT agent from the family's parker; if it finds a
  // subtype/co-cause/aperture the parker missed, that root's standing reverts to survives — each judged alone).
  await parallel(groups.map(g => () => dispatch(
    '## Step 3 adversarial reframe — the ' + (g.family || 'unnamed') + ' family\n\n' +
    bindRule('steps/step3-disconfirm.md') + '\n\n' +
    'You are a DIFFERENT agent from the parker. For EACH hypothesis below that is PARKED, give the strongest case ' +
    'it was parked myopically — a subtype, a less obvious form, a co-cause context, or an aperture the parker ' +
    'missed; if you find one, note that its standing should revert to survives, appended to that hypothesis\'s ' +
    'file. Skip any that are not parked. Judge each INDEPENDENTLY — do not rank or compare.\n' +
    g.hs.map(h => '  - ' + h.id + ': `' + at(dRel(h)) + '`').join('\n') + '\n' +
    SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'reframe:' + famSlug(g.family), phase: 'Hypothesise · Disconfirm', schema: WROTE_SCHEMA })))
  await refreshCensus('step-3-reframe', 'Hypothesise · Disconfirm')
  // Step 3 ends at the per-hypothesis disconfirm/reframe verdicts on disk. The old step5-cross-check
  // evidence-tier ledger (and its working-truth seed) were REMOVED: select reads the disconfirm standings
  // directly, and the per-claim verification that ledger used to hold is carried by the tier+[src:] discipline
  // enforced on every gated file. (working-truth.md remains as its bootstrap stub; its downstream readers are
  // retired stage-by-stage as we reach them.)
}
if (stopAfter('disconfirm')) return smokeReturn('disconfirm')

// ── Step 4a — SELECT: partition in-play (→ deep research) vs parked-provisional (→ the Step-7 reopen pool).
// Split out from Disconfirm above so a `select` slice runs standalone (it reads step5-cross-check.md from disk).
if (stageActive('select') && !smoke && nonNull.length && !isDone('selection.md')) {
  phase('Hypothesise · Select')
  if (cfg.useStructuralSynthesis) {
    // ── STRUCTURAL SYNTHESIS (flag-gated Step-4a replacement): Weaver → reasoning assessor → computed graph.
    // Replaces citation-count ranking (which buried whole causal systems and filled deep research with five
    // views of one story) with connectivity-computed groups; one anchor per DISTINCT group reaches deep
    // research, so the set is diverse by construction. Fail-closed and resume-aware at each sub-step. See
    // HYPOTHESIS-STRUCTURAL-SYNTHESIS-DRAFT-2026-07-21.md + lib/synthesize/CALIBRATION.md.
    const tl = at(TIMELINE_REL), sm = at(TIMELINE_REL)
    // 1. Weaver → weave-map.md (nodes tagged temporal+role; typed edges; rules NOTHING out; over-connects).
    if (!isDone('weave-map.md')) {
      await dispatch(
        '## Step 2d — the Weaver (structural synthesis)\n\n' +
        bindRule('steps/step2d-weave.md') + '\n\n' +
        'READ the integrated hypothesis cards `' + at('hypothesis-set.md') + '` (every `### ` root card — tag ALL of them), ' +
        'the timeline `' + tl + '`, and the symptom matrix `' + sm + '`. One node per card: card `H26` → node `UH26`, ' +
        '`S1` → `US1`. Write `' + at('weave-map.md') + '`. ' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
        { label: 'weave', phase: 'Hypothesise · Select', schema: WROTE_SCHEMA })
      await refreshCensus('step-2d-weave', 'Hypothesise · Select', [at('weave-map.md')])
    }
    const missW = await missingAbs([at('weave-map.md')], 'weave-verify', 'Hypothesise · Select')
    if (missW === null || missW.length) return await halt('4a', 'the Weaver did not write weave-map.md — cannot synthesise groups.')
    // 2. Code mints the canonical edge worklist — the ONE identity site (weave_parse.canonical_edge_id), so
    //    the assessor echoes handles instead of re-deriving ids that could disagree on symmetric edges.
    const worklistBash =
      'python3 "' + SYNTHESIZE_LIB_DIR + '/weave_parse.py" --weave-map "' + at('weave-map.md') + '" --worklist > "' + at('edge-worklist.json') + '"' +
      ' && python3 "' + SYNTHESIZE_LIB_DIR + '/weave_parse.py" --weave-map "' + at('weave-map.md') + '" --json'
    const wpr = await trusted('Structural synthesis — mint the canonical edge worklist',
      worklistBash, WEAVE_PARSE_SCHEMA, 'step:weave-parse', 'Hypothesise · Select')
    if (!wpr || wpr.ranSuccessfully === false)
      return await halt('4a', 'weave_parse FAILED — no edge worklist — ' + ((wpr && wpr.note) || '') + ' (is weave-map.md well-formed?).')
    // 3. Reasoning assessor → assessor-a-grounding.md (a verdict per worklist edge + temporal tag, grounded
    //    ONLY in the person's own record; it scores, never deletes).
    if (!isDone('assessor-a-grounding.md')) {
      await dispatch(
        '## Step 2e — the reasoning assessor (structural synthesis)\n\n' +
        bindRule('steps/step2e-assess.md') + '\n\n' +
        'READ the weaver map `' + at('weave-map.md') + '`, the hypothesis cards `' + at('hypothesis-set.md') + '`, ' +
        'the timeline `' + tl + '` (your primary instrument), and the symptom matrix `' + sm + '`. Score EXACTLY the ids in ' +
        'the code-generated worklist `' + at('edge-worklist.json') + '` — every temporal tag and every edge — echoing each id ' +
        'VERBATIM (never re-derive or invent one). Write `' + at('assessor-a-grounding.md') + '`. ' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
        { label: 'assess', phase: 'Hypothesise · Select', schema: WROTE_SCHEMA })
      await refreshCensus('step-2e-assess', 'Hypothesise · Select', [at('assessor-a-grounding.md')])
    }
    const missA = await missingAbs([at('assessor-a-grounding.md')], 'assess-verify', 'Hypothesise · Select')
    if (missA === null || missA.length) return await halt('4a', 'the reasoning assessor did not write assessor-a-grounding.md — cannot synthesise groups.')
    // 4. Compute the groups → selection.md (parse-selection reads the anchors) + the visible sidecar files.
    const backend = cfg.synthesisBackend || 'modularity'
    const minWeight = (cfg.synthesisMinWeight != null) ? Number(cfg.synthesisMinWeight) : 0.0
    const groupsBash =
      'python3 "' + SYNTHESIZE_LIB_DIR + '/build-groups.py"' +
      ' --weave-map "' + at('weave-map.md') + '"' +
      ' --grounding "' + at('assessor-a-grounding.md') + '"' +
      ' --hypothesis-set "' + at('hypothesis-set.md') + '"' +
      ' --backend ' + backend + ' --min-weight ' + minWeight +
      ' --out-selection "' + at('selection.md') + '"' +
      ' --out-groups-md "' + at('synthesis-groups.md') + '"' +
      ' --out-groups-json "' + at('synthesis-groups.json') + '"' +
      ' --json'
    const gr = await trusted('Structural synthesis — compute groups → selection.md (' + backend + ')',
      groupsBash, BUILD_GROUPS_SCHEMA, 'step:build-groups', 'Hypothesise · Select')
    if (!gr || gr.ranSuccessfully === false)
      return await halt('4a', 'build-groups FAILED — selection.md not written — ' + ((gr && gr.note) || '') + ' (need weave-map.md + assessor-a-grounding.md).')
    log('Structural synthesis: ' + (gr.nGroups || 0) + ' distinct groups from ' + (gr.nNodes || 0) + ' hypotheses (sizes ' +
        JSON.stringify(gr.groupSizes || []) + ', largest ' + Math.round((gr.largestGroupFrac || 0) * 100) + '% of nodes, ' +
        (gr.nEdgesContradicted || 0) + ' edges cut); anchors → deep research: ' + ((gr.groups || []).map(x => x.anchor).join(', ')))
    await refreshCensus('step-4a', 'Hypothesise · Select', [at('selection.md')])
  } else {
    // DETERMINISTIC selector: pick the top-N disconfirmation survivors by how much raw data each quotes among
    // its reasons (a `[src:]`-citation count — a proxy for the fullest evidential picture); the parked (data-
    // refuted) are excluded and everything unselected is carried forward (the reopen pool). No LLM (counting is
    // deterministic) and no dependency on the retired step5-cross-check ledger — it reads the cards + standings.
    const topN = Number(cfg.selectTopN) || 10
    const selectBash =
      'python3 "' + INTEGRATE_LIB_DIR + '/select-top.py"' +
      ' --cards-dir "' + at('hypotheses/cards') + '"' +
      ' --disconfirm-dir "' + at('disconfirm') + '"' +
      ' --top ' + topN +
      ' --out "' + at('selection.md') + '"' +
      ' --json'
    const selr = await trusted(
      'Step 4a selection — deterministic top-' + topN + ' by cited raw data (disconfirmation survivors)',
      selectBash, SELECT_SCHEMA, 'step:select', 'Hypothesise · Select')
    if (!selr || selr.ranSuccessfully === false)
      return await halt('4a', 'deterministic selector FAILED — selection.md not written — ' + ((selr && selr.note) || '') +
        ' (needs hypotheses/cards/_families.json + disconfirm/*.md; re-run integrate → disconfirm, then select).')
    log('Selected top ' + (selr.nTop || 0) + ' of ' + (selr.nSurvivors || 0) + ' survivors for deep research (' +
        (selr.nParked || 0) + ' parked, ' + (selr.nCarried || 0) + ' carried): ' +
        ((selr.top || []).map(t => t.id).join(', ')))
    await refreshCensus('step-4a', 'Hypothesise · Select', [at('selection.md')])
  }
}
if (stopAfter('select')) return smokeReturn('select')

// ── In-play survivors + the deep-research dispatch (SINGLE SOURCE, reused by the sweep-reopen path).
// Research runs ONLY on the disconfirmation survivors (in-play), never on every non-null hypothesis:
// research is onerous, so each candidate is checked against the person's own data first and only the
// non-demoted ones are researched (a parked candidate is set aside, reopenable later by the sweep). The
// standing lives on disk (selection.md); read it via a read-only parse dispatch (modelled on
// resume-parse-hyp). FAIL-CLOSED: if selection.md is absent when research is about to run, HALT — never
// fall back to researching all non-null (the exact expensive behaviour this removes). Smoke skips
// disconfirm/select/research entirely, so inPlaySet stays null there.
let inPlaySet = null
if (stageActive('research') && !smoke && nonNull.length) {
  if (!isDone('selection.md')) await refreshCensus('selection-precheck', 'Hypothesise · Select', [at('selection.md')])
  if (!isDone('selection.md'))
    return await halt('4a', 'selection.md (the disconfirmation survivor list) is not on disk — refusing to research ' +
      'every non-null hypothesis. Re-run disconfirm → select to produce selection.md, then resume.')
  const sel = await agent(
    '## Parse the selection — the deep-research set (read-only)\n\n' +
    'Read `' + at('selection.md') + '` and return, as `inPlay`, the hypothesis ids listed under the ' +
    '"## Deep-research set" heading (the ones selected for deep research). Ignore the "Carried forward" ' +
    'section. Do NOT write or modify any file — parsing only. ' + RETURN_RULE + ' Structured output only.',
    { label: 'parse-selection', phase: 'Hypothesise · Select',
      schema: { type: 'object', required: ['inPlay'], properties: { inPlay: { type: 'array', items: { type: 'string' } } } } })
  inPlaySet = new Set(((sel && Array.isArray(sel.inPlay)) ? sel.inPlay : []).map(x => String(x).toUpperCase()))
  log('In-play survivors (from selection.md): ' + ([...inPlaySet].join(', ') || '(none)') + ' — ' +
    inPlaySet.size + ' of ' + nonNull.length + ' non-null go to deep research.')
  // Phase-B deepens the SELECTED (researched) hypotheses, in selection order — never the first N of the raw
  // hypothesis-set order, which would deep-dive candidates that have no research dossier behind them.
  const researched = [...inPlaySet].map(id => nonNull.find(h => String(h.id).toUpperCase() === id)).filter(Boolean)
  if (researched.length) {
    leading = researched.slice(0, leadingLimit)
    log('Phase-B deep-dive set (top ' + leading.length + ' of the researched selection): ' +
      leading.map(h => h.id).join(', '))
  }
}

// Deep-research dispatch for ONE hypothesis — BOTH engines (consensus + practitioner), each appending the
// 4c `## Differentiating diagnostic questions` section the Step-5.5 interview harvests. Returns the pending
// thunks (skips an engine whose file is already on disk). SINGLE SOURCE used by the survivor research loop
// AND the sweep-reopen on-demand path (a reopened parked hypothesis was never researched).
const researchFileNames = (h) => {
  const hn = String(h.id).toLowerCase(), rslug = slugify(h.slug || h.id)
  return { hn, cFile: 'research/' + hn + '-' + rslug + '-consensus.md', pFile: 'research/' + hn + '-' + rslug + '-practitioner.md' }
}
const researchJobsFor = (h, ph) => {
  const { hn, cFile, pFile } = researchFileNames(h)
  const jobs = []
  if (!isDone(cFile)) jobs.push(() => dispatch(
    '## Step 4b — deep research (CONSENSUS) for hypothesis ' + h.id + ' (' + (h.slug || '') + ')\n\n' +
    bindRule('steps/step4b.md') + '\n\n' +
    'Read `' + at('hypothesis-set.md') + '` for this hypothesis. Do comprehensive consensus research ' +
    '(/research: current literature, guidelines, meta-analyses — use web search) into its FULL shape per ' +
    'steps/step4b.md: all forms/subtypes, per-form features (mechanism + precise location/cell type), the ' +
    'clues/data expected per form, how it blends as one of several things at once, what a standard work-up ' +
    'misses. Then follow steps/step4c.md: append a `## Differentiating diagnostic questions` section (each ' +
    'question with expected-answer-per-hypothesis + qualitative sensitivity + specificity + a person/test ' +
    'tag; drop those the records already answer). Tier + cite every load-bearing claim. Write `' + at(cFile) + '`. ' +
    RETURN_RULE + ' Structured output only.',
    { label: 'research:consensus:' + hn, phase: ph, schema: WROTE_SCHEMA }))
  if (!isDone(pFile)) jobs.push(() => dispatch(
    '## Step 4b — deep research (PRACTITIONER) for hypothesis ' + h.id + ' (' + (h.slug || '') + ')\n\n' +
    bindRule('steps/step4b.md') + '\n\n' +
    'Read `' + at('hypothesis-set.md') + '` for this hypothesis. Do comprehensive practitioner research ' +
    '(/research-practitioner: what experienced clinicians report in real patients — use web search for ' +
    'practitioner writing, case series, clinician discussion) per steps/step4b.md, then follow steps/step4c.md ' +
    'and append a `## Differentiating diagnostic questions` section (expected-answer-per-hypothesis + ' +
    'qualitative sensitivity + specificity + a person/test tag; drop the already-answered). Tier + cite ' +
    'every claim. Write `' + at(pFile) + '`. ' + RETURN_RULE + ' Structured output only.',
    { label: 'research:practitioner:' + hn, phase: ph, schema: WROTE_SCHEMA }))
  return jobs
}
// Resolve a sweep-reopened slug back to a known non-null hypothesis (by id, slug, or a candidate slug) so a
// reopened parked hypothesis can be researched + deepened on demand. Returns undefined for an unmatched slug.
const resolveReopened = (s) => nonNull.find(h =>
  String(h.id).toLowerCase() === s || slugify(h.slug || '') === s ||
  (Array.isArray(h.candidates) && h.candidates.map(slugify).includes(s)))

// ── Step 4b/4c — DEEP RESEARCH per survivor (BOTH engines) + the interview's diagnostic-questions
//    contract. The Step-5.5 harvest requires research/<hn>-*-{consensus,practitioner}.md carrying a
//    `## Differentiating diagnostic questions` section — 4c appends that section into those files.
if (stageActive('research') && !smoke && nonNull.length) {
  phase('Investigate · Research')
  // Research targets = the in-play survivors ONLY (never all non-null). inPlaySet was parsed from
  // selection.md above (with a fail-closed HALT if it was absent), so it is non-null on this path.
  const researchTargets = inPlaySet ? nonNull.filter(h => inPlaySet.has(String(h.id).toUpperCase())) : []
  const rjobs = researchTargets.flatMap(h => researchJobsFor(h, 'Investigate · Research'))
  if (rjobs.length) {
    log('Step-4b/4c paired research: dispatching ' + rjobs.length + ' research agents across ' +
      researchTargets.length + ' in-play survivors (of ' + nonNull.length + ' non-null).')
    await parallel(rjobs)
    await refreshCensus('step-4b-research', 'Investigate · Research')
  }
}
if (stopAfter('research')) return smokeReturn('research')

// ── Step 5.5 — Interview: the ONE interactive handoff in the whole workflow. Workflows cannot take
//    mid-run input, so the flow runs straight to here, GENERATES the question set (one agent), then
//    PAUSES and hands back to the conversational layer. The human answers (writes interview-answers.md
//    into the run); a resume continues from 5.7. There is NO model-orchestrator anywhere else — this
//    pause is the only break between Step 1 and the finish-line offer.
if (stageActive('interview')) {
phase('Investigate · Interview')
const interviewStep = STEPS.find(s => s.id === '5.5')
const answersFile = at('interview-answers.md')
if (!parseCensus(census, [answersFile]).complete) {
  if (!(cfg.resumeFrom && isDone('question-bank.md'))) {
    await dispatch(dispatchPrompt(interviewStep), { label: 'step:5.5', phase: 'Investigate · Interview', schema: WROTE_SCHEMA })
    await refreshCensus('step-5.5', 'Investigate · Interview')
    if (!isDone('question-bank.md')) return await halt('5.5', 'question-bank.md not produced by the interview step.')
  }
  log('Interview questions ready — PAUSING for the subject to answer, then resume.')
  return {
    root: cfg.root, halted: false, paused: 'interview',
    questionBank: at('question-bank.md'), answersExpectedAt: answersFile,
    note: 'Workflow paused at the Step-5.5 interview (the only interactive handoff). Present the ' +
          'questions in question-bank.md to the subject; write their answers to interview-answers.md; ' +
          'then resume with resumeFrom set — the flow continues 5.7 → Phase-B → 6 → offer with no ' +
          'orchestrator in between.',
  }
}
log('Interview answers present (interview-answers.md) — continuing past 5.5 without a pause.')
}
if (stopAfter('interview')) return smokeReturn('interview')

// Step 5.7 (coherence).
if (stageActive('cohere') && !(await runStep(STEPS.find(s => s.id === '5.7')))) return { root: cfg.root, halted: true }
if (stopAfter('cohere')) return smokeReturn('cohere')

// ───────────────────────── Phase B (5.8 → 5.14) over EVERY leading hypothesis ─────────────────────────
// pipeline() runs each hypothesis through B1→B2→B3 independently (no barrier); then a genuine barrier
// for the single cross-hypothesis system-integration + connection-plausibility; then per-Hn convergence.
if (stageActive('deepen')) {
phase('Model · Deepen')
const sub = (name) => PHASE_B_SUBSTEPS.find(s => s.name === name)
const phaseBWrite = (subStep, hn, candidate) => {
  const out = subStep.outPattern.replace('<Hn>', hn).replace('<candidate>', slugify(candidate))
  return '## Phase-B ' + subStep.code + ' (' + subStep.id + ') — ' + subStep.name +
    (candidate ? ' for candidate: ' + candidate : ' for hypothesis: ' + hn) + '\n\n' +
    bindRule(subStep.ref) + '\n\n' +
    (subStep.needs ? 'Prerequisite (must be on disk / read first): `' + subStep.needs + '`.\n' : '') +
    'Write `' + at(out) + '`. ' + (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.'
}

if (!leading.length) {
  log('WARNING: no leading hypotheses parsed — Phase-B loop skipped; the offer will name why (no deep-dive).')
} else {
  // Fix 3 (Phase 3): per-hypothesis resume — redo ONLY the leading hypotheses whose convergence is not yet
  // on disk (not all-or-nothing). A partial resume completes exactly the unfinished hypotheses.
  const pending = await resumeTodo(leading, h => 'convergence-' + h.id + '.md', 'phaseb-conv-exist', 'Model · Deepen')
  if (!pending.length) {
    log('resume: Phase-B convergence already on disk for all leading hypotheses — skipping Phase-B.')
  } else {
    if (cfg.resumeFrom && pending.length < leading.length)
      log('resume: Phase-B redoing ' + pending.length + ' of ' + leading.length + ' leading hypotheses (rest already converged).')
    // B1 → B2 → B3 per pending hypothesis (B3 fans out per candidate).
    await pipeline(
      pending,
      (h) => dispatch(phaseBWrite(sub('constraints'), h.id), { label: 'B1:' + h.id, phase: 'Model · Deepen', schema: WROTE_SCHEMA }).then(() => h),
      (h) => dispatch(phaseBWrite(sub('shape-profile'), h.id), { label: 'B2:' + h.id, phase: 'Model · Deepen', schema: WROTE_SCHEMA }).then(() => h),
      (h) => {
        const cands = cap1((Array.isArray(h.candidates) && h.candidates.length) ? h.candidates : [h.slug || h.id])
        return parallel(cands.map(c => () =>
          dispatch(phaseBWrite(sub('mechanism-map'), h.id, c), { label: 'B3:' + h.id + '/' + c, phase: 'Model · Deepen', schema: WROTE_SCHEMA }))).then(() => h)
      },
    )
    // Barrier: the single cross-hypothesis integration + plausibility. Re-run whenever ANY hypothesis was
    // (re)done this pass — they must reflect the full mechanism-map set (all pending maps now exist on disk
    // alongside the already-done ones), so a partial resume gets a complete, non-stale integration.
    await dispatch(phaseBWrite(sub('system-integration'), 'all'), { label: 'B5.5:system-integration', phase: 'Model · Deepen', schema: WROTE_SCHEMA })
    await dispatch(phaseBWrite(sub('connection-plausibility'), 'all'), { label: 'B5.6:connection-plausibility', phase: 'Model · Deepen', schema: WROTE_SCHEMA })
    // Per-Hn convergence for the pending hypotheses (each needs its maps + the two single files).
    await parallel(pending.map(h => () =>
      dispatch(phaseBWrite(sub('convergence'), h.id), { label: 'B5:convergence:' + h.id, phase: 'Model · Deepen', schema: WROTE_SCHEMA })))
    await refreshCensus('phaseB', 'Model · Deepen', leading.map(h => at('convergence-' + h.id + '.md')))
  }
  // Full-chain-over-every-hypothesis completeness halt (unchanged): EVERY leading Hn must have its
  // convergence-<Hn>.md on disk well-formed — checked over the whole leading set, not just the pending ones.
  const missingConv = leading.map(h => at('convergence-' + h.id + '.md')).filter(p => !parseCensus(census, [p]).complete)
  if (missingConv.length) return await halt('5.14', 'Phase-B did not converge every leading hypothesis: missing ' + missingConv.join(', '))
}
}  // end stageActive('deepen')
if (stopAfter('5.14') || stopAfter('phaseB')) return smokeReturn('5.14', { convergence: leading.map(h => at('convergence-' + h.id + '.md')) })

// Step 6 (prioritize) + per-Hn reverse-engineered responses (B7).
if (stageActive('prioritize') && !(await runStep(STEPS.find(s => s.id === '6')))) return { root: cfg.root, halted: true }
// Legacy '6' stop is MID-stage (right after step6-prioritize.md, BEFORE B7) — matched raw so a full
// `prioritize` stage stop (which must include the B7 responses below) is not swallowed here.
if (cfg.stopAfter === '6') return smokeReturn('6', { stepArtifact: at('step6-prioritize.md') })
// B7 responses — one per leading hypothesis. Fix 3 (Phase 3): per-item resume (redo only the missing) +
// completeness halt (every leading Hn must have its responses file on disk).
if (stageActive('prioritize') && leading.length) {
  const pendingR = await resumeTodo(leading, h => 'responses-mechanism-' + h.id + '.md', 'phaseb-resp-exist', 'Model · Deepen')
  if (pendingR.length) {
    await parallel(pendingR.map(h => () =>
      dispatch(
        '## Step 6 / B7 — reverse-engineered responses (mechanism) for hypothesis: ' + h.id + '\n\n' +
        bindRule('prioritizer.md') + '\n\n' +
        'Write `' + at('responses-mechanism-' + h.id + '.md') + '` (## Winners / ## Neutrals / ## Worseners / ' +
        '## Failures, each tied to a node or flagged as a hole). ' + (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' +
        RETURN_RULE + ' Structured output only.',
        { label: 'B7:responses:' + h.id, phase: 'Model · Prioritize', schema: WROTE_SCHEMA })))
    await refreshCensus('b7-responses', 'Model · Prioritize', leading.map(h => at('responses-mechanism-' + h.id + '.md')))
  }
  const missingR = leading.map(h => at('responses-mechanism-' + h.id + '.md')).filter(p => !parseCensus(census, [p]).complete)
  if (missingR.length) return await halt('6', 'B7 responses incomplete: missing reverse-engineered response sheet(s): ' + missingR.join(', '))
}
if (stopAfter('prioritize')) return smokeReturn('prioritize')

// ───────────────────────── Step 7 — SWEEP-CHECK (one loop) → reopen + on-demand deepening ─────────────
// Go back to ALL original data one datum at a time against the current picture (the deepening
// mechanism-maps). Reconcile UNEXPLAINED and CONTESTED; a reopen with no map triggers an on-demand
// deepening pass (build its mechanism-map) BEFORE Step 8 / the offer. One loop; still-unexplained flagged.
// `sweep` + `reopenNeedingMap` are declared OUTSIDE the stage guard — the intervene stage below consumes
// reopenNeedingMap, so a slice that skips the sweep sees the empty defaults (no reopens), not undefined.
let sweep = { reopened: [], stillUnexplained: [] }
let reopenNeedingMap = []
if (stageActive('sweep')) {
phase('Model · Sweep')
if (!(cfg.resumeFrom && isDone('sweep-check.md'))) {
  const sw = await dispatch(
    '## Step 7 — sweep-check: every original datum against the current picture (ONE loop)\n\n' +
    bindRule('steps/step7-sweep.md') + '\n\n' +
    'Read every compiled datum, the leading/in-play hypotheses with their deepening mechanism-maps ' +
    '(`mechanism-map-<slug>.md`), and the parked-provisional set + its CONTESTED-BY data. Per datum give a ' +
    'MATCH verdict {explained | partial | UNEXPLAINED} citing the chain node; RECONCILE unexplained-and-' +
    'load-bearing AND contested data against the parked pool (a fit → REOPEN); ONE loop; still-UNEXPLAINED ' +
    'data → still_unexplained[]. Write `' + at('sweep-check.md') + '`. Return { done, reopened: ' +
    '[<hypothesis-slug>...], stillUnexplained: [<datum>...] }. ' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'step:sweep', phase: 'Model · Sweep', schema: {
      type: 'object', required: ['done'],
      properties: { done: { type: 'boolean' }, promptBindSha: { type: 'string' },
        reopened: { type: 'array', items: { type: 'string' } },
        stillUnexplained: { type: 'array', items: { type: 'string' } } } } })
  await refreshCensus('step-7-sweep', 'Model · Sweep', [at('sweep-check.md')])
  if (!isDone('sweep-check.md')) return await halt('7', 'sweep-check.md not on disk well-formed after the sweep.')
  sweep = { reopened: Array.isArray(sw && sw.reopened) ? sw.reopened : [],
            stillUnexplained: Array.isArray(sw && sw.stillUnexplained) ? sw.stillUnexplained : [] }
}
// On-demand RESEARCH for a reopened parked hypothesis: it was parked before Select, so it was never
// in-play and has NO deep-research files. Dispatch 4b/4c NOW — before the on-demand deepening below and
// before the offer consumes it — else it would reach the write-up with a mechanism sketch but no evidence.
// (Keyed to a known non-null hypothesis by resolveReopened; an unmatched reopen slug gets only a map.)
{
  // BOUNDED. The sweep can reopen many hypotheses at once (6 on a real run), and each costs a PAIR of
  // heavy web-research agents — 12 in one parallel block, which is where a real run crashed: the back half
  // did the work and then failed to emit structured output. Cap the reopen research the same way Step 8
  // caps nodes; the uncapped remainder stays reopened and carried, just not researched this pass.
  const reopenCap = Number(cfg.reopenResearchCap) || 4
  const allReopenSlugs = [...new Set(sweep.reopened.map(slugify).filter(Boolean))]
  const reopenSlugs = allReopenSlugs.slice(0, reopenCap)
  const deferredReopen = allReopenSlugs.slice(reopenCap)
  if (deferredReopen.length) {
    log('Sweep reopened ' + allReopenSlugs.length + ' hypotheses; researching the first ' + reopenCap +
      ' this pass. DEFERRED (reopened + carried, not researched): ' + deferredReopen.join(', ') +
      ' — the offer must name these as reopened-but-not-yet-researched rather than imply they were covered.')
  }
  const reopenResearch = []
  for (const s of reopenSlugs) {
    const h = resolveReopened(s)
    if (h) reopenResearch.push(...researchJobsFor(h, 'Model · Sweep'))
  }
  if (reopenResearch.length) {
    log('Sweep-reopened hypothesis(es) were parked before Select and never researched — on-demand 4b/4c ' +
      'research (' + reopenResearch.length + ' file(s)) BEFORE the on-demand deepening.')
    await parallel(reopenResearch)
    await refreshCensus('reopen-research', 'Model · Sweep')
  }
}
// On-demand deepening: a REOPENED hypothesis was never selected for deepening, so it has NO mechanism-map
// — build it now (the unchanged deepening step) BEFORE Step 8 / the offer can consume it. Until the map
// exists the reconciler treats the reopened hypothesis as validly-owned (deepening-pending), not a FAIL.
reopenNeedingMap = sweep.reopened.map(slugify).filter(s => s && !isDone('mechanism-map-' + s + '.md'))
if (reopenNeedingMap.length) {
  log('Sweep reopened ' + reopenNeedingMap.length + ' hypothesis(es) with no mechanism-map — on-demand deepening.')
  await parallel(reopenNeedingMap.map(s => () =>
    dispatch(
      '## On-demand deepening — build the mechanism-map for a reopened candidate: ' + s + '\n\n' +
      bindRule('steps/step5.10.md') + '\n\n' +
      'This candidate was REOPENED at the sweep and has no mechanism-map yet. Write `' +
      at('mechanism-map-' + s + '.md') + '` per steps/step5.10.md (resolved nodes + tiered edges) so Step 8 ' +
      'and the offer can consume it. ' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
      { label: 'deepen:reopen:' + s, phase: 'Model · Sweep', schema: WROTE_SCHEMA })))
  await refreshCensus('reopen-deepen', 'Model · Sweep', reopenNeedingMap.map(s => at('mechanism-map-' + s + '.md')))
  const missingRe = reopenNeedingMap.map(s => at('mechanism-map-' + s + '.md')).filter(p => !parseCensus(census, [p]).complete)
  if (missingRe.length) return await halt('7', 'On-demand deepening for a reopened hypothesis incomplete: missing ' + missingRe.join(', '))
}
}  // end stageActive('sweep')
if (stopAfter('7') || stopAfter('sweep')) return smokeReturn('7')

// ───────────────────────── Step 8 — INTERVENTION research across each deepening mechanism-map ─────────
// One agent per candidate's deepening mechanism-map (the driver has no map-node visibility, so it fans per
// candidate map; each agent walks that map's nodes). Typed levers (or an explicit no-lever line) feed the
// offer §2/§3 router. NOT only drugs/supplements. Includes any reopened candidate now carrying a map.
// Mirror B3's candidate fallback (`[h.slug||h.id]` when candidates is empty) so Step-8 fans over EXACTLY
// the mechanism-maps B3 wrote. The deterministic 2c assembler produces no candidate sub-slugs, so every
// leading root deep-dives once under its own slug; without this fallback mapCandidates would be empty and
// Step-8 would silently orphan the maps B3 built.
const mapCandidates = [...new Set(leading.flatMap(h =>
  ((Array.isArray(h.candidates) && h.candidates.length) ? h.candidates : [h.slug || h.id]).map(slugify)
).concat(reopenNeedingMap))].filter(Boolean)
if (stageActive('intervene') && mapCandidates.length) {
  phase('Model · Intervene')
  const ivRel = (c) => 'interventions-' + c + '.md'
  const pendingIv = await resumeTodo(mapCandidates, ivRel, 'intervene-exist', 'Model · Intervene')
  if (pendingIv.length) {
    // Researching EVERY node across every mechanism map is unbounded (a map can carry dozens) and spends
    // the same effort on a node with no lever as on the one place with real leverage. So a single selector
    // reads all the maps and picks the NODES most worth acting on; intervention research then runs on those.
    const nodeCap = Number(cfg.interveneNodeCap) || 10
    const sel = await agent(
      '## Step 8 prep — choose the ' + nodeCap + ' nodes most worth acting on (read-only)\n\n' +
      'Read every deepening mechanism-map: ' + mapCandidates.map(c => '`' + at('mechanism-map-' + c + '.md') + '`').join(', ') + '.\n' +
      'Enumerate every node across all of them, then choose the **' + nodeCap + ' with the most intervention ' +
      'leverage**. Judge leverage by: (a) the node names real `vulnerabilities` or `persistence-structure` ' +
      'disruptors — something could actually be done there; (b) several arms or symptoms run through it, so ' +
      'moving it moves more than one thing; (c) acting there could plausibly help on a weeks timescale even ' +
      'while the deeper causes persist — an upstream node nobody can act on now is an ORIGIN, not a lever; ' +
      '(d) a cheap, reversible probe of it exists; (e) it serves a high-consequence candidate. Prefer spread ' +
      'across candidates over ' + nodeCap + ' nodes of one map, unless one map genuinely holds all the leverage. ' +
      'Return `nodes`: for each, the candidate slug, the node handle, and one line on why it earned a place. ' +
      'Do NOT write or modify any file — selection only. ' + RETURN_RULE + ' Structured output only.',
      { label: 'intervene:select-nodes', phase: 'Model · Intervene', schema: NODESEL_SCHEMA })
    const picked = ((sel && Array.isArray(sel.nodes)) ? sel.nodes : [])
      .filter(n => n && n.candidate && n.node).slice(0, nodeCap)
    if (!picked.length) return await halt('8', 'Step-8 node selection returned no nodes — refusing to research ' +
      'every node of every map unbounded. Re-run intervene, or set cfg.interveneNodeCap.')
    log('Step-8 nodes selected (' + picked.length + ' of the full node set): ' +
      picked.map(n => n.candidate + '/' + n.node).join(', '))
    // one focused agent per SELECTED node, grouped back into its candidate's lever sheet
    const byCand = new Map()
    for (const n of picked) {
      if (!byCand.has(n.candidate)) byCand.set(n.candidate, [])
      byCand.get(n.candidate).push(n)
    }
    await parallel([...byCand.entries()].filter(([c]) => pendingIv.includes(c)).map(([c, nodes]) => () =>
      dispatch(
        '## Step 8 — intervention research for candidate ' + c + ' (' + nodes.length + ' selected node(s))\n\n' +
        bindRule('steps/step8-intervention.md') + '\n\n' +
        'Read this candidate\'s deepening mechanism-map `' + at('mechanism-map-' + c + '.md') + '`. Research how we ' +
        'could ACT at each of these SELECTED nodes (they were chosen for leverage; do not research the rest):\n' +
        nodes.map(n => '  - ' + n.node + (n.why ? ' — selected because: ' + n.why : '')).join('\n') + '\n\n' +
        'Cover the FULL space of ways to act, and weight them by what would actually help this person — ' +
        '**drugs and supplements are a major part of that and must be researched properly** (agent, form, ' +
        'dose, where it acts, evidence), ALONGSIDE the non-pharmacological levers: diet and eating patterns, ' +
        'breathwork, movement, sleep and circadian timing, stress and nervous-system practices, and clinician ' +
        'procedures. Neither category is the default answer; the node decides which fits. Dispatch BOTH ' +
        '/research and /research-practitioner. Per lever: mechanism-of-correction (cited); type tags ' +
        '[self|clinician][cheap|costly][reversible-harm|not][tier]; program + sequence + read-out window; ' +
        'if-X→then-Y; etiology fit; already-tried check; safety. "No known lever at this node" is a valid, ' +
        'required output — never invent a dose the research does not give. Write `' + at(ivRel(c)) + '`. ' +
        (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
        { label: 'intervene:' + c, phase: 'Model · Intervene', schema: WROTE_SCHEMA })))
    await refreshCensus('step-8-intervene', 'Model · Intervene', mapCandidates.map(c => at(ivRel(c))))
  }
  const missingIv = mapCandidates.map(c => at(ivRel(c))).filter(p => !parseCensus(census, [p]).complete)
  if (missingIv.length) return await halt('8', 'Step-8 intervention incomplete: missing lever sheet(s): ' + missingIv.join(', '))
}
if (stopAfter('8') || stopAfter('intervene')) return smokeReturn('8')

// ───────────────────────── Offer — draft sections, Council, Strip (terminal) ─────────────────────────
// Fix 3 (Phase 3): each offer section is written to its OWN file offer-sections/s<i>.md (so a resume
// redoes only the missing sections — appending to one shared file cannot be made idempotent), then a
// deterministic trusted concat assembles offering-draft.md. The offer EMITTER is unchanged: it parses a
// single draft by headings, so the per-section files concatenated in order produce byte-identical output.
if (stageActive('compose')) {
phase('Share · Compose')
// `recompose` forces the whole section pass to re-run over an existing run: the writers OVERWRITE their
// section files in place (never a delete — nothing may be removed under the run root before the finish
// line). Needed whenever the offer SPECS change, since otherwise every existing section is skipped as
// done and the run silently re-ships prose written against the old spec.
const recompose = cfg.recompose === true
// `replan` additionally redoes the PREP artifacts (glossary, name registry, plan). They are expensive and
// spec-current once written, so a recompose keeps them by default — re-running the section pass after a
// mid-run failure should not throw away the planning that already succeeded.
const replan = cfg.replan === true
if (recompose) log('recompose: rewriting every offer SECTION against the current specs (overwritten in place, nothing deleted)' +
  (replan ? '; replan: the glossary, name registry and plan are rebuilt too.' : '; the existing glossary, name registry and plan are kept — pass replan:true to rebuild them.'))
const sectionDone = (rel) => recompose ? false : isDone(rel)
const prepDone = (rel) => replan ? false : isDone(rel)
if (!recompose && cfg.resumeFrom && isDone('offering-draft.md')) {
  log('resume: offering-draft.md already assembled — skipping the section pass + concat, going to the council.')
} else {
  // Stage-0b — own-words glossary (the person's own words for their experience, injected into every writer).
  if (!prepDone('offer-glossary.md')) await dispatch(
    '## Offer prep (Stage-0b) — own-words glossary\n\n' + bindRule('offer-examples/offer-coordination.md') + '\n\n' +
    'Build the own-words glossary — the person\'s OWN words for their symptoms/experience (from the interview + ' +
    'symptom artifacts) — so every offer writer uses their words, not coined ones. Write `' + at('offer-glossary.md') + '`. ' +
    SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:glossary', phase: 'Share · Compose', schema: WROTE_SCHEMA })
  // Stage-0a — mechanism-name registry. The glossary above translates the SYMPTOM axis (the person's own
  // words); nothing translated the MECHANISM axis, so writers obeyed "use the map's name" and emitted
  // `N14` / `connector B4` into patient prose (2026-07-20 review). This registry gives every node and
  // connection a plain-English name BEFORE any section is written; writers then use the name, never the id.
  // A positive substitution, deliberately not another ban list — the existing four-word ban list failed
  // (`aperture` appeared 43 times in the delivered document).
  if (!prepDone('offer-names.md')) await dispatch(
    '## Offer prep (Stage-0a) — mechanism-name registry\n\n' + bindRule('offer-examples/names.md') + '\n\n' +
    'Read the deepening mechanism-maps (`mechanism-map-*.md`) and `system-integration.md`. For EVERY node and ' +
    'every cross-candidate connection any section will reference, assign a plain-English name a non-expert can ' +
    'read without a glossary, plus a one-line plain description. Record the internal identifier alongside it for ' +
    'the writers\' lookup ONLY — it must never reach client prose. Write `' + at('offer-names.md') + '`. ' +
    SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:names', phase: 'Share · Compose', schema: WROTE_SCHEMA })
  // Stage-0c — the §2/§3 router: partition the UNION of Step-8 levers + Step-4 tests + Step-7 flags into
  // §2 (act-and-learn) vs §3 (test-first), default-to-§3 on ambiguity, deduped by underlying action.
  const routed = await dispatch(
    '## Offer prep (Stage-0c) — the §2/§3 router (the partition arbiter)\n\n' + bindRule('offer-examples/offer-coordination.md') + '\n\n' +
    'Read the Step-8 lever sheets (`interventions-*.md`), the Step-4 diagnostic questions (`research/*`), and the ' +
    'Step-7 sweep flags (`sweep-check.md`). Take their UNION, dedupe by underlying action, and assign each to ' +
    'exactly one section by the written criteria (default to §3 on ambiguity; a contraindication → §3; barren ' +
    'chain-steps → an explicit no-lever line). Write `' + at('offer-router.md') + '` and return ' +
    '{ done, levers: [<§2-item-id>...], tests: [<§3-item-id>...] }. ' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:router', phase: 'Share · Compose', schema: {
      type: 'object', required: ['done'],
      properties: { done: { type: 'boolean' }, promptBindSha: { type: 'string' },
        levers: { type: 'array', items: { type: 'string' } }, tests: { type: 'array', items: { type: 'string' } } } } })
  const allLevers = (routed && Array.isArray(routed.levers) && routed.levers.length) ? routed.levers : ['lever-1']
  const allTests = (routed && Array.isArray(routed.tests)) ? routed.tests : []
  const leverCap = Number(cfg.offerLeverCap) || 8
  const testCap = Number(cfg.offerTestCap) || 6
  const levers = allLevers.slice(0, leverCap)
  const tests = allTests.slice(0, testCap)
  const deferredLevers = allLevers.slice(leverCap)
  const deferredTests = allTests.slice(testCap)
  if (deferredLevers.length || deferredTests.length) log(
    'Offer §2/§3 capped: writing ' + levers.length + ' of ' + allLevers.length + ' act-and-learn item(s) and ' +
    tests.length + ' of ' + allTests.length + ' test(s). Deferred, and NAMED in the index rather than dropped: ' +
    [...deferredLevers, ...deferredTests].join(', ') + '.')
  // §1 fans over the DEEP-DIVED candidates only — the ones carrying a mechanism map. It used to fan over
  // every non-null candidate, which on 2026-07-19 wrote 42 sections where 3 had a map behind them: 32 of
  // them rested on no research at all and ~274KB was written and discarded. Everything not deep-dived is
  // named in the plan's roster instead, with an offer to open it on request.
  // "Deep-dived" means CARRIES A MECHANISM MAP — not "is top-ranked", and not "is in mapCandidates"
  // (that set derives from `leading`, which on a sliced startAt:'compose' run falls back to the first N,
  // so keying off it dispatched §1 for unresearched candidates). The map FILE ON DISK is the predicate.
  // But do NOT read it via isDone() over the shared `census`: that census carries all 48 hypotheses plus
  // every artifact, and the LLM relay can TRUNCATE the long list and drop the map entries — which made
  // this guard misfire as "no deep-dived candidate" on a run where all three maps were present on disk.
  // A dedicated, SCOPED disk read (a three-line output the relay cannot truncate) is the reliable signal.
  const mapLs = await trusted('List the mechanism-map files on disk (scoped, truncation-proof)',
    'for f in "' + root + '"/mechanism-map-*.md; do [ -e "$f" ] && basename "$f"; done',
    { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
    'offer-maplist', 'Share · Compose')
  const mapSlugs = new Set(((mapLs && Array.isArray(mapLs.files)) ? mapLs.files : [])
    .map(f => String(f).replace(/^mechanism-map-/, '').replace(/\.md$/, '')))
  const hasMap = (h) => (
    (Array.isArray(h.candidates) && h.candidates.length) ? h.candidates : [h.slug || h.id]
  ).map(slugify).some(sl => mapSlugs.has(sl))
  const deepCandidates = nonNull.filter(hasMap)
  if (!deepCandidates.length) return await halt('7',
    'Offer §1 has no deep-dived candidate: no mechanism-map-<slug>.md on disk matches any candidate slug ' +
    '(maps found: ' + ([...mapSlugs].join(', ') || 'none') + '; candidates: ' +
    (nonNull.slice(0, 6).map(h => slugify(h.slug || h.id)).join(', ')) + '…). ' +
    'Refusing to compose an offering with no researched candidate behind it.')
  const rosterCandidates = nonNull.filter(h => !deepCandidates.some(d => String(d.id) === String(h.id)))
  log('Offer §1 fan-out: ' + deepCandidates.length + ' deep-dived candidate(s) get a full section (' +
    deepCandidates.map(h => h.id).join(', ') + '); ' + rosterCandidates.length + ' named in the roster.')
  // The fanned section files: Opening (single) + Index + §1 per candidate + §2 per routed lever + §3 per routed test.
  const openingRel = 'offer-sections/opening.md'
  const indexRel = 'offer-sections/index.md'
  const s1Files = deepCandidates.map(h => ({ rel: 'offer-sections/sec1-' + String(h.id).toLowerCase() + '.md', h }))
  const part2Rel = 'offer-sections/sec2-000-intro.md'
  const part3Rel = 'offer-sections/sec3-000-intro.md'
  const s2Files = levers.map(l => ({ rel: 'offer-sections/sec2-' + slugify(l) + '.md', key: l }))
  const s3Files = tests.map(t => ({ rel: 'offer-sections/sec3-' + slugify(t) + '.md', key: t }))
  const secFiles = [openingRel, indexRel, ...s1Files.map(x => x.rel),
    part2Rel, ...s2Files.map(x => x.rel), part3Rel, ...s3Files.map(x => x.rel)]
  // Stage-0d — THE PLANNER (document architect). Nothing in this pipeline ever held the whole document as
  // an object: compose fanned out to blind parallel writers and joined their bytes, so there was no index,
  // no seams between parts, no non-overlap contract and no length budget — the 2026-07-20 review's
  // "way too long / super hard to navigate / redundant" findings are all downstream of that. The planner
  // runs before any prose is written and decides what is written, in what order, under what titles, with
  // what each section covers and — the anti-redundancy mechanism — what it must NOT cover.
  const planRel = 'offer-plan.md'
  const plan = (!prepDone(planRel)) ? await dispatch(
    '## Offer prep (Stage-0d) — the document plan (you are the ARCHITECT; you write no client prose)\n\n' +
    bindRule('offer-examples/planner.md') + '\n\n' +
    'Read the deepening mechanism-maps (`mechanism-map-*.md`), `step6-prioritize.md`, `sweep-check.md`, ' +
    '`interview-answers.md`, `' + at('offer-router.md') + '`, `' + at('offer-glossary.md') + '` and `' +
    at('offer-names.md') + '`.\n\n' +
    'Candidates with a full section (deep-dived, each carrying a mechanism map): ' +
    deepCandidates.map(h => h.id + ' — ' + (h.slug || '')).join('; ') + '.\n' +
    'Candidates named in the roster only (no deep dive): ' +
    (rosterCandidates.map(h => h.id).join(', ') || '(none)') + '.\n' +
    'Routed act-and-learn items: ' + (levers.join(', ') || '(none)') + '.\n' +
    'Routed test-first items: ' + (tests.join(', ') || '(none)') + '.\n\n' +
    'Write `' + at(planRel) + '` per offer-examples/planner.md: the ordered section list with FINAL ' +
    'client-facing titles, per-section `covers` and `excludes`, a word budget per section and for the whole ' +
    'document, the ordering rationale, the seams between major parts, and the roster entries.\n\n' +
    'BUDGET BINDING — this is what makes the budgets real rather than advisory. Each of the following ' +
    'section files will be written by one writer, and the editor enforces your budget against the file. In ' +
    'your structured return, every section that maps to one of these files MUST carry `file` set to its ' +
    'EXACT stem from this list, alongside its `budgetWords`:\n' +
    secFiles.map(r => '  - ' + r.split('/').pop().replace(/\.md$/, '')).join('\n') + '\n' +
    'Sections of the plan that are sub-parts of a file (a heading inside the opening, say) carry no `file` ' +
    'and are budgeted inside their parent. A section file with no budget is a section the editor cannot cut.\n' +
    'Set each `budgetWords` at the TOP of the range its writer spec states for that section type, never below ' +
    'it — a budget under the spec range makes a compliant section get cut for being compliant. ' +
    SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:plan', phase: 'Share · Compose', schema: {
      type: 'object', required: ['done'],
      properties: { done: { type: 'boolean' }, promptBindSha: { type: 'string' },
        totalBudgetWords: { type: 'number' },
        sections: { type: 'array', items: { type: 'object', required: ['id', 'title'], properties: {
          id: { type: 'string' }, file: { type: 'string' }, title: { type: 'string' },
          covers: { type: 'array', items: { type: 'string' } },
          excludes: { type: 'array', items: { type: 'object', properties: {
            material: { type: 'string' }, ownedBy: { type: 'string' } } } },
          seamOut: { type: 'string' }, budgetWords: { type: 'number' } } } } } } }) : null
  // Budgets are keyed by the section FILE STEM, which the planner is told to echo verbatim — keying off a
  // free-form `id` silently matched nothing and disabled the editor for every section.
  const planSections = (plan && Array.isArray(plan.sections)) ? plan.sections : []
  const planBudgets = new Map(planSections
    .filter(sec => sec && sec.file && Number(sec.budgetWords) > 0)
    .map(sec => [String(sec.file).replace(/\.md$/, '').toLowerCase(), Number(sec.budgetWords)]))
  if (!plan && isDone(planRel)) {
    // Resumed run: the plan is on disk but its structured return is not in memory. Read the budgets back
    // rather than letting the editor silently no-op, which is how this stage would die on every resume.
    const reread = await dispatch(
      '## Offer prep (Stage-0d, read-back) — recover the section budgets from the existing plan\n\n' +
      'Read `' + at(planRel) + '` and return its section list VERBATIM as structured data — for every ' +
      'section that names one of these files, its `file` stem and its `budgetWords`:\n' +
      secFiles.map(r => '  - ' + r.split('/').pop().replace(/\.md$/, '')).join('\n') + '\n' +
      'Return the plan as written. Do NOT re-plan, re-title, re-budget or add a section. ' +
      NO_SIDEWORK_RULE + '\n' + RETURN_RULE + ' Structured output only.',
      { label: 'offer:plan:reread', phase: 'Share · Compose', schema: {
        type: 'object', required: ['done'], properties: { done: { type: 'boolean' },
          sections: { type: 'array', items: { type: 'object', properties: {
            file: { type: 'string' }, budgetWords: { type: 'number' } } } } } } })
    for (const sec of ((reread && Array.isArray(reread.sections)) ? reread.sections : [])) {
      if (sec && sec.file && Number(sec.budgetWords) > 0) {
        planBudgets.set(String(sec.file).replace(/\.md$/, '').toLowerCase(), Number(sec.budgetWords))
      }
    }
    log('Editor: recovered ' + planBudgets.size + ' section budget(s) from the existing plan on resume.')
  }
  if (planSections.length && !planBudgets.size) log(
    'Editor: the plan returned ' + planSections.length + ' section(s) but none carried a `file` + `budgetWords` ' +
    'pair, so no budget can be enforced. Sections will be written unbudgeted.')
  // Every writer is bound to the plan and the registry. Threaded into all four prompts below.
  const PLAN_RULE = 'BOUND TO THE PLAN: read `' + at(planRel) + '`. Write ONLY what the plan assigns this ' +
    'section under `covers`; do NOT write what it assigns elsewhere under `excludes` — overlap with another ' +
    'section is a FAIL. Use the plan\'s title verbatim. Stay within the plan\'s word budget for this section; ' +
    'over-budget is a defect to be cut, not thoroughness.'
  const NAMES_RULE = 'BOUND TO THE NAME REGISTRY: read `' + at('offer-names.md') + '`. Refer to every ' +
    'mechanism node and every connection by its PLAIN-ENGLISH NAME there. Never write an internal identifier ' +
    '(N-number, B-number, H-number, S-number, "§1", a map filename) in client-facing text. Every sentence ' +
    'must be understandable on its own, without the reader looking anywhere else in the document. No ' +
    'pipeline meta: no safety attestations, no audit notes, no sentences about this process.'
  // Opening (single agent; owns the across-candidate interaction; reads the deepening maps — no registry).
  if (!sectionDone(openingRel)) await dispatch(
    '## Offer — Opening: "The shape of it" + the across-candidate interaction (you OWN it)\n\n' + bindRule('offer-examples/opening.md') + '\n\n' +
    'Read the deepening mechanism-maps (`mechanism-map-*.md`), `step6-prioritize.md`, `sweep-check.md`, ' +
    '`interview-answers.md`, and `offer-glossary.md`. Write `' + at(openingRel) + '` per offer-examples/opening.md — the integrated picture + how ' +
    'the candidates couple.\n' + PLAN_RULE + '\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:opening', phase: 'Share · Compose', schema: WROTE_SCHEMA })
  // §1 per candidate (fanned) — taught once, completely; node names from its deepening map.
  await parallel((recompose ? s1Files : await resumeTodo(s1Files, x => x.rel, 'offer-s1-exist', 'Share · Compose')).map(x => () => dispatch(
    '## Offer — §1: what may be going on, for candidate ' + x.h.id + '\n\n' + bindRule('offer-examples/sec1.md') + '\n\n' +
    'Write the §1 passage for candidate ' + x.h.id + ' (' + (x.h.slug || '') + ') per offer-examples/sec1.md — teach it once, ' +
    'completely, using the person\'s words from `offer-glossary.md`. Carry the DEPTH its source artifacts carry: ' +
    'where the mechanism-map holds a quantitative estimate, carry its assumptions and its result; where it holds a ' +
    'causal chain to a felt symptom, narrate that chain end to end; where it holds a per-agent or per-organism ' +
    'breakdown, carry it; where a number comes from a measurement, say what was measured, when, and in what ' +
    'sample. Silently dropping depth the source carries is a FAIL. Write `' + at(x.rel) + '`.\n' + PLAN_RULE + '\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:sec1:' + String(x.h.id).toLowerCase(), phase: 'Share · Compose', schema: WROTE_SCHEMA })))
  // The SEAMS. The reviewer hit the boundary from the candidate sections straight into the interventions
  // with nothing in between — "there isn't a section transition that takes us into interventions". The
  // concat joins bytes, so no writer owned that boundary. These two short pieces do.
  await parallel([
    { rel: part2Rel, what: 'the act-and-learn part — things that could be tried, each of which also reads as a test',
      from: 'the possibilities just taught' },
    { rel: part3Rel, what: 'the test-first part — things worth measuring before acting',
      from: 'the things that could be tried' },
  ].filter(x => !sectionDone(x.rel)).map(x => () => dispatch(
    '## Offer — the seam into ' + x.what + '\n\n' + bindRule('offer-examples/offer-coordination.md') + '\n\n' +
    'Write the short transition that takes the reader from ' + x.from + ' into ' + x.what + '. Read `' +
    at(planRel) + '` for what this part contains and the order it runs in. Say what changes now, what this ' +
    'part holds, and how to use it — a few sentences, no more. Teach NO mechanism and make NO claim that ' +
    'belongs to a section: this is a doorway, not a room. Write `' + at(x.rel) + '`.\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:seam:' + x.rel.split('/').pop().replace(/\.md$/, ''), phase: 'Share · Compose', schema: WROTE_SCHEMA })))
  // §2 per routed lever (fanned) — references the §1 node by its deepening-map name, never re-teaches it.
  await parallel((recompose ? s2Files : await resumeTodo(s2Files, x => x.rel, 'offer-s2-exist', 'Share · Compose')).map(x => () => dispatch(
    '## Offer — §2: act-and-learn lever ' + x.key + '\n\n' + bindRule('offer-examples/sec2.md') + '\n\n' +
    'Write the §2 entry for the lever ROUTED here (' + x.key + ') per offer-examples/sec2.md — where it acts (the §1 node ' +
    'by its plain name from the registry; do NOT re-teach the mechanism), type tags, program + read-out window, ' +
    'act-as-test read-out, decision branch, already-tried note. Write `' + at(x.rel) + '`.\n' + PLAN_RULE + '\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:sec2:' + slugify(x.key), phase: 'Share · Compose', schema: WROTE_SCHEMA })))
  // §3 per routed test (fanned; may be empty) — references §1 candidates + §2 levers by name.
  await parallel((recompose ? s3Files : await resumeTodo(s3Files, x => x.rel, 'offer-s3-exist', 'Share · Compose')).map(x => () => dispatch(
    '## Offer — §3: test-first / diagnostic ' + x.key + '\n\n' + bindRule('offer-examples/sec3.md') + '\n\n' +
    'Write the §3 entry for the item ROUTED here (' + x.key + ') per offer-examples/sec3.md — test-first / pure-diagnostic ' +
    '/ unexplained-flag / thin-spot, referring to candidates and act-and-learn items by their plain names, never ' +
    're-explaining and never by section number. Write `' + at(x.rel) + '`.\n' + PLAN_RULE + '\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:sec3:' + slugify(x.key), phase: 'Share · Compose', schema: WROTE_SCHEMA })))
  // Stage-3d — THE EDITOR (the only stage that can CUT). Every audit in this pipeline used to check for
  // omission ("what is missing"), so every force pushed the document longer and none pushed back; the
  // 2026-07-20 delivery ran to 4,242 lines. This pass word-counts each written section against the plan's
  // budget and re-dispatches ONLY the over-budget ones, with a cut-only remit. Bounded by construction:
  // at most one agent per over-budget section, and none at all when everything is within budget.
  if (planBudgets.size) {
    const wcBash = 'for f in ' + secFiles.map(r => JSON.stringify(at(r))).join(' ') +
      '; do printf "%s\\t%s\\n" "$f" "$(wc -w < "$f" 2>/dev/null || echo 0)"; done'
    const wc = await trusted('Word-count each offer section against its plan budget', wcBash,
      { type: 'object', required: ['done'], properties: { done: { type: 'boolean' },
        counts: { type: 'array', items: { type: 'object', properties: {
          file: { type: 'string' }, words: { type: 'number' } } } } } }, 'offer-wordcount', 'Share · Compose')
    const counts = (wc && Array.isArray(wc.counts)) ? wc.counts : []
    const over = counts.map(c => {
      const rel = secFiles.find(r => String(c.file || '').endsWith(r.split('/').pop()))
      if (!rel) return null
      const key = rel.split('/').pop().replace(/\.md$/, '').toLowerCase()
      const budget = planBudgets.get(key)
      return (budget && Number(c.words) > budget * 1.15) ? { rel, budget, words: Number(c.words) } : null
    }).filter(Boolean)
    if (over.length) {
      log('Editor: ' + over.length + ' section(s) over their plan budget by >15% — cutting to budget.')
      await parallel(over.map(x => () => dispatch(
        '## Offer Stage-3d — EDITOR: cut `' + x.rel + '` to its budget\n\n' +
        bindRule('offer-examples/offer-coordination.md') + '\n\n' +
        'This section runs to ' + x.words + ' words against a plan budget of ' + x.budget + '. Read `' +
        at(planRel) + '` for what it is assigned to cover, then rewrite `' + at(x.rel) + '` within budget.\n' +
        'You may ONLY CUT. Remove restatement, throat-clearing, hedge-stacking, anything the plan assigns to ' +
        'another section, any surviving internal identifier, and any sentence about this pipeline. You may ' +
        'NOT add a new claim, and you may NOT drop a load-bearing fact: a quantitative estimate keeps its ' +
        'assumptions and its result, a causal chain to a felt symptom stays narrated end to end, a ' +
        'per-item breakdown keeps its discrimination between members, a measurement keeps ' +
        'what/when/which-sample.\n' +
        'SUBSTANCE OUTRANKS BUDGET. The writer spec permits a deliberate overrun when the required ' +
        'substance will not fit, provided the section says what pushed it over. If this section carries ' +
        'such a line and the overrun is genuinely that substance, LEAVE IT LONG and report that in your ' +
        'note — cutting it would remove the depth the spec just protected, which is a worse failure than ' +
        'the length. Cut only where the length is not carrying substance. If the section cannot reach ' +
        'budget without losing substance, cut what you can and say so rather than gutting it. ' +
        SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
        { label: 'offer:edit:' + x.rel.split('/').pop().replace(/\.md$/, ''), phase: 'Share · Compose', schema: WROTE_SCHEMA })))
    }
  }
  // The INDEX — "here is everything in this document, and what each part covers" — so the reader can pick
  // where to go instead of reading 4,000 lines in order. Rendered from the plan, which already holds every
  // title and its `covers`; this writer composes no new analysis and adds no claim of its own.
  if (!sectionDone(indexRel)) await dispatch(
    '## Offer — the index: what is in this document, and what each part covers\n\n' +
    bindRule('offer-examples/planner.md') + '\n\n' +
    'Read `' + at(planRel) + '` AND the one-line opener that starts each written section file. Render the ' +
    'reader-facing index: every part of the document in order, under the plan\'s own titles, each with one ' +
    'plain sentence saying what it covers — take that sentence from the section\'s own opener where it has ' +
    'one, so the index and the section cannot drift apart. Group it so the person can choose where to go.' +
    ((deferredLevers.length || deferredTests.length) ? (' Also name, plainly, the items considered and ' +
      'written up no further this time, so nothing is silently dropped: ' +
      [...deferredLevers, ...deferredTests].join(', ') + '.') : '') + '\n' +
    'Then the roster line: name the candidates carried but not deep-dived (' +
    (rosterCandidates.map(h => h.id).join(', ') || '(none)') + ') and say plainly that any of them can be ' +
    'opened to the same depth on request. Add NO analysis and NO claim not already in the plan. Write `' +
    at(indexRel) + '`.\n' + NAMES_RULE + '\n' +
    (smoke ? SMOKE_RULE : '') + '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + ' Structured output only.',
    { label: 'offer:index', phase: 'Share · Compose', schema: WROTE_SCHEMA })
  await refreshCensus('offer-sections', 'Share · Compose', secFiles.map(at))
  // Coverage reconciler (Stage-3a): the fan-out gives EXACTLY one file per item, so a missing file is a
  // zero-owner FAIL — the missing-file check IS the coverage reconciler here (no double-owner is possible).
  // Deterministic verify (check-exist; offer-sections/* are SUBDIR files, census-truncation-vulnerable).
  const missingSecs = await missingAbs(secFiles.map(at), 'offer-secs-verify', 'Share · Compose')
  if (missingSecs === null || missingSecs.length) return await halt('7', 'Offer section pass incomplete: missing section file(s): ' + ((missingSecs || ['(existence check failed)']).join(', ')))
  // Deterministic concat Opening + §1..§3 → offering-draft.md (same trusted heredoc concat; reverts with
  // the driver; SKIPS when the draft is already complete + newer than every section, so a resume re-concat
  // cannot needlessly bump the draft mtime past fresh council readproof markers).
  const concatBash = buildOfferConcatCmd(at('offering-draft.md'), secFiles.map(at))
  await trusted('Assemble offering-draft.md from the offer section files (deterministic concat)',
    concatBash, WROTE_SCHEMA, 'offer-concat', 'Share · Compose')
  await refreshCensus('offer-draft', 'Share · Compose', [at('offering-draft.md')])
  if (!isDone('offering-draft.md')) return await halt('7', 'offering-draft.md not on disk / not structurally complete after the section concat.')
  // Stage-3b/3c — plain-language auditor + faithfulness pass over the assembled draft (a FAIL halts for a
  // fix + resume). The coordination layer distinct from the council's register/structure/substance audits.
  const stage3 = (await parallel([
    () => dispatch('## Offer Stage-3b — plain-language auditor\n\n' + bindRule('offer-examples/offer-coordination.md') + '\n\n' +
      'Audit `' + at('offering-draft.md') + '` for the plain-language FAIL categories (undefined term on first use, ' +
      'invented label, leaked analytic/pipeline jargon, stacked hedge, cross-ref to an absent name, missing paragraph ' +
      'breaks, a mechanism not retellable with technical names removed, a coined word where a glossary term exists). ' +
      'Return { verdict: PASS|FAIL, findingsOpen: [...] }. ' + NO_SIDEWORK_RULE + ' Structured output only.',
      { label: 'offer:plainlang', phase: 'Share · Compose', schema: { type: 'object', required: ['verdict'], properties: { verdict: { type: 'string' }, findingsOpen: { type: 'array', items: { type: 'string' } } } } }),
    () => dispatch('## Offer Stage-3c — faithfulness / citation pass\n\n' + bindRule('offer-examples/offer-coordination.md') + '\n\n' +
      'Check `' + at('offering-draft.md') + '`: every load-bearing claim (dose, mechanism step, interaction, location) ' +
      'traces to a cited upstream artifact OR sits under a "gaps for upstream" note; an uncited, unflagged claim FAILS. ' +
      'Return { verdict: PASS|FAIL, findingsOpen: [...] }. ' + NO_SIDEWORK_RULE + ' Structured output only.',
      { label: 'offer:faithful', phase: 'Share · Compose', schema: { type: 'object', required: ['verdict'], properties: { verdict: { type: 'string' }, findingsOpen: { type: 'array', items: { type: 'string' } } } } }),
  ])).filter(Boolean)
  const stage3Fail = stage3.filter(s => s && s.verdict !== 'PASS')
  if (stage3Fail.length) return await halt('7', 'Offer coordination audit not PASS (plain-language / faithfulness): ' +
    stage3Fail.map(s => s.verdict).join(', ') + '. Fix and resume.')
}
}  // end stageActive('compose')
if (stopAfter('compose')) return smokeReturn('compose')

// ── Council: the 7 finish-line auditors (parallel — they read the draft, they don't write it). Each:
//    dispatch on offering-draft.md → readproof (verbatim line-numbered spans) → open/close findings →
//    (deterministic aggregation) → mint its gate token. Group A rides `offering`; Group B mint own tokens.
//    The token is minted by audit-council-completion.sh (trusted, reads the secret), NOT by the driver.
if (stageActive('audit')) {
phase('Share · Audit')
let councilFailing = []
let councilRan = false            // did we actually dispatch the council this run (vs. resume-skip)?
let councilReturned = 0           // how many auditors came back non-null (Fix 2: a dead auditor must not pass)
if (cfg.resumeFrom) await refreshCensus('council-precheck', 'Share · Audit')
if (cfg.resumeFrom && isDone('offering.md')) {
  log('resume: offering.md already on disk — skipping the council.')
} else {
councilRan = true
const councilResults = (await parallel(AUDITORS.map(a => () =>
  dispatch(
    '## Step 7 finish-line auditor: ' + a.role + ' (gate: ' + a.gate + ')\n\n' +
    'Audit `' + at('offering-draft.md') + '` against primary sources — NOT the synthesizer\'s prose. ' +
    bindRule(a.ref) + '\n\n' +
    'Proof-of-read (SP1): return `read_proof` = at least ' + a.minSpans + ' verbatim, line-numbered ' +
    'quote-spans from the draft. Then run, in Bash (session is provided — do not use an env var):\n```bash\n' +
    // B1 — key the readproof marker by a.gate (NOT a.role): the census + finish gate count by GATE, so
    // Group-A's role-keyed markers would never satisfy the `offering` gate → finish-line deadlock. The 3
    // Group-A auditors thus share one `offering.readproof-ok` (last-writer-wins, a 1-of-3 disk-proof);
    // accepted as-designed — the verdicts are independently gated (councilReturned + unanimity check).
    'bash ' + hookScript('council-readproof.sh') + " '" + IH_SESSION + "' " + a.gate + ' "' + at('offering-draft.md') + '" ' + a.minSpans + '  # pipe your read_proof YAML\n' +
    '# open a finding ONLY for a blocking FAIL (never on PASS):\n' +
    '# bash ' + hookScript('council-finding.sh') + " open '" + IH_SESSION + "' " + a.gate + ' <finding-id> <artifact_local|upstream_gap> "<issue>"\n```\n\n' +
    'Do NOT mint the gate token yourself — the workflow mints it deterministically (with the explicit run ' +
    'root) after all auditors PASS. Your job is the readproof marker + any blocking finding + the verdict. ' +
    'Return {gate, role, verdict (PASS|FAIL|ESCALATE), readproofOk, findingsOpen, tokenMinted:false}. ' +
    NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'audit:' + a.role, phase: 'Share · Audit', schema: COUNCIL_SCHEMA }))
)).filter(Boolean)
councilReturned = councilResults.length

councilFailing = councilResults.filter(c => c && c.verdict !== 'PASS')
if (councilFailing.length) {
  log('Council: ' + councilFailing.length + ' auditor(s) not PASS — ' + councilFailing.map(c => c.gate + ':' + c.verdict).join(', '))
} else {
  log('Council: all ' + councilReturned + ' auditors returned; ' + (councilReturned === AUDITORS.length ? 'all PASS.' : 'BUT ' + (AUDITORS.length - councilReturned) + ' did not return.'))
}
}
// Finish-line gate — DRIVER-OWNED, no HMAC tokens. The driver itself dispatched the 7 auditors, so it
// reads their verdicts directly; a signed-manifest / gate-token layer is redundant now that CODE (not
// the model) decides when the offer is written — and it cannot be produced anyway from a sandboxed
// dispatch (the signer can't reach the key). Require: council unanimous PASS + the extraction spot-check.
await refreshCensus('council', 'Share · Audit')
const spotCheck = parseCensus(census, [at('extracted/spot-check.md')]).complete
// Fix 2 — a null/dead auditor is silence, not agreement: require ALL 7 to have returned before the
// verdicts can be trusted. Only enforced when the council actually ran this pass (not a resume-skip).
if (councilRan && councilReturned !== AUDITORS.length)
  return await halt('7', 'finish-line: council incomplete — only ' + councilReturned + ' of ' + AUDITORS.length + ' auditors returned (a null/dead auditor cannot count as PASS). Re-dispatch and resume.')
if (councilFailing.length) return await halt('7', 'finish-line: council not unanimous — ' + councilFailing.map(c => c.gate + ':' + c.verdict).join(', ') + '. Address the findings and resume.')
if (!spotCheck)            return await halt('7', 'finish-line: extracted/spot-check.md missing — cannot write the offer without the extraction spot-check.')
// A7 (slice-safety belt-and-suspenders): runStep1 gates the fresh + resume Step-1 paths, but a modular
// run that STARTS after 'extract' (cfg.startAt) skips runStep1 — so the offer could otherwise be built
// on a DIRTY extraction. Re-read the verdict at THIS offer chokepoint and HALT if not clean (fail-closed),
// so NO path — sliced or not — ships an offer on flawed extraction data.
const finishVerdict = await readVerdict(at('extracted/spot-check.md'))
if (!finishVerdict.clean) return await halt('7', 'finish-line: extraction accuracy verdict is NOT clean (' + verdictReason(finishVerdict) + ') — the offer must not be built on flawed extraction. Fix the source(s), remove extracted/spot-check.md, and re-run the extraction.')
// Fix 2 — disk-proof the council actually did the work: every gate must have left a proof-of-read marker
// that is FRESH for the current draft, and no blocking finding may be open (both unioned across the two
// audit mirrors by the census). Backward-compat: only enforced when the census reports councilState AND
// the council ran this pass; an older census (no councilState) retains today's verdict+spot-check gate.
if (councilRan && census && census.councilState) {
  const cs = census.councilState
  // B1 — the required gate set is single-sourced from AUDITORS[].gate (the exact set the readproof
  // dispatch above writes markers under), not a hardcoded literal that could drift.
  const missingProof = finishLineMissingProof(cs.readproofGates)
  if (missingProof.length)
    return await halt('7', 'finish-line: proof-of-read missing or stale for gate(s): ' + missingProof.join(', ') +
      ' — each auditor group must leave a readproof marker newer than the current offering-draft.md. Re-audit the current draft and resume.')
  if ((cs.openFindings || 0) > 0)
    return await halt('7', 'finish-line: ' + cs.openFindings + ' blocking council finding(s) still open on disk — resolve (close) them and resume.')
}
}  // end stageActive('audit')
if (stopAfter('audit')) return smokeReturn('audit')

// ── Strip: offering.md = a MECHANICAL faithful strip of offering-draft.md (provenance tags removed, no
//    prose change). Produced by the deterministic EMITTER investigate-offer-emit.py — a python SCRIPT
//    (NOT `python -c`), so the bash-gate allows it to write the gated offering.md; it reuses
//    faithful-strip.py's own functions so the output passes faithful-strip + council-offer-complete
//    validation. (faithful-strip.py itself is only a VALIDATOR: no --emit, and it reads the client from
//    stdin — the driver's old `--emit`/`--out` call was against an API that never existed, so it hung.)
//    No HMAC finish-line token: the offer is gated by the deterministic driver sequence + the council
//    verdicts + this completeness check, not by a token a sandboxed dispatch can't mint.
//    GUARD: offering.md must ALWAYS be produced by this emitter (a named python script), never by a
//    Write/Edit or a shell redirect — the still-live write-check Check 4 / bash-gate treat offering.md as
//    gated, so a hand-edit would be denied and could deadlock a future change. Keep it emitter-written.
if (stageActive('finalise')) {
phase('Share · Finalise')
await trusted('Faithful strip → offering.md (deterministic emitter) + completeness validation',
  'python3 "' + refPath('investigate-offer-emit.py') + '" --draft "' + at('offering-draft.md') + '" --out "' + at('offering.md') + '" --hooks-lib ' + hookScript('lib') + '\n' +
  'bash ' + hookScript('council-offer-complete.sh') + " '" + IH_SESSION + "' \"" + at('offering-draft.md') + '" "' + at('offering.md') + '"',
  WROTE_SCHEMA, 'strip:offering', 'Share · Finalise')
await refreshCensus('strip', 'Share · Finalise', [at('offering.md')])
if (!isDone('offering.md')) return await halt('7', 'offering.md not on disk after the deterministic strip (emitter or completeness check failed).')
// Presentation layer — the STANDARD final deliverable. offering.md is faithful but bare; this renders
// a styled HTML page with a clickable Contents index (always) and, when pandoc is present, a .docx whose
// TOC entries are real internal links so Google Docs imports clickable navigation + collapsible headings.
// Deterministic (a named python helper, no agent); NON-fatal — a missing renderer/pandoc never blocks the
// run, because offering.md is the source of record and the render is a convenience on top of it.
await trusted('Render offering.md → offering.html (+ offering.docx if pandoc present)',
  'python3 "' + refPath('investigate-offer-render.py') + '" --in "' + at('offering.md') + '" ' +
  '--out-html "' + at('offering.html') + '" --out-docx "' + at('offering.docx') + '" || ' +
  'echo "render skipped (non-fatal)"',
  WROTE_SCHEMA, 'render:offering', 'Share · Finalise')
}
if (stopAfter('finalise')) return smokeReturn('finalise', { offering: at('offering.md') })

// Step 7.5 — deeper-pass invitation (the run is "done" only after the offer is surfaced to the person,
// which is a skill-retained conversational turn, not a file write).
if (stageActive('openthreads') && !(await runStep(STEPS.find(s => s.id === '7.5')))) return { root: cfg.root, halted: true }
if (stopAfter('openthreads')) return smokeReturn('openthreads', { offering: at('offering.md') })

log('investigate-health-orchestrator complete: offer built, audited by 7 finish-line auditors, stripped to client offering.md.')
return {
  root: cfg.root,
  halted: false,
  hypotheses: hypSet.map(h => h.id),
  leading: leading.map(h => h.id),
  phaseBFiles: leading.map(h => 'convergence-' + h.id + '.md'),
  offerSections: OFFER_SECTIONS.map(s => s.id),
  auditors: AUDITORS.map(a => a.role),
  offering: at('offering.md'),
  summary: leading.length + ' leading hypotheses deep-dived through Phase-B (5.8→5.14); 7-section offer ' +
           'drafted + audited by all ' + AUDITORS.length + ' finish-line auditors (disk-proofed via ' +
           'census.councilState); client offering.md is a faithful strip.',
}
