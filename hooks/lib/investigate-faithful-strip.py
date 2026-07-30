#!/usr/bin/env python3
"""investigate-faithful-strip.py — L2/L3 faithful-strip engine.

Proves offering.md (the client doc) is a MECHANICAL strip of offering-draft.md: every client
section must equal the matching draft section after removing ONLY the allowed provenance
tokens ([src:]/[ledger:]/[grain:]/tier markers/verification:pending/orchestrator-memory only),
modulo whitespace + tag-removal debris. Any added word, dropped sentence, changed word, or
reordered prose -> FAIL. A homoglyph swapped into the client is a word difference -> FAIL
(the comparison is verbatim, NOT canonicalized).

Usage:  python3 investigate-faithful-strip.py <draft_path> [allowed_csv_or_json] < client_content
Exit 0 = faithful;  exit 1 = mismatch, with a one-line reason on stdout.
"""
import sys
import re
import difflib
import json

DEFAULT_ALLOWED = ["src", "ledger", "tier", "grain", "verification-pending", "orch-memory"]


def parse_allowed(arg):
    if not arg:
        return list(DEFAULT_ALLOWED)
    arg = arg.strip()
    if arg.startswith("["):
        try:
            return list(json.loads(arg))
        except Exception:
            pass
    return [x.strip() for x in arg.split(",") if x.strip()]


def norm_heading(line):
    return re.sub(r"\s+", " ", re.sub(r"^#{1,6}\s*", "", line)).strip().lower()


def split_sections(text):
    """-> (preamble_str, [(heading_line, heading_norm, body_str), ...])"""
    lines = text.split("\n")
    pre, secs = [], []
    cur_h = cur_n = None
    body = []
    for ln in lines:
        if re.match(r"^#{1,6}\s", ln):
            if cur_h is not None:
                secs.append((cur_h, cur_n, "\n".join(body)))
            cur_h, cur_n, body = ln, norm_heading(ln), []
        elif cur_h is None:
            pre.append(ln)
        else:
            body.append(ln)
    if cur_h is not None:
        secs.append((cur_h, cur_n, "\n".join(body)))
    return "\n".join(pre), secs


def strip_provenance(text, allowed):
    a = set(allowed)
    if "src" in a:
        text = re.sub(r"\[src:[^\]]*\]", "", text)
    if "ledger" in a:
        text = re.sub(r"\[ledger:[^\]]*\]", "", text)
    if "grain" in a:
        text = re.sub(r"\[grain:[^\]]*\]", "", text)
    if "tier" in a:
        text = re.sub(r"\bT[0-5]\s*[-–—]\s*T[0-5]\b", "", text)
        text = re.sub(r"\bT[0-5]\b", "", text)
    if "verification-pending" in a:
        text = re.sub(r"verification:\s*pending", "", text, flags=re.I)
    if "orch-memory" in a:
        text = re.sub(r"orchestrator-memory only", "", text, flags=re.I)
    return text


_PROV_ANY = re.compile(r"\[src:[^\]]*\]|\[ledger:[^\]]*\]|\[grain:[^\]]*\]|\bT[0-5]\b|verification:\s*pending|orchestrator-memory only", re.I)


def normalize(text):
    text = re.sub(r"\s+([.,;:)\]])", r"\1", text)   # debris before punctuation
    text = re.sub(r"([(\[])\s+", r"\1", text)        # debris after opener
    text = re.sub(r"\s+", " ", text)                  # collapse whitespace runs
    return text.strip()


def fail(msg):
    sys.stdout.write(msg)
    sys.exit(1)


def context(words, j, span=8):
    a = max(0, j - span)
    return " ".join(words[a:j + span])


def is_internal(heading):
    """A draft section heading marked [[draft-internal]] is NOT required in the client offer."""
    return "[[draft-internal]]" in heading.lower()


