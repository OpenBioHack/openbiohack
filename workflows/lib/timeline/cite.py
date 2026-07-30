#!/usr/bin/env python3
"""Resolve `[[TL-S0042]]` and `[[TL-S0042-u07]]` to the exact words.

This is how nobody ever retypes a quotation. An agent writes the identifier; this script
substitutes the text, read back out of the block's own source file at the block's own byte
range and cross-checked against what the document holds.

An unknown identifier is a hard error. Never an empty string, never a silently stale quote.

    cite.py get TL-S0042-u07 --json
    cite.py hydrate draft.md --out final.md
    cite.py check draft.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402


def resolve(doc: tl.Document, corpus: Path, ref: str) -> dict[str, object]:
    bid, _, unit = ref.partition("-u")
    block = doc.by_id(bid)
    a, z = block.span
    from_source = tl.slice_source(corpus / block.src, a, z)
    if from_source != block.body:
        tl.die(f"{bid}: the document and {block.src} bytes {a}:{z} no longer agree. The quote is "
               f"stale; nothing is substituted until verify.py passes.")
    if tl.sha(block.body) != block.attrs.get("sha"):
        tl.die(f"{bid}: recorded sha does not match the text — refusing to quote it")
    if not unit:
        return {"id": bid, "text": block.body, "src": block.src, "span": f"{a}:{z}",
                "date": block.date, "prec": block.prec}
    try:
        n = int(unit)
    except ValueError:
        tl.die(f"{ref}: a unit is written u01, u02, … — got {unit!r}")
        raise
    if not 1 <= n <= len(block.units):
        tl.die(f"{ref}: {bid} has {len(block.units)} sentence units, so there is no u{n:02d}")
    ua, ub = block.units[n - 1]
    return {"id": ref, "text": block.body[ua:ub], "src": block.src,
            "span": f"{a + len(block.body[:ua].encode('utf-8'))}:"
                    f"{a + len(block.body[:ub].encode('utf-8'))}",
            "date": block.date, "prec": block.prec}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["get", "hydrate", "check"])
    ap.add_argument("target", help="an identifier (get) or a file (hydrate, check)")
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="hydrate: where to write; default is stdout")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = tl.parse(args.doc)
    corpus = args.corpus.resolve()

    if args.mode == "get":
        got = resolve(doc, corpus, args.target)
        print(json.dumps(got, ensure_ascii=False) if args.json else got["text"])
        return 0

    text = Path(args.target).read_text(encoding="utf-8")
    refs = [m.group(0)[2:-2] for m in tl.CITE_RE.finditer(text)]
    if args.mode == "check":
        for r in refs:
            resolve(doc, corpus, r)          # dies on the first that does not resolve
        print(f"{len(refs)} citation(s) in {args.target}, all resolving to exact text")
        return 0

    out = tl.CITE_RE.sub(lambda m: str(resolve(doc, corpus, m.group(0)[2:-2])["text"]), text)
    if args.out:
        tl.atomic_write(args.out, out)
        print(f"hydrated {len(refs)} citation(s) → {args.out}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
