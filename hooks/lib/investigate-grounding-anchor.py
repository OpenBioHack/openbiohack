#!/usr/bin/env python3
"""investigate-grounding-anchor.py — Layer 2 of the memory-interpretation quarantine.

Per hypothesis block (### H<n>) in a hypothesis-set / working-hypothesis write, verify the
block's grounding does NOT rest SOLELY on a memory/curated INTERPRETATION or on index-flagged
DERIVED/CURATED sources. A block is inadmissible (DENY) iff it grounds on interpretation and/or
derived/curated sources yet carries NO admissible anchor, where an admissible anchor is any of:
  - a [src: F] whose F is NOT classified DERIVED/CURATED by extracted/index.md (a primary raw
    source, or a pipeline-internal derived-from-primary view like compiled/ or research/), or
  - a first-person observation line: **[STATED]** / [self-report] / [experiential: ...].

Condition-agnostic + filename-free: the DERIVED/CURATED classification keys ONLY on the
provenance-class STRINGS the extractor writes into index.md (Curated / DERIVED / PRIOR-ANALYSIS /
digitization / prior analysis), never on any specific extract filename or disease term.

Usage:  python3 investigate-grounding-anchor.py <index_md_path> < hypothesis_set_content
Exit 1 + "H<n> — <title>" of the first inadmissible block on stdout; exit 0 if all admissible.
Fail-closed: on an internal error the caller treats a non-zero exit as DENY.
"""
import sys, re, os
sys.path.insert(0, os.environ.get("IH_LIB", os.path.dirname(os.path.abspath(__file__))))
try:
    from investigate_canon import match_copy  # fold homoglyph/zero-width evasions of the markers
except Exception:
    def match_copy(s):
        return s

INTERP = re.compile(r"\[interpretation\]|\[prior-analysis note\]|\*\*\[INFERRED\]\*\*", re.I)
STATED = re.compile(r"\*\*\[STATED\]\*\*|\[self-report\]|\[experiential:", re.I)
SRC = re.compile(r"\[src:\s*([^,\]]+)")
# provenance-class strings that mark an extract as DERIVED/CURATED (lower-authority) in index.md.
DERIVED_CLASS = re.compile(
    r"\bDERIVED\b|\bPRIOR-ANALYSIS\b|\bcurated\b|\bdigitiz(?:ed|ation)\b"
    r"|\bprior analysis\b|\bprior digitization\b|\bbackground note\b",
    re.I,
)


def norm_src(s):
    """Canonical basename of a cited source: fold homoglyphs, strip a #fragment / ?query and
    surrounding whitespace, take the basename. Defeats the 'curated-notes.md#s1' evasion (H3)."""
    s = match_copy(s).strip()
    s = s.split("#", 1)[0].split("?", 1)[0].strip()
    return os.path.basename(s)


def looks_like_file(s):
    """A real source reference (has an extension or a path separator) — NOT a bare token / id.
    Kills the 'anchor satisfied by [src: S02] or [src: notes]' bypass (H2)."""
    s = s.split("#", 1)[0].split("?", 1)[0].strip()
    if re.match(r"^S\d+$", s):          # subject-pack ids are unverified memory refs, never anchors
        return False
    return ("/" in s) or bool(re.search(r"\.[A-Za-z0-9]{1,5}$", s))


def load_index_derived(index_path):
    """Return basename->bool 'is this extract flagged DERIVED/CURATED in index.md?'. A source is
    derived iff SOME index line names its basename as a DELIMITED TOKEN (not a mere substring — so
    'notes.md' does not match inside 'lab-notes.md', L2) AND carries a derived-class string.
    Unknown/absent basenames are NOT derived (pipeline-internal derived-from-primary views such as
    compiled/ and research/ are legitimately admissible)."""
    lines = []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            lines = match_copy(f.read()).split("\n")
    except Exception:
        lines = []

    def is_derived(basename):
        if not basename:
            return False
        tok = re.compile(r"(?<![\w.-])" + re.escape(basename) + r"(?![\w-])")
        for ln in lines:
            if tok.search(ln) and DERIVED_CLASS.search(ln):
                return True
        return False

    return is_derived


def blocks(text):
    """Yield (label, body) for each ### H<n> block. Tolerates a missing space after the hashes
    (###H1) so a no-space heading is still evaluated, not silently skipped (L1)."""
    cur_label, cur = None, []
    for ln in text.split("\n"):
        m = re.match(r"^\s*#{2,4}\s*(H\d+\b.*)$", ln)
        if m:
            if cur_label is not None:
                yield cur_label, "\n".join(cur)
            cur_label, cur = m.group(1).strip(), []
            continue
        # any other heading closes the current H block
        if re.match(r"^\s*#{1,4}\s+\S", ln) and cur_label is not None:
            yield cur_label, "\n".join(cur)
            cur_label, cur = None, []
            continue
        if cur_label is not None:
            cur.append(ln)
    if cur_label is not None:
        yield cur_label, "\n".join(cur)


def has_clean_observation(body):
    """A first-person observation line counts ONLY if it is not also carrying an interpretation
    marker on the same line (contradictory provenance — M2). Folds homoglyphs first."""
    for ln in body.split("\n"):
        fl = match_copy(ln)
        if STATED.search(fl) and not INTERP.search(fl):
            return True
    return False


def main():
    index_path = sys.argv[1] if len(sys.argv) > 1 else ""
    is_derived = load_index_derived(index_path)
    text = sys.stdin.read()

    for label, raw_body in blocks(text):
        fbody = match_copy(raw_body)          # fold homoglyph/zero-width evasions of the markers (L3)
        srcs = [s.strip() for s in SRC.findall(fbody)]
        has_interp = bool(INTERP.search(fbody))
        has_stated = has_clean_observation(raw_body)
        derived_srcs = [s for s in srcs if is_derived(norm_src(s))]
        # an admissible primary [src:] must be a real file reference (not a bare id/token) AND not
        # index-flagged derived. (Whether that file was actually read is enforced by write-check
        # Check 2 src_in_readlog, so a fabricated *.md name is caught there.)
        primary_srcs = [s for s in srcs if looks_like_file(s) and not is_derived(norm_src(s))]

        grounds_on_interp_or_derived = has_interp or bool(derived_srcs)
        has_admissible_anchor = has_stated or bool(primary_srcs)

        if grounds_on_interp_or_derived and not has_admissible_anchor:
            print(label[:200])
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
