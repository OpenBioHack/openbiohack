#!/usr/bin/env python3
"""extract-chunker.py — deterministic, section-aware, never-mid-table document chunker.

Partition a converted source .txt into an ordered set of CONTIGUOUS line-range chunks that break
only at real section boundaries, never inside a table / logical record, so a large single source
can be extracted in parallel and reassembled LOSSLESSLY.

LOSSLESSNESS IS GUARANTEED BY CONSTRUCTION (INV-CHUNK-LOSSLESS / INV-CHUNK-ORDER): a chunk is a
half-open line range [a, b); the chunk set is a PARTITION of [0, N) — ordered, contiguous, no gaps,
no overlaps, covering every line. Chunk text is "\\n".join(lines[a:b]); the document is
"\\n".join(lines). Therefore "\\n".join(chunk_texts) == original, BYTE-FOR-BYTE. The chunker only
CHOOSES cut indices; it never transforms, re-emits, or normalizes text, so there is nothing for a
reassembly to lose or duplicate. The extract-atom-diff.py oracle is then a redundant second proof,
not the mechanism.

Boundary detection is HYBRID and deterministic (no RNG, no wall-clock, sorted candidate sets):
  TEXT      banners (===/---), first line after a blank run, a structural-keyword lexicon.
  POSITION  font-size section titles from the .pos.json sidecar — the strongest signal on dense lab
            panels that have no blank lines and ambiguous ALLCAPS. Uses MEDIAN word height per
            visual line + a histogram-gap threshold above the body cluster (robust to a single tall
            glyph like ™ / a superscript that would fool a per-line MAX).

NEVER-MID-TABLE guard (INV-CHUNK-NOSPLIT): a candidate cut (gap before line i) is VETOED if the
nearest CONTENT line on BOTH sides is "tabular" (a record row). The neighbour search skips blank
AND `===== PAGE n =====` markers, so a table spanning a page break still sees a tabular row on each
side and vetoes the cut — this is what protects cross-page tables. A banner is always a safe cut.

Thresholds (INV-CHUNK-THRESHOLD): a doc under CHUNK_THRESHOLD bytes, or with no safe boundary
(a single un-sectioned giant table), stays exactly ONE chunk — never split mid-table, never 0.

Usage:
  python3 extract-chunker.py --source <src.txt> [--positions <pos.json>]
      [--emit-dir DIR --stem NAME]   # write <stem>.chunkNN.txt files + print their paths
      [--verify]                     # assert byte-lossless reassembly; exit 1 if it ever fails
Default: prints the boundaries JSON to stdout. Deterministic: same input -> identical output.
"""
import sys
import os
import re
import json
import argparse
from collections import Counter

# ---- tunables (corpus-calibrated; see SPIKE-chunker-design.md) --------------------------------
# Default raised 12000 -> 50000 (2026-07-02): the live A/B showed chunking a 22KB doc cost +4 agents,
# +140K tokens, and an extra converge/resolve round for ZERO benefit (identical fidelity, no speed
# gain) — a single agent extracts a doc this size cleanly in one pass. Nothing in the real corpus
# (max ~22KB) needs chunking; chunking is reserved for genuinely large sources. Tunable via
# --threshold / the workflow's args.chunkThreshold.
CHUNK_THRESHOLD = 50000   # bytes: below this a doc is left as exactly ONE chunk
TARGET_MIN = 6000         # bytes: minimum chunk size before a safe boundary is taken
OVERSIZE_FLAG = 16000     # bytes: flag (never split) a chunk that had to stay whole over this
BODY_MARGIN = 1.0         # pos.json fallback: header if median line height >= body + this

# ---- structural section-header lexicon (condition-agnostic; the font signal is the vendor-
#      agnostic backstop — do NOT let this lexicon become the primary detector) ----------------
HEADER_KEYWORDS = [
    "results overview", "clinical history", "report", "opinion", "impression", "summary",
    "findings", "interpretation", "recommendations", "comments", "microbiology", "bacteriology",
    "mycology", "parasitology", "commensal bacteria", "commensal abundance", "commensal balance",
    "dysbiosis patterns", "relative commensal", "physician notes", "digestive", "inflammation",
    "metabolite", "additional bacteria",
]

