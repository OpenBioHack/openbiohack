#!/usr/bin/env python3
"""investigate-mask-interpretation.py — Layer 1 of the memory-interpretation quarantine.

The grounding-assembly step (the dispatch that reads the extraction to build hypothesis-set.md)
must never SEE a memory/curated interpretation as if it were fact. This filter is piped over the
extraction bundle before that dispatch: every line carrying an interpretation marker
([interpretation] / [prior-analysis note] / **[INFERRED]**) has its interpretive PROSE replaced by

    [memory-interpretation withheld — re-derive from primary]

keeping the "a lead existed here" signal (and any [src:] pointer on the line) but removing the
conclusion itself, so the assembler is forced to re-derive from primary data. First-person
observations (**[STATED]** / [self-report] / [experiential:]) and measurement citations
([src: ...]) are preserved verbatim — those are admissible primary anchors, not interpretation.

Condition-agnostic + filename-free: keys ONLY on the extractor's own marker tags.

stdin: extraction bundle.  stdout: masked bundle.  (Never rewrites anything on disk.)
"""
import sys, re, os
sys.path.insert(0, os.environ.get("IH_LIB", os.path.dirname(os.path.abspath(__file__))))
try:
    from investigate_canon import match_copy  # fold homoglyph/zero-width evasions of the markers (L3)
except Exception:
    def match_copy(s):
        return s

PLACEHOLDER = "[memory-interpretation withheld — re-derive from primary]"

INTERP = re.compile(r"\[interpretation\]|\[prior-analysis note\]|\*\*\[INFERRED\]\*\*", re.I)
OBSERV = re.compile(r"\*\*\[STATED\]\*\*|\[self-report\]|\[experiential:", re.I)
SRC_SPAN = re.compile(r"\[src:[^\]]*\]")
LEAD = re.compile(r"^(\s*(?:[-*]\s+|\d+[.)]\s+)?)")
STRUCT = re.compile(r"^(\s*$|\s*#|\s*[-*]\s|\s*\d+[.)]\s|\s*\|)")


def _mask_interp_line(line):
    """Replace an interpretation line's prose with the placeholder, preserving any [src:] pointer."""
    lead = LEAD.match(line).group(1)
    srcs = SRC_SPAN.findall(line)
    return lead + PLACEHOLDER + ((" " + " ".join(srcs)) if srcs else "")


def main():
    text = sys.stdin.read()
    out = []
    masking = False   # inside a multiline interpretation span whose wrapped continuations we withhold
    for line in text.split("\n"):
        fl = match_copy(line)                       # detect markers on the folded copy (L3)
        interp = bool(INTERP.search(fl))
        obs = bool(OBSERV.search(fl))
        has_src = bool(SRC_SPAN.search(fl))
        if obs and not interp:
            # a clean first-person observation is an admissible anchor — preserve verbatim; ends a span
            masking = False
            out.append(line)
        elif interp:
            # M2: a line carrying an interpretation marker is withheld even if it ALSO wears an
            # observation tag (contradictory provenance — do not let the observation tag rescue it).
            out.append(_mask_interp_line(line))
            masking = True
        else:
            # M3: a wrapped continuation of the interpretation prose (not a structural line, not a
            # measurement citation) is part of the same span and is withheld too.
            if masking and not STRUCT.match(line) and not has_src:
                out.append(LEAD.match(line).group(1).rstrip())
            else:
                masking = False
                out.append(line)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
