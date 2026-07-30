#!/usr/bin/env python3
"""geom-extract.py — deterministic, LLM-free structure-preserving extraction of a source's
word geometry into (a) a linearised reading-order .txt and (b) a structured extract whose
[src:] quotes are verbatim spans of that .txt.

Input: a word-box list (the converter's `.pos.json`: list of {text,x0,y0,x1,y1,page}) — the
same geometry PyMuPDF `get_text("words")` / Tesseract `image_to_data` produce.

Why: plain pdftotext reads multi-column tables top-to-bottom per column and SCRAMBLES the
name<->value<->range association. Word coordinates keep it: group by y (rows), bucket by x
(columns per page, auto-detected). Proven across multi-column lab panels, genotyping exports, and clinician letters.

Emits BOTH artifacts so cite_verify (grounds each quote as a whitespace-normalised substring
of --source .txt) checks the extract against THIS linearised .txt — reconstructed rows are
substrings of it by construction, so grounding holds correctly.

Association-integrity validation (NOT word-conservation, which is blind to misalignment):
per-row column-count vs modal + monotonic-x + each value's x-centre within its column band.
"""
import json
import statistics
import sys
from collections import Counter


def load_words(pos):
    """pos: list of {text,x0,y0,x1,y1,page}. Returns {page: [(x0,y0,x1,y1,text)]}."""
    by_page: dict[int, list[tuple[float, float, float, float, str]]] = {}
    for w in pos:
        t = (w.get("text") or "").strip()
        if not t:
            continue
        by_page.setdefault(int(w.get("page", 1)), []).append(
            (float(w["x0"]), float(w["y0"]), float(w["x1"]), float(w["y1"]), t)
        )
    return by_page


def median_space(words):
    """Median inter-word gap within rough y-bands = one space width `s` (per page)."""
    gaps: list[float] = []
    ws = sorted(words, key=lambda w: (round(w[1] / 3), w[0]))
    band, prev = None, None
    for w in ws:
        yb = round(w[1] / 3)
        if yb == band and prev is not None:
            g = w[0] - prev[2]
            if 0 < g < 60:
                gaps.append(g)
        band, prev = yb, w
    return statistics.median(gaps) if gaps else 4.0


def cluster_rows(words):
    """Group words into rows by y0 with a gap threshold ~0.6x median glyph height."""
    if not words:
        return []
    h = statistics.median([w[3] - w[1] for w in words]) or 10.0
    ws = sorted(words, key=lambda w: (w[1], w[0]))
    rows, cur, ry = [], [], None
    for w in ws:
        if ry is None or abs(w[1] - ry) <= h * 0.6:
            cur.append(w)
        else:
            rows.append(sorted(cur, key=lambda x: x[0]))
            cur = [w]
        ry = w[1]
    if cur:
        rows.append(sorted(cur, key=lambda x: x[0]))
    return rows


def row_cells(row, gutter):
    """Split a row into cells at inter-word gaps wider than `gutter`. Returns
    [(x0, x1, text)] per cell."""
    cells: list[tuple[float, float, str]] = []
    cx0 = cx1 = None
    buf: list[str] = []
    prev_x1 = None
    for x0, _, x1, _, t in row:
        if prev_x1 is not None and x0 - prev_x1 > gutter:
            cells.append((cx0, cx1, " ".join(buf)))
            buf, cx0 = [], None
        if cx0 is None:
            cx0 = x0
        cx1 = x1
        buf.append(t)
        prev_x1 = x1
    if buf:
        cells.append((cx0, cx1, " ".join(buf)))
    return cells


def cell_display(text):
    """The ONE cell string used identically in the .txt line, the visible extract datum, and (once
    delimited) the cite quote — so the quote is always a verbatim whitespace-normalised substring of
    the .txt and grounding holds. Verbatim except the pathological case where the cell contains BOTH
    a straight `"` and a curly `”` double-quote (no safe delimiter left): there straight->single,
    applied here so ALL three renderings share it (essentially never occurs in lab documents)."""
    if '"' in text and "”" in text:
        return text.replace('"', "'")
    return text


