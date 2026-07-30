#!/usr/bin/env python3
"""Insert one new block at a named point. Surgical: nothing else in the document is touched.

The text comes out of a source file by byte range, exactly as at the initial build. This script
has no whole-file write path — it hands a single region to tl.splice, which refuses the write if
any line outside that region would change. A line the person typed into the document by hand is
outside every region, so it survives.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402
from build import load_rules, match_any  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--source", required=True, help="path of the source, relative to the corpus")
    ap.add_argument("--span", required=True, help="byte range in that source, START:END")
    ap.add_argument("--after", help="identifier of the block to sit after")
    ap.add_argument("--before", help="identifier of the block to sit before")
    ap.add_argument("--date", default="")
    ap.add_argument("--prec", default="unknown", choices=list(tl.PRECISIONS))
    ap.add_argument("--tags", default="")
    ap.add_argument("--sources", type=Path, help="the source contract, for source primacy")
    ap.add_argument("--batch", default="", help="the batch this edit belongs to")
    args = ap.parse_args()

    if bool(args.after) == bool(args.before):
        tl.die("name exactly one anchor: --after or --before")
    if args.batch:
        tl.require_batch(args.doc, args.batch)

    corpus = args.corpus.resolve()
    if args.sources:
        rules = load_rules(args.sources)
        hit = match_any(args.source, list(rules["exclude"]))     # type: ignore[arg-type]
        if hit:
            tl.die(f"{args.source} is excluded by rule {hit!r} — a derived or model-written file "
                   f"cannot become a block")
        if not match_any(args.source, list(rules["include"])):   # type: ignore[arg-type]
            tl.die(f"{args.source} is not on the primary-source list")

    doc = tl.parse(args.doc)
    anchor_id = args.after or args.before
    anchor = doc.by_id(anchor_id)

    a, b = (int(x) for x in args.span.split(":"))
    body = tl.slice_source(corpus / args.source, a, b)
    if not body.strip():
        tl.die(f"{args.source} {a}:{b} is only whitespace — there is nothing to insert")

    tags = [t for t in args.tags.split(",") if t]
    if len(tags) > 3:
        tl.die(f"{len(tags)} tags — the heading carries at most three")
    tl.render_date(args.date, args.prec)

    for existing in doc.blocks:
        if existing.src == args.source:
            x, y = existing.span
            if a < y and x < b:
                tl.die(f"{args.source} {a}:{b} overlaps {existing.bid} ({x}:{y}) — those words "
                       f"are already in the document")

    bid = doc.next_id()
    rendered = tl.render_block(bid, args.source, a, b, body, args.date, args.prec, tags,
                               tl.split_units(body))
    at = anchor.line_end + 1 if args.after else anchor.line_start
    edits: list[tuple[int, int, list[str]]] = [(at, 0, [""] + rendered.split("\n"))]

    # The coverage record for this source now covers different bytes. It is restated, not
    # recomputed from scratch: the other sources' records are not touched.
    spans = [x.span for x in doc.blocks if x.src == args.source] + [(a, b)]
    line = tl.coverage_line(args.source, tl.source_bytes(corpus / args.source), spans)
    cov = doc.coverage.get(args.source)
    if cov is not None:
        edits.append((cov.line, 1, [line]))
    else:
        edits.append((len(doc.lines) - 1, 0, [line]))
    tl.splice_many(args.doc, edits)

    print(f"inserted {bid} ({b - a} bytes from {args.source}) "
          f"{'after' if args.after else 'before'} {anchor_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
