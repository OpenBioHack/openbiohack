# Step 2c — Integration (SHARDED by cause-family; DO NOT FLATTEN; ROOTS vs CONTRIBUTING FACTORS)

Merge every generator's cards into one integrated ledger — sharded by cause-family (so no agent is under
length pressure to gist), with a strict identity test so distinct roots stay separate, AND keeping ROOT
CAUSES separate from CONTRIBUTING FACTORS. The later steps (disconfirmation, deep-dive, prioritisation,
offer) focus on the ROOT CAUSES first; contributing factors ride along as sub-hypotheses of the root they
feed, or in a separate bucket — they are never treated as leading hypotheses. The driver shards by family
and dispatches one integrator per family; a final assembler collates the families.

## Prompt (family integrator — one per family)

```
Merge one CAUSE-FAMILY's cards into integrated entries. You handle only your family.

YOUR FAMILY: <<family>>   INPUT: every `### HYP` card routed to this family. Each card carries a
ROLE: root cause | contributing factor. KEEP that ROLE — merge within ROLE, never across it.

IDENTITY TEST (strict): two cards are the SAME only if they share the SAME ROOT and would be
confirmed/treated by the SAME test/intervention. Same downstream label but different root or different
test = DISTINCT — keep separate. (Hashimoto's vs iodine-deficiency hypothyroidism = DISTINCT.) When
unsure, keep separate. CARRY REASONING VERBATIM — copy each source's REASONING line unchanged; never gist.

ROOT-cause cards → integrated `### HYP H<n>` entries (the primary hypotheses):
### HYP H<n> [COMPOUND if applicable]
CLAIM: <root cause, plain>
SOURCES: <generator ids (2a-<view> / 2b-whole-picture) that contributed>
REASONINGS (verbatim, one per distinct source rationale):
- "<source reasoning, copied>" [from: <generator-id>] [data: <cited>]
LIKELIHOOD-RANGE: <span>

CONTRIBUTING-FACTOR cards → integrated `### CF<n>` entries (secondary — do NOT merge into a root, do NOT
promote to a root):
### CF<n>
CLAIM: <the contributing factor / systemic state, plain>
FEEDS: <the root cause(s) it contributes to, named by CLAIM — the root MAY be in another family; write
        "unattached" if it feeds no single identifiable root>
SOURCES / REASONINGS (verbatim): as above.

Anti-flatten (driver checks it): every input card maps to exactly one entry (an H or a CF); each entry's
REASONINGS count ≥ the number of distinct source rationales it absorbed. Dropping a rationale FAILS.
```

## Assembly — deterministic, NOT a free-form LLM step

The assembler is `lib/integrate/assemble-hypset.py`, a stdlib Python helper the driver runs by name
(`python3 assemble-hypset.py --integrated-dir hypotheses --out hypothesis-set.md --json`). There is NO
LLM in the writing path: the family files are already spec-compliant (the family integrators applied the
writing spec upstream), so the assembler only REARRANGES and COPIES already-written text — it composes
nothing. It parses every `hypotheses/integrated-*.md`, applies the optional judge instruction map (below),
renumbers roots, buckets contributing factors, and WRITES `hypothesis-set.md` directly. Because it rewrites
the file wholesale on every run, a leftover file from an earlier run can never survive — a re-run replaces
it, which structurally dissolves the old "silent stale file" failure. A non-zero exit HALTs the driver; it
never falls back to accepting a pre-existing file.

What the assembler produces, deterministically:
- ROOT CAUSES are the primary set and the ONLY thing later steps work on first. Each root becomes a pinned
  `### Hn — <slug>` heading (n = 1,2,3,… in a FIXED cause-family order), preserving `[COMPOUND]`, with its
  full CLAIM / SOURCES / REASONINGS / LIKELIHOOD body carried VERBATIM (byte-for-byte).
- ONE parallel-null block `### Hn — <slug> [null]`, and each judge-flagged safety must-exclude as
  `### Sn — <slug> [safety]`. `leading` is chosen from ROOTS only; a contributing factor is NEVER an
  `### Hn` and NEVER leading.
- CONTRIBUTING FACTORS are collected into ONE trailing `## Contributing factors` bucket, each a BULLET
  (never a `###` heading), copying the `FEEDS:` line and REASONINGS the family integrator wrote, verbatim:
     - [CF] <claim>  [family: <X>]  FEEDS: <root it feeds (verbatim from the CF entry, or "unattached")>
  Nesting / cross-attaching CFs to individual roots is deliberately NOT done (that cross-matching is what
  hung the old free-form assembler); the flat bucket records the linkage without re-deriving it.

The slug is a cosmetic human label the assembler derives from the CLAIM; the `Hn` id is the load-bearing
token the census counts. The assembler does NOT re-dedup or re-reason across families — the family
integrators already merged within family; the ONLY cross-family judgement (which roots are the SAME root)
is made by the LLM judge and handed in as instructions, never inferred by the tool.

## LLM judge — merge/move instructions ONLY (the one semantic call)

Before the assembler, a small bounded LLM judge reads all `integrated-*.md` and returns ONLY a structured
instruction map — it composes no document:

```
{
  "merges":  [ [ {"family": "<fam>", "id": "H<n>"}, … ], … ],   // groups of roots that are the SAME root
  "moves":   [ {"family": "<fam>", "id": "H<n>|CF<n>", "to": "root|contributing"} ],
  "safety":  [ {"slug": "<short>", "reason": "<why must-exclude>", "src": "<citation>"} ],
  "nullSlug": "<slug for the parallel-null block>"
}
```

IDENTITY TEST (strict, conservative): merge two roots only if they share the SAME underlying root AND would
be confirmed/treated by the SAME test/intervention. Same downstream label but a different root or a
different confirming test = DISTINCT — keep separate. When unsure, keep separate. The judge writes no
file; an empty map is valid (identity assembly).

## Assembler self-checks (in code, fail-closed — exit 2, no/atomic file — NOT self-certified by an agent)
- Every input `### HYP` / `### CF` entry maps to EXACTLY one output entry (a root `### Hn` or a `- [CF]`
  bucket bullet); zero-owner or duplicate FAILS.
- Every input REASONINGS line appears byte-for-byte in the output; a merged root's REASONINGS contain every
  absorbed member's lines byte-for-byte (a byte check, not a count) — a dropped rationale FAILS.
- Every `### Hn` is a ROOT cause; no contributing factor is an `### Hn`.
- A malformed instruction map, an unknown family/id, overlapping merge groups, or a merge/move naming the
  wrong entry-kind FAILS.
- Grounding self-check: the assembler re-runs the real `investigate-grounding-anchor` admissibility verdict
  over the assembled roots (single-source with the write-check gate the direct write bypasses); an
  inadmissible root FAILS. Compliance is preserved by verbatim copy + this deterministic re-check, not by
  an LLM re-reading a spec.
