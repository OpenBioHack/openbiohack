#!/usr/bin/env python3
"""Attach a note to a block without touching the block.

A note is the place for anything that is *about* a passage rather than *in* it: a transcription
error the person spotted, a correction they made later, a reason a dating was chosen. It sits
outside the block's own region, so the block's text, provenance and sha are unchanged by it and
`verify.py` still checks that block against its source exactly as before.

Notes are the only writing in the document that did not come out of a source, and they are
marked as such.
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
    ap.add_argument("--block", required=True)
    ap.add_argument("--note", required=True, help="the note text")
    ap.add_argument("--by", default="", help="who is saying it, if that matters")
    ap.add_argument("--batch", default="")
    args = ap.parse_args()

    if args.batch:
        tl.require_batch(args.doc, args.batch)
    if "-->" in args.note or "\n" in args.note:
        tl.die("a note cannot contain a comment terminator or a newline")

    doc = tl.parse(args.doc)
    block = doc.by_id(args.block)
    before = "\n".join(block.raw_lines)

    existing = doc.notes.get(args.block)
    who = f" — {args.by}" if args.by else ""
    line = f"*Note on {args.block}: {args.note}{who}*"
    if existing:
        at, close = existing
        tl.splice(args.doc, close, 0, [line])
    else:
        at = block.line_end + 1
        tl.splice(args.doc, at, 0,
                  ["", f"<!--TLN {args.block}-->", line, f"<!--/TLN {args.block}-->"])

    after = tl.parse(args.doc)
    if "\n".join(after.by_id(args.block).raw_lines) != before:
        tl.die(f"the note changed {args.block} itself — refusing; restore the last dated copy")
    print(f"note attached to {args.block}; the block itself is unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
