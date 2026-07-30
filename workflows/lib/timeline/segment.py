#!/usr/bin/env python3
"""Decide where each passage starts and stops. Never what it says.

This is the one step between converted sources and the document, and it is the only place a
model touches the corpus before `build.py` copies bytes out of it. What the model returns is a
list of **boundaries** — the first few words of each new passage, copied exactly — and nothing
else. No summary, no title, no paraphrase, no description. If a boundary it returns cannot be
found in the source, or is found twice, this stops and names it rather than matching
approximately.

Most sources need no model at all. A clinic letter, a lab report, an imaging study is one
record: it becomes one block, whole, and nothing is decided. Only a long free narrative — an
interview, a person's own written notes — has to be cut into passages, because it covers thirty
years and nobody would read one block that long.

    segment.py plan    --corpus C --sources S --out plan/     # index for the easy ones,
                                                              # dispatches for the rest
    segment.py collect --corpus C --sources S --plan plan/ \\
                       --boundaries b/ --out index.json       # the full block index
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tl  # noqa: E402
from build import enumerate_corpus, load_rules  # noqa: E402

MIN_BLOCK = 200          # bytes; below this a "passage" is a fragment, not a passage
MAX_NARRATIVE_BLOCK = 12000

BOUNDARY_PROMPT = """You are cutting one long spoken or written account into passages. You decide
ONLY where each passage begins. You do not summarise it, title it, describe it or change one
character of it — a script copies the text between your boundaries byte for byte, and a check
fails the whole build if a single character differs.

<source name="{name}">
{text}
</source>

Return JSON only:

  {{"boundaries": ["...", "...", "..."]}}

Each string is the **first few words of a new passage, copied exactly from the text above** —
enough words to appear exactly once in the whole source, usually six to twelve. The first passage
starts at the beginning of the source, so do NOT include a boundary for it.

What makes a boundary:

- The account moves to a different period, a different part of the body, a different episode, or
  a different subject. Those are the cuts.
- **Where the speaker jumps back in time mid-flow, cut there.** "oh another thing to mention,
  actually going back in time" starts a new passage even though it sits in the middle of a later
  story — that passage gets dated where it belongs, not where it was said.

What ruins a boundary:

- Cutting mid-sentence. Always start at the beginning of a sentence or a list item.
- Cutting a hedge away from what it hedges. If someone says "I think it was 2015, but I can't
  quite remember" — that whole thing is one passage. Putting the cut between them deletes the
  uncertainty as surely as rewriting it would, and it is the single most damaging thing you can
  do here.
- Boundaries so close together that a passage is a fragment. Aim for a paragraph or more.
- A string that appears more than once in the source. Add words until it is unique.
- Retyping. Copy from the text above; do not type from memory. A near-miss is a hard failure,
  not a warning.

Aim for passages of a few hundred to a couple of thousand words. Fewer, longer passages are
better than many short ones: a passage that carries its own context is a passage that can be
read on its own later."""


def kinds_of(rules: dict[str, object]) -> tuple[list[str], dict[str, str]]:
    k = dict(rules.get("kinds", {}))                       # type: ignore[arg-type]
    return list(k.get("narrative", [])), dict(k.get("bundle", {}))


def match_any(rel: str, globs: list[str]) -> str | None:
    """Match a rule against the path AND the bare filename.

    A source's folder is not stable across the pipeline: a narrative sits in the person's corpus
    under whatever folder they keep interviews in, and the SAME narrative reaches the extractor as
    a converted file under `extracted/sources/`. A rule that only matched the folder would classify
    it correctly in one place and silently wrongly in the other — and the wrong answer here is a
    thirty-year account emitted as one undivided block, with the passage-cutting step never running
    at all. Matching the basename too makes the rule mean the same thing wherever the file is.
    """
    base = rel.rsplit("/", 1)[-1]
    for g in globs:
        gbase = g.rsplit("/", 1)[-1]
        if (fnmatch.fnmatch(rel, g) or fnmatch.fnmatch("/" + rel, g)
                or fnmatch.fnmatch(base, gbase)):
            return g
    return None


def after_header(raw: bytes) -> int:
    """The converter's own <<<...>>> banner is not part of the record."""
    pos = 0
    for line in raw.split(b"\n"):
        if line.startswith(b"<<<"):
            pos += len(line) + 1
        else:
            break
    return pos


