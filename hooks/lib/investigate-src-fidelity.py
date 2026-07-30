#!/usr/bin/env python3
"""investigate-src-fidelity.py — Layer 3(a): verbatim [src:]-quote fidelity for extraction outputs.

extract-health-data's core contract: "Every item carries a source ID ... + the verbatim source
quote it came from." A citation of the form  [src: F, <loc>, "<quote>"]  asserts that <quote>
appears verbatim in F. This check re-verifies that assertion for every citation whose target F is a
RESOLVABLE TEXT source (another extract / a .md/.txt source under the run): a quote that does NOT
resolve in F is a fabricated citation and is DENIED. This is what stops a fabricated [src:] from
laundering an injected claim past the Foundation gate's [src:] escape.

Only TEXT targets are checked. Binary/original captures (.pdf/.png/.jpg/...) cannot be re-read as
text in a hook, so their citations are SKIPPED (never false-denied) — those are covered by the raw
two-pass extraction verification upstream. Citations without a quoted span are skipped (nothing to
verify). Condition-agnostic; keys on the [src:] shape only.

Usage:  python3 investigate-src-fidelity.py <base_dir> < extract_content
        <base_dir> is the directory the extract is written into (its [src:] targets resolve
        relative to it, to it/.., and to the run root's extracted/).
Exit 1 + first fabricated citation on stdout; exit 0 if all verifiable quotes resolve.
"""
import sys, re, os

# [src: F , loc , "quote"]  — require the quoted span (single or double quotes).
CITE = re.compile(r'\[src:\s*([^,\]]+?)\s*,[^,\]]*,\s*(?:"([^"]+)"|“([^”]+)”)\s*\]')
TEXT_EXT = (".md", ".txt", ".tsv", ".csv", ".markdown")


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def resolve(f, base_dir):
    cands = [
        os.path.join(base_dir, f),
        os.path.join(base_dir, os.path.basename(f)),
        os.path.join(base_dir, "extracted", os.path.basename(f)),
        os.path.join(os.path.dirname(base_dir.rstrip("/")), os.path.basename(f)),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    text = sys.stdin.read()
    for m in CITE.finditer(text):
        f = m.group(1).strip()
        quote = m.group(2) if m.group(2) is not None else m.group(3)
        if not quote:
            continue
        # S## subject-pack ids and non-text/binary sources are not text-verifiable here.
        if re.match(r"^S\d+$", f):
            continue
        if not f.lower().endswith(TEXT_EXT):
            continue
        target = resolve(f, base_dir)
        if target is None:
            continue  # unresolvable target -> cannot verify, do not false-deny
        try:
            with open(target, "r", encoding="utf-8") as fh:
                body = norm_ws(fh.read())
        except Exception:
            continue  # unreadable/binary -> skip
        if norm_ws(quote) not in body:
            print('fabricated [src:] quote — "%s" does not appear in %s' % (quote[:80], os.path.basename(f)))
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
