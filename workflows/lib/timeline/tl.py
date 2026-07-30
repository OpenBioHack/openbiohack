#!/usr/bin/env python3
"""Shared primitives for the one-document timeline.

The document is the only artifact. Every block carries an inline provenance comment naming its
source file and the byte range it was copied from, so the document describes itself and nothing
needs a sidecar index that could drift out of step with it.

Nothing in this module writes prose. It parses, renders and hashes; the words always come from a
source file, copied byte for byte.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# ── the marker grammar ────────────────────────────────────────────────────────
# A block region runs from its open marker line to its close marker line, inclusive. Everything
# outside a region is free text: the header, hand-typed lines, annotations. Free text is never
# touched by any tool.
OPEN_RE = re.compile(r"^<!--TL (TL-S\d{4}) (.*?)-->$")
UNITS_RE = re.compile(r"^<!--TLU (.*?)-->$")
CLOSE_RE = re.compile(r"^<!--/TL (TL-S\d{4})-->$")
COVER_RE = re.compile(r"^<!--TLC (.*?)-->$")
NOTE_OPEN_RE = re.compile(r"^<!--TLN (TL-S\d{4})-->$")
NOTE_CLOSE_RE = re.compile(r"^<!--/TLN (TL-S\d{4})-->$")
CITE_RE = re.compile(r"\[\[(TL-S\d{4})(?:-(u\d{2}))?\]\]")

ID_FMT = "TL-S%04d"
SHA_LEN = 12

PRECISIONS = ("day", "month", "year", "span", "unknown")


def read_doc(path: Path) -> str:
    """Read the document with newline translation OFF.

    `read_text` silently turns \r\n into \n, so a source with Windows line endings (every RTF
    imaging report, for one) would come back out of the document different from how it went in
    and fail verification with no way to tell why. Nothing here may translate anything.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:SHA_LEN]


def die(msg: str) -> None:
    """Fail loudly. Every failure names the block or the file it is about."""
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


# ── source text ───────────────────────────────────────────────────────────────
# A source's canonical text is its bytes decoded as strict UTF-8. Spans are byte offsets into
# those bytes. A file that is not valid UTF-8 cannot be a source: decoding it with replacement
# would mean the "verbatim" text was not what the file contains.

_SRC_CACHE: dict[Path, bytes] = {}


def source_bytes(path: Path) -> bytes:
    if path not in _SRC_CACHE:
        if not path.exists():
            die(f"source file missing: {path}")
        _SRC_CACHE[path] = path.read_bytes()
    return _SRC_CACHE[path]


def source_text(path: Path) -> str:
    raw = source_bytes(path)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as e:
        die(f"source is not valid UTF-8, so it cannot be quoted verbatim: {path} ({e})")
        raise  # unreachable; keeps type checkers happy


def slice_source(path: Path, start: int, end: int) -> str:
    raw = source_bytes(path)
    if not 0 <= start < end <= len(raw):
        die(f"span {start}:{end} is outside {path} (length {len(raw)})")
    chunk = raw[start:end]
    try:
        return chunk.decode("utf-8")
    except UnicodeDecodeError as e:
        die(f"span {start}:{end} of {path} does not decode as UTF-8 — it cuts a character ({e})")
        raise


# ── blockquote rendering, exactly invertible ──────────────────────────────────
# quote:   line -> ">" + (" " + line if line else "")
# unquote: strip one leading ">", then at most one following space.
# A source line that is literally ">" renders as "> >" and comes back as ">". An empty source
# line renders as ">" with no trailing space, so an editor that strips trailing whitespace
# cannot silently alter the body.


def quote(body: str) -> str:
    return "\n".join(">" + (" " + ln if ln else "") for ln in body.split("\n"))


def unquote(lines: list[str]) -> str:
    out = []
    for ln in lines:
        if not ln.startswith(">"):
            die(f"block body line is not quoted, so the document has been reflowed: {ln[:60]!r}")
        rest = ln[1:]
        out.append(rest[1:] if rest.startswith(" ") else rest)
    return "\n".join(out)


# ── dates ─────────────────────────────────────────────────────────────────────
# The rendered date is a lookup keyed on the stored precision. A year-precision placement has no
# code path that can render it as a specific day.

