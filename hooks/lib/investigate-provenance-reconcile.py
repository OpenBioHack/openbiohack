#!/usr/bin/env python3
"""investigate-provenance-reconcile.py — Layer 3(b): provenance-class reconciliation FLAG.

The forensic failure: a curated note DISTORTED facts — e.g. "sweet potato", a food the subject
never mentioned — and that distortion leaked downstream. A DERIVED/CURATED source is lower-
authority; a concrete factual claim it makes that is corroborated by NO primary/raw source is
unverifiable and should be surfaced for the subject to confirm — exactly like index.md's own
"Items Requiring Human Review". This is an ADVISORY FLAG, never a hard block (the caller emits it
as a WARN): a distorted curated fact is caught for confirmation, not silently trusted, on any
condition.

Given the primary corpus (the raw/primary-class extracts) and a curated/derived extract on stdin,
flag each distinctive factual token (alphabetic, length >= 6, not a stopword) that appears in the
curated extract's factual lines but in NONE of the primary sources. Interpretation-tagged lines are
skipped (they are interpretations, quarantined elsewhere, not facts to corroborate). Condition-
agnostic; no disease/food lists — the signal is purely "curated-only, absent from primary".

Usage:
  # explicit corpus (unit tests):
  python3 investigate-provenance-reconcile.py <primary_file.md> [<primary_file.md> ...] < curated_extract
  # auto corpus (hook): self-gate on the extract's own index.md class, assemble the primary
  # corpus from the sibling non-DERIVED extracts, then flag:
  python3 investigate-provenance-reconcile.py --auto <index.md> <self_basename> <extracted_dir> < curated_extract
Prints one flagged token per line; exit 1 if any flagged (advisory), else exit 0. In --auto mode
a NON-derived self (nothing to reconcile) exits 0 with no output.
"""
import sys, re, os, glob

INTERP = re.compile(r"\[interpretation\]|\[prior-analysis note\]|\*\*\[INFERRED\]\*\*", re.I)
DERIVED_CLASS = re.compile(
    r"\bDERIVED\b|\bPRIOR-ANALYSIS\b|\bcurated\b|\bdigitiz(?:ed|ation)\b"
    r"|\bprior analysis\b|\bprior digitization\b|\bbackground note\b",
    re.I,
)
NONCLAIM = {"index.md", "data-completeness.md", "spot-check.md"}


def index_is_derived(index_path, basename):
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception:
        return None  # unknown
    for ln in lines:
        if basename and basename in ln and DERIVED_CLASS.search(ln):
            return True
    return False


def auto_primaries(index_path, self_basename, extracted_dir):
    """Return primary-class sibling extract paths (non-DERIVED, non-manifest, not self)."""
    prims = []
    for p in sorted(glob.glob(os.path.join(extracted_dir, "*.md"))):
        b = os.path.basename(p)
        if b == self_basename or b in NONCLAIM:
            continue
        if index_is_derived(index_path, b):
            continue
        prims.append(p)
    return prims
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
STOP = set("""
about above after again against because before being below between could during
should through under until where which while would their there these those event
still after worse certain thing things something anything nothing across around
report reports reported record records note notes noted source sources status flags
subject background curated primary derived section extract patient sample result results
""".split())


def _strip_markers(s):
    # drop bracketed marker/citation spans ([self-report], [src: ...], [experiential: ...],
    # [interpretation], ...) and ** emphasis so tag text never leaks in as a "fact" token.
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = s.replace("*", " ")
    return s


def toks(s):
    s = _strip_markers(s)
    return [w.lower() for w in WORD.findall(s) if len(w) >= 6 and w.lower() not in STOP]


def main():
    args = sys.argv[1:]
    if args and args[0] == "--auto":
        # --auto <index> <self_basename> <extracted_dir>
        if len(args) < 4:
            sys.exit(0)
        index_path, self_basename, extracted_dir = args[1], args[2], args[3]
        if not index_is_derived(index_path, self_basename):
            sys.exit(0)  # only DERIVED/CURATED extracts are reconciled
        primaries = auto_primaries(index_path, self_basename, extracted_dir)
    else:
        primaries = args
    corpus = set()
    for p in primaries:
        try:
            with open(p, "r", encoding="utf-8") as f:
                corpus.update(toks(f.read()))
        except Exception:
            continue

    text = sys.stdin.read()
    flagged, seen = [], set()
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        if INTERP.search(s):
            continue                 # interpretation, not a fact to corroborate
        for t in toks(s):
            if t in corpus or t in seen:
                continue
            seen.add(t)
            flagged.append(t)

    for t in flagged:
        print(t)
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
