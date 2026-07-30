#!/usr/bin/env python3
"""Build the timeline document. Once.

This is the only script in lib/timeline/ with a whole-file write path, and it is used to create
the document and then not used again. Everything after this is an insert, a move or an
annotation.

It does three things and nothing else:

  1. Enumerates the corpus against the declared primary-source list, so that every file is
     either eligible to become a block or excluded with a stated reason. Model-written trees are
     excluded by path rule — without that, model prose enters as a source and byte-identity then
     certifies it as verbatim with nothing able to tell it from a clinic letter.
  2. Copies the declared byte ranges out of those sources, character for character.
  3. Emits identifiers, tags, inline provenance and frozen sentence units.

It writes no prose of its own beyond the fixed header. If a declared span cannot be found or
cannot be decoded, it stops rather than guessing.
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

HEADER = """# Timeline

**Nothing here is summarised, paraphrased or shortened.** Every block below is your own words, or
the document's own words, copied character for character by script. The only decisions taken were
where each passage starts and stops, and where it sits in time — because you jumped around when
you spoke.

Each block carries a hidden comment naming the file it came from and the exact byte range, so the
document describes itself. A check can be run at any moment that re-reads every source and
confirms every block still matches it.

**One limit worth stating plainly.** Where a block came from a recording or a scan, it is
verbatim with respect to the *transcript* or the *scanned text* — speech recognition and OCR make
mistakes, and a system that copies faithfully will copy those mistakes faithfully too. Where you
spot one, say so and it gets a note attached; the block itself stays as it is.

Read the headings as *where this belongs in your life*, not as *when you said it*.

---
"""


def _blocks_of(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)\n```", text, re.S)
    if not blocks:
        tl.die(f"no json rules block in {path}")
    out: dict[str, object] = {}
    for i, b in enumerate(blocks):
        try:
            out.update(json.loads(b))
        except json.JSONDecodeError as e:
            tl.die(f"{path}: json block {i + 1} does not parse — {e}")
    return out


def load_rules(path: Path) -> dict[str, object]:
    """The source contract, plus a local overlay for whatever is specific to ONE corpus.

    The committed contract carries only rules that hold for any corpus: converter sidecars,
    viewer software, the document itself. A particular person's folder layout and the titles of
    the analyses sitting in it are theirs — naming them here would publish the shape of their
    working directory in an open-source repo. Those live in `<contract>.local.md` next to it,
    which is gitignored, and are merged in here: lists extend, maps update.
    """
    merged = _blocks_of(path)
    local = path.with_name(path.stem + ".local" + path.suffix)
    if local.exists():
        for k, v in _blocks_of(local).items():
            cur = merged.get(k)
            if isinstance(cur, list) and isinstance(v, list):
                merged[k] = cur + v
            elif isinstance(cur, dict) and isinstance(v, dict):
                merged[k] = {**cur, **v}
            else:
                merged[k] = v
    for key in ("include", "exclude", "exclude_reasons"):
        if key not in merged:
            tl.die(f"{path}: rules are missing {key!r}")
    return merged


def match_any(rel: str, globs: list[str]) -> str | None:
    for g in globs:
        if fnmatch.fnmatch(rel, g) or (g.endswith("/**") and fnmatch.fnmatch(rel, g[:-3])):
            return g
    return None


CONV_SOURCE = re.compile(rb"^<<<source: (.+?)>>>$", re.M)
CONV_TOOL = re.compile(rb"^<<<tool: (.+?)>>>$", re.M)
BULK_BYTES = 2_000_000


def conversion_map(corpus: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Which original each converted text came from, and which tool made it.

    The converter writes both facts into its own header, so the pairing is read off the artifact
    rather than guessed from filenames. This is what stops a record being counted twice — once as
    the original and once as its conversion.
    """
    origin: dict[str, str] = {}
    tool: dict[str, str] = {}
    text_dir = corpus / "_text"
    if not text_dir.is_dir():
        return origin, tool
    for p in sorted(text_dir.glob("*.txt")):
        head = p.read_bytes()[:2000]
        m, t = CONV_SOURCE.search(head), CONV_TOOL.search(head)
        if not m:
            continue
        try:
            src = str(Path(m.group(1).decode("utf-8")).resolve().relative_to(corpus.resolve()))
        except ValueError:
            continue
        rel = str(p.relative_to(corpus))
        origin[rel] = src
        tool[rel] = t.group(1).decode("utf-8") if t else "unknown"
    return origin, tool