def trim(raw: bytes, a: int, b: int) -> tuple[int, int]:
    while a < b and raw[a:a + 1].isspace():
        a += 1
    while b > a and raw[b - 1:b].isspace():
        b -= 1
    return a, b


def classify(rel: str, narrative: list[str], bundle: dict[str, str]) -> tuple[str, str]:
    if match_any(rel, narrative):
        return "narrative", ""
    for g, rx in bundle.items():
        if fnmatch.fnmatch(rel, g):
            return "bundle", rx
    return "document", ""


def plan(corpus: Path, rules: dict[str, object], out: Path,
         only: list[str] | None = None) -> int:
    narrative, bundle = kinds_of(rules)
    eligible, _ = enumerate_corpus(corpus, rules, only)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dispatch").mkdir(exist_ok=True)

    blocks: list[dict[str, object]] = []
    pending: list[str] = []
    counts = {"document": 0, "bundle": 0, "narrative": 0}

    for rel in sorted(eligible):
        raw = tl.source_bytes(corpus / rel)
        kind, rx = classify(rel, narrative, bundle)
        counts[kind] += 1
        head = after_header(raw)
        if kind == "document":
            a, b = trim(raw, head, len(raw))
            if b - a >= 1:
                blocks.append({"src": rel, "span": f"{a}:{b}", "date": "", "prec": "unknown"})
            continue
        if kind == "bundle":
            text = raw.decode("utf-8")
            cuts = sorted({head} | {m.start() for m in re.finditer(rx, text) if m.start() > head}
                          | {len(raw)})
            for x, y in zip(cuts, cuts[1:]):
                a, b = trim(raw, x, y)
                if b - a >= MIN_BLOCK:
                    blocks.append({"src": rel, "span": f"{a}:{b}", "date": "", "prec": "unknown"})
            continue
        # narrative — the only kind that needs a model, and only for the cut points
        (out / "dispatch" / f"{tl.sha(rel)}.txt").write_text(
            BOUNDARY_PROMPT.format(name=rel, text=raw[head:].decode("utf-8")), encoding="utf-8")
        pending.append(rel)

    (out / "pending.json").write_text(
        json.dumps({"narrative": {tl.sha(r): r for r in pending}}, indent=1) + "\n",
        encoding="utf-8")
    (out / "settled.json").write_text(json.dumps({"blocks": blocks}, indent=1) + "\n",
                                      encoding="utf-8")
    print(f"{len(eligible)} eligible sources: {counts['document']} whole documents, "
          f"{counts['bundle']} bundles, {counts['narrative']} narratives")
    print(f"{len(blocks)} blocks settled with no model involved")
    if pending:
        print(f"{len(pending)} narrative source(s) need boundaries → {out / 'dispatch'}")
        print("each dispatch asks for boundary strings only; a reply goes to "
              "<boundaries>/<same-name>.json")
    return 0