_PAGE_RE = re.compile(r"^\s*=+\s*PAGE\s+\d+\s*=+\s*$", re.I)
_BANNER_RE = re.compile(r"={6,}|-{6,}")
_CONV_HDR_RE = re.compile(r"^\s*<<<.*?>>>\s*$")
_NUMISH_RE = re.compile(r"^[<>]?[+-]?\d[\d,.\-–/eE^%]*$")
_UNITISH_RE = re.compile(r"^[A-Za-zµμ/%²³]{1,6}$")
_ALLCAPS_RE = re.compile(r"^[A-Z0-9 \-:,.()/&']{4,}$")


# =============================================================================================
# line reading / classification
# =============================================================================================
def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return text, text.split("\n")


def line_kind(line):
    s = line.strip()
    if s == "":
        return "blank"
    if _PAGE_RE.match(s):
        return "page"
    if _CONV_HDR_RE.match(line):
        return "convhdr"
    if _BANNER_RE.search(s):
        return "banner"
    return "content"


def is_tabular(line):
    """True if a CONTENT line looks like a table row / logical-record fragment. In the collapsed
    fitz two-column dump, table cells land as very short lines (a label fragment or a bare
    value/unit). Signals: <=2 whitespace tokens, or >=40% of tokens numeric/unit shaped. Designed
    to fail SAFE — a short prose line ('Normal OGD.') reads as tabular and only causes a spurious
    veto (fewer, larger, still-lossless chunks), never a mid-table cut."""
    s = line.strip()
    if not s:
        return False
    toks = s.split()
    if len(toks) <= 2:
        return True
    numish = sum(1 for t in toks if _NUMISH_RE.match(t) or _UNITISH_RE.match(t))
    return numish / len(toks) >= 0.4


# =============================================================================================
# TEXT-heuristic candidate boundaries (cut BEFORE line index i)
# =============================================================================================
def text_boundaries(lines):
    cands = set()
    for i in range(1, len(lines)):
        k = line_kind(lines[i])
        prev = lines[i - 1]
        s = lines[i].strip().lower()
        if k == "banner":
            cands.add(i)
        elif line_kind(prev) == "blank" and k not in ("blank", "page"):
            cands.add(i)                                  # first line after a blank run
        elif k == "content" and any(s == kw or s.startswith(kw) for kw in HEADER_KEYWORDS):
            cands.add(i)
        elif k == "content" and _ALLCAPS_RE.match(lines[i].strip()) \
                and any(c.isalpha() for c in lines[i]) and len(lines[i].strip().split()) <= 5:
            cands.add(i)                                  # short ALLCAPS line = candidate head
    return cands


