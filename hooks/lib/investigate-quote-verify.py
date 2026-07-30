#!/usr/bin/env python3
"""investigate-quote-verify.py — SP1 proof-of-read (quote-and-grep).

An auditor proves it actually READ the dispatched artifact by returning N verbatim line-
numbered spans. This verifier:
  1. checks the auditor's DECLARED artifact_path == the DISPATCHED path (defeats the
     confabulation where an auditor "audits" the worked-example patient s1..s7 instead of the
     real draft, or invents a verdict);
  2. fixed-string greps each quote (whitespace-normalized) against THAT artifact;
  3. checks each quote resolves within +/-tolerance lines of its declared line number;
  4. requires at least <min_quotes> quotes.
Any failure -> exit 1 + reasons on stdout (the verdict is then discarded). Pass -> exit 0.

Usage:  python3 investigate-quote-verify.py <dispatched_artifact_path> [min_quotes] [tol] < auditor_yaml
"""
import sys
import re
import os

TOL_DEFAULT = 3
MIN_DEFAULT = 3


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def parse_yaml(text):
    """Return (declared_path, [(line:int, quote:str), ...]). Tolerant of the
    `artifact_path:` line and `- { line: N, quote: "..." }` / block entries."""
    declared = ""
    m = re.search(r'(?im)^\s*artifact_path\s*:\s*["\']?([^"\'\n]+?)["\']?\s*$', text)
    if m:
        declared = m.group(1).strip()
    quotes = []
    # inline form: line: N, quote: "..."  (double or single quoted)
    for lm in re.finditer(r'line\s*:\s*(\d+)\s*,\s*quote\s*:\s*"((?:[^"\\]|\\.)*)"', text):
        quotes.append((int(lm.group(1)), lm.group(2)))
    for lm in re.finditer(r"line\s*:\s*(\d+)\s*,\s*quote\s*:\s*'((?:[^'\\]|\\.)*)'", text):
        quotes.append((int(lm.group(1)), lm.group(2)))
    # block form:
    #   - line: 142
    #     quote: "..."
    if not quotes:
        for bm in re.finditer(r'line\s*:\s*(\d+)\s*\n\s*quote\s*:\s*["\'](.+?)["\']', text):
            quotes.append((int(bm.group(1)), bm.group(2)))
    return declared, quotes


def same_file(a, b):
    if not a or not b:
        return False
    if a == b:
        return True
    try:
        if os.path.realpath(a) == os.path.realpath(b):
            return True
    except Exception:
        pass
    return os.path.basename(a) == os.path.basename(b)


def main():
    if len(sys.argv) < 2:
        sys.stdout.write("quote-verify: usage error (no dispatched artifact path)")
        sys.exit(1)
    dispatched = sys.argv[1]
    min_q = int(sys.argv[2]) if len(sys.argv) > 2 else MIN_DEFAULT
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else TOL_DEFAULT
    text = sys.stdin.read()
    declared, quotes = parse_yaml(text)

    fails = []
    if not same_file(declared, dispatched):
        sys.stdout.write("SP1 FAIL: auditor audited the wrong file - declared artifact_path '%s' "
                         "but was dispatched on '%s'. Re-audit the exact dispatched file; do not "
                         "quote the worked examples." % (declared or "(none)", dispatched))
        sys.exit(1)
    if len(quotes) < min_q:
        sys.stdout.write("SP1 FAIL: only %d read-proof quote(s) provided; at least %d verbatim "
                         "line-numbered spans from %s are required." % (len(quotes), min_q, dispatched))
        sys.exit(1)
    try:
        with open(dispatched, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception:
        sys.stdout.write("SP1 FAIL: dispatched artifact could not be read at %s" % dispatched)
        sys.exit(1)
    norm_lines = [norm_ws(l) for l in lines]

    for ln, q in quotes:
        nq = norm_ws(q)
        if not nq:
            fails.append("empty quote at declared line %d" % ln)
            continue
        hits = [i + 1 for i, nl in enumerate(norm_lines) if nq in nl]
        if not hits:
            fails.append("quote not found in %s: \"%s\"" % (os.path.basename(dispatched), q[:60]))
            continue
        if not any(abs(h - ln) <= tol for h in hits):
            fails.append("quote resolves at line(s) %s but was declared at line %d (tol +/-%d): \"%s\""
                         % (",".join(map(str, hits[:3])), ln, tol, q[:50]))
    if fails:
        sys.stdout.write("SP1 FAIL (%d of %d quotes did not verify against %s):\n  - %s"
                         % (len(fails), len(quotes), os.path.basename(dispatched), "\n  - ".join(fails)))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
