export const meta = {
  name: 'extract-health-data',
  description: 'Parallel verbatim extraction sized by the actual data: section-aware chunking of large sources (never mid-table), fan-out Phase-A extraction, then a deterministic exact verifier (whole-token grounding: every data-line token verbatim in its own [src:] quote and each quote verbatim in the source; plus DATA-coverage: every source value reaches the extract data) drives a surgical, non-rewriting resolve to empty; then a carry-forward Phase-B (per-source fragments that DECLARE their date span → a deterministic structure manifest, no LLM merge and no re-reading pass); and finally the ONE cross-source artifact — a single chronological document in which every character is copied from a source by script, addressable by identifier. There are no compiled views: a view replaces its source for whoever reads it, so a compression error inside one is invisible downstream.',
  whenToUse: 'When raw health materials have already been CONVERTED to text (by scripts/convert-source.sh) and need faithful, coverage-proven extraction plus the single verbatim timeline that every later stage reads. The orchestrator converts first (non-LLM, free, parallel) and passes the converted paths as args. Not for conversion itself.',
  phases: [
    { title: 'Chunk', detail: 'deterministically section-chunk large sources (never mid-table); small sources stay whole' },
    { title: 'Extract', detail: 'one extraction agent per chunk (model-tiered: cheap for clean text, top for OCR)' },
    { title: 'Verify', detail: 'deterministic grounding + DATA-coverage per source (agent Bash runs cite_verify.py; date/unit reformats auto-reverted by code)' },
    { title: 'Resolve', detail: 'ONE Edit-only pass-2 on the residual worklist; re-verify; converge (≤3 iters)' },
    { title: 'EventLog', detail: 'per-source fragments that DECLARE their date span → compiled/structure.md (no merge, no re-read)' },
    { title: 'Timeline', detail: 'build the ONE verbatim document: segment each source into passages (agents emit boundaries only, never prose), copy the byte ranges, then verify every block against its own source span' },
  ],
}

// ───────────────────────── config ─────────────────────────
const MAX_ITERS   = 3          // converge-loop cap per source (cost bound)
// Extraction (and everything else) runs on the session's TOP model — always Opus, never a cheaper
// tier. Faithful medical extraction is the accuracy-critical step; a cheaper model under-extracts
// dense tables (it costs extra resolve rounds and risks silent drops). We omit `model` everywhere so
// every agent inherits the session top-tier. (The old sonnet CLEAN_MODEL tier was removed 2026-07-02.)
// OCR-ambiguous chunks, the resolver, and all of Phase B omit `model` → inherit the session's
// top-tier model (extraction error rate scales inversely with capability; spend it where it counts).

