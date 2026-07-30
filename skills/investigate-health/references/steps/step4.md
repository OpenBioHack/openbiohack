### Step 4 — Inventory (enumerate shared nodes, then gate by addressability)

**Patience preamble.** This step has no time pressure. Take however long you need; the
cost of rushing is higher than the cost of doing it slowly. The enumeration and the
addressability gate are dispatched to sub-agents (`subagent_type: general-purpose`) with
clean context; the orchestrator prepares the packet (the Step-3 graphs) and does not
synthesise inline. The sub-agents are dispatched as the enumerate/addressability role.
(The register, flat-context, and cross-subject-memory guards are injected by the driver via
`references/register.md`; the role-specific instructions — this preamble and the
dispatch-neutrality rule below — live in this file.)

**Dispatch-neutrality rule (non-negotiable).** The dispatch packet is the unranked,
unweighted set of Step-3 mechanism graphs. The orchestrator must NOT, in the dispatch
prompt or any wrapper text:

- name specific nodes or candidates as worth special evaluation, "the likely connector,"
  "must be held as a parallel layer," or any other singling-out language
- mention candidates by clinical name that did not also appear in the graphs under the
  same name
- describe the expected shape of the answer ("evaluate whether X is the connector")
- reference what prior runs concluded, what manual analyses found, or
  what the orchestrator "knows" about this kind of case
- pre-weight by warning the agent against specific candidates
  ("don't fix on X as the answer automatically") — the warning still elevates X by
  putting it in front

If a specific candidate name appears in the dispatch wrapper, the dispatch is biased and
must be rewritten. The agent enumerates every shared node equally; the orchestrator does
not pre-select which nodes the agent attends to. This rule is the structural equivalent of
blinded evaluation — the agent should not be able to reconstruct, from the dispatch prompt
alone, what the orchestrator suspects the answer is.

Failure mode this prevents: the orchestrator, having seen prior runs or having background
knowledge of the case, leaks the suspected answer into the dispatch by naming it "for
evaluation." Even neutrally framed, the name's appearance gives it disproportionate
attention versus the other nodes the graphs surfaced — the agent then re-derives a similar
answer not because the rules drove it, but because the dispatch seeded it.

When in doubt: name no candidate. Point the agent at the graphs and let it enumerate.

**Do not hunt for "the connector" or rank nodes by importance.** Ranking by
importance/centrality silently buries cheap, broad, reversible nodes underneath
central-but-unactionable hubs — a node that appears in many graphs is *more shared*
precisely by being a generic hub, and importance-ranking rewards exactly that. Enumerate
first; judge last. Convergence is **read off** the finished graphs, never used to steer
them. Strict admission has not gone away — it has moved to Step 6, where the prioritizer's
safety/attribution constraints and value-as-a-move ranking do the disciplined selection.
Generate wide (Step 3, blind), enumerate complete (Pass 1), gate honestly (Pass 2),
prioritise strictly (Step 6).

**Pass 1 — enumerate every shared node.** List EVERY node appearing in ≥2 of the Step-3
graphs, matched at the resolved-entity level (clear synonyms for the same
molecule/cell/receptor/microbe are one node). For each: which graphs it appears in, and the
count. Be exhaustive — include every shared node, central or peripheral; do **not** omit a
node because it seems minor or because it appears in only two graphs. The burying failure
mode is real: a cheap, addressable node that sits in only two or three graphs is exactly
what importance-ranking loses, and exactly what the person can often act on. A node shared
across mechanisms representing *different* symptom domains spans more of the picture than
one shared across near-duplicate mechanisms — record the domain diversity, but never let it
(or any importance judgment) drop a node from the enumeration.

