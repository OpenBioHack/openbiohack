#!/usr/bin/env python3
"""extract-atom-diff.py — deterministic bidirectional coverage-diff for extract-health-data.

The mechanical core of the parallel coverage-diff extraction workflow. Given a converted SOURCE
(plain text staged by the converter) and the UNION of that source's Phase-A extract file(s), it
diffs the *content atoms* on each side and reports, condition-agnostically:

  omissions     content present in the SOURCE but missing from the EXTRACTION (missed data)
  fabrications  content present in the EXTRACTION but absent from the SOURCE (hallucination —
                the "sweet potato" failure: a value/entity the source never contained)
  unit_issues   a value that survived but LOST or CHANGED its unit (mg->mcg style drift)
  ambiguous     a source date that cannot be read without guessing (EU day/month, 03-05) —
                surfaced, never silently resolved, and excluded from the coverage diff
  binding_issues (optional, needs --positions) a value whose nearest-left source label does not
                match the label it was extracted under ("right number, wrong row")

Atoms are HIGH-VALUE content only, never the markdown structure / tags / provenance the extractor
legitimately adds. Four typed atoms:
  NUMBER(+unit)  decimals / scientific / signed / thousands / ranges, canonicalized with
                 decimal.Decimal and matched by VALUE, EXACT (zero-tolerance) — the numeric-
                 fidelity guarantee. 67.3 != 67, -0.3 != 0.3, 1.76e6 == 1760000, 1,574 == 1574,
                 a range 1.0e6-5.0e7 splits into two number atoms.
  UNIT           normalized via a curated spelling map (mcg/ug/micro-sign -> ug; mg/dl canonical)
                 — NORMALIZED, NEVER CONVERTED (mg/dL<->mmol/L needs an analyte molar mass and is
                 forbidden). Tracked as an attribute of its number, checked as unit_issues.
  DATE           dateutil if present else a stdlib strptime format-list -> ISO; ambiguous numeric
                 dates are flagged, not guessed. Matched EXACT on the ISO string.
  ENTITY         distinctive content words + capitalized phrases + analyte-shaped tokens, unicode-
                 folded (investigate_canon.match_copy). Matched FUZZY (rapidfuzz token_sort_ratio,
                 else difflib) with a threshold high enough not to collapse DHEA vs DHEA-S; short
                 tokens require an exact match. OCR-noise tolerant.

Stdlib floor (unicodedata / re / decimal / datetime / difflib) ALWAYS runs; python-dateutil,
rapidfuzz, unidecode are optional enhancers behind try/except with graceful, result-equivalent
fallback. Deterministic: same inputs -> same output. No filesystem writes.

Usage:
  python3 extract-atom-diff.py --source <src.txt> --extraction <e1.md> [<e2.md> ...] \
      [--positions <src.pos.json>] [--theta 0.88] [--entity-min 6]
Prints a JSON report on stdout. Exit 1 if any omissions / fabrications / unit_issues /
binding_issues (a real coverage or fidelity problem); exit 0 if clean. Ambiguous-only is exit 0.
"""
import sys
import os
import re
import json
import argparse
import difflib
import unicodedata
from decimal import Decimal, InvalidOperation
from collections import defaultdict

# --- unicode canonicalizer (VENDORED from hooks/lib/investigate_canon.py so this lib is fully
#     self-contained and can live in the skill's scripts/ dir, not the protected hooks/ dir).
#     match_copy = NFKC fold + strip format/combining marks + fold Latin-look-alike homoglyphs.
_ZW = "".join(chr(c) for c in (
    0x200b, 0x200c, 0x200d, 0x200e, 0x200f, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064,
    0xfeff, 0x00ad, 0x034f, 0x061c, 0x202a, 0x202b, 0x202c, 0x202d, 0x202e,
    0x2066, 0x2067, 0x2068, 0x2069,
))
_CONFUSABLES = {
    0x0430: "a", 0x0435: "e", 0x043e: "o", 0x0440: "p", 0x0441: "c", 0x0445: "x", 0x0443: "y",
    0x0456: "i", 0x0458: "j", 0x0455: "s", 0x043a: "k", 0x0501: "d", 0x04bb: "h", 0x0432: "v",
    0x043c: "m", 0x043d: "n", 0x0442: "t", 0x0431: "b",
    0x0410: "A", 0x0415: "E", 0x041e: "O", 0x0420: "P", 0x0421: "C", 0x0425: "X", 0x0423: "Y",
    0x0406: "I", 0x041a: "K", 0x0412: "B", 0x041c: "M", 0x041d: "H", 0x0422: "T",
    0x03bf: "o", 0x03b1: "a", 0x03bd: "v", 0x03c1: "p", 0x03b5: "e", 0x03c4: "t", 0x03b9: "i",
    0x03ba: "k", 0x03c5: "u",
    0x0399: "I", 0x039f: "O", 0x03a1: "P", 0x03a4: "T", 0x0391: "A", 0x0392: "B", 0x0395: "E",
    0x0397: "H", 0x039a: "K", 0x039c: "M", 0x039d: "N", 0x03a7: "X", 0x0396: "Z",
    0x0261: "g", 0x0269: "i", 0x026a: "i", 0x0274: "n", 0x1d04: "c", 0x1d07: "e", 0x04cf: "l",
    0x0578: "n", 0x0585: "o",
}


def _canon(text):
    if not text:
        return text
    t = unicodedata.normalize("NFKC", text)
    out = []
    for ch in t:
        if ch in _ZW:
            continue
        cat = unicodedata.category(ch)
        if cat == "Cf" or cat == "Mn":
            continue
        out.append(ch)
    return "".join(out)