def resolve_boundaries(corpus: Path, rel: str, given: list[str]) -> list[tuple[int, int]]:
    raw = tl.source_bytes(corpus / rel)
    head = after_header(raw)
    offsets = [head]
    for i, s in enumerate(given, start=1):
        if not str(s).strip():
            tl.die(f"{rel}: boundary {i} is empty")
        b = str(s).encode("utf-8")
        n = raw.count(b, head)
        if n == 0:
            tl.die(f"{rel}: boundary {i} is not in the source, so it was not copied from it: "
                   f"{str(s)[:70]!r}")
        if n > 1:
            tl.die(f"{rel}: boundary {i} appears {n} times, so it does not say where to cut. "
                   f"Give more words: {str(s)[:70]!r}")
        offsets.append(raw.index(b, head))
    if offsets != sorted(offsets):
        tl.die(f"{rel}: the boundaries are not in the order they appear in the source")
    if len(set(offsets)) != len(offsets):
        tl.die(f"{rel}: two boundaries land on the same place")
    offsets.append(len(raw))

    spans: list[tuple[int, int]] = []
    for x, y in zip(offsets, offsets[1:]):
        a, b = trim(raw, x, y)
        if b > a:
            spans.append((a, b))

    # A passage below the minimum is a fragment — a bare section heading, a one-line aside. It is
    # merged FORWARD into the passage that follows it, which can only make a block bigger. Cutting
    # is what strips a hedge from what it hedges; joining never can. Nothing is dropped, and every
    # merge is named so a bad boundary set is visible rather than quietly absorbed.
    merged = spans
    out: list[tuple[int, int]] = []
    i = 0
    while i < len(merged):
        a, b = merged[i]
        while b - a < MIN_BLOCK and i + 1 < len(merged):
            print(f"NOTE: {rel} {a}:{b} is {b - a} bytes — too short to stand as a passage, so it "
                  f"is joined to the one after it. Nothing is dropped.")
            i += 1
            b = merged[i][1]
        if b - a < MIN_BLOCK and out:
            print(f"NOTE: {rel} {a}:{b} is the last passage and only {b - a} bytes, so it is "
                  f"joined to the one before it. Nothing is dropped.")
            pa, _pb = out.pop()
            a, b = pa, b
        if b - a > MAX_NARRATIVE_BLOCK:
            print(f"NOTE: {rel} {a}:{b} is {b - a} bytes — one long passage. Nothing is lost, "
                  f"but it will be hard to place in time as a single piece.")
        out.append((a, b))
        i += 1
    return out


def collect(corpus: Path, rules: dict[str, object], plan_dir: Path, boundaries: Path,
            out: Path) -> int:
    settled = json.loads((plan_dir / "settled.json").read_text(encoding="utf-8"))["blocks"]
    pending = json.loads((plan_dir / "pending.json").read_text(encoding="utf-8"))["narrative"]
    blocks = list(settled)
    missing = []
    for key, rel in sorted(pending.items()):
        p = boundaries / f"{key}.json"
        if not p.exists():
            missing.append(rel)
            continue
        try:
            given = json.loads(p.read_text(encoding="utf-8"))["boundaries"]
        except (json.JSONDecodeError, KeyError) as e:
            tl.die(f"{rel}: the boundary reply is not usable — {e}")
        for a, b in resolve_boundaries(corpus, rel, list(given)):
            blocks.append({"src": rel, "span": f"{a}:{b}", "date": "", "prec": "unknown"})
    if missing:
        tl.die("no boundaries came back for: " + ", ".join(missing) + ". A narrative source with "
               "no boundaries would become one enormous block or be dropped entirely; neither is "
               "acceptable, so the build stops here.")

    # nothing may be emitted twice, and nothing may straddle another block
    per: dict[str, list[tuple[int, int]]] = {}
    for b in blocks:
        a, z = (int(x) for x in str(b["span"]).split(":"))
        per.setdefault(str(b["src"]), []).append((a, z))
    for src, spans in per.items():
        spans.sort()
        for (a1, b1), (a2, b2) in zip(spans, spans[1:]):
            if a2 < b1:
                tl.die(f"{src}: passages {a1}:{b1} and {a2}:{b2} overlap")

    out.write_text(json.dumps({"blocks": blocks}, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    covered = sum(b - a for spans in per.values() for a, b in spans)
    total = sum(len(tl.source_bytes(corpus / s)) for s in per)
    print(f"{len(blocks)} blocks from {len(per)} sources; {covered} of {total} bytes placed "
          f"({covered * 100 // max(total, 1)}%)")
    print(f"index: {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "collect"])
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--plan", type=Path, default=Path("segment-plan"))
    ap.add_argument("--boundaries", type=Path, default=Path("boundaries"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--only", type=Path,
                    help="a JSON array of corpus-relative paths — the exact source set")
    args = ap.parse_args()

    corpus = args.corpus.resolve()
    rules = load_rules(args.sources)
    only = json.loads(args.only.read_text(encoding="utf-8")) if args.only else None
    if args.mode == "plan":
        return plan(corpus, rules, args.out or args.plan, only)
    if not args.out:
        tl.die("--out is required: it is the block index build.py consumes")
    return collect(corpus, rules, args.plan, args.boundaries, args.out)


if __name__ == "__main__":
    sys.exit(main())