# =============================================================================================
# POSITION-based header detection (font size) -> mapped to .txt line indices
# =============================================================================================
def _visual_lines(words):
    """Group pos.json words into visual lines by (page, y-band); return [(median_height, text)]."""
    bands = {}
    for w in words:
        try:
            key = (int(w["page"]), round(float(w["y0"]) / 3.0))
            bands.setdefault(key, []).append(w)
        except Exception:
            continue
    out = []
    for key in sorted(bands):
        ws = sorted(bands[key], key=lambda w: float(w.get("x0", 0)))
        hs = sorted(round(float(w["y1"]) - float(w["y0"]), 1) for w in ws)
        med = hs[len(hs) // 2] if hs else 0.0            # MEDIAN height (robust to one tall glyph)
        text = " ".join(str(w.get("text", "")) for w in ws).strip()
        out.append((med, text))
    return out


def _header_threshold(line_heights):
    """Header font threshold from the per-line MEDIAN-height histogram. The 'body' is not the global
    mode (a dense report's most-common height is often the tiny footnote font — the pollution the
    spike flagged), but the LARGEST height that still occurs SUBSTANTIALLY (>= 10% of the busiest
    height's word/line count). Section titles are the sparse heights above that. Threshold =
    body_top + BODY_MARGIN, which cleanly excludes a lone noise height just above the body cluster
    while capturing the genuine title cluster. Returns None if nothing sits above the body."""
    if not line_heights:
        return None
    cnt = Counter(round(h, 1) for h in line_heights)
    max_c = max(cnt.values())
    floor = max(2, max_c * 0.1)
    body_heights = [h for h, c in cnt.items() if c >= floor]
    body_top = max(body_heights) if body_heights else max(cnt)
    if not any(h > body_top for h in cnt):
        return None
    return body_top + BODY_MARGIN


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def position_header_lines(txt_lines, pos_path):
    """Return (set_of_line_indices, header_phrases). A visual line whose MEDIAN word height exceeds
    the histogram-gap threshold, with <=6 words and at least one letter, is a section title; map
    each such phrase back to the first matching .txt line (deterministic first hit)."""
    try:
        with open(pos_path, "r", encoding="utf-8") as f:
            words = json.load(f)
    except Exception:
        return set(), []
    if not isinstance(words, list) or not words:
        return set(), []

    vis = _visual_lines(words)
    thresh = _header_threshold([h for h, _ in vis])
    if thresh is None:
        return set(), []
    phrases = [t for (h, t) in vis
               if h >= thresh and len(_norm(t)) >= 4 and len(t.split()) <= 6 and any(c.isalpha() for c in t)]

    idx = set()
    norm_txt = [_norm(l) for l in txt_lines]
    for ph in phrases:
        nph = _norm(ph)
        first_tok = nph.split()[0] if nph.split() else ""
        for i, nt in enumerate(norm_txt):
            if not nt:
                continue
            if nt == nph or nt.startswith(nph) or (len(nph) >= 6 and nph in nt) \
               or (first_tok and len(first_tok) >= 5 and nt.startswith(first_tok)):
                idx.add(i)
                break
    return idx, phrases


# =============================================================================================
# never-mid-table guard
# =============================================================================================
def _nearest_content(lines, i, direction):
    j = i
    while 0 <= j < len(lines):
        k = line_kind(lines[j])
        if k in ("content", "banner"):
            return j
        j += direction
    return None


def _is_table_header(lines, idx):
    """A content line is a TABLE HEADER (column-title row) if it is itself non-tabular but the next
    content line (skipping blanks/page markers) is tabular. Cutting between such a header and its
    rows severs the header→row binding even though byte-losslessness holds (red-team F6)."""
    if idx is None or line_kind(lines[idx]) != "content" or is_tabular(lines[idx]):
        return False
    nxt = _nearest_content(lines, idx + 1, +1)
    return nxt is not None and line_kind(lines[nxt]) == "content" and is_tabular(lines[nxt])


def cut_is_safe(lines, i):
    """A cut BEFORE line i is unsafe (mid-table) iff the nearest content lines on BOTH sides are
    tabular. Blanks and page markers between them are skipped, so cross-page tables are protected.
    A banner immediately below is always a safe cut (explicit structural delimiter). Additionally,
    a cut is vetoed when it would land between a column HEADER row and its data rows — the header
    (a long-word, non-tabular line) is otherwise mistaken for a safe section boundary (red-team F6)."""
    above = _nearest_content(lines, i - 1, -1)
    below = _nearest_content(lines, i, +1)
    if above is None or below is None:
        return True
    if line_kind(lines[below]) == "banner":
        return True
    if is_tabular(lines[below]) and _is_table_header(lines, above):
        return False   # cutting between a table header and its rows
    return not (is_tabular(lines[above]) and is_tabular(lines[below]))


# =============================================================================================
# chunk assembly
# =============================================================================================
def byte_len(lines, a, b):
    return len("\n".join(lines[a:b]))


def chunk_document(text, lines, pos_path=None, threshold=CHUNK_THRESHOLD):
    """Return an info dict with the ordered chunk partition and diagnostics. `chunks` is a list of
    (start_line, end_line) half-open ranges partitioning [0, len(lines)). `threshold` (bytes) is the
    minimum document size worth splitting — below it the doc is left as exactly one chunk."""
    N = len(lines)
    info = {"n_lines": N, "n_bytes": len(text), "mode": None, "vetoed": [],
            "boundaries": [], "flags": [], "pos_header_phrases": []}

    if len(text) < threshold:
        info["mode"] = "single(threshold)"
        info["chunks"] = [(0, N)]
        return _finish(info, lines)

    tcands = text_boundaries(lines)
    pcands, phrases = (set(), [])
    if pos_path and os.path.exists(pos_path):
        pcands, phrases = position_header_lines(lines, pos_path)
    info["text_cands"] = len(tcands)
    info["pos_cands"] = len(pcands)
    info["pos_header_phrases"] = phrases
    info["mode"] = "hybrid(text+pos)" if pcands else "text-only"

    all_cands = sorted(tcands | pcands)
    safe, vetoed = [], []
    for i in all_cands:
        (safe if cut_is_safe(lines, i) else vetoed).append(i)
    info["vetoed"] = vetoed

    if not safe:
        info["mode"] += "/no-safe-boundary->single"
        info["chunks"] = [(0, N)]
        return _finish(info, lines)

    chunks = []
    start = 0
    for b in safe:
        if byte_len(lines, start, b) >= TARGET_MIN:
            chunks.append((start, b))
            start = b
    chunks.append((start, N))
    info["chunks"] = chunks
    info["boundaries"] = [c[0] for c in chunks[1:]]
    return _finish(info, lines)


def _finish(info, lines):
    for n, (a, b) in enumerate(info["chunks"]):
        if byte_len(lines, a, b) > OVERSIZE_FLAG:
            info["flags"].append("oversized_table:%d" % n)
    return info


def reassemble(lines, chunks):
    return "\n".join("\n".join(lines[a:b]) for (a, b) in chunks)


# =============================================================================================
# main
# =============================================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description="deterministic section-aware never-mid-table chunker")
    ap.add_argument("--source", required=True)
    ap.add_argument("--positions", default=None)
    ap.add_argument("--threshold", type=int, default=CHUNK_THRESHOLD,
                    help="min document size in bytes worth splitting (default %(default)s); below it "
                         "the source stays exactly one chunk")
    ap.add_argument("--emit-dir", default=None, help="write <stem>.chunkNN.txt files into DIR")
    ap.add_argument("--stem", default=None, help="basename stem for emitted chunk files")
    ap.add_argument("--verify", action="store_true",
                    help="assert byte-lossless reassembly (exit 1 if it ever fails)")
    args = ap.parse_args(argv)

    text, lines = read_lines(args.source)
    pos = args.positions if (args.positions and os.path.exists(args.positions)) else None
    info = chunk_document(text, lines, pos, threshold=args.threshold)
    chunks = info["chunks"]

    # losslessness is guaranteed by construction; --verify makes it an explicit gate.
    if args.verify:
        if reassemble(lines, chunks) != text:
            sys.stderr.write("extract-chunker: REASSEMBLY NOT LOSSLESS for %s\n" % args.source)
            return 1

    out = {"source": args.source, "n_lines": info["n_lines"], "n_bytes": info["n_bytes"],
           "mode": info["mode"], "n_chunks": len(chunks), "boundaries": info["boundaries"],
           "flags": info["flags"],
           "chunks": [{"chunk_num": n, "start_line": a, "end_line": b, "bytes": byte_len(lines, a, b)}
                      for n, (a, b) in enumerate(chunks)]}

    if args.emit_dir:
        stem = args.stem or os.path.splitext(os.path.basename(args.source))[0]
        os.makedirs(args.emit_dir, exist_ok=True)
        written = []
        for n, (a, b) in enumerate(chunks):
            p = os.path.join(args.emit_dir, "%s.chunk%02d.txt" % (stem, n))
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(lines[a:b]))
            written.append(p)
        out["emitted"] = written
        # cross-check the emitted files reassemble to the original (guard against IO surprises)
        joined = "\n".join(open(p, encoding="utf-8").read() for p in written)
        if joined != text:
            sys.stderr.write("extract-chunker: EMITTED CHUNKS DO NOT REASSEMBLE for %s\n" % args.source)
            return 1

    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
