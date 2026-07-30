#!/usr/bin/env python3
"""Move a block to a different point in the document.

Moving is moving. The block is carried across with its identifier, its text, its provenance
comment and its sha unchanged. There is no delete path in this script and no re-creation path:
the same lines that came out go back in, and tl.relocate refuses the write if they do not.

Placing a block in time is done here. The stored date and precision are updated together, and
the heading is re-derived from them by the same lookup used everywhere else — so a
year-precision placement still cannot render as a specific day.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--block", required=True, help="identifier of the block to move")
    ap.add_argument("--after", help="identifier of the block it should sit after")
    ap.add_argument("--before", help="identifier of the block it should sit before")
    ap.add_argument("--date", help="restate when this passage belongs (with --prec)")
    ap.add_argument("--prec", choices=list(tl.PRECISIONS))
    ap.add_argument("--batch", default="")
    args = ap.parse_args()

    if bool(args.after) == bool(args.before):
        tl.die("name exactly one anchor: --after or --before")
    if bool(args.date) != bool(args.prec):
        tl.die("--date and --prec are given together or not at all — a date without its "
               "precision cannot be rendered honestly")
    if args.batch:
        tl.require_batch(args.doc, args.batch)

    doc = tl.parse(args.doc)
    block = doc.by_id(args.block)
    anchor_id = args.after or args.before
    if anchor_id == args.block:
        tl.die("a block cannot be moved relative to itself")
    anchor = doc.by_id(anchor_id)

    # ── the date, if it is being restated ─────────────────────────────────────
    # Only two lines change: the provenance comment's date fields and the heading derived from
    # them. The body is not re-rendered, so the words cannot move when the date does.
    if args.date is not None:
        tl.render_date(args.date, args.prec)
        a0, z0 = block.span
        tl.splice_many(args.doc, [
            (block.line_start, 1, [tl.render_open(block.bid, block.src, a0, z0, block.body,
                                                  args.date, args.prec, block.tags)]),
            (block.line_start + 2, 1, ["## " + tl.heading_for(
                block.bid, args.date, args.prec, block.tags, tl.opening_words(block.body))]),
        ])
        doc = tl.parse(args.doc)
        block = doc.by_id(args.block)
        anchor = doc.by_id(anchor_id)

    # ── the move itself: the block's own lines, carried across ────────────────
    before_text = tl.read_doc(args.doc)
    a, b = block.line_start, block.line_end + 1
    at = anchor.line_end + 1 if args.after else anchor.line_start
    if at != a:
        tl.relocate(args.doc, a, b, at)

    after = tl.parse(args.doc)
    moved = after.by_id(args.block)
    if moved.body != block.body or moved.attrs != block.attrs or moved.units != block.units:
        tl.die(f"{args.block} did not survive the move unchanged — the document has been "
               f"restored to nothing; investigate before re-running")
    if len([x for x in after.blocks if x.bid == args.block]) != 1:
        tl.die(f"{args.block} appears more than once after the move — it was copied, not moved")
    if len(after.blocks) != len(doc.blocks):
        tl.die("the move changed how many blocks the document has")
    if sorted(before_text.split("\n")) != sorted(tl.read_doc(args.doc).split("\n")):
        tl.die("the move changed the document's lines, not just their order")

    print(f"moved {args.block} {'after' if args.after else 'before'} {anchor_id}"
          + (f", placed at {tl.render_date(args.date, args.prec)}" if args.date is not None else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
