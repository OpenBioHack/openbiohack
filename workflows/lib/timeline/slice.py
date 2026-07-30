#!/usr/bin/env python3
"""Read part of the document. Read-only, and it writes nothing.

There are no views any more. A stage that used to read `symptom-matrix.md` reads the timeline
and, if it needs a subset, addresses one here — by period, by tag, by source, by identifier. The
subset is printed; it is never materialised as a file, because a materialised subset is a view,
and a view replaces its source for whoever reads it, which is how compilation errors became
invisible in the first place.

Every line printed is either the document's own text or the document's own provenance.

    slice.py --doc D --from 2019 --to 2022
    slice.py --doc D --tags gut,urology --format ids
    slice.py --doc D --ids TL-S0042,TL-S0087
    slice.py --doc D --source _text/... --format table
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402


def year_of(b: tl.Block) -> str | None:
    if b.prec == "unknown" or not b.date:
        return None
    return b.date.split("..")[0][:4]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--from", dest="frm", help="earliest year to include, e.g. 2019")
    ap.add_argument("--to", help="latest year to include")
    ap.add_argument("--tags", help="comma-separated; a block matches if it carries any of them")
    ap.add_argument("--source", help="only blocks copied from this source path")
    ap.add_argument("--ids", help="comma-separated identifiers")
    ap.add_argument("--undated", action="store_true", help="only the blocks with no placement")
    ap.add_argument("--format", default="blocks", choices=["blocks", "ids", "table", "json"])
    ap.add_argument("--count", action="store_true", help="print how many match and stop")
    args = ap.parse_args()

    doc = tl.parse(args.doc)
    want_tags = {t for t in (args.tags or "").split(",") if t}
    want_ids = {i for i in (args.ids or "").split(",") if i}
    picked = []
    for b in doc.blocks:
        if want_ids and b.bid not in want_ids:
            continue
        if args.undated and b.prec != "unknown":
            continue
        if args.source and b.src != args.source:
            continue
        if want_tags and not (want_tags & set(b.tags)):
            continue
        y = year_of(b)
        if args.frm and (y is None or y < args.frm):
            continue
        if args.to and (y is None or y > args.to):
            continue
        picked.append(b)

    missing = want_ids - {b.bid for b in picked}
    if missing:
        tl.die(f"no such block: {', '.join(sorted(missing))}")

    if args.count:
        print(len(picked))
        return 0
    if args.format == "ids":
        print("\n".join(b.bid for b in picked))
        return 0
    if args.format == "table":
        print("| when | id | tags | opening words |")
        print("|---|---|---|---|")
        for b in picked:
            print(f"| {tl.render_date(b.date, b.prec)} | {b.bid} | "
                  f"{' '.join(b.tags) or '—'} | {tl.opening_words(b.body)} |")
        return 0
    if args.format == "json":
        print(json.dumps([{"id": b.bid, "date": b.date, "prec": b.prec, "tags": b.tags,
                           "src": b.src, "span": b.attrs["span"], "text": b.body}
                          for b in picked], ensure_ascii=False, indent=1))
        return 0
    for b in picked:
        print("\n".join(b.raw_lines))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