def strip_for_client(text, allowed):
    """Provenance-stripped draft body, readable (paragraph structure preserved) — the exact text
    the orchestrator should append to offering.md for a missing section."""
    t = strip_provenance(text, allowed)
    t = re.sub(r"[ \t]+([.,;:)\]])", r"\1", t)   # tag-removal debris before punctuation
    t = re.sub(r"([(\[])[ \t]+", r"\1", t)
    t = re.sub(r"[ \t]{2,}", " ", t)              # collapse runs of spaces, KEEP newlines
    return t.strip("\n")


def run_completeness(draft_path, allowed, client):
    """H2: offering.md must include EVERY client-required draft section (all sections whose
    heading is not [[draft-internal]]). Missing -> exit 1 with the exact section(s) to add."""
    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            draft = f.read()
    except Exception:
        fail("offer-completeness: offering-draft.md could not be read at %s" % draft_path)
    _, dsecs = split_sections(draft)
    _, csecs = split_sections(client)
    chead = set(n for _h, n, _b in csecs)
    missing = []
    for h, n, b in dsecs:
        if is_internal(h):
            continue
        if n not in chead:
            missing.append((h.strip(), strip_for_client(b, allowed)))
    if missing:
        parts = ["offer-completeness FAIL: offering.md is missing %d required section(s) from "
                 "offering-draft.md. Add EACH with a targeted Edit that appends the provenance-"
                 "stripped section below verbatim (or, if a section genuinely should not reach the "
                 "person, mark its draft heading with [[draft-internal]] and re-run):" % len(missing)]
        for h, content in missing:
            parts.append("\n===== MISSING SECTION =====\n%s\n\n%s" % (h, content))
        sys.stdout.write("\n".join(parts))
        sys.exit(1)
    sys.exit(0)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--completeness":
        if len(sys.argv) < 3:
            fail("offer-completeness: usage error (no draft path)")
        draft_path = sys.argv[2]
        allowed = parse_allowed(sys.argv[3] if len(sys.argv) > 3 else "")
        run_completeness(draft_path, allowed, sys.stdin.read())
        return
    if len(sys.argv) < 2:
        fail("faithful-strip: usage error (no draft path)")
    draft_path = sys.argv[1]
    allowed = parse_allowed(sys.argv[2] if len(sys.argv) > 2 else "")
    client = sys.stdin.read()
    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            draft = f.read()
    except Exception:
        fail("faithful-strip: offering-draft.md could not be read at %s" % draft_path)

    cpre, csecs = split_sections(client)
    dpre, dsecs = split_sections(draft)
    dmap = {}
    for h, n, b in dsecs:
        dmap.setdefault(n, (h, b))

    # preamble (text before any heading): only compared if the client has non-trivial preamble
    units = []
    if cpre.strip():
        units.append(("(preamble)", cpre, dpre))
    for h, n, b in csecs:
        if n not in dmap:
            fail("faithful-strip: client section '%s' has no matching section in offering-draft.md "
                 "- the client offer must be a strip of an existing draft section, not new prose." % h.strip())
        units.append((h.strip(), b, dmap[n][1]))

    for label, cbody, dbody in units:
        # client must itself be provenance-clean
        m = _PROV_ANY.search(cbody)
        if m:
            fail("faithful-strip: client section '%s' still carries a provenance token '%s' - strip "
                 "[src:]/[ledger:]/[grain:]/tier/verification tags from the client offer." % (label, m.group(0)[:40]))
        d_clean = normalize(strip_provenance(dbody, allowed))
        c_clean = normalize(cbody)
        dw, cw = d_clean.split(), c_clean.split()
        sm = difflib.SequenceMatcher(None, dw, cw, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                d_ctx = context(dw, i1) if dw else "(empty)"
                c_ctx = context(cw, j1) if cw else "(empty)"
                fail("faithful-strip mismatch in section '%s': draft says '...%s...' but client says "
                     "'...%s...' - the client offer may ONLY remove provenance tags; prose may not be "
                     "added, changed, dropped, or reordered. Re-strip from offering-draft.md." %
                     (label, d_ctx, c_ctx))
    sys.exit(0)


if __name__ == "__main__":
    main()