def render_date(date: str, prec: str) -> str:
    if prec not in PRECISIONS:
        die(f"unknown date precision {prec!r} (expected one of {', '.join(PRECISIONS)})")
    if prec == "unknown":
        return "undated"
    if prec == "day":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            die(f"day precision needs YYYY-MM-DD, got {date!r}")
        return date
    if prec == "month":
        if not re.fullmatch(r"\d{4}-\d{2}", date):
            die(f"month precision needs YYYY-MM, got {date!r}")
        return date
    if prec == "year":
        if not re.fullmatch(r"\d{4}", date):
            die(f"year precision needs YYYY, got {date!r}")
        return "~" + date
    if not re.fullmatch(r"\d{4}(-\d{2})?\.\.\d{4}(-\d{2})?", date):
        die(f"span precision needs A..B where each side is YYYY or YYYY-MM, got {date!r}")
    return "~" + date.replace("..", "–")


def sort_key(date: str, prec: str, seq: int) -> tuple[str, int, int]:
    """Coarse precision sorts at the start of its earliest period; undated sorts last."""
    if prec == "unknown":
        return ("9999", 9, seq)
    start = date.split("..")[0] if prec == "span" else date
    pad = {"day": 2, "month": 1, "year": 0, "span": 0}[prec]
    return (start.split("-")[0] if prec == "year" else start, pad, seq)


# ── the parsed document ───────────────────────────────────────────────────────

@dataclass
class Block:
    bid: str
    attrs: dict[str, str]
    units: list[tuple[int, int]]
    body: str
    heading: str
    line_start: int          # index of the open-marker line
    line_end: int            # index of the close-marker line
    raw_lines: list[str] = field(default_factory=list)

    @property
    def src(self) -> str:
        return self.attrs["src"]

    @property
    def span(self) -> tuple[int, int]:
        a, b = self.attrs["span"].split(":")
        return int(a), int(b)

    @property
    def date(self) -> str:
        return self.attrs.get("date", "")

    @property
    def prec(self) -> str:
        return self.attrs.get("prec", "unknown")

    @property
    def tags(self) -> list[str]:
        t = self.attrs.get("tags", "")
        return [x for x in t.split(",") if x]


@dataclass
class Coverage:
    src: str
    length: int
    skips: list[tuple[int, int, str]]
    line: int


@dataclass
class Document:
    path: Path
    lines: list[str]
    blocks: list[Block]
    coverage: dict[str, Coverage]
    notes: dict[str, tuple[int, int]]

    def by_id(self, bid: str) -> Block:
        for b in self.blocks:
            if b.bid == bid:
                return b
        die(f"no block {bid} in {self.path.name}")
        raise

    def next_id(self) -> str:
        n = max((int(b.bid.split("-S")[1]) for b in self.blocks), default=0)
        return ID_FMT % (n + 1)


def attr_escape(v: str) -> str:
    """Provenance attributes are space-separated, and real filenames contain spaces."""
    return v.replace("%", "%25").replace(" ", "%20")


def attr_unescape(v: str) -> str:
    return v.replace("%20", " ").replace("%25", "%")


