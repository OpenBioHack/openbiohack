#!/usr/bin/env python3
"""Read-only. Check the document against the sources it declares.

Never writes. Can be run at any moment, and is run after every edit.

For every block: re-read the source it names, take the byte range it names, and confirm the text
in the document is that text — its own source's span, not merely a span of some source in the
corpus. A block attributed to the wrong file fails here even when its words appear verbatim in
another one.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402
from build import load_rules, match_any  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--sources", type=Path, help="the source contract, for the source-primacy "
                                                 "and tag-vocabulary checks")
    ap.add_argument("--strict", action="store_true",
                    help="also require tiling and heading checks to pass")
    args = ap.parse_args()

    corpus = args.corpus.resolve()
    doc = tl.parse(args.doc)
    fails: list[str] = []
    checked = 0

    vocab: set[str] = set()
    include: list[str] = []
    exclude: list[str] = []
    if args.sources:
        rules = load_rules(args.sources)
        include = list(rules["include"])      # type: ignore[arg-type]
        exclude = list(rules["exclude"])      # type: ignore[arg-type]
        body = args.sources.read_text(encoding="utf-8")
        vocab = set(re.findall(r"`([a-z][a-z-]+)`",
                               body.split("## 4. Tag vocabulary")[1].split("## 5.")[0]))

    # ── identifiers are unique ────────────────────────────────────────────────
    seen: set[str] = set()
    for b in doc.blocks:
        if b.bid in seen:
            fails.append(f"{b.bid}: appears more than once")
        seen.add(b.bid)

    for b in doc.blocks:
        a, z = b.span

        # ── source primacy: a block's source is on the declared list ──────────
        if args.sources:
            hit = match_any(b.src, exclude)
            if hit:
                fails.append(f"{b.bid}: its source {b.src} is excluded by rule {hit!r} — a "
                             f"derived or model-written file cannot be a source")
                continue
            if not match_any(b.src, include):
                fails.append(f"{b.bid}: its source {b.src} is not on the primary-source list")
                continue

        p = corpus / b.src
        if not p.exists():
            fails.append(f"{b.bid}: its source is gone: {b.src}")
            continue

        # ── byte identity against its OWN declared span ───────────────────────
        raw = tl.source_bytes(p)
        if z > len(raw):
            fails.append(f"{b.bid}: span {a}:{z} runs past the end of {b.src} "
                         f"({len(raw)} bytes) — the source changed after the block was taken")
            continue
        try:
            want = raw[a:z].decode("utf-8")
        except UnicodeDecodeError:
            fails.append(f"{b.bid}: span {a}:{z} of {b.src} no longer decodes as UTF-8")
            continue
        if b.body != want:
            fails.append(f"{b.bid}: the text in the document is not {b.src} bytes {a}:{z}. "
                         f"The source was edited after the block was taken, or the document was "
                         f"reflowed. Nothing is re-anchored automatically.")
            continue
        if tl.sha(b.body) != b.attrs.get("sha"):
            fails.append(f"{b.bid}: recorded sha {b.attrs.get('sha')} does not match the text")
            continue
        checked += 1

        # ── units tile the body exactly ───────────────────────────────────────
        joined = "".join(b.body[x:y] for x, y in b.units)
        if joined != b.body:
            fails.append(f"{b.bid}: its sentence units do not reconstruct the block "
                         f"({len(joined)} characters against {len(b.body)}) — a unit was dropped "
                         f"or the block was re-split")

        # ── tags ──────────────────────────────────────────────────────────────
        if len(b.tags) > 3:
            fails.append(f"{b.bid}: {len(b.tags)} tags — the heading carries at most three")
        if vocab:
            for t in b.tags:
                if t not in vocab:
                    fails.append(f"{b.bid}: tag {t!r} is not in the closed vocabulary")

        # ── the heading says what the stored date and precision say ───────────
        if args.strict:
            want_head = tl.heading_for(b.bid, b.date, b.prec, b.tags, tl.opening_words(b.body))
            if b.heading != want_head:
                fails.append(f"{b.bid}: heading is {b.heading!r} but its stored date "
                             f"{b.date!r}/{b.prec} and text give {want_head!r}")

    # ── tiling: block spans plus recorded skips partition each source ─────────
    if args.strict:
        used: dict[str, list[tuple[int, int]]] = {}
        for b in doc.blocks:
            used.setdefault(b.src, []).append(b.span)
        for src, spans in sorted(used.items()):
            spans.sort()
            for (a1, b1), (a2, b2) in zip(spans, spans[1:]):
                if a2 < b1:
                    fails.append(f"{src}: spans {a1}:{b1} and {a2}:{b2} overlap")
            cov = doc.coverage.get(src)
            if cov is None:
                fails.append(f"{src}: no coverage record, so nothing states which bytes were "
                             f"left out")
                continue
            n = len(tl.source_bytes(corpus / src))
            if cov.length != n:
                fails.append(f"{src}: coverage records {cov.length} bytes, the file has {n}")
                continue
            gaps: list[tuple[int, int]] = []
            cursor = 0
            for a, z in spans:
                if a > cursor:
                    gaps.append((cursor, a))
                cursor = max(cursor, z)
            if cursor < n:
                gaps.append((cursor, n))
            recorded = [(a, z) for a, z, _ in cov.skips]
            if gaps != recorded:
                fails.append(f"{src}: the recorded skips do not match the uncovered bytes "
                             f"(recorded {recorded[:4]}…, actual {gaps[:4]}…)")

    for f in fails:
        print("FAIL: " + f)
    if fails:
        print(f"\n{len(fails)} failure(s) across {len(doc.blocks)} blocks.")
        return 1
    total = sum(z - a for a, z in (b.span for b in doc.blocks))
    print(f"verify: {checked}/{len(doc.blocks)} blocks byte-identical to their own declared "
          f"source span ({total} bytes)")
    print(f"        {len(doc.coverage)} sources tiled, {len(doc.notes)} notes, "
          f"identifiers unique")
    return 0


if __name__ == "__main__":
    sys.exit(main())