def match_copy(text):
    if not text:
        return text
    return "".join(_CONFUSABLES.get(ord(ch), ch) for ch in _canon(text))

# --- optional-dependency enhancers (graceful fallback) ---------------------------------------
try:
    from dateutil import parser as _dateutil_parser  # noqa: N816
except Exception:
    _dateutil_parser = None
try:
    from rapidfuzz import fuzz as _rf_fuzz
except Exception:
    _rf_fuzz = None
try:
    from unidecode import unidecode as _unidecode
except Exception:
    _unidecode = None

DEPS = {
    "dateutil": _dateutil_parser is not None,
    "rapidfuzz": _rf_fuzz is not None,
    "unidecode": _unidecode is not None,
}

# =============================================================================================
# Shared tokenizer bits (extends investigate-provenance-reconcile's tokenizer)
# =============================================================================================

# Stopwords + structural/lab terms the extractor legitimately adds as headers, labels, flags.
# Suppressed for ENTITY atoms on BOTH sides so reformatting is not read as omission/fabrication.
STOP = set("""
about above after again against because before being below between could during should through
under until where which while would their there these those event still worse certain thing
things something anything nothing across around report reports reported record records note notes
noted source sources status flags subject background curated primary derived section extract
patient sample result results value values units unit reference range normal high low elevated
decreased increased positive negative none reported date name test tests panel level levels within
outside total free ratio marker markers analyte analytes measured taken given first second third
overview timeline summary index page pages line lines location loc quote verbatim item items
collected collection drawn specimen
reorganised reorganized reorganise reorganize reorder reordered reordering ordering ordered order
single table tables column columns header headers into faithful extracted extraction provenance
converted artifact tool staged reformatted restructured original document rows preserved
ambiguous surfaced resolved unresolved flagged organism organisms count counts
""".split())

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9'\-]*")
# analyte-shaped: mixed alnum (HbA1c, 25-OH, T3, rT3, B12) or short ALLCAPS acronym (TSH, DHEA)
_ANALYTE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9\-]{2,}$|^[A-Z]{2,6}(?:-[A-Z0-9]{1,3})?$")

# =============================================================================================
# Provenance / structure stripping — decide what is CONTENT vs. extractor-added scaffolding
# =============================================================================================

_SRC_CITE = re.compile(r"\[src:[^\]]*\]")           # provenance appendages — never content
_MD_TAG = re.compile(r"\[[a-z][a-z \-]*\]", re.I)   # [interpretation], [self-report], ...
_CONV_HEADER = re.compile(r"^\s*<<<.*?>>>\s*$")     # converter provenance header lines
_PAGE_MARK = re.compile(r"^\s*(?:[-=]{2,}|\f)?\s*(?:page|pg)\s+\d+\s*(?:of\s+\d+\s*)?(?:[-=]{2,})?\s*$", re.I)


_CODEPOINT = re.compile(r"[Uu]\+[0-9A-Fa-f]{4,6}")  # 'U+0435' -> its '435' must not become a number


def _strip_noise(text):
    """Blank annotation scaffolding that appears on EITHER side and pollutes the diff: [src:]
    provenance citations, unicode codepoint mentions (U+0435 — the extractor writes these when
    flagging homoglyphs) and inline page references (Page 1 / pg 3). Applied to BOTH sides.

    Stripping [src:] on both sides matters when the 'source' is itself a compiled artifact that
    carries citations — the Phase-B QC diffs a VIEW against the EVENT LOG, and BOTH sides then hold
    `[src: ..., "raw quote"]` appendages. The extraction side already dropped them (strip_extraction);
    if the source side keeps them, a value inside a quote (e.g. a reference-range bound sitting next
    to a unit in the quoted text: "3.2-38.6 mg/g") picks up a unit on the source side but not the
    view side, producing SPURIOUS unit_issues. A genuine raw converter source never contains
    '[src:', so stripping it there is a harmless no-op for the Phase-A source-vs-extract case."""
    text = _SRC_CITE.sub(" ", text)
    text = _CODEPOINT.sub(" ", text)
    text = _PAGE_REF.sub(" ", text)
    text = _LIST_ORDINAL.sub(" ", text)
    return text


def strip_source(text):
    """Source side: drop the converter's <<<...>>> provenance header lines and page-delimiter
    markers (e.g. '--- Page 1 ---') — converter scaffolding, not content. [src:] citations (present
    only when the 'source' is a compiled event log) are dropped by _strip_noise for both-side symmetry."""
    text = text.replace("\f", "\n")
    text = "\n".join(l for l in text.split("\n")
                     if not _CONV_HEADER.match(l) and not _PAGE_MARK.match(l))
    return _strip_noise(text)


def _keep_src_quotes(m):
    """[src: name, loc, "verbatim quote"] -> keep ONLY the "quoted" content (verbatim source text =
    real captured content), dropping the src:/location metadata and the brackets. Used in Phase-A
    (raw source has no [src:] of its own) so a value the extractor placed INSIDE its citation quote
    counts as CAPTURED — present in the extract — not a false omission that spawns pass-2 rework.

    A leading list-ordinal INSIDE a verbatim quote (a genuinely-numbered source line, quoted back) is
    the same list rendering _LIST_ORDINAL blanks at line-start on the source side; strip it here too so
    the re-injected (now mid-line) quote stays SYMMETRIC with the source and does not leave a phantom
    ordinal number atom on the extract side."""
    parts = [re.sub(r"^\s*\d+[.)](?=\s)", " ", q) for q in re.findall(r'"([^"]*)"', m.group(0))]
    return " " + " ".join(parts) + " "


