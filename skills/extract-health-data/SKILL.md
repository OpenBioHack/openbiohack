---
name: extract-health-data
description: >-
  Turns raw health materials (PDFs, scanned documents, images, spreadsheets, exported
  files) into two layers: first a faithful, fully traceable extraction of each source;
  then a set of cross-source compiled views (timeline, lab-trends, and others) built once
  for pattern-spotting without re-burning tokens. Every item traces back to a verbatim
  source quote. Reorganises data; never interprets, concludes, or flags. Use when handed
  raw health materials that need to become structured, traceable, pattern-ready data
  before any analysis. Called by /investigate-health Step 1, or directly when extraction
  is the whole task. Triggers: "extract this data", "process these records",
  "pull the values out of these PDFs", "/extract-health-data".
---

# Extract-Health-Data

Turns raw materials into trustworthy, pattern-ready data in two phases: **Phase A**
extracts each source faithfully and traceably; **Phase B** compiles cross-source views
(timeline, lab-trends, and others) once, so downstream work can spot patterns without
redoing the compilation each time. Both phases reorganise data only — they never
interpret, conclude, or flag. That is downstream work.

## Use the highest-capability model available

Extraction error rates scale inversely with model capability. The cost of one careful
extraction with the best model is far smaller than the cost of an investigation built
on bad data. Default to the top-tier model available (Opus over Sonnet over Haiku) for
this work. Lower-tier models routinely make the silent transcription errors this skill
is built to prevent.

## Principles — apply to every extracted item

These rules are universal. They apply regardless of source type or output shape. Output
shape itself is not prescribed — use whatever structure (table, list, sections) faithfully
represents the source while following these principles.

- **Verbatim originals are canonical.** The source file is the truth. The extracted
  markdown is an interpretation. When they disagree, the source wins.
- **Loss-less to STRUCTURE, not just to values — the extraction is a representation, never
  a summary.** Preserve not only every individual value but the source's entire internal
  *structure*: its ordering, grouping, sectioning, axes, columns and their headers, any
  printed annotations, footnotes, threshold/reference lines, legends, and every relationship
  the source lays out between elements (which row belongs to which group, which label spans
  which range, what is plotted against what). The single success test: **the original could
  be reconstructed from the extraction with nothing lost or flattened.** Never reduce,
  select, rank, headline, or decide "what matters" — that is interpretation and lives
  downstream. This is fully general and form-agnostic: it holds for a time-series, a table
  of ratios, a spatial layout, a categorical breakdown, a correlation, a free-text
  narrative, or anything else — the rule is "carry all structure through exactly as given,"
  never "look for feature X." A reduction is precisely where structure silently dies, so
  the extraction contains no reductions at all.
- **Every item carries a source ID.** At minimum: file name + location (page, section,
  or line) + the verbatim source quote it came from. Format: `[src: <file>, <location>,
  "<quote>"]`. An item without a source ID is not allowed in the output.
- **Numbers keep their units explicitly.** mg/dL and mmol/L are different. mg and mcg
  are different. Never silently convert, never silently drop a unit.
- **Categorical values preserve the source's exact wording.** Don't recode "elevated"
  as "high." Don't smooth "borderline" to "in range." Don't translate clinical hedges
  into clean assertions.
- **Dates in ISO format (YYYY-MM-DD).** Date format drift between US and UK
  conventions is a silent error source.
- **Free text preserved verbatim.** Patient self-reports, practitioner narrative,
  anything in prose — preserve the original wording. Paraphrase smuggles interpretation
  in.
- **Practitioner interpretation tagged separately from raw values.** A clinician's
  "consistent with X" is their interpretation, not an established fact. Tag the
  interpretation as theirs.
- **Absence is explicit.** When a value isn't in the source, mark it "not reported."
  Never leave it silently missing.
- **Conservative on ambiguity.** When a value could be one of two readings — OCR
  uncertainty, smudged scan, illegible handwriting — surface both options for
  resolution. Never silently pick.

## Output — exactly what this skill produces