// deterministic helper library — lives in the skill's scripts/ dir (writable), NOT the protected
// hooks/ dir. The chunker is self-contained here. Overridable via args.libDir (e.g. to point at an
// un-installed scratchpad build), or args.libPath for back-compat (a single helper-dir path).
// (the Phase-B category labeler is gone with the views it labelled for — Phase B carries structure forward from the
// chunk plan + fragment declarations; the .py stays in-tree, unused.)
let LIBDIR = '"$HOME/.claude/skills/extract-health-data/scripts"'
const libFile = (name) => LIBDIR.replace(/"$/, '') + '/' + name + '"'
let CHUNKER  = libFile('extract-chunker.py')     // deterministic section chunker
// The verifier is reached through its OWN explicit path (NOT the flat atom-diff seam above): the
// orchestrator computes VERIFY_LIB_DIR and passes it as args.verifyLibDir. Keeping this a separate
// seam is what makes the atom-diff → cite_verify cutover a co-change across the driver AND the
// orchestrator (red-team hidden-coupling-2), instead of silently overloading libDir (which still
// resolves chunker + manifest from lib/atom-diff).
let VERIFYDIR = '"$HOME/.claude/workflows/lib/verify"'
let VERIFY = VERIFYDIR.replace(/"$/, '') + '/cite_verify.py"'   // the ONE grounding + coverage verifier
let RECONCILE = VERIFYDIR.replace(/"$/, '') + '/image_reconcile.py"'  // dual-vision reconcile + materialise
let CONVERTDIR = '"$HOME/.claude/workflows/lib/convert"'
let GEOM = CONVERTDIR.replace(/"$/, '') + '/geom-extract.py"'   // deterministic PDF word-geometry extractor
// The timeline layer — the ONE cross-source artifact. Its own explicit path (args.timelineLibDir),
// for the same reason the verifier has one: a cutover here must be a visible co-change across the
// driver and the orchestrator, never a silent overload of libDir.
let TIMELINEDIR = '"$HOME/.claude/workflows/lib/timeline"'
const tlFile = (name) => TIMELINEDIR.replace(/"$/, '') + '/' + name + '"'
let SEGMENT = tlFile('segment.py')      // where each passage starts and stops — boundaries only
let TLBUILD = tlFile('build.py')        // copies the declared byte ranges; the only whole-file write
let TLVERIFY = tlFile('verify.py')      // read-only; re-reads every source and checks byte identity
// The source contract: what may become a block, the identifier scheme, the tag vocabulary. Lives
// with the other prompt specs so it is version-controlled with them and carries no subject data.
let TIMELINE_SOURCES = '"$HOME/.claude/skills/investigate-health/references/timeline-source.md"'

// There are no compiled views. Six of them used to sit here, each an LLM-written compression of the
// per-source extracts, and each downstream stage read the compression instead of the record. A view
// REPLACES its source for whoever reads it, so a compilation error inside one is invisible to
// everything after it — measured on 2026-07-26 at 33 unsupported claims, 61 losses of the person's
// own meaning, a date moved five months, and a denial he volunteered deleted while the sentence it
// denied was kept. The replacement is the Timeline phase below: ONE document, every character copied
// from a source by script, addressable by identifier so nobody ever retypes a quotation.
const VIEWS = []

// ───────────────────────── schemas ─────────────────────────
// UNGROUNDED = a token not verbatim in its cited quote, or a quote not verbatim in the source.
const UNGROUNDED = {
  type: 'object', required: ['reason'],
  properties: { file: { type: 'string' }, line: { type: 'number' }, token: { type: 'string' },
                quote: { type: 'string' }, reason: { type: 'string' }, detail: { type: 'string' } },
}
// UNCOVERED = a source value that never reached the extract DATA (dropped row/prose, or a value left
// in a citation quote but off the data line).
const UNCOVERED = {
  type: 'object', required: ['reason'],
  properties: { source: { type: 'string' }, token: { type: 'string' }, quote: { type: 'string' },
                line: { type: 'string' }, reason: { type: 'string' } },
}
// the verify-runner echoes cite_verify's own JSON (grounding + DATA-coverage), validated on the way
// back. `reverted` records the date/unit reformats code fixed in place before reporting.
const VERIFY_SCHEMA = {
  type: 'object', required: ['ungrounded', 'uncovered', 'ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    ungrounded: { type: 'array', items: UNGROUNDED },   // drives the converge loop
    uncovered: { type: 'array', items: UNCOVERED },      // drives the converge loop
    reverted: { type: 'array', items: {
      type: 'object', properties: { file: { type: 'string' }, line: { type: 'number' },
        old: { type: 'string' }, new: { type: 'string' }, kind: { type: 'string' } } } },
    summary: { type: 'object', properties: {
      ungrounded: { type: 'number' }, uncovered: { type: 'number' }, reverted: { type: 'number' } } },
    ok: { type: 'boolean' },
    note: { type: 'string' },
  },
}
const WROTE_SCHEMA = {
  type: 'object', required: ['file', 'done'],
  properties: { file: { type: 'string' }, done: { type: 'boolean' }, note: { type: 'string' } },
}
// Phase-B per-source FRAGMENT step: writes the fragment (like WROTE_SCHEMA) AND declares, as it goes,
// the source's date span — captured at write time so the structure manifest needs NO re-reading pass.
const FRAGMENT_SCHEMA = {
  type: 'object', required: ['file', 'done'],
  properties: { file: { type: 'string' }, done: { type: 'boolean' }, note: { type: 'string' },
    firstDate: { type: 'string' }, lastDate: { type: 'string' } },
}
// Fragment-reuse pre-check (cfg.reuseFragments): per source, does its event-log fragment already exist,
// and if so its date span, parsed from the fragment's own ISO headings. Mirrors the Phase-A
// disk-check — no raw source re-read.
const FRAG_REUSE_SCHEMA = {
  type: 'object', required: ['sources', 'ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    sources: { type: 'array', items: {
      type: 'object', required: ['name', 'exists'],
      properties: { name: { type: 'string' }, exists: { type: 'boolean' },
        firstDate: { type: 'string' }, lastDate: { type: 'string' }, note: { type: 'string' } } } },
    note: { type: 'string' },
  },
}
// Phase-A chunk plan: per source, the ordered chunk source-file list (1 entry = whole source).
const CHUNK_PLAN_SCHEMA = {
  type: 'object', required: ['sources', 'ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    sources: { type: 'array', items: {
      type: 'object', required: ['name', 'chunks'],
      properties: { name: { type: 'string' }, nChunks: { type: 'number' },
                    chunks: { type: 'array', items: { type: 'string' } },
                    flags: { type: 'array', items: { type: 'string' } } } } },
    note: { type: 'string' },
  },
}

// ───────────────────────── prompts ─────────────────────────
// AUTONOMY: these agents run UNATTENDED — the operator must be able to start the run and walk away.
// A single permission prompt (e.g. an rm) blocks the whole run. So agents must do ONLY their one
// task and nothing that could prompt or leave mess: no backups, no probes, no self-verification, no
// cleanup, no shell beyond what is explicitly shown.
const NO_SIDEWORK_RULE =
  'UNATTENDED RUN — do ONLY the single task described, nothing else. Do NOT create backup / probe / ' +
  '"before"/"after" / temp copies of any file (no *_bak, *_probe, *.orig). Do NOT run your own ' +
  'verification, diff, or "gate check" — the workflow re-diffs your output automatically. Do NOT run ' +
  'any shell command beyond the one(s) explicitly shown in this prompt (extraction/merge agents: use ' +
  'only the Read/Write/Edit tools on the named files). Do NOT delete, move, or clean up anything ' +
  '(no rm/rmdir/mv/find -delete) — a single cleanup/permission prompt halts an unattended run. Edit ' +
  'the target file IN PLACE; the workflow keeps its own history via resume.'
const SCRATCH_RULE =
  'NEVER delete anything under the investigation root (no rm/rmdir/mv/find -delete), and never create ' +
  'backup or scratch copies of an extract. If a genuine scratch render is unavoidable it goes under ' +
  '<root>/extracted/_staged/ and is LEFT in place — never cleaned up mid-run. ' + NO_SIDEWORK_RULE

const RETURN_RULE =
  'Return ONLY a completion signal (done + the file path). NEVER a summary, headline, orientation, or ' +
  'any account of the contents — the files are the sole deliverable.'

const extractPrompt = (src, chunkPath, chunkIdx, nChunks, extractFile, iterHint) =>
  '## Phase-A faithful extraction — source: ' + src.name +
  (nChunks > 1 ? ' (chunk ' + (chunkIdx + 1) + ' of ' + nChunks + ')' : '') + '\n\n' +
  'Converted source text' + (nChunks > 1 ? ' CHUNK' : '') + ' (the converter output; the ORIGINAL ' +
  'remains canonical): `' + chunkPath + '`\n' +
  (nChunks > 1 ? 'This is ONE section-aligned chunk of a larger source that was split at structural ' +
    'boundaries (never mid-table). Extract ONLY what is in this chunk; do not guess at content in ' +
    'other chunks. The chunks are re-diffed as a whole against the full source afterwards.\n' : '') +
  'Write the faithful extract to: `' + extractFile + '`\n\n' +
  '## Rules (extract-health-data Phase A — these are enforced by the installed Foundation and ' +
  'src-fidelity write-gates; a write that violates them is DENIED):\n' +
  '- Loss-less to STRUCTURE, not just values: preserve ordering, grouping, columns+headers, ' +
  'reference ranges, footnotes, flags, and every row→group relationship. The original must be ' +
  'reconstructable from the extract.\n' +
  '- Every item carries `[src: ' + src.name + ', <loc>, "<verbatim quote>"]`. No item without a source ID.\n' +
  '- VERBATIM VALUES — copy every value character-for-character from the source: numbers, units, ' +
  'dates, reference ranges, flags, and words. NEVER reformat anything in the extract: a date stays ' +
  'exactly as written ("12-Nov-2024" stays "12-Nov-2024"; "10/05/1991" stays "10/05/1991" — do NOT ' +
  'convert to ISO), a unit stays exactly ("µg/g" stays "µg/g", never "mcg/g"); never convert or drop a ' +
  'unit; decimals and negative signs exact (67.3 ≠ 67). Conservative on OCR ambiguity — surface both ' +
  'readings, never silently pick.\n' +
  '- GROUNDING (this is machine-checked, exactly): every data line carries `[src: ' + src.name + ', ' +
  '<loc>, "<verbatim quote>"]`, and EVERY word / number / unit you write on that data line must appear ' +
  'verbatim INSIDE that line\'s own quote. So put the source\'s own text on the data line and quote the ' +
  'exact span it came from. A token not in its quote — a reformatted date, a converted unit, an ' +
  'invented word or number, a value copied from a different row — is flagged and sent back to you.\n' +
  '- LABELS ARE THE SOURCE\'S OWN WORDS. Any label / column name on a data line must itself be present ' +
  'in that line\'s quote (e.g. quote the header row "| Organism | Result | Reference |"). Do NOT add ' +
  'your own label words ("Result:", "Reference:", "ref") onto a data line. YOUR OWN organizing headers ' +
  'and section titles go on SEPARATE lines that carry NO `[src:]` — those structure lines are not ' +
  'grounded, so use them freely for readable structure.\n' +
  '- COMPLETENESS + DATA-COVERAGE: capture the FULL source — every section, row, value, flag, footnote ' +
  'AND the source\'s own narrative / interpretive / "clinical associations" / notes text — quoting ' +
  'source prose verbatim as data lines; do not skip, summarise, or thin. A value you QUOTE must ALSO ' +
  'appear in the visible DATA of that line, not only inside the quote (a value tucked into the quote ' +
  'but left off the line reads as dropped and is flagged). Add NONE of your own words as data: (a) no ' +
  'preamble / title / meta-note (no "# Faithful Extract" heading, no converter-banner or tool lines, no ' +
  '"Note on OCR/layout" of your own) — begin at the first source item. (b) NEVER reference source LINE ' +
  'or POSITION numbers. (c) Do NOT restate these rules. (d) Use markdown bullets (`-`), NOT numbered ' +
  'lists, and do NOT invent "Report N" / "Row N" / "Section N" numbers the source does not print. ' +
  '(e) If a value is ambiguous, surface BOTH readings as data rows with `[src:]` cites, not as prose.\n' +
  '- Chunk by natural boundary (page/section); never mid-table.\n' +
  (iterHint || '') +
  '\n' + SCRATCH_RULE + '\n' + RETURN_RULE + '\nStructured output only.'

const verifyPrompt = (src) =>
  '## Deterministic grounding + DATA-coverage verify — source: ' + src.name + '\n\n' +
  'Run the verifier and return its JSON verbatim. This is NOT a judgement task — you run ONE command ' +
  'and report exactly what it prints. It checks the extract file(s) against the ORIGINAL converted ' +
  'source, WHOLE-SOURCE (the union of every chunk extract): GROUNDING (every data-line token is ' +
  'verbatim in its own `[src:]` quote, and each quote is verbatim in the source) and COVERAGE (every ' +
  'source value reaches the extract DATA). It also REVERTS any date/unit reformat in place to the ' +
  'verbatim source form before reporting, so those never reach you.\n\n' +
  '```bash\npython3 ' + VERIFY + ' \\\n' +
  '  --extract ' + src.extractGlob + ' \\\n' +
  '  --source "' + src.name + '=' + src.converted + '" \\\n' +
  '  --coverage --apply-reverts' + proseCoverageFlag(src) + ' --json\n```\n\n' +
  'The tool prints a JSON object. Copy the `ungrounded` and `uncovered` arrays (the worklist) and the ' +
  '`reverted` array into your StructuredOutput exactly (each item keeps all its fields). ' +
  'Set ranSuccessfully=true if the command ran (exit 0 OR 1 are both normal — 1 just means the ' +
  'worklist is non-empty). If it errored (missing file, traceback), set ranSuccessfully=false and put ' +
  'the error in note. Do NOT invent, filter, or "fix" entries. Run ONLY the one command shown above — ' +
  'no extra "gate check" commands, no backups, no cleanup. ' + NO_SIDEWORK_RULE + ' Structured output only.'

// SURGICAL resolver: ONE Edit (old_string → new_string) per worklist item, AT ITS LOCATION; never a
// Write / whole-file rewrite. A rewrite that drops content is re-flagged UNCOVERED next pass and a
// reformatting rewrite is re-flagged UNGROUNDED — but the correct move is a pinpoint edit, not to
// rely on the re-catch. Date/unit reformats were already reverted by code, so what remains is
// judgement work.
const wlItem = (u) => '- [' + (u.reason || '?') + '] ' +
  (u.line != null ? 'L' + u.line + ' ' : '') +
  (u.source ? u.source + ': ' : '') +
  '`' + (u.token || u.quote || '') + '`' +
  (u.quote && u.token ? ' (quote: "' + u.quote + '")' : '') +
  (u.detail ? ' — ' + u.detail : '')
const resolvePrompt = (src, v) =>
  '## Surgical pass-2 — resolve ONLY the verifier worklist for source: ' + src.name + '\n\n' +
  'The deterministic verifier flagged these exact issues between the converted source `' + src.converted +
  '` and the extract file(s) `' + src.extractGlob + '`. Fix ONLY these, each with ONE targeted `Edit` ' +
  '(old_string → new_string). A whole-file re-Write is FORBIDDEN — every byte OUTSIDE these items must ' +
  'stay identical.\n\n' +
  '### HOW (surgical-edit protocol — a full rewrite is forbidden):\n' +
  '- For each item, `grep -n` the extract for the flagged token / line, Read only that small region if ' +
  'needed, then make ONE Edit at that spot.\n' +
  '- UNGROUNDED = a token on a data line is NOT verbatim in that line\'s own `[src:]` quote (a ' +
  'reformatted value, an invented word/number, a value copied from another row), OR a quote is not ' +
  'verbatim in the source. Fix by making the data line match the source EXACTLY: copy the value ' +
  'verbatim (never reformat), or correct the quote to the exact source span it should cite, or remove ' +
  'an invented token. Do NOT reformat to satisfy the check — copy what the source literally says.\n' +
  '- UNCOVERED = a source value is missing from the extract DATA. `quote-value-not-in-data`: the value ' +
  'is sitting in a citation quote but not on the data line — ADD it to the visible data line. ' +
  '`source-not-in-data`: a source span was never extracted — ADD a new data line quoting that span ' +
  'verbatim with a `[src: ' + src.name + ', <loc>, "<verbatim quote>"]`.\n' +
  '- NEVER DELETE a line that carries a `[src:]` cite unless it is a worklisted invention. Prefer ' +
  'editing IN PLACE to deleting.\n\n' +
  '### UNGROUNDED (' + v.ungrounded.length + '):\n' +
  (v.ungrounded.length ? v.ungrounded.map(wlItem).join('\n') : '- (none)') + '\n\n' +
  '### UNCOVERED (' + v.uncovered.length + '):\n' +
  (v.uncovered.length ? v.uncovered.map(wlItem).join('\n') : '- (none)') + '\n\n' +
  'For every UNCOVERED omission, first CONFIRM the value is genuinely in the source before adding it ' +
  '(re-read the region). If it is genuinely absent, do NOT invent it — note it instead. If a value is ' +
  'genuinely ambiguous, surface both readings. The write-gates re-check every edit.\n' +
  SCRATCH_RULE + '\n' + RETURN_RULE + '\nStructured output only.'

// ───────────────────────── helpers ─────────────────────────
// The worklist that drives the converge loop: ungrounded (extract→source) + uncovered (source→DATA).
const worklistSize = (v) => v.ungrounded.length + v.uncovered.length

// dateSortKey — a best-effort sortable "YYYY-MM-DD" key from a verbatim declared date, for ORDERING
// documents in the structure manifest only (advisory: the views interleave from the verbatim entry
// dates, not this key). Handles ISO (2024-11-12 / 2026-02 / 2024), DD-Mon-YYYY / Mon-YYYY, MM/DD/YYYY,
// and a bare year. Missing parts pad with "00"; anything unparseable sorts LAST ("9999-99-99").
const _MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 }
const _pad2 = (n) => String(n).padStart(2, '0')
const dateSortKey = (raw) => {
  if (!raw || typeof raw !== 'string') return '9999-99-99'
  const s = raw.trim()
  let m
  if ((m = s.match(/(\d{4})-(\d{1,2})(?:-(\d{1,2}))?/)))     // ISO YYYY-MM[-DD]
    return m[1] + '-' + _pad2(+m[2]) + '-' + (m[3] ? _pad2(+m[3]) : '00')
  if ((m = s.match(/(?:(\d{1,2})[ \-/])?([A-Za-z]{3,})[ \-/](\d{4})/))) {  // [DD ]Mon YYYY
    const mo = _MONTHS[m[2].slice(0, 3).toLowerCase()]
    if (mo) return m[3] + '-' + _pad2(mo) + '-' + (m[1] ? _pad2(+m[1]) : '00')
  }
  if ((m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/)))       // MM/DD/YYYY (best effort)
    return m[3] + '-' + _pad2(+m[1]) + '-' + _pad2(+m[2])
  if ((m = s.match(/\b(\d{4})\b/))) return m[1] + '-00-00'   // bare year
  return '9999-99-99'
}

