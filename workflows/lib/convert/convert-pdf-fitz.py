#!/usr/bin/env python3
"""convert-pdf-fitz.py — PyMuPDF (fitz) word-level text extraction for text-layer PDFs.

Primary text-PDF path for the extract-health-data converter. Unlike `pdftotext -layout`, it
returns every word WITH its bounding box, so a downstream position-aware binding check can verify
a numeric value sits next to its correct source label (the "right number, wrong row" failure).

Emits:
  <out_txt>   the reconstructed plain text (layout-ish: words grouped into lines, lines ordered
              top-to-bottom, columns left-to-right). NO provenance header — the bash converter
              prepends its own `<<<CONVERTED ARTIFACT ...>>>` header.
  --pos P     (optional) a JSON sidecar: [{"text","x0","y0","x1","y1","page"}] for every word,
              consumed by extract-atom-diff.py --positions.

Exit codes (any non-zero => the bash converter falls through to the UNCHANGED pdftotext/OCR path,
so behaviour is exactly equivalent when PyMuPDF is absent):
  0  success (a real text layer was extracted)
  2  usage error
  3  no / negligible text layer (scanned PDF) — fall back to OCR
  4  PyMuPDF missing or the PDF could not be opened — fall back
"""
import sys
import os
import json
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_txt")
    ap.add_argument("--pos", default=None)
    ap.add_argument("--min-chars", type=int, default=100,
                    help="below this many extracted chars, treat as scanned and fall back to OCR")
    try:
        args = ap.parse_args()
    except SystemExit:
        return 2

    try:
        import fitz  # PyMuPDF
    except Exception:
        return 4

    try:
        doc = fitz.open(args.pdf)
    except Exception:
        return 4

    lines_out = []
    words_pos = []
    try:
        for pno in range(doc.page_count):
            page = doc.load_page(pno)
            # words: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
            words = page.get_text("words")
            if not words:
                lines_out.append("===== PAGE %d =====" % (pno + 1))
                continue
            lines_out.append("===== PAGE %d =====" % (pno + 1))
            groups = {}
            for w in words:
                x0, y0, x1, y1, text, bno, lno, wno = w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7]
                if not str(text).strip():
                    continue
                groups.setdefault((bno, lno), []).append((x0, y0, x1, y1, text))
                words_pos.append({"text": text, "x0": round(x0, 1), "y0": round(y0, 1),
                                  "x1": round(x1, 1), "y1": round(y1, 1), "page": pno + 1})
            # order lines by their top y, then join words left-to-right
            def line_key(item):
                (_b, _l), ws = item
                return (min(w[1] for w in ws), min(w[0] for w in ws))
            for _key, ws in sorted(groups.items(), key=line_key):
                ws.sort(key=lambda w: w[0])
                lines_out.append(" ".join(str(w[4]) for w in ws))
    finally:
        doc.close()

    text = "\n".join(lines_out).strip() + "\n"
    # strip the page markers when counting real content for the scanned-PDF threshold
    content = "\n".join(l for l in text.split("\n") if not l.startswith("===== PAGE"))
    if len(content.strip()) < args.min_chars:
        return 3

    with open(args.out_txt, "w", encoding="utf-8") as f:
        f.write(text)
    if args.pos:
        with open(args.pos, "w", encoding="utf-8") as f:
            json.dump(words_pos, f, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
