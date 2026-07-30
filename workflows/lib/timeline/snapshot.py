#!/usr/bin/env python3
"""Take a dated copy of the document before a batch of edits.

Backups are copies, not version control. `timeline.md` → `timeline-2026-07-27-pre-round2.md`,
sitting next to the original. Plain files. Nothing about the person's history goes into a
repository — the scripts are versioned, the history is not.

The copy is the rollback path for every phase before the cutover: restore it and the document is
exactly as it was.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--label", required=True,
                    help="what this copy is before, e.g. pre-round2")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="the copy's date stamp (defaults to today)")
    ap.add_argument("--list", action="store_true", help="list the copies that exist and stop")
    args = ap.parse_args()

    if args.list:
        for p in tl.snapshots_for(args.doc):
            print(f"{p.name}  {p.stat().st_size} bytes  sha {tl.sha(tl.read_doc(p))}")
        return 0

    if not args.doc.exists():
        tl.die(f"nothing to copy: {args.doc} does not exist")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.label):
        tl.die(f"label {args.label!r} must be lowercase letters, digits and hyphens")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        tl.die(f"date {args.date!r} must be YYYY-MM-DD")

    dest = args.doc.with_name(f"{args.doc.stem}-{args.date}-{args.label}{args.doc.suffix}")
    if dest.exists():
        tl.die(f"{dest.name} already exists — a dated copy is never overwritten. Use a different "
               f"label.")
    shutil.copy2(args.doc, dest)

    live = tl.sha(tl.read_doc(args.doc))
    if tl.sha(tl.read_doc(dest)) != live:
        tl.die(f"the copy does not match the document — {dest} is not trustworthy")
    print(f"copied {args.doc.name} → {dest.name}  (sha {live})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
