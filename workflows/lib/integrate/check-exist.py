#!/usr/bin/env python3
"""check-exist.py — a deterministic present-and-non-empty check for a KNOWN, small set of files.

Why this exists: the workflow driver runs sandboxed and cannot stat disk itself, so it dispatches an agent
to run a script and RELAY the result. The full census (investigate-census.sh) walks the whole run tree and
returns a large artifact list; the relaying LLM agent intermittently TRUNCATES that list (drops real files),
so the driver concludes a present file is missing and redoes finished work — which once re-integrated and
corrupted fixture files. This helper answers ONLY the specific question the driver's resume/skip gates need
— "are these exact paths present and non-empty?" — and prints a TINY, fixed-size JSON (usually just an empty
`missing`), so the relay has nothing large to mangle. Deterministic (os.stat), no tree walk, no judgement.

CLI:  python3 check-exist.py --paths <p1> <p2> ... [--json]
Out:  {"ranSuccessfully": true, "checked": <n>, "missing": ["<abs path>", ...]}   (missing = absent OR empty)
Exit: 0 always on a successful run (presence is reported in `missing`, not the exit code).
"""
from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Compact present-and-non-empty check for a known set of paths.")
    ap.add_argument("--paths", nargs="+", required=True, help="the exact file paths to check")
    ap.add_argument("--json", action="store_true", help="emit JSON (the default and only format)")
    args = ap.parse_args()

    import os
    missing = []
    for p in args.paths:
        try:
            ok = os.path.isfile(p) and os.path.getsize(p) > 0
        except OSError:
            ok = False
        if not ok:
            missing.append(p)

    print(json.dumps({"ranSuccessfully": True, "checked": len(args.paths), "missing": missing},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