def cite_quote(disp):
    """Wrap `disp` in the double-quote style `cite_verify.CITE_RE` parses without truncating on an
    internal quote: straight `"..."` when the cell has no straight quote, else curly `“...”` (CITE_RE
    accepts both, and cell_display guarantees a cell with a straight `"` has no curly `”`)."""
    if '"' not in disp:
        return f'"{disp}"'
    return f"“{disp}”"


def linearise_page(words, name, page_no):
    """Reconstruct one page → (txt_lines, extract_lines, cell_grid). Row-ordered; cells
    joined by ' | ' where a real gutter separates them (readable + substring-groundable)."""
    s = median_space(words)
    gutter = max(2.0 * s, 12.0)
    rows = cluster_rows(words)
    txt_lines: list[str] = []
    extract_lines: list[str] = []
    grid: list[list[tuple[float, float, str]]] = []
    for ri, row in enumerate(rows):
        cells = row_cells(row, gutter)
        if not cells:
            continue
        grid.append(cells)
        disp = [cell_display(c[2]) for c in cells]
        # linearised text line: cells joined by ' | ' (the groundable reference-of-record)
        line = " | ".join(disp)
        txt_lines.append(line)
        # ONE data line per ROW (not per cell): the row's cells as a single datum, quoting the WHOLE
        # linearised line — so an analyte's name+value+range stay grounded TOGETHER. Per-cell emission
        # split them onto separate lines, and a downstream event-log entry that recombined "name: value"
        # could then cite only one cell's quote, leaving the other cell's tokens ungrounded (the Phase-B
        # QC pollution the live E2E surfaced). Grouped, every token is verbatim in the one row quote.
        datum = " ".join(disp)
        extract_lines.append(f"- {datum} [src: {name}, p{page_no} r{ri}, {cite_quote(line)}]")
    return txt_lines, extract_lines, grid


NUM = tuple("0123456789")
COMPARATORS = "<>=≤≥"
COL_GAP = 40.0  # x0 gap that separates two table columns (columns here sit >100pt apart; within-
#                column value spread is <~20pt, so 40 cleanly splits columns without merging them).


def has_number(text):
    return any(ch in NUM for ch in text)


def first_glyph_kind(text):
    """Kind of the first non-space glyph: 'value' (digit or comparator — a measured value/limit),
    'label' (a letter — an analyte name / prose), 'other' (bullet/symbol), or 'empty'."""
    for ch in text:
        if ch.isspace():
            continue
        if ch.isdigit() or ch in COMPARATORS:
            return "value"
        if ch.isalpha():
            return "label"
        return "other"
    return "empty"


def is_value_cell(text):
    return first_glyph_kind(text) == "value"


def is_label_cell(text):
    return first_glyph_kind(text) == "label"


def is_analyte_row(row):
    """A data row that binds an analyte name to >=1 measured value: a leading label cell followed by
    at least one value cell. Chart ticks / axis labels (all-value rows, no leading label) are NOT
    analyte rows — they carry no analyte<->value association to misalign."""
    return bool(row) and is_label_cell(row[0][2]) and any(is_value_cell(c[2]) for c in row)


def value_bands(grid):
    """Header-locked value columns, realised from data: the x0-clusters of value cells across analyte
    rows. A cluster is a real column only if its support >= max(2, round(0.34 * n_analyte_rows)); a
    lone drifted value, or a furniture number that slipped into an analyte row's y-band, is below
    support and so is NOT a band — the membership check below then flags it. Returns [(lo, hi)]."""
    analyte = [r for r in grid if is_analyte_row(r)]
    xs = sorted(c[0] for r in analyte for c in r if is_value_cell(c[2]))
    if not xs:
        return []
    clusters: list[list[float]] = [[xs[0]]]
    for x in xs[1:]:
        (clusters.append([x]) if x - clusters[-1][-1] > COL_GAP else clusters[-1].append(x))
    support = max(2, round(0.34 * len(analyte)))
    return [(min(c) - 1.0, max(c) + 1.0) for c in clusters if len(c) >= support]