// writeVerbatimPrompt — a mechanical Write of already-computed JS content (structure.md, spot-check.md,
// index.md). The workflow script has no filesystem API, so deterministic files are written through this
// one agent. Defined here so both Phase-B (structure) and the finish-line writes share it.
const writeVerbatimPrompt = (path, content, name) =>
  '## Write ' + name + ' (verbatim, deterministic)\n\n' +
  'Write the EXACT content delimited below to `' + path + '` using the Write tool — verbatim, character for ' +
  'character, with NO additions, edits, reordering, commentary, or reformatting. This is a mechanical write of ' +
  'already-computed data, NOT a judgement task. Do not read other files. Do NOT use a Bash `>` redirect (the ' +
  'cleanup-block denies bash writes into extracted/ mid-run) — use the Write tool.\n\n' +
  '<<<BEGIN ' + name + ' CONTENT>>>\n' + content + '\n<<<END ' + name + ' CONTENT>>>\n\n' +
  'Return {file:"' + path + '", done:true}. ' + NO_SIDEWORK_RULE + ' Structured output only.'

// run the deterministic verifier for one source and return the parsed report (safe empty default).
// The verify agent runs cite_verify with --apply-reverts, so date/unit reformats are already fixed in
// place by code and re-checked before this returns; only genuine residual reaches the resolver.
const runVerify = (src, phaseName) =>
  agent(verifyPrompt(src), { label: 'verify:' + src.name, phase: phaseName, schema: VERIFY_SCHEMA })
    .then(v => v || { ungrounded: [], uncovered: [], reverted: [], ranSuccessfully: false,
                      note: 'verify agent returned null' })
    .then(v => ({ ungrounded: [], uncovered: [], reverted: [], summary: {}, ...v }))