def strip_extraction(text, keep_src_quotes=False):
    """Extraction side: drop [src: ...] provenance citations and [tag] markers and markdown
    emphasis, but KEEP table-cell values and prose (that is the extracted content). When
    keep_src_quotes is True (Phase-A: the raw source carries no citations of its own), the verbatim
    text inside each [src: ..., "quote"] is RETAINED as captured content instead of blanked — a
    quoted value is present in the extract, so coverage must not read it as omitted. Phase-B (the
    'source' is a compiled event log that itself carries [src:]) keeps the symmetric full blanking."""
    text = _SRC_CITE.sub(_keep_src_quotes if keep_src_quotes else " ", text)
    text = _MD_TAG.sub(" ", text)
    text = text.replace("*", " ").replace("|", " ").replace("`", " ")
    return _strip_noise(text)


# =============================================================================================
# DATES  — extract first so their digit components never pollute NUMBER atoms
# =============================================================================================

_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
# a numeric date requires the SAME separator between all parts (\2 backref), so a decimal
# reference range like 12.0-22.0 (mixed '.' and '-') is NOT misread as a date. The separator class
# includes unicode hyphen variants — soft hyphen U+00AD, the U+2010..U+2015 dash block, and the
# minus sign U+2212 — because real converted sources embed them (e.g. a SIBO collection date
# rendered '13­12­2023'); a range still has only ONE separator so it never matches here.
_NUMERIC_DATE = re.compile(r"\b(\d{1,2})([/.\-­‐‑‒–—―−])(\d{1,2})\2(\d{2,4})\b")
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
# an optional ordinal suffix (1st/2nd/3rd/4th) on the day is accepted — real sources write
# "3rd March 2025" (a consumer blood panel) — the suffix is non-capturing so the day/month/year groups are unchanged.
# day/month/year may be separated by whitespace OR hyphen/dash (real sources write "3rd September
# 2024" AND "12-Nov-2024") — a hyphenated month-name date must parse or the ISO the extractor writes
# reads as a fabricated date the source "does not contain".
_MDSEP = r"[\s/.\-­‐‑‒–—―−]+"
_MONTH_NAME_DATE = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?" + _MDSEP + r"([A-Za-z]{3,9})\.?" + _MDSEP + r"(\d{4})\b"   # 3rd September 2024 / 12-Nov-2024
    r"|\b([A-Za-z]{3,9})\.?" + _MDSEP + r"(\d{1,2})(?:st|nd|rd|th)?,?" + _MDSEP + r"(\d{4})\b",  # September 3rd, 2024 / Nov-12-2024
    re.I)


def _month_num(name):
    return _MONTHS.get(name[:3].lower())


def extract_dates(text):
    """Return (dates:list[(iso,context)], ambiguous:list[(raw,context,note)]) and the text with
    every matched date span blanked out (so NUMBER extraction never sees date digits)."""
    dates, ambiguous = [], []
    spans = []

    for m in _ISO.finditer(text):
        y, mo, d = m.groups()
        dates.append(("%s-%s-%s" % (y, mo, d), _ctx(text, m.start(), m.end())))
        spans.append((m.start(), m.end()))

    for m in _MONTH_NAME_DATE.finditer(text):
        if m.group(1):   # D Month YYYY
            d, mon, y = m.group(1), m.group(2), m.group(3)
        else:            # Month D YYYY
            d, mon, y = m.group(5), m.group(4), m.group(6)
        mn = _month_num(mon)
        if not mn:
            continue
        try:
            iso = "%04d-%02d-%02d" % (int(y), mn, int(d))
        except ValueError:
            continue
        dates.append((iso, _ctx(text, m.start(), m.end())))
        spans.append((m.start(), m.end()))

    for m in _NUMERIC_DATE.finditer(text):
        a, b, y = int(m.group(1)), int(m.group(3)), m.group(4)
        yy = int(y) if len(y) == 4 else 2000 + int(y)
        ctx = _ctx(text, m.start(), m.end())
        spans.append((m.start(), m.end()))
        if a > 12 and b <= 12:            # a is day -> D/M/Y unambiguous
            iso = _safe_iso(yy, b, a)
            (dates if iso else ambiguous).append((iso, ctx) if iso else (m.group(0), ctx, "unparseable numeric date"))
        elif b > 12 and a <= 12:          # b is day -> M/D/Y unambiguous
            iso = _safe_iso(yy, a, b)
            (dates if iso else ambiguous).append((iso, ctx) if iso else (m.group(0), ctx, "unparseable numeric date"))
        elif a <= 12 and b <= 12:
            ambiguous.append((m.group(0), ctx, "day/month order ambiguous (both <= 12)"))
        else:
            ambiguous.append((m.group(0), ctx, "unparseable numeric date"))

    # blank the date spans
    chars = list(text)
    for s, e in spans:
        for i in range(s, e):
            chars[i] = " "
    return dates, ambiguous, "".join(chars)


def _ambiguous_iso_options(raw):
    """Both ISO readings (D/M/Y and M/D/Y) of an ambiguous numeric date string like '10/05/1991'.
    Used to recognise that an ISO date in the extract merely RESOLVES an ambiguous source date (it is
    covered, not fabricated). Returns a set of valid ISO strings (empty if the raw does not parse)."""
    m = _NUMERIC_DATE.search(raw)
    if not m:
        return set()
    a, b, y = int(m.group(1)), int(m.group(3)), m.group(4)
    yy = int(y) if len(y) == 4 else 2000 + int(y)
    opts = set()
    for mo, da in ((b, a), (a, b)):        # D/M/Y then M/D/Y
        iso = _safe_iso(yy, mo, da)
        if iso:
            opts.add(iso)
    return opts