def association_integrity(grid):
    """The real data-safety gate (NOT word-conservation, which is blind to misassociation). Flags:
    - rows whose column count deviates from the modal table-row count (structural split/merge);
    - non-monotonic x (a cell whose x0 precedes the previous cell's x1) => overlap/misbucket;
    - a value cell in an analyte row whose x0 falls outside every header-locked value-column band
      (value-x-in-band): a value drifted into a gutter or another column, or a chart tick pulled into
      the row. This is the check word-conservation cannot make — a misplaced value still conserves
      tokens. Boundary: two values that BOTH drift to the same wrong x form their own supported band
      and pass; the target is the realistic single-cell drift / orphan-number case.
    Returns list of {row, reason}. Empty = clean."""
    flags: list[dict] = []
    counts = [len(r) for r in grid if len(r) >= 2 and any(has_number(c[2]) for c in r)]
    modal = Counter(counts).most_common(1)[0][0] if counts else 0
    bands = value_bands(grid)
    for ri, row in enumerate(grid):
        is_data = len(row) >= 2 and any(has_number(c[2]) for c in row)
        odd_shape = bool(is_data and modal and abs(len(row) - modal) > 1)
        if odd_shape:
            flags.append({"row": ri, "reason": f"column-count {len(row)} != modal {modal}"})
        prev_x1 = None
        for c in row:
            if prev_x1 is not None and c[0] < prev_x1 - 1.0:
                flags.append({"row": ri, "reason": "non-monotonic x (cell overlap)"})
                break
            prev_x1 = c[1]
        # value-x-in-band only on NORMAL-shaped analyte rows: an odd-shaped row (header, chart-axis,
        # multi-section banner) already carries the column-count flag; band-checking it too just
        # double-flags known-odd rows. On a normal row a value out of band is the true misassociation
        # signal — a value that drifted into a gutter or another column without changing the count.
        if bands and not odd_shape and is_analyte_row(row):
            for c in row:
                if is_value_cell(c[2]) and not any(lo <= c[0] <= hi for lo, hi in bands):
                    flags.append({"row": ri, "reason":
                                  f"value {c[2]!r} x0={c[0]:.0f} outside value-column bands"})
    return flags


def run(pos, name):
    by_page = load_words(pos)
    txt_all: list[str] = []
    ext_all: list[str] = []
    all_flags: list[dict] = []
    for page_no in sorted(by_page):
        tl, el, grid = linearise_page(by_page[page_no], name, page_no)
        txt_all.extend(tl)
        ext_all.extend(el)
        for f in association_integrity(grid):
            f["page"] = page_no
            all_flags.append(f)
    return "\n".join(txt_all), "\n".join(ext_all), all_flags


def main():
    if len(sys.argv) < 3:
        print("usage: geom-extract.py <pos.json> <source-name> "
              "[--txt OUT.txt] [--extract OUT.md]", file=sys.stderr)
        sys.exit(2)
    pos = json.load(open(sys.argv[1]))
    name = sys.argv[2]
    txt, ext, flags = run(pos, name)
    args = sys.argv[3:]
    if "--txt" in args:
        open(args[args.index("--txt") + 1], "w").write(txt + "\n")
    if "--extract" in args:
        open(args[args.index("--extract") + 1], "w").write(ext + "\n")
    if "--txt" not in args and "--extract" not in args:
        print(txt)
    print(json.dumps({"name": name, "assoc_flags": flags,
                      "txt_lines": txt.count("\n") + 1,
                      "extract_lines": ext.count("\n") + 1}), file=sys.stderr)


if __name__ == "__main__":
    main()