// ───────────────────────── input ─────────────────────────
// args = { root, sources: [{ name, converted, positions?, ocr? }], libDir?, libPath? }
// Accept args as an object OR a JSON string (some callers/harnesses pass it stringified).
let cfg = args
if (typeof cfg === 'string') { try { cfg = JSON.parse(cfg) } catch (e) { cfg = {} } }
if (!cfg || typeof cfg !== 'object') cfg = {}
if (!cfg.root || !Array.isArray(cfg.sources) || cfg.sources.length === 0) {
  return { error: 'extract-health-data workflow needs args = { root, sources: [{name, converted, positions?, ocr?}] }. Convert sources first with scripts/convert-source.sh, then pass the converted .txt paths.' }
}
if (cfg.libDir) {                            // test hook: run the chunker (+ reuse labeler) from an un-installed dir
  LIBDIR = '"' + cfg.libDir.replace(/\/$/, '') + '"'
  CHUNKER = libFile('extract-chunker.py')
} else if (cfg.libPath) {                     // back-compat: a single helper-dir path
  const dir = cfg.libPath.replace(/\/[^/]*$/, '')
  CHUNKER = '"' + dir + '/extract-chunker.py"'
}
// the verifier path — the EXPLICIT seam the orchestrator drives (default = installed runtime dir).
if (cfg.verifyLibDir) {
  VERIFYDIR = '"' + cfg.verifyLibDir.replace(/\/$/, '') + '"'
  VERIFY = VERIFYDIR.replace(/"$/, '') + '/cite_verify.py"'
  RECONCILE = VERIFYDIR.replace(/"$/, '') + '/image_reconcile.py"'
}
if (cfg.convertLibDir) {
  CONVERTDIR = '"' + cfg.convertLibDir.replace(/\/$/, '') + '"'
  GEOM = CONVERTDIR.replace(/"$/, '') + '/geom-extract.py"'
}
if (cfg.timelineLibDir) {
  TIMELINEDIR = '"' + cfg.timelineLibDir.replace(/\/$/, '') + '"'
  SEGMENT = tlFile('segment.py'); TLBUILD = tlFile('build.py'); TLVERIFY = tlFile('verify.py')
}
if (cfg.timelineSources) TIMELINE_SOURCES = '"' + cfg.timelineSources + '"'
const rootClean = cfg.root.replace(/\/$/, '')
const extractedDir = rootClean + '/extracted'
const stagedDir = extractedDir + '/_staged'
const chunkDir = stagedDir + '/_chunks'
// Each source gets its OWN extract subdirectory `extracted/<name>/`, so its extract file(s) can never
// collide with another source whose name is a prefix (the old flat `extracted/<name>*.md` glob matched
// `<name>-other.md` — a real cross-source contamination risk). The per-source glob is now bounded to
// that subdir, so it matches exactly this source's files regardless of naming.
const sources = cfg.sources.map(s => {
  const dir = extractedDir + '/' + s.name
  return {
    ...s,
    extractDir: dir,
    extractFile: dir + '/' + s.name + '.md',              // single-chunk / whole-source extract
    // a source may split across several chunk extract files; diff over the whole subdir (isolated)
    extractGlob: '"' + dir + '"/*.md',
    // image (dual-vision) kind: the agreed rows serialise to <name>.vision.txt (its OWN `converted`,
    // grounded like a geom/text source); disagreements are held for human sign-off in review.json.
    visionTxt: dir + '/' + s.name + '.vision.txt',
    reviewFile: dir + '/' + s.name + '.review.json',
    // vector-pdf (geom) kind: the reconstructed tables serialise to <name>.geom.txt (its OWN
    // `converted`); the [src:]-cited .md is a verbatim slice of it, so cite_verify grounds it 0/0.
    geomTxt: dir + '/' + s.name + '.geom.txt',
  }
})
// Phase-2 kind routing (flag-gated, default OFF → the legacy text path runs for EVERY kind, unchanged).
// A route is taken only when its flag is on AND the source is that kind AND the needed input is present.
const USE_VISION_IMAGES = cfg.useVisionImages === true
const USE_GEOM_EXTRACT = cfg.useGeomExtract === true
const isImageRoute = (s) => USE_VISION_IMAGES && s.kind === 'image' && !!s.image
const isGeomRoute = (s) => USE_GEOM_EXTRACT && s.kind === 'vector-pdf' && !!s.positions
// Prose coverage relaxation (source-span only; grounding + quote→data value coverage stay strict).
// A free-text source (kind:text — a symptom diary, comparison notes) is mostly narrative + embedded
// analysis prose; the strict source-span rule (every source line must reach a data line) cries wolf on
// every sentence and never converges (symptom-log: 590 false omissions). The medical VALUES live in the
// lab tables (geom/vision, strict); text sources carry narrative context where faithfulness — not
// value-coverage — is the guarantee. So kind:text → --coverage-skip-span (grounding + quote→data value
// coverage still run). Non-text kinds get nothing (strict, unchanged). cfg.textCoverage='value-only'
// switches text to the stricter #1 (only genuine measured values are must-cover) when a text source is
// known to be measurement-dense.
const proseCoverageFlag = (s) => s.kind !== 'text' ? ''
  : (cfg.textCoverage === 'value-only'
      ? ' --coverage-value-only "' + s.name + '"'
      : ' --coverage-skip-span "' + s.name + '"')
log('Extracting ' + sources.length + ' source(s); converge cap ' + MAX_ITERS + ' iters/source' +
    (USE_VISION_IMAGES ? '; dual-vision image path ON' : '') + (USE_GEOM_EXTRACT ? '; geom PDF path ON' : '') + '.')

// ───────────────────────── Phase A stage 0: deterministic section chunking (one agent) ─────────────────────────
// Large sources are split at structural boundaries (never mid-table) so their chunks extract in
// parallel; small sources stay whole (1 chunk). This is a DETERMINISTIC, non-LLM step — the agent
// just runs the chunker in Bash and echoes the emitted chunk paths. Losslessness is by construction
// (the chunker's --verify asserts the partition reassembles byte-for-byte) and re-proven by the
// whole-source diff later.
phase('Chunk')
// chunk threshold (bytes) is tunable via args.chunkThreshold; the helper default (12000) applies
// when unset. A source below the threshold stays one whole chunk.
const chunkThreshArg = (cfg.chunkThreshold ? ' --threshold ' + parseInt(cfg.chunkThreshold, 10) : '')
const chunkBash = sources.map(s =>
  'echo "=== ' + s.name + ' ==="; mkdir -p "' + s.extractDir + '"; python3 ' + CHUNKER + ' --source "' + s.converted + '"' +
  (s.positions ? ' --positions "' + s.positions + '"' : '') + chunkThreshArg +
  ' --emit-dir "' + chunkDir + '" --stem "' + s.name + '" --verify').join('\n')
const plan = await agent(
  '## Phase A — deterministic section chunk plan (all sources)\n\n' +
  'Run the chunker for each source below and report the emitted chunk files. This is NOT a judgement ' +
  'task — run the commands and echo what they print. Each command prints a JSON object with an ' +
  '`emitted` array (the ordered chunk source-file paths) and an `n_chunks` count; `--verify` makes it ' +
  'exit non-zero if the partition is ever not byte-lossless.\n\n' +
  '```bash\n' + chunkBash + '\n```\n\n' +
  'For each source return `{name, nChunks, chunks:[<emitted paths IN ORDER>], flags:[...]}`. If a ' +
  'command exits non-zero or errors, set ranSuccessfully=false and put the source + error in note ' +
  '(do NOT fabricate chunk paths). ' + SCRATCH_RULE + '\nStructured output only.',
  { label: 'chunk-plan', phase: 'Chunk', schema: CHUNK_PLAN_SCHEMA }
)
const planByName = {}
if (plan && plan.ranSuccessfully && Array.isArray(plan.sources)) {
  for (const ps of plan.sources) if (ps && ps.name && Array.isArray(ps.chunks) && ps.chunks.length) planByName[ps.name] = ps.chunks
}
// fallback (chunker unavailable / plan failed): treat each source as ONE whole chunk — never drop a
// source, never extract from a partial subset. Correctness is preserved; only parallelism is lost.
for (const s of sources) {
  s.chunks = planByName[s.name] || [s.converted]
  s.multi = s.chunks.length > 1
}
log('Chunk plan: ' + sources.map(s => s.name + '×' + s.chunks.length).join(', ') +
    (plan && plan.ranSuccessfully ? '' : ' (fallback: chunker unavailable → whole-source)'))

// extract-file naming, all inside the source's OWN subdir extracted/<name>/ (collision-proof):
// single chunk → <name>.md; multi → <name>.chunkNN.md (the per-subdir glob covers both)
const chunkExtractFile = (s, i) => s.multi
  ? s.extractDir + '/' + s.name + '.chunk' + String(i).padStart(2, '0') + '.md'
  : s.extractFile

// ── Image (dual-vision) producer: two independent vision reads → deterministic reconcile + materialise.
// Each pass VIEWS the ORIGINAL image (no OCR text) and writes its rows; image_reconcile.py then writes
// ONLY the rows both agree on into <name>.vision.txt (the source's own `converted`) + the [src:]-cited
// extract, and holds disagreements in review.json for human sign-off. A single vision read is never the
// extract; agreement is the grounding gate, and the extract still grounds via cite_verify (uniform).
const RECONCILE_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: { ranSuccessfully: { type: 'boolean' }, agreed: { type: 'number' },
    flagged: { type: 'number' }, note: { type: 'string' } },
}
const passFile = (src, n) => src.extractDir + '/' + src.name + '.pass' + n + '.json'
const visionPrompt = (src, n, outFile) =>
  '## Dual-vision extraction — pass ' + n + ' of 2 — image source: ' + src.name + '\n\n' +
  'VIEW (Read) the image at `' + src.image + '` — a lab-result screenshot. Extract EVERY analyte result ' +
  'you can see, reading each value straight off the pixels (mind decimals; a screenshot value the text ' +
  'layer mis-reads must be read correctly here). For each analyte capture: the name; the value EXACTLY as ' +
  'shown (keep decimals and any leading `<`/`>`); the unit (nmol/L, mg/dL, ratio, pg/mL, … — blank if the ' +
  'card shows none); and the status/flag (NORMAL / ABNORMAL / OPTIMAL, or the section heading the card ' +
  'sits under such as "Out of Range" / "Average" / "Optimal").\n' +
  'This is ONE of two INDEPENDENT reads — do NOT read any OCR text or other file, and do NOT guess: read ' +
  'the image itself. Write ONLY a JSON array to `' + outFile + '` with the Write tool (NOT a bash ' +
  'redirect) — each element {"analyte":"","value":"","unit":"","flag":""}. ' + NO_SIDEWORK_RULE + '\n' +
  'Return {file:"' + outFile + '", done:true}. Structured output only.'
const reconcilePrompt = (src) =>
  '## Dual-vision reconcile + materialise (deterministic) — image source: ' + src.name + '\n\n' +
  'Run EXACTLY this command and report what it prints — NOT a judgement task, run it and echo the JSON:\n\n' +
  '```bash\npython3 ' + RECONCILE + ' "' + passFile(src, 1) + '" "' + passFile(src, 2) + '" \\\n' +
  '  --name "' + src.name + '" --emit-txt "' + src.visionTxt + '" --emit-md "' + src.extractFile + '" \\\n' +
  '  --emit-review "' + src.reviewFile + '" --json\n```\n\n' +
  'It writes ONLY the dual-vision-AGREED rows into the grounding text (`--emit-txt`) and the `[src:]`-cited ' +
  'extract (`--emit-md`); rows the two passes DISAGREE on (or one missed) go to `--emit-review` for human ' +
  'sign-off and are NEVER written as values. From the JSON it prints, return {ranSuccessfully:true, ' +
  'agreed:<n>, flagged:<n>} (exit 0 = full agreement, exit 1 = some flagged — BOTH are normal). If it ' +
  'errored (missing file / traceback), set ranSuccessfully=false with the error in note. ' +
  NO_SIDEWORK_RULE + ' Structured output only.'
// One image source: two vision passes (parallel) → reconcile + materialise. Repoints src.converted to the
// vision-agreed grounding text so stage-2 verify (below) grounds it uniformly, and carries the open
// review-flag count into the accuracy verdict.
const extractImageSource = async (src) => {
  await parallel([1, 2].map(n => () =>
    agent(visionPrompt(src, n, passFile(src, n)),
      { label: 'vision:' + src.name + '#' + n, phase: 'Extract', schema: WROTE_SCHEMA })))
  const rec = await agent(reconcilePrompt(src),
    { label: 'reconcile:' + src.name, phase: 'Extract', schema: RECONCILE_SCHEMA })
    .then(r => r || { ranSuccessfully: false, agreed: 0, flagged: 0, note: 'reconcile agent returned null' })
  src.converted = src.visionTxt          // the image's OWN grounding artifact (in-memory repoint only)
  src.imageMode = true
  src.imageReviewOpen = rec.flagged || 0
  src.reconcileOk = rec.ranSuccessfully === true
  log(src.name + ' [image/dual-vision]: ' + (rec.agreed || 0) + ' agreed, ' + (rec.flagged || 0) +
      ' held for review' + (rec.ranSuccessfully ? '' : ' (reconcile did NOT confirm — treated as needs-review)'))
}

// ── Vector-PDF (geom) producer: deterministic word-geometry reconstruction (no LLM). geom-extract.py
// rebuilds the tables from the PDF's word positions → <name>.geom.txt (its OWN `converted`) + the
// [src:]-cited extract (verbatim slices of it), so stage-2 cite_verify grounds it 0/0 by construction.
const GEOM_SCHEMA = {
  type: 'object', required: ['ranSuccessfully'],
  properties: { ranSuccessfully: { type: 'boolean' }, assocFlags: { type: 'number' }, note: { type: 'string' } },
}
const geomPrompt = (src) =>
  '## Deterministic geometry extraction — vector-PDF source: ' + src.name + '\n\n' +
  'Run EXACTLY this command and report what it prints — NOT a judgement task, run it and echo the result:\n\n' +
  '```bash\npython3 ' + GEOM + ' "' + src.positions + '" "' + src.name + '" \\\n' +
  '  --txt "' + src.geomTxt + '" --extract "' + src.extractFile + '"\n```\n\n' +
  'It reconstructs the PDF tables from word geometry (no LLM), writing the linearised grounding text ' +
  '(`--txt`) and the `[src:]`-cited extract (`--extract`), and prints a JSON line on stderr carrying an ' +
  '`assoc_flags` array (header/footer/misaligned rows flagged for a human spot-read — ADVISORY, not a ' +
  'failure). Return {ranSuccessfully:true, assocFlags:<the length of that assoc_flags array>}. If it ' +
  'errored (missing positions file / traceback), set ranSuccessfully=false with the error in note. ' +
  NO_SIDEWORK_RULE + ' Structured output only.'
// One vector-PDF source: geom reconstruct → own converted (repoint in-memory). Stage-2 verify then
// grounds the geom extract against geom's own text (0/0). assoc flags are advisory (human spot-read).
const extractGeomSource = async (src) => {
  const g = await agent(geomPrompt(src), { label: 'geom:' + src.name, phase: 'Extract', schema: GEOM_SCHEMA })
    .then(r => r || { ranSuccessfully: false, assocFlags: 0, note: 'geom agent returned null' })
  src.converted = src.geomTxt            // the PDF's OWN grounding artifact (in-memory repoint only)
  src.geomMode = true
  src.geomFlags = g.assocFlags || 0
  log(src.name + ' [vector-pdf/geom]: reconstructed' +
      (g.assocFlags ? ', ' + g.assocFlags + ' header/footer row(s) flagged for spot-read (advisory)' : '') +
      (g.ranSuccessfully ? '' : ' (geom did NOT confirm — stage-2 verify will catch a missing extract)'))
}

// ───────────────────────── Phase A stage 0.5: disk-skip pre-check (resume from what's on disk) ─────────
// Modularity / resume: a source whose per-source extract is ALREADY on disk AND still grounds + covers
// clean should NOT be re-extracted — the run continues from what exists (the same principle the run root
// embodies). ONE deterministic agent runs cite_verify (read-only, NO --apply-reverts) over every source
// against its OWN grounding artifact (geom → <name>.geom.txt, image → <name>.vision.txt, else the
// converted source), with the text-source prose relaxation applied (proseCoverageFlag). A source is
// REUSABLE iff its extract .md exists AND the check reports 0 ungrounded + 0 uncovered. A reused source
// skips the expensive Phase-A producer (stage 1) AND its converge loop (stage 2 short-circuits to
// converged), so it costs ZERO extra agents beyond this ONE shared pre-check. A FRESH run (nothing on
// disk) marks every source not-reusable → the legacy full-extract path runs unchanged (the pre-check is
// then a no-op costing +1 agent). cfg.forceReextract=true disables the skip entirely (rollback escape
// hatch → always re-extract). Read-only clean ⟹ clean under --apply-reverts too (reverts only ever
// reduce the ungrounded worklist), so a source that passes here is safe to treat as converged.
const groundSourceFor = (s) => isGeomRoute(s) ? s.geomTxt : isImageRoute(s) ? s.visionTxt : s.converted
const DISKCHECK_SCHEMA = {
  type: 'object', required: ['sources', 'ranSuccessfully'],
  properties: {
    ranSuccessfully: { type: 'boolean' },
    sources: { type: 'array', items: {
      type: 'object', required: ['name', 'exists'],
      properties: { name: { type: 'string' }, exists: { type: 'boolean' },
        ungrounded: { type: 'number' }, uncovered: { type: 'number' },
        heldReview: { type: 'number' }, note: { type: 'string' } } } },
    note: { type: 'string' },
  },
}
const reuseByName = {}
if (!cfg.forceReextract) {
  const checkBash = sources.map(s => {
    const g = groundSourceFor(s)
    return 'echo "=== ' + s.name + ' ==="\n' +
      'if ls ' + s.extractGlob + ' >/dev/null 2>&1 && [ -f "' + g + '" ]; then\n' +
      '  python3 ' + VERIFY + ' --extract ' + s.extractGlob + ' --source "' + s.name + '=' + g + '"' +
      ' --coverage' + proseCoverageFlag(s) + ' --json\n' +
      (isImageRoute(s)
        ? '  [ -f "' + s.reviewFile + '" ] && echo "HELD $(grep -c \'\\"signedOff\\": false\' "' +
          s.reviewFile + '" 2>/dev/null || echo 0)" || echo "HELD 0"\n'
        : '') +
      'else\n  echo MISSING\nfi'
  }).join('\n')
  const check = await agent(
    '## Phase A — disk-skip pre-check (which sources are already extracted clean)\n\n' +
    'For each source below, check whether its per-source extract is already on disk and still grounds + ' +
    'covers clean. This is NOT a judgement task — run the commands and report exactly what cite_verify ' +
    'prints. Each `=== <name> ===` block prints EITHER a cite_verify JSON object (an extract .md is ' +
    'present and a grounding source exists) OR the literal `MISSING` (no extract .md yet, or no grounding ' +
    'source yet).\n\n' +
    '```bash\n' + checkBash + '\n```\n\n' +
    'For each source return `{name, exists, ungrounded, uncovered, heldReview}`: `exists`=true iff the ' +
    'block printed cite_verify JSON (NOT MISSING); `ungrounded` / `uncovered` = that JSON\'s ' +
    '`summary.ungrounded` / `summary.uncovered` counts (use -1 for a MISSING source); `heldReview` = the ' +
    'integer on the `HELD N` line (image sources only; 0 for every other source and 0 when no HELD line ' +
    'printed). Do NOT pass --apply-reverts, do NOT edit any file, do NOT extract — this is READ-ONLY. Set ' +
    'ranSuccessfully=false with the error in note only if a command could not run at all. ' +
    NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'disk-check', phase: 'Chunk', schema: DISKCHECK_SCHEMA }
  ).then(r => r || { ranSuccessfully: false, sources: [] })
  if (check.ranSuccessfully && Array.isArray(check.sources)) {
    for (const c of check.sources) if (c && c.name) reuseByName[c.name] = c
  }
}
// Decide reuse per source DETERMINISTICALLY in JS (never trust the agent to compute the gate). Repoint a
// reused geom/image source's `converted` to its OWN grounding artifact so the downstream Phase-B QC
// grounds it against the same text the producer would have (the fresh-path producers do this repoint
// themselves). Carry an image's open review count into the verdict — an unsigned dual-vision disagreement
// blocks Step 1 even on reuse (never launder a held row clean). Reused geom loses its advisory assoc-flag
// count (stderr-only, not persisted); those flags were already spot-read in the prior clean run.
// TRUST_DISK (cfg.trustDiskExtracts): accept an on-disk extract AS-IS even with grounding residual —
// Phase A is skipped and Phase-B assembles over the sufficiently-complete extracts. This is the operator
// escape hatch for sources that cannot converge under the current grounder (e.g. embedded-quote citation
// parsing, or an editorial-tag extract) but whose DATA is complete. The residual is NOT silently laundered
// clean: it is carried into spot-check as a NON-GATING advisory (see trustResidual). Only ever accepts an
// extract that EXISTS on disk — a missing extract still (re)extracts normally.
const TRUST_DISK = cfg.trustDiskExtracts === true
let reusedCount = 0, trustAcceptedCount = 0
for (const s of sources) {
  const c = reuseByName[s.name]
  const groundClean = !!c && c.exists === true && (c.ungrounded || 0) === 0 && (c.uncovered || 0) === 0
  const trustReuse = TRUST_DISK && !groundClean && !!c && c.exists === true
  if (!groundClean && !trustReuse) continue
  s.reused = true
  reusedCount++
  if (trustReuse) { s.trustAccepted = true; s.trustResidual = (c.ungrounded || 0) + (c.uncovered || 0); trustAcceptedCount++ }
  if (isGeomRoute(s)) { s.converted = s.geomTxt; s.geomMode = true; s.geomFlags = 0 }
  else if (isImageRoute(s)) { s.converted = s.visionTxt; s.imageMode = true; s.imageReviewOpen = c.heldReview || 0 }
}
log(reusedCount + '/' + sources.length + ' source(s) reused from disk' +
    (trustAcceptedCount ? ' (incl. ' + trustAcceptedCount + ' operator-accepted with grounding residual — advisory)' : ' (already extracted clean)') +
    '; ' + (sources.length - reusedCount) + ' to (re)extract' +
    (cfg.forceReextract ? ' (forceReextract: disk-skip OFF)' : '') + '.')

// ───────────────────────── Phase A: fan-out extract (per chunk) → converge (no barrier) ─────────────────────────
const perSource = await pipeline(
  sources,

  // stage 1 — deterministic producers by kind (flag-gated): vector-pdf → geom, image → dual-vision.
  // All other kinds (and flags-off pdf/image): pass-1 LLM extraction, one agent PER CHUNK, parallel.
  // A source already on disk + clean (disk-skip pre-check) skips the producer entirely.
  async (src) => {
    if (src.reused) return { src }
    if (isGeomRoute(src)) { await extractGeomSource(src); return { src } }
    if (isImageRoute(src)) { await extractImageSource(src); return { src } }
    await parallel(src.chunks.map((chunkPath, i) => () =>
      agent(extractPrompt(src, chunkPath, i, src.chunks.length, chunkExtractFile(src, i), ''), {
        label: 'extract:' + src.name + (src.multi ? '#' + i : ''),
        phase: 'Extract',
        schema: WROTE_SCHEMA,
        // no model override → inherits the session TOP model (Opus) for every source, OCR or not
      })))
    return { src }
  },

  // stage 2 — converge loop: WHOLE-SOURCE verify → code-revert (in the verify agent) → ONE Edit-only
  // resolve → re-verify, until the worklist is empty or MAX_ITERS. Verify is always
  // source-vs-union-of-chunk-extracts, so chunking cannot hide a coverage gap.
  async ({ src }) => {
    // reused from disk (pre-check): no verify/resolve. Clean-reuse grounds 0/0; trust-reuse is accepted
    // as-is with a NON-GATING grounding-residual advisory (operator judged the document complete).
    if (src.reused) {
      log(src.name + (src.trustAccepted
        ? ' reused from disk (operator-accepted; ' + (src.trustResidual || 0) + ' grounding item(s) not re-verified — advisory).'
        : ' reused from disk — extract already grounds + covers clean; not re-extracted.'))
      return { src: src.name, chunks: src.chunks.length, iters: 0, converged: true, reverted: 0, reused: true,
               trustAccepted: !!src.trustAccepted, trustResidual: src.trustResidual || 0,
               imageMode: !!src.imageMode, imageReviewOpen: src.imageReviewOpen || 0,
               geomMode: !!src.geomMode, geomFlags: src.geomFlags || 0 }
    }
    let last = null
    for (let i = 0; i < MAX_ITERS; i++) {
      const v = await runVerify(src, 'Verify')
      last = v
      if (!v.ranSuccessfully) { log('verify could not run for ' + src.name + ' — ' + (v.note || '')); break }
      const nUng = v.ungrounded.length, nUnc = v.uncovered.length, nRev = (v.reverted || []).length
      log(src.name + ' iter ' + (i + 1) + ': ' + nUng + ' ungrounded, ' + nUnc + ' uncovered' +
          (nRev ? ' (' + nRev + ' date/unit reformat' + (nRev > 1 ? 's' : '') + ' auto-reverted by code)' : ''))
      if (worklistSize(v) === 0)
        return { src: src.name, chunks: src.chunks.length, iters: i, converged: true, reverted: nRev,
                 imageMode: !!src.imageMode, imageReviewOpen: src.imageReviewOpen || 0,
                 geomMode: !!src.geomMode, geomFlags: src.geomFlags || 0 }
      // ONE Edit-only pass-2 on the residual (code already reverted the date/unit reformats)
      await agent(resolvePrompt(src, v), { label: 'resolve:' + src.name, phase: 'Resolve', schema: WROTE_SCHEMA })
    }
    log('WARNING: ' + src.name + ' did not fully converge in ' + MAX_ITERS + ' iters; residual left for human review.')
    return { src: src.name, chunks: src.chunks.length, iters: MAX_ITERS, converged: false, residual: last,
             imageMode: !!src.imageMode, imageReviewOpen: src.imageReviewOpen || 0,
             geomMode: !!src.geomMode, geomFlags: src.geomFlags || 0 }
  }
)

const unconverged = perSource.filter(Boolean).filter(s => !s.converged)
log('Phase A complete: ' + (perSource.length - unconverged.length) + '/' + perSource.length + ' sources converged clean.')

// ───────────────────────── Phase B: fragments + carried-forward structure, then views ─────────────────────────
phase('EventLog')
const compiledDir = extractedDir + '/compiled'
const structureFile = compiledDir + '/structure.md'
// per-source FRAGMENTS (parallel, each bounded to ONE extract). A stall or death affects only its own
// fragment, and on resume only the changed pieces re-run. As it writes, EACH fragment also DECLARES —
// recall-safe — this source's date span; the driver carries
// those forward (union → populated set; earliest date → document order) with NO re-reading pass.
// fragments are INTERNAL intermediate pieces — they live in compiled/_fragments/ (underscore = internal,
// like _staged/_chunks), NOT directly in compiled/. This keeps compiled/ as exactly the cross-source
// analysis surface (the views + structure.md) so downstream enumeration (the orchestrator's doc-manifest)
// never mistakes a raw per-source fragment for a compiled analysis document.
const fragmentFile = (name) => compiledDir + '/_fragments/event-log-' + name + '.md'
const fragmentPrompt = (s) =>
  '## Phase B — event-log FRAGMENT for source: ' + s.name + '\n\n' +
  'Read the Phase-A extract(s) for this source ONLY — the files matching `' + s.extractGlob + '` ' +
  '(there may be several chunk files; read them all, in order) — and do NOT read the other sources. ' +
  'Emit one entry per dated, sourced datum found in them — each carrying its `[src:]` forward — to ' +
  '`' + fragmentFile(s.name) + '`. Non-dated static facts: put under a "## Undated / static" heading. ' +
  'Reorganise only — never interpret, average, convert units, or flag "noteworthy".\n\n' +
  '## ALSO DECLARE (recall-safe) — capture in your StructuredOutput from the content already in hand ' +
  '(no extra pass, no re-read):\n' +
  '- `firstDate` / `lastDate`: the earliest and latest date that appears in this source, copied ' +
  'VERBATIM as written (leave blank only if the source is wholly undated).\n' +
  SCRATCH_RULE + '\n' + RETURN_RULE + '\nStructured output only.'

// ── Fragment-reuse pre-check (cfg.reuseFragments, default OFF): a fragment already on disk is NOT
//    re-generated. ONE deterministic agent derives each existing fragment's declaration WITHOUT re-reading
//    the raw source — dates from the fragment's own ISO date headings. (It used to also derive view
//    CATEGORIES from a deterministic labeler; there are no views to be a category of.) The fragment-level analog of the
//    Phase-A disk-skip: on resume it skips the 20 Opus fragment agents entirely. Fresh runs (flag off, or
//    no fragment on disk) always (re)write the fragment via the agent above, unchanged.
const reuseFragByName = {}
if (cfg.reuseFragments) {
  const reuseBash = sources.map(s => {
    const f = fragmentFile(s.name)
    return 'echo "=== ' + s.name + ' ==="\n' +
      'if [ -f "' + f + '" ]; then\n' +
      '  echo "DATES $(grep -oE \'^#{1,4}[[:space:]]+[0-9]{4}-[0-9]{2}-[0-9]{2}\' "' + f + '" | ' +
      'grep -oE \'[0-9]{4}-[0-9]{2}-[0-9]{2}\' | sort | sed -n \'1p;$p\' | tr \'\\n\' \' \')"\n' +
      'else\n  echo MISSING\nfi'
  }).join('\n')
  const rc = await agent(
    '## Phase B — fragment-reuse pre-check (which per-source fragments are already on disk)\n\n' +
    'For each source, report whether its event-log fragment already exists and, if so, its date span. ' +
    'NOT a judgement task — run the commands and report exactly what they print. ' +
    'Each `=== <name> ===` block prints EITHER a `DATES <first> <last>` line (the fragment\'s earliest and ' +
    'latest ISO date headings; may be empty if the fragment is wholly undated), OR the literal `MISSING` ' +
    '(no fragment on disk).\n\n' +
    '```bash\n' + reuseBash + '\n```\n\n' +
    'For each source return `{name, exists, firstDate, lastDate}`: `exists`=true iff the block ' +
    'printed a DATES line (NOT MISSING); `firstDate`/`lastDate` = the two tokens on the DATES line ' +
    '(blank if none). ' +
    'Do NOT edit any file, do NOT extract — this is READ-ONLY. ' + NO_SIDEWORK_RULE + ' Structured output only.',
    { label: 'fragment-check', phase: 'EventLog', schema: FRAG_REUSE_SCHEMA }
  ).then(r => r || { ranSuccessfully: false, sources: [] })
  if (rc.ranSuccessfully && Array.isArray(rc.sources)) for (const c of rc.sources) if (c && c.name) reuseFragByName[c.name] = c
}

const fragmentResults = await parallel(sources.map(s => () => {
  const ru = reuseFragByName[s.name]
  if (ru && ru.exists === true) {           // reuse the on-disk fragment — no agent, derived declaration
    return Promise.resolve({ name: s.name, chunks: s.chunks || [s.converted], reused: true,
      decl: { file: fragmentFile(s.name), done: true,
              firstDate: ru.firstDate || '', lastDate: ru.lastDate || '' } })
  }
  return agent(fragmentPrompt(s), { label: 'eventlog:' + s.name, phase: 'EventLog', schema: FRAGMENT_SCHEMA })
    .then(r => ({ name: s.name, chunks: s.chunks || [s.converted], decl: r || null }))
}))
const reusedFragCount = fragmentResults.filter(fr => fr.reused).length
if (cfg.reuseFragments) log('Fragment reuse: ' + reusedFragCount + '/' + sources.length + ' fragment(s) reused from disk (not re-generated).')
const fragByName = {}
for (const fr of fragmentResults) fragByName[fr.name] = fr
const fragments = fragmentResults.filter(fr => fr.decl && fr.decl.done).map(fr => fragmentFile(fr.name))
log('Assembled ' + fragments.length + '/' + sources.length + ' event-log fragments.')

// Carried-forward STRUCTURE — captured here from the chunk plan (document + ordered pieces,
// already in hand) + the fragment declarations (date span). No agent re-reads the fragments to
// build this. The declared CATEGORIES are gone with the views they used to select: nothing now
// chooses a subset of the record to compile, so there is no subset to declare.
// structure.md — documents ordered by earliest declared date, each with its ordered pieces + date span.
const structDocs = sources.map(s => {
  const d = (fragByName[s.name] || {}).decl || {}
  return { name: s.name, chunks: s.chunks || [s.converted],
           first: (d.firstDate || '').trim(), last: (d.lastDate || '').trim() }
}).sort((a, b) => {
  const ka = dateSortKey(a.first), kb = dateSortKey(b.first)
  return ka < kb ? -1 : ka > kb ? 1 : a.name < b.name ? -1 : a.name > b.name ? 1 : 0
})
const structureMd =
  '# Structure manifest\n' +
  'Documents in earliest-declared-date order, each with its ordered source pieces (from the chunk plan) ' +
  'and its declared date span. Captured at chunk/extract time — no re-reading pass. The ordering is ' +
  'advisory; the timeline places each passage in time from its own words.\n\n' +
  structDocs.map(d =>
    '## ' + d.name + '  (dates: ' + (d.first || '—') + ' … ' + (d.last || '—') + ')\n' +
    d.chunks.map(c => '- piece: ' + c).join('\n')).join('\n\n') + '\n'
await agent(writeVerbatimPrompt(structureFile, structureMd, 'structure.md'),
  { label: 'write:structure', phase: 'EventLog', schema: WROTE_SCHEMA })

// ── Timeline: the ONE cross-source artifact. Nothing in it is written by a model. ─────────
//    Three steps, and only the middle one involves an agent at all:
//      1. segment.py plan — a clinic letter, a lab report, an imaging study is ONE record and
//         becomes one block whole; a multi-record bundle splits at its own repeated boundary.
//         Neither needs a model.
//      2. one agent per NARRATIVE source (an interview, the person's own notes), which returns
//         BOUNDARIES ONLY — the first few words of each new passage, copied. Never prose. A
//         boundary that is not found verbatim, or is found twice, fails the build by name.
//      3. build.py copies those byte ranges out; verify.py re-reads every source and confirms
//         each block is byte-identical to its OWN declared span. That check is the gate.
//    build.py is the only script here with a whole-file write path, and it runs once.
phase('Timeline')
const timelineFile = extractedDir + '/timeline.md'
const segDir = extractedDir + '/_timeline'
const boundDir = segDir + '/boundaries'
const onlyJson = segDir + '/sources.json'
const indexJson = segDir + '/index.json'
// The run already knows its sources, so the document is built from exactly those — never from a
// sweep of whatever happens to be on disk, which is how model-written files get in as "sources".
const onlyList = JSON.stringify(sources.map(s => s.converted))
const segPlan = await agent(
  '## Timeline 1/3 — plan the segmentation (deterministic, no judgement)\n\n' +
  'Run the commands and report exactly what they print. NOT a judgement task.\n\n' +
  '```bash\nmkdir -p "' + segDir + '" "' + boundDir + '"\n' +
  'cat > "' + onlyJson + '" <<\'SRCJSON\'\n' + onlyList + '\nSRCJSON\n' +
  'python3 ' + SEGMENT + ' plan --corpus / --sources ' + TIMELINE_SOURCES +
  ' --only "' + onlyJson + '" --out "' + segDir + '"\n```\n\n' +
  'Return {ranSuccessfully, narratives:[<the source paths listed as needing boundaries>], note}. ' +
  NO_SIDEWORK_RULE + ' Structured output only.',
  { label: 'timeline-plan', phase: 'Timeline', schema: {
    type: 'object', properties: { ranSuccessfully: { type: 'boolean' },
      narratives: { type: 'array', items: { type: 'string' } }, note: { type: 'string' } } } }
).then(r => r || { ranSuccessfully: false, narratives: [] })
const narratives = Array.isArray(segPlan.narratives) ? segPlan.narratives : []
log('Timeline: ' + (narratives.length
  ? narratives.length + ' narrative source(s) need passage boundaries'
  : 'no narrative sources — every block is a whole record, no agent involved'))

// One boundary agent per narrative source. It reads a prompt segment.py wrote and answers with
// boundary strings only; it never writes a word of the document.
if (narratives.length) {
  await parallel(narratives.map(n => () => agent(
    '## Timeline 2/3 — passage boundaries for ONE source\n\n' +
    'Read `' + segDir + '/dispatch/' + '`, find the dispatch file for `' + n + '` (its name is a ' +
    'hash; the file names the source at the top), and follow it EXACTLY. It asks for ONE thing: the ' +
    'first few words of each new passage, COPIED character for character from the text it shows you.\n\n' +
    'Do not summarise, title, describe or rewrite anything. A script copies the text between your ' +
    'boundaries byte for byte and the build FAILS, naming you, if a boundary is not found verbatim ' +
    'or is found twice.\n\n' +
    'Write your answer as JSON to `' + boundDir + '/<the dispatch file\'s basename>.json` in the ' +
    'form {"boundaries": ["...", "..."]}. ' + SCRATCH_RULE + '\n' + RETURN_RULE +
    ' Structured output only.',
    { label: 'boundaries:' + String(n).split('/').pop().replace(/[^A-Za-z0-9._-]+/g, '-').slice(0, 48),
      phase: 'Timeline',
      schema: WROTE_SCHEMA })))
}

// Collect, build, verify. The verify is the gate: if a single character of a single block does not
// match its own source span, this reports it and the run does not get a clean timeline.
const built = await agent(
  '## Timeline 3/3 — build the document and verify every block against its source\n\n' +
  'Run the commands and report exactly what they print. NOT a judgement task.\n\n' +
  '```bash\n' +
  'python3 ' + SEGMENT + ' collect --corpus / --sources ' + TIMELINE_SOURCES +
  ' --plan "' + segDir + '" --boundaries "' + boundDir + '" --out "' + indexJson + '"\n' +
  'python3 ' + TLBUILD + ' --corpus / --sources ' + TIMELINE_SOURCES +
  ' --index "' + indexJson + '" --only "' + onlyJson + '" --out "' + timelineFile + '"' +
  ' --ledger "' + segDir + '/ledger.json"\n' +
  'python3 ' + TLVERIFY + ' --doc "' + timelineFile + '" --corpus / --sources ' +
  TIMELINE_SOURCES + ' --strict\n```\n\n' +
  'Return {ranSuccessfully, blocks:<the block count build.py printed>, ' +
  'verified:<true iff verify.py exited 0 and printed no FAIL line>, note:<the verify.py output, ' +
  'verbatim, if it printed any FAIL line>}. ' + NO_SIDEWORK_RULE + ' Structured output only.',
  { label: 'timeline-build', phase: 'Timeline', schema: {
    type: 'object', properties: { ranSuccessfully: { type: 'boolean' },
      blocks: { type: 'number' }, verified: { type: 'boolean' }, note: { type: 'string' } } } }
).then(r => r || { ranSuccessfully: false, blocks: 0, verified: false })

const timelineBlocks = Number(built.blocks || 0)
const timelineVerified = built.verified === true
if (!timelineVerified) {
  log('Timeline: NOT verified — ' + (built.note || 'verify.py did not confirm every block ' +
      'against its own source span') + '. The document is not trustworthy as a verbatim record ' +
      'until this is resolved; nothing downstream should quote from it.')
} else {
  log('Timeline: ' + timelineBlocks + ' block(s), every one byte-identical to its own source span.')
}

// ── Spot-check + source index (the Step-1 finish-line artifacts) ─────────────────────────
// spot-check.md AGGREGATES the per-source verify results already computed above (each source's
// residual grounding/coverage worklist + the Phase-B grounding hops) into the per-source accuracy
// summary the investigate finish-line reads — no new computation. index.md is the minimal source
// manifest (a converted raw source is PRIMARY by nature). Both are NON-gated, census-visible
// `extracted/` top-level files, and the extraction-check hook skips their basenames. They are written
// through the Write tool (like every other derived file here) — NEVER a bash `>` into extracted/, which
// the cleanup-block denies mid-run.
phase('Spotcheck')
const spotCheckFile = extractedDir + '/spot-check.md'
const indexFile = extractedDir + '/index.md'
const ps = perSource.filter(Boolean)
const cleanSrc = ps.filter(s => s.converged)
const dirtySrc = ps.filter(s => !s.converged)
const wlLines = (arr) => (Array.isArray(arr) && arr.length)
  ? arr.map(a => '  - `' + (a.reason || '?') + '` ' + (a.token || a.quote || '') +
      (a.line != null ? ' (L' + a.line + ')' : '') + (a.source ? ' [' + a.source + ']' : '')).join('\n')
  : '  - (none)'
const perSourceMd = ps.map(s => {
  const imgHeld = s.imageMode && (s.imageReviewOpen || 0) > 0
  const head = '### ' + s.src + '  (chunks: ' + (s.chunks != null ? s.chunks : '?') +
    ', iters: ' + (s.iters != null ? s.iters : '?') + ') — ' +
    (!s.converged ? 'UNCONVERGED — residual findings for human review'
      : s.trustAccepted ? 'REUSED FROM DISK — operator-accepted, ' + (s.trustResidual || 0) + ' grounding item(s) not re-verified (advisory)'
      : imgHeld ? 'CONVERGED (agreed rows) — ' + s.imageReviewOpen + ' held for human sign-off'
      : s.imageMode ? 'CONVERGED CLEAN (dual-vision, all rows agreed)'
      : s.geomMode ? 'CONVERGED CLEAN (geom, deterministic)' : 'CONVERGED CLEAN')
  if (s.converged && s.trustAccepted) {
    return head + '\n' +
      '- reused from disk AS-IS (Phase A skipped): ' + (s.trustResidual || 0) + ' grounding item(s) ' +
      'NOT re-verified this run — ADVISORY, non-gating. Operator judged the document sufficiently ' +
      'complete; see the run dev note for the underlying grounder limitation.'
  }
  if (s.converged) {
    return head + '\n' +
      '- residual: 0 ungrounded, 0 uncovered (grounding + DATA-coverage drained to empty)' +
      (s.imageMode ? '\n- image (dual-vision): ' + (imgHeld
        ? s.imageReviewOpen + ' disagreement(s) HELD in review.json for human sign-off — verdict needs-review'
        : 'all rows agreed across two independent reads, 0 held') : '') +
      (s.geomMode ? '\n- vector-pdf (geom): reconstructed from word geometry' + (s.geomFlags
        ? '; ' + s.geomFlags + ' header/footer/misaligned row(s) flagged for human spot-read (advisory)'
        : '; no association-integrity flags') : '') +
      (s.reverted ? '\n- code auto-reverted ' + s.reverted + ' date/unit reformat(s) to the verbatim source form' : '')
  }
  const r = s.residual || {}
  return head + '\n' +
    '- ungrounded (' + ((r.ungrounded && r.ungrounded.length) || 0) + '):\n' + wlLines(r.ungrounded) + '\n' +
    '- uncovered (' + ((r.uncovered && r.uncovered.length) || 0) + '):\n' + wlLines(r.uncovered)
}).join('\n\n')
// A7 — the machine-readable ACCURACY VERDICT the investigate orchestrator gates Step 1 on (fresh AND
// resume). Computed from values already in hand — any unconverged source (dirtySrc), and a timeline
// that did not verify block-for-block against its own sources. The
// orchestrator's readVerdict() greps this exact token off spot-check.md and HALTS the run unless
// clean:true, so a real accuracy failure stops the pipeline instead of being logged and built upon. This
// file NEVER halts or throws on the verdict — it only writes the token; the halt is enforced solely in
// the orchestrator, so standalone /extract-health-data is unaffected. The token is a single-line HTML
// comment emitted immediately AFTER the H1 (the file still opens with a heading, so the census wellFormed
// heuristic is undisturbed) and is position-robust: the reader greps ACCURACY-VERDICT wherever it sits.
const verdictFailures = []
for (const s of dirtySrc) verdictFailures.push({ kind: 'unconverged', detail: String(s.src) })
// The timeline is the run's ONE cross-source artifact, so a timeline that does not verify halts
// the run. This is a stricter gate than the per-view grounding it replaces: that asked whether a
// summary's values were traceable to a source, which tolerated a summary at all; this asks
// whether every block is byte-identical to its own declared source span, which nothing written
// by a model can pass.
if (!timelineVerified) verdictFailures.push({ kind: 'timeline-unverified',
  detail: (built.note || 'verify.py did not confirm every block against its own source span') })
if (!timelineBlocks) verdictFailures.push({ kind: 'timeline-empty',
  detail: 'the timeline has no blocks — every later stage reads it, so an empty one is a silent ' +
          'loss of the whole record, not a run with nothing to say' })
// An image source's AGREED rows ground clean, but any dual-vision DISAGREEMENT is a data fact a human
// must sign off — it blocks Step-1 regardless of grounding. Cleared ONLY by a human signing off the
// review.json entry, never by a flag flip (so a flag-off rollback cannot launder a held row clean).
for (const s of ps) if ((s.imageReviewOpen || 0) > 0)
  verdictFailures.push({ kind: 'image-needs-review', detail: s.src + ': ' + s.imageReviewOpen + ' unsigned dual-vision disagreement(s) — human sign-off required' })
// NON-GATING advisories: sources accepted from disk as-is (trustDiskExtracts) with grounding residual
// that was NOT re-verified this run. Recorded in the machine-readable verdict so the acceptance is never
// silent, but does NOT set clean:false (the operator judged the documents sufficiently complete).
const trustAdvisories = ps.filter(s => s.trustAccepted).map(s =>
  ({ kind: 'trust-disk-accepted', detail: s.src + ': ' + (s.trustResidual || 0) + ' grounding item(s) accepted un-reverified (operator)' }))
const accuracyVerdict = { clean: verdictFailures.length === 0, failures: verdictFailures,
  ...(trustAdvisories.length ? { advisories: trustAdvisories } : {}) }
const verdictToken = '<!-- ACCURACY-VERDICT ' + JSON.stringify(accuracyVerdict) + ' -->'
const trustAcceptedSrc = ps.filter(s => s.trustAccepted)
const spotCheckMd =
  '# Spot-check — per-source extraction accuracy\n' +
  verdictToken + '\n\n' +
  'Deterministic grounding + DATA-coverage results per source. A source is CONVERGED CLEAN when its ' +
  'worklist (ungrounded tokens + uncovered source values) drained to zero; an UNCONVERGED source lists ' +
  'its residual worklist for human review. Date/unit reformats are auto-reverted by code, so they never ' +
  'appear as residual.\n\n' +
  '## Summary\n' +
  '- sources: ' + ps.length + '\n' +
  '- converged clean: ' + cleanSrc.length + '/' + ps.length + '\n' +
  '- unconverged (human review): ' + (dirtySrc.length ? dirtySrc.map(s => s.src).join(', ') : 'none') + '\n' +
  (trustAcceptedSrc.length
    ? '- reused from disk, operator-accepted with grounding residual (ADVISORY, non-gating): ' +
      trustAcceptedSrc.map(s => s.src + ' (' + (s.trustResidual || 0) + ')').join(', ') + '\n'
    : '') +
  '- timeline: ' + timelineBlocks + ' block(s) — ' + (timelineVerified
      ? 'every one re-read from its own source file and confirmed byte-identical to the exact byte '
        + 'range it declares. Nothing in it was written by a model.'
      : 'NOT VERIFIED. Do not quote from it and do not build on it until this is resolved.')
    + '\n\n' +
  (timelineVerified ? ''
    : '## The timeline did not verify\n' + (built.note || 'verify.py did not confirm every block '
      + 'against its own declared source span') + '\n\n') +
  '## Per source\n' + (perSourceMd || '(no sources)') + '\n'
const indexRows = sources.map(s => '| ' + s.name + ' | ' + s.extractFile + ' | primary |').join('\n')
const indexMd =
  '# Source index\n\n' +
  'Converted raw sources for this investigation. Every entry is a PRIMARY record — the faithful converted ' +
  'text of a source the person provided; no derived or secondary sources are indexed here.\n\n' +
  '| source | extract file | class |\n| --- | --- | --- |\n' + (indexRows || '| (none) | | |') + '\n'
const spotWrites = await parallel([
  () => agent(writeVerbatimPrompt(spotCheckFile, spotCheckMd, 'spot-check.md'),
    { label: 'write:spot-check', phase: 'Spotcheck', schema: WROTE_SCHEMA }),
  () => agent(writeVerbatimPrompt(indexFile, indexMd, 'index.md'),
    { label: 'write:index', phase: 'Spotcheck', schema: WROTE_SCHEMA }),
])
if (!(spotWrites[0] && spotWrites[0].done)) log('WARNING: spot-check.md write did not confirm.')
if (!(spotWrites[1] && spotWrites[1].done)) log('WARNING: index.md write did not confirm.')

return {
  root: cfg.root,
  spotCheck: spotCheckFile,
  index: indexFile,
  sources: perSource.filter(Boolean),
  unconverged: unconverged.map(s => s.src),
  structure: structureFile,
  timeline: timelineFile,
  timelineBlocks,
  timelineVerified,
  summary: (perSource.length - unconverged.length) + '/' + perSource.length + ' sources converged; ' +
           'timeline ' + timelineBlocks + ' block(s), ' +
           (timelineVerified ? 'every one byte-identical to its own source span'
                             : 'NOT VERIFIED — do not quote from it') +
           (unconverged.length ? '; UNCONVERGED (human review): ' + unconverged.map(s => s.src).join(', ') : '') + '.',
}