def _safe_iso(y, mo, d):
    try:
        if 1 <= mo <= 12 and 1 <= d <= 31 and 1900 <= y <= 2100:
            return "%04d-%02d-%02d" % (y, mo, d)
    except Exception:
        pass
    return None


# =============================================================================================
# NUMBERS (+ adjacent unit)
# =============================================================================================

# a signed decimal / thousands-grouped / scientific number.
# A2: also match a number GLUED to its unit ("45mg", "12mmol/L", "1,200mg") and a LEADING-DOT decimal
# (".5"). Two changes vs the original:
#   - trailing guard (?![\d]) (was (?![\w])) — a unit letter may now follow the digits; extract_numbers
#     then keeps a glued-alpha match ONLY when the following run is a valid unit, so "19th"/"3D"/"COVID19b"
#     still produce no number (matched then skipped), preserving the old behaviour for non-unit glue.
#   - a `|[+-]?\.\d+(?:[eE]…)?` alternative captures a decimal written without a leading zero.
_NUM = re.compile(r"(?<![\w.])([+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?|[+-]?\.\d+(?:[eE][+-]?\d+)?)(?![\d])")
# a unit token immediately after a number: letters/% + micro sign, optional /denominator, and an
# optional 'x10^N' count prefix. Deliberately does NOT allow whitespace before a trailing number,
# so it never swallows the following reference-range value (e.g. 'ug/L    15' must stay 'ug/L').
_UNIT_AFTER = re.compile(r"[ \t]*(%|(?:x?10\^?\d+/)?[A-Za-zµμ]+(?:/[A-Za-zµμ0-9^]+)?)")

# curated unit normalization — spelling only, NEVER value conversion
_UNIT_MAP = {
    "mcg": "ug", "ug": "ug", "mug": "ug", "µg": "ug", "μg": "ug",
    "mcg/dl": "ug/dl", "ug/dl": "ug/dl",
    "mg/dl": "mg/dl", "mg/l": "mg/l", "g/dl": "g/dl",
    "mmol/l": "mmol/l", "umol/l": "umol/l", "µmol/l": "umol/l", "nmol/l": "nmol/l",
    "pmol/l": "pmol/l", "iu/l": "iu/l", "miu/l": "miu/l", "uiu/ml": "uiu/ml",
    "ng/ml": "ng/ml", "pg/ml": "pg/ml", "ng/dl": "ng/dl",
    "cfu/g": "cfu/g", "cfu/ml": "cfu/ml",
}
# base (single) units — a compound "a/b" is a valid unit iff each part is a base unit or %.
_BASE_UNITS = {
    "mg", "g", "kg", "ug", "mcg", "ng", "pg", "fg", "l", "ml", "dl", "ul", "u", "iu",
    "miu", "uiu", "meq", "mmol", "umol", "nmol", "pmol", "mol", "cfu", "mm", "cm", "m",
    "mmhg", "bpm", "kpa", "s", "min", "hr", "yr", "%", "cells", "wbc", "rbc",
}
_PART_MAP = {"mcg": "ug", "µg": "ug", "μg": "ug"}


def _norm_unit(raw):
    if not raw:
        return ""
    u = match_copy(raw).lower().strip()
    u = re.sub(r"\s*/\s*", "/", u)
    u = re.sub(r"\s*\^\s*", "^", u)
    u = u.rstrip(".")
    if u in _UNIT_MAP:
        return _UNIT_MAP[u]
    parts = u.split("/")
    parts = [_PART_MAP.get(p, p) for p in parts]
    return "/".join(parts)


def _is_unit(cand):
    """True if cand is a plausible medical unit — a base unit, %, x10^N, or a '/'-compound of
    base units. Guards against attaching a stray following word (e.g. a label) as a 'unit'."""
    if not cand:
        return False
    if cand in _UNIT_MAP or cand in _UNIT_MAP.values():
        return True
    if re.match(r"^x?10\^?\d+$", cand):
        return True
    parts = cand.split("/")
    return all(p in _BASE_UNITS or re.match(r"^x?10\^?\d+$", p) for p in parts) and len(parts) <= 2


def _canon_number(raw):
    s = raw.replace(",", "")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def extract_numbers(text):
    """Return list of dicts {value:Decimal, unit:str, context:str}. Ranges fall out naturally:
    an en-dash '1.0e6-5.0e7' yields two matches; an ASCII-hyphen range is pre-split so the second
    number is not read as negative."""
    # pre-split ASCII-hyphen ranges (digit-hyphen-digit) so 5.0e7 isn't parsed as -5.0e7
    text = re.sub(r"(?<=\d)\s*[-–—]\s*(?=[+]?\d)", " ", text)
    out = []
    for m in _NUM.finditer(text):
        val = _canon_number(m.group(1))
        if val is None:
            continue
        end = m.end()
        unit = ""
        um = _UNIT_AFTER.match(text, end)
        if um:
            cand = _norm_unit(um.group(1))
            if _is_unit(cand):
                unit = cand
        # A2: a number glued directly to an ALPHA run that is NOT a valid unit is part of an
        # identifier/word ("19th", "3D", "COVID19b") — not a measured value — so skip it. This restores
        # the original (?![\w]) behaviour for non-unit glue while still capturing "45mg"/"12mmol/L".
        if not unit and end < len(text) and text[end].isalpha():
            continue
        out.append({"value": val, "unit": unit, "context": _ctx(text, m.start(), end)})
    return out