def parse_attrs(s: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in s.split():
        if "=" not in tok:
            die(f"malformed provenance attribute {tok!r} — the whole comment was "
                f"{s[:120]!r}. A value containing a space must be escaped as %20.")
        k, v = tok.split("=", 1)
        out[k] = attr_unescape(v)
    return out


def parse(path: Path) -> Document:
    text = read_doc(path)
    lines = text.split("\n")
    blocks: list[Block] = []
    coverage: dict[str, Coverage] = {}
    notes: dict[str, tuple[int, int]] = {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        mo = OPEN_RE.match(ln)
        if mo:
            bid, attrs = mo.group(1), parse_attrs(mo.group(2))
            j = i + 1
            mu = UNITS_RE.match(lines[j]) if j < len(lines) else None
            if not mu:
                die(f"{bid}: the unit table must be the line after the provenance comment")
            units = []
            for part in mu.group(1).split(","):
                if part:
                    a, b = part.split(":")
                    units.append((int(a), int(b)))
            j += 1
            if j >= len(lines) or not lines[j].startswith("## "):
                die(f"{bid}: no heading after the unit table")
            heading = lines[j][3:]
            j += 1
            body_start = j
            while j < len(lines) and not CLOSE_RE.match(lines[j]):
                j += 1
            if j >= len(lines):
                die(f"{bid}: no closing marker — the document is truncated or was reflowed")
            mc = CLOSE_RE.match(lines[j])
            assert mc
            if mc.group(1) != bid:
                die(f"{bid}: closing marker says {mc.group(1)} — blocks are interleaved")
            body_lines = lines[body_start:j]
            blocks.append(Block(bid, attrs, units, unquote(body_lines), heading, i, j,
                                lines[i:j + 1]))
            i = j + 1
            continue
        mv = COVER_RE.match(ln)
        if mv:
            a = parse_attrs(mv.group(1))
            skips = []
            for part in a.get("skip", "").split(";"):
                if part:
                    rng, why = part.split("(", 1)
                    x, y = rng.split(":")
                    skips.append((int(x), int(y), why.rstrip(")")))
            coverage[a["src"]] = Coverage(a["src"], int(a["len"]), skips, i)
            i += 1
            continue
        mn = NOTE_OPEN_RE.match(ln)
        if mn:
            k = i + 1
            while k < len(lines) and not NOTE_CLOSE_RE.match(lines[k]):
                k += 1
            if k >= len(lines):
                die(f"note on {mn.group(1)}: no closing marker")
            notes[mn.group(1)] = (i, k)
            i = k + 1
            continue
        i += 1
    return Document(path, lines, blocks, coverage, notes)


# ── rendering a block (the only place block text is laid out) ─────────────────

def heading_for(bid: str, date: str, prec: str, tags: list[str], opening: str) -> str:
    tagpart = " ".join(f"[{t}]" for t in tags)
    bits = [render_date(date, prec), bid]
    if tagpart:
        bits.append(tagpart)
    if opening:
        bits.append(opening)
    return " · ".join(bits)


def opening_words(body: str, limit: int = 60) -> str:
    """The block's own opening words, copied — cut at a word boundary, never rewritten."""
    flat = " ".join(body.split())
    if len(flat) <= limit:
        return flat
    cut = flat[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def render_open(bid: str, src: str, start: int, end: int, body: str, date: str, prec: str,
                tags: list[str]) -> str:
    attrs = (f"src={attr_escape(src)} span={start}:{end} sha={sha(body)} "
             f"date={date or 'none'} prec={prec}")
    if tags:
        attrs += " tags=" + ",".join(tags)
    return f"<!--TL {bid} {attrs}-->"


def render_block(bid: str, src: str, start: int, end: int, body: str, date: str, prec: str,
                 tags: list[str], units: list[tuple[int, int]]) -> str:
    unit_s = ",".join(f"{a}:{b}" for a, b in units)
    head = heading_for(bid, date, prec, tags, opening_words(body))
    return (f"{render_open(bid, src, start, end, body, date, prec, tags)}\n"
            f"<!--TLU {unit_s}-->\n"
            f"## {head}\n"
            f"{quote(body)}\n"
            f"<!--/TL {bid}-->")


# ── frozen sentence units ─────────────────────────────────────────────────────
# Units tile the block body exactly: concat(units) == body. A boundary falls after a newline, or
# after sentence-ending punctuation followed by whitespace. Trailing whitespace belongs to the
# unit before it, so no character sits outside a unit.

_BOUND = re.compile(r"(?<=\n)|(?<=[.!?…])\s+(?=[^\s])")


def split_units(body: str) -> list[tuple[int, int]]:
    cuts = {0, len(body)}
    for m in _BOUND.finditer(body):
        if 0 < m.end() < len(body):
            cuts.add(m.end())
    ordered = sorted(cuts)
    return [(a, b) for a, b in zip(ordered, ordered[1:]) if b > a]


# ── atomic write ──────────────────────────────────────────────────────────────
# A tool interrupted partway must leave the document exactly as it was, never truncated.

def atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tl-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ── the only way an edit tool may change the document ─────────────────────────
# The document is built once. After that nothing regenerates it: an edit names the lines it
# touches and everything else must come through byte-identical. `splice` and `relocate` check
# that themselves, so the guarantee does not rest on each tool being careful. build.py is the
# only script that composes a whole document, and it runs at creation.


def splice(path: Path, at: int, drop: int, new_lines: list[str]) -> None:
    """Replace lines [at, at+drop) with `new_lines`. Everything else must be unchanged."""
    before = read_doc(path).split("\n")
    if not 0 <= at <= len(before) or at + drop > len(before):
        die(f"edit region {at}:{at + drop} is outside {path.name} ({len(before)} lines)")
    after = before[:at] + new_lines + before[at + drop:]
    if after[:at] != before[:at] or after[at + len(new_lines):] != before[at + drop:]:
        die("the edit would change lines outside the region it named — refusing")
    atomic_write(path, "\n".join(after))


def splice_many(path: Path, edits: list[tuple[int, int, list[str]]]) -> None:
    """Apply several non-overlapping region edits at once. Same guarantee as `splice`."""
    before = read_doc(path).split("\n")
    ordered = sorted(edits, key=lambda e: e[0])
    for (a1, d1, _), (a2, _, _) in zip(ordered, ordered[1:]):
        if a1 + d1 > a2:
            die(f"edit regions {a1}:{a1 + d1} and {a2}:… overlap — refusing")
    after = before
    kept_outside = [x for i, x in enumerate(before)
                    if not any(a <= i < a + d for a, d, _ in ordered)]
    for at, drop, new in reversed(ordered):
        after = after[:at] + new + after[at + drop:]
    touched: set[int] = set()
    shift = 0
    for at, drop, new in ordered:
        touched.update(range(at + shift, at + shift + len(new)))
        shift += len(new) - drop
    if [x for i, x in enumerate(after) if i not in touched] != kept_outside:
        die("the edit would change lines outside the regions it named — refusing")
    atomic_write(path, "\n".join(after))


def classify_skip(raw: bytes, a: int, b: int) -> str:
    chunk = raw[a:b]
    if not chunk.strip():
        return "whitespace"
    if chunk.lstrip().startswith(b"<<<"):
        return "converter-header"
    return "not-placed"


def coverage_line(src: str, raw: bytes, spans: list[tuple[int, int]]) -> str:
    """Which bytes of a source became blocks, and which did not — stated, never implied."""
    skips: list[tuple[int, int, str]] = []
    cursor = 0
    for a, b in sorted(spans):
        if a > cursor:
            skips.append((cursor, a, classify_skip(raw, cursor, a)))
        cursor = max(cursor, b)
    if cursor < len(raw):
        skips.append((cursor, len(raw), classify_skip(raw, cursor, len(raw))))
    skip_s = ";".join(f"{a}:{b}({w})" for a, b, w in skips)
    return f"<!--TLC src={attr_escape(src)} len={len(raw)} skip={skip_s}-->"


def relocate(path: Path, a: int, b: int, anchor: int) -> None:
    """Move lines [a, b) so they sit at `anchor` (an index in the ORIGINAL line numbering).

    A move is a move. The lines are carried across unchanged; nothing is deleted and re-created,
    and no text is regenerated on the way.
    """
    before = read_doc(path).split("\n")
    if not 0 <= a < b <= len(before):
        die(f"move region {a}:{b} is outside {path.name} ({len(before)} lines)")
    if a <= anchor < b:
        die("a block cannot be moved inside itself")
    moved = before[a:b]
    rest = before[:a] + before[b:]
    at = anchor if anchor < a else anchor - (b - a)
    after = rest[:at] + moved + rest[at:]
    if after[at:at + len(moved)] != moved:
        die("the moved block did not survive the move unchanged — refusing")
    if [x for i, x in enumerate(after) if not at <= i < at + len(moved)] != rest:
        die("the move would change lines outside the block being moved — refusing")
    atomic_write(path, "\n".join(after))


# ── the batch guard ───────────────────────────────────────────────────────────
# Every batch of edits is preceded by a dated copy. The marker records which batch the document
# is currently in; an edit under a new batch name requires a snapshot of the document as it
# stands right now.

def marker_path(doc: Path) -> Path:
    return doc.with_suffix(doc.suffix + ".batch")


def snapshots_for(doc: Path) -> list[Path]:
    stem = doc.stem
    return sorted(p for p in doc.parent.glob(f"{stem}-*{doc.suffix}")
                  if re.fullmatch(rf"{re.escape(stem)}-\d{{4}}-\d{{2}}-\d{{2}}-.+", p.stem))


def require_batch(doc: Path, batch: str) -> None:
    mp = marker_path(doc)
    current = read_doc(mp).strip() if mp.exists() else ""
    if current == batch:
        return
    live = sha(read_doc(doc))
    for snap in snapshots_for(doc):
        if sha(read_doc(snap)) == live:
            mp.write_text(batch + "\n", encoding="utf-8")
            return
    die(f"batch {batch!r} has no dated copy of the document as it stands. "
        f"Run snapshot.py --doc {doc} --label {batch} first.")
