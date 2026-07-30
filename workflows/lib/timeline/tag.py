#!/usr/bin/env python3
"""Put up to three tags from the closed list on a block.

Two lines change: the provenance comment and the heading derived from it. The block's text, its
span and its sha are not touched, so `verify.py` still checks it against its source exactly as
before. Like every other tool here, it splices a named region; it does not rewrite the document.

A tag names which part of the record a block is, never what it means. The vocabulary is closed
and lives in references/timeline-source.md — an unknown tag is refused rather than added.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402


def vocabulary(sources: Path) -> set[str]:
    body = sources.read_text(encoding="utf-8")
    if "## 4. Tag vocabulary" not in body:
        tl.die(f"{sources} has no tag vocabulary section")
    section = body.split("## 4. Tag vocabulary")[1].split("## 5.")[0]
    return set(re.findall(r"`([a-z][a-z-]+)`", section))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--block", required=True)
    ap.add_argument("--tags", required=True, help="comma-separated, at most three, or empty to clear")
    ap.add_argument("--batch", default="")
    args = ap.parse_args()

    if args.batch:
        tl.require_batch(args.doc, args.batch)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if len(tags) > 3:
        tl.die(f"{len(tags)} tags — the heading carries at most three")
    vocab = vocabulary(args.sources)
    for t in tags:
        if t not in vocab:
            tl.die(f"tag {t!r} is not in the closed vocabulary. The list is in {args.sources}; "
                   f"add it there deliberately rather than inventing one here.")

    doc = tl.parse(args.doc)
    b = doc.by_id(args.block)
    a, z = b.span
    before_body, before_sha = b.body, b.attrs.get("sha")

    tl.splice_many(args.doc, [
        (b.line_start, 1, [tl.render_open(b.bid, b.src, a, z, b.body, b.date, b.prec, tags)]),
        (b.line_start + 2, 1, ["## " + tl.heading_for(b.bid, b.date, b.prec, tags,
                                                      tl.opening_words(b.body))]),
    ])

    after = tl.parse(args.doc).by_id(args.block)
    if after.body != before_body or after.attrs.get("sha") != before_sha:
        tl.die(f"tagging changed {args.block}'s text — refusing; restore the last dated copy")
    print(f"{args.block}: " + (" ".join(f"[{t}]" for t in tags) if tags else "tags cleared"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