# =============================================================================================
# ENTITIES
# =============================================================================================

# capitalized multiword name. Continuation tokens must start with a LETTER — a trailing number is
# never part of an entity name, so "Reference 11", "Count 1", "Page 1", "MRN 88021" do NOT become
# phantom entities (a real false-positive source on model-formatted per-cell tables).
_CAP_PHRASE = re.compile(r"\b([A-Z][A-Za-z0-9]+(?:[ \-][A-Z][A-Za-z0-9]*)*)\b")
# page references ("Page 1", "pg 3") are converter/layout scaffolding, not content — blanked on
# BOTH sides before number/entity extraction so neither the word nor the page number becomes an atom.
_PAGE_REF = re.compile(r"(?i)\b(?:page|pg)\.?\s*\d+\b")

# Leading markdown/list ORDINAL ("1. ", "2) ") at the start of a line — list RENDERING the extractor
# adds when it turns a source bullet/prose list into a numbered list. Blanked on BOTH sides (via
# _strip_noise) so an enumeration index the extractor introduced does not read as a fabricated number
# (nor, symmetrically, as an omission if the source itself was numbered). SAFE by construction: it
# matches ONLY a run of digits IMMEDIATELY followed by '.'/')' AND then whitespace, at line start — so
# a decimal ("3.2 mg", no whitespace after the dot) and a bare year/value at line start ("1990 ...",
# no dot) are NOT touched, and any value AFTER the marker ("1. 45 mg" -> "45 mg") is preserved. This
# does not cover bare row-index CELLS ("| 7 |"), which are indistinguishable from data and are handled
# upstream by the Phase-A extract prompt (no added enumeration numbers), not here.
_LIST_ORDINAL = re.compile(r"(?m)^[ \t]*\d+[.)](?=\s)")

# A3: provenance-token shape guards — a source-filename token that is a bare number ("1250") or a date
# ("2024-03-15", or a bare year "2024") is CONTENT, not metadata, so it must NOT be blanked from the
# extraction side (blanking it hid the A3 false-clean: a fabricated value equal to the filename stem).
_PROV_PURE_NUM = re.compile(r"^[+-]?\d[\d,]*(?:\.\d+)?$")
_PROV_DATE_SHAPED = re.compile(r"^\d{4}$|^\d{1,4}[-/.]\d{1,2}(?:[-/.]\d{1,4})?$")


def _canon_entity(tok):
    t = match_copy(tok)
    if _unidecode:
        t = _unidecode(t)
    return t.lower().strip(" -'")


def extract_entities(text, entity_min, extra_stop=frozenset()):
    """Distinctive content words (len >= entity_min, not stop/structural), plus capitalized
    multiword phrases, plus analyte-shaped tokens. Returns a set of canonical entity strings and a
    map canon->example-context. extra_stop suppresses run-specific scaffolding (e.g. the source
    filename stem, which appears in both the converter header and the extractor's title).

    The text is unicode-folded (match_copy) BEFORE tokenizing so a homoglyph inside a word
    (Cyrillic 'o' in 'Lactobacillus') does not split the ASCII _WORD token — otherwise the source
    would yield the fragment 'bacillus' while the clean extraction yields 'lactobacillus', producing
    a spurious omission+fabrication pair."""
    text = match_copy(text)
    ents, ctx = set(), {}

    def add(raw, at):
        c = _canon_entity(raw)
        if len(c) < 3 or c in STOP or c in extra_stop:
            return
        ents.add(c)
        ctx.setdefault(c, _ctx(text, at, at + len(raw)))

    # capitalized phrases (multi-word medical names: "Lactobacillus spp", "Free Testosterone")
    for m in _CAP_PHRASE.finditer(text):
        raw = m.group(1)
        if len(raw) >= 3 and _canon_entity(raw) not in STOP:
            add(raw, m.start())

    for m in _WORD.finditer(text):
        tok = m.group(0)
        low = tok.lower()
        if low in STOP:
            continue
        if _ANALYTE.match(tok) or len(low) >= entity_min:
            add(tok, m.start())
    return ents, ctx


# =============================================================================================
# context helper
# =============================================================================================

def _ctx(text, start, end, width=32):
    a = max(0, start - width)
    b = min(len(text), end + width)
    return re.sub(r"\s+", " ", text[a:b]).strip()


# =============================================================================================
# POLARITY (A1) — result poles the NUMBER/DATE/ENTITY channels miss. The pole words are stopwords AND
# the entity channel is only advisory, so a flipped result (positive->negative, reactive->non-reactive,
# present->absent, high->low) is invisible today. A conserved-total FLIP is a HARD fidelity failure.
# =============================================================================================

# canonical pole word -> (family, sign). A negation prefix ("non-"/"not"/"no"/"un") flips the sign.
_POLARITY_POLE = {
    "positive": ("posneg", 1),   "negative": ("posneg", -1),
    "present": ("presence", 1),  "absent": ("presence", -1),
    "reactive": ("react", 1),
    "detected": ("detect", 1),
    "high": ("highlow", 1),      "elevated": ("highlow", 1),
    "low": ("highlow", -1),      "reduced": ("highlow", -1),   "decreased": ("highlow", -1),
}
# (family, sign) -> a readable word for the reported atom
_POLE_WORD = {
    ("posneg", 1): "positive",  ("posneg", -1): "negative",
    ("presence", 1): "present", ("presence", -1): "absent",
    ("react", 1): "reactive",   ("react", -1): "non-reactive",
    ("detect", 1): "detected",  ("detect", -1): "not detected",
    ("highlow", 1): "high",     ("highlow", -1): "low",
}
_POLARITY_RE = re.compile(
    r"\b(?P<neg>non-?|not\s+|no\s+|un)?"
    r"(?P<w>positive|negative|present|absent|reactive|detected|elevated|decreased|reduced|high|low)\b",
    re.I)


