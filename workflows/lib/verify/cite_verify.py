#!/usr/bin/env python3
"""cite_verify.py — the ONE deterministic extraction verifier (grounding + DATA-coverage).

Replaces the representation-sensitive atom-diff. One primitive underlies everything: *is byte-span
X a whitespace-normalised substring of span Y*. No fuzzy matcher, no tokenizer type-split, no
normaliser on the gating path.

The AI writes a NATURAL extract whose every data line carries an inline citation:

    - Campylobacter <dl < 1.00e3 [src: gi-map, Page 1 Bacterial, "| Campylobacter | <dl | < 1.00e3 |"]

Code verifies that citation AFTER the fact, in two directions:

GROUNDING (extract -> source), per DATA line (a line carrying >=1 valid `[src:]`):
  (a) each cite's quote is a verbatim substring of ITS OWN routed source (by the cite `name`);
  (b) every non-scaffolding token on the line is a verbatim substring of the UNION of that line's
      cite quotes.
  A miss is an UNGROUNDED item {file, line, token, quote, reason}. Whole-token (not just numeric
  atoms): an invented diagnosis WORD fails exactly like an invented number. A same-quote wrong-row
  value fails (its value is absent from the single cited quote). A SPLIT citation (label quoted from
  one row, value from another, two cites on one line) is a documented boundary NOT caught here —
  each token grounds in its own cite; positional binding is a `.pos.json` follow-up.

PROSE sources (free text, e.g. a symptom diary) relax source-span coverage ONLY: `--coverage-value-only
NAME` flags an uncovered run only if it carries a genuine measured value (number+unit / %% / scientific
/ comparator+number), so narrative and embedded-analysis prose do not cry wolf; `--coverage-skip-span
NAME` drops source-span coverage for that source entirely. Grounding (verbatim) and quote->data value
coverage are UNCHANGED in both — extracted content stays faithful and a quoted value is never droppable.

COVERAGE (source -> DATA), extract stage only (views/event-log are intentional subsets => grounding
only). Two parts, both emit UNCOVERED:
  (1) source-span: a MEANINGFUL run of source content that no cite quote covers = an omission
      (a dropped row / dropped prose line).
  (2) quote->data: every meaningful value-token inside a cite's quote must ALSO appear on some data
      line citing that exact (name, quote) — a value that stays in the quote but is dropped from the
      DATA is UNCOVERED. This is the DATA-based definition (red-team critical fix): a value merely
      quoted, never extracted, is a drop; and a resolve edit that deletes a value while leaving its
      quote is re-flagged.

CODE-REVERT (--apply-reverts, extract stage): an UNGROUNDED token that is a recognisable REFORMAT of
a token in its own cited quote — a date the parser confirms is the same calendar date, or a unit in a
small synonym table — is reverted IN PLACE to the verbatim source form by CODE (no AI round-trip).
Because the revert writes the verbatim form, the next verify pass re-checks it: a bad revert re-flags.
All other UNGROUNDED / UNCOVERED items go to the AI as one pinpoint edit each.

Every check is against ONE reference point: the ORIGINAL converted source, routed by the cite `name`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field

# [src: NAME , loc , "quote"] — same shape the write-gate (investigate-src-fidelity.py) enforces.
# NAME has no comma; loc has no comma; quote (straight or curly double quotes) has no internal ".
CITE_RE = re.compile(r'\[src:\s*([^,\]]+?)\s*,[^,\]]*,\s*(?:"([^"]+)"|“([^”]+)”)\s*\]')
# a line that TRIES to cite (contains the literal opener) — used to flag malformed cites.
CITE_OPENER = re.compile(r"\[src:")

# Edge punctuation stripped from both ends of a raw token (repeatedly). Internal chars are kept, so
# value punctuation that carries meaning (`<` in `<dl`, `/` in `g/dL`, `-`/`.` inside numbers/dates,
# `%`, `+`, `=`) survives. Markdown emphasis (`**`, `__`, `*`, `_`) and table/list glue strip away.
_EDGE = "-*_|:;,.()[]{}\"'`~—–…“”‘’•>"

# A SMALL fixed connective allowlist: lowercase function words that may glue a data line without
# being in the quote. Deliberately minimal — faithful lines quote verbatim, so they rarely need it.
CONNECTIVES = frozenset(
    "a an the and or of to in on at for with per vs by is was as".split()
)

# Coverage source-span: a run is a flag-worthy omission when it carries a real value — a digit, or a
# contiguous alphabetic phrase this long (tolerates a lone uncited header word; catches dropped prose
# sentences and dropped numeric values).
COVERAGE_MIN_ALPHA = 8

# A MEASURED VALUE — the value-aware coverage predicate for prose (free-text) sources. A strict
# lab table has a value in every row, so its default coverage (any digit / long phrase) is right; a
# free-text diary is mostly narrative + embedded analysis prose that carries digits without being a
# recorded measurement ("2-3x higher", "day 2-3", "H1"). Demanding every such run reach a data line
# makes coverage cry wolf on prose (symptom-log: 590 false omissions -> never converges). For a prose
# source, a run is a must-cover omission ONLY if it carries a genuine measurement: a number bound to a
# unit, a percentage, scientific notation, or a comparator+number. Bare numbers-in-prose and pure
# narrative are exempt (grounding still guarantees whatever IS extracted is verbatim; quote->data
# value coverage still guarantees a QUOTED value is not dropped).
_MEASURED_VALUE_RE = re.compile(
    r"[<>=≤≥]\s*\d"                                          # comparator + number  (<dl < 1.00e3)
    r"|\d[\d.,]*\s*(?:%"                                     # percentage           (18%)
    r"|[eE][+-]?\d+"                                         # scientific notation  (1.2e5)
    r"|(?:mg|mcg|µg|μg|ug|ng|pg|g|kg|ml|dl|cl|l|iu|u"        # mass / volume / activity units
    r"|mmol|umol|µmol|μmol|nmol|mol|meq"
    r"|mg/g|mcg/g|ng/g|mcg/ml|ng/ml|pg/ml|mcg/dl|ng/dl"      # concentrations
    r"|mg/dl|g/dl|mg/l|mmol/l|umol/l|nmol/l|u/l|iu/l"
    r"|cells|cfu|copies|bpm|mmhg|kcal|cal)\b)",              # counts / misc clinical units
    re.I)


def _has_measured_value(run: str) -> bool:
    """True if `run` carries a genuine measured value (see _MEASURED_VALUE_RE) — the value-aware
    coverage predicate for prose sources."""
    return bool(_MEASURED_VALUE_RE.search(run))

# Non-DATA source lines — excluded from coverage source-span (grounding is unaffected). Two kinds:
#   * converter-added provenance / page markers (same shapes the atom-diff strips) — never source
#     content; a faithful extract does not cite the converter's own banners.
#   * markdown ATX section headers (`#`..`######`) — document STRUCTURE, which the verbatim prompt
#     has the extractor reproduce on its own no-cite structure lines. Demanding a citation for a
#     source section title is a false omission; a dropped section is still caught via its data rows.
_CONV_HEADER = re.compile(r"^\s*<<<.*?>>>\s*$")
_PAGE_MARK = re.compile(
    r"^\s*(?:[-=]{2,}|\f)?\s*(?:page|pg)\s+\d+\s*(?:of\s+\d+\s*)?(?:[-=]{2,})?\s*$", re.I)
_ATX_HEADER = re.compile(r"^\s*#{1,6}\s")


def _is_converter_noise(raw_line: str) -> bool:
    """Converter banner / page marker only (used by the corpus generator to skip tool noise)."""
    return bool(_CONV_HEADER.match(raw_line) or _PAGE_MARK.match(raw_line))


def _is_noncontent_source_line(raw_line: str) -> bool:
    """Lines coverage source-span skips: converter noise + markdown section headers (structure)."""
    return _is_converter_noise(raw_line) or bool(_ATX_HEADER.match(raw_line))


def norm_ws(s: str) -> str:
    """Collapse every whitespace run to a single space and strip ends (the write-gate's own rule)."""
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class Cite:
    name: str          # the source name in [src: NAME, ...]
    quote: str         # the verbatim quoted span (raw)
    line_no: int       # 1-indexed line in the extract file
    file: str          # extract file path


@dataclass
class DataLine:
    file: str
    line_no: int
    raw: str                       # the full source line
    content: str                   # the line with every [src:...] block removed (the DATA span)
    cites: list[Cite] = field(default_factory=list)


def parse_cites_on_line(line: str, line_no: int, file: str) -> list[Cite]:
    out: list[Cite] = []
    for m in CITE_RE.finditer(line):
        quote = m.group(2) if m.group(2) is not None else m.group(3)
        out.append(Cite(name=m.group(1).strip(), quote=quote, line_no=line_no, file=file))
    return out


def strip_cites(line: str) -> str:
    return CITE_RE.sub(" ", line)


def content_tokens(text: str) -> list[str]:
    """Non-scaffolding tokens: whitespace-split, edge-punct + markdown-emphasis stripped, connective
    allowlist and pure-punctuation dropped. What remains must be grounded / covered."""
    out: list[str] = []
    for raw in text.split():
        t = raw.strip(_EDGE)
        # strip markdown emphasis wrappers that survive the edge set on the inside of a run
        while t[:2] in ("**", "__") and len(t) > 2:
            t = t[2:].strip(_EDGE)
        while t[-2:] in ("**", "__") and len(t) > 2:
            t = t[:-2].strip(_EDGE)
        if not t:
            continue
        if t.lower() in CONNECTIVES:
            continue
        out.append(t)
    return out


def value_tokens(text: str) -> list[str]:
    """Meaningful value-tokens of a quote (for quote->data coverage): content tokens of length >= 2.
    A lone punctuation-ish char is not a value to chase into the data line."""
    return [t for t in content_tokens(text) if len(t) >= 2]


# ───────────────────────── grounding ─────────────────────────
def _is_value_tok(s: str) -> bool:
    """A measured VALUE, not a name: the first non-space glyph is a digit or a comparator. This keeps
    analyte names that merely CONTAIN digits (B12, T4, FT3, HbA1c) and source labels (a consumer blood panel-1) on the
    tolerated 'word' side — only a token that STARTS like a number (>500, 45.2, 117) is gate-eligible."""
    for ch in s:
        if ch.isspace():
            continue
        return ch.isdigit() or ch in "<>=≤≥"
    return False


def ground_line(dl: DataLine, sources: dict[str, str], lenient: bool = False,
                src_all: str = "", src_dates: "frozenset" = frozenset()) -> list[dict]:
    """Return UNGROUNDED items for one data line. `sources` maps name -> normalised source text.

    lenient — SUMMARY-layer QC ONLY, never the verbatim extract stage. The extract stage stays strict
    (every token verbatim in its cited quote). The compiled timeline/views, by design, relabel and
    reorder, so grounding them strictly cries wolf on the summary's own words. In lenient mode a
    token/quote is tolerated (NOT a hop) when it is (A) verbatim ANYWHERE in a source (real content the
    summary recombined), (B) a date-equivalent of a source date (an ISO reformat), or (C) a pure WORD
    with no digit (a label/section word the summary legitimately adds). Only a VALUE (has a digit) that
    is absent from every source AND is not a source-date survives — the sole real data-integrity risk
    (a fabricated/mis-transcribed number). `src_all` = normalised union of all sources; `src_dates` =
    every calendar date in the sources (see source_date_set)."""
    items: list[dict] = []

    def tolerate(text: str) -> bool:
        return (norm_ws(text) in src_all) or bool(parse_date_set(text) & src_dates) or (not _is_value_tok(text))

    # (a) each cite's quote must be a verbatim (ws-normalised) substring of its routed source.
    ok_cites: list[Cite] = []
    for c in dl.cites:
        src = sources.get(c.name)
        if src is None:
            items.append({"file": dl.file, "line": dl.line_no, "token": "", "quote": c.quote,
                          "reason": "unknown-source", "detail": c.name})
            continue
        if norm_ws(c.quote) not in src:
            if lenient and tolerate(c.quote):
                continue
            items.append({"file": dl.file, "line": dl.line_no, "token": "", "quote": c.quote,
                          "reason": "quote-not-in-source", "detail": c.name})
            continue
        ok_cites.append(c)
    # (b) every content token on the line must be a ws-normalised substring of the UNION of this
    #     line's cite quotes. The union is over ALL cites the extractor WROTE (not only the
    #     in-source ones): "did the extractor copy this token from a quote it wrote" is orthogonal to
    #     "does that quote resolve in source" (flagged separately above), so a fabricated-quote line
    #     is not double-flagged token-by-token. Union => a multi-cite line's split-cite wrong-row is
    #     not caught (documented boundary); a single-cite line's same-quote wrong-row IS caught.
    quote_union = " ".join(norm_ws(c.quote) for c in dl.cites)
    for tok in content_tokens(dl.content):
        if norm_ws(tok) not in quote_union:
            if lenient and tolerate(tok):
                continue
            items.append({"file": dl.file, "line": dl.line_no, "token": tok,
                          "quote": dl.cites[0].quote if dl.cites else "",
                          "reason": "token-not-in-quote"})
    return items


# ───────────────────────── coverage ─────────────────────────
def _merge(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    ranges = sorted(ranges)
    merged = [list(ranges[0])]
    for a, b in ranges[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def _meaningful_run(run: str) -> bool:
    if any(ch.isdigit() for ch in run):
        return True
    alpha = sum(ch.isalpha() for ch in run)
    return alpha >= COVERAGE_MIN_ALPHA


def coverage_source_span(source_raw: str, quotes: list[str], name: str,
                         value_only: bool = False) -> list[dict]:
    """(1) Every meaningful run of source content must be covered by SOME cite quote. Works on the
    whitespace-normalised source line-by-line (offsets stay local). Uncovered meaningful runs =
    omissions.

    value_only — the value-aware predicate for a PROSE (free-text) source: an uncovered run is an
    omission ONLY if it carries a genuine measured value (_has_measured_value), so narrative and
    embedded-analysis prose do not trip coverage while a dropped lab value still does. Default
    (strict, for tables) keeps the original any-digit / long-phrase predicate."""
    is_omission = _has_measured_value if value_only else _meaningful_run
    items: list[dict] = []
    qn = [norm_ws(q) for q in quotes if norm_ws(q)]
    for raw_line in source_raw.split("\n"):
        if _is_noncontent_source_line(raw_line):
            continue
        line = norm_ws(raw_line)
        if not line:
            continue
        covered: list[tuple[int, int]] = []
        for q in qn:
            start = 0
            while True:
                i = line.find(q, start)
                if i < 0:
                    break
                covered.append((i, i + len(q)))
                start = i + 1
        mask = [False] * len(line)
        for a, b in _merge(covered):
            for i in range(a, min(b, len(line))):
                mask[i] = True
        run, run_start = "", None
        for i, ch in enumerate(line):
            if not mask[i]:
                if run_start is None:
                    run_start = i
                run += ch
            else:
                if run.strip() and is_omission(run):
                    items.append({"source": name, "token": run.strip(), "line": line,
                                  "reason": "source-not-in-data"})
                run, run_start = "", None
        if run.strip() and is_omission(run):
            items.append({"source": name, "token": run.strip(), "line": line,
                          "reason": "source-not-in-data"})
    return items


def coverage_quote_to_data(cites: list[Cite], data_by_group: dict[tuple[str, str], str]) -> list[dict]:
    """(2) Every meaningful value-token in a cite's quote must appear on the DATA span of some data
    line citing that exact (name, ws-quote). A value quoted but dropped from data => UNCOVERED."""
    items: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for c in cites:
        key = (c.name, norm_ws(c.quote))
        data = data_by_group.get(key, "")
        for tok in value_tokens(c.quote):
            dedup = (key[0], key[1], tok)
            if dedup in seen:
                continue
            if norm_ws(tok) not in data:
                seen.add(dedup)
                items.append({"source": c.name, "token": tok, "quote": c.quote,
                              "line": norm_ws(c.quote), "reason": "quote-value-not-in-data"})
    return items


# ───────────────────────── date / unit reverts ─────────────────────────
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
_MONTHS_FULL = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december"], start=1)}


def _mon_num(s: str) -> int | None:
    s = s.lower().rstrip(".")
    return _MONTHS_FULL.get(s) or _MONTHS.get(s[:3])


def _valid(y: int, m: int, d: int) -> bool:
    if not (1 <= m <= 12 and 1 <= d <= 31 and 1000 <= y <= 9999):
        return False
    dim = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return d <= dim


def parse_date_set(token: str) -> set[tuple[int, int, int]]:
    """All (y, m, d) a date token could denote. Ambiguous numeric forms (NN/NN/YYYY) yield BOTH
    day/month orderings; an alphabetic month is unambiguous. Empty set => not a date."""
    t = token.strip(_EDGE)
    out: set[tuple[int, int, int]] = set()
    # ISO  YYYY-MM-DD  or YYYY/MM/DD
    m = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", t)
    if m:
        y, a, b = int(m[1]), int(m[2]), int(m[3])
        if _valid(y, a, b):
            out.add((y, a, b))
        return out
    # DD-Mon-YYYY / DD Mon YYYY / Mon-DD-YYYY / Mon DD YYYY (alphabetic month, unambiguous)
    m = re.fullmatch(r"(\d{1,2})[-/ ]([A-Za-z]{3,9})[-/ ,]*(\d{4})", t)
    if m:
        mon = _mon_num(m[2])
        if mon and _valid(int(m[3]), mon, int(m[1])):
            out.add((int(m[3]), mon, int(m[1])))
        return out
    m = re.fullmatch(r"([A-Za-z]{3,9})[-/ ]+(\d{1,2})[-/ ,]*(\d{4})", t)
    if m:
        mon = _mon_num(m[1])
        if mon and _valid(int(m[3]), mon, int(m[2])):
            out.add((int(m[3]), mon, int(m[2])))
        return out
    # NN/NN/YYYY or NN-NN-YYYY — ambiguous day/month
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", t)
    if m:
        a, b, y = int(m[1]), int(m[2]), int(m[3])
        if _valid(y, a, b):
            out.add((y, a, b))
        if _valid(y, b, a):
            out.add((y, b, a))
    return out


_SRC_DATE_RE = re.compile(
    r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/ ][A-Za-z]{3,9}[-/ ,]*\d{4}"
    r"|[A-Za-z]{3,9}[-/ ]+\d{1,2}[-/ ,]*\d{4}|\d{1,2}[-/.]\d{1,2}[-/.]\d{4}")


def source_date_set(sources_norm: dict[str, str]) -> "frozenset":
    """Every calendar (y, m, d) date appearing anywhere in the sources — the reference set for the
    lenient date-equivalence tolerance (an ISO-reformatted summary date matches its source date)."""
    out: set = set()
    for text in sources_norm.values():
        for m in _SRC_DATE_RE.findall(text):
            out |= parse_date_set(m)
    return frozenset(out)


# unit synonyms — each variant maps to a canonical spelling; a token equal to a quote token after
# canonicalising units is a unit-reformat and reverts to the quote's verbatim form.
_UNIT_SYN = {"µg": "mcg", "μg": "mcg", "ug": "mcg", "µg/g": "mcg/g", "μg/g": "mcg/g",
             "ug/g": "mcg/g", "µmol": "umol", "μmol": "umol", "µmol/l": "umol/l",
             "μg/dl": "mcg/dl", "µg/dl": "mcg/dl"}


def _canon_units(tok: str) -> str:
    low = tok.lower()
    for k, v in _UNIT_SYN.items():
        if k in low:
            low = low.replace(k, v)
    return low


def _has_unit_variant(tok: str) -> bool:
    return _canon_units(tok) != tok.lower()


def try_revert(token: str, quote_tokens: list[str]) -> str | None:
    """If `token` (ungrounded) is a recognisable reformat of some quote token, return the verbatim
    quote token to revert to; else None. Date (same calendar date) or unit-synonym only."""
    tds = parse_date_set(token)
    if tds:
        for qt in quote_tokens:
            if qt == token:
                return None
            if tds & parse_date_set(qt):
                return qt
    # unit reformat: token and a quote token are equal after unit-canonicalisation but differ in raw
    # form, and at least one carries a recognised unit variant (so a mere case difference never
    # triggers a "unit" revert).
    tc = _canon_units(token)
    for qt in quote_tokens:
        if qt != token and _canon_units(qt) == tc and (_has_unit_variant(token) or _has_unit_variant(qt)):
            return qt
    return None


def _replace_token_on_line(line: str, old: str, new: str) -> str:
    """Replace the first whole-token occurrence of `old` with `new`, OUTSIDE any [src:...] block
    (never touch a quote), matching on token boundaries so a substring is not clobbered."""
    spans = [(m.start(), m.end()) for m in CITE_RE.finditer(line)]

    def in_cite(i: int) -> bool:
        return any(a <= i < b for a, b in spans)

    pat = re.compile(r"(?<![^\s(\[|:;,])" + re.escape(old) + r"(?![^\s)\]|:;,.])")
    for m in pat.finditer(line):
        if not in_cite(m.start()):
            return line[:m.start()] + new + line[m.end():]
    # fallback: plain first occurrence outside a cite
    idx = line.find(old)
    while idx >= 0:
        if not in_cite(idx):
            return line[:idx] + new + line[idx + len(old):]
        idx = line.find(old, idx + 1)
    return line


# ───────────────────────── driver ─────────────────────────
def read_data_lines(extract_files: list[str]) -> tuple[list[DataLine], list[dict]]:
    """Parse every extract file into data lines. Returns (data_lines, malformed_cite_items)."""
    data_lines: list[DataLine] = []
    malformed: list[dict] = []
    for f in extract_files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            malformed.append({"file": f, "line": 0, "token": "", "quote": "",
                              "reason": "unreadable-extract", "detail": str(e)})
            continue
        for i, raw in enumerate(text.split("\n"), start=1):
            cites = parse_cites_on_line(raw, i, f)
            if not cites:
                if CITE_OPENER.search(raw):
                    malformed.append({"file": f, "line": i, "token": "", "quote": "",
                                      "reason": "malformed-citation"})
                continue
            data_lines.append(DataLine(file=f, line_no=i, raw=raw,
                                       content=strip_cites(raw), cites=cites))
    return data_lines, malformed


def verify(extract_files: list[str], sources_raw: dict[str, str], coverage: bool,
           lenient: bool = False, value_only_sources: "frozenset" = frozenset(),
           skip_span_sources: "frozenset" = frozenset()) -> dict:
    """One pass: grounding (+coverage for the extract stage). Read-only. lenient => SUMMARY-layer
    tolerances (see ground_line): only a VALUE absent from every source and not a source-date is a hop.

    value_only_sources — names whose source-span coverage uses the value-aware predicate (#1 prose
    coverage: only a genuine measured value is a must-cover omission). skip_span_sources — names whose
    source-span coverage is SKIPPED entirely (#2 prose passthrough: grounding + quote->data value
    coverage still run, so extracted content stays verbatim and a quoted value is still not droppable,
    but narrative need not reach a data line). A name in skip_span_sources wins over value_only."""
    sources_norm = {k: norm_ws(v) for k, v in sources_raw.items()}
    data_lines, malformed = read_data_lines(extract_files)

    src_all = " ".join(sources_norm.values()) if lenient else ""
    src_dates = source_date_set(sources_norm) if lenient else frozenset()
    ungrounded: list[dict] = list(malformed)
    for dl in data_lines:
        ungrounded.extend(ground_line(dl, sources_norm, lenient=lenient,
                                      src_all=src_all, src_dates=src_dates))

    uncovered: list[dict] = []
    if coverage:
        all_cites = [c for dl in data_lines for c in dl.cites]
        # quote->data groups: (name, ws-quote) -> union of the DATA spans of lines citing it
        data_by_group: dict[tuple[str, str], str] = {}
        for dl in data_lines:
            dc = norm_ws(dl.content)
            for c in dl.cites:
                key = (c.name, norm_ws(c.quote))
                data_by_group[key] = (data_by_group.get(key, "") + " " + dc).strip()
        # (1) source-span coverage, per source, using only cites that route to that source. A prose
        # source is either skipped (#2 passthrough) or run value-aware (#1); a table stays strict.
        for name, src in sources_raw.items():
            if name in skip_span_sources:
                continue
            quotes = [c.quote for c in all_cites if c.name == name]
            uncovered.extend(coverage_source_span(src, quotes, name,
                                                  value_only=(name in value_only_sources)))
        # (2) quote->data value coverage
        uncovered.extend(coverage_quote_to_data(all_cites, data_by_group))

    return {
        "ok": not ungrounded and not uncovered,
        "ungrounded": ungrounded,
        "uncovered": uncovered,
        "summary": {"ungrounded": len(ungrounded), "uncovered": len(uncovered)},
        "ranSuccessfully": True,
    }


def apply_reverts(extract_files: list[str], sources_raw: dict[str, str]) -> list[dict]:
    """Revert every UNGROUNDED token that is a date/unit reformat of a token in its own cited quote,
    IN PLACE. Returns the list of applied reverts. Files are rewritten only where a revert applies."""
    sources_norm = {k: norm_ws(v) for k, v in sources_raw.items()}
    reverted: list[dict] = []
    data_lines, _ = read_data_lines(extract_files)
    # group ungrounded token-not-in-quote items by file
    by_file: dict[str, list[tuple[DataLine, dict]]] = {}
    for dl in data_lines:
        for item in ground_line(dl, sources_norm):
            if item["reason"] == "token-not-in-quote":
                by_file.setdefault(dl.file, []).append((dl, item))
    for f, entries in by_file.items():
        with open(f, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
        changed = False
        for dl, item in entries:
            qtoks: list[str] = []
            for c in dl.cites:
                qtoks.extend(content_tokens(c.quote))
            new = try_revert(item["token"], qtoks)
            if new is None:
                continue
            idx = dl.line_no - 1
            updated = _replace_token_on_line(lines[idx], item["token"], new)
            if updated != lines[idx]:
                lines[idx] = updated
                changed = True
                reverted.append({"file": f, "line": dl.line_no, "old": item["token"],
                                 "new": new, "kind": "date-or-unit-reformat"})
        if changed:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
    return reverted


def _parse_sources(pairs: list[str]) -> dict[str, str]:
    sources: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"--source must be NAME=PATH (got {p!r})")
        name, path = p.split("=", 1)
        with open(path, encoding="utf-8", errors="replace") as fh:
            sources[name.strip()] = fh.read()
    return sources


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic extraction verifier (grounding + coverage).")
    ap.add_argument("--extract", nargs="+", required=True, help="extract .md file(s) to verify")
    ap.add_argument("--source", nargs="+", required=True, metavar="NAME=PATH",
                    help="original source(s): the cite `name` routes to its converted-text path")
    ap.add_argument("--coverage", action="store_true", help="also run source->DATA coverage (extract stage)")
    ap.add_argument("--apply-reverts", action="store_true",
                    help="revert date/unit reformats in place, then re-verify (implies --coverage)")
    ap.add_argument("--json", action="store_true", help="emit machine JSON")
    ap.add_argument("--lenient", action="store_true",
                    help="SUMMARY-layer QC tolerances: a token verbatim anywhere in a source, a "
                         "date-equivalent of a source date, or a pure word is not a hop — only a VALUE "
                         "absent from every source (a fabricated number) fails. NEVER use for the "
                         "verbatim extract stage.")
    ap.add_argument("--coverage-value-only", default="", metavar="NAME[,NAME...]",
                    help="PROSE coverage (#1): for these source names, a source-span omission counts "
                         "ONLY if the uncovered run carries a genuine measured value (number+unit, %%, "
                         "scientific, comparator+number). Narrative / embedded-analysis prose is "
                         "exempt. Use for free-text sources (e.g. a symptom diary); tables stay strict.")
    ap.add_argument("--coverage-skip-span", default="", metavar="NAME[,NAME...]",
                    help="PROSE passthrough (#2): for these source names, source->DATA span coverage is "
                         "skipped entirely (grounding + quote->data value coverage still run). The full "
                         "escape hatch when even --coverage-value-only is too strict for a source.")
    args = ap.parse_args()

    value_only_sources = frozenset(n.strip() for n in args.coverage_value_only.split(",") if n.strip())
    skip_span_sources = frozenset(n.strip() for n in args.coverage_skip_span.split(",") if n.strip())

    try:
        sources = _parse_sources(args.source)
    except OSError as e:
        print(json.dumps({"ranSuccessfully": False, "note": f"source read failed: {e}",
                          "ungrounded": [], "uncovered": [], "ok": False}))
        return 2

    coverage = args.coverage or args.apply_reverts
    reverted: list[dict] = []
    if args.apply_reverts:
        reverted = apply_reverts(args.extract, sources)

    report = verify(args.extract, sources, coverage, lenient=args.lenient,
                    value_only_sources=value_only_sources, skip_span_sources=skip_span_sources)
    report["reverted"] = reverted
    report["summary"]["reverted"] = len(reverted)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        s = report["summary"]
        print(f"cite_verify: {s['ungrounded']} UNGROUNDED, {s['uncovered']} UNCOVERED, "
              f"{s.get('reverted', 0)} reverted -> {'OK' if report['ok'] else 'FAIL'}")
        for it in report["ungrounded"][:40]:
            print(f"  UNGROUNDED [{it['reason']}] L{it['line']} {it.get('token') or it.get('quote', '')!r}")
        for it in report["uncovered"][:40]:
            print(f"  UNCOVERED  [{it['reason']}] {it['source']}: {it['token']!r}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