**Match on the shared underlying mechanism, not the shared word — and escalate it.**
Convergence is not only exact-name overlap. Different labels can be facets of one underlying
thing — a mediator, the cell that releases it, the pathway it sits on, the enzyme that
clears it can be the *same axis* under different names. When nodes across graphs are
mechanistically linked this way, recognise the underlying shared mechanism, group the
facets, and **name the axis explicitly** — sharpening a scattered set of near-relations into
one identified thing. Treat a strong cross-graph convergence as a signal to **investigate
that axis more deeply** (its sources, its clearance, its localised and non-canonical forms —
via `/research` and `/research-practitioner`), not as a node to read off and move past.
Convergence *raises* investigation; it does not substitute for it.

**Pass 2 — gate by addressability.** For each shared node, mark whether a DIRECT, specific,
reversible real-world handle exists (a drug, supplement, diet change, specific microbe or
its substrate, cofactor, behavioural lever) — Yes/No, and name the handle if Yes. A node may
be a generic non-addressable hub (a broad cytokine, a master transcription switch) and still
belong in the *complete* table — it is simply marked not-cheaply-addressable, not excluded.

**Multi-route note.** When a single addressable node is produced/accumulated through more
than one distinct route across the graphs (and, for accumulating compounds, also poorly
cleared), record every route and every clearance gap. Such a node is both a high-value
target and the reason a single-route intervention gives only partial relief — that is
information for Step 6, surfaced here, not a reason to fix on it as the answer now.

The addressable subset is the candidate set Step 6 prioritises.

**Agent overlap is observed and noted, not used as evidence.** When multiple
research agents independently surface the same candidate, hypothesis, or
recommended test, that's a process observation — not a Bayesian update on the
candidate's likelihood. Agents reading the same input data through similar
training priors reach similar conclusions; that's the architecture, not
evidence. Even when inputs are partially non-overlapping, training-prior shared
structure makes "independent convergence" difficult to verify from the outside.
What IS weight-bearing: the underlying *content* the agents cite — specific
primary studies, named mechanisms, falsifiers, discriminators. When two agents
cite the same primary RCT, the RCT is the evidence; the agents are reporters.
When the underlying evidence in agent outputs is the same fact cited from
different angles, that fact gets weighted once at its actual strength, not N
times. Record "candidate X surfaced by N of the dispatched agents" as a process
observation in the decision log using the phrase **"observed in N agents,"** not
"converged on by N agents." No tier is lifted on the strength of agent overlap
alone.

**Completeness audit — what's absent, not just what's present.** Pass 1–2 inventory what is
*present* across the graphs. This asks what is *missing*: list every
observation the hypothesis doesn't explain; name any body system or category of cause that
isn't represented at all; ask what a specialist in an unrelated field would notice is
missing. Absences found here are honest gaps to carry forward (step 7), and sometimes
point back to a route step 3 never opened.

Concrete checklist — go through these seven categories of body system and ask, for
each: is this represented in the working hypothesis? If not, why not — is it genuinely
irrelevant to this case, or has it just not been considered?

- **Digestion and absorption** — gut, microbiome, nutrient uptake, bile
- **Immune system and inflammation** — defence, repair, infection, allergy
- **Energy production** — mitochondria, thyroid, adrenal output, blood sugar
- **Detoxification and elimination** — liver, kidneys, sweat, bowel
- **Transport** — blood vessels, lymph, blood cells
- **Hormones and nerve-signalling** — endocrine, neurotransmitters, autonomic balance
- **Structural integrity** — cell membranes, connective tissue, joints, fascia

Used as a checklist of *what's been looked at*, not as a framework that claims any of
these is the right answer. A category where the working hypothesis has nothing to say
is either a gap to go fill (back to step 3) or an honest "not relevant here because X"
entry — both are fine, an empty category with no justification is not. The audit produces
a 7-row table — category / verdict (represented with cited claim / not relevant because X
/ unexplored) — and no "unexplored" verdict remains by the time the working hypothesis
is offered.

*Output:* `<root>/shared-node-inventory.md` — the complete shared-node table plus the
addressable shared-node subset, plus the 7-system completeness table flagging honest gaps.
This inventory is the input to Step 4.5; the technical working hypothesis emerges from the
hypotheses that survive cross-check, interview, and prioritisation.