def extract_polarity(text):
    """A1: per-family multiset of result poles + an example context per (family, sign). A negation prefix
    flips the sign ('non-reactive' -> react/-1); a bare pole glued into a hyphenated compound NAME
    ('high-density', 'low-grade') is not a result and is skipped."""
    counts = defaultdict(int)
    ctx = {}
    for m in _POLARITY_RE.finditer(text):
        fam, sign = _POLARITY_POLE[m.group("w").lower()]
        if m.group("neg"):
            sign = -sign
        else:
            tail = text[m.end():m.end() + 2]
            if tail[:1] == "-" and tail[1:2].isalpha():
                continue
        counts[(fam, sign)] += 1
        ctx.setdefault((fam, sign), _ctx(text, m.start(), m.end()))
    return counts, ctx


# =============================================================================================
# atomize a side
# =============================================================================================

def atomize(text, side, entity_min, extra_stop=frozenset(), source_has_cite=True):
    text = strip_source(text) if side == "source" else strip_extraction(text, keep_src_quotes=not source_has_cite)
    polarity, pol_ctx = extract_polarity(text)
    dates, ambiguous, text_nodate = extract_dates(text)
    numbers = extract_numbers(text_nodate)
    entities, ent_ctx = extract_entities(text_nodate, entity_min, extra_stop)
    return {
        "dates": dates, "ambiguous": ambiguous,
        "numbers": numbers, "entities": entities, "ent_ctx": ent_ctx,
        "polarity": polarity, "pol_ctx": pol_ctx,
    }


# =============================================================================================
# fuzzy entity match
# =============================================================================================