Everything lands in an `extracted/` directory in the investigation's project folder, in
two tiers. This is the complete, fixed manifest — producing all of these files is what
"done" means. **When this extraction is run by a dispatched agent, that agent returns ONLY
a completion signal — "done" plus the file path(s) — and NEVER a summary, headline,
orientation, or any account of the contents or findings.** The files are the sole
deliverable; there is deliberately no compressed version, so whoever consumes the
extraction is forced to open the actual files. (The only thing an agent may surface besides
"done" is a *process* failure — e.g. a source was illegible or corrupt — never a content
summary.) The manifest:

```
extracted/
├── index.md                      Phase A manifest + completeness report: every source,
│                                  its extract file, per-source processed/flagged status
├── <source-name>.md              Phase A: one faithful extract per source file
│                                  (e.g. bloods-2024-09.md, gut-panel.md) — one per source
└── compiled/                     Phase B: cross-source views, derived from the Phase A
    │                              extract files above (never re-read from the originals)
    ├── event-log.md              the canonical store — every dated, sourced datum;
    │                              the single source of truth the other views derive from
    ├── timeline-overview.md      whole-span arc: milestones + major changes only
    ├── timeline-<period>.md      detailed period chunks (e.g. timeline-2021.md);
    │                              as many as the span and data density need
    ├── lab-trends.md             each analyte across every date it was measured
    ├── symptom-matrix.md         symptoms by date, intensity where reported
    ├── treatment-response.md     each treatment + dose + duration + reported response
    ├── active-exposure.md        what the person was taking on any given date
    ├── natural-experiments.md    episodes of markedly better/worse + their conditions
    ├── static-facts.md           non-temporal: genetics, family history, demographics
    ├── data-gaps.md              what has never been measured
    ├── normals-and-negatives.md  what was checked and normal / tried and did nothing
    └── conflicts.md              where sources disagree — surfaced, not resolved
```

