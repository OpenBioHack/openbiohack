#!/usr/bin/env python3
"""convert-iwork.py — text extraction for modern Apple iWork bundles (.pages/.numbers/.key).

Modern iWork files are zip bundles whose content lives in Index/*.iwa: Snappy-compressed
Protobuf ("IWA"). There is no QuickLook/Preview.pdf to lift (that only exists in the legacy
'09 format), no textutil path, and no Pages/Numbers app on a headless box — which is why the
bundled converter previously had to escalate these as unhandled.

This reads the IWA directly with no third-party dependencies:
  1. unzip Index/*.iwa
  2. decode the IWA chunk framing (4-byte header: 0x00 + uint24-LE compressed length)
  3. raw-Snappy-decompress each chunk (implemented below; the stdlib has no snappy)
  4. walk the Protobuf wire format and collect length-delimited fields that are valid UTF-8
     text — in iWork these carry the document's actual strings (paragraph runs, cell values)

It is a TEXT extractor, not a layout/format extractor: it recovers what the document SAYS,
not how it looked. Ordering follows the document's own storage order, which for prose and
for table cells is close to reading order. Styling, images, and formulas are dropped.

Emits the text to <out_txt>. Exit codes:
  0  success (real text recovered)
  3  no text recovered (bundle is empty, image-only, or an unexpected variant) — caller may
     fall back to OCR of the bundle's preview.jpg
  4  not a readable iWork zip bundle
"""
import sys
import re
import zipfile
import argparse


def snappy_raw_decompress(data: bytes) -> bytes:
    """Minimal raw-Snappy decoder (no framing). Python has no stdlib snappy."""
    # preamble: varint uncompressed length
    pos, shift, ulen = 0, 0, 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        ulen |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    out = bytearray()
    n = len(data)
    while pos < n:
        tag = data[pos]
        kind = tag & 0x03
        if kind == 0:  # literal
            ln = tag >> 2
            pos += 1
            if ln < 60:
                ln += 1
            else:
                extra = ln - 59
                ln = int.from_bytes(data[pos:pos + extra], "little") + 1
                pos += extra
            out += data[pos:pos + ln]
            pos += ln
            continue
        if kind == 1:  # copy, 1-byte offset
            ln = 4 + ((tag >> 2) & 0x07)
            off = ((tag >> 5) << 8) | data[pos + 1]
            pos += 2
        elif kind == 2:  # copy, 2-byte offset
            ln = (tag >> 2) + 1
            off = int.from_bytes(data[pos + 1:pos + 3], "little")
            pos += 3
        else:  # copy, 4-byte offset
            ln = (tag >> 2) + 1
            off = int.from_bytes(data[pos + 1:pos + 5], "little")
            pos += 5
        if off == 0 or off > len(out):
            break
        start = len(out) - off
        for i in range(ln):  # overlapping copies are legal in snappy
            out.append(out[start + i])
    return bytes(out[:ulen] if ulen else out)


def iwa_chunks(raw: bytes) -> bytes:
    """Decode IWA chunk framing into one decompressed protobuf byte stream."""
    out = bytearray()
    pos = 0
    while pos + 4 <= len(raw):
        if raw[pos] != 0x00:
            break
        clen = int.from_bytes(raw[pos + 1:pos + 4], "little")
        pos += 4
        block = raw[pos:pos + clen]
        pos += clen
        if not block:
            break
        try:
            out += snappy_raw_decompress(block)
        except Exception:
            continue
    return bytes(out)


# text we never want: protobuf/iWork internal identifiers, style names, UUID-ish tokens
_NOISE = re.compile(
    r"^(?:[A-Z]{2,4}\.[A-Za-z.]+|[A-Za-z]+Archive|[A-Za-z]*Stylesheet[A-Za-z]*|"
    r"[0-9a-fA-F-]{16,}|\$[0-9A-Fa-f-]{20,}|[A-Za-z]+-[0-9]+|SF[A-Z][A-Za-z]*|"
    r"TS[A-Z][A-Za-z]*|CalculationEngine|Document|ViewState|Metadata|iso-[a-z0-9]+|"
    r"decimal|Office Theme|Europe/[A-Za-z_]+|[A-Za-z]+_[A-Za-z0-9_]*series[A-Za-z0-9_]*)$"
)
_PRINTABLE = re.compile(r"^[\x20-\x7E -￿\n\t]+$")