def enumerate_corpus(corpus: Path, rules: dict[str, object],
                     only: list[str] | None = None) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Returns (eligible sources, ledger). Every file lands in exactly one of them.

    `only` names the exact set to consider, for a pipeline run that already knows its sources
    rather than discovering a folder tree. The include/exclude rules still apply to it: a run
    handing over a derived path gets the same refusal a corpus sweep would give.
    """
    include = list(rules["include"])          # type: ignore[arg-type]
    exclude = list(rules["exclude"])          # type: ignore[arg-type]
    reasons: dict[str, str] = dict(rules["exclude_reasons"])   # type: ignore[arg-type]
    pinned: dict[str, str] = dict(rules.get("pinned_shas", {}))  # type: ignore[arg-type]

    # A record and its conversion are ONE record. Whichever of the pair is the text the person's
    # words actually live in is the source; the other is a duplicate of it and is excluded by
    # name, so nothing is emitted twice from two paths.
    origin, tool = conversion_map(corpus)
    copies = {c for c, t in tool.items() if t.strip().lower() == "copy"}
    converted_originals = {origin[c] for c in origin if c not in copies}

    eligible: dict[str, str] = {}
    ledger: list[dict[str, str]] = []
    candidates = sorted(corpus.rglob("*")) if only is None else \
        [corpus / o for o in sorted(only)]
    for p in candidates:
        if p.is_dir():
            continue
        if p.is_symlink() and not p.exists():
            tl.die(f"broken symlink in the corpus: {p}")
        rel = str(p.resolve().relative_to(corpus.resolve())) if not p.is_symlink() \
            else str(p.relative_to(corpus))
        hit = match_any(rel, exclude)
        if hit:
            why = reasons.get(hit)
            if why is None:
                tl.die(f"exclude rule {hit!r} has no stated reason")
            want = pinned.get(rel)
            if want and tl.sha(p.read_bytes().hex()) != want:
                tl.die(f"{rel} is pinned as excluded but its content changed — re-check it")
            ledger.append({"file": rel, "status": "excluded", "rule": hit, "reason": why})
            continue
        inc = match_any(rel, include)
        if not inc:
            ledger.append({"file": rel, "status": "excluded", "rule": "(no include rule)",
                           "reason": "not on the primary-source list"})
            continue
        if rel in copies:
            ledger.append({"file": rel, "status": "excluded", "rule": "conversion-pair",
                           "reason": f"duplicate — a straight copy of {origin[rel]}, which is "
                                     f"itself the source"})
            continue
        if rel in converted_originals:
            ledger.append({"file": rel, "status": "excluded", "rule": "conversion-pair",
                           "reason": "converted — the pipeline's text conversion of this record "
                                     "is the source, so the original is not read twice"})
            continue
        raw = p.read_bytes()
        if len(raw) > BULK_BYTES:
            ledger.append({"file": rel, "status": "excluded", "rule": "bulk",
                           "reason": f"bulk instrument output, {len(raw):,} bytes — a raw data "
                                     f"dump is not a passage of anyone's history; the interpreted "
                                     f"report of it is the record"})
            continue
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            ledger.append({"file": rel, "status": "excluded", "rule": inc,
                           "reason": "not valid UTF-8 text — cannot be quoted verbatim"})
            continue
        if not raw.strip():
            ledger.append({"file": rel, "status": "excluded", "rule": inc,
                           "reason": "empty file"})
            continue
        eligible[rel] = inc
        ledger.append({"file": rel, "status": "source", "rule": inc, "reason": ""})
    return eligible, ledger


def assert_no_repo(corpus: Path, eligible: dict[str, str]) -> None:
    """The person's history is never version-controlled.

    Checked by walking UP from each source to the corpus root, not by sweeping the corpus for
    `.git`. A run passes `--corpus /` because its sources are absolute paths, and sweeping there
    would walk the whole filesystem — it never finishes, and it is certain to find somebody
    else's repository and refuse a build for no reason. Walking up asks the question that
    actually matters: is the folder this record sits in under version control.
    """
    stop = corpus.resolve()
    seen: set[Path] = set()
    for rel in eligible:
        d = (corpus / rel).resolve().parent
        while True:
            if d in seen:
                break
            seen.add(d)
            if (d / ".git").exists():
                tl.die(f"{d} is inside a git repository ({d / '.git'}). The person's history is "
                       f"never version-controlled — the scripts are versioned, the records are "
                       f"not. Move the corpus outside the repository before building.")
            if d == stop or d.parent == d:
                break
            d = d.parent


def resolve_span(corpus: Path, entry: dict[str, object]) -> tuple[int, int]:
    """Turn a declared boundary into an exact byte range. Ambiguity is a failure, not a guess."""
    src = corpus / str(entry["src"])
    raw = tl.source_bytes(src)
    if "span" in entry:
        a, b = (int(x) for x in str(entry["span"]).split(":"))
    else:
        start = str(entry["start"]).encode("utf-8")
        n = raw.count(start)
        if n == 0:
            tl.die(f"{entry['src']}: start boundary not found: {entry['start']!r}")
        if n > 1:
            tl.die(f"{entry['src']}: start boundary appears {n} times, so it is ambiguous: "
                   f"{entry['start']!r}")
        a = raw.index(start)
        end = entry.get("end")
        if end is None:
            b = len(raw)
        else:
            e = str(end).encode("utf-8")
            m = raw.count(e)
            if m == 0:
                tl.die(f"{entry['src']}: end boundary not found: {end!r}")
            if m > 1:
                tl.die(f"{entry['src']}: end boundary appears {m} times, so it is ambiguous: {end!r}")
            b = raw.index(e)
            if b <= a:
                tl.die(f"{entry['src']}: end boundary precedes start: {entry['start']!r} .. {end!r}")
    while a < b and raw[a:a + 1].isspace():
        a += 1
    while b > a and raw[b - 1:b].isspace():
        b -= 1
    if a >= b:
        tl.die(f"{entry['src']}: span {entry.get('span') or entry.get('start')} is empty after "
               f"trimming whitespace")
    return a, b


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--index", required=True, type=Path,
                    help="the block index: which spans become blocks, and where they sit in time")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--ledger", type=Path, help="where to write the per-file source ledger")
    ap.add_argument("--only", type=Path,
                    help="a JSON array of corpus-relative paths — the exact source set, for a "
                         "pipeline run that already knows what its sources are")
    args = ap.parse_args()

    corpus = args.corpus.resolve()

    rules = load_rules(args.sources)
    only = json.loads(args.only.read_text(encoding="utf-8")) if args.only else None
    eligible, ledger = enumerate_corpus(corpus, rules, only)
    assert_no_repo(corpus, eligible)
    vocab = set(re.findall(r"`([a-z][a-z-]+)`", args.sources.read_text(encoding="utf-8")
                           .split("## 4. Tag vocabulary")[1].split("## 5.")[0]))

    index = json.loads(args.index.read_text(encoding="utf-8"))
    entries: list[dict[str, object]] = index["blocks"]

    # ── resolve every declared span before emitting anything ──────────────────
    resolved: list[dict[str, object]] = []
    for e in entries:
        rel = str(e["src"])
        if rel not in eligible:
            reason = next((r["reason"] for r in ledger if r["file"] == rel),
                          "not present in the corpus")
            tl.die(f"block index names {rel} as a source, but it is not one: {reason}")
        a, b = resolve_span(corpus, e)
        body = tl.slice_source(corpus / rel, a, b)
        prec = str(e.get("prec", "unknown"))
        date = str(e.get("date", "")) if prec != "unknown" else ""
        tags = [str(t) for t in e.get("tags", [])]
        if len(tags) > 3:
            tl.die(f"{rel} {a}:{b}: {len(tags)} tags — the heading carries at most three")
        for t in tags:
            if t not in vocab:
                tl.die(f"{rel} {a}:{b}: tag {t!r} is not in the closed vocabulary")
        tl.render_date(date, prec)          # fails loudly on a precision/value mismatch
        resolved.append({"src": rel, "a": a, "b": b, "body": body, "date": date,
                         "prec": prec, "tags": tags})

    # ── no source may be emitted twice over the same bytes ────────────────────
    per_source: dict[str, list[tuple[int, int]]] = {}
    for r in resolved:
        per_source.setdefault(str(r["src"]), []).append((int(r["a"]), int(r["b"])))
    for src, spans in per_source.items():
        spans.sort()
        for (a1, b1), (a2, b2) in zip(spans, spans[1:]):
            if a2 < b1:
                tl.die(f"{src}: spans {a1}:{b1} and {a2}:{b2} overlap — the same words would be "
                       f"emitted twice")

    # ── order, identify, render ───────────────────────────────────────────────
    order = {s: i for i, s in enumerate(per_source)}
    resolved.sort(key=lambda r: (tl.sort_key(str(r["date"]), str(r["prec"]), 0)[:2],
                                 order[str(r["src"])], int(r["a"])))
    out: list[str] = [HEADER]
    for i, r in enumerate(resolved, start=1):
        bid = tl.ID_FMT % i
        body = str(r["body"])
        out.append("")
        out.append(tl.render_block(bid, str(r["src"]), int(r["a"]), int(r["b"]), body,
                                   str(r["date"]), str(r["prec"]),
                                   [str(t) for t in r["tags"]], tl.split_units(body)))

    # ── coverage: every byte of every used source is either in a block or a recorded skip ──
    out.append("")
    out.append("<!-- coverage: which bytes of each source became blocks, and which did not -->")
    for src in sorted(per_source):
        out.append(tl.coverage_line(src, tl.source_bytes(corpus / src), per_source[src]))

    text = "\n".join(out) + "\n"
    tl.atomic_write(args.out, text)

    if args.ledger:
        args.ledger.write_text(json.dumps(ledger, indent=1) + "\n", encoding="utf-8")

    n_src = sum(1 for r in ledger if r["status"] == "source")
    n_exc = sum(1 for r in ledger if r["status"] == "excluded")
    n_der = sum(1 for r in ledger if "derived" in r["reason"])
    print(f"corpus files: {len(ledger)}  ({n_src} eligible sources, {n_exc} excluded, "
          f"of which {n_der} derived or model-written)")
    print(f"blocks: {len(resolved)}  from {len(per_source)} sources")
    print(f"words copied: {sum(len(str(r['body']).split()) for r in resolved)}")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