def _sim(a, b):
    if _rf_fuzz is not None:
        return _rf_fuzz.token_sort_ratio(a, b) / 100.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def entity_covered(src_ent, ext_set, ext_exact, theta):
    """True if src_ent is present in the extraction. Exact match always counts; fuzzy only for
    tokens of length >= 5 (short analytes must match exactly so DHEA != DHEA-S), AND only when the
    length delta is small. OCR noise is typically a single-character substitution (same length),
    whereas a genuinely different analyte differs by a whole morpheme — e.g. creatine vs creatinine
    (ratio 0.889, but +2 chars). The length-delta guard refuses that collapse where a raw ratio
    threshold alone (0.88) would wrongly merge two clinically distinct analytes."""
    if src_ent in ext_exact:
        return True
    if len(src_ent) < 5:
        return False
    for e in ext_set:
        if len(e) < 5:
            continue
        if abs(len(e) - len(src_ent)) > max(1, max(len(e), len(src_ent)) // 10):
            continue
        if _sim(src_ent, e) >= theta:
            return True
    return False


# =============================================================================================
# the diff
# =============================================================================================

def diff(src, ext, theta):
    # HARD keys (drive the exit code and the workflow converge loop) are the clean, exact-match
    # channels: numbers, dates, units, binding. ENTITY diffs are ADVISORY (surfaced for human
    # review, never loop-driving) — the extractor legitimately writes prose annotation (OCR notes,
    # homoglyph explanations) whose content words cannot be told apart from hallucinated data by a
    # lexical diff. The smoke test proved entity fabrication is too noisy to gate on.
    report = {"omissions": [], "fabrications": [], "unit_issues": [], "binding_issues": [],
              "entity_omissions": [], "entity_fabrications": [], "ambiguous": []}

    # --- NUMBERS: EXACT by Decimal value, SET-based (presence). Set (not multiset) so the extractor
    #     re-quoting a value in prose does not inflate the count into a phantom fabrication. ---
    src_num_ctx = defaultdict(list)
    for a in src["numbers"]:
        src_num_ctx[a["value"]].append(a)
    ext_num_ctx = defaultdict(list)
    for a in ext["numbers"]:
        ext_num_ctx[a["value"]].append(a)
    src_num, ext_num = set(src_num_ctx), set(ext_num_ctx)

    for val in sorted(src_num - ext_num, key=str):
        ex = src_num_ctx[val][0]
        report["omissions"].append({"type": "number", "atom": _fmt_num(val, ex["unit"]),
                                    "context": ex["context"]})
    for val in sorted(ext_num - src_num, key=str):
        ex = ext_num_ctx[val][0]
        report["fabrications"].append({"type": "number", "atom": _fmt_num(val, ex["unit"]),
                                       "context": ex["context"]})

    # --- UNITS: for numbers present on BOTH sides, a source unit that is dropped/changed ---
    for val in src_num & ext_num:
        src_units = {a["unit"] for a in src_num_ctx[val] if a["unit"]}
        ext_units = {a["unit"] for a in ext_num_ctx[val] if a["unit"]}
        if src_units and not (src_units & ext_units):
            report["unit_issues"].append({
                "type": "unit", "atom": _fmt_num(val, ""),
                "source_unit": sorted(src_units), "extraction_unit": sorted(ext_units) or ["(none)"],
                "context": src_num_ctx[val][0]["context"]})

    # --- POLARITY (A1): a conserved-total pole FLIP is a HARD fidelity failure. Only flag a FLIP —
    #     the family's total count is preserved but the per-pole split differs — so legitimate
    #     reformatting that ADDS or DROPS a pole (a raw 'H' flag rewritten as the word 'high', or a
    #     dropped attendance 'present') changes the total and is NOT flagged (avoids false positives).
    #     The over-asserted extraction pole is reported as a FABRICATION (the hard channel the workflow
    #     already gates on) so a flip drives the converge loop, the exit code, and the A7 halt. ---
    src_pol, ext_pol = src["polarity"], ext["polarity"]
    for fam in sorted({f for (f, _s) in set(src_pol) | set(ext_pol)}):
        s_by = {sg: n for (f, sg), n in src_pol.items() if f == fam}
        e_by = {sg: n for (f, sg), n in ext_pol.items() if f == fam}
        s_tot, e_tot = sum(s_by.values()), sum(e_by.values())
        if s_tot > 0 and s_tot == e_tot and s_by != e_by:
            for sg in sorted(e_by):
                if e_by.get(sg, 0) > s_by.get(sg, 0):   # the extract over-asserts this pole = the flip
                    report["fabrications"].append({
                        "type": "polarity",
                        "atom": _POLE_WORD.get((fam, sg), fam),
                        "context": ext["pol_ctx"].get((fam, sg), "")})

    # --- DATES: EXACT on ISO string, SET-based ---
    src_d_ctx = {d: c for d, c in src["dates"]}
    ext_d_ctx = {d: c for d, c in ext["dates"]}
    src_d, ext_d = set(src_d_ctx), set(ext_d_ctx)
    # A source numeric date with both parts <= 12 (e.g. "10/05/1991") is AMBIGUOUS and held out of
    # src_d — but the extractor, told to write ISO, resolves it to one reading ("1991-05-10"). That ISO
    # is NOT a fabrication: it is a valid reading of a date the source genuinely contains. Cover an
    # extract date that equals EITHER interpretation of any ambiguous source date (the ambiguous entry
    # still surfaces for human review; picking a reading is not inventing data).
    src_ambig_iso = set()
    for _raw, _c, _n in src["ambiguous"]:
        src_ambig_iso |= _ambiguous_iso_options(_raw)
    for d in sorted(src_d - ext_d):
        report["omissions"].append({"type": "date", "atom": d, "context": src_d_ctx.get(d, "")})
    for d in sorted(ext_d - src_d):
        if d in src_ambig_iso:
            continue
        report["fabrications"].append({"type": "date", "atom": d, "context": ext_d_ctx.get(d, "")})

    # --- ambiguous source dates (surface, don't guess) ---
    for raw, ctx, note in src["ambiguous"]:
        report["ambiguous"].append({"type": "date", "atom": raw, "context": ctx, "note": note})

    # --- ENTITIES: fuzzy set diff both directions — ADVISORY only ---
    ext_exact = set(ext["entities"])
    src_exact = set(src["entities"])
    for e in sorted(src["entities"]):
        if not entity_covered(e, ext["entities"], ext_exact, theta):
            report["entity_omissions"].append({"type": "entity", "atom": e,
                                               "context": src["ent_ctx"].get(e, "")})
    for e in sorted(ext["entities"]):
        if not entity_covered(e, src["entities"], src_exact, theta):
            report["entity_fabrications"].append({"type": "entity", "atom": e,
                                                 "context": ext["ent_ctx"].get(e, "")})
    return report


def _fmt_num(val, unit):
    s = format(val.normalize(), "f") if val == val.to_integral_value() and abs(val) < Decimal("1e16") else str(val.normalize())
    return (s + " " + unit).strip() if unit else s


# =============================================================================================
# optional position-aware binding check ("right number, wrong row")
# =============================================================================================

def binding_check(pos_path, ext_text, theta, report):
    """Given a converter .pos.json sidecar [{text, x0,y0,x1,y1, page}], for each number extracted
    under a markdown-table label 'Label | value | ...', verify the same number's nearest-left word
    on the same source line matches Label (fuzzy). Degrades to no-op on any problem."""
    try:
        with open(pos_path, "r", encoding="utf-8") as f:
            words = json.load(f)
    except Exception:
        return
    if not isinstance(words, list) or not words:
        return
    # index numbers -> the nearest-left alphabetic word on the same page/row band
    src_pairs = []  # (number_value, left_label_canon)
    by_line = defaultdict(list)
    for w in words:
        try:
            key = (w.get("page", 0), round(float(w.get("y0", 0)) / 3.0))
            by_line[key].append(w)
        except Exception:
            continue
    for key, ws in by_line.items():
        ws.sort(key=lambda w: float(w.get("x0", 0)))
        for i, w in enumerate(ws):
            val = _canon_number(str(w.get("text", "")).strip())
            if val is None:
                continue
            label = ""
            for j in range(i - 1, -1, -1):
                cand = str(ws[j].get("text", ""))
                if re.search(r"[A-Za-z]{3,}", cand):
                    label = _canon_entity(cand)
                    break
            if label:
                src_pairs.append((val, label))
    src_label = defaultdict(set)
    for val, label in src_pairs:
        src_label[val].add(label)

    # extraction table rows: 'Label | value | ...'
    for line in ext_text.split("\n"):
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        row_label = _canon_entity(re.sub(r"\[src:[^\]]*\]", "", cells[0]))
        if len(row_label) < 3:
            continue
        for c in cells[1:]:
            val = _canon_number(re.sub(r"[^\d.,+eE-]", "", c) or "x")
            if val is None or val not in src_label:
                continue
            labels = src_label[val]
            if any(_sim(row_label, sl) >= theta or row_label in sl or sl in row_label for sl in labels):
                continue
            report["binding_issues"].append({
                "type": "binding", "atom": _fmt_num(val, ""), "extracted_label": row_label,
                "source_labels": sorted(labels),
                "note": "value bound to a label that does not match its source row"})


# =============================================================================================
# main
# =============================================================================================

def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def main(argv=None):
    ap = argparse.ArgumentParser(description="bidirectional content-atom coverage diff")
    ap.add_argument("--source", required=True)
    ap.add_argument("--extraction", nargs="+", required=True)
    ap.add_argument("--positions", default=None)
    ap.add_argument("--theta", type=float, default=0.88)
    ap.add_argument("--entity-min", type=int, default=6)
    ap.add_argument("--brief", action="store_true",
                    help="omit the (large, advisory) entity + binding arrays from stdout, keeping the "
                         "summary counts and the small HARD worklist. Lets a workflow diff-runner "
                         "agent echo the result without re-serialising huge arrays token-by-token.")
    args = ap.parse_args(argv)

    src_text = _read(args.source)
    ext_text = "\n".join(_read(p) for p in args.extraction)

    # --- provenance filename blanking (both sides) ---------------------------------------------
    # The extractor legitimately writes a "Source (original, canonical): <path>" header into the
    # extract. That path often carries DATE DIGITS (e.g. "...Letter08Apr2024_2025-08-15...pdf") which
    # are NOT source content — but they leak as phantom NUMBER/DATE fabrications and can block
    # convergence forever (the resolver can't remove a filename it keeps re-citing). The source's own
    # <<<source: PATH>>> converter header is already stripped from the SOURCE side (strip_source), so
    # blank the SAME original path/filename/stem, plus the converted filename, on the EXTRACTION side.
    _prov = {os.path.basename(args.source), os.path.splitext(os.path.basename(args.source))[0]}
    _hm = re.search(r"<<<\s*source:\s*(.+?)\s*>>>", src_text, re.I)
    if _hm:
        _orig = _hm.group(1).strip()
        _prov.update({_orig, os.path.basename(_orig), os.path.splitext(os.path.basename(_orig))[0]})
    for _nm in sorted((n for n in _prov if n and len(n) >= 4), key=len, reverse=True):
        # A3: never blank a provenance token that is a BARE NUMBER or DATE — blanking it would erase a
        # legitimate (or FABRICATED) numeric/date CONTENT atom that merely coincides with the source
        # filename. A real filename WORD (e.g. 'Letter08Apr2024') still carries letters, so it is still
        # blanked. And blank only at WORD BOUNDARIES so the stem cannot nuke a longer token that merely
        # contains it as a substring.
        if _PROV_PURE_NUM.match(_nm) or _PROV_DATE_SHAPED.match(_nm):
            continue
        ext_text = re.sub(r"(?<![\w-])" + re.escape(_nm) + r"(?![\w-])", " ", ext_text)

    # the source filename stem is metadata (it appears in the converter header AND the extractor's
    # title/[src:] cites) — never treat its tokens as content atoms.
    stem = os.path.splitext(os.path.basename(args.source))[0]
    _st = {_canon_entity(stem)}
    _st.update(_canon_entity(t) for t in re.split(r"[^A-Za-z0-9]+", stem) if len(t) >= 3)
    extra_stop = frozenset(t for t in _st if t)

    # Phase-A (raw source, no [src:]) vs Phase-B (source is a compiled event log carrying [src:]).
    # In Phase-A a value inside the extraction's [src:"quote"] is CAPTURED content, not an omission.
    source_has_cite = "[src:" in src_text
    src = atomize(src_text, "source", args.entity_min, extra_stop)
    ext = atomize(ext_text, "extraction", args.entity_min, extra_stop, source_has_cite=source_has_cite)
    report = diff(src, ext, args.theta)

    if args.positions:
        # raw ext_text: binding_check needs the '|' table structure and does its own per-cell
        # [src:] stripping — do NOT pre-strip (that removes the pipes it keys on).
        binding_check(args.positions, ext_text, args.theta, report)

    report["deps"] = DEPS
    report["summary"] = {
        "omissions": len(report["omissions"]),
        "fabrications": len(report["fabrications"]),
        "unit_issues": len(report["unit_issues"]),
        "binding_issues": len(report["binding_issues"]),
        "entity_omissions": len(report["entity_omissions"]),
        "entity_fabrications": len(report["entity_fabrications"]),
        "ambiguous": len(report["ambiguous"]),
    }
    if args.brief:
        # keep summary counts + the small HARD worklist; empty the large advisory arrays (their real
        # counts remain in `summary`) so a diff-runner agent can echo this without a huge
        # token-by-token re-serialisation. `briefOmitted` records what was dropped.
        report["briefOmitted"] = {"entity_omissions": report["summary"]["entity_omissions"],
                                  "entity_fabrications": report["summary"]["entity_fabrications"],
                                  "binding_issues": report["summary"]["binding_issues"]}
        report["entity_omissions"] = []
        report["entity_fabrications"] = []
        report["binding_issues"] = []

    sys.stdout.write(json.dumps(report, indent=2, default=str) + "\n")

    # exit code reflects HARD gaps only: numbers/dates (exact, set-based) + units. Binding and
    # entity diffs are ADVISORY — the real multi-source run showed the position-aware "nearest-left
    # label" binding check false-positives badly on real layouts (values repeated across rows, e.g.
    # a common bacterial abundance, and page-footer numbers colliding with score values), so gating
    # on it makes the resolver chase phantom "wrong row" gaps forever. It is reported for review.
    hard = (report["summary"]["omissions"] + report["summary"]["fabrications"]
            + report["summary"]["unit_issues"])
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