# Numbers/Pages embed locale + number-format tables in the same archives as the user's cells
# (month names, weekday names, ISO currency codes, ICU format patterns). That is the app's
# boilerplate, not the document's data, and it would otherwise swamp a small spreadsheet.
_MONTHS = ("January February March April May June July August September October November "
           "December Jan Feb Mar Apr Jun Jul Aug Sep Sept Oct Nov Dec").split()
_DAYS = ("Sunday Monday Tuesday Wednesday Thursday Friday Saturday "
         "Sun Mon Tue Wed Thu Fri Sat").split()
_CCY = ("GBP AUD BRL CAD CNY EUR HKD ILS INR JPY KRW MXN NZD PHP TWD USD CHF SEK NOK DKK "
        "PLN RUB THB TRY ZAR SGD").split()
_LOCALE_NOISE = set(_MONTHS + _DAYS + _CCY + [
    "gregorian", "latn", "AM", "PM", "NaN", "a.m.", "p.m.", "BC", "AD",
    "1st quarter", "2nd quarter", "3rd quarter", "4th quarter",
    "Before Christ", "Anno Domini",
])
# ICU / number format patterns: "d MMM y", "HH:mm:ss zzzz", "#,##0.###", "#E0"
_FORMAT_PAT = re.compile(r"^[#0.,%E\-+ ]+$|^[dMyHhmsazEG:/,.\- ']+$")


def is_boilerplate(s: str) -> bool:
    if s in _LOCALE_NOISE:
        return True
    # a format pattern has no real word in it
    if _FORMAT_PAT.match(s) and not re.search(r"[A-Za-z]{4}", s):
        return True
    return False


def harvest_strings(buf: bytes, min_len: int = 3, depth: int = 0) -> list[str]:
    """Walk protobuf wire format; collect length-delimited fields that decode as real text.

    Recurses into nested messages: iWork stores table-cell text several levels down (the
    document's own strings sit inside sub-messages of the Tables/DataList archives), so a
    top-level-only walk silently returns nothing for spreadsheets.
    """
    if depth > 8:
        return []
    found: list[str] = []
    pos, n = 0, len(buf)
    while pos < n:
        # read a varint key
        key, shift = 0, 0
        start = pos
        while pos < n:
            b = buf[pos]
            pos += 1
            key |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
            if shift > 35:
                break
        if pos >= n:
            break
        wire = key & 0x07
        if wire == 2:  # length-delimited — the only one that can hold a string
            ln, shift = 0, 0
            while pos < n:
                b = buf[pos]
                pos += 1
                ln |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
                if shift > 35:
                    ln = 0
                    break
            if ln <= 0 or pos + ln > n:
                continue
            chunk = buf[pos:pos + ln]
            pos += ln
            text = None
            try:
                cand = chunk.decode("utf-8").strip()
                if (len(cand) >= min_len and _PRINTABLE.match(cand)
                        and not _NOISE.match(cand) and re.search(r"[A-Za-z]{3}|[0-9]", cand)):
                    text = cand
            except UnicodeDecodeError:
                pass
            if text is not None:
                found.append(text)
            else:
                # not a leaf string — treat as a nested message and descend
                found.extend(harvest_strings(chunk, min_len, depth + 1))
        elif wire == 0:  # varint
            while pos < n and buf[pos] & 0x80:
                pos += 1
            pos += 1
        elif wire == 5:
            pos += 4
        elif wire == 1:
            pos += 8
        else:
            pos = start + 1  # unknown wire type: resync
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("out_txt")
    ap.add_argument("--min-chars", type=int, default=20)
    args = ap.parse_args()

    try:
        z = zipfile.ZipFile(args.bundle)
    except Exception:
        return 4

    names = [n for n in z.namelist() if n.endswith(".iwa")]
    # Document/Tables carry the content; ViewState/Stylesheet/CalculationEngine carry chrome.
    names.sort(key=lambda n: (0 if "Tables" in n or "Document" in n else 1, n))

    seen: set[str] = set()
    lines: list[str] = []
    for name in names:
        if any(k in name for k in ("ViewState", "Stylesheet", "CalculationEngine",
                                   "AnnotationAuthor", "Metadata")):
            continue
        try:
            buf = iwa_chunks(z.read(name))
        except Exception:
            continue
        for s in harvest_strings(buf):
            if s in seen or is_boilerplate(s):
                continue
            seen.add(s)
            lines.append(s)

    text = "\n".join(lines).strip()
    if len(text) < args.min_chars:
        return 3

    with open(args.out_txt, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