**Every file in `compiled/` is always produced.** Where a view has no data in the current
sources, the file still exists and says so ("No data for this view in the current
sources"), so the output is deterministic — you always know exactly which files to expect.

The top of every Phase A extract file records: source name, dates covered, what was
processed, what was flagged, what was escalated.

The structure *inside* any file is determined by what the data actually contains — use
the shape that fits. The principles above are what's enforced, not a schema.

## Phase A — faithful extraction

The job of Phase A is to get each source's data out accurately, with every item
traceable to a verbatim quote. It runs per source, and within a source, per chunk.

### Chunking

Models lose accuracy on long inputs. Extracting across a long document in one pass
produces measurably worse results than processing it in smaller pieces.

- **Chunk by natural boundary, not by token count.** Page boundaries for PDFs; section
  headers for structured documents; one logical category per chunk for multi-section
  reports.
- **Never chunk mid-table.** A table that crosses a page boundary is reassembled before
  extraction. If reassembly isn't possible, flag the table for human review.
- **One chunk per extraction pass.** Don't try to extract several sections together to
  save time. Error rates compound.
- **Maintain a chunk inventory** — what's in each chunk, processed yes/no, errors
  encountered. This is what makes the skill resumable and auditable.

### The extraction loop — run per chunk

1. **Convert.** Use the bundled converter rather than hand-rolling the conversion loop
   inline — `scripts/convert-source.sh <source-file-or-dir> <output-dir>` (in this skill's
   directory). It chooses the right tool per file type and stages plain text for Phase A:
   `pdftotext -layout` for text PDFs, automatic OCR fallback (`pdftoppm` 300dpi +
   `tesseract`, page-delimited) when a PDF is scanned (output below the char threshold),
   `tesseract` for images, `textutil` for rtf/doc/docx, a stdlib-python `xlsx`→tsv, verbatim
   copy for csv/tsv/txt/md, embedded-PDF-preview extraction for Apple iWork
   (`.pages`/`.numbers`/`.key`), and a zip manifest for archives. Encrypted PDFs are tried
   with `qpdf --decrypt` (empty password) and, failing that, marked `.ENCRYPTED`. Anything
   it can't handle gets an explicit `.ESCALATE` or `.TOOL-MISSING` marker instead of a
   silent skip — so coverage is auditable. Every converted file carries a provenance header
   (`<<<source: …>>> <<<tool: …>>>`); the original remains canonical and is what Phase A
   verifies against. If a required tool is missing, install it per "OCR tooling and safe
   package installs" below (verify >7 days old, official source, log the install), then
   re-run the converter. Only escalate a source when the converter emits a marker it cannot
   resolve (genuinely proprietary format, or an encrypted file with no unencrypted
   duplicate and no password).
2. **First-pass extract.** Produce structured output for this chunk, following the
   principles above.
3. **Quote-back verification.** For every value in the first pass, the model must
   produce the exact surrounding source text as a verbatim quote. Reject any item that
   can't be quoted back from the source.
4. **Second-pass extract** using a structurally different prompt — different ordering,
   different framing, different entry point into the chunk. Same model is fine and
   recommended; different prompts force the model into a different reasoning path on
   the same data.
5. **Mechanical diff** between pass 1 and pass 2, item by item. Items that match
   exactly are accepted. Items that differ are flagged.
6. **Resolve flagged items.** For each diverged item: re-read the source. If the source
   itself resolves the question, take the source's answer. If the source is genuinely
   ambiguous, surface to the human for resolution. Never silently pick.
7. **Spot-check audit.** Randomly sample ~10% of accepted items and verify each against
   the original source. **Zero tolerance for numeric disagreement** — any mismatch on a
   value triggers a halt and a full re-audit of the chunk.
8. **Write the chunk's output** with source IDs and a flag on any item that required
   human resolution.

**Scratch renders + no deletion (applies to every extraction agent).** When OCR verification
needs page images (`pdftoppm` renders), write them into a scratch dir UNDER the investigation
root — `<root>/extracted/_staged/_verify/` — never into `/tmp`. And **never issue a deletion**
(`rm`/`rmdir`/`mv`/`find -delete`/`rmtree`) during extraction: the investigate-health
"NO CLEANUP MID-RUN" rule forbids removing anything under the root until the Step-7 finish-line,
and rendering into `/tmp` invites an out-of-root cleanup that trips the security hook and alarms
the operator. Leave scratch renders in place; a single named cleanup step removes them at
end-of-run. When dispatching extraction to sub-agents, put this rule in the agent prompt — the
sub-agent does not inherit this file.

After all chunks: update `index.md` — the Phase A completeness report — so every page of
every source is accounted for, processed status visible, any unresolved items listed.

### Raw-genetics files at intake

Identify the file by header format (23andMe, MyHeritage, AncestryDNA, etc.).
Record its presence as a static fact and its path. Do NOT attempt per-row
extraction at intake — the file is dense (hundreds of thousands of SNPs) and the
relevant queries are determined later by the orchestrator. The intake task here
is to confirm the file is readable, log row count, identify the reference build
(GRCh37, GRCh38, etc.), and note any header anomalies. No downstream
`genetics-snps.md` is produced at intake. The orchestrator (`/investigate-health`
Step 2) issues per-mechanism queries against the raw file once the working
mechanism map exists; those queries produce
`<root>/extracted/genetics-<mechanism>.md` files at that point, not here.

### Structured interview transcripts

Patient interviews and questionnaires carry question/answer structure that's
load-bearing for downstream interview-substrate use (`/investigate-health` Step
5.5). Phase A extracts of an interview must preserve the structure: each Q + A
pair as a unit, with the verbatim Q and verbatim A both quoted, plus
meta-context (date, context, who was asking). Output:
`<root>/extracted/interview-<date>-<short-context>.md`. Prose-flattening loses
the questions-already-asked vs questions-still-pending match the downstream
skill depends on. The question-bank in the orchestrator must be able to cite
specific Q+A pairs by ID from this extract.

### Failure modes to actively guard against

These are not edge cases. They happen routinely. The verification passes exist
specifically to catch them.

- **Rounding** — 67.3 silently becomes 67.
- **Unit drift** — mg becomes mcg, mmol becomes nmol, often when column layouts shift
  across pages.
- **Reference-range / value confusion** — the reference range gets extracted as the
  patient's value, or the other way round.
- **Row misalignment** — patient values from row 3 attached to analyte names from row
  4 in multi-row tables.
- **Paraphrase smuggling** — "slightly elevated" silently becomes "elevated"; lab-flag
  asterisks dropped.
- **Auto-completion from prior knowledge** — the model fills in a "missing" value it
  expects based on common patterns. **This is hallucination of medical data and is the
  most dangerous failure.**
- **Adjacent-value confusion** — DHEA vs DHEA-S, T3 vs free T3 vs reverse T3, total
  testosterone vs free testosterone, similar-named analytes that mean very different
  things.
- **Negative-sign loss** — -0.3 becomes 0.3.
- **Date format drift** — US vs UK date formats silently reinterpreted.
- **Footnote and asterisk loss** — modifiers that change interpretation get dropped.
- **Page-boundary errors** — a table that spans two pages, one half extracted, the
  other lost.
- **Multi-pass drift** — a later re-extraction differs from the original, and no one
  notices.

If verification catches any of these mid-loop, halt the chunk and re-run its extraction
loop after the fix.

## Phase B — cross-source compilation

Phase B runs only after Phase A is complete for every source. **It reads the Phase A
extract files (`extracted/*.md`) — not the original sources again — and derives every
view from them.** The provenance chain is: original source → Phase A extract (carrying
source IDs) → Phase B view (carrying those same source IDs forward). Built once, so
downstream work doesn't repeat the compilation or drift between agents' versions of it.
Phase B still only *reorganises* — it never interprets.

**Build the event log first; everything else derives from it.** The first Phase B step is
to read every Phase A extract and assemble `compiled/event-log.md` — one entry per dated,
sourced datum. That file is the single source of truth. Every other view in `compiled/`
is then generated *from the event log* (not re-read independently from the Phase A
files), so the views cannot fall out of sync with each other. The event log isn't meant
to be read cover to cover — the views are what you read.

The build order is therefore: Phase A extracts → `event-log.md` → the pivot views
(timeline, lab-trends, symptom-matrix, treatment-response, active-exposure) → the
non-pivot views (natural-experiments, static-facts, data-gaps, normals-and-negatives,
conflicts).

**The views.** Several are pivots of the event log (the same data sorted along different
axes); a few are not.

Pivots of the event log:

- **Timeline.** Two layers. An *overview / arc layer* — milestones and major changes
  only, the whole span on one readable page, so slow long-run patterns stay visible. And
  *detailed period chunks* — everything, windowed, for close reading of one stretch.
- **Lab-trends.** Each analyte across every date it was measured, regardless of source.
  If long: an overview of which markers are actually moving, then per-marker detail.
- **Symptom matrix.** Symptoms by date, with intensity where reported, verbatim-quoted.
- **Treatment-response.** Every treatment tried + dose + duration + reported response.
- **Active-exposure-over-time.** What the person was actually taking on any given date,
  reconstructed from start/stop events — distinct from treatment-response, which is
  trial-by-trial. Catches the confound where a change lines up with something already in
  use, not a new trial.

Not pivots:

- **Natural-experiment catalogue.** Every reported episode of markedly better or worse
  functioning, with the conditions of that episode where stated.
- **Static / constitutional facts.** The non-temporal data: genetics, family history,
  demographics, lifelong traits, allergies. Keeps the lifelong-vs-acquired distinction
  cleanly separable from the dated data.
- **Data-gaps / coverage map.** What has never been measured. The inverse of lab-trends;
  feeds the later question of what's worth testing.
- **Normals-and-negatives.** What was checked and came back in range; what was tried and
  did nothing. Negative data is easy to lose but it's what lets candidates be ruled out.
- **Cross-source conflict log.** Where two sources report the same date or value
  differently — surfaced as data, never silently resolved.

**Sizing for attention.** Every view must be sized so it can be held at once. Where a
view would be too long, split it — an overview layer for the whole arc, detailed chunks
for close reading. Chunk boundaries are *mechanical*: calendar period (year by default,
finer where the data is dense), and natural breaks where the record has long gaps. Never
chunk by "illness phase" or any boundary that requires a judgment about what the data
means — that's interpretation, and it belongs to the orchestrator, not here.

**Phase B principles** (these extend Phase A's, they don't replace them):

- **No cleanup mid-run.** No deletion, removal, move, or `git clean`-style
  operation on `extracted/` or its parents between the start of Phase A and
  the completion of Phase B. Intermediate per-chunk scratch files stay on
  disk until end-of-run; cleanup is a single named step at the end. A
  mid-run `rm` against a Phase A extract can silently desync Phase B views
  derived from the event log.
- Every compiled entry carries a source ID tracing back through Phase A to the original.
- Reorganised, never interpreted: no averaging, no unit conversion, no smoothing, and no
  flagging of what's "noteworthy" beyond the source's own flags.
- Conflicts surfaced, not resolved.
- The same two-pass diff verification applies: compile each view twice with different
  prompts, diff mechanically, resolve discrepancies against the Phase A files.

**Incremental updates.** When a new source arrives later, Phase A runs only on that new
source; then the affected Phase B views re-derive from the updated event log. Phase A
extracts of unchanged sources never re-run.

## OCR tooling and safe package installs

**OCR tool choice.** The long-term OCR tool is chosen deliberately on four
criteria: (a) open-source license, (b) macOS-native invocation (CLI or Python
binding), (c) accuracy on medical-report layouts (multi-column tables, reference
ranges, lab flags), (d) maintenance and safety track record. `tesseract` via
Homebrew meets all four for typed lab reports; accuracy on handwriting is
limited, and handwritten sections should still be flagged for human review.
macOS GUI tools (Scanner Pro, etc.) are not deterministically scriptable and
should not be used as the long-term default; they're acceptable as a one-off
when no CLI option is installed and the source is otherwise stuck.

**Before installing any package** (`brew install`, `npm install`, `pip install`,
`cargo install`, etc.):

1. Check the package's published version history. **Do NOT install any version
   less than 7 days old** — that's the minimum window for supply-chain
   compromises (typosquatting, credential theft, malicious updates) to be
   detected and reported. If the latest version is younger than 7 days, install
   the prior stable version.
2. Check vulnerability databases (CVE, GitHub Security Advisories, OSV) for the
   package name. Skip any package with unpatched critical advisories.
3. Verify the source matches the official upstream — no typosquatting (e.g.
   `pillow` vs `pilow`, `python-requests` vs `requests-python`). Cross-check
   the package's listed GitHub repo against the maintainer organisation.
4. Prefer well-established mainline distributions (homebrew-core, PyPI top-1000,
   npm with >1M weekly downloads) over random taps or low-traffic packages.
5. For any new package install on this machine, log the install (package name,
   version, date, source verified) so the decision is auditable. The install log
   lives at `~/.claude/install-log.md`; append one line per install.

Any package install referenced by this skill or its callers must carry a
verification trail in that log; no package <7 days old is installed; vulnerability
checks are documented inline in the log entry.

## When to escalate to the human

- A file format that needs proprietary software to open (`.pages`, `.numbers`).
- A handwritten section where OCR confidence is low.
- A scanned page degraded enough that re-imaging the original is the right move.
- A two-pass disagreement on a source that is itself genuinely ambiguous.
- A table that crosses page boundaries in a way that can't be reassembled.
- Any case where the source contains information that is materially important and
  cannot be extracted with confidence.

In each case: stop, report clearly what can't be done alone, wait. Silent best-guessing
is forbidden.

## What this skill does NOT do

- Interpret findings, propose mechanisms, or draw conclusions.
- Build the interpreted working hypothesis. Phase B produces neutral, reorganised views;
  turning them into a mechanistic model is the orchestrator's job.
- Find correlations or causal patterns ("these symptoms cluster," "X precedes Y").
  Reorganising data so patterns *can* be spotted is Phase B's job; asserting the patterns
  is not.
- Translate values into different units or scales.
- Add its own judgment of which values are noteworthy. It preserves the source's own
  flags; it does not editorialise.

All of the above are jobs for `/investigate-health`. This skill produces the trusted,
neutral data layer those jobs run on.
